import argparse, re, os
from .product import version
import importlib.util
import threading


def register_watch(module, filepath):
    spec = importlib.util.spec_from_file_location(module, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    watches = []
    for (name, item) in module.__dict__.items():
        if name.startswith('watch'):
            watches.append(item)
    return watches


def tagExpressionGen(argstr):
    tagRules = []
    for part in argstr:
        # 有单引号，是表达式
        if "'" in part:
            rule = re.sub(r"'.+?'", lambda m: f'tagmatch({m.group(0)})', part)
            tagRules.append(f'({rule})')
        # 是简单标签名
        else:
            rule = f"tagmatch('{part}')"
            tagRules.append(f'{rule}')
    return ' or '.join(tagRules)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=f'hytest v{version}', help="显示版本号")
    parser.add_argument('--new', metavar='project_dir', help="创建新项目目录")
    parser.add_argument("case_dir", help="用例根目录", nargs='?', default='cases')
    parser.add_argument("-L", "--loglevel", metavar='Level_Number', type=int, help="日志级别  0:低 - 1:高", default=0)

    parser.add_argument("--test", metavar='Case_Name', action='append', help="用例名过滤，支持通配符", default=[])
    parser.add_argument("--suite", metavar='Suite_Name', action='append', help="套件名过滤，支持通配符", default=[])
    parser.add_argument("--tag", metavar='Tag_Expression', action='append', help="标签名过滤，支持通配符", default=[])
    parser.add_argument("--tagnot", metavar='Tag_Expression', action='append', help="标签名过滤，支持通配符", default=[])
    parser.add_argument("-A", "--argfile", metavar='Argument_File', help="参数文件",
                        type=argparse.FileType('r', encoding='utf8'))
    parser.add_argument('-W', "--watch", nargs='?', help="多线程监控")

    args = parser.parse_args()

    event = threading.Event()
    if args.watch:
        watch_list = register_watch('watch', args.watch)
        for item in watch_list:
            t = threading.Thread(target=item, args=(event,))
            t.setDaemon(True)
            t.start()
    else:
        watch_list = None
    # 有参数放在文件中
    if args.argfile:
        fileArgs = [para for para in args.argfile.read().replace('\n', ' ').split() if para]
        args = parser.parse_args(fileArgs, args)

    # 创建项目目录
    if args.new:
        projDir = args.new
        if os.path.exists(projDir):
            print(f'{projDir} already exists！')
            exit(2)
        os.makedirs(f'{projDir}/cases')
        with open(f'{projDir}/cases/case1.py', 'w', encoding='utf8') as f:
            f.write('''class c1:
    name = '用例名称 - 0001'

    # 测试用例步骤
    def teststeps(self):...''')

        exit()

    if not os.path.exists(args.case_dir):
        print(f' {args.case_dir} 目录不存在，工作目录为：{os.getcwd()}')
        exit(2)  # 2 表示没有可以执行的用例

    if not os.path.isdir(args.case_dir):
        print(f' {args.case_dir} 不是目录，工作目录为：{os.getcwd()}')
        exit(2)  # 2 表示没有可以执行的用例

    # 同时执行log里面的初始化日志模块，注册signal的代码
    from .utils.log import LogLevel
    from .utils.runner import Collector, Runner

    LogLevel.level = args.loglevel
    # print('loglevel',LogLevel.level)

    # --tag "'冒烟测试' and 'UITest' or (not '快速' and 'fast')" --tag 白月 --tag 黑羽

    tag_include_expr = tagExpressionGen(args.tag)
    tag_exclude_expr = tagExpressionGen(args.tagnot)

    # print(tag_include_expr)
    # print(tag_exclude_expr)

    print(f'''           
    *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *     
    *       hytest {version}            www.byhy.net   *
    *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *
    '''
          )

    os.makedirs('log/imgs', exist_ok=True)

    Collector.run(
        casedir=args.case_dir,
        suitename_filters=args.suite,
        casename_filters=args.test,
        tag_include_expr=tag_include_expr,
        tag_exclude_expr=tag_exclude_expr,
    )

    # 0 表示执行成功 , 1 表示有错误 ， 2 表示没有可以执行的用例,3 表示网页或APP崩溃恢复原状失败
    result = []  # 懒得重写thread 就传list拿结果
    t = threading.Thread(target=Runner.run, args=(result, event))
    t.setDaemon(True)
    t.start()
    try:
        while t.is_alive():
            pass
    except:
        print('Stopped by keyboard')

    if watch_list:
        event.clear()
    if not result:
        return 0
    return result[0]


if __name__ == '__main__':
    exit(run())

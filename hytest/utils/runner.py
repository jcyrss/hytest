import os, types, importlib.util, fnmatch, traceback

from .signal import signal

from ..cfg import l



# 用例标签匹配，有一个满足即可
def tagmatch(pattern):
    for tag in Collector.current_case_tags:
        if fnmatch.fnmatch(tag,pattern):
            # print(' --> match')
            return True
    # print(' --> nomatch')
    return False


 
'''
搜集有效执行对象的 思路 伪代码如下：

循环遍历加载用例目录下面所有的 py 文件，导入为模块：
    从该模块找到测试相关的信息 比如：套件标签、套件初始化清除、用例类， 保存到字典meta中

    如果是用例模块，根据 选择条件 判定模块里面的用例 是否被选中，去掉没有选中的用例

从执行列表中去掉 没有包含用例的 目录模块
''' 
class Collector:
    
    SUITE_TAGS = [
        'force_tags',
        'default_tags', # 暂时不用
    ]

    SUITE_STS = [
        'suite_setup',
        'suite_teardown',
        'test_setup',
        'test_teardown',
    ]

    # 最终要执行的 相关模块文件
    exec_list = []
    # 最终要执行的 相关模块文件 和 对应的 对象
    exec_table = {}

    # 记录本次要执行的用例个数
    case_number = 0

    # 标签表，根据进入的路径，记录和当前模块相关的标签    
    #   格式如下  
    #     'force_tags': {
    #         'cases\\': ['冒烟测试', '订单功能'],
    #         'cases\\customer\\功能21.py': ['冒烟测试', '订单功能'],},
    #     'default_tags': {
    #         'cases\\customer\\功能31.py': ['优先级7']   }

    suite_tag_table = {
        'force_tags':{},
        'default_tags':{}
    } 

    # 当前用例的所有标签
    current_case_tags = []


    @classmethod
    def run(cls,
            casedir='cases',
            suitename_filters=[], # 只要有一个匹配就算匹配
            casename_filters=[],   # 只要有一个匹配就算匹配
            tag_include_expr=None,    
            tag_exclude_expr=None,   
            ):


        signal.info(
            ('\n\n===   [ 收集测试用例 ]  === \n',
            '\n\n===   [ collect test cases ]  === \n')[l.n]
        )

        for (dirpath, dirnames, filenames) in os.walk(casedir):
            # 确保 __st__.py 在最前面
            if '__st__.py' in filenames:
                filenames.remove('__st__.py')
                filenames.insert(0,'__st__.py')

            # 处理每个可能的执行模块文件
            for fn in filenames:
                filepath = os.path.join(dirpath, fn)
                if not filepath.endswith('.py'):
                    continue
                
                signal.info(f'\n== {filepath} \n')
                module_name = fn[:-3]
                spec = importlib.util.spec_from_file_location(module_name, filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # 处理一个模块文件
                cls.handleOneModule(module,filepath,
                    tag_include_expr,
                    tag_exclude_expr,
                    suitename_filters,
                    casename_filters)

        
        # *** 从执行列表中去掉 没有包含用例的 目录模块 ***
        # 先把 套件目录 和 套件文件 分别放到列表 sts, cases 中
        sts, cases = [], []
        for filepath in cls.exec_list:
            if filepath.endswith('py'):
                cases.append(filepath)
            else:
                sts.append(filepath)

        # 再找出 套件目录中没有可以执行的测试文件的 哪些， 去掉不要
        for stPath in sts:
            valid = False
            for  casePath in cases:
                if casePath.startswith(stPath):
                    valid = True
                    break
            if not valid:
                cls.exec_list.remove(stPath) 
                cls.exec_table.pop(stPath)


    # 处理一个模块文件
    @classmethod
    def handleOneModule(cls,module,filepath:str,
                        tag_include_expr:str,
                        tag_exclude_expr:str,
                        suitename_filters:list,
                        casename_filters:list):

        cur_module_name = os.path.basename(filepath).replace('.py','')

        stType = filepath.endswith('__st__.py')
        caseType = not stType

        if stType:
            filepath = filepath.replace('__st__.py','')

        # ======  搜寻该模块  hytest关键信息 ，保存在 meta 里面========
        meta = { 'type': 'casefile' if caseType else 'st' }
        if caseType: 
            meta['cases'] = []

        for name,item in module.__dict__.items():

            # __ 开头的名字肯定不是hytest关键名，跳过
            if name.startswith('__'):
                continue

            # 对应一个模块文件的，肯定是外部导入的模块，跳过
            if hasattr(item,'__file__'):
                continue

            # 外部模块内部导入的名字，跳过
            if hasattr(item,'__module__'):
                if item.__module__ != cur_module_name:
                    continue

            # signal.info(f'-- {name}')

            # 列表 ： 是 标签 吗？
            if isinstance(item, list):
                # 非标签关键字，跳过
                if name not in cls.SUITE_TAGS:
                    continue

                # 如果标签列表为空，跳过
                if not item:
                    continue

                meta[name] = item
                cls.suite_tag_table[name][filepath] = item

                signal.debug(f'-- {name}')

            # 函数 ： 是 初始化清除 吗？
            elif isinstance(item, types.FunctionType):
                # 非套件初始化清除关键字，跳过
                if name not in cls.SUITE_STS:
                    continue

                meta[name] = item

                signal.debug(f'-- {name}')
                    
            # 类  ： 是 用例 吗？
            elif caseType and isinstance(item, type):  
                # 没有 teststeps  ， 肯定不是用例类, 跳过
                if not hasattr(item, 'teststeps'):
                    signal.info(f'no teststeps in class "{name}", skip it.')
                    continue 
                
                # 如果 有 name    是 一个用例
                if  hasattr(item, 'name'):
                    # 同时有 ddt_cases ，格式不对
                    if hasattr(item, 'ddt_cases') : 
                        signal.info(f'both "name" and "ddt_cases" in class "{name}", skip it.')
                        continue 

                    meta['cases'].append(item())

                    signal.debug(f'-- {name}')

                # 如果 有 ddt_cases  是数据驱动用例，对应多个用例
                elif hasattr(item, 'ddt_cases') :  
                    for caseData in item.ddt_cases:
                        # 实例化每个用例，属性name，para设置好
                        case = item()
                        case.name, case.para = caseData['name'], caseData['para'],               
                        meta['cases'].append(case)  

                # 没有 name 也没有 ddt_cases， 类名作为用例名
                else:
                    item.name = name
                    meta['cases'].append(item())

                    signal.debug(f'-- {name}')


        # suite_tag_table 表中去掉 和 当前模块不相干的记录， 
        # 这样每次进入新的模块目录，就会自动去掉前面已经处理过的路径 标签记录
        new_suite_tag_table = {}
        for tname, table in cls.suite_tag_table.items(): 
            new_suite_tag_table[tname] = {p:v for p,v in table.items() if filepath.startswith(p)}                 
        cls.suite_tag_table = new_suite_tag_table
        
        
        #  用例模块 
        if caseType:            
            # 如果 没有用例 
            if not meta['cases']:
                signal.info(f'\n** no cases in this file, skip it.')
                return

            #  模块里面的用例 根据选择条件过滤 ，如果没有通过，会从 meta['cases'] 里面去掉
            cls.caseFilter(filepath, meta, tag_include_expr, tag_exclude_expr,suitename_filters,casename_filters)

            # 如果 用例都被过滤掉了
            if not meta['cases']:
                signal.info(f'\n** no cases in this file , skip it.')
                return

            # 待执行用例总数更新
            cls.case_number += len(meta['cases'])

        # __st__ 模块
        else:   
            #  应该包含 初始化 或者 清除 或者 标签 ，否则是无效模块，跳过
            if len(meta) == 1:
                signal.info(f'\n** no setup/teardown/tags in this file , skip it.')
                return 
            
        # 该模块文件 先暂时 加入执行列表
        cls.exec_list.append(filepath)
        cls.exec_table[filepath] = meta

    # 经过这个函数的执行， 最后 meta['cases'] 里面依然保存的，才是需要执行的用例
    @classmethod
    def caseFilter (cls,filepath:str, meta:dict,
                        tag_include_expr:str,
                        tag_exclude_expr:str,
                        suitename_filters:list,
                        casename_filters:list):
          
        # -------- 模块所有用例进行分析 ---------

        # 没有任何过滤条件，就不需要再看每个用例的情况了
        if not tag_include_expr and not tag_exclude_expr and not suitename_filters and not casename_filters:
            return 
        
        # 如果没有排除过滤， 
        # 并且 有 套件名过滤，并且整个套件被选中，就不需要再看每个用例的情况了
        # 一个用例文件 ，路径上的每一级都是一个套件
        if not tag_exclude_expr and suitename_filters:
            suitenames = filepath.split(os.path.sep) 
            # 套件文件名的后缀.py 去掉 作为套件名
            suitenames = [sn[:-3] if sn.endswith('.py') else sn  for sn in suitenames ]
            if cls._patternMatch(suitenames,suitename_filters):
                return
        
        # -------- 对每个用例进行分析 ---------

        passedCases = [] # 被选中的用例列表

        for caseClass in meta['cases']:     
            signal.debug(f'\n* {caseClass.name}')
            
            # ----------- 先看标签排除过滤 ------------
            
            # 得到当前模块相关的 套件 标签，就是表中现有的标签合并
            suite_tags = [t for tl in cls.suite_tag_table['force_tags'].values() for t in tl]
            # 用例本身的标签
            case_tags = getattr(caseClass, 'tags',[])
            # 用例关联的所有的标签
            cls.current_case_tags = set(suite_tags + case_tags)
            # print(cls.current_case_tags)

            # 如果有标签排除过滤
            if tag_exclude_expr:   
                # 条件满足，被排除
                if eval(tag_exclude_expr) == True: 
                    signal.debug(f'excluded for meeting expr : {tag_exclude_expr}')
                    continue 
                # 没有被排除
                else:
                    # 并且没有其他的 选择条件（只有标签排除过滤），就是被选中
                    if not casename_filters and not suitename_filters and not tag_include_expr:
                        passedCases.append(caseClass)
                        continue


            # --------- 再看 名字匹配过滤 ------------ 
            # 有用例名过滤
            if casename_filters:
                caseName = getattr(caseClass, 'name')
                #  通过用例名过滤 
                if  cls._patternMatch([caseName],casename_filters):
                    passedCases.append(caseClass)
                    continue


            # ----------- 再看标签匹配过滤 ------------
            if tag_include_expr :                
                if eval(tag_include_expr) == True:                    
                    passedCases.append(caseClass)
                    continue 

            # 上面一个选择条件也没有满足
            signal.debug(f'excluded for not meet any include rules')

        # 最终存放 通过过滤的用例
        meta['cases'] = passedCases


    @classmethod
    def _patternMatch (cls,names,patterns):
        for name in names:
            for pattern in patterns:
                if fnmatch.fnmatch(name,pattern):
                    return True
        return False
 

'''
执行自动化的 思路 伪代码如下：

1. 先保证 exec_list 中 该teardown的地方插入 teardown记录


执行前， exec_list 示例如下
[
    'cases\\',
    'cases\\.功能3.py',
    'cases\\功能1.py',
    'cases\\功能2.py',
    'cases\\customer\\',
    'cases\\customer\\功能21.py',
    'cases\\order\\',
    'cases\\order\\功能31.py',
] 


遍历 exec_table 中的每个对象：    
    如果 该执行对象 type 是 st， 说明是 套件目录：
        如果有 tear_down, 到 exec_list 中 找到合适的位置，插入 tear_down 操作

执行完此步骤后， exec_list 示例如下
[
    'cases\\',
    'cases\\.功能3.py',
    'cases\\功能1.py',
    'cases\\功能2.py',
    'cases\\customer\\',
    'cases\\customer\\功能21.py',
    'cases\\customer\\--teardown--',
    'cases\\order\\',
    'cases\\order\\功能31.py',
    'cases\\order\\--teardown--',
    'cases\\--teardown--'
] 
    

2. 然后执行测试

suite_setup_failed_list = [] 记录初始化失败的套件

for name in  exec_list：    
    检查 这个name 是否以 suite_setup_failed_list 里面的内容开头
    如果是 continue

    if name 以 --teardown--  结尾：
        去掉 --teardown-- 部分，找到 exec_table中的对象执行 teardown
    else：
        以name 为key， 找到 exec_table中的对象：
            if 类型是 st ：
                如果 有 suite_setup:
                    执行 suite_setup
                    如果 suite_setup 抛异常：
                        添加 name 到 suite_setup_failed_list 
            esif 类型是 case：
                执行 case里面的用例：
                    先执行用例的 setup
                    如果 setup 异常，后面的 teststeps 和 teardown都不执行


''' 
class Runner:
    
    curRunningCase = None 

    # 记录所有测试用例的执行结果，每个元素都是用户定义的测试用例类实例
    #  执行过程中写入了测试几个到每个测试用例类中
    case_list = []

    @classmethod
    def run(cls,):
        
        signal.info(
            ('\n\n===   [ 执行测试用例 ]  === \n',
            '\n\n===   [ execute test cases ]  === \n')[l.n]
        )

        # 如果本次没有可以执行的用例（可能是过滤项原因），直接返回
        if not Collector.exec_list:
            signal.error(('!! 没有可以执行的测试用例','!! No cases to run')[l.n])
            return 2 # 2 表示没有可以执行的用例

        signal.info(f"{('预备执行用例数量','Number of cases to run')[l.n]} : {Collector.case_number}\n")

        # 执行用例时，为每个用例分配一个id，方便测试报告里面根据id跳转到用例
        cls.caseId = 0

        # 1. 先保证 exec_list 中 该teardown的地方插入 teardown记录
        for name,meta in Collector.exec_table.items():
            if meta['type'] == 'st' and 'suite_teardown' in meta:
                cls._insertTeardownToExecList(name)

        # print(Collector.exec_list)

        # 2. 然后执行自动化流程         
        signal.test_start()
        cls.execTest()
        signal.test_end(cls)

        from hytest.common import  GSTORE
        # 0 表示执行成功 , 1 表示有错误 ， 2 表示没有可以执行的用例, 3 表示未知错误
        return GSTORE.get('---ret---',3)

    @classmethod
    def execTest(cls):

        suite_setup_failed_list = [] # 记录初始化失败的套件
        for name in  Collector.exec_list:
            # 检查 这个name 是否属于套件初始化失败影响的范围
            affected = False
            for suite_setup_failed in suite_setup_failed_list:
                if name.startswith(suite_setup_failed):
                    affected = True
                    break
            if affected:
                continue

            # 套件目录清除
            if name.endswith('--teardown--'):
                # 去掉 --teardown-- 部分
                name = name.replace('--teardown--','')
                # 找到 exec_table 中的对象执行 teardown
                suite_teardown = Collector.exec_table[name]['suite_teardown']
                                
                signal.teardown(name,'suite')
                
                try:
                    suite_teardown()
                except Exception as e:
                    # 套件目录 清除失败
                    signal.teardown_fail(name,'suite', e,traceback.format_exc())


            else:
                meta = Collector.exec_table[name]

                # 进入套件目录
                if meta['type'] == 'st': 

                    signal.enter_suite(name,'dir')

                    suite_setup = meta.get('suite_setup')
                    
                    # 套件目录初始化
                    if suite_setup:                        
                        signal.setup(name,'suite')
                        try:
                            suite_setup()
                        except Exception as e:
                            # 套件目录 初始化失败,
                            signal.setup_fail(name,'suite', e,traceback.format_exc())
                            # 记录到 初始化失败目录列表 中， 该套件目录内容都不会再执行
                            suite_setup_failed_list.append(name)

                # 进入套件文件
                elif meta['type'] == 'casefile': 

                    signal.enter_suite(name,'file')
                    
                    # 套件文件 初始化
                    suite_setup = meta.get('suite_setup')
                    if suite_setup:                        
                        signal.setup(name,'suite')
                        
                        try:
                            suite_setup()
                        except Exception as e:
                            # 套件文件 初始化失败 
                            signal.setup_fail(name,'suite', e, traceback.format_exc())
                            # 该套件文件内容都不会再执行
                            continue 

                    # 执行套件文件里面的用例
                    cls._exec_cases(meta)
                    
                    # 套件文件 清除
                    suite_teardown = meta.get('suite_teardown')
                    if suite_teardown:
                        signal.teardown(name,'suite')                        
                        try:
                            suite_teardown()
                        except Exception as e:
                            # 套件文件 清除失败
                            signal.teardown_fail(name, 'suite', e,traceback.format_exc())


    #  exec_list 中 找到 stName 对应的 teardown的地方插入 teardown记录
    @classmethod
    def _insertTeardownToExecList(cls,stName):
        findStart = False
        insertPos = -1
        for pos, name in enumerate(Collector.exec_list):
            # 这样肯定会先找到 等于 stName 的位置
            if not findStart:
                if name != stName:
                    continue
                else:
                    findStart = True
            else:
                # print(name,stName)
                # 接下来找 不以 stName 开头的那个元素，就在此位置插入
                if not name.startswith(stName):
                    insertPos = pos
                    break
        
        # 直到最后也没有找到，是用例根目录，添加到最后
        tearDownName = stName+'--teardown--'

        if insertPos == -1:
            Collector.exec_list.append(tearDownName)
        else:            
            Collector.exec_list.insert(insertPos,tearDownName)
            

    # 执行套件文件里面的多个用例
    @classmethod
    def _exec_cases(cls,meta):
        # 缺省  test_setup test_teardown
        test_setup = meta.get('test_setup')
        test_teardown = meta.get('test_teardown')

        # 取出每一个用例
        for case in meta['cases']:
            # 记录到 cls.case_list 中，方便测试结束后，遍历每个测试用例
            cls.case_list.append(case)

            case_className = type(case).__name__

            # 用例 id 自动递增 分配， 这个id 主要是 作为 产生的HTML日志里面的html元素id
            cls.caseId += 1  
            signal.enter_case(cls.caseId, case.name, case_className)
            
            # 记录当前执行的case
            cls.curRunningCase = case
            
            # 如果用例有 setup
            caseSetup = getattr(case,'setup',None)
            if caseSetup:
                signal.setup(case.name,'case')
                
                try:
                    caseSetup()
                except Exception as e:
                    signal.setup_fail(case.name, 'case', e, traceback.format_exc())
                    continue # 初始化失败，这个用例的后续也不用执行了
                
            # 如果用例没有 setup，但是有缺省  test_setup
            elif test_setup:
                signal.setup(case.name,'case_default')                
                try:
                    test_setup()
                except Exception as e:
                    signal.setup_fail(case.name, 'case_default', e, traceback.format_exc())
                    continue # 初始化失败，这个用例的后续也不用执行了
                

            signal.case_steps(case.name)

            try:
                # 先预设结果为通过，如果有检查点不通过，那里会设置为fail
                case.execRet = 'pass'
                case.teststeps()
                signal.case_result(case) 
            except AssertionError as e:   
                case.execRet = 'fail'
                case.error = e 
                case.stacktrace = traceback.format_exc()
                signal.case_result(case)            
            except Exception as e:  
                case.execRet = 'abort'
                case.error = e
                case.stacktrace = traceback.format_exc()
                signal.case_result(case)  
                



            # 用例 teardown
            caseTeardown = getattr(case,'teardown',None)
            if caseTeardown:
                signal.teardown(case.name, 'case')
                try:
                    caseTeardown()   
                except Exception as e:
                    signal.teardown_fail(case.name, 'case', e,traceback.format_exc())
            # 如果用例没有 teardown ，但是有缺省  test_teardown
            elif test_teardown:
                signal.teardown(case.name, 'case_default')                
                try:
                    test_teardown()   
                except Exception as e:
                    signal.teardown_fail(case.name, 'case_default', e,traceback.format_exc())


if __name__ == '__main__':
    Collector.run(
        # suitename_filters=['cust*'],
        # casename_filters=['cust*','or*'],
        # tag_include_expr="(tagmatch('优先级4')) or (tagmatch('UITest'))  or  (tagmatch('Web*'))"
        )

    # print(Collector.exec_table)

    Runner.run()


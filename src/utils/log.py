import logging, os, time, traceback, platform
import shutil
from logging.handlers import RotatingFileHandler


from rich.console import Console
from rich.theme import Theme

from hytest.product import version

from datetime import datetime

from hytest.common import GSTORE

from .runner import Collector
from ..cfg import l,Settings

os.makedirs('log',exist_ok=True)

# 日志文件
logger = logging.getLogger('my_logger') 
logger.setLevel(logging.DEBUG)

logFile = os.path.join('log','testresult.log')
handler = RotatingFileHandler(
    logFile, 
    maxBytes=1024*1024*30, 
    backupCount=2,
    encoding='utf8')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt='%(message)s')
handler.setFormatter(formatter)

handler.doRollover() # 每次启动创建一个新log文件，而不是从原来的基础上继续添加

logger.addHandler(handler)


# # 重定向stdout，改变print行为，同时写屏和日志
# import sys
# class MyPrintClass:
 
#     def __init__(self):
#         self.console = sys.stdout

#     def write(self, message):
#         self.console.write(message)
#         logger.info(message)
 
#     def flush(self):
#         self.console.flush()
#         # self.file.flush()

# sys.stdout = MyPrintClass()



console = Console(theme=Theme(inherit=False))

print = console.print



class LogLevel:
    """
    here, we use different log level numbers with Python logging lib
    CRITICAL - 0
    ERROR    - 1
    WARNING  - 2
    INFO     - 3
    DEBUG    - 4
    ALL      - 5
    """
    level = 3



class Stats:

    def test_start(self,_title='Test Report'):
        self.result = {
            # 这是准备执行的用例数量
            'case_count_to_run': Collector.case_number,
            # 这个是实际执行的用例数量，可能有其他的用例因为初始化失败没有执行
            'case_count' : 0,
            'case_pass'  : 0,
            'case_fail'  : 0,
            'case_abort' : 0,
            'suite_setup_fail' : 0,
            'case_setup_fail' : 0,
            'suite_teardown_fail' : 0,
            'case_teardown_fail' : 0,
            'case_pass_list'  : [],
            'case_fail_list'  : [],
            'case_abort_list' : [],

        }
                
    
        self.start_time = time.time()

    def test_end(self, runner):
        self.end_time = time.time()
        self.test_duration = self.end_time-self.start_time

        if  self.result['case_fail'] or \
            self.result['case_abort'] or \
            self.result['suite_setup_fail'] or \
            self.result['case_setup_fail'] or \
            self.result['suite_teardown_fail'] or \
            self.result['case_teardown_fail'] :
            GSTORE['---ret---'] = 1
        else:
            GSTORE['---ret---'] = 0


    def enter_case(self, caseId ,name, case_className):
        self.result['case_count'] += 1    
    

    def case_result(self,case):
        if case.execRet == 'pass':
            self.result['case_pass'] += 1   
        elif case.execRet == 'fail':
            self.result['case_fail'] += 1  
        elif case.execRet == 'abort':
            self.result['case_abort'] += 1   


    # utype 可能是 suite  case  case_default     
    def setup_fail(self,name, utype, e, stacktrace):  
        if utype == 'suite':
            self.result['suite_setup_fail'] += 1   
        else:
            self.result['case_setup_fail'] += 1 
    
    def teardown_fail(self,name, utype, e, stacktrace):  
        if utype == 'suite':
            self.result['suite_teardown_fail'] += 1   
        else:
            self.result['case_teardown_fail'] += 1 

stats = Stats()

class ConsoleLogger:
    
    def test_end(self, runner):
        ret = stats.result
        print((f'\n\n  ========= 测试耗时 : {stats.test_duration:.3f} 秒 =========\n',
               f'\n\n  ========= Duration Of Testing : {stats.test_duration:.3f} seconds =========\n')[l.n])


        print(f"\n  {('预备执行用例数量','number of cases plan to run')[l.n]} : {ret['case_count_to_run']}")

        print(f"\n  {('实际执行用例数量','number of cases actually run')[l.n]} : {ret['case_count']}")

        print(f"\n  {('通过','passed')[l.n]} : {ret['case_pass']}", style='green')
        
        num = ret['case_fail']
        style = 'white' if num == 0 else 'bright_red'
        print(f"\n  {('失败','failed')[l.n]} : {num}", style=style)
        
        num = ret['case_abort']
        style = 'white' if num == 0 else 'bright_red'
        print(f"\n  {('异常','exception aborted')[l.n]} : {num}", style=style)
        
        num = ret['suite_setup_fail']
        style = 'white' if num == 0 else 'bright_red'
        print(f"\n  {('套件初始化失败','suite setup failed')[l.n]} : {num}", style=style)
        
        num = ret['suite_teardown_fail']
        style = 'white' if num == 0 else 'bright_red'
        print(f"\n  {('套件清除  失败','suite teardown failed')[l.n]} : {num}", style=style)
        
        num = ret['case_setup_fail']
        style = 'white' if num == 0 else 'bright_red'
        print(f"\n  {('用例初始化失败','cases setup failed')[l.n]} : {num}", style=style)
        
        num = ret['case_teardown_fail']
        style = 'white' if num == 0 else 'bright_red'
        print(f"\n  {('用例清除  失败','cases teardown failed')[l.n]} : {num}", style=style)

        print("\n\n")
    
    def enter_suite(self,name,suitetype):   
        if suitetype == 'file' :
            print(f'\n\n>>> {name}',style='bold bright_white')

    
    def enter_case(self, caseId ,name, case_className):        
        print(f'\n* {name}',style='bright_white')

    
    def case_steps(self,name):...

    
    # def case_pass(self, case, caseId, name):
    #     print('                          PASS',style='green')

    
    # def case_fail(self, case, caseId, name, e, stacktrace):
    #     print(f'                          FAIL\n{e}',style='bright_red')
        
    
    # def case_abort(self, case, caseId, name, e, stacktrace):
    #     print(f'                          ABORT\n{e}',style='magenta')


    def case_result(self,case):
        if case.execRet == 'pass':
            print('                          PASS',style='green')
        elif case.execRet == 'fail':
            print(f'                          FAIL\n{case.error}',style='bright_red')
        elif case.execRet == 'abort':
            print(f'                          ABORT\n{case.error}',style='magenta')


    
    def setup(self,name, utype):...
    
    
    def teardown(self,name, utype):...

    # utype 可能是 suite  case  case_default
    def setup_fail(self,name, utype, e, stacktrace): 
        utype =  ('套件','suite')[l.n] if utype == 'suite' else ('用例','case')[l.n]
        print(f"\n{utype} {('初始化失败','setup failed')[l.n]} | {name} | {e}",style='bright_red')
        # print(f'\n{utype} setup fail | {name} | {e}',style='bright_red')

    
    def teardown_fail(self,name, utype, e, stacktrace):      
        utype =  ('套件','suite')[l.n] if utype == 'suite' else ('用例','case')[l.n]
        print(f"\n{utype} {('清除失败','teardown failed')[l.n]} | {name} | {e}", style='bright_red')
        # print(f'\n{utype} teardown fail | {name} | {e}',style='bright_red')


    def info(self, msg):
        if LogLevel.level >= 3:
            print(f'{msg}')

    def debug(self, msg):
        if LogLevel.level >= 4:
            print(f'{msg}')

    def error(self,msg):
        if LogLevel.level >= 1:
            print(f'{msg}', style='bright_red')


    def critical(self,msg):
        if LogLevel.level >= 0:
            print(f'{msg}', style='green')



class TextLogger:

    def test_start(self,_title=''):
        startTime = time.strftime('%Y%m%d_%H%M%S',
                                           time.localtime(stats.start_time))

        logger.info(f'\n\n  ========= {("测试开始","Test Start")[l.n]} : {startTime} =========\n')


    def test_end(self, runner):
        endTime = time.strftime('%Y%m%d_%H%M%S',
                                  time.localtime(stats.end_time))
        logger.info(f'\n\n  ========= {("测试结束","Test End")[l.n]} : {endTime} =========\n')

        logger.info(f"\n  {('耗时','Duration Of Testing ')[l.n]}    : {(stats.end_time-stats.start_time):.3f} 秒\n")
        ret = stats.result

        logger.info(f"\n  {('预备执行用例数量','number of cases plan to run')[l.n]} : {ret['case_count_to_run']}")
        logger.info(f"\n  {('实际执行用例数量','number of cases actually run')[l.n]} : {ret['case_count']}")
        logger.info(f"\n  {('通过','passed')[l.n]} : {ret['case_pass']}")
        logger.info(f"\n  {('失败','failed')[l.n]} : {ret['case_fail']}")
        logger.info(f"\n  {('异常','exception aborted')[l.n]} : {ret['case_abort']}")
        logger.info(f"\n  {('套件初始化失败','suite setup failed')[l.n]} : {ret['suite_setup_fail']}")
        logger.info(f"\n  {('套件清除  失败','suite teardown failed')[l.n]} : {ret['suite_teardown_fail']}")
        logger.info(f"\n  {('用例初始化失败','cases setup failed')[l.n]} : {ret['case_setup_fail']}")
        logger.info(f"\n  {('用例清除  失败','cases teardown failed')[l.n]} : {ret['case_teardown_fail']}")
    
    def enter_suite(self,name,suitetype): 
        logger.info(f'\n\n>>> {name}')

    
    def enter_case(self, caseId ,name , case_className):
        curTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f'\n* {name}  -  {curTime}')

    
    def case_steps(self,name):  
        logger.info(f'\n  [ case execution steps ]')

    
    # def case_pass(self, case, caseId, name):
    #     logger.info('  PASS ')

    
    # def case_fail(self, case, caseId, name, e, stacktrace):
    #     stacktrace = "Traceback:\n" +stacktrace.split("\n",3)[3]
    #     logger.info(f'  FAIL   {e} \n{stacktrace}')
        
    
    # def case_abort(self, case, caseId, name, e, stacktrace):
    #     stacktrace = "Traceback:\n" +stacktrace.split("\n",3)[3]
    #     logger.info(f'  ABORT   {e} \n{stacktrace}')


    def case_result(self,case):
        if case.execRet == 'pass':
            logger.info('  PASS ')
        else:
            stacktrace = "Traceback:\n" +case.stacktrace.split("\n",3)[3]
            if case.execRet == 'fail':
                logger.info(f'  FAIL   {case.error} \n{stacktrace}')
            elif case.execRet == 'abort':
                logger.info(f'  ABORT   {case.error} \n{stacktrace}')



    
    def setup(self,name, utype): 
        logger.info(f'\n[ {utype} setup ] {name}')
    
    
    def teardown(self,name, utype): 
        logger.info(f'\n[ {utype} teardown ] {name}')

    
    def setup_fail(self,name, utype, e, stacktrace):  
        stacktrace = "Traceback:\n" +stacktrace.split("\n",3)[3]     
        logger.info(f'{utype} setup fail | {e} \n{stacktrace}')

    
    def teardown_fail(self,name, utype, e, stacktrace):  
        stacktrace = "Traceback:\n" +stacktrace.split("\n",3)[3]  
        logger.info(f'{utype} teardown fail | {e} \n{stacktrace}')

    
    def info(self, msg):
        if LogLevel.level >= 3:
            logger.info(f'{msg}')

    def debug(self, msg): 
        if LogLevel.level >= 4:
            logger.info(f'{msg}')

    def error(self,msg):
        if LogLevel.level >= 1:
            logger.info(f'{msg}')


    def critical(self,msg):
        if LogLevel.level >= 0:
            logger.info(f'{msg}')

    def step(self,stepNo,desc):
        logger.info((f'\n-- 第 {stepNo} 步 -- {desc} \n',
                     f'\n-- Step #{stepNo} -- {desc} \n',
                     )[l.n])

    def checkpoint_pass(self, desc):
        logger.info((f'\n** 检查点 **  {desc} ---->  通过\n',
                     f'\n** checkpoint **  {desc} ---->  pass\n'
                     )[l.n])
        
    def checkpoint_fail(self, desc):
        logger.info((f'\n** 检查点 **  {desc} ---->  !! 不通过!!\n',
                     f'\n** checkpoint **  {desc} ---->  !! fail!!\n'
                     )[l.n])


    def log_img(self,imgPath: str, width: str = None):
        logger.info(f'picture {imgPath}')


from dominate.tags import *
from dominate.util import raw
from dominate import document

class HtmlLogger:

    def __init__(self):
        self.curEle = None
        
    def test_start(self,_title=''):
        # css file
        with open(os.path.join(os.path.dirname(__file__) , 'report.css'), encoding='utf8') as f:
            _css_style = f.read()
        # js file
        with open(os.path.join(os.path.dirname(__file__) , 'report.js'), encoding='utf8') as f:
            _js = f.read()


        self.doc = document(title= Settings.report_title)
        self.doc.head.add(
                        meta(charset="UTF-8"),
                        style(raw(_css_style)),
                        script(raw(_js), type='text/javascript'))

        self.main = self.doc.body.add(div(_class='main_section'))

        self.main.add(h1(f'{Settings.report_title}', style='font-family: auto'))

        self.main.add(h3(('统计结果','Test Statistics')[l.n]))

        resultDiv = self.main.add(div(_class='result'))

        self.result_table, self.result_barchart = resultDiv.add(
            table(_class='result_table'),
            div(_class='result_barchart')
        )

        _, self.logDiv = self.main.add(
            div(
                # span('切换到精简模式',_class='h3_button', id='display_mode' ,onclick="toggle_folder_all_cases()"), 
                h3(('执行日志','Test Execution Log')[l.n],style='display:inline'),
                style='margin-top:2em'
            ),
            div(_class='exec_log')
        )

        # 查看上一个和下一个错误的 
        self.ev = div(
                div('∧', _class = 'menu-item', onclick="previous_error()", title='上一个错误'), 
                div('∨', _class = 'menu-item', onclick="next_error()", title='下一个错误'),
                _class = 'error_jumper'
            )

        helpLink = ("http://www.byhy.net/tut/auto/hytest/01",'https://github.com/jcyrss/hytest/Documentation.md') [l.n]
         
        self.doc.body.add(div(
            div(('页首','Home')[l.n], _class = 'menu-item',
                onclick='document.querySelector("body").scrollIntoView()'),
            div(('帮助','Help')[l.n], _class = 'menu-item', 
                onclick=f'window.open("{helpLink}", "_blank"); '),
            div(('Summary','Summary')[l.n],_class='menu-item', id='display_mode' ,onclick="toggle_folder_all_cases()"),
            self.ev,
            id='float_menu')
        )

        self.curEle = self.main  # 记录当前所在的 html element
        self.curSuiteEle = None   # 记录当前的套件元素
        self.curCaseEle = None   # 记录当前的用例元素
        self.curCaseLableEle = None   # 记录当前的用例里面的 种类标题元素
        self.curSetupEle = None   # 记录当前的初始化元素
        self.curTeardownEle = None   # 记录当前的清除元素
        self.suitepath2element = {}


    
    def test_end(self, runner):

        execStartTime = time.strftime('%Y/%m/%d %H:%M:%S',
                                           time.localtime(stats.start_time))
        execEndTime = time.strftime('%Y/%m/%d %H:%M:%S',
                                           time.localtime(stats.end_time))

        ret = stats.result

        errorNum = 0

        trs = []        
        
        trs.append(tr(td(('hytest 版本','hytest version')[l.n]), td(version)))
        trs.append(tr(td(('开始时间','Test Start Time')[l.n]), td(f'{execStartTime}')))
        trs.append(tr(td(('结束时间','Test End Time')[l.n]), td(f'{execEndTime}')))

        trs.append(tr(td(('耗时','Duration Of Testing')[l.n]), td(f'{stats.test_duration:.3f}' + (' 秒',' Seconds')[l.n])))

        trs.append(tr(td(('预备执行用例数量','number of cases plan to run')[l.n]), td(f"{ret['case_count_to_run']}")))
        trs.append(tr(td(('实际执用例行数量','number of cases actually run')[l.n]), td(f"{ret['case_count']}")))

        trs.append(tr(td(('通过','passed')[l.n]), td(f"{ret['case_pass']}")))


        case_count_to_run = ret['case_count_to_run']

        num = ret['case_fail']
        style = '' if num == 0 else 'color:red'
        trs.append(tr(td(('失败','failed')[l.n]), td(f"{num}", style=style)))
        errorNum += num
        
        num = ret['case_abort']
        style = '' if num == 0 else 'color:red'
        trs.append(tr(td(('异常','exception aborted')[l.n]), td(f"{num}", style=style)))
        errorNum += num

        # 计算阻塞用例个数
        blocked_num = case_count_to_run - ret['case_pass'] - ret['case_fail'] - ret['case_abort']
        style = '' if blocked_num == 0 else 'color:red'
        trs.append(tr(td(('阻塞','blocked')[l.n]), td(f"{blocked_num}", style=style)))
        
        num = ret['suite_setup_fail']
        style = '' if num == 0 else 'color:red'
        trs.append(tr(td(('套件初始化失败','suite setup failed')[l.n]), td(f"{num}", style=style)))
        errorNum += num
        
        num = ret['suite_teardown_fail']
        style = '' if num == 0 else 'color:red'
        trs.append(tr(td(('套件清除  失败','suite teardown failed')[l.n]), td(f"{num}", style=style)))
        errorNum += num
        
        num = ret['case_setup_fail']
        style = '' if num == 0 else 'color:red'
        trs.append(tr(td(('用例初始化失败','cases setup failed')[l.n]), td(f"{num}", style=style)))
        errorNum += num
        
        num = ret['case_teardown_fail']
        style = '' if num == 0 else 'color:red'
        trs.append(tr(td(('用例清除  失败','cases teardown failed')[l.n]), td(f"{num}", style=style)))
        errorNum += num

        self.ev['display'] = 'none' if errorNum==0 else 'block'

        # 添加结果统计表
        self.result_table.add(tbody(*trs))

        # 添加 结果柱状图

        def add_barchar_item(statName, percent, color):
            if type(percent) == str:
                barPercentStr = percent
                percentStr ='-'

            else:
                # 小于 1% 的， 都显示 1% 长度，否则就看不见了
                barPercent = 1 if 0 < percent <= 1 else percent

                barPercentStr = f'{barPercent}%'
                percentStr = f'{percent}%'

            self.result_barchart.add(
                div(
                    span(statName),
                    div(
                        div(
                            "" , # 柱状里面不填写内容了，如果值为1.86%,背景色部分太短，由于颜色是白色，溢出到右边的空白背景，看不清
                            style=f'width: {barPercentStr}; background-color: {color};',
                            _class="barchart_bar",
                        ),
                        _class="barchart_barbox"
                    ),
                    _class="barchar_item"
                )
            )

        # add_barchar_item(
        #     f"用例总数 ： {ret['case_count']} 个",
        #     100,
        #     '#2196f3')


        def percentCalc(upper,lower):
            percent = str(round(upper * 100 / lower, 1))
            percent = percent[:-2] if percent.endswith('.0') else percent
            return percent

        percent = percentCalc(ret['case_pass'], case_count_to_run)
        add_barchar_item(
            f"{('用例通过','cases passed')[l.n]} {percent}% ： {ret['case_pass']} {('个','')[l.n]}",
            float(percent),
            '#04AA6D')

        percent = percentCalc(ret['case_fail'], case_count_to_run)
        add_barchar_item(
            f"{('用例失败','cases failed')[l.n]} {percent}% ： {ret['case_fail']} {('个','')[l.n]}",
            float(percent),
            '#bb4069')

        percent = percentCalc(ret['case_abort'], case_count_to_run)
        add_barchar_item(
            f"{('用例异常','cases exception aborted')[l.n]} {percent}% ： {ret['case_abort']} {('个','')[l.n]}",
            float(percent),
            '#9c27b0')


        percent = percentCalc(blocked_num, case_count_to_run)
        add_barchar_item(
            f"{('用例阻塞','cases blocked')[l.n]} {percent}% ： {blocked_num} {('个','')[l.n]}",
            float(percent),
            '#dcbdbd')

        # st_fail = ret['suite_setup_fail'] + ret['case_setup_fail'] + ret['suite_teardown_fail'] + ret['case_teardown_fail']
        # percent = '100%' if st_fail > 0 else '0%'
        # add_barchar_item(
        #     f"初始化/清除 失败  {st_fail} 次",
        #     percent,
        #     '#dcbdbd')


        # 产生文件
        htmlcontent = self.doc.render()

        timestamp = time.strftime('%Y%m%d_%H%M%S',time.localtime(stats.start_time))
        fileName = f'report_{timestamp}.html'
        reportPath = os.path.join('log',fileName)
        with open(reportPath,'w',encoding='utf8') as f:
            f.write(htmlcontent)

        if Settings.auto_open_report:
            try:
                my_os = platform.system().lower()
                if my_os == 'windows':
                    os.startfile(reportPath)
                elif my_os == 'darwin': # macOS
                    os.system(f'open {reportPath}')
            except:
                print(traceback.format_exc())

        #  with command line parameter report_url_prefix
        #  need to copy report from dir 'log' to 'reports'
        if Settings.report_url_prefix:
            os.makedirs('reports', exist_ok=True)
            cpTargetPath = os.path.join('reports',fileName)
            shutil.copyfile(reportPath, cpTargetPath)
            o1 = ('测试报告','test report')[l.n]
            print(f"{o1} : {Settings.report_url_prefix}/{fileName} \n")


    # def _findParentSuite(self,name):
    #     if name.endswith(os.path.sep):
    #         name = name[:-1]
        
    #     parentpath = os.path.dirname(name)

    #     # name 对应的 是用例根目录, 
    #     if  parentpath == '': 
    #         self._addSuiteDir(self.body,name)
    #         return None
        
    #     # rug 
    #     if parentpath not in self.suitepath2element:
    #         dirToCreate = []
    #         levels = parentpath.split(os.sep)
    #         cur = ''
    #         for level in levels:
    #             cur = os.path.join(cur,level)
            

    
    def enter_suite(self,name:str,suitetype): 
        _class = 'suite_'+suitetype

        enterInfo = ('进入目录','Enter Folder')[l.n] if suitetype == 'dir' else ('进入文件','Enter File')[l.n]
        self.curEle = self.logDiv.add(
            div(                
                div(
                    span(enterInfo,_class='label'),
                    span(name)
                ),         
                _class=_class, id=f'{_class} {name}'
            )
        )
        self.curSuiteEle = self.curEle
        self.curSuiteFilePath = name

        self.suitepath2element[name] = self.curEle
             
    
    def enter_case(self, caseId ,name, case_className):       
        # 执行有结果后，要修改这个 self.curCaseLableEle ，比如 加上 PASS
        self.curCaseLableEle = span(('用例','Case')[l.n],_class='label caselabel')

        # folder_body 是折叠区 内容部分，可以隐藏
        self.curCaseBodyEle = div(
            span(f'{self.curSuiteFilePath}::{case_className}', _class='case_class_path') , 
            _class='folder_body')
        self.curCaseEle = self.curSuiteEle.add(
            div(
                div(
                    self.curCaseLableEle,
                    span(name, _class='casename'),
                    span(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), _class='executetime'),
                    _class='folder_header'
                ),
                self.curCaseBodyEle ,
                _class='case',id=f'case_{caseId:08}'
               )
        )
        self.curEle = self.curCaseBodyEle

    
    def case_steps(self,name):          
        ele = div(
            span(('测试步骤','Test Steps')[l.n],_class='label'),
            _class='test_steps',id='test_steps '+name)        
        self.curEle = self.curCaseBodyEle.add(ele)

    
    # def case_pass(self, case, caseId, name): 
    #     self.curCaseEle['class'] += ' pass'
    #     self.curCaseLableEle += ' PASS'
    
    # def case_fail(self, case, caseId, name, e, stacktrace):
        
    #     self.curCaseEle['class'] += ' fail'
    #     self.curCaseLableEle += ' FAIL'

    #     stacktrace = "Traceback:\n" +stacktrace.split("\n",3)[3]
    #     self.curEle += div(f'{e} \n{stacktrace}', _class='info error-info')
        
    
    # def case_abort(self, case, caseId, name, e, stacktrace):
        
    #     self.curCaseEle['class'] += ' abort'
    #     self.curCaseLableEle += ' ABORT'

    #     stacktrace = "Traceback:\n" +stacktrace.split("\n",3)[3]
    #     self.curEle += div(f'{e} \n{stacktrace}', _class='info error-info')


    def case_result(self,case):
        if case.execRet == 'pass':
            self.curCaseEle['class'] += ' pass'
            self.curCaseLableEle += ' PASS'
        else:
            # Traceback 前3行信息多余， 不要
            stacktrace = "Traceback:\n" +case.stacktrace.split("\n",3)[3]
            if case.execRet == 'fail':
                # 如果 Traceback 后3行信息固定的是 common.py 里面的 AssertionError ，也多余， 不要
                if ', in CHECK_POINT' in  stacktrace:
                    stacktrace = stacktrace.rsplit("\n",4)[0]
                self.curCaseEle['class'] += ' fail'
                self.curCaseLableEle += ' FAIL'
                self.curEle += div(f'{case.error} \n{stacktrace}', _class='info error-info')
                
            elif case.execRet == 'abort':                
                self.curCaseEle['class'] += ' abort'
                self.curCaseLableEle += ' ABORT'

                self.curEle += div(f'{case.error} \n{stacktrace}', _class='info error-info')


            
    # utype 可能是 suite  case  case_default
    def setup(self,name, utype): 

        _class = f'{utype}_setup setup'
                     
        # 套件 setup
        if utype == 'suite':
            
            # folder_body 是折叠区 内容部分，可以隐藏
            stHeaderEle = div(
                span(('套件初始化','Suite Setup')[l.n],_class='label'),
                span(name),
                span(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), _class='executetime'),
                _class='folder_header')
            
            stBodyEle = self.curEle = div(_class='folder_body')
            
            self.curSetupEle = div(
                stHeaderEle,
                stBodyEle,
                _class=_class,
                id=f'{_class} {name}')   

            self.curSuiteEle.add(self.curSetupEle)  

        # 用例 setup
        else:
            
            self.curSetupEle = self.curEle = div(
                span(('用例初始化','Case Setup')[l.n],_class='label'),
                _class=_class,
                id=f'{_class} {name}')   

            self.curCaseBodyEle.add(self.curSetupEle)
            self.curEle['class'] += ' case_st_lable'
    
        
    # utype 可能是 suite  case  case_default
    def teardown(self,name, utype): 

        _class = f'{utype}_teardown teardown'

        # 套件 teardown
        if utype == 'suite':    
            
            # folder_body 是折叠区 内容部分，可以隐藏
            stHeaderEle = div(
                span(('套件清除','Suite Teardown')[l.n],_class='label'),
                span(name),
                span(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), _class='executetime'),
                _class='folder_header')
            
            stBodyEle = self.curEle = div(_class='folder_body')
            
            self.curTeardownEle = div(
                stHeaderEle,
                stBodyEle,
                _class=_class,
                id=f'{_class} {name}')   

            self.curSuiteEle.add(self.curTeardownEle)

        # 用例 teardown
        else:            
            self.curTeardownEle = self.curEle = div(
                span(('用例清除','Case Teardown')[l.n],_class='label'),
                _class=_class,
                id=f'{_class} {name}')       

            self.curCaseBodyEle.add(self.curTeardownEle)
            self.curEle['class'] += ' case_st_lable'


    
    def setup_fail(self,name, utype, e, stacktrace):  
        self.curSetupEle['class'] += ' fail'

        stacktrace = "Traceback:\n" +stacktrace.split("\n",3)[3]
        self.curEle += div(f'{utype} setup fail | {e} \n{stacktrace}', _class='info error-info')
    
    def teardown_fail(self,name, utype, e, stacktrace):           
        self.curTeardownEle['class'] += ' fail'

        stacktrace = "Traceback:\n" +stacktrace.split("\n",3)[3]
        self.curEle += div(f'{utype} teardown fail | {e} \n{stacktrace}', _class='info error-info')

    def info(self, msg):
        msg = f'{msg}'
        if self.curEle is None:
            return

        self.curEle += div(msg, _class='info')


    def step(self,stepNo,desc):
        if self.curEle is None:
            return

        self.curEle += div(span(f'{("步骤","Step")[l.n]} #{stepNo}', _class='tag'), span(desc), _class='case_step')

    def checkpoint_pass(self, desc):
        if self.curEle is None:
            return

        self.curEle += div(span(f'{("检查点","CheckPoint")[l.n]} PASS', _class='tag'), span(desc), _class='checkpoint_pass')
        
    def checkpoint_fail(self, desc):
        if self.curEle is None:
            return

        self.curEle += div(span(f'{("检查点","CheckPoint")[l.n]} FAIL', _class='tag'), span(desc), _class='checkpoint_fail')


    def log_img(self,imgPath: str, width: str = None):
        if self.curEle is None:
            return

        self.curEle += div(img(src=imgPath, width= 'aa' if width is None else width, _class='screenshot' ))



from .signal import signal

signal.register([
    stats,
    ConsoleLogger(), 
    TextLogger(), 
    HtmlLogger()])



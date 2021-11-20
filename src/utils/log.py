_f=' case_st_lable'
_e='green'
_d='tag'
_c=' fail'
_b='folder_header'
_a='executetime'
_Z='folder_body'
_Y='%Y%m%d_%H%M%S'
_X='用例'
_W='log'
_V='info error-info'
_U='%Y-%m-%d %H:%M:%S'
_T='abort'
_S='fail'
_R='pass'
_Q='utf8'
_P='case_count'
_O='case_count_toberun'
_N='label'
_M='Traceback:\n'
_L='suite'
_K='case_teardown_fail'
_J='suite_teardown_fail'
_I='case_setup_fail'
_H='suite_setup_fail'
_G='class'
_F='\n'
_E='case_pass'
_D='case_abort'
_C='case_fail'
_B='bright_red'
_A=None
import logging,os,time
from logging.handlers import RotatingFileHandler
from rich.console import Console
from rich.theme import Theme
from hytest.product import version
from datetime import datetime
from hytest.common import GSTORE
from .runner import Collector
os.makedirs(_W,exist_ok=True)
logger=logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)
logFile=os.path.join(_W,'testresult.log')
handler=RotatingFileHandler(logFile,maxBytes=1024*1024*30,backupCount=2,encoding=_Q)
handler.setLevel(logging.DEBUG)
formatter=logging.Formatter(fmt='%(message)s')
handler.setFormatter(formatter)
handler.doRollover()
logger.addHandler(handler)
console=Console(theme=Theme(inherit=False))
print=console.print
class LogLevel:level=0
class Stats:
	def test_start(self,_title='Test Report'):self.result={_O:Collector.case_number,_P:0,_E:0,_C:0,_D:0,_H:0,_I:0,_J:0,_K:0,'case_pass_list':[],'case_fail_list':[],'case_abort_list':[]};self.start_time=time.time()
	def test_end(self,runner):
		A='---ret---';self.end_time=time.time();self.test_duration=self.end_time-self.start_time
		if self.result[_C]or self.result[_D]or self.result[_H]or self.result[_I]or self.result[_J]or self.result[_K]:GSTORE[A]=1
		else:GSTORE[A]=0
	def enter_case(self,caseId,name,case_className):self.result[_P]+=1
	def case_result(self,case):
		if case.execRet==_R:self.result[_E]+=1
		elif case.execRet==_S:self.result[_C]+=1
		elif case.execRet==_T:self.result[_D]+=1
	def setup_fail(self,name,utype,e,stacktrace):
		if utype==_L:self.result[_H]+=1
		else:self.result[_I]+=1
	def teardown_fail(self,name,utype,e,stacktrace):
		if utype==_L:self.result[_J]+=1
		else:self.result[_K]+=1
stats=Stats()
class ConsoleLogger:
	def test_end(self,runner):A='white';ret=stats.result;print(f"\n\n  ========= 测试耗时 : {stats.test_duration:.3f} 秒 =========\n");print(f"\n  预备执行用例数量 : {ret[_O]}");print(f"\n  实际执行用例数量 : {ret[_P]}");print(f"\n  通过 : {ret[_E]}",style=_e);num=ret[_C];style=A if num==0 else _B;print(f"\n  失败 : {num}",style=style);num=ret[_D];style=A if num==0 else _B;print(f"\n  异常 : {num}",style=style);num=ret[_H];style=A if num==0 else _B;print(f"\n  套件初始化失败 : {num}",style=style);num=ret[_J];style=A if num==0 else _B;print(f"\n  套件清除  失败 : {num}",style=style);num=ret[_I];style=A if num==0 else _B;print(f"\n  用例初始化失败 : {num}",style=style);num=ret[_K];style=A if num==0 else _B;print(f"\n  用例清除  失败 : {num}",style=style)
	def enter_suite(self,name,suitetype):
		if suitetype=='file':print(f"\n\n>>> {name}",style='bold bright_black')
	def enter_case(self,caseId,name,case_className):print(f"\n* {name}",style='bright_white')
	def case_steps(self,name):...
	def case_result(self,case):
		if case.execRet==_R:print('                          PASS',style=_e)
		elif case.execRet==_S:print(f"                          FAIL\n{case.error}",style=_B)
		elif case.execRet==_T:print(f"                          ABORT\n{case.error}",style='magenta')
	def setup(self,name,utype):...
	def teardown(self,name,utype):...
	def setup_fail(self,name,utype,e,stacktrace):utype='套件'if utype==_L else _X;print(f"\n{utype} 初始化失败 | {name} | {e}",style=_B)
	def teardown_fail(self,name,utype,e,stacktrace):utype='套件'if utype==_L else _X;print(f"\n{utype} 清除失败 | {name} | {e}",style=_B)
	def debug(self,msg):
		if LogLevel.level>0:print(f"{msg}")
	def criticalInfo(self,msg):print(f"{msg}",style=_B)
class TextLogger:
	def test_start(self,_title=''):startTime=time.strftime(_Y,time.localtime(stats.start_time));logger.info(f"\n\n  ========= 测试开始 : {startTime} =========\n")
	def test_end(self,runner):endTime=time.strftime(_Y,time.localtime(stats.end_time));logger.info(f"\n\n  ========= 测试结束 : {endTime} =========\n");logger.info(f"\n  耗时    : {stats.end_time-stats.start_time:.3f} 秒\n");ret=stats.result;logger.info(f"\n  预备执行用例数量 : {ret[_O]}");logger.info(f"\n  实际执行用例数量 : {ret[_P]}");logger.info(f"\n  通过 : {ret[_E]}");logger.info(f"\n  失败 : {ret[_C]}");logger.info(f"\n  异常 : {ret[_D]}");logger.info(f"\n  套件初始化失败 : {ret[_H]}");logger.info(f"\n  套件清除  失败 : {ret[_J]}");logger.info(f"\n  用例初始化失败 : {ret[_I]}");logger.info(f"\n  用例清除  失败 : {ret[_K]}")
	def enter_suite(self,name,suitetype):logger.info(f"\n\n>>> {name}")
	def enter_case(self,caseId,name,case_className):curTime=datetime.now().strftime(_U);logger.info(f"\n* {name}  -  {curTime}")
	def case_steps(self,name):logger.info(f"\n  [ case execution steps ]")
	def case_result(self,case):
		if case.execRet==_R:logger.info('  PASS ')
		else:
			stacktrace=_M+case.stacktrace.split(_F,3)[3]
			if case.execRet==_S:logger.info(f"  FAIL   {case.error} \n{stacktrace}")
			elif case.execRet==_T:logger.info(f"  ABORT   {case.error} \n{stacktrace}")
	def setup(self,name,utype):logger.info(f"\n[ {utype} setup ] {name}")
	def teardown(self,name,utype):logger.info(f"\n[ {utype} teardown ] {name}")
	def setup_fail(self,name,utype,e,stacktrace):stacktrace=_M+stacktrace.split(_F,3)[3];logger.info(f"{utype} setup fail | {e} \n{stacktrace}")
	def teardown_fail(self,name,utype,e,stacktrace):stacktrace=_M+stacktrace.split(_F,3)[3];logger.info(f"{utype} teardown fail | {e} \n{stacktrace}")
	def info(self,msg):logger.info(msg)
	def debug(self,msg):
		if LogLevel.level>0:logger.debug(msg)
	def step(self,stepNo,desc):logger.info(f"\n-- 第 {stepNo} 步 -- {desc} \n")
	def checkpoint_pass(self,desc):logger.info(f"\n** 检查点 **  {desc} ---->  通过\n")
	def checkpoint_fail(self,desc):logger.info(f"\n** 检查点 **  {desc} ---->  !! 不通过!!\n")
	def criticalInfo(self,msg):logger.info(f"!!! {msg} !!!")
	def log_img(self,imgPath,width=_A):logger.info(f"图 {imgPath}")
from dominate.tags import *
from dominate.util import raw
from dominate import document
class HtmlLogger:
	def __init__(self):self.curEle=_A
	def test_start(self,_title=''):
		A='menu-item'
		with open(os.path.join(os.path.dirname(__file__),'report.css'),encoding=_Q)as f:_css_style=f.read()
		with open(os.path.join(os.path.dirname(__file__),'report.js'),encoding=_Q)as f:_js=f.read()
		self.doc=document(title=f"测试报告");self.doc.head.add(meta(charset='UTF-8'),style(raw(_css_style)),script(raw(_js),type='text/javascript'));self.main=self.doc.body.add(div(_class='main_section'));self.main.add(h1(f"测试报告 - hytest v{version}",style='font-family: auto'));self.main.add(h3(f"统计结果"));resultDiv=self.main.add(div(_class='result'));self.result_table,self.result_barchart=resultDiv.add(table(_class='result_table'),div(_class='result_barchart'));_,self.logDiv=self.main.add(div(h3('执行日志',style='display:inline'),style='margin-top:2em'),div(_class='exec_log'));self.ev=div(div('∧',_class=A,onclick='previous_error()',title='上一个错误'),div('∨',_class=A,onclick='next_error()',title='下一个错误'),_class='error_jumper');self.main.add(div(div('页首',_class=A,onclick='document.querySelector("body").scrollIntoView()'),div('教程',_class=A,onclick='window.open("http://www.byhy.net/tut/auto/hytest/01", "_blank"); '),div('精简',_class=A,id='display_mode',onclick='toggle_folder_all_cases()'),self.ev,id='float_menu'));self.curEle=self.main;self.curSuiteEle=_A;self.curCaseEle=_A;self.curCaseLableEle=_A;self.curSetupEle=_A;self.curTeardownEle=_A;self.suitepath2element={}
	def test_end(self,runner):
		B='%Y%m%d %H:%M:%S';A='color:red';execStartTime=time.strftime(B,time.localtime(stats.start_time));execEndTime=time.strftime(B,time.localtime(stats.end_time));ret=stats.result;errorNum=0;trs=[];trs.append(tr(td('开始时间'),td(f"{execStartTime}")));trs.append(tr(td('结束时间'),td(f"{execEndTime}")));trs.append(tr(td('耗时'),td(f"{stats.test_duration:.3f} 秒")));trs.append(tr(td('预备执行用例数量'),td(f"{ret[_O]}")));trs.append(tr(td('实际执用例行数量'),td(f"{ret[_P]}")));trs.append(tr(td('通过'),td(f"{ret[_E]}")));case_count_toberun=ret[_O];num=ret[_C];style=''if num==0 else A;trs.append(tr(td('失败'),td(f"{num}",style=style)));errorNum+=num;num=ret[_D];style=''if num==0 else A;trs.append(tr(td('异常'),td(f"{num}",style=style)));errorNum+=num;blocked_num=case_count_toberun-ret[_E]-ret[_C]-ret[_D];style=''if blocked_num==0 else A;trs.append(tr(td('阻塞'),td(f"{blocked_num}",style=style)));num=ret[_H];style=''if num==0 else A;trs.append(tr(td('套件初始化失败'),td(f"{num}",style=style)));errorNum+=num;num=ret[_J];style=''if num==0 else A;trs.append(tr(td('套件清除失败'),td(f"{num}",style=style)));errorNum+=num;num=ret[_I];style=''if num==0 else A;trs.append(tr(td('用例初始化失败'),td(f"{num}",style=style)));errorNum+=num;num=ret[_K];style=''if num==0 else A;trs.append(tr(td('用例清除失败'),td(f"{num}",style=style)));errorNum+=num;self.ev['display']='none'if errorNum==0 else'block';self.result_table.add(tbody(*trs))
		def add_barchar_item(statName,percent,color):
			if type(percent)==str:barPercentStr=percent;percentStr='-'
			else:barPercent=1 if 0<percent<=1 else percent;barPercentStr=f"{barPercent}%";percentStr=f"{percent}%"
			self.result_barchart.add(div(span(statName),div(div(percentStr,style=f"width: {barPercentStr}; background-color: {color};",_class='barchart_bar'),_class='barchart_barbox'),_class='barchar_item'))
		def percentCalc(upper,lower):percent=str(round(upper*100/lower,2));percent=percent[:-2]if percent.endswith('.0')else percent;return percent
		percent=percentCalc(ret[_E],case_count_toberun);add_barchar_item(f"用例通过 {percent}% ： {ret[_E]} 个",float(percent),'#04AA6D');percent=percentCalc(ret[_C],case_count_toberun);add_barchar_item(f"用例失败 {percent}% ： {ret[_C]} 个",float(percent),'#bb4069');percent=percentCalc(ret[_D],case_count_toberun);add_barchar_item(f"用例异常 {percent}% ： {ret[_D]} 个",float(percent),'#9c27b0');percent=percentCalc(blocked_num,case_count_toberun);add_barchar_item(f"用例阻塞 {percent}% ： {blocked_num} 个",float(percent),'#dcbdbd');htmlcontent=self.doc.render();timestamp=time.strftime(_Y,time.localtime(stats.start_time));reportFile=os.path.join(_W,f"log_{timestamp}.html")
		with open(reportFile,'w',encoding=_Q)as f:f.write(htmlcontent)
		try:os.startfile(reportFile)
		except:
			try:os.system(f"open {reportFile}")
			except:...
	def enter_suite(self,name,suitetype):_class='suite_'+suitetype;enterInfo='进入目录'if suitetype=='dir'else'进入文件';self.curEle=self.logDiv.add(div(div(span(enterInfo,_class=_N),span(name)),_class=_class,id=f"{_class} {name}"));self.curSuiteEle=self.curEle;self.curSuiteFilePath=name;self.suitepath2element[name]=self.curEle
	def enter_case(self,caseId,name,case_className):self.curCaseLableEle=span(_X,_class='label caselabel');self.curCaseBodyEle=div(span(f"{self.curSuiteFilePath}::{case_className}",_class='case_class_path'),_class=_Z);self.curCaseEle=self.curSuiteEle.add(div(div(self.curCaseLableEle,span(name,_class='casename'),span(datetime.now().strftime(_U),_class=_a),_class=_b),self.curCaseBodyEle,_class='case',id=f"case_{caseId:08}"));self.curEle=self.curCaseBodyEle
	def case_steps(self,name):ele=div(span('测试步骤',_class=_N),_class='test_steps',id='test_steps '+name);self.curEle=self.curCaseBodyEle.add(ele)
	def case_result(self,case):
		if case.execRet==_R:self.curCaseEle[_G]+=' pass';self.curCaseLableEle+=' PASS'
		else:
			stacktrace=_M+case.stacktrace.split(_F,3)[3]
			if case.execRet==_S:
				if', in CHECK_POINT'in stacktrace:stacktrace=stacktrace.rsplit(_F,4)[0]
				self.curCaseEle[_G]+=_c;self.curCaseLableEle+=' FAIL';self.curEle+=div(f"{case.error} \n{stacktrace}",_class=_V)
			elif case.execRet==_T:self.curCaseEle[_G]+=' abort';self.curCaseLableEle+=' ABORT';self.curEle+=div(f"{case.error} \n{stacktrace}",_class=_V)
	def setup(self,name,utype):
		_class=f"{utype}_setup setup"
		if utype==_L:stHeaderEle=div(span('套件初始化',_class=_N),span(name),span(datetime.now().strftime(_U),_class=_a),_class=_b);stBodyEle=self.curEle=div(_class=_Z);self.curSetupEle=div(stHeaderEle,stBodyEle,_class=_class,id=f"{_class} {name}");self.curSuiteEle.add(self.curSetupEle)
		else:self.curSetupEle=self.curEle=div(span('用例初始化',_class=_N),_class=_class,id=f"{_class} {name}");self.curCaseBodyEle.add(self.curSetupEle);self.curEle[_G]+=_f
	def teardown(self,name,utype):
		_class=f"{utype}_teardown teardown"
		if utype==_L:stHeaderEle=div(span('套件清除',_class=_N),span(name),span(datetime.now().strftime(_U),_class=_a),_class=_b);stBodyEle=self.curEle=div(_class=_Z);self.curTeardownEle=div(stHeaderEle,stBodyEle,_class=_class,id=f"{_class} {name}");self.curSuiteEle.add(self.curTeardownEle)
		else:self.curTeardownEle=self.curEle=div(span('用例清除',_class=_N),_class=_class,id=f"{_class} {name}");self.curCaseBodyEle.add(self.curTeardownEle);self.curEle[_G]+=_f
	def setup_fail(self,name,utype,e,stacktrace):self.curSetupEle[_G]+=_c;stacktrace=_M+stacktrace.split(_F,3)[3];self.curEle+=div(f"{utype} setup fail | {e} \n{stacktrace}",_class=_V)
	def teardown_fail(self,name,utype,e,stacktrace):self.curTeardownEle[_G]+=_c;stacktrace=_M+stacktrace.split(_F,3)[3];self.curEle+=div(f"{utype} teardown fail | {e} \n{stacktrace}",_class=_V)
	def info(self,msg):
		if self.curEle is _A:return
		self.curEle+=div(msg,_class='info')
	def step(self,stepNo,desc):
		if self.curEle is _A:return
		self.curEle+=div(span(f"第 {stepNo} 步",_class=_d),span(desc),_class='case_step')
	def checkpoint_pass(self,desc):
		if self.curEle is _A:return
		self.curEle+=div(span(f"检查点 PASS",_class=_d),span(desc),_class='checkpoint_pass')
	def checkpoint_fail(self,desc):
		if self.curEle is _A:return
		self.curEle+=div(span(f"检查点 FAIL",_class=_d),span(desc),_class='checkpoint_fail')
	def log_img(self,imgPath,width=_A):
		if self.curEle is _A:return
		self.curEle+=div(img(src=imgPath,width='aa'if width is _A else width,_class='screenshot'))
from .signal import signal
signal.register([stats,ConsoleLogger(),TextLogger(),HtmlLogger()])
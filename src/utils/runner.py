_Q='casefile'
_P='.py'
_O='test_teardown'
_N='test_setup'
_M='default_tags'
_L='--teardown--'
_K='name'
_J='st'
_I='suite_setup'
_H='force_tags'
_G='type'
_F='suite_teardown'
_E='__st__.py'
_D=None
_C=False
_B=True
_A='cases'
import os,types,importlib.util,fnmatch,traceback
from .signal import signal
def tagmatch(pattern):
	for tag in Collector.current_case_tags:
		if fnmatch.fnmatch(tag,pattern):return _B
	return _C
class Collector:
	SUITE_TAGS=[_H,_M];SUITE_STS=[_I,_F,_N,_O];exec_list=[];exec_table={};case_number=0;suite_tag_table={_H:{},_M:{}};current_case_tags=[]
	@classmethod
	def run(cls,casedir=_A,suitename_filters=[],casename_filters=[],tag_include_expr=_D,tag_exclude_expr=_D):
		for (dirpath,dirnames,filenames) in os.walk(casedir):
			if _E in filenames:filenames.remove(_E);filenames.insert(0,_E)
			for fn in filenames:
				filepath=os.path.join(dirpath,fn)
				if not filepath.endswith(_P):continue
				signal.debug(f"\n=== {filepath} \n");module_name=fn[:-3];spec=importlib.util.spec_from_file_location(module_name,filepath);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);cls.handleOneModule(module,filepath,tag_include_expr,tag_exclude_expr,suitename_filters,casename_filters)
		sts,cases=[],[]
		for filepath in cls.exec_list:
			if filepath.endswith('py'):cases.append(filepath)
			else:sts.append(filepath)
		for stPath in sts:
			valid=_C
			for casePath in cases:
				if casePath.startswith(stPath):valid=_B;break
			if not valid:cls.exec_list.remove(stPath);cls.exec_table.pop(stPath)
	@classmethod
	def handleOneModule(cls,module,filepath,tag_include_expr,tag_exclude_expr,suitename_filters,casename_filters):
		stType=filepath.endswith(_E);caseType=not stType
		if stType:filepath=filepath.replace(_E,'')
		meta={_G:_Q if caseType else _J}
		if caseType:meta[_A]=[]
		for (name,item) in module.__dict__.items():
			if isinstance(item,list):
				if name in cls.SUITE_TAGS:
					if not item:continue
					meta[name]=item;cls.suite_tag_table[name][filepath]=item
			elif isinstance(item,types.FunctionType):
				if name in cls.SUITE_STS:meta[name]=item
			elif caseType and isinstance(item,type):
				if not hasattr(item,'teststeps'):signal.debug(f"no teststeps in class {name}, skip it.");continue
				if hasattr(item,_K):meta[_A].append(item())
				elif hasattr(item,'ddt_cases'):
					for caseData in item.ddt_cases:case=item();case.name,case.para=caseData[_K],caseData['para'];meta[_A].append(case)
				else:item.name=name;meta[_A].append(item())
		new_suite_tag_table={}
		for (tname,table) in cls.suite_tag_table.items():new_suite_tag_table[tname]={p:v for(p,v)in table.items()if filepath.startswith(p)}
		cls.suite_tag_table=new_suite_tag_table
		if caseType:
			if not meta[_A]:signal.debug(f"\n--- finally, no cases in this module , skip it.");return
			cls.caseFilter(filepath,meta,tag_include_expr,tag_exclude_expr,suitename_filters,casename_filters)
			if not meta[_A]:signal.debug(f"\n--- finally, no cases in this module , skip it.");return
			cls.case_number+=len(meta[_A])
		elif len(meta)==1:signal.debug(f"\n--- finally, no setup/teardown/tags in this module , skip it.");return
		cls.exec_list.append(filepath);cls.exec_table[filepath]=meta
	@classmethod
	def caseFilter(cls,filepath,meta,tag_include_expr,tag_exclude_expr,suitename_filters,casename_filters):
		if not tag_include_expr and not tag_exclude_expr and not suitename_filters and not casename_filters:return
		if not tag_exclude_expr and suitename_filters:
			suitenames=filepath.split(os.path.sep);suitenames=[sn[:-3]if sn.endswith(_P)else sn for sn in suitenames]
			if cls._patternMatch(suitenames,suitename_filters):return
		passedCases=[]
		for caseClass in meta[_A]:
			signal.debug(f"\n* {caseClass.name}");suite_tags=[t for tl in cls.suite_tag_table[_H].values()for t in tl];case_tags=getattr(caseClass,'tags',[]);cls.current_case_tags=set(suite_tags+case_tags)
			if tag_exclude_expr:
				if eval(tag_exclude_expr)==_B:signal.debug(f"excluded for meeting expr : {tag_exclude_expr}");continue
				elif not casename_filters and not suitename_filters and not tag_include_expr:passedCases.append(caseClass);continue
			if casename_filters:
				caseName=getattr(caseClass,_K)
				if cls._patternMatch([caseName],casename_filters):passedCases.append(caseClass);continue
			if tag_include_expr:
				if eval(tag_include_expr)==_B:passedCases.append(caseClass);continue
			signal.debug(f"excluded for not meet any include rules")
		meta[_A]=passedCases
	@classmethod
	def _patternMatch(cls,names,patterns):
		for name in names:
			for pattern in patterns:
				if fnmatch.fnmatch(name,pattern):return _B
		return _C
class Runner:
	curRunningCase=_D;case_list=[]
	@classmethod
	def run(cls):
		if not Collector.exec_list:signal.criticalInfo('没有可以执行的测试用例');return 2
		cls.caseId=0
		for (name,meta) in Collector.exec_table.items():
			if meta[_G]==_J and _F in meta:cls._insertTeardownToExecList(name)
		signal.test_start();cls.execTest();signal.test_end(cls);from hytest.common import GSTORE;return GSTORE.get('---ret---',3)
	@classmethod
	def execTest(cls):
		A='suite';suite_setup_failed_list=[]
		for name in Collector.exec_list:
			affected=_C
			for suite_setup_failed in suite_setup_failed_list:
				if name.startswith(suite_setup_failed):affected=_B;break
			if affected:continue
			if name.endswith(_L):
				name=name.replace(_L,'');suite_teardown=Collector.exec_table[name][_F];signal.teardown(name,A)
				try:suite_teardown()
				except Exception as e:signal.teardown_fail(name,A,e,traceback.format_exc())
			else:
				meta=Collector.exec_table[name]
				if meta[_G]==_J:
					signal.enter_suite(name,'dir');suite_setup=meta.get(_I)
					if suite_setup:
						signal.setup(name,A)
						try:suite_setup()
						except Exception as e:signal.setup_fail(name,A,e,traceback.format_exc());suite_setup_failed_list.append(name)
				elif meta[_G]==_Q:
					signal.enter_suite(name,'file');suite_setup=meta.get(_I)
					if suite_setup:
						signal.setup(name,A)
						try:suite_setup()
						except Exception as e:signal.setup_fail(name,A,e,traceback.format_exc());continue
					cls._exec_cases(meta);suite_teardown=meta.get(_F)
					if suite_teardown:
						signal.teardown(name,A)
						try:suite_teardown()
						except Exception as e:signal.teardown_fail(name,A,e,traceback.format_exc())
	@classmethod
	def _insertTeardownToExecList(cls,stName):
		findStart=_C;insertPos=-1
		for (pos,name) in enumerate(Collector.exec_list):
			if not findStart:
				if name!=stName:continue
				else:findStart=_B
			elif not name.startswith(stName):insertPos=pos;break
		tearDownName=stName+_L
		if insertPos==-1:Collector.exec_list.append(tearDownName)
		else:Collector.exec_list.insert(insertPos,tearDownName)
	@classmethod
	def _exec_cases(cls,meta):
		B='case_default';A='case';test_setup=meta.get(_N);test_teardown=meta.get(_O)
		for case in meta[_A]:
			cls.case_list.append(case);case_className=type(case).__name__;cls.caseId+=1;signal.enter_case(cls.caseId,case.name,case_className);cls.curRunningCase=case;caseSetup=getattr(case,'setup',_D)
			if caseSetup:
				signal.setup(case.name,A)
				try:caseSetup()
				except Exception as e:signal.setup_fail(case.name,A,e,traceback.format_exc());continue
			elif test_setup:
				signal.setup(case.name,B)
				try:test_setup()
				except Exception as e:signal.setup_fail(case.name,B,e,traceback.format_exc());continue
			signal.case_steps(case.name)
			try:case.execRet='pass';case.teststeps();signal.case_result(case)
			except AssertionError as e:case.execRet='fail';case.error=e;case.stacktrace=traceback.format_exc();signal.case_result(case)
			except Exception as e:case.execRet='abort';case.error=e;case.stacktrace=traceback.format_exc();signal.case_result(case)
			caseTeardown=getattr(case,'teardown',_D)
			if caseTeardown:
				signal.teardown(case.name,A)
				try:caseTeardown()
				except Exception as e:signal.teardown_fail(case.name,A,e,traceback.format_exc())
			elif test_teardown:
				signal.teardown(case.name,B)
				try:test_teardown()
				except Exception as e:signal.teardown_fail(case.name,B,e,traceback.format_exc())
if __name__=='__main__':Collector.run();Runner.run()
_Q = 'casefile'
_P = '.py'
_O = 'test_teardown'
_N = 'test_setup'
_M = 'default_tags'
_L = '--teardown--'
_K = 'name'
_J = 'st'
_I = 'suite_setup'
_H = 'force_tags'
_G = 'type'
_F = None
_E = 'suite_teardown'
_D = '__st__.py'
_C = False
_B = True
_A = 'cases'
already_setup = {}

import os,types,importlib.util,fnmatch,traceback
from .signal import signal
from logzero import logger


def tagmatch(pattern):
    for tag in Collector.current_case_tags:
        if fnmatch.fnmatch(tag, pattern): return _B
    return _C


class Collector:
    SUITE_TAGS = [_H, _M];
    SUITE_STS = [_I, _E, _N, _O];
    exec_list = [];
    exec_table = {};
    suite_tag_table = {_H: {}, _M: {}};
    current_case_tags = []

    @classmethod
    def run(cls, casedir=_A, suitename_filters=[], casename_filters=[], tag_include_expr=_F, tag_exclude_expr=_F):
        for (dirpath, dirnames, filenames) in os.walk(casedir):
            if _D in filenames: filenames.remove(_D);filenames.insert(0, _D)
            for fn in filenames:
                filepath = os.path.join(dirpath, fn)
                if not filepath.endswith(_P): continue
                signal.debug(f"\n=== {filepath} \n");
                module_name = fn[:-3];
                spec = importlib.util.spec_from_file_location(module_name, filepath);
                module = importlib.util.module_from_spec(spec);
                spec.loader.exec_module(module);
                cls.handleOneModule(module, filepath, tag_include_expr, tag_exclude_expr, suitename_filters,
                                    casename_filters)
        sts, cases = [], []
        for filepath in cls.exec_list:
            if filepath.endswith('py'):
                cases.append(filepath)
            else:
                sts.append(filepath)
        for stPath in sts:
            valid = _C
            for casePath in cases:
                if casePath.startswith(stPath): valid = _B;break
            if not valid: cls.exec_list.remove(stPath);cls.exec_table.pop(stPath)

    @classmethod
    def handleOneModule(cls, module, filepath, tag_include_expr, tag_exclude_expr, suitename_filters, casename_filters):
        stType = filepath.endswith(_D);
        caseType = not stType
        if stType: filepath = filepath.replace(_D, '')
        meta = {_G: _Q if caseType else _J}
        if caseType: meta[_A] = []
        cls_ddt = 'cls_ddt_cases' in module.__dict__.keys()
        for (name, item) in module.__dict__.items():
            if isinstance(item, list):
                if name in cls.SUITE_TAGS:
                    if not item: continue
                    meta[name] = item;
                    cls.suite_tag_table[name][filepath] = item
            elif isinstance(item, types.FunctionType):
                if name in cls.SUITE_STS: meta[name] = item
            elif caseType and isinstance(item, type):
                if not hasattr(item, 'teststeps'): signal.debug(f"no teststeps in class {name}, skip it.");continue
                if not cls_ddt:
                    if hasattr(item, _K) and not hasattr(item, 'ddt_cases'):
                        meta[_A].append(item())
                    elif hasattr(item, 'ddt_cases'):
                        for caseData in item.ddt_cases:
                            case = item();
                            case.name, case.para = caseData[_K], caseData['para'];
                            meta[_A].append(case)
                    else:
                        item.name = name;
                        meta[_A].append(item())
                else:
                    cls_ddt_cases = module.__dict__['cls_ddt_cases']
                    for cls_data in cls_ddt_cases:
                        if hasattr(item, _K) and not hasattr(item, 'ddt_cases'):
                            case = item()
                            case.cls_para = cls_data['cls_para']
                            case.name = f"{cls_data['cls_name']}-{case.name}"
                            meta[_A].append(case)
                        elif hasattr(item, 'ddt_cases'):
                            for caseData in item.ddt_cases:
                                case = item()
                                case.cls_para = cls_data['cls_para']
                                case.name, case.para = f"{cls_data['cls_name']}-{caseData[_K]}", caseData['para'];
                                meta[_A].append(case)
                        else:
                            case = item()
                            case.cls_para = cls_data['cls_para']
                            case.name = f"{cls_data['cls_name']}-{name}"
                            meta[_A].append(case)
        new_suite_tag_table = {}
        for (tname, table) in cls.suite_tag_table.items(): new_suite_tag_table[tname] = {p: v for (p, v) in
                                                                                         table.items() if
                                                                                         filepath.startswith(p)}
        cls.suite_tag_table = new_suite_tag_table
        if caseType:
            if not meta[_A]: signal.debug(f"\n--- finally, no cases in this module , skip it.");return
            cls.caseFilter(filepath, meta, tag_include_expr, tag_exclude_expr, suitename_filters, casename_filters)
            if not meta[_A]: signal.debug(f"\n--- finally, no cases in this module , skip it.");return
        elif len(meta) == 1:
            signal.debug(f"\n--- finally, no setup/teardown/tags in this module , skip it.");return
        cls.exec_list.append(filepath);
        cls.exec_table[filepath] = meta

    @classmethod
    def caseFilter(cls, filepath, meta, tag_include_expr, tag_exclude_expr, suitename_filters, casename_filters):
        if not tag_include_expr and not tag_exclude_expr and not suitename_filters and not casename_filters: return
        if not tag_exclude_expr and suitename_filters:
            suitenames = filepath.split(os.path.sep);
            suitenames = [sn[:-3] if sn.endswith(_P) else sn for sn in suitenames]
            if cls._patternMatch(suitenames, suitename_filters): return
        passedCases = []
        for caseClass in meta[_A]:
            signal.debug(f"\n* {caseClass.name}");
            suite_tags = [t for tl in cls.suite_tag_table[_H].values() for t in tl];
            case_tags = getattr(caseClass, 'tags', []);
            cls.current_case_tags = set(suite_tags + case_tags)
            if tag_exclude_expr:
                if eval(tag_exclude_expr) == _B:
                    signal.debug(f"excluded for meeting expr : {tag_exclude_expr}");continue
                elif not casename_filters and not suitename_filters and not tag_include_expr:
                    passedCases.append(caseClass);continue
            if casename_filters:
                caseName = getattr(caseClass, _K)
                if cls._patternMatch([caseName], casename_filters): passedCases.append(caseClass);continue
            if tag_include_expr:
                if eval(tag_include_expr) == _B: passedCases.append(caseClass);continue
            signal.debug(f"excluded for not meet any include rules")
        meta[_A] = passedCases

    @classmethod
    def _patternMatch(cls, names, patterns):
        for name in names:
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern): return _B
        return _C


class Runner:
    @classmethod
    def run(cls,result,event):
        if not Collector.exec_list:
            signal.criticalInfo('没有可以执行的测试用例')
            result.append(2)
            return
        # return 2
        cls.caseId = 0
        for (name, meta) in Collector.exec_table.items():
            if meta[_G] == _J and _E in meta: cls._insertTeardownToExecList(name)
        signal.testStart()
        code = cls.execTest(event)
        if code:
            result.append(code)
            signal.criticalInfo('恢复原状失败')
            return
        signal.test_end(cls)
        from hytest.common import GSTORE
        result.append(GSTORE.get('---ret---', 3))
        return

    @classmethod
    def execTest(cls,event):
        A = 'suite';
        suite_setup_failed_list = []
        for name in Collector.exec_list:
            affected = _C
            for suite_setup_failed in suite_setup_failed_list:
                if name.startswith(suite_setup_failed): affected = _B;break
            if affected: continue
            if name.endswith(_L):
                name = name.replace(_L, '');
                suite_teardown = Collector.exec_table[name][_E];
                signal.teardown(name, A)
                try:
                    suite_teardown()
                except Exception as e:
                    signal.teardown_fail(name, A, e, traceback.format_exc())
            else:
                meta = Collector.exec_table[name]
                if meta[_G] == _J:
                    signal.enter_suite(name, 'dir');
                    suite_setup = meta.get(_I)
                    if suite_setup:
                        signal.setup(name, A)
                        try:
                            suite_setup()
                        except Exception as e:
                            signal.setup_fail(name, A, e, traceback.format_exc());suite_setup_failed_list.append(name)
                        else:
                            if not already_setup.__contains__(name):
                                already_setup[name] = suite_setup

                elif meta[_G] == _Q:
                    signal.enter_suite(name, 'file');
                    suite_setup = meta.get(_I)
                    if suite_setup:
                        signal.setup(name, A)
                        try:
                            suite_setup()
                        except Exception as e:
                            signal.setup_fail(name, A, e, traceback.format_exc());continue
                    # 开启监控
                    event.set()
                    code = cls._exec_cases(meta, event);
                    if code:
                        return code
                    suite_teardown = meta.get(_E)
                    if suite_teardown:
                        signal.teardown(name, A)
                        try:
                            suite_teardown()
                        except Exception as e:
                            signal.teardown_fail(name, A, e, traceback.format_exc())
                        finally:
                            already_setup.pop(name)

    @classmethod
    def _insertTeardownToExecList(cls, stName):
        findStart = _C;
        insertPos = -1
        for (pos, name) in enumerate(Collector.exec_list):
            if not findStart:
                if name != stName:
                    continue
                else:
                    findStart = _B
            elif not name.startswith(stName):
                insertPos = pos;break
        tearDownName = stName + _L
        if insertPos == -1:
            Collector.exec_list.append(tearDownName)
        else:
            Collector.exec_list.insert(insertPos, tearDownName)

    @classmethod
    def _exec_cases(cls, meta,event):
        B = 'case_default';
        A = 'case';
        test_setup = meta.get(_N);
        test_teardown = meta.get(_O)
        for case in meta[_A]:
            while not event.is_set():
                logger.warn('Wait for recover')
                for dir, item in already_setup.items():
                    logger.info(f'开始恢复-{dir} suite_setup')
                    try:
                        item()
                    except Exception as e:
                        raise Exception(f'"{dir}" :恢复原先状态失败\n{e}')
                        return 3
                event.set()
            case_className = type(case).__name__
            cls.caseId += 1
            signal.enter_case(cls.caseId, case.name, case_className)
            caseSetup = getattr(case, 'setup', _F)
            if caseSetup:
                signal.setup(case.name, A)
                try:
                    caseSetup()
                except Exception as e:
                    signal.setup_fail(case.name, A, e, traceback.format_exc());continue
            elif test_setup:
                signal.setup(case.name, B)
                try:
                    test_setup()
                except Exception as e:
                    signal.setup_fail(case.name, B, e, traceback.format_exc());continue
            signal.case_steps(case.name)
            try:
                case.teststeps();signal.case_pass(cls.caseId, case.name)
            except AssertionError as e:
                signal.case_fail(cls.caseId, case.name, e, traceback.format_exc())
            except Exception as e:
                signal.case_abort(cls.caseId, case.name, e, traceback.format_exc())
            caseTeardown = getattr(case, 'teardown', _F)
            if caseTeardown:
                signal.teardown(case.name, A)
                try:
                    caseTeardown()
                except Exception as e:
                    signal.teardown_fail(case.name, A, e, traceback.format_exc())
            elif test_teardown:
                signal.teardown(case.name, B)
                try:
                    test_teardown()
                except Exception as e:
                    signal.teardown_fail(case.name, B, e, traceback.format_exc())


if __name__ == '__main__': Collector.run();Runner.run()

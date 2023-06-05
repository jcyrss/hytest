from hytest import INFO,GSTORE
from lib.share import  gs

force_tags = ['功能测试']


def suite_setup():
    GSTORE['你 好'] = '吼吼吼吼吼吼吼吼吼吼吼吼吼吼吼吼'
    GSTORE.hello = 'hellooooooooooooooooooooooo'
    gs.driver = 'abc'
    INFO('总初始化')


def suite_teardown():
    INFO('总清除')
    pass


from hytest import signal

# class MySignalHandler:
#     TEST_RET_COL_NO = 6 # 测试结果在用例excel文件中的列数
#
#     def __init__(self) -> None:
#         self.caseNum2Row = {} # 用例编号->行数 表
#         self.getCaseNum2RowInExcel()
#
#         import win32com.client
#         self.excel = win32com.client.Dispatch("Excel.Application")
#         self.excel.Visible = True
#         workbook = self.excel.Workbooks.Open(r"h:\tcs-api.xlsx")
#         self.sheet = workbook.Sheets(1)
#
#     def getCaseNum2RowInExcel(self):
#         """
#         得到Excel 中用例 编号对应的行数，方便填写测试结果
#         """
#         import xlrd
#         book = xlrd.open_workbook(r"h:\tcs-api.xlsx")
#         sheet = book.sheet_by_index(0)
#         caseNumbers = sheet.col_values(colx=1)
#         print(caseNumbers)
#
#         for row, cn in enumerate(caseNumbers):
#             if '-' in cn:
#                 self.caseNum2Row[cn] = row + 1
#
#         print(self.caseNum2Row)
#
#     def case_result(self, case):
#         """
#         case_result 是 每个用例执行结束 ，会调用的函数
#
#         @param case: 用例类 实例
#         @return:
#         """
#         import time
#         time.sleep(0.1)
#         # 找到对应的测试用例在excel中的行数
#         if ' - ' not in case.name :
#             return
#
#         caseNo = case.name.split(' - ')[-1].strip()
#
#         cell = self.sheet.Cells(self.caseNum2Row[caseNo], self.TEST_RET_COL_NO)
#
#         self.excel.ActiveWindow.ScrollRow = self.caseNum2Row[caseNo]-2
#
#         if case.execRet == 'pass':
#             cell.Value = 'pass'
#             cell.Font.Color =  0xBF00
#         else:
#             cell.Font.Color =  0xFF
#             if case.execRet == 'fail':
#                 cell.Value = 'fail'
#
#             elif case.execRet == 'abort':
#                 cell.Value = 'abort'
#
#     def test_end(self, runner):
#         """
#         test_end 整个测试执行完 ，会调用的函数
#
#         @param runner.case_list:  列表，里面包含了每个用例类 实例
#         """
#         for case in runner.case_list:
#             print(f'{case.name} --- {case.execRet}')
#
# # 注册这个类的实例 为一个 hytest 信号处理对象
# signal.register(MySignalHandler())

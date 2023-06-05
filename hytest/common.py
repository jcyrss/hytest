from .utils.signal import signal
from .utils.runner import Runner
from datetime import datetime
from .cfg import l

class _GlobalStore:
    def __getitem__(self, key, default=None):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            return default
    def __setitem__(self,key,value):
        setattr(self, key, value )

    get = __getitem__

# used for storing global shared data
GSTORE = _GlobalStore()

def INFO(info):
    """
    print information in log and report.
    This will not show in terminal window.

    Parameters
    ----------
    info : object to print
    """
    signal.info(f'{info}')

def STEP(stepNo:int,desc:str):
    """
    print information about test steps in log and report .
    This will not show in terminal window.


    Parameters
    ----------
    stepNo : step number
    desc :   description about this step
    """
    signal.step(stepNo,desc)


def CHECK_POINT(desc:str, condition, failStop=True, failLogScreenWebDriver = None):
    """
    check point of testing.
    pass or fail of this check point depends on argument condition is true or false.
    it will print information about check point in log and report.

    Parameters
    ----------
    desc :    check point description, like check what.
    condition : usually it's a bool expression, like  `a==b`, 
        so actually, after evaluating the expression, it's a result bool object passed in .
    failStop : switch for whether continue this test cases when the condition is false 
    failLogScreenWebDriver : Selenium web driver object,
        when you want a screenshot image of browser in test report if current check point fail.
    """

    if condition:
        signal.checkpoint_pass(desc)
    else:
        signal.checkpoint_fail(desc)

        # 如果需要截屏
        if failLogScreenWebDriver is not None:
            SELENIUM_LOG_SCREEN(failLogScreenWebDriver)

        # 记录下当前执行结果为失败
        Runner.curRunningCase.execRet='fail'
        Runner.curRunningCase.error=('检查点不通过','checkpoint failed')[l.n]
        Runner.curRunningCase.stacktrace="\n"*3+('具体错误看测试步骤检查点','see checkpoint of case for details')[l.n]
        # 如果失败停止，中止此测试用例
        if failStop:
            raise AssertionError()

def LOG_IMG(imgPath: str, width: str = None):
    """
    add image in test report

    Parameters
    ----------
    imgPath: the path of image
    width:  display width of image in html, like 50% / 800px / 30em 
    """

    signal.log_img(imgPath, width)


def SELENIUM_LOG_SCREEN(driver, width: str = None):
    """
    add screenshot image of browser into test report when using Selenium
    在日志中加入selenium控制的 浏览器截屏图片

    Parameters
    ----------
    driver: selenium webdriver
    width:  display width of image in html, like 50% / 800px / 30em 
    """
    filename = datetime.now().strftime('%Y%m%d%H%M%S%f')
    filepath = f'log/imgs/{filename}.png'
    filepath_relative_to_log = f'imgs/{filename}.png'
    driver.get_screenshot_as_file(filepath)
    signal.log_img(filepath_relative_to_log, width)
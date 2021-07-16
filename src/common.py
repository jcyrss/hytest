from .utils.signal import signal
from datetime import datetime



# 存储 全局共享 数据
GSTORE = {}

def INFO(info):
    """
    在日志和测试报告中打印 重要信息，
    使得 运行报告更加清晰

    参数：
    @param info :   信息描述
    """
    signal.info(f'{info}')

def STEP(stepNo:int,desc:str):
    """
    在日志和测试报告中打印出 测试步骤说明，
    使得 运行报告更加清晰

    参数：
    @param stepNo : 指定 是第几步
    @param desc :   步骤描述
    """
    signal.step(stepNo,desc)


def CHECK_POINT(desc:str, condition):
    """
    检查点

    参数：
    @param desc :   检查点文字描述
    @param condition ： 检查点 表达式
    """

    if condition:
        signal.checkpoint_pass(desc)
    else:
        signal.checkpoint_fail(desc)
        raise AssertionError()

def LOG_IMG(imgPath: str, width: str = None):
    """
    在日志中加入图片

    @param imgPath: 插入日志的图片路径
    @param width:  图片html 显示宽度， 可以是 50% / 800px / 30em 这些格式
    """

    signal.log_img(imgPath, width)


def SELENIUM_LOG_SCREEN(driver, width: str = None):
    """
    在日志中加入selenium控制的 浏览器截屏图片

    @param driver: selenium webdriver对象
    @param width:  图片html 显示宽度， 可以是 50% / 800px / 30em 这些格式
    """
    filename = datetime.now().strftime('%Y%m%d%H%M%S%f')
    filepath = f'log/imgs/{filename}.png'
    filepath_relative_to_log = f'imgs/{filename}.png'
    driver.get_screenshot_as_file(filepath)
    signal.log_img(filepath_relative_to_log, width)
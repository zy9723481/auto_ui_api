# 路径处理工具，用于创建文件夹
from pathlib import Path

class BasePage:
    """
    所有页面的父类（基类）
    作用：封装所有页面公共操作：等待元素、截图、公共方法
    遵循 PO 模式（Page Object）设计思想
    """

    def __init__(self, page):
        """
        构造方法：初始化页面
        :param page: playwright 提供的页面对象，所有操作靠它
        """
        self.page = page

    def wait_visible(self, locator):
        """
        公共方法：等待元素 可见
        :param locator: 元素定位器（CSS 或 XPath）
        """
        self.page.wait_for_selector(
            locator,
            state="visible",   # 等待状态：可见
            timeout=10000      # 超时时间：10秒
        )

    def wait_clickable(self, locator):
        """
        公共方法：等待元素 可被点击
        """
        self.page.wait_for_selector(
            locator,
            state="attached",
            timeout=10000
        )

    def screenshot(self, name="error"):
        """
        公共方法：自动截图（用例失败时调用）
        :param name: 截图名称
        """
        # 创建截图文件夹，不存在则自动创建
        Path("./screenshot").mkdir(exist_ok=True)
        # 执行截图，保存到项目根目录 screenshot 文件夹
        self.page.screenshot(
            path=f"screenshot/{name}.png",
            full_page=True    # 截取整个网页
        )
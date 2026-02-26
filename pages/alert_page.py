from common.base import BasePage
from common.config import config

class AlertPage(BasePage):
    """
    JS弹框（Alert）处理
    """
    def __init__(self, page):
        super().__init__(page)
        self.url = config.data["ui_url"] + "/alerts" + ".html"

    def open(self):
        self.page.goto(self.url)

    def click_and_accept(self):
        """
        点击按钮并自动接受弹窗
        """
        # 监听弹窗，出现就自动确认
        self.page.on("dialog", lambda d: d.accept())
        self.page.click("a[onclick=\"alert('cheese');\"]")
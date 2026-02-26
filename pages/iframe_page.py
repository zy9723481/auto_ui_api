from common.base import BasePage
from common.config import config

class IFramePage(BasePage):
    """
    内嵌页面（iframe）操作
    很多后台管理系统、富文本都会用到
    """
    def __init__(self, page):
        super().__init__(page)
        self.url = config.data["ui_url"] + "/iframes" + ".html"

    def open(self):
        self.page.goto(self.url)

    def edit_iframe(self, content):
        """
        切换到iframe并输入内容
        """
        frame = self.page.frame_locator("#mce_0_ifr")
        frame.locator("#tinymce").clear()
        frame.locator("#tinymce").fill(content)
from common.base import BasePage
from common.config import config

class WindowPage(BasePage):
    """
    多窗口、多标签页操作
    """
    def __init__(self, page):
        super().__init__(page)
        self.url = config.data["base_url"] + "/windows"

    def open(self):
        self.page.goto(self.url)

    def open_new_window(self):
        """
        打开新窗口并获取文本
        """
        with self.page.expect_popup() as popup_info:
            self.page.click("#windowButton")
        new_page = popup_info.value
        text = new_page.locator("h3").text_content()
        new_page.close()
        return text
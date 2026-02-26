from common.base import BasePage
from common.config import config

class WindowPage(BasePage):
    """
    多窗口、多标签页操作
    """
    def __init__(self, page):
        super().__init__(page)
        self.url = config.data["ui_url"] + "/window_switching_tests/page_with_frame.html"

    def open(self):
        self.page.goto(self.url)

    def open_new_window(self):
        """
        打开新窗口并获取其中指定元素的文本内容（Playwright 处理新窗口的标准写法）
        :return: 新窗口中 h3 标签的文本内容
        """
        # 1. 预注册新窗口监听（核心步骤）
        # expect_popup() 是 Playwright 内置的上下文管理器，用于监听页面弹出的新窗口/新标签页
        # 必须在触发新窗口的操作（点击链接）前执行，否则无法捕获新窗口
        with self.page.expect_popup() as popup_info:
            # 2. 点击触发新窗口的链接（ID 为 a-link-that-opens-a-new-window 的元素）
            # 点击该链接后会弹出新窗口，此时 expect_popup() 会捕获到这个新窗口对象
            self.page.click("#a-link-that-opens-a-new-window")
        
        # 3. 获取捕获到的新窗口对象
        # popup_info.value 是 expect_popup() 捕获到的新窗口 Page 实例，和主页面 self.page 用法一致
        new_page = popup_info.value
        
        # 4. 定位新窗口中的 h3 标签并获取其文本内容
        # text_content()：获取元素的文本内容（包括隐藏文本），若需获取可见文本用 inner_text()
        text = new_page.locator("xpath=/html/body/div").text_content()
        
        # 5. 关闭新窗口（避免残留多个窗口影响后续操作）
        new_page.close()
        
        # 6. 返回新窗口中获取到的文本内容
        return text
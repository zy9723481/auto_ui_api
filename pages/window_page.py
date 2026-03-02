from common.base import BasePage
from common.config import config


class WindowPage(BasePage):
    """
    多窗口、多标签页操作
    仅适配 Playwright 驱动运行
    核心场景：新窗口打开、窗口切换、内容获取、窗口关闭
    """

    def __init__(self, driver):
        """
        初始化多窗口操作页面
        :param driver: Playwright的page对象（统一命名为driver）
        """
        # 调用父类初始化方法，传入Playwright驱动
        super().__init__(driver)
        # 页面基础URL：从全局配置读取UI基础地址，拼接多窗口测试页面路径
        self.url = config.data["ui_url"] + "/window_switching_tests/page_with_frame.html"

        # 元素定位器（Playwright原生写法，统一维护）
        # 触发新窗口的链接定位器（通过ID精准匹配）
        self.loc_new_window_link = "#a-link-that-opens-a-new-window"
        # 新窗口中目标文本元素定位器（XPath）
        self.loc_new_window_text = "xpath=/html/body/div"

    def open(self):
        """
        打开多窗口测试页面
        复用父类BasePage封装的open方法（适配Playwright超时配置）
        """
        # 调用父类open方法，传入当前页面的URL
        super().open(self.url)

    def open_new_window(self):
        """
        核心业务方法：打开新窗口并获取其中指定元素的文本内容
        Playwright 处理新窗口的标准写法：先监听 → 触发 → 捕获 → 操作
        :return: 新窗口中目标元素的文本内容
        """
        # 1. 预注册新窗口监听（核心前置步骤）
        # expect_popup() 是 Playwright 内置上下文管理器，监听新窗口/新标签页弹出
        # 必须在触发新窗口操作前执行，否则无法捕获新窗口
        with self.driver.expect_popup() as popup_info:
            # 2. 点击链接触发新窗口（使用统一维护的定位器）
            self.driver.click(self.loc_new_window_link)

        # 3. 获取捕获到的新窗口对象
        # popup_info.value 是新窗口的 Page 实例，用法和主驱动一致
        new_page = popup_info.value

        # 4. 定位新窗口目标元素并获取文本内容
        # text_content()：获取元素所有文本（含隐藏），可见文本可用 inner_text()
        text = new_page.locator(self.loc_new_window_text).text_content()

        # 5. 关闭新窗口（避免残留窗口影响后续操作）
        new_page.close()

        # 6. 返回新窗口获取的文本内容
        return text
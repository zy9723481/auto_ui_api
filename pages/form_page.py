# 继承公共页面基类
from common.base import BasePage
# 导入全局配置
from common.config import config

class FormPage(BasePage):
    """
    表单页面
    PO模式：元素定位 + 业务操作 全部封装在这里
    """
    def __init__(self, page):
        super().__init__(page)
        # 从配置读取URL
        self.url = config.data["ui_url"] + "/web-form" + ".html"


        # 元素定位统一写这里，便于维护
        self.input_text = "[name='my-text']"
        self.input_pwd = "[name='my-password']"
        self.textarea = "[name='my-textarea']"
        self.submit = "button[type='submit']"
        self.result = "h1"

    def open(self):
        """打开页面"""
        self.page.goto(self.url)

    def fill_form(self, text, password, textarea):
        """
        填写表单业务方法
        """
        self.wait_visible(self.input_text)
        self.page.fill(self.input_text, text)
        self.page.fill(self.input_pwd, password)
        self.page.fill(self.textarea, textarea)

    def submit_form(self):
        """提交表单"""
        self.wait_clickable(self.submit)
        self.page.click(self.submit)

    def get_result(self):
        """获取提交结果"""
        self.wait_visible(self.result)
        return self.page.locator(self.result).text_content().strip()
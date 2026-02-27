# 继承公共页面基类
from common.base import BasePage
# 导入全局配置
from common.config import config

class FormPage(BasePage):
    """
    表单页面（仅适配 Playwright 驱动）
    PO模式：元素定位 + 业务操作 全部封装在这里
    """
    def __init__(self, driver):  # 入参为Playwright的page对象，统一命名为driver
        super().__init__(driver)
        # 从配置文件读取基础URL，拼接表单页面完整地址
        self.url = config.data["ui_url"] + "/web-form.html"

        # ========== 元素定位器（Playwright原生CSS选择器） ==========
        # 文本输入框
        self.input_text = "[name='my-text']"
        # 密码输入框
        self.input_pwd = "[name='my-password']"
        # 文本域输入框
        self.textarea = "[name='my-textarea']"
        # 提交按钮
        self.submit = "button[type='submit']"
        # 提交结果展示区域
        self.result = "h1"

    def open(self):
        """
        直接使用 self.url，调用父类Playwright版open方法
        """
        # 方式1：复用父类封装的 open 方法（适配Playwright超时）
        super().open(self.url) # 调用Playwright的goto方法打开页面

    def fill_form(self, text, password, textarea):
        """
        填写表单核心业务方法
        :param text: 文本输入框要填写的内容
        :param password: 密码输入框要填写的内容
        :param textarea: 文本域要填写的内容
        """
        # 等待文本输入框可见（复用父类封装的等待方法）
        self.wait_visible(self.input_text)
        # 填充文本输入框
        self.driver.fill(self.input_text, text)
        # 填充密码输入框
        self.driver.fill(self.input_pwd, password)
        # 填充文本域
        self.driver.fill(self.textarea, textarea)

    def submit_form(self):
        """提交表单（点击提交按钮）"""
        # 等待提交按钮可点击（避免元素未加载完成点击失效）
        self.wait_clickable(self.submit)
        # 点击提交按钮
        self.driver.click(self.submit)

    def get_result(self):
        """
        获取表单提交后的结果文本
        :return: 结果区域的纯文本内容（去除首尾空格）
        """
        # 等待结果区域可见
        self.wait_visible(self.result)
        # 定位结果元素并获取文本内容，去除首尾空格后返回
        return self.driver.locator(self.result).text_content().strip()
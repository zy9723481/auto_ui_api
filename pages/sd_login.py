from common.base import BasePage
from common.config import config
from selenium.webdriver.common.by import By


class LoginPage(BasePage):


    def __init__(self, driver):
        """
        初始化页面
        :param driver: sel的page对象（统一命名为driver）
        """
        # 调用父类初始化方法，传入sel驱动
        super().__init__(driver)
        # 页面基础URL：从全局配置读取UI基础地址
        self.url = config.data["ui_saucedemo_url"]
        #账号文本框-元素-ID定位
        self.input_name = (By.ID,"user-name")
        #密码文本框-元素-ID定位
        self.input_pwd = (By.ID,"password")
        #登录按钮-元素-ID定位
        self.click_submit=(By.ID,"login-button")

        #登录成功logo文本-元素-xpath定位
        self.logo_img_text=(By.XPATH,"/html/body/div/div/div/div[1]/div[1]/div[2]/div")
        #登录失败-提示-元素-xpath定位
        self.error_message = (By.XPATH,"/html/body/div/div/div[2]/div[1]/div/div/form/div[3]/h3")

        self
    def open(self):
        """
        直接使用 self.url，调用父类open方法
        """
        # 复用父类封装的 open 方法
        super().open(self.url) # 调用goto方法打开页面

    def send_name_or_pwd(self, text, password):
        """
        填写表单核心业务方法
        :param text: 文本输入框要填写的内容
        :param password: 密码输入框要填写的内容
        :param textarea: 文本域要填写的内容
        """
        # 填充文本输入框
        self.Find_element_send_keys(self.input_name,text)
        # 填充密码输入框
        self.Find_element_send_keys(self.input_pwd, password)

    def submit(self):
        """提交表单（点击提交按钮）"""
        # 点击提交按钮
        self.Find_element_clicks(self.click_submit)

    def get_error_message(self):
        """获取异常提示，并返回提示"""
        error_txt=self.search_element(self.error_message)
        return error_txt.text

    def get_login_message(self):
        """获取登录成功，并返回提示"""
        login_txt = self.search_element(self.logo_img_text)
        return login_txt.text

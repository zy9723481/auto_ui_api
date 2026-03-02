from common.base import BasePage
from common.config import config


class IFramePage(BasePage):
    """
    内嵌页面（iframe）操作
    仅适配 Playwright 驱动运行
    核心场景：后台管理系统、富文本编辑器等内嵌iframe的页面操作
    """

    def __init__(self, driver):
        """
        初始化IFrame页面
        :param driver: Playwright的page对象（统一命名为driver）
        """
        # 调用父类初始化方法，传入Playwright驱动
        super().__init__(driver)
        # 页面基础URL：从全局配置读取UI基础地址，拼接iframe测试页面路径
        self.url = config.data["ui_url"] + "/iframes" + ".html"

        # 元素定位器（Playwright原生写法）
        # iframe定位器（通过ID精准匹配目标内嵌框架）
        self.loc_iframe = "#iframe1"
        # iframe内邮箱输入框
        self.loc_iframe_email = "#email"
        # iframe内年龄输入框
        self.loc_iframe_age = "#age"

    def open(self):
        """
        打开iframe测试页面
        复用父类BasePage封装的open方法（适配Playwright超时配置）
        """
        # 调用父类open方法，传入当前页面的URL
        super().open(self.url)

    def edit_iframe(self, email, age):
        """
        核心业务方法：切换到iframe并填写邮箱、年龄内容
        :param email: 要填写到iframe内邮箱输入框的内容
        :param age: 要填写到iframe内年龄输入框的内容
        """
        # 步骤1：定位目标iframe（Playwright frame_locator 原生方法）
        frame = self.driver.frame_locator(self.loc_iframe)

        # 步骤2：填写iframe内邮箱输入框
        frame.locator(self.loc_iframe_email).fill(email)

        # 步骤3：填写iframe内年龄输入框
        frame.locator(self.loc_iframe_age).fill(age)
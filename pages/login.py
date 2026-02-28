from common.base import BasePage
from common.config import config


class LoginPage(BasePage):


    def __init__(self, driver):
        """
        初始化页面
        :param driver: Playwright的page对象（统一命名为driver）
        """
        # 调用父类初始化方法，传入Playwright驱动
        super().__init__(driver)
        # 页面基础URL：从全局配置读取UI基础地址，拼接弹框测试页面路径
        self.url = config.data["ui_url"] + "/alerts" + ".html"
        # 元素定位器：Playwright原生CSS选择器
        # 触发Alert弹窗的按钮（通过onclick事件定位，精准匹配目标按钮）
        self.loc_alert_btn = "a[onclick=\"alert('cheese');\"]"

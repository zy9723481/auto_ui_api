from common.base import BasePage
from common.config import config


class AlertPage(BasePage):
    """
    JS弹框（Alert）处理页面
    仅适配 Playwright 驱动运行（已移除所有Selenium兼容逻辑）
    核心功能：触发JS Alert弹窗并自动确认弹窗
    """

    def __init__(self, driver):
        """
        初始化Alert页面
        :param driver: Playwright的page对象（统一命名为driver）
        """
        # 调用父类初始化方法，传入Playwright驱动
        super().__init__(driver)
        # 页面基础URL：从全局配置读取UI基础地址，拼接弹框测试页面路径
        self.url = config.data["ui_url"] + "/alerts" + ".html"
        # 元素定位器：Playwright原生CSS选择器
        # 触发Alert弹窗的按钮（通过onclick事件定位，精准匹配目标按钮）
        self.loc_alert_btn = "a[onclick=\"alert('cheese');\"]"

    def open(self):
        """
        打开Alert弹框测试页面
        复用父类BasePage封装的open方法（内置Playwright的goto+超时配置）
        """
        # 调用父类open方法，传入当前页面的URL
        super().open(self.url)

    def click_and_accept(self):
        """
        核心业务方法：点击触发弹窗的按钮，并自动接受（确认）Alert弹窗
        Playwright特性：提前监听dialog事件，弹窗出现时自动执行accept()
        """
        # 等待弹窗按钮可点击（复用父类等待方法，避免元素未加载完成点击失效）
        self.wait_clickable(self.loc_alert_btn)

        # 步骤1：监听dialog事件（Alert弹窗属于dialog类型），弹窗出现时自动确认
        # lambda d: d.accept()：匿名函数，接收dialog对象并执行确认操作
        self.driver.on("dialog", lambda d: d.accept())

        # 步骤2：点击按钮触发Alert弹窗
        # 点击后会触发dialog事件，上面的监听逻辑会自动确认弹窗
        self.driver.click(self.loc_alert_btn)
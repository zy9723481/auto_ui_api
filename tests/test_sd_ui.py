import allure
import pytest
from pages.sd_login import LoginPage
from common.yaml_util import read_yaml
from selenium.webdriver.common.by import By

@allure.feature("UI自动化测试合集")
class TestUI_Sd:
    @allure.story("登录功能")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("data", read_yaml("data/login_data.yaml")["test_login"])
    def test_login(self, selenium_driver, data):
        """
        改造后：适配登录成功/失败双场景，失败用例校验错误提示，执行后重置环境
        :param selenium_driver: Selenium驱动fixture（建议设为function级别，自动重开浏览器）
        :param data: 数据驱动的测试用例数据
        """
        # 初始化登录页面对象
        login = LoginPage(selenium_driver)
        try:
            with allure.step(f"打开登录页面：{login.url}"):
                login.open()  # 每次用例都重新打开登录页，避免缓存影响

            with allure.step(f"输入登录信息 - 用户名：{data['username']}，密码：******"):
                # 先清空输入框（避免残留内容），再输入
                login.send_name_or_pwd(data["username"], data["password"])

            with allure.step("点击登录按钮"):
                login.submit()

            # ========== 核心改造：区分成功/失败场景 ==========
            if "expect_error_msg" in data:
                # 场景1：登录失败 - 校验错误提示
                with allure.step(f"校验登录失败错误提示：{data['expect_error_msg']}"):
                    # 获取页面实际错误提示
                    actual_error_msg = login.get_error_message()
                    # 附加错误提示到Allure报告
                    allure.attach(actual_error_msg, "实际错误提示", allure.attachment_type.TEXT)
                    # 断言：实际错误提示与预期一致
                    assert actual_error_msg == data["expect_error_msg"], \
                        f"错误提示校验失败！预期：{data['expect_error_msg']}，实际：{actual_error_msg}"
                with allure.step("登录失败，重置环境（刷新页面）"):
                    # 方案1：刷新页面（轻量，保留浏览器）
                    selenium_driver.refresh()
                    # 方案2：重开浏览器（彻底，需fixture配合，注释备用）
                    # selenium_driver.quit()
                    # from selenium import webdriver
                    # selenium_driver = webdriver.Chrome()

            else:
                # 场景2：登录成功 - 原有校验逻辑
                with allure.step(f"校验登录成功：页面包含『Swag Labs』"):
                    actual_result = login.get_login_message()
                    allure.attach(actual_result, "实际页面内容", allure.attachment_type.TEXT)
                    assert "Swag Labs" in actual_result, \
                        f"登录成功校验失败！实际结果：{actual_result}"
        except Exception as e:
            # 异常处理：截图+附加异常信息
            screenshot_data = login.screenshot()
            allure.attach(
                screenshot_data,
                name=f"{data['case_name']}执行失败",
                attachment_type=allure.attachment_type.PNG
            )
            allure.attach(str(e), "异常详情", allure.attachment_type.TEXT)
            raise e  # 抛出异常，标记用例失败
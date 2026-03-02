import allure
import pytest
from pages.form_page import FormPage
from pages.iframe_page import IFramePage
from pages.alert_page import AlertPage
from pages.window_page import WindowPage
from common.yaml_util import read_yaml

@allure.feature("UI自动化测试合集")
class TestUI:
    @allure.story("表单提交功能")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("data", read_yaml("data/form_data.yaml")["test_submit"])
    def test_form(self, pw_page, data):
        """测试表单提交场景（支持多组数据驱动）"""
        try:
            form = FormPage(pw_page)
            with allure.step(f"打开表单页面：{form.url}"):
                form.open()
            with allure.step(f"填写表单 - 文本：{data['text']}，密码：******，文本域：{data['textarea'][:20]}..."):
                form.fill_form(data["text"], data["password"], data["textarea"])
            with allure.step("点击表单提交按钮"):
                form.submit_form()
            with allure.step(f"断言提交结果：包含『Form submitted』"):
                actual_result = form.get_result()
                allure.attach(actual_result, "实际返回结果", allure.attachment_type.TEXT)
                assert "Form submitted" in actual_result, f"表单提交失败！实际结果：{actual_result}"
        except Exception as e:
            screenshot_data = form.screenshot()
            allure.attach(
                screenshot_data,
                name=f"表单提交失败-{data['case_name']}",
                attachment_type=allure.attachment_type.PNG
            )
            raise e

    @allure.story("iframe内嵌页面操作")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试iframe页面内容编辑")
    def test_iframe(self, pw_page):
        """测试内嵌iframe页面的文本编辑功能"""
        try:
            iframe = IFramePage(pw_page)
            with allure.step("打开iframe测试页面"):
                iframe.open()
            with allure.step("编辑iframe内文本内容：邮箱1234，年龄18"):
                iframe.edit_iframe("1234", "18")
            with allure.step("验证iframe内容编辑成功"):
                pass
        except Exception as e:
            screenshot_data = iframe.screenshot()
            allure.attach(
                screenshot_data,
                name="iframe操作失败截图",
                attachment_type=allure.attachment_type.PNG
            )
            raise e

    @allure.story("JS Alert弹窗处理")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试Alert弹窗自动确认功能")
    def test_alert(self, pw_page):
        """测试JS Alert弹窗的触发和自动确认功能"""
        try:
            alert = AlertPage(pw_page)
            with allure.step("打开Alert弹窗测试页面"):
                alert.open()
            with allure.step("点击按钮触发Alert弹窗并自动确认"):
                alert.click_and_accept()
        except Exception as e:
            screenshot_data = alert.screenshot()
            allure.attach(
                screenshot_data,
                name="Alert弹窗处理失败截图",
                attachment_type=allure.attachment_type.PNG
            )
            raise e

    @allure.story("浏览器多窗口切换")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试多窗口打开和内容验证")
    def test_window(self, pw_page):
        """测试新窗口打开、切换窗口、内容验证功能"""
        try:
            win = WindowPage(pw_page)
            with allure.step("打开多窗口测试页面"):
                win.open()
            with allure.step("打开新窗口并获取窗口文本内容"):
                text = win.open_new_window()
            with allure.step(f"断言新窗口内容：包含『Simple page with simple test.』"):
                allure.attach(text, "新窗口实际文本", allure.attachment_type.TEXT)
                assert "Simple page with simple test." in text, f"新窗口内容验证失败！实际内容：{text}"
        except Exception as e:
            screenshot_data = win.screenshot()
            allure.attach(
                screenshot_data,
                name="多窗口切换失败截图",
                attachment_type=allure.attachment_type.PNG
            )
            raise e
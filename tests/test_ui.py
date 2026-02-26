# allure测试报告装饰器
import allure
# pytest测试框架
import pytest
# 导入各个页面类
from pages.form_page import FormPage
from pages.iframe_page import IFramePage
from pages.alert_page import AlertPage
from pages.window_page import WindowPage
# 导入YAML数据驱动工具
from common.yaml_util import read_yaml

# allure报告模块名称
@allure.feature("UI自动化")
class TestUI:
    """UI自动化测试用例集合"""

    # 数据驱动：从yaml读取多组测试数据
    @pytest.mark.parametrize("data", read_yaml("data/form_data.yaml")["test_submit"])
    # allure子模块名称
    @allure.story("表单提交")
    def test_form(self, page, data):
        """
        测试表单提交
        :param page: conftest中定义的fixture
        :param data: 数据驱动传入的测试数据
        """
        # 实例化页面对象
        form = FormPage(page)
        # 打开页面
        form.open()
        # 填写表单
        form.fill_form(data["text"], data["password"], data["textarea"])
        # 提交
        form.submit_form()
        # 断言结果
        assert "Form submitted" in form.get_result()

    @allure.story("iframe操作")
    def test_iframe(self, page):
        """测试内嵌页面iframe"""
        iframe = IFramePage(page)
        iframe.open()
        iframe.edit_iframe("PyCharm运行成功")

    @allure.story("alert弹窗")
    def test_alert(self, page):
        """测试JS弹框"""
        alert = AlertPage(page)
        alert.open()
        alert.click_and_accept()

    @allure.story("多窗口")
    def test_window(self, page):
        """测试多窗口切换"""
        win = WindowPage(page)
        win.open()
        text = win.open_new_window()
        assert "Simple page with simple test." in text
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    """
    全局唯一浏览器 fixture
    scope="session"：整个测试只启动一次浏览器
    新增：使用本地 Chrome 浏览器，无需下载 Playwright 自带版本
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # False=显示浏览器，True=无界面
            # ******** 核心修改：添加以下两行 ********
            executable_path=r"D:\chrome-win64\chrome.exe",  # 本地 Chrome 路径
            args=["--no-sandbox", "--disable-gpu"]  # 避免 Chrome 安全/兼容性报错
        )
        yield browser       # 提供给测试用例
        browser.close()    # 测试结束关闭

@pytest.fixture(scope="function")
def page(browser):
    """
    每个用例一个全新页面
    防止用例之间相互污染
    """
    page = browser.new_page()
    yield page
    page.close()
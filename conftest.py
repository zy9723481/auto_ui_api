import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    """
    适配 Linux 服务器的 Playwright 浏览器配置
    1. 不指定本地 Chrome 路径，使用 Playwright 自带的 Chromium
    2. 启用 headless=True（Linux 服务器无桌面，必须无界面运行）
    3. 添加 Linux 必要的启动参数
    """
    with sync_playwright() as p:
        # 关键修改：去掉 executable_path，使用 Playwright 自带浏览器
        browser = p.chromium.launch(
            headless=True,  # Linux 必须开启无界面模式
            args=[
                "--no-sandbox",  # Linux 下禁用沙箱（权限问题）
                "--disable-gpu",  # 禁用 GPU 加速
                "--disable-dev-shm-usage",  # 解决 Linux 内存不足问题
                "--remote-debugging-port=9222"  # 可选：调试用
            ]
        )
        yield browser
        # 测试结束后关闭浏览器
        browser.close()
@pytest.fixture(scope="function")
def page(browser):
    """
    每个用例一个全新页面
    防止用例之间相互污染
    """
    page = browser.new_page()
    yield page
    page.close()
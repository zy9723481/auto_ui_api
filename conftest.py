import os
import sys
import pytest
from playwright.sync_api import sync_playwright
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ===================== 核心：环境判断工具函数 =====================
def is_jenkins_env():
    """
    判断当前是否为 Jenkins 运行环境
    依据：Jenkins 会自动注入 JENKINS_URL 环境变量
    备用判断：路径包含 /root/.jenkins/ 或 系统为 Linux
    """
    # 方式1：通过 Jenkins 环境变量（最准确）
    if os.getenv("JENKINS_URL"):
        return True
    # 方式2：通过系统路径/系统类型兜底
    if sys.platform == "linux" and "/root/.jenkins/" in os.getcwd():
        return True
    return False

# ===================== Playwright 兼容配置（核心修改：复用本地Chrome路径） =====================
@pytest.fixture(scope="session")
def pw_browser():
    """
    Playwright 浏览器 fixture（兼容本地/Jenkins）
    核心修复：本地环境强制使用系统Chrome，避免Playwright自带版本路径错误
    命名前缀 pw_ 区分 selenium，避免冲突
    """
    is_jenkins = is_jenkins_env()
    with sync_playwright() as p:
        # 公共配置
        launch_kwargs = {
            "args": [
                "--no-sandbox",  # 兼容 Linux/Jenkins 权限
                "--disable-dev-shm-usage",  # 解决 Linux 内存不足
                "--start-maximized"  # 窗口最大化（全环境通用）
            ]
        }

        # ******** 核心修改：复用本地Chrome绝对路径，解决路径报错 ********
        if not is_jenkins:  # 本地环境（Windows）
            # Windows 本地 Chrome 路径（根据你的实际路径调整！！！）
            launch_kwargs["executable_path"] = r"D:\chrome-win64\chrome.exe"
            # 本地环境：有界面调试（和你单框架一致）
            launch_kwargs["headless"] = False
        else:
            # Jenkins/Linux 环境：无界面 + 禁用GPU（用Playwright自带Chromium）
            launch_kwargs["headless"] = True
            launch_kwargs["args"].extend(["--disable-gpu"])

        # 启动浏览器（兼容本地/Jenkins）
        browser = p.chromium.launch(**launch_kwargs)
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def pw_page(pw_browser):
    """Playwright 页面 fixture（每个用例全新页面）"""
    page = pw_browser.new_page()
    # 本地环境设置窗口大小（最大化）
    if not is_jenkins_env():
        page.set_viewport_size({"width": 1920, "height": 1080})
    yield page
    page.close()

# ===================== Selenium 兼容配置（保留原有逻辑） =====================
@pytest.fixture(scope="session")
def selenium_driver():
    """
    Selenium ChromeDriver fixture（兼容本地/Jenkins）
    自动下载匹配版本的 chromedriver，无需手动管理
    """
    is_jenkins = is_jenkins_env()
    chrome_options = Options()

    # 公共配置
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)


    # 环境差异化配置
    if is_jenkins:
        # Jenkins/Linux 环境：无界面 + 权限适配
        chrome_options.add_argument("--headless=new")  # 新版 headless
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
    else:
        # 本地环境：有界面 + 最大化
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--ignore-certificate-errors")  # 忽略证书错误（本地调试）

    # 自动下载 chromedriver（兼容所有系统）
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # 设置隐式等待时间（元素查找超时时间）30秒
    driver.implicitly_wait(30)
    yield driver
    driver.quit()

# ===================== 可选：通用驱动 fixture（按需切换框架） =====================
@pytest.fixture(scope="function", params=["playwright", "selenium"])
def ui_driver(request, pw_page, selenium_driver):
    """
    通用 UI 驱动 fixture，可批量跑两套框架的用例
    params 控制要执行的框架，注释掉其中一个则只跑对应框架
    """
    if request.param == "playwright":
        yield pw_page
    elif request.param == "selenium":
        yield selenium_driver
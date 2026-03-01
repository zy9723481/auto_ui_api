import os
import sys
import platform
import pytest
from playwright.sync_api import sync_playwright
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# ===================== 核心：环境判断 + 路径配置工具函数 =====================
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


def get_system_type():
    """判断当前系统类型（windows/linux），适配不同版本的Chrome/ChromeDriver"""
    sys_platform = platform.system().lower()
    return "windows" if sys_platform == "windows" else "linux"


def get_browser_driver_path():
    """
    核心：根据你实际的目录结构，拼接 Chrome 浏览器和 ChromeDriver 的绝对路径
    实际目录结构（从你的终端输出提取）：
    auto_ui_api/
    ├── browser/
    │   ├── windows/Chrome/chrome.exe                # Windows Chrome 路径
    │   └── linux/chrome-headless-shell-linux64/chrome-headless-shell  # Linux Chrome 无头版路径
    ├── driver/
    │   ├── windows/chromedriver-win64/chromedriver.exe  # Windows ChromeDriver 路径
    │   └── linux/chromedriver-linux64/chromedriver      # Linux ChromeDriver 路径
    """
    # 项目根目录（当前文件所在目录，即 auto_ui_api/）
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys_type = get_system_type()

    # ========== 拼接 Chrome 浏览器路径（适配你的实际多级目录） ==========
    if sys_type == "windows":
        # Windows Chrome 路径：browser/windows/Chrome/chrome.exe
        chrome_path = os.path.join(
            project_root,
            "browser",
            "windows",
            "Chrome",
            "chrome.exe"
        )
    else:
        # Linux Chrome 无头版路径：browser/linux/chrome-headless-shell-linux64/chrome-headless-shell
        chrome_path = os.path.join(
            project_root,
            "browser",
            "linux",
            "chrome-headless-shell-linux64",
            "chrome-headless-shell"
        )

    # ========== 拼接 ChromeDriver 路径（适配你的实际多级目录） ==========
    if sys_type == "windows":
        # Windows ChromeDriver 路径：driver/windows/chromedriver-win64/chromedriver.exe
        driver_path = os.path.join(
            project_root,
            "driver",
            "windows",
            "chromedriver-win64",
            "chromedriver.exe"
        )
    else:
        # Linux ChromeDriver 路径：driver/linux/chromedriver-linux64/chromedriver
        driver_path = os.path.join(
            project_root,
            "driver",
            "linux",
            "chromedriver-linux64",
            "chromedriver"
        )

    # 验证路径是否存在（调试用，可注释）
    print(f"🔍 系统类型：{sys_type}")
    print(f"🔍 Chrome 路径：{chrome_path} | 存在：{os.path.exists(chrome_path)}")
    print(f"🔍 ChromeDriver 路径：{driver_path} | 存在：{os.path.exists(driver_path)}")

    return chrome_path, driver_path


# ===================== Playwright 兼容配置（修正 Chrome 路径） =====================
@pytest.fixture(scope="session")
def pw_browser():
    """
    Playwright 浏览器 fixture（兼容本地/Jenkins）
    核心：使用项目内的 Chrome 路径，而非系统路径
    """
    is_jenkins = is_jenkins_env()
    sys_type = get_system_type()
    chrome_path, _ = get_browser_driver_path()  # 复用上面的路径逻辑

    with sync_playwright() as p:
        # 公共配置
        launch_kwargs = {
            "args": [
                "--no-sandbox",  # 兼容 Linux/Jenkins 权限
                "--disable-dev-shm-usage",  # 解决 Linux 内存不足
                "--start-maximized"  # 窗口最大化（全环境通用）
            ]
        }

        # 环境差异化配置
        if not is_jenkins:  # 本地环境（Windows）
            # 使用项目内的 Chrome 路径（替代硬编码）
            launch_kwargs["executable_path"] = chrome_path
            launch_kwargs["headless"] = False  # 有界面调试
        else:  # Jenkins/Linux 环境
            # 使用项目内的 Linux Chrome 无头版路径
            launch_kwargs["executable_path"] = chrome_path
            launch_kwargs["headless"] = True  # 无界面运行
            launch_kwargs["args"].extend(["--disable-gpu"])

        # 启动浏览器
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


# ===================== Selenium 兼容配置（核心适配实际路径） =====================
@pytest.fixture(scope="session")
def selenium_driver():
    """
    Selenium ChromeDriver fixture（兼容本地/Jenkins）
    核心：使用你实际目录中的 Chrome/ChromeDriver，替代自动下载
    """
    is_jenkins = is_jenkins_env()
    sys_type = get_system_type()
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

    # ========== 核心：使用项目内的 Chrome/ChromeDriver ==========
    chrome_path, driver_path = get_browser_driver_path()

    # 1. 指定 Chrome 浏览器二进制文件路径
    chrome_options.binary_location = chrome_path

    # 2. 处理 ChromeDriver 权限（Linux/Jenkins 必需）
    if sys_type == "linux" and os.path.exists(driver_path):
        os.chmod(driver_path, 0o755)  # 赋予执行权限

    # 3. 优先使用项目内的 ChromeDriver，失败则降级自动下载（兜底）
    try:
        service = Service(executable_path=driver_path)
    except Exception as e:
        print(f"⚠️ 项目内驱动使用失败：{e}，降级为自动下载")
        service = Service(ChromeDriverManager().install())

    # 启动浏览器
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(30)  # 隐式等待30秒
    yield driver
    driver.quit()  # 确保关闭浏览器


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
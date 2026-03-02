import os
import sys
import platform
import re
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
    核心：根据环境动态返回 Chrome 浏览器和 ChromeDriver 的绝对路径
    适配逻辑：
    - Windows/本地：使用项目内的 Chrome/Driver 路径
    - Linux/Jenkins：优先使用系统安装的 Chrome + Jenkins 工作目录的 Driver（兜底用项目内路径）
    """
    # 项目根目录（当前文件所在目录，即 auto_ui_api/）
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys_type = get_system_type()
    is_jenkins = is_jenkins_env()

    # ========== 拼接 Chrome 浏览器路径（核心适配 Jenkins/Linux） ==========
    if sys_type == "windows":
        # Windows 本地：使用项目内 Chrome 路径
        chrome_path = os.path.join(
            project_root,
            "browser",
            "windows",
            "Chrome",
            "chrome.exe"
        )
    else:
        # Linux/Jenkins 环境：优先用系统安装的 Chrome（已装在 /opt/google/chrome/google-chrome）
        jenkins_chrome_path = "/opt/google/chrome/google-chrome"
        # 兜底：项目内 Linux 无头版路径
        project_chrome_path = os.path.join(
            project_root,
            "browser",
            "linux",
            "chrome-headless-shell-linux64",
            "chrome-headless-shell"
        )
        # 优先用系统 Chrome，不存在再用项目内的
        chrome_path = jenkins_chrome_path if os.path.exists(jenkins_chrome_path) else project_chrome_path

    # ========== 拼接 ChromeDriver 路径（适配 Jenkins/Linux 实际路径） ==========
    if sys_type == "windows":
        # Windows 本地：使用项目内 Driver 路径
        driver_path = os.path.join(
            project_root,
            "driver",
            "windows",
            "chromedriver-win64",
            "chromedriver.exe"
        )
    else:
        # Linux/Jenkins 环境：优先用 Jenkins 工作目录的 Driver（手动下载的路径）
        jenkins_driver_path = "/root/.jenkins/workspace/driver/linux/chromedriver-linux64/chromedriver"
        # 兜底：项目内 Linux Driver 路径
        project_driver_path = os.path.join(
            project_root,
            "driver",
            "linux",
            "chromedriver-linux64",
            "chromedriver"
        )
        # 优先用 Jenkins 工作目录的 Driver，不存在再用项目内的
        driver_path = jenkins_driver_path if os.path.exists(jenkins_driver_path) else project_driver_path

    # 验证路径是否存在（调试用，可保留）
    print(f"🔍 系统类型：{sys_type} | Jenkins 环境：{is_jenkins}")
    print(f"🔍 Chrome 路径：{chrome_path} | 存在：{os.path.exists(chrome_path)}")
    print(f"🔍 ChromeDriver 路径：{driver_path} | 存在：{os.path.exists(driver_path)}")

    return chrome_path, driver_path


def get_chrome_major_version(chrome_path):
    """获取 Chrome 主版本号（用于匹配 Driver 版本）"""
    try:
        if get_system_type() == "windows":
            import subprocess
            result = subprocess.check_output(f'"{chrome_path}" --version', shell=True, text=True, stderr=subprocess.STDOUT)
        else:
            result = os.popen(f'"{chrome_path}" --version').read()
        # 提取主版本号（如 138/145）
        major_version = re.search(r'Chrome (\d+)', result).group(1)
        return major_version
    except Exception as e:
        print(f"⚠️ 获取 Chrome 版本失败：{e}，将使用最新版 Driver")
        return None


# ===================== Playwright 兼容配置（修正 Chrome 路径） =====================
@pytest.fixture(scope="session")
def pw_browser():
    """
    Playwright 浏览器 fixture（兼容本地/Jenkins）
    核心：Jenkins 优先用系统 Chrome，本地用项目内 Chrome
    """
    is_jenkins = is_jenkins_env()
    sys_type = get_system_type()
    chrome_path, _ = get_browser_driver_path()  # 复用路径逻辑

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
        if not is_jenkins:  # 本地 Windows 环境
            launch_kwargs["executable_path"] = chrome_path
            launch_kwargs["headless"] = False  # 有界面调试
        else:  # Jenkins/Linux 环境
            launch_kwargs["executable_path"] = chrome_path
            launch_kwargs["headless"] = True  # 无界面运行
            launch_kwargs["args"].extend(["--disable-gpu", "--ignore-certificate-errors"])

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


# ===================== Selenium 兼容配置（核心适配 Jenkins） =====================
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

    # ===================== 【本地关闭弹窗：登录、密码泄露、更新、通知】 =====================
    chrome_options.add_argument("--no-first-run")                        # 取消首次运行向导
    chrome_options.add_argument("--no-default-browser-check")           # 不检查默认浏览器
    chrome_options.add_argument("--disable-popup-blocking")             # 禁用弹窗拦截
    chrome_options.add_argument("--disable-notifications")              # 禁用浏览器通知
    chrome_options.add_argument("--disable-infobars")                  # 禁用顶部黄色提示条
    chrome_options.add_argument("--safebrowsing-disable-extension-blacklist")
    chrome_options.add_argument("--safebrowsing-disable-download-protection")
    chrome_options.add_argument("--disable-save-password-bubble")      # 关闭密码保存提示
    chrome_options.add_argument("--disable-translate")                 # 关闭翻译提示
    chrome_options.add_argument("--disable-extensions")                # 禁用扩展
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-features=TranslateUI,BraveAds,OptimizationGuide")
    # 关闭 Google 账号登录弹窗
    chrome_options.add_argument("--disable-signin-promo")
    chrome_options.add_argument("--disable-sync")
    # ===================== 【专门关闭：密码泄露安全提示】 =====================
    chrome_options.add_argument("--safebrowsing-disable-password-protection")  # 关闭密码泄露警告
    chrome_options.add_argument("--disable-password-manager-reauthentication")  # 关闭密码管理器二次验证
    chrome_options.add_argument("--incognito")
    # 禁用密码管理 + 安全浏览（彻底关掉泄露提示）
    chrome_options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2,
        "safebrowsing.enabled": False,
        "safebrowsing.disable_password_protection": True
    })

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
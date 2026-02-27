"""
页面基类模块（BasePage）
核心作用：
1. 封装 Playwright + Selenium 通用操作方法，实现两套框架的统一调用
2. 适配本地 Windows / Jenkins Linux 双环境的路径、配置差异
3. 提供通用定位器转换、元素等待、截图、页面操作等基础能力
4. 所有业务页面对象（如 FormPage、IFramePage）均继承此类
"""
from pathlib import Path
import os
from datetime import datetime
# Selenium 定位枚举（父类统一导入，子类无需重复导入）
from selenium.webdriver.common.by import By


class BasePage:
    """
    所有页面的父类（基类）
    设计原则：
    - 兼容性：同时支持 Playwright（优先）和 Selenium 驱动
    - 通用性：封装通用操作，子类仅需关注业务逻辑
    - 适配性：自动识别运行环境（本地/Jenkins），适配路径/配置
    """

    def __init__(self, driver):
        """
        基类初始化方法
        :param driver: 驱动对象（Playwright Page 或 Selenium WebDriver）
        """
        # 驱动实例（核心属性，子类所有操作均基于此）
        self.driver = driver
        # 标记当前驱动类型（Playwright / Selenium）
        self.is_playwright = self._is_playwright_driver()
        # 初始化截图保存目录（适配本地/Jenkins）
        self.screenshot_dir = self._get_screenshot_dir()

    def _is_playwright_driver(self):
        """
        私有方法：判断当前驱动是否为 Playwright 类型
        判定依据：Playwright Page 对象包含 "wait_for_selector" 方法
        :return: bool - True=Playwright，False=Selenium
        """
        return hasattr(self.driver, "wait_for_selector")

    def _get_screenshot_dir(self):
        """
        私有方法：获取截图保存目录（适配本地/Jenkins 环境）
        - 本地环境（Windows）：项目根目录下 ./screenshot
        - Jenkins 环境（Linux）：/root/.jenkins/workspace/screenshot
        :return: Path 对象 - 截图目录路径
        """
        # 判断是否为 Jenkins 运行环境
        is_jenkins = os.getenv("JENKINS_URL") or (os.name == "posix" and "/root/.jenkins/" in os.getcwd())
        # 定义不同环境的截图路径
        dir_path = Path("/root/.jenkins/workspace/screenshot") if is_jenkins else Path("./screenshot")
        # 确保目录存在（不存在则创建，存在则不操作）
        dir_path.mkdir(exist_ok=True)
        return dir_path

    # ===================== 核心通用方法：定位器转换（子类复用） =====================
    def _get_locator(self, loc_str, loc_type="css"):
        """
        通用定位器转换方法（核心封装，解决两套框架定位格式差异）
        :param loc_str: 定位字符串（如 "[name='my-text']" / "//input[@name='my-text']"）
        :param loc_type: 定位类型（默认 css，支持：css/xpath/id/name/class_name/tag_name）
        :return: 适配后的定位器
                 - Playwright：直接返回定位字符串（框架原生支持）
                 - Selenium：返回 (By.XXX, loc_str) 元组（框架要求格式）
        :raises ValueError: 传入不支持的定位类型时抛出异常
        """
        if self.is_playwright:
            # Playwright 无需转换，直接返回定位字符串
            return loc_str
        else:
            # Selenium 定位类型映射（枚举值 + 字符串）
            loc_map = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "name": By.NAME,
                "class_name": By.CLASS_NAME,
                "tag_name": By.TAG_NAME
            }
            # 校验定位类型合法性，避免无效调用
            if loc_type not in loc_map:
                raise ValueError(f"不支持的定位类型：{loc_type}，可选类型：{list(loc_map.keys())}")
            # 返回 Selenium 要求的元组格式
            return (loc_map[loc_type], loc_str)

    # ===================== 通用元素等待方法（解决元素加载延迟） =====================
    def wait_visible(self, locator, timeout=10):
        """
        等待元素可见（通用方法，适配两套框架）
        :param locator: 定位器（已通过 _get_locator 转换后的格式）
        :param timeout: 超时时间（秒），默认 10 秒
        """
        # 转换超时时间（Playwright 需毫秒，Selenium 需秒）
        timeout_ms = timeout * 1000
        if self.is_playwright:
            # Playwright：等待元素可见（visible）
            self.driver.wait_for_selector(locator, state="visible", timeout=timeout_ms)
        else:
            # Selenium：导入等待依赖（延迟导入，避免未使用时加载）
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            # Selenium：等待元素可见
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))

    def wait_clickable(self, locator, timeout=10):
        """
        等待元素可点击（通用方法，适配两套框架）
        :param locator: 定位器（已通过 _get_locator 转换后的格式）
        :param timeout: 超时时间（秒），默认 10 秒
        """
        # 转换超时时间（Playwright 需毫秒，Selenium 需秒）
        timeout_ms = timeout * 1000
        if self.is_playwright:
            # Playwright：等待元素附加到 DOM（attached）= 可点击状态
            self.driver.wait_for_selector(locator, state="attached", timeout=timeout_ms)
        else:
            # Selenium：导入等待依赖（延迟导入，避免未使用时加载）
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            # Selenium：等待元素可点击
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))

    # ===================== 通用截图方法（失败时自动保存） =====================
    def screenshot(self, name=None):
        """
        通用截图方法（适配两套框架 + 双环境路径）
        :param name: 截图文件名（不含后缀），默认自动生成：error_YYYYMMDD_HHMMSS
        :return: 无返回值，截图保存到指定目录并打印路径
        """
        # 生成默认文件名（时间戳，避免重复）
        if not name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"error_{timestamp}"
        # 拼接完整截图路径（目录 + 文件名 + 后缀）
        screenshot_path = self.screenshot_dir / f"{name}.png"

        if self.is_playwright:
            # Playwright：全屏截图（full_page=True），保存到指定路径
            self.driver.screenshot(path=str(screenshot_path), full_page=True)
        else:
            # Selenium：保存截图到指定路径
            self.driver.save_screenshot(str(screenshot_path))

        # 打印截图路径，便于调试/日志查看
        print(f"截图已保存：{screenshot_path}")

    # ===================== 通用页面操作方法 =====================
    def open(self, url):
        """
        打开指定 URL（通用方法，适配两套框架）
        :param url: 目标网址（如 "https://www.example.com"）
        """
        if self.is_playwright:
            # Playwright：设置超时 60 秒，等待 DOM 加载完成后返回
            self.driver.goto(url, timeout=60000, wait_until="domcontentloaded")
        else:
            # Selenium：打开指定 URL
            self.driver.get(url)

    def click(self, locator):
        """
        点击元素（通用方法，先等可点击再操作，避免点击失效）
        :param locator: 定位器（已通过 _get_locator 转换后的格式）
        """
        # 先等待元素可点击，再执行点击操作
        self.wait_clickable(locator)
        if self.is_playwright:
            # Playwright：原生点击方法
            self.driver.click(locator)
        else:
            # Selenium：先定位元素，再点击
            self.driver.find_element(*locator).click()

    def input_text(self, locator, text):
        """
        输入文本（通用方法，先等可见再操作，自动清空原有内容）
        :param locator: 定位器（已通过 _get_locator 转换后的格式）
        :param text: 要输入的文本内容
        """
        # 先等待元素可见，再执行输入操作
        self.wait_visible(locator)
        if self.is_playwright:
            # Playwright：原生填充方法（自动清空原有内容）
            self.driver.fill(locator, text)
        else:
            # Selenium：先定位元素 → 清空 → 输入文本
            elem = self.driver.find_element(*locator)
            elem.clear()
            elem.send_keys(text)
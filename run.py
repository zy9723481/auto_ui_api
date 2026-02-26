import os
import sys

# pytest框架，用于执行测试用例

import pytest
# 导入消息推送工具
from common.message_util import MessageSender

os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'


def main():
    """
    项目主入口
    PyCharm 一键运行，无需命令行、无需宝塔
    """
    print("===== PyCharm 直接运行：UI+接口自动化 =====")

    # 执行 tests 目录下所有用例
    pytest.main([
        "-vs",           # 显示详细日志
        "tests/"         # 用例路径
    ])

    # 完成推送
    MessageSender.send_feishu("✅ 测试执行完成，Allure 已集成！")
    print("\n===== 全部用例执行完毕 =====")

# 程序入口
if __name__ == "__main__":
    if sys.platform == 'win32':
        import _locale
        _locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])
    main()
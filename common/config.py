# YAML配置文件解析库
import yaml
# 系统环境变量工具
import os

class Config:
    """
    配置工具类：读取环境配置（dev/test/prod）
    使用单例模式：全局只加载一次配置，节省资源
    """
    # 单例实例，确保全局唯一
    _instance = None

    def __new__(cls):
        """
        重写new方法，实现单例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 读取环境变量，默认使用 test 环境
            env = os.getenv("ENV", "test")
            # 打开并读取 YAML 环境配置文件
            with open("config/env.yaml", "r", encoding="utf-8") as f:
                # 把对应环境的配置存入实例
                cls._instance.data = yaml.safe_load(f)[env]
        return cls._instance

# 全局配置对象，任何地方直接 import 就能用
config = Config()
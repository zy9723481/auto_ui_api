# 接口测试必备请求库
import requests

class RequestUtil:
    """
    接口自动化工具类
    封装 GET/POST，供测试用例直接调用
    """

    @staticmethod
    def post(url, json=None):
        """
        封装 POST 请求
        :param url: 接口地址
        :param json: 请求体参数
        :return: 响应对象
        """
        return requests.post(url, json=json)

    @staticmethod
    def get(url, params=None):
        """
        封装 GET 请求
        """
        return requests.get(url, params=params)
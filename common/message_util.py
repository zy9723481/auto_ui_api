class MessageSender:
    """
    测试完成后消息推送工具
    可扩展：飞书、钉钉、企业微信、邮件
    """

    @staticmethod
    def send_feishu(text):
        """
        飞书机器人推送（这里简化为打印）
        """
        print("【推送通知】", text)

    @staticmethod
    def send_email(report_content):
        """
        邮件发送测试报告
        """
        print("【邮件】测试报告已发送")
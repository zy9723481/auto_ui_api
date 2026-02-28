# -*- coding: GBK -*-

import logging
import logging.handlers
import os
import colorlog


class LoggerFactory:
    @staticmethod
    def get_logger(name="my_app"):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # 控制台处理器和彩色格式化器
        console_handler = logging.StreamHandler()
        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s-[%(levelname)-8s]-[%(name)s]-[%(filename)s:%(funcName)s:%(lineno)d]-%(message)s%(reset)s",
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            style='%',
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.DEBUG)

        # 文件处理器和标准格式化器
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=os.path.join(log_dir, "test.log"),
            when="D",
            backupCount=5,
        )
        file_formatter = logging.Formatter(
            '%(asctime)s-[%(levelname)s]-[%(name)s]-[%(filename)s:%(funcName)s:%(lineno)d]-%(message)s')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)

        # 添加处理器到日志记录器（仅当它们尚未添加时）
        if not logger.handlers:
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)

        return logger
    # 使用示例
log = LoggerFactory.get_logger()

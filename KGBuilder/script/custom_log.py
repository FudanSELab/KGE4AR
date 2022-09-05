import logging

from definitions import LOG_FILE


class LogUtil():
    __log_util = None  # 单例模式标记

    def __init__(self):
        self.logger = logging.getLogger("KGBuilder")
        # 日志模式 w为写入前清空 a为追加
        ch = logging.FileHandler(LOG_FILE, mode='a')
        formats = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formats)
        self.logger.addHandler(ch)
        self.logger.setLevel(logging.DEBUG)

    @classmethod
    def get_log_util(cls, ):
        if cls.__log_util is None:
            cls.__log_util: LogUtil = LogUtil()
        return cls.__log_util

    def debug(self, *messages):
        for message in messages:
            self.logger.debug(message)

    def info(self, *messages):
        for message in messages:
            self.logger.info(message)

    def warning(self, *messages):
        for message in messages:
            self.logger.warning(message)

    def error(self, *messages):
        for message in messages:
            self.logger.error(message, exc_info=True)
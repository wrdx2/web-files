# _*_ coding: utf-8 _*_
import logging
import logging.handlers
import os.path


def singleton(cls):
    instance = {}

    def _singleton(*args, **kw):
        if cls not in instance:
            instance[cls] = cls(*args, **kw)
        return instance[cls]

    return _singleton


@singleton
class Logger(object):
    def __init__(self, logger=None):
        """
        指定保存日志的文件路径，日志级别，以及调用文件
            将日志存入到指定的文件中
        :param logger:
        """
        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)

        # 创建日志名称。
        # rq = time.strftime('%Y%m%d', time.localtime(time.time()))

        # os.getcwd()获取当前文件的路径，os.path.dirname()获取指定文件路径的上级路径
        # path_dir = os.path.dirname(__file__)
        log_path = os.path.dirname(os.path.realpath(__file__)) + '/logs/'

        if not os.path.exists(log_path):
            os.makedirs(log_path)
        log_name = os.path.join(log_path, 'log.log')

        # 创建一个handler，用于写入日志文件
        # fh = logging.FileHandler(log_name, encoding='utf-8')
        fh = logging.handlers.TimedRotatingFileHandler(log_name, 'D', 1, 5, encoding='utf8')
        fh.setLevel(logging.INFO)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # 定义handler的输出格式
        DEFAULT_FORMAT = '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d %(funcName)s] %(message)s'
        DEFAULT_DATE_FORMAT = '%y-%m-%d %H:%M:%S'

        # formatter = logging.Formatter('%(asctime)s  %(levelname)s %(filename)s %(funcName)s:%(lineno)d - %(message)s')
        formatter = logging.Formatter(fmt=DEFAULT_FORMAT, datefmt=DEFAULT_DATE_FORMAT, style='%')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def get_logger(self):
        return self.logger


if __name__ == '__main__':
    pass

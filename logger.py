import logging
from logging import handlers


class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

# fmt ='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    def __init__(self, filename, level='info', when='D', backCount=3, fmt='%(asctime)s - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)  # set log format
        self.logger.setLevel(self.level_relations.get(level))  # set log level
        sh = logging.StreamHandler()  # print to terminal
        sh.setFormatter(format_str)   # set terminal format
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount, encoding='utf-8')
        #interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.setFormatter(format_str)  # set to file
        self.logger.addHandler(sh)
        self.logger.addHandler(th)


if __name__ == '__main__':
    log = Logger('all.log', level='debug')
    log.logger.debug('debug')
    log.logger.info('info')
    log.logger.warning('警告')
    log.logger.error('报错')
    log.logger.critical('严重')
    Logger('error.log', level='error').logger.error('error')
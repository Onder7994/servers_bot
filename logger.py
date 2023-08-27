import logging
import logging.handlers
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'asctime': self.formatTime(record, self.datefmt),
            'filename': record.filename,
            'codeLine': record.lineno,
            'levelname': record.levelname,
            'message': record.getMessage(),
        }
        return json.dumps(log_record, ensure_ascii=False)

class Logging():
    def __init__(self, logger_name, log_file):
        self.logger_name = logger_name
        self.logger = logging.getLogger(self.logger_name)
        self.logger.setLevel(logging.INFO)
        formatter = JSONFormatter()
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_file, when='midnight', interval=1, backupCount=7
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler) 

    def log(self, level, message, *args):
        self.logger.log(level, message, *args)

    def info(self, message, *args):
        self.log(logging.INFO, message, *args)

    def debug(self, message, *args):
        self.log(logging.DEBUG, message, *args)

    def warning(self, message, *args):
        self.log(logging.WARNING, message, *args)

    def error(self, message, *args):
        self.log(logging.ERROR, message, *args)

    def critical(self, message, *args):
        self.log(logging.CRITICAL, message, *args)

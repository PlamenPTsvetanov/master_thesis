import logging as log

log.basicConfig(
    level=log.DEBUG,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class Logger:
    @staticmethod
    def info(message):
        log.info(message)

    @staticmethod
    def warning(message):
        log.warning(message)

    @staticmethod
    def debug(message):
        log.debug(message)

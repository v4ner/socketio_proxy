import logging
import sys

def setup_logging():
    """
    配置应用程序的日志系统。
    日志将输出到控制台和文件。
    """
    # 获取根日志器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 创建文件处理器
    file_handler = logging.FileHandler('socketio_proxy.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 避免重复添加处理器
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger

# 在模块导入时设置日志
logger = setup_logging()
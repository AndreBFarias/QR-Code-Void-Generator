import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
    Configures the global logging system.
    Logs are written to console and 'app.log'.
    Format: [TIME] [LEVEL] [FILE:LINE] - Message
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formatter
    # [HORA] [NÍVEL] [ARQUIVO:LINHA] - Mensagem
    log_format = '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s'
    date_format = '%H:%M:%S'
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # File Handler (Rotating to avoid huge files)
    log_file = os.path.join(os.getcwd(), 'app.log')
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Hook uncaught exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception
    
    logging.info("Logging system initialized successfully.")

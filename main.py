import sys
import os
import platform
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import qVersion
import PIL
from ui.main_window import MainWindow
from core.logger import setup_logging

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # --- System Checks & Logging ---
    logger.info("="*40)
    logger.info("   QR CODE VOID GENERATOR - STARTUP   ")
    logger.info("="*40)
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"OS: {platform.system()} {platform.release()} ({platform.version()})")
    logger.info(f"PyQt6 Version: {qVersion()}")
    logger.info(f"Pillow (PIL) Version: {PIL.__version__}")
    
    # Asset Check
    logger.info("Initializing Asset Manager...")
    
    icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'logos', 'pix.png') # Use pix as app icon if generic not found
    # Or better, use a specific app icon if available. The user didn't specify an app icon, but we can use one of the downloaded ones or just skip if not found.

    try:
        app = QApplication(sys.argv)
        
        if os.path.exists(icon_path):
            from PyQt6.QtGui import QIcon
            app.setWindowIcon(QIcon(icon_path))
            
        window = MainWindow()
        window.show()
        
        logger.info("Main window shown successfully.")
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Fatal error during execution: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

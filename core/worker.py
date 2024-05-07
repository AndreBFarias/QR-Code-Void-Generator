import os
import logging
import time
from PyQt6.QtCore import QThread, pyqtSignal
from PIL import Image, ImageDraw
from core.generator import QRGenerator
from core.logo_handler import add_logo
from ui.styles import DraculaTheme
logger = logging.getLogger(__name__)

class QRWorker(QThread):
    finished = pyqtSignal(object, int)
    error = pyqtSignal(str, int)

    def __init__(self, request_id, data, ec, size, rounded, logo_img, logo_size, logo_opacity, logo_pos='center', easter_egg=False, fill_color='black', back_color='white'):
        super().__init__()
        self.request_id = request_id
        self.data = data
        self.ec = ec
        self.size = size
        self.rounded = rounded
        self.logo_img = logo_img
        self.logo_size = logo_size
        self.logo_opacity = logo_opacity
        self.logo_pos = logo_pos
        self.easter_egg = easter_egg
        self.fill_color = fill_color
        self.back_color = back_color
        self.generator = QRGenerator()

    def run(self):
        worker_start = time.time()
        try:
            logger.debug(f'Worker started for Request ID: {self.request_id}')
            if self.easter_egg:
                size = 1000
                img = Image.new('RGB', (size, size), color='black')
                draw = ImageDraw.Draw(img)
                center = size // 2
                radius = 150
                draw.ellipse((center - radius, center - radius, center + radius, center + radius), outline=DraculaTheme.PURPLE, width=10)
                draw.ellipse((center - 50, center - 50, center + 50, center + 50), fill=DraculaTheme.PURPLE)
                self.finished.emit(img, self.request_id)
            else:
                qr_start = time.time()
                qr_img = self.generator.generate_qr(data=self.data, error_correction=self.ec, box_size=10, border=4, fill_color=self.fill_color, back_color=self.back_color, rounded_modules=self.rounded)
                qr_time = time.time() - qr_start
                logger.info(f'QR generation: {qr_time*1000:.2f}ms')
                
                if self.logo_img:
                    logo_start = time.time()
                    qr_img = add_logo(qr_img, self.logo_img, self.logo_size, self.logo_opacity, position=self.logo_pos, border_width=40, back_color=self.back_color)
                    logo_time = time.time() - logo_start
                    logger.info(f'Logo overlay: {logo_time*1000:.2f}ms')
                
                self.finished.emit(qr_img, self.request_id)
            
            worker_total = time.time() - worker_start
            logger.info(f'Worker total time: {worker_total*1000:.2f}ms (Request ID: {self.request_id})')
        except Exception as e:
            logger.error(f'Error in QRWorker (ID: {self.request_id}): {e}', exc_info=True)
            self.error.emit(str(e), self.request_id)
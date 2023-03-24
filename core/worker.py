import os
import logging
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
                logger.debug(f'Generating QR with Logo? {bool(self.logo_img)}')
                logger.debug(f'Final Colors -> Back: {self.back_color}, Fill: {self.fill_color}')
                qr_img = self.generator.generate_qr(data=self.data, error_correction=self.ec, box_size=10, border=4, fill_color=self.fill_color, back_color=self.back_color, rounded_modules=self.rounded)
                if self.logo_img:
                    qr_img = add_logo(qr_img, self.logo_img, self.logo_size, self.logo_opacity, position=self.logo_pos, border_width=40)
                self.finished.emit(qr_img, self.request_id)
            logger.debug(f'Worker finished for Request ID: {self.request_id}')
        except Exception as e:
            logger.error(f'Error in QRWorker (ID: {self.request_id}): {e}', exc_info=True)
            self.error.emit(str(e), self.request_id)
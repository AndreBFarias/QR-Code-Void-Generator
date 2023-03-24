import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QBuffer, QIODevice
from PIL import Image

def save_image(image: Image.Image, path: str):
    directory = os.path.dirname(path)
    if directory and (not os.path.exists(directory)):
        os.makedirs(directory)
    image.save(path)
    import logging
    logging.getLogger(__name__).info(f'Image saved successfully to: {path}')

def copy_to_clipboard(image: Image.Image):
    if image.mode == 'RGB':
        (r, g, b) = image.split()
        image = Image.merge('RGB', (b, g, r))
    elif image.mode == 'RGBA':
        (r, g, b, a) = image.split()
        image = Image.merge('RGBA', (b, g, r, a))
    im_data = image.tobytes('raw', image.mode)
    qim = QImage(im_data, image.size[0], image.size[1], QImage.Format.Format_ARGB32 if image.mode == 'RGBA' else QImage.Format.Format_RGB888)
    clipboard = QApplication.clipboard()
    clipboard.setImage(qim)

def pil_to_qpixmap(pil_image: Image.Image) -> QPixmap:
    if pil_image.mode != 'RGBA':
        pil_image = pil_image.convert('RGBA')
    im_data = pil_image.tobytes('raw', 'RGBA')
    qim = QImage(im_data, pil_image.size[0], pil_image.size[1], QImage.Format.Format_RGBA8888)
    return QPixmap.fromImage(qim)

def save_image_dialog(image: Image.Image, parent=None):
    from PyQt6.QtWidgets import QFileDialog
    (file_path, _) = QFileDialog.getSaveFileName(parent, 'Salvar QR Code', 'qrcode.png', 'Imagens PNG (*.png);;Imagens JPG (*.jpg);;Imagens JPEG (*.jpeg);;Documento PDF (*.pdf);;Vetor SVG (*.svg);;Todos os Arquivos (*)')
    if file_path:
        save_image(image, file_path)

def get_wifi_ssid_linux() -> str:
    import subprocess
    import logging
    import shutil
    logger = logging.getLogger(__name__)
    if not shutil.which('nmcli'):
        logger.error('nmcli not found')
        return None
    try:
        result = subprocess.run(['nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi'], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            if line.startswith('yes:') or line.startswith('sim:'):
                ssid = line.split(':', 1)[1]
                logger.info(f'Wi-Fi Detected: {ssid}')
                return ssid
    except FileNotFoundError:
        logger.error('nmcli not found. Install network-manager.')
    except subprocess.CalledProcessError as e:
        logger.error(f'nmcli failed: {e.stderr}')
    except Exception as e:
        logger.error(f'Wi-Fi detection error: {e}')
    return None
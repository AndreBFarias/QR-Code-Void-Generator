import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QBuffer, QIODevice
from PIL import Image

def save_image(image: Image.Image, path: str):
    """
    Save the PIL Image to the specified path.
    Supports PNG, PDF, and other formats supported by PIL.
    For SVG, we might need a different approach if we want true vector SVG.
    """
    # Create directory if it doesn't exist
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    image.save(path)

def copy_to_clipboard(image: Image.Image):
    """
    Copy the PIL Image to the system clipboard.
    """
    # Convert PIL Image to QImage
    if image.mode == "RGB":
        r, g, b = image.split()
        image = Image.merge("RGB", (b, g, r))
    elif image.mode == "RGBA":
        r, g, b, a = image.split()
        image = Image.merge("RGBA", (b, g, r, a))
        
    im_data = image.tobytes("raw", image.mode)
    qim = QImage(im_data, image.size[0], image.size[1], QImage.Format.Format_ARGB32 if image.mode == "RGBA" else QImage.Format.Format_RGB888)
    
    clipboard = QApplication.clipboard()
    clipboard.setImage(qim)

def pil_to_qpixmap(pil_image: Image.Image) -> QPixmap:
    """
    Convert PIL Image to QPixmap for display in QLabel.
    """
    # Ensure image is in RGBA mode for consistency
    if pil_image.mode != "RGBA":
        pil_image = pil_image.convert("RGBA")
    
    im_data = pil_image.tobytes("raw", "RGBA")
    
    # Use Format_RGBA8888 which expects R, G, B, A order
    qim = QImage(im_data, pil_image.size[0], pil_image.size[1], QImage.Format.Format_RGBA8888)
    
    return QPixmap.fromImage(qim)

def save_image_dialog(image: Image.Image, parent=None):
    """
    Opens a file dialog to save the image.
    """
    from PyQt6.QtWidgets import QFileDialog
    
    file_path, _ = QFileDialog.getSaveFileName(
        parent,
        "Salvar QR Code",
        "qrcode.png",
        "Imagens PNG (*.png);;Imagens JPG (*.jpg);;Imagens JPEG (*.jpeg);;Documento PDF (*.pdf);;Vetor SVG (*.svg);;Todos os Arquivos (*)"
    )
    
    if file_path:
        save_image(image, file_path)

def get_wifi_ssid_linux() -> str:
    """
    Detects the currently connected Wi-Fi SSID on Linux using nmcli.
    Returns None if detection fails.
    """
    import subprocess
    import logging
    import shutil
    logger = logging.getLogger(__name__)
    
    if not shutil.which("nmcli"):
        logger.error("nmcli not found")
        return None
    
    try:
        # nmcli -t -f active,ssid dev wifi
        result = subprocess.run(
            ['nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Output format:
        # no:SSID1
        # yes:ConnectedSSID
        # no:SSID2
        
        for line in result.stdout.splitlines():
            # Handle localized output (yes/sim)
            if line.startswith("yes:") or line.startswith("sim:"):
                ssid = line.split(":", 1)[1]
                logger.info(f"Wi-Fi Detected: {ssid}")
                return ssid
                
    except FileNotFoundError:
        logger.error("nmcli not found. Install network-manager.")
    except subprocess.CalledProcessError as e:
        logger.error(f"nmcli failed: {e.stderr}")
    except Exception as e:
        logger.error(f"Wi-Fi detection error: {e}")
        
    return None

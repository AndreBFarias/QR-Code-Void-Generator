import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, SquareModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image

class QRGenerator:

    def __init__(self):
        pass

    def generate_qr(self, data: str, error_correction: str='H', box_size: int=10, border: int=4, fill_color: str='black', back_color: str='white', rounded_modules: bool=True) -> Image.Image:
        ec_map = {'L': qrcode.constants.ERROR_CORRECT_L, 'M': qrcode.constants.ERROR_CORRECT_M, 'Q': qrcode.constants.ERROR_CORRECT_Q, 'H': qrcode.constants.ERROR_CORRECT_H}
        qr = qrcode.QRCode(version=None, error_correction=ec_map.get(error_correction, qrcode.constants.ERROR_CORRECT_H), box_size=box_size, border=border)
        qr.add_data(data)
        qr.make(fit=True)
        module_drawer = RoundedModuleDrawer() if rounded_modules else SquareModuleDrawer()
        if not fill_color:
            fill_color = 'black'
        if not back_color:
            back_color = 'white'
        print(f'DEBUG: Generator Colors -> Back: {back_color}, Fill: {fill_color}')
        img = qr.make_image(image_factory=StyledPilImage, module_drawer=module_drawer, color_mask=SolidFillColorMask(back_color=tuple((int(back_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))) if back_color.startswith('#') else (255, 255, 255), front_color=tuple((int(fill_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))) if fill_color.startswith('#') else (0, 0, 0)))
        import logging
        logger = logging.getLogger(__name__)
        if hasattr(img, '_img'):
            return img._img
        return img

    def generate_svg(self, data: str, error_correction: str='H', border: int=4, rounded_modules: bool=True) -> str:
        import qrcode.image.svg
        ec_map = {'L': qrcode.constants.ERROR_CORRECT_L, 'M': qrcode.constants.ERROR_CORRECT_M, 'Q': qrcode.constants.ERROR_CORRECT_Q, 'H': qrcode.constants.ERROR_CORRECT_H}
        qr = qrcode.QRCode(version=None, error_correction=ec_map.get(error_correction, qrcode.constants.ERROR_CORRECT_H), border=border)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
        return img.to_string(encoding='unicode')
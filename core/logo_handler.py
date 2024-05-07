from PIL import Image, ImageDraw, ImageFilter
import logging
import time

logger = logging.getLogger(__name__)

def add_logo(qr_image: Image.Image, logo_source: object, size_percent: int, opacity: int, position: str='center', border_width: int=0, back_color: str='white') -> Image.Image:
    start_time = time.time()
    
    if not logo_source:
        return qr_image
    try:
        qr_image = qr_image.convert('RGBA')
        if isinstance(logo_source, str):
            logo = Image.open(logo_source).convert('RGBA')
        elif isinstance(logo_source, Image.Image):
            logo = logo_source.convert('RGBA')
        else:
            logger.error(f'Invalid logo source type: {type(logo_source)}')
            return qr_image
    except Exception as e:
        logger.error(f'Error loading logo: {e}')
        return qr_image
    
    load_time = time.time() - start_time
    logger.debug(f'Logo load time: {load_time*1000:.2f}ms')
    
    process_start = time.time()
    qr_width, qr_height = qr_image.size
    logo_size = int(min(qr_width, qr_height) * (size_percent / 100))
    if logo_size == 0:
        return qr_image
    
    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
    
    to_paste = logo
    paste_size = logo_size
    
    if opacity < 100:
        alpha_channel = logo.split()[3]
        alpha_channel = alpha_channel.point(lambda p: p * (opacity / 100))
        logo.putalpha(alpha_channel)
        to_paste = logo
    
    process_time = time.time() - process_start
    logger.debug(f'Logo processing time: {process_time*1000:.2f}ms')
    
    paste_start = time.time()
    safe_margin = border_width + 10
    padding = max(int(qr_width * 0.05), safe_margin)
    
    if position == 'center':
        pos_x = (qr_width - paste_size) // 2
        pos_y = (qr_height - paste_size) // 2
    elif position == 'top-left':
        pos_x = padding
        pos_y = padding
    elif position == 'top':
        pos_x = (qr_width - paste_size) // 2
        pos_y = padding
    elif position == 'top-right':
        pos_x = qr_width - paste_size - padding
        pos_y = padding
    elif position == 'left':
        pos_x = padding
        pos_y = (qr_height - paste_size) // 2
    elif position == 'right':
        pos_x = qr_width - paste_size - padding
        pos_y = (qr_height - paste_size) // 2
    elif position == 'bottom-left':
        pos_x = padding
        pos_y = qr_height - paste_size - padding
    elif position == 'bottom':
        pos_x = (qr_width - paste_size) // 2
        pos_y = qr_height - paste_size - padding
    elif position == 'bottom-right':
        pos_x = qr_width - paste_size - padding
        pos_y = qr_height - paste_size - padding
    else:
        pos_x = (qr_width - paste_size) // 2
        pos_y = (qr_height - paste_size) // 2
    
    qr_with_logo = qr_image.copy()
    qr_with_logo.paste(to_paste, (pos_x, pos_y), to_paste)
    
    paste_time = time.time() - paste_start
    total_time = time.time() - start_time
    logger.info(f'add_logo total: {total_time*1000:.2f}ms (load: {load_time*1000:.2f}ms, process: {process_time*1000:.2f}ms, paste: {paste_time*1000:.2f}ms)')
    
    return qr_with_logo
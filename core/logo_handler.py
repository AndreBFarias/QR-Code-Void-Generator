from PIL import Image

def add_logo(qr_image: Image.Image, logo_source: object, size_percent: int, opacity: int, position: str='center', border_width: int=0) -> Image.Image:
    if not logo_source:
        return qr_image
    try:
        qr_image = qr_image.convert('RGBA')
        if isinstance(logo_source, str):
            logo = Image.open(logo_source).convert('RGBA')
        elif isinstance(logo_source, Image.Image):
            logo = logo_source.convert('RGBA')
        else:
            print(f'Invalid logo source type: {type(logo_source)}')
            return qr_image
    except Exception as e:
        print(f'Error loading logo: {e}')
        return qr_image
    (qr_width, qr_height) = qr_image.size
    logo_size = int(min(qr_width, qr_height) * (size_percent / 100))
    if logo_size == 0:
        return qr_image
    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
    backplate_size = int(logo_size * 1.0)
    backplate = Image.new('RGBA', (backplate_size, backplate_size), 'white')
    offset = (backplate_size - logo_size) // 2
    backplate.paste(logo, (offset, offset), logo)
    to_paste = backplate
    paste_size = backplate_size
    if opacity < 100:
        alpha = to_paste.split()[3]
        alpha = alpha.point(lambda p: p * (opacity / 100))
        to_paste.putalpha(alpha)
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
    return qr_with_logo
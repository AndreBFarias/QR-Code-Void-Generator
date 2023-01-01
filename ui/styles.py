class DraculaTheme:
    from PyQt6.QtGui import QColor
    from core.config import cfg

    # Colors
    # Configurable Colors & Values
    BACKGROUND = cfg.get_str('JanelaPrincipal', 'CorFundo', '#282a36')
    SIDEBAR = cfg.get_str('BlocoEsquerdo_Sidebar', 'CorFundo', '#21222c')
    CURRENT_LINE = "#44475a"
    FOREGROUND = "#f8f8f2"
    COMMENT = "#6272a4"
    CYAN = "#8be9fd"
    GREEN = "#50fa7b"
    ORANGE = "#ffb86c"
    PINK = "#ff79c6"
    PURPLE = "#bd93f9"
    RED = "#ff5555"
    YELLOW = "#f1fa8c"
    
    BORDER_RADIUS = cfg.get_str('EstiloGlobal', 'BorderRadius', '12px')
    FONT_FAMILY = cfg.get_str('EstiloGlobal', 'FonteFamilia', 'Segoe UI')
    
    INPUT_HEIGHT = cfg.get_str('BlocoCentral_Formularios', 'AlturaInput', '45') + "px"
    INPUT_FONT_SIZE = cfg.get_str('BlocoCentral_Formularios', 'TamanhoFonteInput', '14px')
    
    BTN_GENERATE_HEIGHT = cfg.get_str('BlocoCentral_Formularios', 'AlturaBotaoGerar', '55') + "px"
    BTN_GENERATE_FONT_SIZE = cfg.get_str('BlocoCentral_Formularios', 'TamanhoFonteBotao', '15px')
    
    BTN_ACTION_HEIGHT = cfg.get_str('BlocoDireito_Preview', 'AlturaBotoesAcao', '50') + "px"

    STYLESHEET = f"""
    QMainWindow {{
        background-color: {BACKGROUND};
        color: {FOREGROUND};
    }}
    QWidget {{
        background-color: {BACKGROUND};
        color: {FOREGROUND};
        font-family: '{FONT_FAMILY}', sans-serif;
        font-size: 14px;
    }}
    
    /* Sidebar */
    QListWidget {{
        background-color: {SIDEBAR};
        border: none;
        outline: none;
    }}
    QListWidget::item {{
        height: 60px;
        color: {COMMENT};
        padding-left: 20px;
        border-left: 4px solid transparent;
        margin-bottom: 5px;
    }}
    QListWidget::item:selected {{
        background-color: {CURRENT_LINE};
        color: {PURPLE};
        border-radius: 8px;
    }}
    QListWidget::item:hover {{
        background-color: {CURRENT_LINE};
        color: {FOREGROUND};
    }}

    /* Inputs */
    QLabel {{
        color: {FOREGROUND};
        font-weight: bold;
        margin-bottom: 5px;
    }}
    QLineEdit, QPlainTextEdit {{
        background-color: {CURRENT_LINE};
        color: {FOREGROUND};
        border: 1px solid transparent;
        border-radius: {BORDER_RADIUS};
        padding: 12px;
        font-size: {INPUT_FONT_SIZE};
        font-size: {INPUT_FONT_SIZE};
        height: {INPUT_HEIGHT};
        margin-bottom: 5px;
        selection-background-color: {PURPLE};
    }}
    QLineEdit:focus, QPlainTextEdit:focus {{
        border: 1px solid {PURPLE};
    }}
    
    /* Inputs with Icons (Applied via objectName or dynamic property in code) */
    QLineEdit#iconInput {{
        padding-left: 45px;
        background-repeat: no-repeat;
        background-position: left 12px center;
    }}

    /* Buttons */
    QPushButton {{
        background-color: {CURRENT_LINE};
        color: {FOREGROUND};
        border: none;
        border-radius: {BORDER_RADIUS};
        padding: 10px 20px;
        font-weight: bold;
        height: {INPUT_HEIGHT};
    }}
    QPushButton:hover {{
        background-color: {COMMENT};
    }}
    QPushButton:pressed {{
        background-color: {PURPLE};
        color: {BACKGROUND};
    }}
    
    /* Action Button (Generate) */
    QPushButton#actionBtn {{
        background-color: {GREEN};
        color: {BACKGROUND};
        font-size: {BTN_GENERATE_FONT_SIZE};
        font-weight: bold;
        height: {BTN_GENERATE_HEIGHT};
        border-radius: {BORDER_RADIUS};
    }}
    QPushButton#actionBtn:hover {{
        background-color: #69ff94; /* Lighter Green */
    }}
    
    /* Secondary Action Buttons (Save/Copy) */
    QPushButton#secondaryBtn {{
        background-color: {PURPLE};
        color: {BACKGROUND};
        font-size: 14px;
        border-radius: {BORDER_RADIUS};
        height: {BTN_ACTION_HEIGHT};
    }}
    QPushButton#secondaryBtn:hover {{
        background-color: #d6acff;
    }}

    /* ComboBox */
    QComboBox {{
        background-color: {CURRENT_LINE};
        color: {FOREGROUND};
        border: none;
        border-radius: 12px;
        padding: 10px;
        min-width: 60px;
        height: {INPUT_HEIGHT};
    }}
    QComboBox::drop-down {{
        border: none;
    }}
    QComboBox QAbstractItemView {{
        background-color: {CURRENT_LINE};
        color: {FOREGROUND};
        selection-background-color: {PURPLE};
        border: 1px solid {COMMENT};
    }}

    /* Sliders */
    QSlider::groove:horizontal {{
        border: 1px solid {COMMENT};
        height: 6px;
        background: {CURRENT_LINE};
        margin: 2px 0;
        border-radius: 3px;
    }}
    QSlider::sub-page:horizontal {{
        background: {PURPLE};
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: {CYAN};
        border: 1px solid {CYAN};
        width: 16px;
        height: 16px;
        margin: -6px 0;
        border-radius: 8px;
    }}

    /* GroupBox */
    QGroupBox {{
        border: 1px solid {COMMENT};
        border-radius: {BORDER_RADIUS};
        font-weight: bold;
        font-size: 12px; /* Reduced font size */
        padding-top: 15px;
        margin-top: 15px; /* Reduced margin top */
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 10px;
        color: {PURPLE};
    }}
    
    /* CheckBox */
    QCheckBox {{
        color: {FOREGROUND};
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 1px solid {COMMENT};
        border-radius: 4px;
        background: {BACKGROUND};
    }}
    QCheckBox::indicator:checked {{
        background: {PURPLE};
        border: 1px solid {PURPLE};
    }}
    
    /* ScrollArea */
    QScrollArea {{
        border: none;
        background-color: transparent;
        background: transparent;
    }}
    QScrollArea > QWidget > QWidget {{
        background: transparent;
        padding-right: 10px;
    }}
    QScrollBar:vertical {{
        border: none;
        background: {BACKGROUND};
        width: 10px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {COMMENT};
        min-height: 20px;
        border-radius: 5px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}
    
    /* Horizontal ScrollBar */
    QScrollBar:horizontal {{
        border: none;
        background: {BACKGROUND};
        height: 10px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:horizontal {{
        background: {COMMENT};
        min-width: 20px;
        border-radius: 5px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        border: none;
        background: none;
    }}
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: none;
    }}

    /* Preview Label (QR Code) */
    PreviewLabel {{
        background-color: #FFFFFF;
        border-radius: 12px;
    }}
    """

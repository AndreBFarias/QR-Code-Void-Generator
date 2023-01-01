import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
                             QStackedWidget, QLabel, QLineEdit, QPushButton, QFrame, 
                             QFileDialog, QColorDialog, QSlider, QGroupBox, QCheckBox, 
                             QListWidgetItem, QScrollArea, QComboBox, QGridLayout, QSizePolicy)
from PyQt6.QtCore import Qt, QSize, QTimer, QUrl
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtGui import QIcon, QPixmap, QColor, QAction, QImage, QPainter, QDesktopServices
from PIL import Image

from ui.styles import DraculaTheme
from ui.components import (Toast, PreviewLabel, ClickableLabel, LogoPositionSelector, 
                           SocialPlatformSelector, LogoLabel)
from core.worker import QRWorker
from core.utils import save_image_dialog, copy_to_clipboard, pil_to_qpixmap, get_wifi_ssid_linux
from core.payloads import WifiPayload, PixPayload, SocialPayload
from core.config import cfg

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VOID | QRcode")
        
        # Configurable Window Size
        width = cfg.get_int('JanelaPrincipal', 'Largura', 1300)
        height = cfg.get_int('JanelaPrincipal', 'Altura', 850)
        self.setFixedSize(width, height)
        
        # Set Window Icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.theme = DraculaTheme()
        self.setStyleSheet(self.theme.STYLESHEET)

        # State
        self.current_qr_image = None
        self.logo_path = None
        self.fg_color = "#440d5c"
        self.bg_color = "#ffffff"
        self.request_id_counter = 0
        
        # Setup UI
        self.setup_ui()
        
        # Initial Generation
        QTimer.singleShot(500, lambda: self.generate_qr(manual=False))

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout: Sidebar | Content | Preview
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar (Left)
        self.setup_sidebar()
        main_layout.addWidget(self.sidebar_container)

        # 2. Content Area (Center)
        self.setup_content_area()
        # setup_content_area creates self.content_container
        main_layout.addWidget(self.content_container)

        # 3. Preview Panel (Right)
        self.setup_preview_panel()
        main_layout.addWidget(self.preview_container)
        
        # Toast
        self.toast = Toast(self)
        
        # Initial Selection (Delayed to ensure UI is ready)
        self.sidebar.setCurrentRow(0)

    def setup_sidebar(self):
        self.sidebar_container = QWidget()
        width = cfg.get_int('BlocoEsquerdo_Sidebar', 'Largura', 280)
        self.sidebar_container.setFixedWidth(width)
        self.sidebar_container.setStyleSheet(f"background-color: {DraculaTheme.SIDEBAR}; border: none;")
        
        layout = QVBoxLayout(self.sidebar_container)
        margin = cfg.get_int('BlocoEsquerdo_Sidebar', 'MargemInterna', 20)
        layout.setContentsMargins(0, margin, 0, 0) # Top margin from config
        layout.setSpacing(0)

        # 1. Header: Icon + Title
        header_layout = QVBoxLayout()
        header_layout.setSpacing(15)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # App Icon
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon.png')
        if os.path.exists(icon_path):
            # Increased size again by 150% (100 -> 150)
            pixmap = QPixmap(icon_path).scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel()
        # Increased font size by 150% (16px -> 24px)
        title_label.setText(f'<html><head/><body><p><span style=" font-size:24px; font-weight:600; color:#ffffff;">VOID</span><span style=" font-size:24px; font-weight:600; color:{DraculaTheme.PURPLE};"> | QRcode</span></p></body></html>')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        layout.addLayout(header_layout)
        
        # Spacer
        layout.addStretch(1)

        # 2. Menu: Navigation
        self.sidebar = QListWidget()
        self.sidebar.currentRowChanged.connect(self.change_page)
        # Increased font size for menu items
        self.sidebar.setStyleSheet(f"font-size: 18px; font-weight: 500;")
        
        # Fix Menu Height & Scrollbar
        menu_height = cfg.get_int('BlocoEsquerdo_Sidebar', 'AlturaMenu', 260)
        self.sidebar.setFixedHeight(menu_height)
        self.sidebar.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        layout.addWidget(self.sidebar)

        # Add Items
        items = [
            ("Link / URL", "menu-url.svg"),
            ("Wi-Fi", "wifi.svg"),
            ("Pix", "menu-pix.svg"),
            ("Redes Sociais", "menu-redes-sociais.svg")
        ]

        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logos')

        for name, icon_file in items:
            item = QListWidgetItem(name)
            
            # Fix for Wi-Fi icon
            if "wi-fi" in name.lower():
                icon_file = "wifi.svg"
                
            icon_path = os.path.join(assets_dir, icon_file)
            if os.path.exists(icon_path):
                item.setIcon(QIcon(icon_path))
            self.sidebar.addItem(item)
            
        # Spacer
        layout.addStretch(1)

        # 4. Container de Upload (Fundo)
        upload_frame = QFrame()
        # Removed border-top as requested
        upload_frame.setStyleSheet("background-color: #21222C;") 
        upload_layout = QVBoxLayout(upload_frame)
        upload_layout.setContentsMargins(15, 20, 15, 20)
        upload_layout.setSpacing(10)
        upload_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        height = cfg.get_int('BlocoEsquerdo_Sidebar', 'AlturaBoxUpload', 220)
        upload_frame.setFixedHeight(height)
        
        lbl_upload = QLabel("Logo Personalizada")
        # Increased font size by 150% (14px -> 21px)
        lbl_upload.setStyleSheet("color: #bd93f9; font-weight: bold; font-size: 21px;")
        lbl_upload.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_layout.addWidget(lbl_upload)
        
        # Horizontal Container for Drop Box + Button
        h_container = QWidget()
        h_layout = QHBoxLayout(h_container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(10)
        h_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Drop Box (Increased size ~25% -> 125x125)
        # Drop Box (Increased size ~25% -> 125x125)
        self.logo_preview_sidebar = LogoLabel("Arraste ou Selecione")
        self.logo_preview_sidebar.setFixedSize(125, 125) 
        self.logo_preview_sidebar.setStyleSheet(f"border: 2px dashed {DraculaTheme.COMMENT}; border-radius: 8px; color: {DraculaTheme.COMMENT}; font-size: 13px; padding: 10px; font-weight: bold;")
        self.logo_preview_sidebar.setScaledContents(True)
        self.logo_preview_sidebar.clicked.connect(self.upload_logo)
        self.logo_preview_sidebar.clearRequested.connect(self.clear_logo)
        h_layout.addWidget(self.logo_preview_sidebar)
        
        # Select Button
        self.upload_logo_btn = QPushButton("Selecionar Logo")
        self.upload_logo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Added visible border as requested
        self.upload_logo_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DraculaTheme.CURRENT_LINE};
                color: {DraculaTheme.FOREGROUND};
                border: 1px solid {DraculaTheme.PURPLE};
                border-radius: 8px;
                padding: 8px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {DraculaTheme.COMMENT};
            }}
        """)
        self.upload_logo_btn.setFixedWidth(130) # Increased width to fit text
        self.upload_logo_btn.clicked.connect(self.upload_logo)
        h_layout.addWidget(self.upload_logo_btn)
        
        upload_layout.addWidget(h_container)
        
        layout.addWidget(upload_frame)

    def setup_content_area(self):
        self.content_container = QWidget()
        layout = QVBoxLayout(self.content_container)
        
        margin = cfg.get_int('BlocoCentral_Formularios', 'MargemInterna', 40)
        spacing = cfg.get_int('BlocoCentral_Formularios', 'EspacamentoVertical', 15)
        
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.setSpacing(spacing)
        
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Pages
        self.page_link = self.create_link_page()
        self.page_wifi = self.create_wifi_page()
        self.page_pix = self.create_pix_page()
        self.page_social = self.create_social_page()
        
        self.stacked_widget.addWidget(self.page_link)
        self.stacked_widget.addWidget(self.page_wifi)
        self.stacked_widget.addWidget(self.page_pix)
        self.stacked_widget.addWidget(self.page_social)

    def create_page_header(self, title):
        label = QLabel(title)
        # Removed color from stylesheet to allow HTML styling
        label.setStyleSheet(f"font-size: 32px; font-weight: bold; margin-bottom: 30px;")
        return label

    def create_generate_button(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 1. Botão Gerar (Principal)
        btn_generate = QPushButton("Gerar QRcode")
        btn_generate.setObjectName("actionBtn")
        btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_generate.clicked.connect(lambda: self.generate_qr(manual=True))
        btn_generate.setFixedHeight(50)
        btn_generate.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # 2. Botão Salvar
        btn_save = QPushButton("Salvar")
        btn_save.setObjectName("secondaryBtn")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self.save_qr)
        btn_save.setFixedHeight(50)
        btn_save.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # 3. Botão Copiar
        btn_copy = QPushButton("Copiar")
        btn_copy.setObjectName("secondaryBtn")
        btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_copy.clicked.connect(self.copy_qr)
        btn_copy.setFixedHeight(50)
        btn_copy.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Adicionar ao Layout (Ordem: Gerar | Salvar | Copiar)
        layout.addWidget(btn_generate, stretch=2)
        layout.addWidget(btn_save, stretch=1)
        layout.addWidget(btn_copy, stretch=1)
        
        return container

    def create_link_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        layout.addWidget(self.create_page_header(f'<html><head/><body><p><span style="color:#ffffff;">Gerar</span><span style="color:#bd93f9;"> Link / URL</span></p></body></html>'))
        
        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("https://seu-site.com")
        # self.link_input.textChanged.connect(self.auto_generate)
        layout.addWidget(QLabel("URL do Site"))
        layout.addWidget(self.link_input)
        
        layout.addStretch()
        layout.addWidget(self.create_generate_button())
        return page

    def create_wifi_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        layout.addWidget(self.create_page_header(f'<html><head/><body><p><span style="color:#ffffff;">Gerar</span><span style="color:#bd93f9;"> Wi-Fi</span></p></body></html>'))
        
        layout.addWidget(QLabel("SSID (Nome da Rede)"))
        # SSID Input + Detect Button
        ssid_layout = QHBoxLayout()
        ssid_layout.setSpacing(10)
        
        self.wifi_ssid = QLineEdit()
        self.wifi_ssid.setPlaceholderText("Nome da Rede")
        # self.wifi_ssid.textChanged.connect(self.auto_generate)
        ssid_layout.addWidget(self.wifi_ssid)
        
        self.btn_detect = QPushButton("Detectar")
        self.btn_detect.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_detect.setStyleSheet(f"""
            QPushButton {{
                background-color: {DraculaTheme.CURRENT_LINE};
                color: {DraculaTheme.FOREGROUND};
                border-radius: {DraculaTheme.BORDER_RADIUS};
                border: 1px solid transparent; /* Match input border */
                font-weight: bold;
                padding: 0 15px;
                height: {DraculaTheme.INPUT_HEIGHT}; /* Match input height */
            }}
            QPushButton:hover {{
                background-color: {DraculaTheme.COMMENT};
            }}
        """)
        self.btn_detect.setFixedHeight(int(cfg.get_str('BlocoCentral_Formularios', 'AlturaInput', '45')))
        self.btn_detect.clicked.connect(self.detect_wifi)
        ssid_layout.addWidget(self.btn_detect)
        
        layout.addLayout(ssid_layout)
        
        layout.addWidget(QLabel("Senha"))
        
        # Password Input with Toggle (Fake Input Container)
        pass_container = QFrame()
        pass_container.setObjectName("fakeInput")
        # Enforce min-height to match other inputs
        input_height_val = int(cfg.get_str('BlocoCentral_Formularios', 'AlturaInput', '45'))
        pass_container.setFixedHeight(input_height_val) # FORCE FIXED HEIGHT
        # Ensure width matches by setting size policy
        pass_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        pass_container.setStyleSheet(f"""
            QFrame#fakeInput {{
                background-color: {DraculaTheme.CURRENT_LINE};
                border-radius: {DraculaTheme.BORDER_RADIUS};
                border: 1px solid transparent;
                height: {DraculaTheme.INPUT_HEIGHT};
            }}
            QFrame#fakeInput:focus-within {{
                border: 1px solid {DraculaTheme.PURPLE};
            }}
        """)
        pass_layout = QHBoxLayout(pass_container)
        pass_layout.setContentsMargins(0, 0, 0, 0)
        pass_layout.setSpacing(0)
        
        self.wifi_password = QLineEdit()
        self.wifi_password.setPlaceholderText(".......")
        self.wifi_password.setEchoMode(QLineEdit.EchoMode.Password)
        # self.wifi_password.textChanged.connect(self.auto_generate)
        # Transparent Input
        self.wifi_password.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                padding: 12px;
                color: #f8f8f2;
                font-size: 14px;
            }
        """)
        pass_layout.addWidget(self.wifi_password)
        
        self.btn_toggle_pass = QPushButton("◉")
        self.btn_toggle_pass.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_pass.setFixedWidth(40)
        # Transparent Button
        self.btn_toggle_pass.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {DraculaTheme.PURPLE};
                border: none;
                font-size: 18px;
                padding-right: 10px;
            }}
            QPushButton:hover {{
                color: {DraculaTheme.COMMENT};
            }}
        """)
        self.btn_toggle_pass.clicked.connect(self.toggle_password_visibility)
        pass_layout.addWidget(self.btn_toggle_pass)
        
        layout.addWidget(pass_container)
        
        self.wifi_encryption = QComboBox()
        self.wifi_encryption.addItems(["WPA/WPA2", "WEP", "Sem Senha"])
        self.wifi_encryption.currentIndexChanged.connect(self.auto_generate)
        layout.addWidget(QLabel("Tipo de Segurança"))
        layout.addWidget(self.wifi_encryption)
        
        self.wifi_hidden = QCheckBox("Rede Oculta")
        self.wifi_hidden.stateChanged.connect(self.auto_generate)
        layout.addWidget(self.wifi_hidden)
        
        layout.addStretch()
        layout.addWidget(self.create_generate_button())
        return page

    def create_pix_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        layout.addWidget(self.create_page_header(f'<html><head/><body><p><span style="color:#ffffff;">Gerar</span><span style="color:#bd93f9;"> Pix</span></p></body></html>'))
        
        self.pix_key = QLineEdit()
        self.pix_key.setPlaceholderText("CPF, CNPJ, E-mail ou Telefone")
        # self.pix_key.textChanged.connect(self.auto_generate)
        layout.addWidget(QLabel("Chave Pix"))
        layout.addWidget(self.pix_key)
        
        self.pix_name = QLineEdit()
        self.pix_name.setPlaceholderText("Nome do Beneficiário")
        # self.pix_name.textChanged.connect(self.auto_generate)
        layout.addWidget(QLabel("Nome Completo"))
        layout.addWidget(self.pix_name)
        
        self.pix_city = QLineEdit()
        self.pix_city.setPlaceholderText("Cidade do Beneficiário")
        # self.pix_city.textChanged.connect(self.auto_generate)
        layout.addWidget(QLabel("Cidade"))
        layout.addWidget(self.pix_city)
        
        self.pix_amount = QLineEdit()
        self.pix_amount.setPlaceholderText("0.00 (Opcional)")
        # self.pix_amount.textChanged.connect(self.auto_generate)
        layout.addWidget(QLabel("Valor (Opcional)"))
        layout.addWidget(self.pix_amount)
        
        self.pix_txid = QLineEdit()
        self.pix_txid.setPlaceholderText("Código da Transação (Opcional)")
        # self.pix_txid.textChanged.connect(self.auto_generate)
        layout.addWidget(QLabel("ID da Transação (TXID)"))
        layout.addWidget(self.pix_txid)
        
        layout.addStretch()
        layout.addWidget(self.create_generate_button())
        return page

    def create_social_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        layout.addWidget(self.create_page_header(f'<html><head/><body><p><span style="color:#ffffff;">Redes</span><span style="color:#bd93f9;"> Sociais</span></p></body></html>'))
        
        # Grid of Icons
        self.social_selector = SocialPlatformSelector()
        self.social_selector.platformSelected.connect(self.on_social_platform_selected)
        layout.addWidget(QLabel("Selecione a Plataforma"))
        layout.addWidget(self.social_selector)
        
        layout.addSpacing(20)
        
        # Input Area with Icon via CSS
        self.social_input = QLineEdit()
        self.social_input.setObjectName("iconInput") # Apply CSS for padding
        self.social_input.setPlaceholderText("Selecione uma rede acima...")
        # self.social_input.textChanged.connect(self.auto_generate)
        
        layout.addWidget(QLabel("Usuário / Link / Número"))
        layout.addWidget(self.social_input)
        
        layout.addStretch()
        layout.addWidget(self.create_generate_button())
        return page

    def setup_preview_panel(self):
        self.preview_container = QWidget()
        width = cfg.get_int('BlocoDireito_Preview', 'Largura', 500)
        self.preview_container.setFixedWidth(width)
        self.preview_container.setStyleSheet(f"background-color: {DraculaTheme.BACKGROUND}; border: none;")
        
        # Main Layout (Top-Down)
        layout = QVBoxLayout(self.preview_container)
        layout.setContentsMargins(20, 40, 20, 20) # Top 40px
        layout.setSpacing(0) # Manual spacing control
        
        # 1. QR Preview (Topo)
        self.qr_label = PreviewLabel()
        # Force 420px regardless of config for now, or update config default
        qr_size = 420 
        self.qr_label.setFixedSize(qr_size, qr_size)
        self.qr_label.leftClicked.connect(self.open_qr_link)
        self.qr_label.actionRequested.connect(self.handle_preview_action)
        layout.addWidget(self.qr_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Spacer 1
        layout.addStretch(1)
        
        # 2. CORES (Meio)
        colors_container = QWidget()
        colors_container.setStyleSheet("background: transparent;")
        colors_layout = QVBoxLayout(colors_container)
        colors_layout.setContentsMargins(20, 0, 20, 0)
        colors_layout.setSpacing(10)
        
        # Helper for Headers
        def make_header(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("font-weight: bold; font-size: 16px; color: #BD93F9; text-transform: none;")
            return lbl

        # --- A. CORES ---
        colors_layout.addWidget(make_header("Cores"))
        
        colors_row = QHBoxLayout()
        colors_row.setSpacing(10)
        
        # Frente
        colors_row.addWidget(QLabel("Frente:"))
        self.fg_color_btn = QPushButton()
        self.fg_color_btn.setFixedSize(34, 34)
        self.fg_color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fg_color_btn.setStyleSheet(f"background-color: {self.fg_color}; border: 2px solid #fff; border-radius: 17px;")
        self.fg_color_btn.clicked.connect(self.pick_fg_color)
        colors_row.addWidget(self.fg_color_btn)
        
        colors_row.addStretch()
        
        # Fundo
        colors_row.addWidget(QLabel("Fundo:"))
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedSize(34, 34)
        self.bg_color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bg_color_btn.setStyleSheet(f"background-color: {self.bg_color}; border: 2px solid #fff; border-radius: 17px;")
        self.bg_color_btn.clicked.connect(self.pick_bg_color)
        colors_row.addWidget(self.bg_color_btn)
        
        colors_layout.addLayout(colors_row)
        layout.addWidget(colors_container)
        
        # Spacer 2
        layout.addStretch(1)
        
        # 3. PERSONALIZAÇÃO DA LOGO (Fundo)
        logo_container = QWidget()
        logo_container.setStyleSheet("background: transparent;")
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(20, 0, 20, 20) # Bottom margin
        logo_layout.setSpacing(10)
        
        logo_layout.addWidget(make_header("Personalização da Logo"))
        
        # Position (Centered)
        pos_row = QHBoxLayout()
        pos_row.addStretch()
        
        self.logo_pos_selector = LogoPositionSelector()
        self.logo_pos_selector.positionChanged.connect(self.auto_generate)
        pos_row.addWidget(self.logo_pos_selector)
        
        pos_row.addStretch()
        logo_layout.addLayout(pos_row)
        
        # Opacidade
        logo_layout.addWidget(QLabel("Opacidade"))
        self.logo_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.logo_opacity_slider.setRange(0, 100)
        self.logo_opacity_slider.setValue(100)
        self.logo_opacity_slider.valueChanged.connect(self.auto_generate)
        logo_layout.addWidget(self.logo_opacity_slider)
        
        layout.addWidget(logo_container)
        
        # Final Spacer (Optional, to keep bottom margin)
        # layout.addStretch(1)

    # --- Logic ---

    def change_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        
        # --- LIMPEZA VISUAL ---
        self.current_qr_image = None
        self.qr_label.clear()
        self.qr_label.setText("Preview") # Texto placeholder
        
        # Limpa a logo anterior (exceto na aba Social que gerencia seus ícones)
        if index != 3: 
            self.logo_path = None
            self.logo_preview_sidebar.clear()
            self.logo_preview_sidebar.setText("Arraste ou Selecione")
            self.logo_preview_sidebar.setStyleSheet(f"border: 2px dashed {DraculaTheme.COMMENT}; border-radius: 8px; color: {DraculaTheme.COMMENT}; font-size: 10px; padding: 10px;")

    def detect_wifi(self):
        ssid = get_wifi_ssid_linux()
        if ssid:
            self.wifi_ssid.setText(ssid)
            # Optional: Show a toast or status message
        else:
            # Fallback/Error handling
            self.wifi_ssid.setPlaceholderText("Erro: 'nmcli' não encontrado. Instale network-manager.")

    def toggle_password_visibility(self):
        if self.wifi_password.echoMode() == QLineEdit.EchoMode.Password:
            self.wifi_password.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_toggle_pass.setStyleSheet(self.btn_toggle_pass.styleSheet().replace(DraculaTheme.PURPLE, DraculaTheme.GREEN))
        else:
            self.wifi_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_toggle_pass.setStyleSheet(self.btn_toggle_pass.styleSheet().replace(DraculaTheme.GREEN, DraculaTheme.PURPLE))

    def on_social_platform_selected(self, name, icon_path):
        self.logo_path = icon_path
        self.update_logo_preview(icon_path)
        
        # Update Input Style (Icon)
        # Remove previous actions (icons)
        for action in self.social_input.actions():
            self.social_input.removeAction(action)
            
        # Add new icon action
        if os.path.exists(icon_path):
            self.social_input.addAction(QIcon(icon_path), QLineEdit.ActionPosition.LeadingPosition)
            
        # Reset stylesheet to remove any background image artifacts if present, keeping base style
        self.social_input.setStyleSheet(f"""
            QLineEdit {{
                padding-left: 5px; /* Reset padding */
            }}
        """)
        
        # Update placeholder
        placeholders = {
            "WhatsApp": "Número (ex: 5511999999999)",
            "Email": "Endereço de E-mail",
            "Instagram": "Usuário do Instagram",
            "Twitter": "Usuário do Twitter",
            "Facebook": "Usuário do Facebook",
            "LinkedIn": "URL do Perfil",
            "GitHub": "Usuário do GitHub",
            "YouTube": "URL do Canal",
            "Discord": "Link de Convite",
            "Telegram": "Usuário (sem @)",
            "Steam": "ID ou URL",
            "Pinterest": "Usuário"
        }
        self.social_input.setPlaceholderText(placeholders.get(name, "Digite aqui..."))
        self.generate_qr()

    def upload_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Logo", "", "Images (*.png *.jpg *.jpeg *.svg)")
        if file_path:
            self.logo_path = file_path
            self.update_logo_preview(file_path)
            self.generate_qr()
            
    def update_logo_preview(self, path):
        # Proteção contra crash se path for None ou vazio #2
        if not path:
            # Opcional: Reset visual se necessário
            self.logo_preview_sidebar.clear()
            self.logo_preview_sidebar.setText("Arraste ou Selecione")
            self.logo_preview_sidebar.setStyleSheet(f"border: 2px dashed {DraculaTheme.COMMENT}; border-radius: 8px; color: {DraculaTheme.COMMENT}; font-size: 13px; padding: 10px; font-weight: bold;")
            return

        if os.path.exists(path):
            pixmap = QPixmap(path).scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_preview_sidebar.setPixmap(pixmap)
            self.logo_preview_sidebar.setStyleSheet("border: none;")

    def pick_fg_color(self):
        color = QColorDialog.getColor(QColor(self.fg_color), self, "Cor da Frente")
        if color.isValid():
            self.fg_color = color.name()
            self.fg_color_btn.setStyleSheet(f"background-color: {self.fg_color}; border: 1px solid #fff; border-radius: 8px;")
            self.generate_qr()

    def pick_bg_color(self):
        color = QColorDialog.getColor(QColor(self.bg_color), self, "Cor do Fundo")
        if color.isValid():
            self.bg_color = color.name()
            self.bg_color_btn.setStyleSheet(f"background-color: {self.bg_color}; border: 1px solid #fff; border-radius: 8px;")
            self.generate_qr()

    def get_current_data(self):
        index = self.stacked_widget.currentIndex()
        
        if index == 0: # Link
            text = self.link_input.text().strip()
            return text if text else None
            
        elif index == 1: # WiFi
            ssid = self.wifi_ssid.text().strip()
            if not ssid: return None
            
            pwd = self.wifi_password.text()
            enc = self.wifi_encryption.currentText()
            hidden = self.wifi_hidden.isChecked()
            
            enc_map = {"WPA/WPA2": "WPA", "WEP": "WEP", "Sem Senha": "nopass"}
            return WifiPayload(ssid, pwd, enc_map.get(enc, "WPA"), hidden).to_string()
            
        elif index == 2: # Pix
            key = self.pix_key.text().strip()
            name = self.pix_name.text().strip()
            city = self.pix_city.text().strip()
            
            if not key or not name or not city:
                return None
                
            return PixPayload(
                key=key,
                name=name,
                city=city,
                amount=self.pix_amount.text(),
                txid=self.pix_txid.text()
            ).to_string()
            
        elif index == 3: # Social
            # Obtém a plataforma selecionada
            platform = self.social_selector.selected_platform
            value = self.social_input.text().strip()
            

            
            if not value: return None
            
            # Normalização para evitar erros de acento ou case
            platform_key = platform.lower().replace("-", "") # vira 'email', 'whatsapp', etc
            
            # Lógica de decisão explícita
            if "email" in platform_key:
                return SocialPayload.email(value)
                
            elif "whatsapp" in platform_key:
                return SocialPayload.whatsapp(value)
            elif "instagram" in platform_key:
                return SocialPayload.instagram(value)
            elif "twitter" in platform_key or "x" == platform_key:
                return SocialPayload.twitter(value)
            elif "facebook" in platform_key:
                return SocialPayload.facebook(value)
            elif "linkedin" in platform_key:
                return SocialPayload.linkedin(value)
            elif "github" in platform_key:
                return SocialPayload.github(value)
            elif "youtube" in platform_key:
                return SocialPayload.youtube(value)
            elif "discord" in platform_key:
                return SocialPayload.discord(value)
            elif "telegram" in platform_key:
                return SocialPayload.telegram(value)
            elif "steam" in platform_key:
                return SocialPayload.steam(value)
            elif "pinterest" in platform_key:
                return SocialPayload.pinterest(value)
                
            # Fallback genérico
            return value
            
        return None

    def auto_generate(self):
        self.generate_qr(manual=False)

    def generate_qr(self, manual=False):
        self.request_id_counter += 1
        req_id = self.request_id_counter
        
        data = self.get_current_data()
        
        if not data:
            if manual:
                # Find the generate button container to position the toast
                # It's the last widget in the current page layout
                current_page = self.stacked_widget.currentWidget()
                # We need to find the button container. It's usually the last item.
                # But safer to store a reference to it when creating pages? 
                # Or just use the content_container which is the parent of stacked_widget
                
                # Let's try to find the button container in the current page
                # It is added last in create_link_page, create_wifi_page, etc.
                # layout.addWidget(self.create_generate_button())
                
                # Actually, let's just use the content_container bottom area
                # Or better, pass the specific button if possible.
                # Since we don't have a direct reference to the button instance easily accessible here across all pages without refactoring,
                # let's position it at the bottom of the content_container.
                
                self.toast.show_message("Preencha os campos obrigatórios!", target_widget=self.content_container)
            # Optional: Clear preview or show placeholder
            # self.qr_label.clear() 
            # self.current_qr_image = None
            return


        
        # Always use High Error Correction as requested
        ec = "H"
        
        # Cancel previous worker if running
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()

        # Load logo (handle SVG if needed)
        logo_img = self.load_logo_to_pil(self.logo_path)

        self.worker = QRWorker(
            request_id=req_id,
            data=data,
            ec=ec,
            size=13, # Increased by 30% for better quality
            rounded=True, # Ensure rounded modules
            logo_img=logo_img,
            logo_size=15, # Fixed size: 15% (Safe for H level)
            logo_opacity=self.logo_opacity_slider.value(),
            logo_pos=self.logo_pos_selector.current_pos,
            fill_color=self.fg_color,
            back_color=self.bg_color
        )
        
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.error.connect(self.on_generation_error)
        self.worker.start()

    def load_logo_to_pil(self, path):
        if not path or not os.path.exists(path):
            return None
            
        try:
            if path.lower().endswith('.svg'):
                # Render SVG using QIcon/QPixmap
                icon = QIcon(path)
                # Render at high resolution
                pixmap = icon.pixmap(1000, 1000)
                if pixmap.isNull():
                    return None
                    
                qimg = pixmap.toImage()
                qimg = qimg.convertToFormat(QImage.Format.Format_RGBA8888)
                
                width = qimg.width()
                height = qimg.height()
                
                ptr = qimg.bits()
                ptr.setsize(height * width * 4)
                arr = ptr.asstring()
                
                return Image.frombytes("RGBA", (width, height), arr)
            else:
                # Standard raster image
                return Image.open(path).convert("RGBA")
        except Exception as e:
            print(f"Error loading logo in UI: {e}")
            return None
    def handle_preview_action(self, action):
        if action == "open":
            self.open_qr_link()
        elif action == "save":
            self.save_qr()
        elif action == "clear":
            self.clear_qr()
        elif action == "print":
            self.print_qr()

    def save_qr(self):
        if not self.current_qr_image:
            self.toast.show_message("Nenhum QR Code para salvar!")
            return

        from PyQt6.QtWidgets import QFileDialog, QMessageBox, QDialog, QHBoxLayout
        
        # Remove spaces in filter string to avoid issues on some platforms
        # Also ensure extensions are correctly mapped
        # "Todos os Arquivos (*)" is first to avoid pre-selecting an extension visually
        filters = "Todos os Arquivos (*);;Imagens PNG (*.png);;Imagens JPG (*.jpg);;Imagens JPEG (*.jpeg);;Documento PDF (*.pdf);;Vetor SVG (*.svg)"
        
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Salvar QR Code",
            "qrcode", 
            filters
        )
        
        if file_path:

            # Enforce extension based on filter
            if selected_filter:
                ext_map = {
                    "Imagens PNG (*.png)": ".png",
                    "Imagens JPG (*.jpg)": ".jpg",
                    "Imagens JPEG (*.jpeg)": ".jpeg",
                    "Documento PDF (*.pdf)": ".pdf",
                    "Vetor SVG (*.svg)": ".svg",
                    "Todos os Arquivos (*)": ".png" # Default to PNG if generic filter
                }
                expected_ext = ext_map.get(selected_filter)
                
                if expected_ext:
                    # Check if file has an extension
                    root, current_ext = os.path.splitext(file_path)
                    
                    # Special case for "Todos os Arquivos": Only append PNG if NO extension is typed
                    if selected_filter == "Todos os Arquivos (*)":
                         if not current_ext:
                             file_path += ".png"
                    # For specific filters, enforce the extension
                    elif not current_ext or current_ext.lower() != expected_ext:
                        file_path = root + expected_ext

            try:
                # Handle PDF/SVG specifically if needed, otherwise PIL handles most
                if file_path.lower().endswith('.pdf'):
                    self.current_qr_image.save(file_path, "PDF", resolution=100.0)
                else:
                    self.current_qr_image.save(file_path)
                    
                self.show_save_success_popup(file_path)
            except Exception as e:
                print(f"Error saving image: {e}")
                self.toast.show_message(f"Erro ao salvar: {e}")

    def show_save_success_popup(self, file_path):
        dialog = QDialog(self)
        dialog.setWindowTitle("QRcode Salvo")
        dialog.setFixedSize(400, 150)
        dialog.setStyleSheet(f"background-color: {DraculaTheme.BACKGROUND}; color: {DraculaTheme.FOREGROUND};")
        
        layout = QVBoxLayout(dialog)
        
        lbl = QLabel("QR Code salvo com sucesso!")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(lbl)
        
        btn_layout = QHBoxLayout()
        
        btn_open = QPushButton("Abrir QRcode")
        btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open.clicked.connect(lambda: self._open_file(file_path))
        
        btn_folder = QPushButton("Abrir Pasta")
        btn_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_folder.clicked.connect(lambda: self._open_folder(file_path))
        
        btn_new = QPushButton("Gerar Novo")
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.clicked.connect(dialog.accept)
        
        # Style buttons
        for btn in [btn_open, btn_folder, btn_new]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {DraculaTheme.CURRENT_LINE};
                    border: 1px solid {DraculaTheme.PURPLE};
                    border-radius: 5px;
                    padding: 8px;
                    color: {DraculaTheme.FOREGROUND};
                }}
                QPushButton:hover {{
                    background-color: {DraculaTheme.COMMENT};
                }}
            """)
            btn_layout.addWidget(btn)
            
        layout.addLayout(btn_layout)
        dialog.exec()

    def _open_file(self, path):
        import subprocess, sys
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':
            subprocess.call(['open', path])
        else:
            subprocess.call(['xdg-open', path])

    def _open_folder(self, path):
        folder = os.path.dirname(path)
        self._open_file(folder)

    def open_qr_link(self):
        data = self.get_current_data()
        if data:

            QDesktopServices.openUrl(QUrl(data))

    def print_qr(self):
        if not self.current_qr_image:
            self.toast.show_message("Nenhum QR Code para imprimir!")
            return

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            painter = QPainter(printer)
            rect = painter.viewport()
            size = self.current_qr_image.size()
            size.scale(rect.size(), Qt.AspectRatioMode.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.current_qr_image.rect())
            painter.drawPixmap(0, 0, self.current_qr_image)
            painter.end()

    def clear_qr(self):
        self.current_qr_image = None
        self.qr_label.clear()
        self.qr_label.original_pixmap = None
        self.clear_logo() # Also clear logo as requested

    def clear_logo(self):
        self.logo_path = None
        self.update_logo_preview(None)
        self.auto_generate() # Regenerate QR without logo
    def on_generation_finished(self, img, req_id):
        if req_id != self.request_id_counter:
            return
            
        self.current_qr_image = img
        qpixmap = pil_to_qpixmap(img)
        self.qr_label.setPixmap(qpixmap)

    def on_generation_error(self, error_msg):
        self.toast.show_message(f"Erro: {error_msg}")

    def save_qr(self):
        if self.current_qr_image:
            save_image_dialog(self.current_qr_image, self)
        else:
            self.toast.show_message("Nenhum QR Code gerado!")

    def copy_qr(self):
        if self.current_qr_image:
            copy_to_clipboard(self.current_qr_image)
            self.toast.show_message("Copiado para a área de transferência!")
        else:
            self.toast.show_message("Nenhum QR Code gerado!")

import os
import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QStackedWidget, QLabel, QLineEdit, QPushButton, QFrame, QFileDialog, QColorDialog, QSlider, QGroupBox, QCheckBox, QListWidgetItem, QScrollArea, QComboBox, QGridLayout, QSizePolicy, QDialog
from PyQt6.QtCore import Qt, QSize, QTimer, QUrl
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtGui import QIcon, QPixmap, QColor, QAction, QImage, QPainter, QDesktopServices
from PyQt6.QtGui import QIcon, QPixmap, QColor, QAction, QImage, QPainter, QDesktopServices
from PIL import Image
import logging
logger = logging.getLogger(__name__)
from ui.styles import DraculaTheme
from ui.components import Toast, PreviewLabel, ClickableLabel, LogoPositionSelector, SocialPlatformSelector, LogoLabel
from core.worker import QRWorker
from core.utils import save_image_dialog, copy_to_clipboard, pil_to_qpixmap, get_wifi_ssid_linux
from core.payloads import WifiPayload, PixPayload, SocialPayload
from core.config import cfg

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('VOID | QRcode')
        width = cfg.get_int('JanelaPrincipal', 'Largura', 1400)
        height = cfg.get_int('JanelaPrincipal', 'Altura', 850)
        self.setFixedSize(width, height)
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.theme = DraculaTheme()
        self.setStyleSheet(self.theme.STYLESHEET)
        self.current_qr_image = None
        self.logo_path = None
        self.fg_color = '#440d5c'
        self.bg_color = '#ffffff'
        self.request_id_counter = 0
        self.setup_ui()
        QTimer.singleShot(500, lambda : self.generate_qr(manual=False))

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setup_sidebar()
        main_layout.addWidget(self.sidebar_container)
        self.setup_content_area()
        main_layout.addWidget(self.content_container)
        self.setup_preview_panel()
        main_layout.addWidget(self.preview_container)
        self.toast = Toast(self)
        self.sidebar.setCurrentRow(0)

    def setup_sidebar(self):
        self.sidebar_container = QWidget()
        width = cfg.get_int('BlocoEsquerdo_Sidebar', 'Largura', 280)
        self.sidebar_container.setFixedWidth(width)
        self.sidebar_container.setStyleSheet(f'background-color: {DraculaTheme.SIDEBAR}; border: none;')
        layout = QVBoxLayout(self.sidebar_container)
        margin = cfg.get_int('BlocoEsquerdo_Sidebar', 'MargemInterna', 20)
        layout.setContentsMargins(0, margin, 0, 0)
        layout.setSpacing(0)
        header_layout = QVBoxLayout()
        header_layout.setSpacing(15)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon.png')
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_label)
        title_label = QLabel()
        title_label.setText(f'<html><head/><body><p><span style=" font-size:26px; font-weight:600; color:#ffffff;">VOID</span><span style=" font-size:26px; font-weight:600; color:{DraculaTheme.PURPLE};"> | QRcode</span></p></body></html>')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        layout.addLayout(header_layout)
        layout.addStretch(1)
        self.sidebar = QListWidget()
        self.sidebar.currentRowChanged.connect(self.change_page)
        self.sidebar.setStyleSheet(f'font-size: 20px; font-weight: 500;')
        menu_height = cfg.get_int('BlocoEsquerdo_Sidebar', 'AlturaMenu', 260)
        self.sidebar.setFixedHeight(menu_height)
        self.sidebar.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self.sidebar)
        items = [('Link / URL', 'menu-url.svg'), ('Wi-Fi', 'wifi.svg'), ('Pix', 'menu-pix.svg'), ('Redes Sociais', 'menu-redes-sociais.svg')]
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logos')
        for (name, icon_file) in items:
            item = QListWidgetItem(name)
            if 'wi-fi' in name.lower():
                icon_file = 'wifi.svg'
            icon_path = os.path.join(assets_dir, icon_file)
            if os.path.exists(icon_path):
                item.setIcon(QIcon(icon_path))
            self.sidebar.addItem(item)
        layout.addStretch(1)
        upload_frame = QFrame()
        upload_frame.setStyleSheet('background-color: #21222C;')
        upload_layout = QVBoxLayout(upload_frame)
        upload_layout.setContentsMargins(15, 20, 15, 20)
        upload_layout.setSpacing(10)
        upload_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        height = cfg.get_int('BlocoEsquerdo_Sidebar', 'AlturaBoxUpload', 220)
        upload_frame.setFixedHeight(height)
        lbl_upload = QLabel('Logo Personalizada')
        lbl_upload.setStyleSheet('color: #bd93f9; font-weight: bold; font-size: 21px;')
        lbl_upload.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_layout.addWidget(lbl_upload)
        h_container = QWidget()
        h_layout = QHBoxLayout(h_container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(10)
        h_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_preview_sidebar = LogoLabel('Arraste ou Selecione')
        self.logo_preview_sidebar.setFixedSize(125, 125)
        self.logo_preview_sidebar.setStyleSheet(f'border: 2px dashed {DraculaTheme.COMMENT}; border-radius: 8px; color: {DraculaTheme.COMMENT}; font-size: 14px; padding: 10px; font-weight: bold;')
        self.logo_preview_sidebar.setScaledContents(True)
        self.logo_preview_sidebar.clicked.connect(self.upload_logo)
        self.logo_preview_sidebar.clearRequested.connect(self.clear_logo)
        h_layout.addWidget(self.logo_preview_sidebar)
        self.upload_logo_btn = QPushButton('Selecionar Logo')
        self.upload_logo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.upload_logo_btn.setStyleSheet(f'\n            QPushButton {{\n                background-color: {DraculaTheme.CURRENT_LINE};\n                color: {DraculaTheme.FOREGROUND};\n                border: 1px solid {DraculaTheme.PURPLE};\n                border-radius: 8px;\n                padding: 8px;\n                font-size: 11px; /* Reduced to 11px */\n                font-weight: bold;\n            }}\n            QPushButton:hover {{\n                background-color: {DraculaTheme.COMMENT};\n            }}\n        ')
        self.upload_logo_btn.setFixedWidth(130)
        self.upload_logo_btn.clicked.connect(self.upload_logo)
        h_layout.addWidget(self.upload_logo_btn)
        upload_layout.addWidget(h_container)
        layout.addWidget(upload_frame)

    def setup_content_area(self):
        self.content_container = QWidget()
        layout = QVBoxLayout(self.content_container)
        margin = cfg.get_int('BlocoCentral_Formularios', 'MargemInterna', 40)
        spacing = cfg.get_int('BlocoCentral_Formularios', 'EspacamentoVertical', 15)
        layout.setContentsMargins(5, margin, 5, margin)
        layout.setSpacing(spacing)
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
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
        label.setStyleSheet(f'font-size: 34px; font-weight: bold; margin-bottom: 30px;')
        return label

    def create_generate_button(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_generate = QPushButton('Gerar QRcode')
        btn_generate.setObjectName('actionBtn')
        btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_generate.clicked.connect(lambda : self.generate_qr(manual=True))
        btn_generate.setFixedHeight(50)
        btn_generate.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_save = QPushButton('Salvar')
        btn_save.setObjectName('secondaryBtn')
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self.save_qr)
        btn_save.setFixedHeight(50)
        btn_save.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_copy = QPushButton('Copiar')
        btn_copy.setObjectName('secondaryBtn')
        btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_copy.clicked.connect(self.copy_qr)
        btn_copy.setFixedHeight(50)
        btn_copy.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
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
        self.link_input.setPlaceholderText('https://seu-site.com')
        layout.addWidget(QLabel('URL do Site'))
        layout.addWidget(self.link_input)
        layout.addStretch()
        layout.addWidget(self.create_generate_button())
        return page

    def create_wifi_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.create_page_header(f'<html><head/><body><p><span style="color:#ffffff;">Gerar</span><span style="color:#bd93f9;"> Wi-Fi</span></p></body></html>'))
        layout.addWidget(QLabel('SSID (Nome da Rede)'))
        ssid_layout = QHBoxLayout()
        ssid_layout.setSpacing(10)
        self.wifi_ssid = QLineEdit()
        self.wifi_ssid.setPlaceholderText('Nome da Rede')
        ssid_layout.addWidget(self.wifi_ssid)
        self.btn_detect = QPushButton('Detectar')
        self.btn_detect.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_detect.setStyleSheet(f'\n            QPushButton {{\n                background-color: {DraculaTheme.CURRENT_LINE};\n                color: {DraculaTheme.FOREGROUND};\n                border-radius: {DraculaTheme.BORDER_RADIUS};\n                border: 1px solid transparent; /* Match input border */\n                font-weight: bold;\n                padding: 0 15px;\n                height: {DraculaTheme.INPUT_HEIGHT}; /* Match input height */\n            }}\n            QPushButton:hover {{\n                background-color: {DraculaTheme.COMMENT};\n            }}\n        ')
        self.btn_detect.setFixedHeight(int(cfg.get_str('BlocoCentral_Formularios', 'AlturaInput', '45')))
        self.btn_detect.clicked.connect(self.detect_wifi)
        ssid_layout.addWidget(self.btn_detect)
        layout.addLayout(ssid_layout)
        layout.addWidget(QLabel('Senha'))
        pass_container = QFrame()
        pass_container.setObjectName('fakeInput')
        input_height_val = int(cfg.get_str('BlocoCentral_Formularios', 'AlturaInput', '45'))
        pass_container.setFixedHeight(input_height_val)
        pass_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        pass_container.setStyleSheet(f'\n            QFrame#fakeInput {{\n                background-color: {DraculaTheme.CURRENT_LINE};\n                border-radius: {DraculaTheme.BORDER_RADIUS};\n                border: 1px solid transparent;\n                height: {DraculaTheme.INPUT_HEIGHT};\n            }}\n            QFrame#fakeInput:focus-within {{\n                border: 1px solid {DraculaTheme.PURPLE};\n            }}\n        ')
        pass_layout = QHBoxLayout(pass_container)
        pass_layout.setContentsMargins(0, 0, 0, 0)
        pass_layout.setSpacing(0)
        self.wifi_password = QLineEdit()
        self.wifi_password.setPlaceholderText('.......')
        self.wifi_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.wifi_password.setStyleSheet('\n            QLineEdit {\n                background: transparent;\n                border: none;\n                padding: 12px;\n                color: #f8f8f2;\n                font-size: 16px;\n                font-weight: bold;\n            }\n        ')
        pass_layout.addWidget(self.wifi_password)
        self.btn_toggle_pass = QPushButton('◉')
        self.btn_toggle_pass.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_pass.setFixedWidth(40)
        self.btn_toggle_pass.setStyleSheet(f'\n            QPushButton {{\n                background: transparent;\n                color: {DraculaTheme.PURPLE};\n                border: none;\n                font-size: 20px;\n                padding-right: 10px;\n            }}\n            QPushButton:hover {{\n                color: {DraculaTheme.COMMENT};\n            }}\n        ')
        self.btn_toggle_pass.clicked.connect(self.toggle_password_visibility)
        pass_layout.addWidget(self.btn_toggle_pass)
        layout.addWidget(pass_container)
        self.wifi_encryption = QComboBox()
        self.wifi_encryption.addItems(['WPA/WPA2', 'WEP', 'Sem Senha'])
        self.wifi_encryption.currentIndexChanged.connect(self.auto_generate)
        layout.addWidget(QLabel('Tipo de Segurança'))
        layout.addWidget(self.wifi_encryption)
        self.wifi_hidden = QCheckBox('Rede Oculta')
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
        self.pix_key.setPlaceholderText('CPF, CNPJ, E-mail ou Telefone')
        layout.addWidget(QLabel('Chave Pix'))
        layout.addWidget(self.pix_key)
        self.pix_name = QLineEdit()
        self.pix_name.setPlaceholderText('Nome do Beneficiário')
        layout.addWidget(QLabel('Nome Completo'))
        layout.addWidget(self.pix_name)
        self.pix_city = QLineEdit()
        self.pix_city.setPlaceholderText('Cidade do Beneficiário')
        layout.addWidget(QLabel('Cidade'))
        layout.addWidget(self.pix_city)
        self.pix_amount = QLineEdit()
        self.pix_amount.setPlaceholderText('0.00 (Opcional)')
        layout.addWidget(QLabel('Valor (Opcional)'))
        layout.addWidget(self.pix_amount)
        self.pix_txid = QLineEdit()
        self.pix_txid.setPlaceholderText('Código da Transação (Opcional)')
        layout.addWidget(QLabel('ID da Transação (TXID)'))
        layout.addWidget(self.pix_txid)
        layout.addStretch()
        layout.addWidget(self.create_generate_button())
        return page

    def create_social_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.create_page_header(f'<html><head/><body><p><span style="color:#ffffff;">Redes</span><span style="color:#bd93f9;"> Sociais</span></p></body></html>'))
        self.social_selector = SocialPlatformSelector()
        self.social_selector.platformSelected.connect(self.on_social_platform_selected)
        layout.addWidget(QLabel('Selecione a Plataforma'))
        layout.addWidget(self.social_selector)
        layout.addSpacing(20)
        self.social_input = QLineEdit()
        self.social_input.setObjectName('iconInput')
        self.social_input.setPlaceholderText('Selecione uma rede acima...')
        layout.addWidget(QLabel('Usuário / Link / Número'))
        layout.addWidget(self.social_input)
        layout.addStretch()
        layout.addWidget(self.create_generate_button())
        return page

    def setup_preview_panel(self):
        self.preview_container = QWidget()
        width = cfg.get_int('BlocoDireito_Preview', 'Largura', 600)
        self.preview_container.setFixedWidth(width)
        self.preview_container.setStyleSheet(f'background-color: {DraculaTheme.BACKGROUND}; border: none;')
        layout = QVBoxLayout(self.preview_container)
        layout.setContentsMargins(20, 40, 20, 20)
        layout.setSpacing(0)
        self.qr_label = PreviewLabel()
        qr_size = 560
        self.qr_label.setFixedSize(qr_size, qr_size)
        self.qr_label.leftClicked.connect(self.open_qr_link)
        self.qr_label.actionRequested.connect(self.handle_preview_action)
        layout.addWidget(self.qr_label, alignment=Qt.AlignmentFlag.AlignCenter)

        def make_header(text):
            lbl = QLabel(text)
            lbl.setStyleSheet('font-weight: bold; font-size: 18px; color: #BD93F9; text-transform: none;')
            return lbl
        layout.addStretch(1)
        lbl_personalizacao = QLabel('Personalização da Logo')
        lbl_personalizacao.setStyleSheet('color: #ff79c6; font-weight: bold; font-size: 21px; margin-top: 0px;')
        lbl_personalizacao.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_personalizacao)
        layout.addSpacing(15)
        logo_container = QWidget()
        logo_container.setStyleSheet('background: transparent;')
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(20, 0, 20, 20)
        logo_layout.setSpacing(10)
        h_logo_container = QWidget()
        h_logo_layout = QHBoxLayout(h_logo_container)
        h_logo_layout.setContentsMargins(0, 0, 0, 0)
        h_logo_layout.setSpacing(50)
        self.logo_pos_selector = LogoPositionSelector()
        self.logo_pos_selector.positionChanged.connect(self.auto_generate)
        h_logo_layout.addWidget(self.logo_pos_selector)
        opacity_container = QWidget()
        opacity_layout = QVBoxLayout(opacity_container)
        opacity_layout.setContentsMargins(0, 0, 0, 0)
        opacity_layout.setSpacing(5)
        opacity_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        lbl_opacity = QLabel('Opacidade')
        lbl_opacity.setStyleSheet('color: #f8f8f2; font-size: 14px;')
        opacity_layout.addWidget(lbl_opacity)
        self.logo_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.logo_opacity_slider.setRange(0, 100)
        self.logo_opacity_slider.setValue(100)
        self.logo_opacity_slider.setFixedWidth(120)
        self.logo_opacity_slider.setFixedHeight(22)
        self.logo_opacity_slider.setStyleSheet(f'\n            QSlider::groove:horizontal {{\n                border: 1px solid {DraculaTheme.COMMENT};\n                height: 8px;\n                background: {DraculaTheme.CURRENT_LINE};\n                margin: 2px 0;\n                border-radius: 4px;\n            }}\n            QSlider::handle:horizontal {{\n                background: {DraculaTheme.PURPLE};\n                border: 1px solid {DraculaTheme.PURPLE};\n                width: 18px;\n                height: 18px;\n                margin: -5px 0;\n                border-radius: 9px;\n            }}\n        ')
        self.logo_opacity_slider.valueChanged.connect(self.auto_generate)
        opacity_layout.addWidget(self.logo_opacity_slider)
        h_logo_layout.addWidget(opacity_container)
        colors_container = QWidget()
        colors_layout = QVBoxLayout(colors_container)
        colors_layout.setContentsMargins(0, 0, 0, 0)
        colors_layout.setSpacing(5)
        colors_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        lbl_colors = QLabel('Cores')
        lbl_colors.setStyleSheet('color: #f8f8f2; font-size: 14px;')
        colors_layout.addWidget(lbl_colors)
        colors_row = QHBoxLayout()
        colors_row.setSpacing(10)
        colors_row.addWidget(QLabel('Dentro'))
        self.fg_color_btn = QPushButton()
        self.fg_color_btn.setFixedSize(30, 30)
        self.fg_color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fg_color_btn.setStyleSheet(f'background-color: {self.fg_color}; border: 2px solid #fff; border-radius: 15px;')
        self.fg_color_btn.setToolTip('Cor da Frente')
        self.fg_color_btn.clicked.connect(self.pick_fg_color)
        colors_row.addWidget(self.fg_color_btn)
        colors_row.addWidget(QLabel('Fora'))
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedSize(30, 30)
        self.bg_color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bg_color_btn.setStyleSheet(f'background-color: {self.bg_color}; border: 2px solid #fff; border-radius: 15px;')
        self.bg_color_btn.setToolTip('Cor do Fundo')
        self.bg_color_btn.clicked.connect(self.pick_bg_color)
        colors_row.addWidget(self.bg_color_btn)
        colors_layout.addLayout(colors_row)
        h_logo_layout.addWidget(colors_container)
        h_logo_layout.addWidget(colors_container)
        h_logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(h_logo_container)
        layout.addWidget(logo_container)
        layout.addStretch(1)

    def change_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        self.current_qr_image = None
        self.qr_label.clear()
        self.qr_label.setText('')
        if index != 3:
            self.logo_path = None
            self.logo_preview_sidebar.clear()
            self.logo_preview_sidebar.setText('Arraste ou Selecione')
            self.logo_preview_sidebar.setStyleSheet(f'border: 2px dashed {DraculaTheme.COMMENT}; border-radius: 8px; color: {DraculaTheme.COMMENT}; font-size: 14px; padding: 10px; font-weight: bold;')

    def detect_wifi(self):
        ssid = get_wifi_ssid_linux()
        if ssid:
            self.wifi_ssid.setText(ssid)
        else:
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
        for action in self.social_input.actions():
            self.social_input.removeAction(action)
        if os.path.exists(icon_path):
            self.social_input.addAction(QIcon(icon_path), QLineEdit.ActionPosition.LeadingPosition)
        self.social_input.setStyleSheet(f'\n            QLineEdit {{\n                padding-left: 5px; /* Reset padding */\n            }}\n        ')
        placeholders = {'WhatsApp': 'Número (ex: 5511999999999)', 'Email': 'Endereço de E-mail', 'Instagram': 'Usuário do Instagram', 'Twitter': 'Usuário do Twitter', 'Facebook': 'Usuário do Facebook', 'LinkedIn': 'URL do Perfil', 'GitHub': 'Usuário do GitHub', 'YouTube': 'URL do Canal', 'Discord': 'Link de Convite', 'Telegram': 'Usuário (sem @)', 'Steam': 'ID ou URL', 'Pinterest': 'Usuário'}
        self.social_input.setPlaceholderText(placeholders.get(name, 'Digite aqui...'))
        self.generate_qr()

    def upload_logo(self):
        (file_path, _) = QFileDialog.getOpenFileName(self, 'Selecionar Logo', '', 'Images (*.png *.jpg *.jpeg *.svg)')
        if file_path:
            self.logo_path = file_path
            self.update_logo_preview(file_path)
            self.generate_qr()

    def update_logo_preview(self, path):
        if not path:
            self.logo_preview_sidebar.clear()
            self.logo_preview_sidebar.setText('Arraste ou Selecione')
            self.logo_preview_sidebar.setStyleSheet(f'border: 2px dashed {DraculaTheme.COMMENT}; border-radius: 8px; color: {DraculaTheme.COMMENT}; font-size: 14px; padding: 10px; font-weight: bold;')
            return
        if os.path.exists(path):
            pixmap = QPixmap(path).scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_preview_sidebar.setPixmap(pixmap)
            self.logo_preview_sidebar.setStyleSheet('border: none;')

    def pick_fg_color(self):
        color = QColorDialog.getColor(QColor(self.fg_color), self, 'Cor da Frente')
        if color.isValid():
            self.fg_color = color.name()
            self.fg_color_btn.setStyleSheet(f'background-color: {self.fg_color}; border: 1px solid #fff; border-radius: 8px;')
            self.generate_qr()

    def pick_bg_color(self):
        color = QColorDialog.getColor(QColor(self.bg_color), self, 'Cor do Fundo')
        if color.isValid():
            self.bg_color = color.name()
            self.bg_color_btn.setStyleSheet(f'background-color: {self.bg_color}; border: 1px solid #fff; border-radius: 8px;')
            self.generate_qr()

    def get_current_data(self):
        index = self.stacked_widget.currentIndex()
        if index == 0:
            text = self.link_input.text().strip()
            return text if text else None
        elif index == 1:
            ssid = self.wifi_ssid.text().strip()
            if not ssid:
                return None
            pwd = self.wifi_password.text()
            enc = self.wifi_encryption.currentText()
            hidden = self.wifi_hidden.isChecked()
            enc_map = {'WPA/WPA2': 'WPA', 'WEP': 'WEP', 'Sem Senha': 'nopass'}
            return WifiPayload(ssid, pwd, enc_map.get(enc, 'WPA'), hidden).to_string()
        elif index == 2:
            key = self.pix_key.text().strip()
            name = self.pix_name.text().strip()
            city = self.pix_city.text().strip()
            if not key or not name or (not city):
                return None
            return PixPayload(key=key, name=name, city=city, amount=self.pix_amount.text(), txid=self.pix_txid.text()).to_string()
        elif index == 3:
            platform = self.social_selector.selected_platform
            value = self.social_input.text().strip()
            if not value:
                return None
            platform_key = platform.lower().replace('-', '')
            if 'email' in platform_key:
                return SocialPayload.email(value)
            elif 'whatsapp' in platform_key:
                return SocialPayload.whatsapp(value)
            elif 'instagram' in platform_key:
                return SocialPayload.instagram(value)
            elif 'twitter' in platform_key or 'x' == platform_key:
                return SocialPayload.twitter(value)
            elif 'facebook' in platform_key:
                return SocialPayload.facebook(value)
            elif 'linkedin' in platform_key:
                return SocialPayload.linkedin(value)
            elif 'github' in platform_key:
                return SocialPayload.github(value)
            elif 'youtube' in platform_key:
                return SocialPayload.youtube(value)
            elif 'discord' in platform_key:
                return SocialPayload.discord(value)
            elif 'telegram' in platform_key:
                return SocialPayload.telegram(value)
            elif 'steam' in platform_key:
                return SocialPayload.steam(value)
            elif 'pinterest' in platform_key:
                return SocialPayload.pinterest(value)
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
                current_page = self.stacked_widget.currentWidget()
                self.toast.show_message('Preencha os campos obrigatórios!', target_widget=self.content_container)
            return
        ec = 'H'
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()
        logo_img = self.load_logo_to_pil(self.logo_path)
        self.worker = QRWorker(request_id=req_id, data=data, ec=ec, size=15, rounded=True, logo_img=logo_img, logo_size=15, logo_opacity=self.logo_opacity_slider.value(), logo_pos=self.logo_pos_selector.current_pos, fill_color=self.fg_color, back_color=self.bg_color)
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.error.connect(self.on_generation_error)
        self.worker.start()

    def load_logo_to_pil(self, path):
        if not path or not os.path.exists(path):
            return None
        try:
            if path.lower().endswith('.svg'):
                icon = QIcon(path)
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
                return Image.frombytes('RGBA', (width, height), arr)
            else:
                return Image.open(path).convert('RGBA')
        except Exception as e:
            logger.error(f'Error loading logo in UI: {e}', exc_info=True)
            return None

    def handle_preview_action(self, action):
        if action == 'open':
            self.open_qr_link()
        elif action == 'save':
            self.save_qr()
        elif action == 'clear':
            self.clear_qr()
        elif action == 'print':
            self.print_qr()

    def save_qr(self):
        if not self.current_qr_image:
            self.toast.show_message('Nenhum QR Code para salvar!')
            return
        from PyQt6.QtWidgets import QFileDialog, QMessageBox, QDialog, QHBoxLayout
        filters = 'Todos os Arquivos (*);;Imagens PNG (*.png);;Imagens JPG (*.jpg);;Imagens JPEG (*.jpeg);;Documento PDF (*.pdf);;Vetor SVG (*.svg)'
        (file_path, selected_filter) = QFileDialog.getSaveFileName(self, 'Salvar QR Code', 'qrcode', filters)
        if file_path:
            if selected_filter:
                ext_map = {'Imagens PNG (*.png)': '.png', 'Imagens JPG (*.jpg)': '.jpg', 'Imagens JPEG (*.jpeg)': '.jpeg', 'Documento PDF (*.pdf)': '.pdf', 'Vetor SVG (*.svg)': '.svg', 'Todos os Arquivos (*)': '.png'}
                expected_ext = ext_map.get(selected_filter)
                if expected_ext:
                    (root, current_ext) = os.path.splitext(file_path)
                    if selected_filter == 'Todos os Arquivos (*)':
                        if not current_ext:
                            file_path += '.png'
                    elif not current_ext or current_ext.lower() != expected_ext:
                        file_path = root + expected_ext
            try:
                if file_path.lower().endswith('.pdf'):
                    self.current_qr_image.save(file_path, 'PDF', resolution=100.0)
                else:
                    self.current_qr_image.save(file_path)
                self.show_save_success_popup(file_path)
            except Exception as e:
                logger.error(f'Error saving image: {e}', exc_info=True)
                self.toast.show_message(f'Erro ao salvar: {e}')

    def show_save_success_popup(self, file_path):
        dialog = QDialog(self)
        dialog.setWindowTitle('')
        dialog.setFixedSize(400, 150)
        dialog.setStyleSheet(f'background-color: {DraculaTheme.BACKGROUND}; color: {DraculaTheme.FOREGROUND};')
        layout = QVBoxLayout(dialog)
        lbl = QLabel('Arquivo salvo com sucesso')
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet('font-size: 16px; font-weight: bold; margin-bottom: 10px;')
        layout.addWidget(lbl)
        btn_layout = QHBoxLayout()
        btn_open = QPushButton('Abrir QRcode')
        btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open.clicked.connect(lambda : self._open_file(file_path))
        btn_folder = QPushButton('Abrir Pasta')
        btn_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_folder.clicked.connect(lambda : self._open_folder(file_path))
        btn_new = QPushButton('Gerar Novo')
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.clicked.connect(dialog.accept)
        for btn in [btn_open, btn_folder, btn_new]:
            btn.setStyleSheet(f'\n                QPushButton {{\n                    background-color: {DraculaTheme.CURRENT_LINE};\n                    border: 1px solid {DraculaTheme.PURPLE};\n                    border-radius: 5px;\n                    padding: 8px;\n                    color: {DraculaTheme.FOREGROUND};\n                }}\n                QPushButton:hover {{\n                    background-color: {DraculaTheme.COMMENT};\n                }}\n            ')
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
            self.toast.show_message('Nenhum QR Code para imprimir!')
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
        self.clear_logo()

    def clear_logo(self):
        self.logo_path = None
        self.update_logo_preview(None)
        self.auto_generate()

    def on_generation_finished(self, img, req_id):
        if req_id != self.request_id_counter:
            return
        self.current_qr_image = img
        qpixmap = pil_to_qpixmap(img)
        self.qr_label.setPixmap(qpixmap)

    def on_generation_error(self, error_msg):
        self.toast.show_message(f'Erro: {error_msg}')

    def copy_qr(self):
        if self.current_qr_image:
            copy_to_clipboard(self.current_qr_image)
            self.toast.show_message('Copiado para a área de transferência!')
        else:
            self.toast.show_message('Nenhum QR Code gerado!')
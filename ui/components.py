import os
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QDialog, QGridLayout, QPushButton, QMenu, QRadioButton, QButtonGroup, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, QUrl
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QDesktopServices, QPainterPath
from ui.styles import DraculaTheme
import random

class SocialPlatformSelector(QWidget):
    platformSelected = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setVerticalSpacing(10)
        layout.setHorizontalSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        self.buttons = {}
        self.selected_platform = None
        platforms = [('WhatsApp', 'whatsapp.svg'), ('Instagram', 'instagram.svg'), ('LinkedIn', 'linkedin.svg'), ('GitHub', 'github.svg'), ('YouTube', 'youtube.svg'), ('Twitter', 'twitter.svg'), ('Facebook', 'facebook.svg'), ('Discord', 'discord.svg'), ('Telegram', 'telegram.svg'), ('Steam', 'steam.svg'), ('Pinterest', 'pinterest.svg'), ('Email', 'email.svg')]
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logos')
        (row, col) = (0, 0)
        for (name, icon_file) in platforms:
            btn = QPushButton()
            btn.setFixedSize(90, 90)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(name)
            icon_path = os.path.join(assets_dir, icon_file)
            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(58, 58))
            btn.setProperty('platform_name', name)
            btn.setProperty('icon_path', icon_path)
            btn.clicked.connect(lambda checked, n=name: self.select_platform(n))
            btn.setStyleSheet(f'\n                QPushButton {{\n                    background-color: {DraculaTheme.CURRENT_LINE};\n                    border: 1px solid {DraculaTheme.COMMENT};\n                    border-radius: 8px;\n                }}\n                QPushButton:checked {{\n                    background-color: {DraculaTheme.PURPLE};\n                    border: 1px solid {DraculaTheme.PURPLE};\n                }}\n                QPushButton:hover {{\n                    background-color: {DraculaTheme.COMMENT};\n                }}\n            ')
            layout.addWidget(btn, row, col)
            self.buttons[name] = btn
            col += 1
            if col > 2:
                col = 0
                row += 1

    def select_platform(self, name):
        if self.selected_platform == name:
            return
        self.selected_platform = name
        for (n, btn) in self.buttons.items():
            btn.setChecked(n == name)
        icon_path = self.buttons[name].property('icon_path')
        self.platformSelected.emit(name, icon_path)

class CompactProtectionSelector(QWidget):
    valueChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        self.btn_group = QButtonGroup(self)
        self.btn_group.idClicked.connect(self._on_group_clicked)
        options = [('L', 'Baixa'), ('M', 'Média'), ('Q', 'Alta'), ('H', 'Máx')]
        for (i, (val, tooltip)) in enumerate(options):
            btn = QPushButton(val)
            btn.setCheckable(True)
            btn.setFixedSize(40, 30)
            btn.setToolTip(tooltip)
            btn.setProperty('ec_value', val)
            btn.setStyleSheet(f'\n                QPushButton {{\n                    background-color: {DraculaTheme.CURRENT_LINE};\n                    border: 1px solid {DraculaTheme.COMMENT};\n                    border-radius: 6px;\n                    font-weight: bold;\n                }}\n                QPushButton:checked {{\n                    background-color: {DraculaTheme.PURPLE};\n                    color: {DraculaTheme.BACKGROUND};\n                    border: 1px solid {DraculaTheme.PURPLE};\n                }}\n                QPushButton:hover {{\n                    background-color: {DraculaTheme.COMMENT};\n                }}\n            ')
            self.btn_group.addButton(btn, i)
            layout.addWidget(btn)
        self.btn_group.button(3).setChecked(True)

    def _on_group_clicked(self, btn_id):
        val = self.btn_group.button(btn_id).property('ec_value')
        self.valueChanged.emit(val)

    def get_value(self):
        return self.btn_group.checkedButton().property('ec_value')

class LogoPositionSelector(QWidget):
    positionChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        self.buttons = {}
        self.current_pos = 'center'
        positions = [('top-left', 0, 0), ('top', 0, 1), ('top-right', 0, 2), ('left', 1, 0), ('center', 1, 1), ('right', 1, 2), ('bottom-left', 2, 0), ('bottom', 2, 1), ('bottom-right', 2, 2)]
        for (name, r, c) in positions:
            btn = QPushButton()
            btn.setFixedSize(25, 25)
            btn.setCheckable(True)
            btn.setProperty('pos_name', name)
            btn.clicked.connect(lambda checked, n=name: self.select_position(n))
            btn.setStyleSheet(f'\n                QPushButton {{\n                    background-color: {DraculaTheme.CURRENT_LINE};\n                    border: 1px solid {DraculaTheme.COMMENT};\n                    border-radius: 4px;\n                }}\n                QPushButton:checked {{\n                    background-color: {DraculaTheme.PURPLE};\n                    border: 1px solid {DraculaTheme.PURPLE};\n                }}\n                QPushButton:hover {{\n                    background-color: {DraculaTheme.COMMENT};\n                }}\n            ')
            layout.addWidget(btn, r, c)
            self.buttons[name] = btn
        self.select_position('center')

    def select_position(self, name):
        self.current_pos = name
        for (n, btn) in self.buttons.items():
            btn.setChecked(n == name)
        self.positionChanged.emit(name)

class Toast(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(f'\n            background-color: {DraculaTheme.CURRENT_LINE}; \n            color: {DraculaTheme.CYAN}; \n            border-radius: 10px; \n            border: 1px solid {DraculaTheme.PURPLE};\n            padding: 10px;\n            font-weight: bold;\n        ')
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet('background: transparent; border: none;')
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.hide()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.hide_toast)

    def show_message(self, message, target_widget=None):
        self.label.setText(message)
        self.adjustSize()
        if self.parent():
            if target_widget:
                global_pos = target_widget.mapToGlobal(target_widget.rect().bottomLeft())
                local_pos = self.parent().mapFromGlobal(global_pos)
                x = local_pos.x() + (target_widget.width() - self.width()) // 2
                y = local_pos.y() + 10
                self.move(x, y)
            else:
                parent_rect = self.parent().rect()
                self.move(parent_rect.width() - self.width() - 20, parent_rect.height() - self.height() - 100)
        self.show()
        self.raise_()
        self.timer.start(3000)

    def hide_toast(self):
        self.hide()

class PreviewLabel(QLabel):
    leftClicked = pyqtSignal()
    actionRequested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMouseTracking(True)
        self.setStyleSheet(f'background-color: {DraculaTheme.BACKGROUND}; border: 1px solid {DraculaTheme.CURRENT_LINE}; border-radius: 12px;')
        self.original_pixmap = None
        self.is_zoomed = False

    def setPixmap(self, pixmap):
        self.original_pixmap = pixmap
        self.update_display()

    def enterEvent(self, event):
        if self.original_pixmap:
            self.is_zoomed = True
            self.update_display()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_zoomed = False
        self.update_display()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.leftClicked.emit()
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet(f'\n            QMenu {{\n                background-color: {DraculaTheme.CURRENT_LINE};\n                color: {DraculaTheme.FOREGROUND};\n                border: 1px solid {DraculaTheme.COMMENT};\n            }}\n            QMenu::item:selected {{\n                background-color: {DraculaTheme.PURPLE};\n            }}\n        ')
        action_open = menu.addAction('Abrir QRcode')
        action_save = menu.addAction('Salvar como')
        action_clear = menu.addAction('Limpar')
        action_print = menu.addAction('Imprimir')
        action = menu.exec(event.globalPos())
        if action == action_open:
            self.actionRequested.emit('open')
        elif action == action_save:
            self.actionRequested.emit('save')
        elif action == action_clear:
            self.actionRequested.emit('clear')
        elif action == action_print:
            self.actionRequested.emit('print')

    def update_display(self):
        if not self.original_pixmap:
            self.clear()
            return
        target_pixmap = self.original_pixmap
        if self.is_zoomed:
            target_pixmap = self.original_pixmap.scaled(int(self.original_pixmap.width() * 1.05), int(self.original_pixmap.height() * 1.05), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            super().setPixmap(target_pixmap)
        else:
            scaled_pixmap = self.original_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            rounded = QPixmap(scaled_pixmap.size())
            rounded.fill(Qt.GlobalColor.transparent)
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(0, 0, scaled_pixmap.width(), scaled_pixmap.height(), 12, 12)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, scaled_pixmap)
            painter.end()
            super().setPixmap(rounded)

class LogoLabel(QLabel):
    clicked = pyqtSignal()
    clearRequested = pyqtSignal()

    def __init__(self, text='', parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet(f'\n            QMenu {{\n                background-color: {DraculaTheme.CURRENT_LINE};\n                color: {DraculaTheme.FOREGROUND};\n                border: 1px solid {DraculaTheme.COMMENT};\n            }}\n            QMenu::item:selected {{\n                background-color: {DraculaTheme.PURPLE};\n            }}\n        ')
        action_clear = menu.addAction('Limpar')
        action = menu.exec(event.globalPos())
        if action == action_clear:
            self.clearRequested.emit()

class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, text='', parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
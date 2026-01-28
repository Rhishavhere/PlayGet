"""
PlayGet - Video Downloader Widget
A modern dark-themed multi-platform video downloader
"""

import sys
import os
import threading
import queue
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QFrame, QStackedWidget,
    QProgressBar, QScrollArea, QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor, QPalette
import yt_dlp

# --- Configuration ---
DOWNLOAD_FOLDER = "Downloads"
CHECK_INTERVAL = 500

# --- Stylesheet ---
STYLESHEET = """
* {
    margin: 0;
    padding: 0;
}

QMainWindow, QWidget#appContainer {
    background: #0d0d0f;
    border-radius: 16px;
}

QWidget {
    background: transparent;
    color: #ffffff;
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
}

/* ==================== TITLE BAR ==================== */
QWidget#titleBar {
    background: #16161a;
    border-top-left-radius: 16px;
    border-top-right-radius: 16px;
}

QLabel#appLogo {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff3b5c, stop:1 #ff6b81);
    border-radius: 7px;
    font-size: 11px;
}

QLabel#appTitle {
    font-weight: 700;
    font-size: 14px;
    letter-spacing: -0.3px;
}

QPushButton#minimizeBtn, QPushButton#closeBtn {
    background: rgba(255, 255, 255, 0.05);
    border: none;
    border-radius: 6px;
    color: rgba(255, 255, 255, 0.5);
    font-size: 11px;
}

QPushButton#minimizeBtn:hover, QPushButton#closeBtn:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
}

QPushButton#closeBtn:hover {
    background: #ff3b5c;
}

/* ==================== MAIN VIEW ==================== */
QLabel.sectionTitle {
    font-size: 10px;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.35);
    letter-spacing: 1.5px;
}

QPushButton.platformBtn {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 14px;
    color: #ffffff;
    font-size: 12px;
    font-weight: 500;
}

QPushButton.platformBtn:hover:!disabled {
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(255, 255, 255, 0.12);
}

QPushButton.platformBtn:disabled {
    color: rgba(255, 255, 255, 0.3);
}

QPushButton#youtubeBtn {
    border-color: rgba(255, 0, 51, 0.15);
}

QPushButton#youtubeBtn:hover {
    background: rgba(255, 0, 51, 0.08);
    border-color: rgba(255, 0, 51, 0.4);
}

/* ==================== YOUTUBE VIEW ==================== */
QPushButton#backBtn {
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.5);
    font-size: 13px;
    font-weight: 500;
    padding: 4px 0;
}

QPushButton#backBtn:hover {
    color: #ff3b5c;
}

QLabel#ytHeaderTitle {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.5px;
}

QLabel#ytHeaderIcon {
    color: #ff0033;
    font-size: 20px;
}

/* URL Input Card */
QFrame#urlCard {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 14px;
}

QLineEdit#urlInput {
    background: transparent;
    border: none;
    color: #ffffff;
    font-size: 13px;
    padding: 0;
    selection-background-color: rgba(255, 59, 92, 0.4);
}

QLineEdit#urlInput:focus {
    background: transparent;
}

QPushButton#pasteBtn {
    background: rgba(255, 59, 92, 0.1);
    border: none;
    border-radius: 8px;
    color: #ff3b5c;
    font-size: 14px;
}

QPushButton#pasteBtn:hover {
    background: rgba(255, 59, 92, 0.2);
}

/* Format Toggle */
QFrame#formatCard {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
}

QPushButton.formatBtn {
    background: transparent;
    border: none;
    border-radius: 8px;
    color: rgba(255, 255, 255, 0.5);
    font-size: 12px;
    font-weight: 600;
    padding: 10px 16px;
}

QPushButton.formatBtn:hover {
    color: rgba(255, 255, 255, 0.7);
}

QPushButton.formatBtn:checked {
    background: rgba(255, 59, 92, 0.15);
    color: #ff3b5c;
}

/* Quality Selector */
QComboBox#qualityCombo {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    color: #ffffff;
    font-size: 13px;
    font-weight: 500;
    padding: 12px 16px;
}

QComboBox#qualityCombo:hover {
    border-color: rgba(255, 255, 255, 0.12);
}

QComboBox#qualityCombo:focus {
    border-color: rgba(255, 59, 92, 0.5);
}

QComboBox#qualityCombo::drop-down {
    border: none;
    width: 28px;
}

QComboBox#qualityCombo::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid rgba(255, 255, 255, 0.4);
    margin-right: 12px;
}

QComboBox QAbstractItemView {
    background: #1a1a1f;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    color: #ffffff;
    selection-background-color: rgba(255, 59, 92, 0.2);
    padding: 6px;
    outline: none;
}

/* Download Button */
QPushButton#downloadBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff3b5c, stop:1 #ff6b81);
    border: none;
    border-radius: 12px;
    color: white;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.3px;
}

QPushButton#downloadBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff4d6d, stop:1 #ff7d93);
}

QPushButton#downloadBtn:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e63350, stop:1 #e65f75);
}

QPushButton#downloadBtn:disabled {
    background: rgba(255, 59, 92, 0.25);
    color: rgba(255, 255, 255, 0.4);
}

/* Progress Bar */
QProgressBar#progressBar {
    background: rgba(255, 255, 255, 0.05);
    border: none;
    border-radius: 3px;
    max-height: 6px;
}

QProgressBar#progressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff3b5c, stop:1 #ff6b81);
    border-radius: 3px;
}

/* Auto Mode Section */
QFrame#autoCard {
    background: linear-gradient(135deg, rgba(255, 59, 92, 0.05) 0%, rgba(255, 107, 129, 0.02) 100%);
    border: 1px solid rgba(255, 59, 92, 0.1);
    border-radius: 14px;
}

QLabel#autoTitle {
    font-size: 13px;
    font-weight: 700;
    color: #ffffff;
}

QLabel#autoIcon {
    color: #ff3b5c;
    font-size: 16px;
}

QLabel.autoDesc {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.4);
    line-height: 1.4;
}

QPushButton#autoToggleBtn {
    background: transparent;
    border: 1px solid rgba(255, 59, 92, 0.3);
    border-radius: 6px;
    color: #ff3b5c;
    font-size: 11px;
    font-weight: 700;
    padding: 6px 14px;
    letter-spacing: 0.5px;
}

QPushButton#autoToggleBtn:hover {
    background: rgba(255, 59, 92, 0.1);
}

QPushButton#autoToggleBtn:checked {
    background: #ff3b5c;
    border-color: #ff3b5c;
    color: white;
}

/* Status Bar */
QFrame#statusBar {
    background: rgba(255, 255, 255, 0.02);
    border-top: 1px solid rgba(255, 255, 255, 0.04);
    border-bottom-left-radius: 16px;
    border-bottom-right-radius: 16px;
}

QLabel#statusIcon {
    font-size: 12px;
}

QLabel#statusText {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.5);
}

QLabel#queueBadge {
    background: rgba(255, 59, 92, 0.15);
    border-radius: 10px;
    color: #ff3b5c;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 8px;
}

/* Coming Soon Badge */
QLabel.soonBadge {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 4px;
    color: rgba(255, 255, 255, 0.3);
    font-size: 8px;
    font-weight: 700;
    letter-spacing: 0.5px;
    padding: 2px 5px;
}

/* Scrollbar */
QScrollBar:vertical {
    background: transparent;
    width: 4px;
    margin: 4px 2px;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.2);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
    height: 0;
}
"""


class DownloadSignals(QObject):
    status_update = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    download_complete = pyqtSignal(str)
    download_error = pyqtSignal(str)
    queue_update = pyqtSignal(int)


class PlayGetApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.signals = DownloadSignals()
        self.url_queue = queue.Queue()
        self.auto_mode_active = False
        self.last_clipboard = ""
        self.download_type = "video"
        self.is_downloading = False
        self.drag_pos = None
        
        self.init_ui()
        self.connect_signals()
        self.start_worker()
        
        self.clipboard_timer = QTimer()
        self.clipboard_timer.timeout.connect(self.check_clipboard)
        
    def init_ui(self):
        self.setWindowTitle("PlayGet")
        self.setFixedSize(380, 620)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        container = QWidget()
        container.setObjectName("appContainer")
        self.setCentralWidget(container)
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.create_title_bar(main_layout)
        
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1)
        
        self.create_main_view()
        self.create_youtube_view()
        
        self.create_status_bar(main_layout)
        
        self.setStyleSheet(STYLESHEET)
        
    def create_title_bar(self, parent_layout):
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(52)
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(16, 0, 12, 0)
        
        logo = QLabel("▶")
        logo.setObjectName("appLogo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFixedSize(26, 26)
        
        title = QLabel("PlayGet")
        title.setObjectName("appTitle")
        
        minimize_btn = QPushButton("─")
        minimize_btn.setObjectName("minimizeBtn")
        minimize_btn.setFixedSize(30, 30)
        minimize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        minimize_btn.clicked.connect(self.showMinimized)
        
        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        
        layout.addWidget(logo)
        layout.addSpacing(10)
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(minimize_btn)
        layout.addSpacing(4)
        layout.addWidget(close_btn)
        
        title_bar.mousePressEvent = self.title_mouse_press
        title_bar.mouseMoveEvent = self.title_mouse_move
        
        parent_layout.addWidget(title_bar)
        
    def create_status_bar(self, parent_layout):
        status_bar = QFrame()
        status_bar.setObjectName("statusBar")
        status_bar.setFixedHeight(42)
        
        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(16, 0, 16, 0)
        
        self.status_icon = QLabel("●")
        self.status_icon.setObjectName("statusIcon")
        self.status_icon.setStyleSheet("color: rgba(255, 255, 255, 0.3);")
        
        self.status_text = QLabel("Ready")
        self.status_text.setObjectName("statusText")
        
        self.queue_badge = QLabel("0")
        self.queue_badge.setObjectName("queueBadge")
        self.queue_badge.setVisible(False)
        
        layout.addWidget(self.status_icon)
        layout.addSpacing(8)
        layout.addWidget(self.status_text)
        layout.addStretch()
        layout.addWidget(self.queue_badge)
        
        parent_layout.addWidget(status_bar)
        
    def title_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            
    def title_mouse_move(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            
    def create_main_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(20, 24, 20, 20)
        layout.setSpacing(20)
        
        title = QLabel("SELECT PLATFORM")
        title.setProperty("class", "sectionTitle")
        layout.addWidget(title)
        
        # Platform grid - row 1
        grid1 = QWidget()
        grid1_layout = QHBoxLayout(grid1)
        grid1_layout.setContentsMargins(0, 0, 0, 0)
        grid1_layout.setSpacing(12)
        
        yt_btn = self.create_platform_button("▶", "YouTube", "youtubeBtn", "#ff0033", True)
        yt_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        grid1_layout.addWidget(yt_btn)
        
        fb_btn = self.create_platform_button("f", "Facebook", "facebookBtn", "#1877f2", False)
        grid1_layout.addWidget(fb_btn)
        
        layout.addWidget(grid1)
        
        # Platform grid - row 2
        grid2 = QWidget()
        grid2_layout = QHBoxLayout(grid2)
        grid2_layout.setContentsMargins(0, 0, 0, 0)
        grid2_layout.setSpacing(12)
        
        ig_btn = self.create_platform_button("◎", "Instagram", "instagramBtn", "#e4405f", False)
        grid2_layout.addWidget(ig_btn)
        
        tt_btn = self.create_platform_button("♪", "TikTok", "tiktokBtn", "#fe2c55", False)
        grid2_layout.addWidget(tt_btn)
        
        layout.addWidget(grid2)
        
        layout.addStretch()
        self.stack.addWidget(view)
        
    def create_platform_button(self, icon, name, obj_name, color, enabled=True):
        btn = QPushButton()
        btn.setObjectName(obj_name)
        btn.setProperty("class", "platformBtn")
        btn.setEnabled(enabled)
        btn.setCursor(Qt.CursorShape.PointingHandCursor if enabled else Qt.CursorShape.ForbiddenCursor)
        btn.setFixedHeight(100)
        
        layout = QVBoxLayout(btn)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)
        
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"font-size: 28px; color: {color if enabled else 'rgba(255,255,255,0.3)'};")
        
        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("font-size: 12px; font-weight: 600;")
        
        layout.addWidget(icon_label)
        layout.addWidget(name_label)
        
        if not enabled:
            badge = QLabel("SOON")
            badge.setProperty("class", "soonBadge")
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setFixedWidth(40)
            layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignCenter)
        
        return btn
        
    def create_youtube_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 16)
        header_layout.setSpacing(0)
        
        back_btn = QPushButton("←  Back")
        back_btn.setObjectName("backBtn")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        
        yt_icon = QLabel("▶")
        yt_icon.setObjectName("ytHeaderIcon")
        
        yt_title = QLabel("YouTube")
        yt_title.setObjectName("ytHeaderTitle")
        
        header_layout.addWidget(yt_icon)
        header_layout.addSpacing(8)
        header_layout.addWidget(yt_title)
        
        layout.addWidget(header)
        
        # URL Input Card
        url_card = QFrame()
        url_card.setObjectName("urlCard")
        url_layout = QHBoxLayout(url_card)
        url_layout.setContentsMargins(16, 12, 12, 12)
        url_layout.setSpacing(12)
        
        self.url_input = QLineEdit()
        self.url_input.setObjectName("urlInput")
        self.url_input.setPlaceholderText("Paste video URL here...")
        
        paste_btn = QPushButton("📋")
        paste_btn.setObjectName("pasteBtn")
        paste_btn.setFixedSize(36, 36)
        paste_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        paste_btn.clicked.connect(self.paste_url)
        
        url_layout.addWidget(self.url_input, 1)
        url_layout.addWidget(paste_btn)
        
        layout.addWidget(url_card)
        layout.addSpacing(16)
        
        # Format Selection
        format_label = QLabel("FORMAT")
        format_label.setProperty("class", "sectionTitle")
        layout.addWidget(format_label)
        layout.addSpacing(8)
        
        format_card = QFrame()
        format_card.setObjectName("formatCard")
        format_layout = QHBoxLayout(format_card)
        format_layout.setContentsMargins(6, 6, 6, 6)
        format_layout.setSpacing(4)
        
        self.video_btn = QPushButton("🎬  Video")
        self.video_btn.setProperty("class", "formatBtn")
        self.video_btn.setCheckable(True)
        self.video_btn.setChecked(True)
        self.video_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.video_btn.clicked.connect(lambda: self.set_type("video"))
        
        self.audio_btn = QPushButton("🎵  Audio")
        self.audio_btn.setProperty("class", "formatBtn")
        self.audio_btn.setCheckable(True)
        self.audio_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.audio_btn.clicked.connect(lambda: self.set_type("audio"))
        
        format_layout.addWidget(self.video_btn, 1)
        format_layout.addWidget(self.audio_btn, 1)
        
        layout.addWidget(format_card)
        layout.addSpacing(16)
        
        # Quality Selection
        quality_label = QLabel("QUALITY")
        quality_label.setProperty("class", "sectionTitle")
        layout.addWidget(quality_label)
        layout.addSpacing(8)
        
        self.quality_combo = QComboBox()
        self.quality_combo.setObjectName("qualityCombo")
        self.quality_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_quality_options()
        layout.addWidget(self.quality_combo)
        layout.addSpacing(20)
        
        # Download Button
        self.download_btn = QPushButton("Download")
        self.download_btn.setObjectName("downloadBtn")
        self.download_btn.setFixedHeight(50)
        self.download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)
        layout.addSpacing(8)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        layout.addWidget(self.progress_bar)
        layout.addSpacing(20)
        
        # Auto Mode Card
        auto_card = QFrame()
        auto_card.setObjectName("autoCard")
        auto_layout = QVBoxLayout(auto_card)
        auto_layout.setContentsMargins(16, 14, 16, 14)
        auto_layout.setSpacing(6)
        
        auto_header = QWidget()
        auto_header_layout = QHBoxLayout(auto_header)
        auto_header_layout.setContentsMargins(0, 0, 0, 0)
        auto_header_layout.setSpacing(8)
        
        auto_icon = QLabel("⚡")
        auto_icon.setObjectName("autoIcon")
        
        auto_title = QLabel("Auto Mode")
        auto_title.setObjectName("autoTitle")
        
        self.auto_btn = QPushButton("START")
        self.auto_btn.setObjectName("autoToggleBtn")
        self.auto_btn.setCheckable(True)
        self.auto_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.auto_btn.clicked.connect(self.toggle_auto_mode)
        
        auto_header_layout.addWidget(auto_icon)
        auto_header_layout.addWidget(auto_title)
        auto_header_layout.addStretch()
        auto_header_layout.addWidget(self.auto_btn)
        
        auto_desc = QLabel("Automatically detect and queue URLs from clipboard")
        auto_desc.setProperty("class", "autoDesc")
        auto_desc.setWordWrap(True)
        
        auto_layout.addWidget(auto_header)
        auto_layout.addWidget(auto_desc)
        
        layout.addWidget(auto_card)
        layout.addStretch()
        
        self.stack.addWidget(view)
        
    def connect_signals(self):
        self.signals.status_update.connect(self.update_status)
        self.signals.progress_update.connect(self.update_progress)
        self.signals.download_complete.connect(self.on_download_complete)
        self.signals.download_error.connect(self.on_download_error)
        self.signals.queue_update.connect(self.update_queue_display)
        
    def set_type(self, type_name):
        self.download_type = type_name
        self.video_btn.setChecked(type_name == "video")
        self.audio_btn.setChecked(type_name == "audio")
        self.update_quality_options()
        
    def update_quality_options(self):
        self.quality_combo.clear()
        if self.download_type == "video":
            self.quality_combo.addItems(["Best Quality", "1080p", "720p", "480p", "360p"])
        else:
            self.quality_combo.addItems(["320 kbps (Best)", "256 kbps", "192 kbps", "128 kbps"])
            
    def paste_url(self):
        clipboard = QApplication.clipboard()
        self.url_input.setText(clipboard.text())
        
    def toggle_auto_mode(self):
        self.auto_mode_active = self.auto_btn.isChecked()
        if self.auto_mode_active:
            self.auto_btn.setText("STOP")
            self.clipboard_timer.start(CHECK_INTERVAL)
            self.update_status_display("Watching clipboard...", "#ff3b5c")
            self.last_clipboard = QApplication.clipboard().text()
        else:
            self.auto_btn.setText("START")
            self.clipboard_timer.stop()
            self.update_status_display("Ready", "rgba(255, 255, 255, 0.3)")
            
    def check_clipboard(self):
        clipboard = QApplication.clipboard()
        current = clipboard.text()
        
        if current != self.last_clipboard:
            self.last_clipboard = current
            if self.is_youtube_url(current):
                self.add_to_queue(current)
                self.update_status_display("Added to queue", "#4ade80")
                
    def is_youtube_url(self, text):
        return text and ("youtube.com/watch" in text or "youtu.be/" in text)
        
    def get_quality_value(self):
        text = self.quality_combo.currentText()
        quality_map = {
            "Best Quality": "best",
            "1080p": "1080", "720p": "720", "480p": "480", "360p": "360",
            "320 kbps (Best)": "320",
            "256 kbps": "256",
            "192 kbps": "192",
            "128 kbps": "128"
        }
        return quality_map.get(text, "best")
        
    def add_to_queue(self, url):
        self.url_queue.put((url, self.download_type, self.get_quality_value()))
        self.signals.queue_update.emit(self.url_queue.qsize())
        
    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.update_status_display("Enter a URL", "#fbbf24")
            return
        if not self.is_youtube_url(url):
            self.update_status_display("Invalid URL", "#ef4444")
            return
            
        self.add_to_queue(url)
        self.url_input.clear()
        
    def start_worker(self):
        worker = threading.Thread(target=self.download_worker, daemon=True)
        worker.start()
        
    def download_worker(self):
        while True:
            url, dtype, quality = self.url_queue.get()
            self.is_downloading = True
            self.signals.status_update.emit("Downloading...")
            self.signals.queue_update.emit(self.url_queue.qsize())
            
            if not os.path.exists(DOWNLOAD_FOLDER):
                os.makedirs(DOWNLOAD_FOLDER)
                
            try:
                if dtype == "audio":
                    q = quality if quality != "best" else "320"
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': q,
                        }],
                        'quiet': True,
                        'no_warnings': True,
                        'progress_hooks': [self.progress_hook],
                    }
                else:
                    fmt = f'bestvideo[height<={quality}]+bestaudio/best' if quality != "best" else 'best'
                    ydl_opts = {
                        'format': fmt,
                        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
                        'merge_output_format': 'mp4',
                        'quiet': True,
                        'no_warnings': True,
                        'progress_hooks': [self.progress_hook],
                    }
                    
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    self.signals.download_complete.emit(url)
                    
            except Exception as e:
                self.signals.download_error.emit(str(e))
            finally:
                self.url_queue.task_done()
                self.is_downloading = False
                self.signals.queue_update.emit(self.url_queue.qsize())
                
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').strip().replace('%', '')
                self.signals.progress_update.emit(int(float(p)))
            except:
                pass
        elif d['status'] == 'finished':
            self.signals.progress_update.emit(100)
            
    def update_status_display(self, text, color):
        self.status_text.setText(text)
        self.status_icon.setStyleSheet(f"color: {color};")
            
    def update_status(self, text):
        self.update_status_display(text, "#ff3b5c")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.download_btn.setEnabled(False)
        
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        
    def on_download_complete(self, url):
        self.update_status_display("Complete!", "#4ade80")
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)
        self.download_btn.setEnabled(True)
        QTimer.singleShot(3000, lambda: self.update_status_display("Ready", "rgba(255, 255, 255, 0.3)"))
        
    def on_download_error(self, error):
        self.update_status_display("Error", "#ef4444")
        self.progress_bar.setVisible(False)
        self.download_btn.setEnabled(True)
        
    def update_queue_display(self, count):
        if count > 0:
            self.queue_badge.setText(str(count))
            self.queue_badge.setVisible(True)
        else:
            self.queue_badge.setVisible(False)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(13, 13, 15))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(22, 22, 26))
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(30, 30, 36))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Highlight, QColor(255, 59, 92))
    app.setPalette(palette)
    
    window = PlayGetApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

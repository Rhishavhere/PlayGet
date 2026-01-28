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
    QProgressBar, QCheckBox, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon
import yt_dlp

# --- Configuration ---
DOWNLOAD_FOLDER = "Downloads"
CHECK_INTERVAL = 500  # ms

# --- Stylesheet ---
STYLESHEET = """
* {
    margin: 0;
    padding: 0;
}

QMainWindow, QWidget#appContainer {
    background: #0d0d0f;
}

QWidget {
    background: transparent;
    color: #ffffff;
    font-family: 'Segoe UI', 'Inter', sans-serif;
}

/* Title Bar */
QWidget#titleBar {
    background: #16161a;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

QLabel#appLogo {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff3b5c, stop:1 #ff6b81);
    border-radius: 6px;
    color: white;
    font-weight: bold;
    font-size: 12px;
}

QLabel#appTitle {
    font-weight: 700;
    font-size: 14px;
}

QPushButton#minimizeBtn, QPushButton#closeBtn {
    background: #1e1e24;
    border: none;
    border-radius: 6px;
    color: rgba(255, 255, 255, 0.7);
    font-size: 12px;
}

QPushButton#minimizeBtn:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
}

QPushButton#closeBtn:hover {
    background: #ff3b5c;
    color: white;
}

/* Section Title */
QLabel.sectionTitle {
    font-size: 11px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.4);
    text-transform: uppercase;
    letter-spacing: 1.5px;
}

/* Platform Buttons */
QPushButton.platformBtn {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    color: #ffffff;
    font-size: 13px;
    font-weight: 500;
    padding: 16px;
    text-align: center;
}

QPushButton.platformBtn:hover:!disabled {
    border-color: rgba(255, 255, 255, 0.2);
    background: rgba(255, 255, 255, 0.06);
}

QPushButton.platformBtn:disabled {
    opacity: 0.4;
    color: rgba(255, 255, 255, 0.4);
}

QPushButton#youtubeBtn:hover {
    background: rgba(255, 0, 51, 0.1);
    border-color: #ff0033;
}

/* Back Button */
QPushButton#backBtn {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: rgba(255, 255, 255, 0.7);
    font-size: 12px;
    padding: 8px 16px;
}

QPushButton#backBtn:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
}

/* URL Input */
QLineEdit#urlInput {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    color: #ffffff;
    font-size: 13px;
    padding: 12px 14px;
    selection-background-color: #ff3b5c;
}

QLineEdit#urlInput:focus {
    border-color: #ff3b5c;
    background: rgba(255, 59, 92, 0.05);
}

/* Paste Button */
QPushButton#pasteBtn {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    color: rgba(255, 255, 255, 0.7);
    font-size: 16px;
}

QPushButton#pasteBtn:hover {
    background: rgba(255, 255, 255, 0.08);
    color: white;
}

/* Type Toggle Buttons */
QPushButton.typeBtn {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    color: rgba(255, 255, 255, 0.6);
    font-size: 12px;
    font-weight: 500;
    padding: 10px 16px;
}

QPushButton.typeBtn:hover {
    background: rgba(255, 255, 255, 0.06);
    color: rgba(255, 255, 255, 0.8);
}

QPushButton.typeBtn:checked {
    background: rgba(255, 59, 92, 0.15);
    border-color: #ff3b5c;
    color: #ffffff;
}

/* Quality Dropdown */
QComboBox {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    color: #ffffff;
    font-size: 13px;
    padding: 10px 14px;
}

QComboBox:focus, QComboBox:on {
    border-color: #ff3b5c;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid rgba(255, 255, 255, 0.5);
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background: #1e1e24;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: #ffffff;
    selection-background-color: rgba(255, 59, 92, 0.3);
    padding: 4px;
    outline: none;
}

/* Download Button */
QPushButton#downloadBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff3b5c, stop:0.5 #ff6b81, stop:1 #ff3b5c);
    border: none;
    border-radius: 10px;
    color: white;
    font-size: 13px;
    font-weight: 600;
    padding: 14px;
}

QPushButton#downloadBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff4d6a, stop:0.5 #ff7d91, stop:1 #ff4d6a);
}

QPushButton#downloadBtn:disabled {
    background: rgba(255, 59, 92, 0.3);
    color: rgba(255, 255, 255, 0.5);
}

/* Auto Mode Card */
QFrame#autoModeCard {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
}

QLabel#autoModeTitle {
    font-size: 13px;
    font-weight: 600;
}

QLabel.autoModeDesc {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.4);
}

/* Start Auto Button */
QPushButton#startAutoBtn {
    background: rgba(255, 59, 92, 0.1);
    border: 1px solid rgba(255, 59, 92, 0.3);
    border-radius: 8px;
    color: #ff3b5c;
    font-size: 12px;
    font-weight: 600;
    padding: 10px 20px;
}

QPushButton#startAutoBtn:hover {
    background: rgba(255, 59, 92, 0.2);
}

QPushButton#startAutoBtn:checked {
    background: #ff3b5c;
    color: white;
}

/* Queue Card */
QFrame#queueCard {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
}

QLabel#queueIcon {
    font-size: 16px;
}

QLabel#queueText {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
}

/* Status Card */
QFrame#statusCard {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
}

QLabel#statusText {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
}

/* Progress Bar */
QProgressBar {
    background: rgba(255, 255, 255, 0.05);
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff3b5c, stop:1 #ff6b81);
    border-radius: 4px;
}

/* Coming Soon Badge */
QLabel.comingSoon {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 4px;
    color: rgba(255, 255, 255, 0.4);
    font-size: 9px;
    padding: 2px 6px;
}

/* Scrollbar */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
    min-height: 20px;
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
    """Signals for thread-safe GUI updates"""
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
        
        # Clipboard timer
        self.clipboard_timer = QTimer()
        self.clipboard_timer.timeout.connect(self.check_clipboard)
        
    def init_ui(self):
        self.setWindowTitle("PlayGet")
        self.setFixedSize(360, 580)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Main container
        container = QWidget()
        container.setObjectName("appContainer")
        self.setCentralWidget(container)
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Title bar
        self.create_title_bar(main_layout)
        
        # Stacked widget for views
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1)
        
        # Create views
        self.create_main_view()
        self.create_youtube_view()
        
        self.setStyleSheet(STYLESHEET)
        
    def create_title_bar(self, parent_layout):
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(48)
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(14, 0, 14, 0)
        
        # Logo
        logo = QLabel("▶")
        logo.setObjectName("appLogo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFixedSize(24, 24)
        
        # Title
        title = QLabel("PlayGet")
        title.setObjectName("appTitle")
        
        # Window controls
        minimize_btn = QPushButton("─")
        minimize_btn.setObjectName("minimizeBtn")
        minimize_btn.setFixedSize(28, 28)
        minimize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        minimize_btn.clicked.connect(self.showMinimized)
        
        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        
        layout.addWidget(logo)
        layout.addSpacing(8)
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(minimize_btn)
        layout.addSpacing(4)
        layout.addWidget(close_btn)
        
        # Dragging
        title_bar.mousePressEvent = self.title_mouse_press
        title_bar.mouseMoveEvent = self.title_mouse_move
        
        parent_layout.addWidget(title_bar)
        
    def title_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            
    def title_mouse_move(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            
    def create_main_view(self):
        """Main view with platform selection"""
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Section title
        title = QLabel("SELECT PLATFORM")
        title.setProperty("class", "sectionTitle")
        layout.addWidget(title)
        
        # Platform grid
        grid = QWidget()
        grid_layout = QHBoxLayout(grid)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(12)
        
        # YouTube button
        yt_btn = self.create_platform_button("🎬", "YouTube", "youtubeBtn", enabled=True)
        yt_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        grid_layout.addWidget(yt_btn)
        
        # Facebook button (disabled)
        fb_btn = self.create_platform_button("📘", "Facebook", "facebookBtn", enabled=False)
        grid_layout.addWidget(fb_btn)
        
        layout.addWidget(grid)
        
        # Second row
        grid2 = QWidget()
        grid2_layout = QHBoxLayout(grid2)
        grid2_layout.setContentsMargins(0, 0, 0, 0)
        grid2_layout.setSpacing(12)
        
        # Instagram button (disabled)
        ig_btn = self.create_platform_button("📸", "Instagram", "instagramBtn", enabled=False)
        grid2_layout.addWidget(ig_btn)
        
        # TikTok button (disabled)
        tt_btn = self.create_platform_button("🎵", "TikTok", "tiktokBtn", enabled=False)
        grid2_layout.addWidget(tt_btn)
        
        layout.addWidget(grid2)
        
        # Queue status
        layout.addStretch()
        self.main_queue_card = self.create_queue_card()
        layout.addWidget(self.main_queue_card)
        
        self.stack.addWidget(view)
        
    def create_platform_button(self, icon, name, object_name, enabled=True):
        btn = QPushButton()
        btn.setObjectName(object_name)
        btn.setProperty("class", "platformBtn")
        btn.setEnabled(enabled)
        btn.setCursor(Qt.CursorShape.PointingHandCursor if enabled else Qt.CursorShape.ForbiddenCursor)
        btn.setMinimumHeight(80)
        
        btn_layout = QVBoxLayout(btn)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.setSpacing(6)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 28px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("font-size: 12px;")
        
        btn_layout.addWidget(icon_label)
        btn_layout.addWidget(name_label)
        
        if not enabled:
            badge = QLabel("SOON")
            badge.setProperty("class", "comingSoon")
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_layout.addWidget(badge)
        
        return btn
        
    def create_youtube_view(self):
        """YouTube download view"""
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)
        
        # Header with back button
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        
        back_btn = QPushButton("← Back")
        back_btn.setObjectName("backBtn")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        
        header_title = QLabel("YouTube")
        header_title.setStyleSheet("font-size: 15px; font-weight: 600;")
        
        header_layout.addWidget(back_btn)
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        # URL Input section
        url_title = QLabel("PASTE URL")
        url_title.setProperty("class", "sectionTitle")
        layout.addWidget(url_title)
        
        url_row = QWidget()
        url_layout = QHBoxLayout(url_row)
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_layout.setSpacing(8)
        
        self.url_input = QLineEdit()
        self.url_input.setObjectName("urlInput")
        self.url_input.setPlaceholderText("https://youtube.com/watch?v=...")
        
        paste_btn = QPushButton("📋")
        paste_btn.setObjectName("pasteBtn")
        paste_btn.setFixedSize(44, 44)
        paste_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        paste_btn.clicked.connect(self.paste_url)
        
        url_layout.addWidget(self.url_input, 1)
        url_layout.addWidget(paste_btn)
        layout.addWidget(url_row)
        
        # Type selection
        type_title = QLabel("DOWNLOAD TYPE")
        type_title.setProperty("class", "sectionTitle")
        layout.addWidget(type_title)
        
        type_row = QWidget()
        type_layout = QHBoxLayout(type_row)
        type_layout.setContentsMargins(0, 0, 0, 0)
        type_layout.setSpacing(8)
        
        self.video_btn = QPushButton("🎬 Video")
        self.video_btn.setProperty("class", "typeBtn")
        self.video_btn.setCheckable(True)
        self.video_btn.setChecked(True)
        self.video_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.video_btn.clicked.connect(lambda: self.set_type("video"))
        
        self.audio_btn = QPushButton("🎵 Audio Only")
        self.audio_btn.setProperty("class", "typeBtn")
        self.audio_btn.setCheckable(True)
        self.audio_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.audio_btn.clicked.connect(lambda: self.set_type("audio"))
        
        type_layout.addWidget(self.video_btn)
        type_layout.addWidget(self.audio_btn)
        layout.addWidget(type_row)
        
        # Quality selection
        quality_title = QLabel("QUALITY")
        quality_title.setProperty("class", "sectionTitle")
        layout.addWidget(quality_title)
        
        self.quality_combo = QComboBox()
        self.quality_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_quality_options()
        layout.addWidget(self.quality_combo)
        
        # Download button
        self.download_btn = QPushButton("⬇ Download")
        self.download_btn.setObjectName("downloadBtn")
        self.download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        layout.addWidget(self.progress_bar)
        
        # Auto Mode Card
        auto_card = QFrame()
        auto_card.setObjectName("autoModeCard")
        auto_layout = QVBoxLayout(auto_card)
        auto_layout.setContentsMargins(14, 14, 14, 14)
        auto_layout.setSpacing(8)
        
        auto_header = QWidget()
        auto_header_layout = QHBoxLayout(auto_header)
        auto_header_layout.setContentsMargins(0, 0, 0, 0)
        
        auto_title = QLabel("⚡ Auto Mode")
        auto_title.setObjectName("autoModeTitle")
        
        self.auto_btn = QPushButton("Start")
        self.auto_btn.setObjectName("startAutoBtn")
        self.auto_btn.setCheckable(True)
        self.auto_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.auto_btn.clicked.connect(self.toggle_auto_mode)
        
        auto_header_layout.addWidget(auto_title)
        auto_header_layout.addStretch()
        auto_header_layout.addWidget(self.auto_btn)
        
        auto_desc = QLabel("Auto-detect clipboard links and add to queue")
        auto_desc.setProperty("class", "autoModeDesc")
        auto_desc.setWordWrap(True)
        
        auto_layout.addWidget(auto_header)
        auto_layout.addWidget(auto_desc)
        layout.addWidget(auto_card)
        
        # Spacer
        layout.addStretch()
        
        # Queue status
        self.queue_card = self.create_queue_card()
        layout.addWidget(self.queue_card)
        
        # Status card
        status_card = QFrame()
        status_card.setObjectName("statusCard")
        status_layout = QHBoxLayout(status_card)
        status_layout.setContentsMargins(12, 10, 12, 10)
        
        self.status_text = QLabel("Ready to download")
        self.status_text.setObjectName("statusText")
        
        status_layout.addWidget(self.status_text)
        layout.addWidget(status_card)
        
        self.stack.addWidget(view)
        
    def create_queue_card(self):
        card = QFrame()
        card.setObjectName("queueCard")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        
        icon = QLabel("📥")
        icon.setObjectName("queueIcon")
        
        text = QLabel("Queue: 0 items")
        text.setObjectName("queueText")
        
        layout.addWidget(icon)
        layout.addWidget(text)
        layout.addStretch()
        
        return card
        
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
            self.quality_combo.addItems(["Best Quality (320 kbps)", "High (256 kbps)", "Medium (192 kbps)", "Low (128 kbps)"])
            
    def paste_url(self):
        clipboard = QApplication.clipboard()
        self.url_input.setText(clipboard.text())
        
    def toggle_auto_mode(self):
        self.auto_mode_active = self.auto_btn.isChecked()
        if self.auto_mode_active:
            self.auto_btn.setText("Stop")
            self.clipboard_timer.start(CHECK_INTERVAL)
            self.status_text.setText("Auto mode: Watching clipboard...")
            self.last_clipboard = QApplication.clipboard().text()
        else:
            self.auto_btn.setText("Start")
            self.clipboard_timer.stop()
            self.status_text.setText("Auto mode stopped")
            
    def check_clipboard(self):
        clipboard = QApplication.clipboard()
        current = clipboard.text()
        
        if current != self.last_clipboard:
            self.last_clipboard = current
            if self.is_youtube_url(current):
                self.add_to_queue(current)
                self.status_text.setText(f"Added: {current[:35]}...")
                
    def is_youtube_url(self, text):
        return text and ("youtube.com/watch" in text or "youtu.be/" in text)
        
    def get_quality_value(self):
        text = self.quality_combo.currentText()
        quality_map = {
            "Best Quality": "best",
            "1080p": "1080", "720p": "720", "480p": "480", "360p": "360",
            "Best Quality (320 kbps)": "320",
            "High (256 kbps)": "256",
            "Medium (192 kbps)": "192",
            "Low (128 kbps)": "128"
        }
        return quality_map.get(text, "best")
        
    def add_to_queue(self, url):
        self.url_queue.put((url, self.download_type, self.get_quality_value()))
        self.signals.queue_update.emit(self.url_queue.qsize())
        
    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.status_text.setText("Please enter a URL")
            return
        if not self.is_youtube_url(url):
            self.status_text.setText("Invalid YouTube URL")
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
            self.signals.status_update.emit(f"Downloading...")
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
            
    def update_status(self, text):
        self.status_text.setText(text)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.download_btn.setEnabled(False)
        
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        
    def on_download_complete(self, url):
        self.status_text.setText("✓ Download complete!")
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)
        self.download_btn.setEnabled(True)
        QTimer.singleShot(3000, lambda: self.status_text.setText("Ready to download"))
        
    def on_download_error(self, error):
        self.status_text.setText(f"✗ Error: {error[:40]}")
        self.progress_bar.setVisible(False)
        self.download_btn.setEnabled(True)
        
    def update_queue_display(self, count):
        text = f"Queue: {count} item{'s' if count != 1 else ''}"
        
        # Update both queue cards
        for card in [self.queue_card, self.main_queue_card]:
            label = card.findChild(QLabel, "queueText")
            if label:
                label.setText(text)


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

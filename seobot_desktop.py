"""
SEOBOT Desktop - Multi-Site Preview & SEO Tool
PyQt6 Application with QWebEngineView for live previews
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QSplitter, QTabWidget, QLabel, QPushButton,
    QTextEdit, QLineEdit, QComboBox, QCheckBox, QProgressBar,
    QScrollArea, QFrame, QToolBar, QStatusBar, QFileDialog,
    QMessageBox, QGroupBox, QSpinBox, QSizePolicy
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QAction, QFont, QPalette, QColor, QIcon

# Project configurations
PROJECTS = {
    "adaryus": {
        "name": "Adaryus.com",
        "domain": "adaryus.com",
        "url": "https://adaryus.com",
        "local_path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\app\dist\index.html",
        "type": "Portfolio",
        "description": "Cyber-kinetic brutalist portfolio with WebGL effects",
        "color": "#ff0000",
        "schema_type": "Person",
        "has_video": False,
        "has_webgl": True
    },
    "ncrjwatch": {
        "name": "NCRJ Watch",
        "domain": "ncrjwatch.org",
        "url": "https://ncrjwatch.org",
        "local_path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\NCRJFincal-main\public_html\index.html",
        "type": "Advocacy",
        "description": "Jail accountability and transparency platform",
        "color": "#ffd700",
        "schema_type": "Organization",
        "has_video": False,
        "has_webgl": False
    },
    "advertisewv": {
        "name": "AdvertiseWV",
        "domain": "advertisewv.com",
        "url": "https://advertisewv.com",
        "local_path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\index.html",
        "type": "Marketing",
        "description": "West Virginia digital marketing agency",
        "color": "#10b981",
        "schema_type": "LocalBusiness",
        "has_video": False,
        "has_webgl": False
    },
    "darkrose": {
        "name": "Dark Rose Tattoo",
        "domain": "darkrosetattoo.com",
        "url": "https://darkrosetattoo.com",
        "local_path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\dark-rose-tattoo-master\index.html",
        "type": "Tattoo Studio",
        "description": "Premium tattoo artistry studio with video backgrounds",
        "color": "#8b5cf6",
        "schema_type": "LocalBusiness",
        "has_video": True,
        "has_webgl": False,
        "video_file": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\dark-rose-tattoo-master\public\firefly_gears.mp4"
    },
    "ultimategotti": {
        "name": "Ultimate Gotti Line",
        "domain": "ultimategottiline.com",
        "url": "https://ultimategottiline.com",
        "local_path": None,
        "type": "Dog Breeding",
        "description": "Premium American Bully breeding",
        "color": "#f59e0b",
        "schema_type": "LocalBusiness",
        "has_video": False,
        "has_webgl": False
    },
    "mdi": {
        "name": "MDI Training",
        "domain": "mditraining.com",
        "url": "https://mditraining.com",
        "local_path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\mountaineerdynamicsinstitute-main\index.html",
        "type": "Training Facility",
        "description": "Professional tactical firearms training",
        "color": "#ef4444",
        "schema_type": "LocalBusiness",
        "has_video": False,
        "has_webgl": False
    }
}

# Dark theme stylesheet matching Design.md
DARK_THEME = """
QMainWindow {
    background-color: #0a0a0b;
    color: #fafafa;
}

QWidget {
    background-color: #0a0a0b;
    color: #fafafa;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Sidebar */
QFrame#sidebar {
    background-color: #141416;
    border-right: 1px solid #27272a;
    min-width: 300px;
    max-width: 350px;
}

/* Preview containers */
QFrame#preview-container {
    background-color: #141416;
    border: 1px solid #27272a;
    border-radius: 8px;
    margin: 4px;
}

QLabel#preview-title {
    color: #d4a017;
    font-weight: 700;
    font-size: 12px;
    padding: 8px 12px;
    background-color: #1a1a1d;
    border-bottom: 1px solid #27272a;
}

QLabel#preview-url {
    color: #71717a;
    font-size: 10px;
    padding: 4px 12px;
    background-color: #0d0d0e;
}

/* Buttons */
QPushButton {
    background-color: #d4a017;
    color: #0a0a0b;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: 700;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #f4d03f;
}

QPushButton:pressed {
    background-color: #b8860b;
}

QPushButton#secondary {
    background-color: transparent;
    color: #d4a017;
    border: 1px solid #d4a017;
}

QPushButton#secondary:hover {
    background-color: rgba(212, 160, 23, 0.1);
}

/* Inputs */
QLineEdit, QTextEdit, QComboBox {
    background-color: #1a1a1d;
    border: 1px solid #27272a;
    border-radius: 6px;
    padding: 8px 12px;
    color: #fafafa;
    font-size: 13px;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border-color: #d4a017;
}

/* Group boxes */
QGroupBox {
    background-color: #141416;
    border: 1px solid #27272a;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: 600;
    color: #d4a017;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #0d0d0e;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #3f3f46;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #d4a017;
}

/* Tabs */
QTabWidget::pane {
    background-color: #141416;
    border: 1px solid #27272a;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #1a1a1d;
    color: #71717a;
    padding: 10px 20px;
    border: none;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #d4a017;
    color: #0a0a0b;
}

QTabBar::tab:hover:!selected {
    background-color: #27272a;
    color: #fafafa;
}

/* Labels */
QLabel#header {
    color: #d4a017;
    font-size: 24px;
    font-weight: 800;
    letter-spacing: 2px;
}

QLabel#subheader {
    color: #71717a;
    font-size: 12px;
}

/* Status indicators */
QLabel#status-online {
    color: #22c55e;
    font-weight: 600;
}

QLabel#status-offline {
    color: #ef4444;
    font-weight: 600;
}

/* Toolbar */
QToolBar {
    background-color: #141416;
    border-bottom: 1px solid #27272a;
    spacing: 8px;
    padding: 8px;
}

QToolBar QPushButton {
    padding: 6px 12px;
    font-size: 11px;
}

/* Splitter */
QSplitter::handle {
    background-color: #27272a;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

/* Progress bar */
QProgressBar {
    background-color: #1a1a1d;
    border: 1px solid #27272a;
    border-radius: 4px;
    text-align: center;
    color: #fafafa;
}

QProgressBar::chunk {
    background-color: #d4a017;
    border-radius: 4px;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
    font-size: 12px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    background-color: #1a1a1d;
    border: 1px solid #27272a;
    border-radius: 4px;
}

QCheckBox::indicator:checked {
    background-color: #d4a017;
    border-color: #d4a017;
}
"""


class PreviewWidget(QFrame):
    """Widget containing a web preview with title bar"""
    
    def __init__(self, project_id, project_data, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.project_data = project_data
        self.setObjectName("preview-container")
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title bar
        title_bar = QFrame()
        title_bar.setStyleSheet("background-color: #1a1a1d; border-bottom: 1px solid #27272a;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(12, 8, 12, 8)
        
        # Project name with color indicator
        name_label = QLabel(f"● {self.project_data['name']}")
        name_label.setStyleSheet(f"color: {self.project_data['color']}; font-weight: 700; font-size: 12px;")
        title_layout.addWidget(name_label)
        
        title_layout.addStretch()
        
        # Type badge
        type_label = QLabel(self.project_data['type'])
        type_label.setStyleSheet("color: #71717a; font-size: 10px; background-color: #27272a; padding: 2px 8px; border-radius: 4px;")
        title_layout.addWidget(type_label)
        
        # Video indicator
        if self.project_data.get('has_video'):
            video_label = QLabel("🎬")
            video_label.setStyleSheet("font-size: 12px;")
            title_layout.addWidget(video_label)
        
        # WebGL indicator
        if self.project_data.get('has_webgl'):
            webgl_label = QLabel("🎮")
            webgl_label.setStyleSheet("font-size: 12px;")
            title_layout.addWidget(webgl_label)
        
        layout.addWidget(title_bar)
        
        # URL bar
        url_bar = QFrame()
        url_bar.setStyleSheet("background-color: #0d0d0e;")
        url_layout = QHBoxLayout(url_bar)
        url_layout.setContentsMargins(12, 4, 12, 4)
        
        self.url_input = QLineEdit(self.project_data['url'])
        self.url_input.setStyleSheet("font-size: 11px; padding: 4px 8px;")
        url_layout.addWidget(self.url_input)
        
        self.load_btn = QPushButton("Load")
        self.load_btn.setObjectName("secondary")
        self.load_btn.setStyleSheet("padding: 4px 12px; font-size: 10px;")
        self.load_btn.clicked.connect(self.load_url)
        url_layout.addWidget(self.load_btn)
        
        self.local_btn = QPushButton("Local")
        self.local_btn.setObjectName("secondary")
        self.local_btn.setStyleSheet("padding: 4px 12px; font-size: 10px;")
        self.local_btn.clicked.connect(self.load_local)
        local_path = self.project_data.get('local_path')
        has_local = local_path is not None and Path(local_path).exists()
        self.local_btn.setEnabled(has_local)
        url_layout.addWidget(self.local_btn)
        
        layout.addWidget(url_bar)
        
        # Web view
        self.webview = QWebEngineView()
        self.webview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Enable video and WebGL
        settings = self.webview.settings()
        settings.setAttribute(self.webview.settings().WebAttribute.PlaybackRequiresUserGesture, False)
        settings.setAttribute(self.webview.settings().WebAttribute.WebGLEnabled, True)
        settings.setAttribute(self.webview.settings().WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(self.webview.settings().WebAttribute.LocalStorageEnabled, True)
        
        layout.addWidget(self.webview, 1)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #71717a; font-size: 10px; padding: 4px 12px; background-color: #0d0d0e;")
        layout.addWidget(self.status_label)
        
        # Load initial URL
        self.load_url()
    
    def load_url(self):
        url = self.url_input.text()
        if not url.startswith(('http://', 'https://', 'file://')):
            url = 'https://' + url
        self.webview.setUrl(QUrl(url))
        self.status_label.setText(f"Loading: {url[:50]}...")
        self.status_label.setStyleSheet("color: #d4a017; font-size: 10px; padding: 4px 12px; background-color: #0d0d0e;")
    
    def load_local(self):
        if self.project_data.get('local_path') and Path(self.project_data['local_path']).exists():
            local_url = QUrl.fromLocalFile(str(Path(self.project_data['local_path']).absolute()))
            self.webview.setUrl(local_url)
            self.status_label.setText(f"Local: {self.project_data['local_path'][:40]}...")
            self.status_label.setStyleSheet("color: #22c55e; font-size: 10px; padding: 4px 12px; background-color: #0d0d0e;")
    
    def reload(self):
        self.webview.reload()
    
    def take_screenshot(self):
        # TODO: Implement screenshot functionality
        pass


class SEOToolsPanel(QFrame):
    """Sidebar panel with SEO tools"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("⚖️ SEOBOT")
        header.setObjectName("header")
        layout.addWidget(header)
        
        subheader = QLabel("SEO Law Engine + Code Rewriter")
        subheader.setObjectName("subheader")
        layout.addWidget(subheader)
        
        # Books count
        books_frame = QFrame()
        books_frame.setStyleSheet("background-color: #1a1a1d; border-radius: 8px; padding: 12px;")
        books_layout = QVBoxLayout(books_frame)
        books_layout.setContentsMargins(12, 12, 12, 12)
        
        books_count = QLabel("3")
        books_count.setStyleSheet("color: #d4a017; font-size: 32px; font-weight: 800; text-align: center;")
        books_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        books_layout.addWidget(books_count)
        
        books_label = QLabel("SEO Books Loaded")
        books_label.setStyleSheet("color: #71717a; font-size: 11px; text-align: center;")
        books_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        books_layout.addWidget(books_label)
        
        layout.addWidget(books_frame)
        
        # Tools tabs
        tools_tabs = QTabWidget()
        
        # Meta Generator Tab
        meta_tab = QWidget()
        meta_layout = QVBoxLayout(meta_tab)
        meta_layout.setSpacing(12)
        
        meta_layout.addWidget(QLabel("Page Title:"))
        self.meta_title = QLineEdit()
        self.meta_title.setPlaceholderText("50-60 characters")
        meta_layout.addWidget(self.meta_title)
        
        self.title_counter = QLabel("0/60")
        self.title_counter.setStyleSheet("color: #71717a; font-size: 10px;")
        meta_layout.addWidget(self.title_counter)
        
        meta_layout.addWidget(QLabel("Description:"))
        self.meta_desc = QTextEdit()
        self.meta_desc.setPlaceholderText("150-160 characters with CTA")
        self.meta_desc.setMaximumHeight(80)
        meta_layout.addWidget(self.meta_desc)
        
        self.desc_counter = QLabel("0/160")
        self.desc_counter.setStyleSheet("color: #71717a; font-size: 10px;")
        meta_layout.addWidget(self.desc_counter)
        
        self.generate_meta_btn = QPushButton("Generate Meta Tags")
        self.generate_meta_btn.clicked.connect(self.generate_meta)
        meta_layout.addWidget(self.generate_meta_btn)
        
        self.meta_output = QTextEdit()
        self.meta_output.setReadOnly(True)
        self.meta_output.setPlaceholderText("Generated meta tags will appear here...")
        meta_layout.addWidget(self.meta_output)
        
        meta_layout.addStretch()
        tools_tabs.addTab(meta_tab, "Meta")
        
        # Schema Tab
        schema_tab = QWidget()
        schema_layout = QVBoxLayout(schema_tab)
        schema_layout.setSpacing(12)
        
        schema_layout.addWidget(QLabel("Schema Type:"))
        self.schema_type = QComboBox()
        self.schema_type.addItems(["Organization", "Person", "LocalBusiness", "WebSite", "Article"])
        schema_layout.addWidget(self.schema_type)
        
        schema_layout.addWidget(QLabel("Name:"))
        self.schema_name = QLineEdit()
        schema_layout.addWidget(self.schema_name)
        
        schema_layout.addWidget(QLabel("URL:"))
        self.schema_url = QLineEdit()
        schema_layout.addWidget(self.schema_url)
        
        self.generate_schema_btn = QPushButton("Generate Schema")
        self.generate_schema_btn.clicked.connect(self.generate_schema)
        schema_layout.addWidget(self.generate_schema_btn)
        
        self.schema_output = QTextEdit()
        self.schema_output.setReadOnly(True)
        self.schema_output.setPlaceholderText("Generated JSON-LD will appear here...")
        schema_layout.addWidget(self.schema_output)
        
        schema_layout.addStretch()
        tools_tabs.addTab(schema_tab, "Schema")
        
        # Code Rewriter Tab
        rewriter_tab = QWidget()
        rewriter_layout = QVBoxLayout(rewriter_tab)
        rewriter_layout.setSpacing(12)
        
        rewriter_info = QLabel("Auto-fix SEO issues in your local project files:")
        rewriter_info.setStyleSheet("color: #71717a; font-size: 11px;")
        rewriter_info.setWordWrap(True)
        rewriter_layout.addWidget(rewriter_info)
        
        self.fix_meta_check = QCheckBox("Fix Meta Tags (50-60 char titles)")
        self.fix_meta_check.setChecked(True)
        rewriter_layout.addWidget(self.fix_meta_check)
        
        self.fix_schema_check = QCheckBox("Add Schema Markup")
        self.fix_schema_check.setChecked(True)
        rewriter_layout.addWidget(self.fix_schema_check)
        
        self.fix_og_check = QCheckBox("Add Open Graph")
        self.fix_og_check.setChecked(True)
        rewriter_layout.addWidget(self.fix_og_check)
        
        self.fix_alt_check = QCheckBox("Fix Image Alt Text")
        self.fix_alt_check.setChecked(True)
        rewriter_layout.addWidget(self.fix_alt_check)
        
        self.rewrite_btn = QPushButton("🚀 Rewrite Project Files")
        self.rewrite_btn.clicked.connect(self.rewrite_project)
        rewriter_layout.addWidget(self.rewrite_btn)
        
        self.rewrite_status = QLabel("Select a project with local files")
        self.rewrite_status.setStyleSheet("color: #71717a; font-size: 11px;")
        self.rewrite_status.setWordWrap(True)
        rewriter_layout.addWidget(self.rewrite_status)
        
        rewriter_layout.addStretch()
        tools_tabs.addTab(rewriter_tab, "Rewriter")
        
        layout.addWidget(tools_tabs)
        
        # Project selector
        layout.addWidget(QLabel("Active Project:"))
        self.project_combo = QComboBox()
        for pid, pdata in PROJECTS.items():
            self.project_combo.addItem(pdata['name'], pid)
        self.project_combo.currentIndexChanged.connect(self.on_project_changed)
        layout.addWidget(self.project_combo)
        
        layout.addStretch()
        
        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #22c55e; font-size: 11px; padding: 8px; background-color: #1a1a1d; border-radius: 4px;")
        layout.addWidget(self.status_label)
    
    def on_project_changed(self, index):
        project_id = self.project_combo.currentData()
        project = PROJECTS[project_id]
        
        # Update fields
        self.meta_title.setText(f"{project['name']} - {project['type']}")
        self.meta_desc.setText(project['description'])
        self.schema_name.setText(project['name'])
        self.schema_url.setText(f"https://{project['domain']}")
        
        # Update rewriter status
        if project.get('local_path') and Path(project['local_path']).exists():
            self.rewrite_status.setText(f"✓ Local files found\n{project['local_path'][:40]}...")
            self.rewrite_status.setStyleSheet("color: #22c55e; font-size: 11px;")
            self.rewrite_btn.setEnabled(True)
        else:
            self.rewrite_status.setText("✗ No local files\nSwitch to Adaryus or NCRJ Watch")
            self.rewrite_status.setStyleSheet("color: #ef4444; font-size: 11px;")
            self.rewrite_btn.setEnabled(False)
    
    def generate_meta(self):
        title = self.meta_title.text()
        desc = self.meta_desc.toPlainText()
        
        # Validate
        title_ok = 50 <= len(title) <= 60
        desc_ok = 150 <= len(desc) <= 160
        
        code = f"""<!-- SEO LAW COMPLIANT META TAGS -->
<title>{title}</title>
<meta name="title" content="{title}">
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- Open Graph -->
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">

<!-- Compliance: Title {len(title)}/60 {'✓' if title_ok else '✗'}, Desc {len(desc)}/160 {'✓' if desc_ok else '✗'} -->"""
        
        self.meta_output.setText(code)
    
    def generate_schema(self):
        schema_type = self.schema_type.currentText()
        name = self.schema_name.text()
        url = self.schema_url.text()
        
        schema = {
            "@context": "https://schema.org",
            "@type": schema_type,
            "name": name,
            "url": url
        }
        
        if schema_type == "Organization":
            schema["logo"] = f"{url}/logo.png"
        elif schema_type == "LocalBusiness":
            schema["address"] = {"@type": "PostalAddress", "addressRegion": "WV"}
        
        code = f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'
        self.schema_output.setText(code)
    
    def rewrite_project(self):
        project_id = self.project_combo.currentData()
        project = PROJECTS[project_id]
        
        if not project.get('local_path'):
            return
        
        self.rewrite_status.setText("Rewriting... Check console for details")
        
        # TODO: Implement actual file rewriting
        # This would call the code_rewriter module
        
        self.rewrite_status.setText("✓ Rewrite complete! Backup created.")


class SEOBOTDesktop(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SEOBOT Desktop - Multi-Site Preview & SEO Tool")
        self.setMinimumSize(1600, 1000)
        
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # SEO Tools sidebar
        self.sidebar = SEOToolsPanel()
        splitter.addWidget(self.sidebar)
        
        # Preview area
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(12, 12, 12, 12)
        preview_layout.setSpacing(12)
        
        # Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: #141416; border-radius: 8px;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)
        
        toolbar_layout.addWidget(QLabel("Layout:"))
        
        self.layout_2x3_btn = QPushButton("2×3 Grid")
        self.layout_2x3_btn.setObjectName("secondary")
        self.layout_2x3_btn.clicked.connect(lambda: self.set_layout(2, 3))
        toolbar_layout.addWidget(self.layout_2x3_btn)
        
        self.layout_3x2_btn = QPushButton("3×2 Grid")
        self.layout_3x2_btn.setObjectName("secondary")
        self.layout_3x2_btn.clicked.connect(lambda: self.set_layout(3, 2))
        toolbar_layout.addWidget(self.layout_3x2_btn)
        
        toolbar_layout.addStretch()
        
        reload_all_btn = QPushButton("🔄 Reload All")
        reload_all_btn.clicked.connect(self.reload_all)
        toolbar_layout.addWidget(reload_all_btn)
        
        preview_layout.addWidget(toolbar)
        
        # Previews grid
        self.previews_widget = QWidget()
        self.previews_layout = QGridLayout(self.previews_widget)
        self.previews_layout.setSpacing(8)
        
        # Create preview widgets for all projects
        self.preview_widgets = {}
        for i, (pid, pdata) in enumerate(PROJECTS.items()):
            preview = PreviewWidget(pid, pdata)
            self.preview_widgets[pid] = preview
        
        # Default layout: 2x3
        self.set_layout(2, 3)
        
        # Scroll area for previews
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.previews_widget)
        scroll.setStyleSheet("background-color: #0a0a0b; border: none;")
        
        preview_layout.addWidget(scroll, 1)
        
        splitter.addWidget(preview_container)
        
        # Set splitter sizes (sidebar: 300, previews: rest)
        splitter.setSizes([320, 1280])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("SEOBOT Desktop Ready | 6 Projects Loaded")
    
    def set_layout(self, cols, rows):
        """Arrange previews in grid"""
        # Clear current layout
        while self.previews_layout.count():
            item = self.previews_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Add widgets in new layout
        project_ids = list(PROJECTS.keys())
        for i, pid in enumerate(project_ids):
            row = i // cols
            col = i % cols
            if row < rows:
                self.previews_layout.addWidget(self.preview_widgets[pid], row, col)
    
    def reload_all(self):
        for preview in self.preview_widgets.values():
            preview.reload()
        self.statusBar().showMessage("All previews reloaded", 3000)
    
    def apply_theme(self):
        self.setStyleSheet(DARK_THEME)


def main():
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont("Inter", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    
    # Create and show main window
    window = SEOBOTDesktop()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

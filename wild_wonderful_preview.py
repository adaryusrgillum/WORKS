"""
WILD & WONDERFUL WEBSITES - Preview Grid
6 Black & White Sites. Zero Bloat. Maximum Impact.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QFont, QColor

# 6 WILD & WONDERFUL Sites
SITES = {
    "wild": {
        "name": "WILD & WONDERFUL",
        "subtitle": "Portfolio",
        "path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\app\dist_wild\index.html",
        "accent": "#000000"
    },
    "ncrj": {
        "name": "NCRJ WATCH",
        "subtitle": "Advocacy",
        "path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\NCRJFincal-main\public_html_wild\index.html",
        "accent": "#000000"
    },
    "advertise": {
        "name": "ADVERTISEWV",
        "subtitle": "Marketing",
        "path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\advertisewv_wild\index.html",
        "accent": "#000000"
    },
    "darkrose": {
        "name": "DARK ROSE",
        "subtitle": "Tattoo Studio",
        "path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\darkrose_wild\index.html",
        "accent": "#000000"
    },
    "mdi": {
        "name": "MDI TRAINING",
        "subtitle": "Firearms Training",
        "path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\mdi_wild\index.html",
        "accent": "#000000"
    },
    "gotti": {
        "name": "ULTIMATE GOTTI",
        "subtitle": "Dog Breeding",
        "path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\ultimategotti_wild\index.html",
        "accent": "#000000"
    }
}

# BLACK & WHITE THEME
THEME = """
QMainWindow, QWidget {
    background-color: #000000;
    color: #ffffff;
    font-family: 'Bebas Neue', 'Inter', sans-serif;
}

#sidebar {
    background-color: #0a0a0a;
    border-right: 2px solid #ffffff;
    min-width: 280px;
    max-width: 300px;
}

#preview-card {
    background-color: #000000;
    border: 2px solid #ffffff;
}

QPushButton {
    background-color: #ffffff;
    color: #000000;
    border: none;
    border-radius: 0;
    padding: 12px 24px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

QPushButton:hover {
    background-color: #cccccc;
}

QPushButton#secondary {
    background-color: transparent;
    color: #ffffff;
    border: 2px solid #ffffff;
}

QPushButton#secondary:hover {
    background-color: #ffffff;
    color: #000000;
}

#header-big {
    color: #ffffff;
    font-size: 2.5rem;
    font-weight: 900;
    letter-spacing: 0.05em;
}

#header-sub {
    color: #888888;
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}

QListWidget {
    background: #000000;
    border: 1px solid #333333;
    color: #ffffff;
}

QListWidget::item {
    padding: 12px;
    border-bottom: 1px solid #222222;
}
"""


class SitePreview(QFrame):
    def __init__(self, site_id, site_data):
        super().__init__()
        self.site_id = site_id
        self.site = site_data
        self.setObjectName("preview-card")
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setStyleSheet("background: #ffffff; color: #000000;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(12, 8, 12, 8)
        
        name = QLabel(self.site['name'])
        name.setStyleSheet("font-weight: 900; font-size: 14px; letter-spacing: 0.05em;")
        hl.addWidget(name)
        
        hl.addStretch()
        
        sub = QLabel(self.site['subtitle'])
        sub.setStyleSheet("font-size: 10px; opacity: 0.6;")
        hl.addWidget(sub)
        
        layout.addWidget(header)
        
        # Web view
        self.webview = QWebEngineView()
        self.webview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        settings = self.webview.settings()
        settings.setAttribute(self.webview.settings().WebAttribute.PlaybackRequiresUserGesture, False)
        settings.setAttribute(self.webview.settings().WebAttribute.WebGLEnabled, True)
        settings.setAttribute(self.webview.settings().WebAttribute.JavascriptEnabled, True)
        
        path = self.site['path']
        if Path(path).exists():
            self.webview.setUrl(QUrl.fromLocalFile(str(Path(path).absolute())))
        
        layout.addWidget(self.webview, 1)
        
        # Status
        self.status = QLabel("Loading...")
        self.status.setStyleSheet("color: #666666; font-size: 10px; padding: 6px 12px; background: #000000;")
        layout.addWidget(self.status)
        
        self.webview.loadFinished.connect(self.on_loaded)
    
    def on_loaded(self, ok):
        self.status.setText("READY" if ok else "ERROR")
        self.status.setStyleSheet(f"color: {'#ffffff' if ok else '#ff0000'}; font-size: 10px; padding: 6px 12px; background: #000000;")
    
    def reload(self):
        self.webview.reload()


class WildWonderfulPreview(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WILD & WONDERFUL WEBSITES - 6 Site Preview")
        self.setMinimumSize(1920, 1080)
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(20, 20, 20, 20)
        
        # Brand
        brand = QLabel("WILD &")
        brand.setObjectName("header-big")
        sl.addWidget(brand)
        
        brand2 = QLabel("WONDERFUL")
        brand2.setObjectName("header-big")
        brand2.setStyleSheet("color: #000000; background: #ffffff; padding: 0 8px; font-size: 2.5rem; font-weight: 900;")
        sl.addWidget(brand2)
        
        sub = QLabel("WEBSITES")
        sub.setObjectName("header-sub")
        sub.setStyleSheet("margin-top: 8px; margin-bottom: 24px;")
        sl.addWidget(sub)
        
        # Stats
        stats = QFrame()
        stats.setStyleSheet("background: #111111; border: 1px solid #333333;")
        st = QVBoxLayout(stats)
        
        sites = QLabel("6")
        sites.setStyleSheet("color: #ffffff; font-size: 48px; font-weight: 900;")
        sites.setAlignment(Qt.AlignmentFlag.AlignCenter)
        st.addWidget(sites)
        
        sites_txt = QLabel("SITES")
        sites_txt.setObjectName("header-sub")
        sites_txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        st.addWidget(sites_txt)
        
        style = QLabel("BLACK & WHITE")
        style.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: 700; margin-top: 16px;")
        style.setAlignment(Qt.AlignmentFlag.AlignCenter)
        st.addWidget(style)
        
        sl.addWidget(stats)
        
        # Site list
        sl.addSpacing(20)
        sl.addWidget(QLabel("SITES:"))
        
        sites_list = QListWidget()
        for sid, sdata in SITES.items():
            item = QListWidgetItem(f"  {sdata['name']}")
            sites_list.addItem(item)
        sl.addWidget(sites_list)
        
        # Controls
        sl.addSpacing(20)
        
        btn_2x3 = QPushButton("2 x 3 GRID")
        btn_2x3.clicked.connect(lambda: self.set_layout(2, 3))
        sl.addWidget(btn_2x3)
        
        btn_3x2 = QPushButton("3 x 2 GRID")
        btn_3x2.setObjectName("secondary")
        btn_3x2.clicked.connect(lambda: self.set_layout(3, 2))
        sl.addWidget(btn_3x2)
        
        btn_reload = QPushButton("RELOAD ALL")
        btn_reload.setObjectName("secondary")
        btn_reload.clicked.connect(self.reload_all)
        sl.addWidget(btn_reload)
        
        sl.addStretch()
        
        # Footer
        footer = QLabel("ZERO BLOAT\nMAXIMUM IMPACT")
        footer.setObjectName("header-sub")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sl.addWidget(footer)
        
        splitter.addWidget(sidebar)
        
        # Preview area
        preview = QWidget()
        pl = QVBoxLayout(preview)
        pl.setContentsMargins(12, 12, 12, 12)
        
        # Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("background: #111111; border: 1px solid #333333;")
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(16, 12, 16, 12)
        
        tl.addWidget(QLabel("6-SITE PREVIEW GRID"))
        tl.addStretch()
        
        tl.addWidget(QLabel("LAYOUT:"))
        for name, cols, rows in [("2x3", 2, 3), ("3x2", 3, 2)]:
            btn = QPushButton(name)
            btn.setObjectName("secondary")
            btn.setStyleSheet("padding: 6px 16px;")
            btn.clicked.connect(lambda c, co=cols, r=rows: self.set_layout(co, r))
            tl.addWidget(btn)
        
        pl.addWidget(toolbar)
        
        # Grid
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(8)
        
        # Create previews
        self.previews = {}
        for sid, sdata in SITES.items():
            preview = SitePreview(sid, sdata)
            self.previews[sid] = preview
        
        self.set_layout(2, 3)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.grid_widget)
        scroll.setStyleSheet("background: #000000; border: none;")
        
        pl.addWidget(scroll, 1)
        
        splitter.addWidget(preview)
        splitter.setSizes([300, 1620])
        
        main_layout.addWidget(splitter)
        
        self.statusBar().setStyleSheet("background: #000000; color: #ffffff; border-top: 2px solid #ffffff;")
        self.statusBar().showMessage("WILD & WONDERFUL WEBSITES | 6 Black & White Sites | Zero Bloat | Maximum Impact")
    
    def set_layout(self, cols, rows):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        for i, (sid, preview) in enumerate(self.previews.items()):
            row = i // cols
            col = i % cols
            if row < rows:
                self.grid_layout.addWidget(preview, row, col)
    
    def reload_all(self):
        for preview in self.previews.values():
            preview.reload()
    
    def apply_theme(self):
        self.setStyleSheet(THEME)


def main():
    app = QApplication(sys.argv)
    
    # Load fonts
    font = QFont("Inter", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    
    window = WildWonderfulPreview()
    window.showMaximized()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

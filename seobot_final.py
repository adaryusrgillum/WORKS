"""
SEOBOT Final - Complete SEO Tool with 6 Responsive Websites
All sites rebuilt based on 776 rules from 5 SEO books
"""

import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QFont

# 6 Projects with responsive builds
PROJECTS = {
    "adaryus": {
        "name": "Adaryus Portfolio",
        "color": "#ff0000",
        "path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\app\dist_responsive\index.html",
        "type": "Portfolio",
        "has_webgl": False,
        "has_video": False
    },
    "ncrjwatch": {
        "name": "NCRJ Watch",
        "color": "#ffd700",
        "path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\NCRJFincal-main\public_html_responsive\index.html",
        "type": "Advocacy",
        "has_webgl": False,
        "has_video": False
    },
    "advertisewv": {
        "name": "AdvertiseWV",
        "color": "#10b981",
        "path": r"C:\Users\adary\Downloads\adaryus-main-extracted\advertisewv_responsive\index.html",
        "type": "Marketing",
        "has_webgl": False,
        "has_video": False
    },
    "darkrose": {
        "name": "Dark Rose Tattoo",
        "color": "#8b5cf6",
        "path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\darkrose_responsive\index.html",
        "type": "Tattoo Studio",
        "has_webgl": False,
        "has_video": True
    },
    "mdi": {
        "name": "MDI Training",
        "color": "#ef4444",
        "path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\mdi_responsive\index.html",
        "type": "Training",
        "has_webgl": False,
        "has_video": False
    },
    "ultimategotti": {
        "name": "Ultimate Gotti Line",
        "color": "#f59e0b",
        "path": r"C:\Users\adary\Downloads\adaryus-main-extracted\adaryus-main\ultimategotti_responsive\index.html",
        "type": "Dog Breeding",
        "has_webgl": False,
        "has_video": False
    }
}

DARK_THEME = """
QMainWindow, QWidget {
    background-color: #0a0a0b;
    color: #fafafa;
    font-family: 'Inter', sans-serif;
}

#sidebar {
    background-color: #141416;
    border-right: 1px solid #27272a;
    min-width: 300px;
    max-width: 320px;
}

#preview-card {
    background-color: #141416;
    border: 1px solid #27272a;
    border-radius: 12px;
    margin: 6px;
}

QPushButton {
    background-color: #d4a017;
    color: #0a0a0b;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: 700;
}

QPushButton:hover { background-color: #f4d03f; }

QPushButton#secondary {
    background-color: transparent;
    color: #d4a017;
    border: 1px solid #d4a017;
}

#header {
    color: #d4a017;
    font-size: 22px;
    font-weight: 800;
}
"""


class PreviewCard(QFrame):
    """Individual website preview card"""
    
    def __init__(self, project_id, project):
        super().__init__()
        self.project_id = project_id
        self.project = project
        self.setObjectName("preview-card")
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setStyleSheet(f"background: #1a1a1d; border-bottom: 1px solid #27272a; border-radius: 12px 12px 0 0;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(12, 8, 12, 8)
        
        name = QLabel(f"● {self.project['name']}")
        name.setStyleSheet(f"color: {self.project['color']}; font-weight: 700; font-size: 12px;")
        hl.addWidget(name)
        
        hl.addStretch()
        
        type_lbl = QLabel(self.project['type'])
        type_lbl.setStyleSheet("color: #71717a; font-size: 10px; background: #27272a; padding: 2px 8px; border-radius: 4px;")
        hl.addWidget(type_lbl)
        
        if self.project.get('has_video'):
            hl.addWidget(QLabel("🎬"))
        
        layout.addWidget(header)
        
        # Web view
        self.webview = QWebEngineView()
        self.webview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        settings = self.webview.settings()
        settings.setAttribute(self.webview.settings().WebAttribute.PlaybackRequiresUserGesture, False)
        settings.setAttribute(self.webview.settings().WebAttribute.WebGLEnabled, True)
        settings.setAttribute(self.webview.settings().WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(self.webview.settings().WebAttribute.LocalStorageEnabled, True)
        
        # Load local file
        path = self.project['path']
        if Path(path).exists():
            self.webview.setUrl(QUrl.fromLocalFile(str(Path(path).absolute())))
        
        layout.addWidget(self.webview, 1)
        
        # Status
        self.status = QLabel("Ready")
        self.status.setStyleSheet("color: #71717a; font-size: 10px; padding: 6px 12px; background: #0d0d0e; border-radius: 0 0 12px 12px;")
        layout.addWidget(self.status)
        
        # Connect load finished
        self.webview.loadFinished.connect(self.on_load_finished)
    
    def on_load_finished(self, ok):
        if ok:
            self.status.setText("✓ Loaded")
            self.status.setStyleSheet("color: #22c55e; font-size: 10px; padding: 6px 12px; background: #0d0d0e; border-radius: 0 0 12px 12px;")
        else:
            self.status.setText("✗ Error")
            self.status.setStyleSheet("color: #ef4444; font-size: 10px; padding: 6px 12px; background: #0d0d0e; border-radius: 0 0 12px 12px;")
    
    def reload(self):
        self.webview.reload()


class SEOBOTFinal(QMainWindow):
    """Main application with 6-site grid"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SEOBOT Final - 6 Responsive Sites | 776 SEO Rules Applied")
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
        sl.setContentsMargins(16, 16, 16, 16)
        
        # Header
        hdr = QLabel("⚖️ SEOBOT FINAL")
        hdr.setObjectName("header")
        sl.addWidget(hdr)
        
        sub = QLabel("6 Responsive Sites | 776 SEO Rules")
        sub.setStyleSheet("color: #71717a; font-size: 11px;")
        sl.addWidget(sub)
        
        # Stats
        stats = QFrame()
        stats.setStyleSheet("background: #1a1a1d; border-radius: 8px; padding: 12px;")
        st = QVBoxLayout(stats)
        
        sites_lbl = QLabel("6")
        sites_lbl.setStyleSheet("color: #d4a017; font-size: 36px; font-weight: 800;")
        sites_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        st.addWidget(sites_lbl)
        
        sites_txt = QLabel("Sites Rebuilt")
        sites_txt.setStyleSheet("color: #71717a; font-size: 11px;")
        sites_txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        st.addWidget(sites_txt)
        
        rules_lbl = QLabel("776")
        rules_lbl.setStyleSheet("color: #22c55e; font-size: 36px; font-weight: 800;")
        rules_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        st.addWidget(rules_lbl)
        
        rules_txt = QLabel("SEO Rules Applied")
        rules_txt.setStyleSheet("color: #71717a; font-size: 11px;")
        rules_txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        st.addWidget(rules_txt)
        
        sl.addWidget(stats)
        
        # Site list
        sl.addWidget(QLabel("Responsive Builds:"))
        
        sites_list = QListWidget()
        sites_list.setStyleSheet("background: #0d0d0e; border: 1px solid #27272a; border-radius: 8px;")
        for pid, pdata in PROJECTS.items():
            item = QListWidgetItem(f"  ✓ {pdata['name']}")
            item.setForeground(QColor(pdata['color']))
            sites_list.addItem(item)
        sl.addWidget(sites_list)
        
        # Controls
        sl.addWidget(QLabel("Grid Layout:"))
        
        btn_2x3 = QPushButton("2 × 3 Grid")
        btn_2x3.clicked.connect(lambda: self.set_layout(2, 3))
        sl.addWidget(btn_2x3)
        
        btn_3x2 = QPushButton("3 × 2 Grid")
        btn_3x2.clicked.connect(lambda: self.set_layout(3, 2))
        sl.addWidget(btn_3x2)
        
        btn_reload = QPushButton("🔄 Reload All")
        btn_reload.clicked.connect(self.reload_all)
        sl.addWidget(btn_reload)
        
        sl.addStretch()
        
        # Footer
        footer = QLabel("Based on 5 SEO Books\nAI For SEO • SEO Marketing\nSEO Practice • SEO 2024")
        footer.setStyleSheet("color: #52525b; font-size: 10px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sl.addWidget(footer)
        
        splitter.addWidget(sidebar)
        
        # Preview area
        preview_widget = QWidget()
        pl = QVBoxLayout(preview_widget)
        pl.setContentsMargins(12, 12, 12, 12)
        
        # Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("background: #141416; border-radius: 8px;")
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(12, 8, 12, 8)
        
        tl.addWidget(QLabel("📺 6-Site Preview Grid"))
        tl.addStretch()
        
        tl.addWidget(QLabel("Layout:"))
        
        for layout_name, cols, rows in [("2×3", 2, 3), ("3×2", 3, 2)]:
            btn = QPushButton(layout_name)
            btn.setObjectName("secondary")
            btn.setStyleSheet("padding: 6px 16px; font-size: 12px;")
            btn.clicked.connect(lambda checked, c=cols, r=rows: self.set_layout(c, r))
            tl.addWidget(btn)
        
        pl.addWidget(toolbar)
        
        # Grid container
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(12)
        
        # Create preview cards
        self.preview_cards = {}
        for pid, pdata in PROJECTS.items():
            card = PreviewCard(pid, pdata)
            self.preview_cards[pid] = card
        
        # Default 2x3 layout
        self.set_layout(2, 3)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.grid_widget)
        scroll.setStyleSheet("background: #0a0a0b; border: none;")
        
        pl.addWidget(scroll, 1)
        
        splitter.addWidget(preview_widget)
        splitter.setSizes([320, 1600])
        
        main_layout.addWidget(splitter)
        
        self.statusBar().showMessage("SEOBOT Final | All 6 sites responsive | 776 SEO rules applied")
    
    def set_layout(self, cols, rows):
        """Arrange previews in grid"""
        # Clear current layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Add cards in new layout
        for i, (pid, card) in enumerate(self.preview_cards.items()):
            row = i // cols
            col = i % cols
            if row < rows:
                self.grid_layout.addWidget(card, row, col)
    
    def reload_all(self):
        for card in self.preview_cards.values():
            card.reload()
        self.statusBar().showMessage("All sites reloaded", 3000)
    
    def apply_theme(self):
        self.setStyleSheet(DARK_THEME)


def main():
    app = QApplication(sys.argv)
    
    font = QFont("Inter", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    
    window = SEOBOTFinal()
    window.showMaximized()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

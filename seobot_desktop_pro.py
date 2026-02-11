"""
SEOBOT Desktop Pro - Complete SEO Tool with Knowledge Engine
Integrates 5 EPUB books, live previews, and auto-update functionality
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QSplitter, QLabel, QPushButton, QTextEdit, QLineEdit,
    QComboBox, QCheckBox, QScrollArea, QFrame, QTabWidget, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog,
    QGroupBox, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QAction, QFont, QPalette, QColor

# Import our modules
sys.path.insert(0, str(Path(__file__).parent))
from seo_knowledge_engine import seo_engine, SEOKnowledgeEngine
from website_updater import WebsiteUpdater

# Project configurations with local paths
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

# Dark theme stylesheet
DARK_THEME = """
QMainWindow, QWidget {
    background-color: #0a0a0b;
    color: #fafafa;
    font-family: 'Inter', -apple-system, sans-serif;
}

#sidebar {
    background-color: #141416;
    border-right: 1px solid #27272a;
    min-width: 350px;
    max-width: 400px;
}

#preview-container {
    background-color: #141416;
    border: 1px solid #27272a;
    border-radius: 8px;
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

QPushButton#secondary:hover { background-color: rgba(212, 160, 23, 0.1); }

QLineEdit, QTextEdit, QComboBox {
    background-color: #1a1a1d;
    border: 1px solid #27272a;
    border-radius: 6px;
    padding: 8px 12px;
    color: #fafafa;
}

QTabWidget::pane {
    background-color: #141416;
    border: 1px solid #27272a;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #1a1a1d;
    color: #71717a;
    padding: 10px 20px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #d4a017;
    color: #0a0a0b;
}

QGroupBox {
    background-color: #141416;
    border: 1px solid #27272a;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: 600;
    color: #d4a017;
}

QTableWidget {
    background-color: #1a1a1d;
    border: 1px solid #27272a;
    border-radius: 8px;
    gridline-color: #27272a;
}

QTableWidget::item { padding: 8px; }
QHeaderView::section {
    background-color: #27272a;
    color: #fafafa;
    padding: 8px;
    font-weight: 600;
}

QProgressBar {
    background-color: #1a1a1d;
    border: 1px solid #27272a;
    border-radius: 4px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #d4a017;
    border-radius: 4px;
}

#header {
    color: #d4a017;
    font-size: 24px;
    font-weight: 800;
}

#subheader {
    color: #71717a;
    font-size: 12px;
}

#status-online { color: #22c55e; }
#status-offline { color: #ef4444; }
#status-warning { color: #f59e0b; }
"""


class PreviewWidget(QFrame):
    """Web preview widget with controls"""
    
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
        
        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #1a1a1d; border-bottom: 1px solid #27272a;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 12, 8)
        
        name = QLabel(f"● {self.project_data['name']}")
        name.setStyleSheet(f"color: {self.project_data['color']}; font-weight: 700; font-size: 12px;")
        header_layout.addWidget(name)
        
        header_layout.addStretch()
        
        type_label = QLabel(self.project_data['type'])
        type_label.setStyleSheet("color: #71717a; font-size: 10px; background: #27272a; padding: 2px 8px; border-radius: 4px;")
        header_layout.addWidget(type_label)
        
        if self.project_data.get('has_video'):
            header_layout.addWidget(QLabel("🎬"))
        if self.project_data.get('has_webgl'):
            header_layout.addWidget(QLabel("🎮"))
        
        layout.addWidget(header)
        
        # URL bar
        url_bar = QFrame()
        url_bar.setStyleSheet("background: #0d0d0e;")
        url_layout = QHBoxLayout(url_bar)
        url_layout.setContentsMargins(12, 4, 12, 4)
        
        self.url_input = QLineEdit(self.project_data['url'])
        self.url_input.setStyleSheet("font-size: 11px;")
        url_layout.addWidget(self.url_input)
        
        load_btn = QPushButton("Load")
        load_btn.setObjectName("secondary")
        load_btn.setStyleSheet("padding: 4px 12px; font-size: 10px;")
        load_btn.clicked.connect(self.load_url)
        url_layout.addWidget(load_btn)
        
        local_btn = QPushButton("Local")
        local_btn.setObjectName("secondary")
        local_btn.setStyleSheet("padding: 4px 12px; font-size: 10px;")
        local_btn.clicked.connect(self.load_local)
        local_path = self.project_data.get('local_path')
        local_btn.setEnabled(local_path is not None and Path(local_path).exists())
        url_layout.addWidget(local_btn)
        
        layout.addWidget(url_bar)
        
        # Web view
        self.webview = QWebEngineView()
        self.webview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        settings = self.webview.settings()
        settings.setAttribute(self.webview.settings().WebAttribute.PlaybackRequiresUserGesture, False)
        settings.setAttribute(self.webview.settings().WebAttribute.WebGLEnabled, True)
        settings.setAttribute(self.webview.settings().WebAttribute.JavascriptEnabled, True)
        
        layout.addWidget(self.webview, 1)
        
        # Status
        self.status = QLabel("Ready")
        self.status.setStyleSheet("color: #71717a; font-size: 10px; padding: 4px 12px; background: #0d0d0e;")
        layout.addWidget(self.status)
        
        self.load_url()
    
    def load_url(self):
        url = self.url_input.text()
        if not url.startswith(('http://', 'https://', 'file://')):
            url = 'https://' + url
        self.webview.setUrl(QUrl(url))
        self.status.setText(f"Loading: {url[:40]}...")
    
    def load_local(self):
        path = self.project_data.get('local_path')
        if path and Path(path).exists():
            self.webview.setUrl(QUrl.fromLocalFile(str(Path(path).absolute())))
            self.status.setText("Local file loaded")
            self.status.setStyleSheet("color: #22c55e; font-size: 10px; padding: 4px 12px; background: #0d0d0e;")
    
    def reload(self):
        self.webview.reload()


class KnowledgePanel(QFrame):
    """SEO Knowledge Engine panel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("⚖️ SEOBOT PRO")
        header.setObjectName("header")
        layout.addWidget(header)
        
        sub = QLabel("Knowledge Engine + Auto-Updater")
        sub.setObjectName("subheader")
        layout.addWidget(sub)
        
        # Books info
        books_frame = QGroupBox("📚 Knowledge Base (5 Books)")
        books_layout = QVBoxLayout()
        
        books = [
            "AI For SEO Essentials (2024)",
            "SEO Marketing Secrets (2016)",
            "SEO Practice: Get To Top (2024)",
            "SEO 2024: Mastering SEO",
            "Python Programming (Ref)"
        ]
        
        for book in books:
            lbl = QLabel(f"  ✓ {book}")
            lbl.setStyleSheet("color: #a1a1aa; font-size: 11px;")
            books_layout.addWidget(lbl)
        
        # Stats
        self.rules_label = QLabel(f"Total Rules: {len(seo_engine.rules)}")
        self.rules_label.setStyleSheet("color: #d4a017; font-weight: 700; margin-top: 8px;")
        books_layout.addWidget(self.rules_label)
        
        critical = len(seo_engine.get_critical_rules())
        self.critical_label = QLabel(f"Critical: {critical} | High: {len(seo_engine.knowledge_base['priorities']['high'])}")
        self.critical_label.setStyleSheet("color: #71717a; font-size: 11px;")
        books_layout.addWidget(self.critical_label)
        
        books_frame.setLayout(books_layout)
        layout.addWidget(books_frame)
        
        # Tabs
        tabs = QTabWidget()
        
        # Meta Generator Tab
        meta_tab = QWidget()
        meta_layout = QVBoxLayout(meta_tab)
        
        meta_layout.addWidget(QLabel("Title:"))
        self.meta_title = QLineEdit()
        self.meta_title.textChanged.connect(self.validate_meta)
        meta_layout.addWidget(self.meta_title)
        
        self.title_status = QLabel("0/60 chars")
        self.title_status.setStyleSheet("font-size: 10px; color: #71717a;")
        meta_layout.addWidget(self.title_status)
        
        meta_layout.addWidget(QLabel("Description:"))
        self.meta_desc = QTextEdit()
        self.meta_desc.setMaximumHeight(80)
        self.meta_desc.textChanged.connect(self.validate_meta)
        meta_layout.addWidget(self.meta_desc)
        
        self.desc_status = QLabel("0/160 chars")
        self.desc_status.setStyleSheet("font-size: 10px; color: #71717a;")
        meta_layout.addWidget(self.desc_status)
        
        gen_btn = QPushButton("Generate Compliant Meta Tags")
        gen_btn.clicked.connect(self.generate_meta)
        meta_layout.addWidget(gen_btn)
        
        self.meta_output = QTextEdit()
        self.meta_output.setReadOnly(True)
        self.meta_output.setPlaceholderText("Generated code...")
        meta_layout.addWidget(self.meta_output)
        
        tabs.addTab(meta_tab, "Meta")
        
        # Schema Tab
        schema_tab = QWidget()
        schema_layout = QVBoxLayout(schema_tab)
        
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
        
        schema_btn = QPushButton("Generate Schema")
        schema_btn.clicked.connect(self.generate_schema)
        schema_layout.addWidget(schema_btn)
        
        self.schema_output = QTextEdit()
        self.schema_output.setReadOnly(True)
        schema_layout.addWidget(self.schema_output)
        
        tabs.addTab(schema_tab, "Schema")
        
        # Auto-Update Tab
        update_tab = QWidget()
        update_layout = QVBoxLayout(update_tab)
        
        update_info = QLabel("Auto-fix SEO issues using Knowledge Engine:")
        update_info.setStyleSheet("color: #a1a1aa; font-size: 12px;")
        update_info.setWordWrap(True)
        update_layout.addWidget(update_info)
        
        # Checkboxes for fixes
        self.fix_meta = QCheckBox("Fix Meta Tags (50-60 char rule)")
        self.fix_meta.setChecked(True)
        update_layout.addWidget(self.fix_meta)
        
        self.fix_schema_cb = QCheckBox("Add Schema Markup")
        self.fix_schema_cb.setChecked(True)
        update_layout.addWidget(self.fix_schema_cb)
        
        self.fix_og = QCheckBox("Add Open Graph")
        self.fix_og.setChecked(True)
        update_layout.addWidget(self.fix_og)
        
        self.fix_twitter = QCheckBox("Add Twitter Cards")
        self.fix_twitter.setChecked(True)
        update_layout.addWidget(self.fix_twitter)
        
        self.fix_alt = QCheckBox("Fix Image Alt Text")
        self.fix_alt.setChecked(True)
        update_layout.addWidget(self.fix_alt)
        
        self.fix_performance = QCheckBox("Add Performance Optimizations")
        self.fix_performance.setChecked(True)
        update_layout.addWidget(self.fix_performance)
        
        self.update_btn = QPushButton("🚀 Auto-Update Project Files")
        self.update_btn.clicked.connect(self.run_auto_update)
        update_layout.addWidget(self.update_btn)
        
        self.update_status = QLabel("Select a project with local files")
        self.update_status.setStyleSheet("color: #71717a; font-size: 11px;")
        self.update_status.setWordWrap(True)
        update_layout.addWidget(self.update_status)
        
        # Results area
        self.update_results = QTextEdit()
        self.update_results.setReadOnly(True)
        self.update_results.setMaximumHeight(150)
        update_layout.addWidget(self.update_results)
        
        tabs.addTab(update_tab, "Auto-Update")
        
        # Rules Tab
        rules_tab = QWidget()
        rules_layout = QVBoxLayout(rules_tab)
        
        self.rules_list = QListWidget()
        for rule in seo_engine.get_critical_rules()[:10]:
            item = QListWidgetItem(f"[{rule.priority.upper()}] {rule.rule[:60]}...")
            item.setToolTip(f"Source: {rule.source}\nFix: {rule.fix_instructions}")
            self.rules_list.addItem(item)
        
        rules_layout.addWidget(QLabel("Critical SEO Rules:"))
        rules_layout.addWidget(self.rules_list)
        
        tabs.addTab(rules_tab, "Rules")
        
        layout.addWidget(tabs)
        
        # Project selector
        layout.addWidget(QLabel("Active Project:"))
        self.project_combo = QComboBox()
        for pid, pdata in PROJECTS.items():
            self.project_combo.addItem(pdata['name'], pid)
        self.project_combo.currentIndexChanged.connect(self.on_project_change)
        layout.addWidget(self.project_combo)
        
        layout.addStretch()
    
    def validate_meta(self):
        title = self.meta_title.text()
        desc = self.meta_desc.toPlainText()
        
        # Validate title
        is_valid, issues = seo_engine.validate_meta_title(title)
        self.title_status.setText(f"{len(title)}/60 - {'✓' if is_valid else '✗'}")
        self.title_status.setStyleSheet(f"font-size: 10px; color: {'#22c55e' if is_valid else '#ef4444'};")
        
        # Validate description
        is_valid, issues = seo_engine.validate_meta_description(desc)
        self.desc_status.setText(f"{len(desc)}/160 - {'✓' if is_valid else '✗'}")
        self.desc_status.setStyleSheet(f"font-size: 10px; color: {'#22c55e' if is_valid else '#ef4444'};")
    
    def generate_meta(self):
        project_id = self.project_combo.currentData()
        project = PROJECTS[project_id]
        
        page_data = {
            'title': self.meta_title.text() or f"{project['name']} - {project['type']}",
            'description': self.meta_desc.toPlainText() or project['description'],
            'url': f"https://{project['domain']}",
            'site_name': project['name'],
            'og_type': 'website'
        }
        
        code = seo_engine.get_complete_meta_tags(page_data)
        self.meta_output.setText(code)
    
    def generate_schema(self):
        project_id = self.project_combo.currentData()
        project = PROJECTS[project_id]
        
        page_data = {
            'schema_type': self.schema_type.currentText(),
            'title': self.schema_name.text() or project['name'],
            'url': self.schema_url.text() or f"https://{project['domain']}",
            'description': project['description'],
            'name': project['name']
        }
        
        code = seo_engine.get_complete_schema(page_data)
        self.schema_output.setText(code)
    
    def run_auto_update(self):
        project_id = self.project_combo.currentData()
        project = PROJECTS[project_id]
        
        local_path = project.get('local_path')
        if not local_path or not Path(local_path).exists():
            self.update_status.setText("✗ No local files found for this project")
            self.update_status.setStyleSheet("color: #ef4444; font-size: 11px;")
            return
        
        self.update_status.setText("⏳ Running auto-update...")
        self.update_status.setStyleSheet("color: #d4a017; font-size: 11px;")
        
        # Get project directory
        project_dir = Path(local_path).parent
        
        # Run updater
        try:
            updater = WebsiteUpdater(str(project_dir), project)
            result = updater.run_full_update()
            
            # Display results
            stats = result['stats']
            report = f"""✅ Update Complete!

Backup: {Path(result['backup_path']).name}
Files Processed: {stats['files_processed']}
Fixes Applied: {stats['fixes_applied']}
Warnings: {stats['warnings']}
Errors: {stats['errors']}

Top Fixes:"""
            
            for r in result['results'][:5]:
                if r['fixes']:
                    report += f"\n• {Path(r['file']).name}: {len(r['fixes'])} fixes"
            
            self.update_results.setText(report)
            self.update_status.setText("✓ Update complete!")
            self.update_status.setStyleSheet("color: #22c55e; font-size: 11px;")
            
        except Exception as e:
            self.update_status.setText(f"✗ Error: {str(e)}")
            self.update_status.setStyleSheet("color: #ef4444; font-size: 11px;")
    
    def on_project_change(self, index):
        project_id = self.project_combo.currentData()
        project = PROJECTS[project_id]
        
        self.meta_title.setText(f"{project['name']} - {project['type']}")
        self.meta_desc.setText(project['description'])
        self.schema_name.setText(project['name'])
        self.schema_url.setText(f"https://{project['domain']}")
        self.schema_type.setCurrentText(project['schema_type'])
        
        local_path = project.get('local_path')
        has_local = local_path is not None and Path(local_path).exists()
        
        if has_local:
            self.update_status.setText(f"✓ Local files ready\n{str(local_path)[:40]}...")
            self.update_status.setStyleSheet("color: #22c55e; font-size: 11px;")
            self.update_btn.setEnabled(True)
        else:
            self.update_status.setText("✗ No local files\nSwitch to Adaryus, NCRJ, AdvertiseWV, Dark Rose, or MDI")
            self.update_status.setStyleSheet("color: #ef4444; font-size: 11px;")
            self.update_btn.setEnabled(False)
        
        self.validate_meta()


class SEOBOTDesktopPro(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SEOBOT Desktop Pro - Knowledge Engine & Auto-Updater")
        self.setMinimumSize(1800, 1100)
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sidebar with knowledge engine
        self.sidebar = KnowledgePanel()
        splitter.addWidget(self.sidebar)
        
        # Preview area
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(12, 12, 12, 12)
        
        # Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("background: #141416; border-radius: 8px;")
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(12, 8, 12, 8)
        
        tb_layout.addWidget(QLabel("📺 Live Previews"))
        tb_layout.addStretch()
        
        layout_2x3 = QPushButton("2×3")
        layout_2x3.setObjectName("secondary")
        layout_2x3.clicked.connect(lambda: self.set_layout(2, 3))
        tb_layout.addWidget(layout_2x3)
        
        layout_3x2 = QPushButton("3×2")
        layout_3x2.setObjectName("secondary")
        layout_3x2.clicked.connect(lambda: self.set_layout(3, 2))
        tb_layout.addWidget(layout_3x2)
        
        reload_btn = QPushButton("🔄 Reload All")
        reload_btn.clicked.connect(self.reload_all)
        tb_layout.addWidget(reload_btn)
        
        preview_layout.addWidget(toolbar)
        
        # Previews grid
        self.previews_widget = QWidget()
        self.previews_layout = QGridLayout(self.previews_widget)
        self.previews_layout.setSpacing(12)
        
        self.preview_widgets = {}
        for pid, pdata in PROJECTS.items():
            preview = PreviewWidget(pid, pdata)
            self.preview_widgets[pid] = preview
        
        self.set_layout(2, 3)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.previews_widget)
        scroll.setStyleSheet("background: #0a0a0b; border: none;")
        
        preview_layout.addWidget(scroll, 1)
        
        splitter.addWidget(preview_widget)
        splitter.setSizes([380, 1420])
        
        main_layout.addWidget(splitter)
        
        self.statusBar().showMessage("SEOBOT Desktop Pro Ready | 5 Books Loaded | 6 Projects | Knowledge Engine Active")
    
    def set_layout(self, cols, rows):
        while self.previews_layout.count():
            item = self.previews_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        for i, pid in enumerate(PROJECTS.keys()):
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
    
    font = QFont("Inter", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    
    window = SEOBOTDesktopPro()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

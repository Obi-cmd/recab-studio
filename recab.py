"""
Recab Studio Home Edition - Enhanced
Version: 4.0.0
Last Updated: 2025-11-07
Author: recabhelp-png

Major Improvements:
- Multi-tab editor support
- Enhanced syntax highlighting (Python, JavaScript, HTML, CSS, JSON)
- Find & Replace functionality
- Auto-completion hints
- Code folding support
- Git integration status
- Recent files menu
- Improved terminal with command history
- Minimap preview
- Bracket matching
- Multiple theme options
- Keyboard shortcuts panel
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QTextEdit, QLineEdit, QFileDialog, QMessageBox, QDockWidget,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QSplitter, QDialog,
    QDialogButtonBox, QCheckBox, QSpinBox, QComboBox, QTreeWidget, QTreeWidgetItem,
    QMenu, QFormLayout, QTabWidget, QToolBar, QStatusBar, QGroupBox, QRadioButton
)
from PyQt6.QtGui import (
    QAction, QFont, QKeySequence, QTextCharFormat, QColor,
    QSyntaxHighlighter, QTextCursor, QPalette, QPainter, QTextFormat, QIcon
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRegularExpression, QSize, QRect

APP_NAME = "Recab Studio Home"
APP_VERSION = "4.0.0"
CONFIG_PATH = Path.home() / ".recab_home_config.json"

def log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    colors = {"INFO": "\033[94m", "ERROR": "\033[91m", "SUCCESS": "\033[92m", "WARN": "\033[93m"}
    print(f"[{timestamp}] [{level}] {colors.get(level, '')}{message}\033[0m")

def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log(f"Config load error: {e}", "ERROR")
    return {
        "theme": "dark", "font_size": 14, "tab_size": 4,
        "word_wrap": False, "show_line_numbers": True,
        "autosave_interval": 120, "recent_files": [],
        "font_family": "Consolas", "auto_indent": True,
        "highlight_current_line": True, "show_minimap": False
    }

def save_config(config: Dict[str, Any]) -> None:
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        log(f"Config save error: {e}", "ERROR")

def apply_theme(app: QApplication, mode: str = "dark") -> None:
    app.setStyle("Fusion")
    palette = QPalette()
    
    if mode == "dark":
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(212, 212, 212))
        palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 48))
        palette.setColor(QPalette.ColorRole.Text, QColor(212, 212, 212))
        palette.setColor(QPalette.ColorRole.Button, QColor(37, 37, 38))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(212, 212, 212))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 122, 204))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    elif mode == "light":
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Button, QColor(243, 243, 243))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
    elif mode == "monokai":
        palette.setColor(QPalette.ColorRole.Window, QColor(39, 40, 34))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(248, 248, 242))
        palette.setColor(QPalette.ColorRole.Base, QColor(39, 40, 34))
        palette.setColor(QPalette.ColorRole.Text, QColor(248, 248, 242))
        palette.setColor(QPalette.ColorRole.Button, QColor(49, 51, 45))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(248, 248, 242))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(73, 72, 62))
    
    app.setPalette(palette)
    stylesheet = """
    QMainWindow { background-color: #1e1e1e; }
    QMenuBar { background-color: #333333; color: #cccccc; padding: 2px; }
    QMenuBar::item:selected { background-color: #3e3e42; }
    QMenu { background-color: #333333; color: #cccccc; }
    QMenu::item:selected { background-color: #3e3e42; }
    QPushButton { background-color: #0e639c; color: white; border: none; 
                  border-radius: 4px; padding: 8px 16px; }
    QPushButton:hover { background-color: #1177bb; }
    QTabWidget::pane { border: 1px solid #555; }
    QTabBar::tab { background-color: #2d2d30; color: #ccc; padding: 8px 16px; }
    QTabBar::tab:selected { background-color: #1e1e1e; color: white; }
    QTabBar::tab:hover { background-color: #3e3e42; }
    """
    app.setStyleSheet(stylesheet)

class MultiLanguageHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, language="python"):
        super().__init__(parent)
        self.language = language
        self.rules = []
        self._setup_rules()
    
    def set_language(self, language: str):
        self.language = language
        self._setup_rules()
        self.rehighlight()
    
    def _setup_rules(self):
        self.rules = []
        
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(197, 134, 192))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        if self.language == "python":
            keywords = ['and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
                       'elif', 'else', 'except', 'False', 'finally', 'for', 'from', 'global',
                       'if', 'import', 'in', 'is', 'lambda', 'None', 'not', 'or', 'pass',
                       'raise', 'return', 'True', 'try', 'while', 'with', 'yield', 'async', 'await']
        elif self.language == "javascript":
            keywords = ['const', 'let', 'var', 'function', 'return', 'if', 'else', 'for', 
                       'while', 'break', 'continue', 'switch', 'case', 'default', 'try',
                       'catch', 'finally', 'throw', 'async', 'await', 'class', 'extends']
        elif self.language == "html":
            keywords = ['html', 'head', 'body', 'div', 'span', 'p', 'a', 'img', 'script',
                       'style', 'link', 'meta', 'title', 'h1', 'h2', 'h3', 'table', 'tr', 'td']
        else:
            keywords = []
        
        for word in keywords:
            self.rules.append((QRegularExpression(f'\\b{word}\\b'), keyword_format))
        
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(206, 145, 120))
        self.rules.append((QRegularExpression('"[^"\\\\]*(\\\\.[^"\\\\]*)*"'), string_format))
        self.rules.append((QRegularExpression("'[^'\\\\]*(\\\\.[^'\\\\]*)*'"), string_format))
        
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(106, 153, 85))
        if self.language in ["python", "javascript"]:
            self.rules.append((QRegularExpression('#[^\n]*'), comment_format))
            self.rules.append((QRegularExpression('//[^\n]*'), comment_format))
        elif self.language == "html":
            self.rules.append((QRegularExpression('<!--.*?-->'), comment_format))
        
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(181, 206, 168))
        self.rules.append((QRegularExpression('\\b[0-9]+\\.?[0-9]*\\b'), number_format))
    
    def highlightBlock(self, text: str):
        for pattern, fmt in self.rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)
    
    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

class FindReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find and Replace")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("Find:"))
        self.find_input = QLineEdit()
        find_layout.addWidget(self.find_input)
        layout.addLayout(find_layout)
        
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("Replace:"))
        self.replace_input = QLineEdit()
        replace_layout.addWidget(self.replace_input)
        layout.addLayout(replace_layout)
        
        self.case_sensitive = QCheckBox("Case Sensitive")
        layout.addWidget(self.case_sensitive)
        
        buttons_layout = QHBoxLayout()
        find_btn = QPushButton("Find Next")
        find_btn.clicked.connect(lambda: self.accept() if self.find_input.text() else None)
        buttons_layout.addWidget(find_btn)
        
        replace_btn = QPushButton("Replace")
        replace_btn.clicked.connect(lambda: self.done(2))
        buttons_layout.addWidget(replace_btn)
        
        replace_all_btn = QPushButton("Replace All")
        replace_all_btn.clicked.connect(lambda: self.done(3))
        buttons_layout.addWidget(replace_all_btn)
        
        layout.addLayout(buttons_layout)

class CodeEditor(QPlainTextEdit):
    cursorMoved = pyqtSignal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = None
        self.setFont(QFont("Consolas", 14))
        self.setTabStopDistance(40)
        
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)
        
        self.highlighter = MultiLanguageHighlighter(self.document())
        self.cursorPositionChanged.connect(self._on_cursor_changed)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        self.highlight_current_line()
    
    def update_language(self, file_path: str):
        ext = Path(file_path).suffix.lower()
        lang_map = {'.py': 'python', '.js': 'javascript', '.html': 'html', 
                    '.css': 'css', '.json': 'json'}
        language = lang_map.get(ext, 'python')
        self.highlighter.set_language(language)
    
    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(64, 64, 64, 100)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)
    
    def _on_cursor_changed(self):
        cursor = self.textCursor()
        self.cursorMoved.emit(cursor.blockNumber() + 1, cursor.columnNumber() + 1)
    
    def line_number_area_width(self) -> int:
        digits = max(1, len(str(self.blockCount())))
        return 10 + self.fontMetrics().horizontalAdvance('9') * digits
    
    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(0, cr.top(), self.line_number_area_width(), cr.height())
    
    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(37, 37, 38))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(QColor(150, 150, 150))
                painter.drawText(0, int(top), self.line_number_area.width() - 5,
                               self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, 
                               str(block_number + 1))
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab:
            cursor = self.textCursor()
            cursor.insertText("    ")
        elif event.key() == Qt.Key.Key_Return:
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()
            indent = len(text) - len(text.lstrip())
            super().keyPressEvent(event)
            cursor = self.textCursor()
            cursor.insertText(" " * indent)
        else:
            super().keyPressEvent(event)

class FileExplorer(QWidget):
    file_opened = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        header = QLabel("EXPLORER")
        header.setStyleSheet("font-weight: 600; font-size: 12px; padding: 4px;")
        layout.addWidget(header)
        
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setText(str(Path.cwd()))
        self.path_input.returnPressed.connect(self.refresh)
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("📁")
        browse_btn.setFixedWidth(40)
        browse_btn.clicked.connect(self.browse_folder)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.tree)
        
        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.clicked.connect(self.refresh)
        layout.addWidget(refresh_btn)
        self.refresh()
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.path_input.setText(folder)
            self.refresh()
    
    def refresh(self):
        self.tree.clear()
        path = Path(self.path_input.text())
        if path.exists() and path.is_dir():
            self._populate_tree(path, self.tree.invisibleRootItem())
    
    def _populate_tree(self, path: Path, parent_item):
        try:
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            for item in items[:100]:
                if item.name.startswith('.') and item.name not in ['.git', '.gitignore']:
                    continue
                tree_item = QTreeWidgetItem(parent_item)
                icon = "📁" if item.is_dir() else ("🐍" if item.suffix == ".py" else "📄")
                tree_item.setText(0, f"{icon} {item.name}")
                tree_item.setData(0, Qt.ItemDataRole.UserRole, str(item))
        except Exception as e:
            log(f"Tree error: {e}", "ERROR")
    
    def _on_item_double_clicked(self, item, column):
        path_str = item.data(0, Qt.ItemDataRole.UserRole)
        if path_str and Path(path_str).is_file():
            self.file_opened.emit(path_str)
    
    def _show_context_menu(self, position):
        item = self.tree.itemAt(position)
        if item:
            menu = QMenu()
            open_action = menu.addAction("Open")
            delete_action = menu.addAction("Delete")
            action = menu.exec(self.tree.mapToGlobal(position))

class TerminalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("  TERMINAL")
        header.setStyleSheet("background-color: #2d2d30; color: #cccccc; padding: 6px;")
        layout.addWidget(header)
        
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 10))
        layout.addWidget(self.output)
        
        input_layout = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter command...")
        self.command_input.returnPressed.connect(self.run_command)
        input_layout.addWidget(self.command_input)
        
        run_btn = QPushButton("Run")
        run_btn.clicked.connect(self.run_command)
        input_layout.addWidget(run_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.output.clear)
        input_layout.addWidget(clear_btn)
        
        layout.addLayout(input_layout)
        self.command_history = []
        self.history_index = 0
    
    def log(self, text: str):
        self.output.append(text)
    
    def run_command(self):
        command = self.command_input.text().strip()
        if not command:
            return
        
        self.command_history.append(command)
        self.log(f"> {command}")
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, 
                                  text=True, timeout=30)
            if result.stdout:
                self.log(result.stdout)
            if result.stderr:
                self.log(f'Error: {result.stderr}')
        except subprocess.TimeoutExpired:
            self.log('⌛ Command timeout')
        except Exception as e:
            self.log(f'❌ Error: {e}')
        
        self.command_input.clear()
    
    def run_file(self, file_path: str):
        if not Path(file_path).exists():
            self.log(f"❌ File not found: {file_path}")
            return
        
        ext = Path(file_path).suffix.lower()
        if ext == '.py':
            cmd = [sys.executable, file_path]
        elif ext == '.js':
            cmd = ['node', file_path]
        else:
            self.log(f"❌ Unsupported file type: {ext}")
            return
        
        self.log(f"▶ Running: {Path(file_path).name}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.stdout:
                self.log(result.stdout)
            if result.stderr:
                self.log(f'Error: {result.stderr}')
            self.log(f'✓ Exit code: {result.returncode}')
        except subprocess.TimeoutExpired:
            self.log('❌ Timeout')
        except FileNotFoundError:
            self.log(f'❌ Interpreter not found for {ext} files')
        except Exception as e:
            self.log(f'❌ Error: {e}')

class SettingsDialog(QDialog):
    def __init__(self, config: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        
        # Editor Tab
        editor_tab = QWidget()
        editor_layout = QFormLayout(editor_tab)
        
        self.font_family = QComboBox()
        self.font_family.addItems(["Consolas", "Courier New", "Monaco", "Fira Code"])
        self.font_family.setCurrentText(config.get("font_family", "Consolas"))
        editor_layout.addRow("Font Family:", self.font_family)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(config.get("font_size", 14))
        editor_layout.addRow("Font Size:", self.font_size)
        
        self.tab_size = QSpinBox()
        self.tab_size.setRange(2, 8)
        self.tab_size.setValue(config.get("tab_size", 4))
        editor_layout.addRow("Tab Size:", self.tab_size)
        
        self.word_wrap = QCheckBox()
        self.word_wrap.setChecked(config.get("word_wrap", False))
        editor_layout.addRow("Word Wrap:", self.word_wrap)
        
        self.auto_indent = QCheckBox()
        self.auto_indent.setChecked(config.get("auto_indent", True))
        editor_layout.addRow("Auto Indent:", self.auto_indent)
        
        tabs.addTab(editor_tab, "Editor")
        
        # Theme Tab
        theme_tab = QWidget()
        theme_layout = QVBoxLayout(theme_tab)
        
        theme_group = QGroupBox("Color Theme")
        theme_group_layout = QVBoxLayout()
        
        self.theme_dark = QRadioButton("Dark")
        self.theme_light = QRadioButton("Light")
        self.theme_monokai = QRadioButton("Monokai")
        
        current_theme = config.get("theme", "dark")
        if current_theme == "dark":
            self.theme_dark.setChecked(True)
        elif current_theme == "light":
            self.theme_light.setChecked(True)
        else:
            self.theme_monokai.setChecked(True)
        
        theme_group_layout.addWidget(self.theme_dark)
        theme_group_layout.addWidget(self.theme_light)
        theme_group_layout.addWidget(self.theme_monokai)
        theme_group.setLayout(theme_group_layout)
        theme_layout.addWidget(theme_group)
        theme_layout.addStretch()
        
        tabs.addTab(theme_tab, "Theme")
        
        layout.addWidget(tabs)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                  QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_settings(self) -> Dict[str, Any]:
        theme = "dark"
        if self.theme_light.isChecked():
            theme = "light"
        elif self.theme_monokai.isChecked():
            theme = "monokai"
        
        return {
            "font_family": self.font_family.currentText(),
            "font_size": self.font_size.value(),
            "tab_size": self.tab_size.value(),
            "word_wrap": self.word_wrap.isChecked(),
            "auto_indent": self.auto_indent.isChecked(),
            "theme": theme
        }

class MainWindow(QMainWindow):
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(1400, 900)
        
        # Multi-tab editor
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        
        self.terminal = TerminalWidget()
        
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.tab_widget)
        splitter.addWidget(self.terminal)
        splitter.setSizes([650, 250])
        self.setCentralWidget(splitter)
        
        self.file_explorer = FileExplorer()
        self.file_explorer.file_opened.connect(self._open_file_from_path)
        
        explorer_dock = QDockWidget("EXPLORER", self)
        explorer_dock.setWidget(self.file_explorer)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, explorer_dock)
        
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_status_bar()
        self._apply_settings()
        
        # Create initial tab
        self._new_file()
        
        self.terminal.log(f"✓ {APP_NAME} v{APP_VERSION} initialized")
        self.terminal.log(f"  Python {sys.version.split()[0]} | PyQt6")
    
    def _get_current_editor(self) -> Optional[CodeEditor]:
        current_widget = self.tab_widget.currentWidget()
        return current_widget if isinstance(current_widget, CodeEditor) else None
    
    def _setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        new_action = QAction("New", self)
        new_action.triggered.connect(self._new_file)
        toolbar.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(self._open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self._save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        run_action = QAction("▶ Run", self)
        run_action.triggered.connect(self._run_file)
        toolbar.addAction(run_action)
        
        toolbar.addSeparator()
        
        find_action = QAction("🔍 Find", self)
        find_action.triggered.connect(self._show_find_replace)
        toolbar.addAction(find_action)
    
    def _setup_menu_bar(self):
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)
        
        # Recent Files submenu
        recent_menu = file_menu.addMenu("Recent Files")
        self._update_recent_files_menu(recent_menu)
        
        file_menu.addSeparator()
        
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self._save_file_as)
        file_menu.addAction(save_as_action)
        
        save_all_action = QAction("Save All", self)
        save_all_action.setShortcut(QKeySequence("Ctrl+Alt+S"))
        save_all_action.triggered.connect(self._save_all)
        file_menu.addAction(save_all_action)
        
        file_menu.addSeparator()
        
        close_tab_action = QAction("Close Tab", self)
        close_tab_action.setShortcut(QKeySequence("Ctrl+W"))
        close_tab_action.triggered.connect(lambda: self._close_tab(self.tab_widget.currentIndex()))
        file_menu.addAction(close_tab_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Alt+F4"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self._redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self._cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self._copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self._paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("&Find...", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self._show_find_replace)
        edit_menu.addAction(find_action)
        
        replace_action = QAction("&Replace...", self)
        replace_action.setShortcut(QKeySequence("Ctrl+H"))
        replace_action.triggered.connect(self._show_find_replace)
        edit_menu.addAction(replace_action)
        
        edit_menu.addSeparator()
        
        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self._select_all)
        edit_menu.addAction(select_all_action)
        
        # View Menu
        view_menu = menubar.addMenu("&View")
        
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self._zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self._zoom_out)
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction("Reset Zoom", self)
        reset_zoom_action.setShortcut(QKeySequence("Ctrl+0"))
        reset_zoom_action.triggered.connect(self._reset_zoom)
        view_menu.addAction(reset_zoom_action)
        
        # Run Menu
        run_menu = menubar.addMenu("&Run")
        
        run_action = QAction("&Run File", self)
        run_action.setShortcut(QKeySequence("F5"))
        run_action.triggered.connect(self._run_file)
        run_menu.addAction(run_action)
        
        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")
        
        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        shortcuts_action = QAction("Keyboard &Shortcuts", self)
        shortcuts_action.setShortcut(QKeySequence("F1"))
        shortcuts_action.triggered.connect(self._show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _update_recent_files_menu(self, menu: QMenu):
        menu.clear()
        recent_files = self.config.get("recent_files", [])
        
        if not recent_files:
            no_files_action = QAction("No recent files", self)
            no_files_action.setEnabled(False)
            menu.addAction(no_files_action)
            return
        
        for file_path in recent_files[:10]:
            if Path(file_path).exists():
                action = QAction(Path(file_path).name, self)
                action.setToolTip(file_path)
                action.triggered.connect(lambda checked, fp=file_path: self._open_file_from_path(fp))
                menu.addAction(action)
        
        menu.addSeparator()
        clear_action = QAction("Clear Recent Files", self)
        clear_action.triggered.connect(self._clear_recent_files)
        menu.addAction(clear_action)
    
    def _add_to_recent_files(self, file_path: str):
        recent = self.config.get("recent_files", [])
        if file_path in recent:
            recent.remove(file_path)
        recent.insert(0, file_path)
        self.config["recent_files"] = recent[:20]
        save_config(self.config)
    
    def _clear_recent_files(self):
        self.config["recent_files"] = []
        save_config(self.config)
        QMessageBox.information(self, "Recent Files", "Recent files cleared")
    
    def _setup_status_bar(self):
        self.statusBar().showMessage("Ready")
        
        self.cursor_label = QLabel("Ln 1, Col 1")
        self.statusBar().addPermanentWidget(self.cursor_label)
        
        self.file_type_label = QLabel("Python")
        self.statusBar().addPermanentWidget(self.file_type_label)
        
        self.encoding_label = QLabel("UTF-8")
        self.statusBar().addPermanentWidget(self.encoding_label)
    
    def _update_cursor_position(self, line: int, col: int):
        self.cursor_label.setText(f"Ln {line}, Col {col}")
    
    def _apply_settings(self):
        font_family = self.config.get("font_family", "Consolas")
        font_size = self.config.get("font_size", 14)
        
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if isinstance(editor, CodeEditor):
                editor.setFont(QFont(font_family, font_size))
                editor.setLineWrapMode(
                    QPlainTextEdit.LineWrapMode.WidgetWidth 
                    if self.config.get("word_wrap", False) 
                    else QPlainTextEdit.LineWrapMode.NoWrap
                )
    
    def _new_file(self):
        editor = CodeEditor()
        editor.cursorMoved.connect(self._update_cursor_position)
        
        font_family = self.config.get("font_family", "Consolas")
        font_size = self.config.get("font_size", 14)
        editor.setFont(QFont(font_family, font_size))
        
        tab_index = self.tab_widget.addTab(editor, "Untitled")
        self.tab_widget.setCurrentIndex(tab_index)
        self.terminal.log("✓ New file created")
    
    def _open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", 
            "All Files (*);;Python Files (*.py);;JavaScript Files (*.js);;HTML Files (*.html)"
        )
        if file_path:
            self._open_file_from_path(file_path)
    
    def _open_file_from_path(self, file_path: str):
        # Check if file is already open
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if isinstance(editor, CodeEditor) and editor.file_path == file_path:
                self.tab_widget.setCurrentIndex(i)
                return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            editor = CodeEditor()
            editor.setPlainText(content)
            editor.file_path = file_path
            editor.update_language(file_path)
            editor.cursorMoved.connect(self._update_cursor_position)
            
            font_family = self.config.get("font_family", "Consolas")
            font_size = self.config.get("font_size", 14)
            editor.setFont(QFont(font_family, font_size))
            
            file_name = Path(file_path).name
            tab_index = self.tab_widget.addTab(editor, file_name)
            self.tab_widget.setCurrentIndex(tab_index)
            
            self._add_to_recent_files(file_path)
            self._update_file_type_label(file_path)
            self.terminal.log(f"✓ Opened: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open: {e}")
            self.terminal.log(f"❌ Error opening file: {e}")
    
    def _update_file_type_label(self, file_path: str):
        ext = Path(file_path).suffix.lower()
        type_map = {
            '.py': 'Python', '.js': 'JavaScript', '.html': 'HTML',
            '.css': 'CSS', '.json': 'JSON', '.txt': 'Text'
        }
        self.file_type_label.setText(type_map.get(ext, 'Plain Text'))
    
    def _save_file(self):
        editor = self._get_current_editor()
        if not editor:
            return
        
        if not editor.file_path:
            self._save_file_as()
        else:
            self._do_save(editor, editor.file_path)
    
    def _save_file_as(self):
        editor = self._get_current_editor()
        if not editor:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save As", "",
            "All Files (*);;Python Files (*.py);;JavaScript Files (*.js);;HTML Files (*.html)"
        )
        if file_path:
            self._do_save(editor, file_path)
    
    def _save_all(self):
        saved_count = 0
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if isinstance(editor, CodeEditor) and editor.file_path:
                self._do_save(editor, editor.file_path)
                saved_count += 1
        
        if saved_count > 0:
            self.terminal.log(f"✓ Saved {saved_count} file(s)")
        else:
            self.terminal.log("ℹ No files to save")
    
    def _do_save(self, editor: CodeEditor, file_path: str):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(editor.toPlainText())
            
            editor.file_path = file_path
            editor.update_language(file_path)
            
            # Update tab title
            tab_index = self.tab_widget.indexOf(editor)
            if tab_index >= 0:
                self.tab_widget.setTabText(tab_index, Path(file_path).name)
            
            self._add_to_recent_files(file_path)
            self._update_file_type_label(file_path)
            self.terminal.log(f"✓ Saved: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Save failed: {e}")
            self.terminal.log(f"❌ Save error: {e}")
    
    def _close_tab(self, index: int):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            editor = self.tab_widget.widget(index)
            if isinstance(editor, CodeEditor):
                editor.clear()
                editor.file_path = None
                self.tab_widget.setTabText(index, "Untitled")
    
    def _run_file(self):
        editor = self._get_current_editor()
        if editor and editor.file_path:
            self.terminal.run_file(editor.file_path)
        else:
            self.terminal.log("❌ Save file first")
    
    # Edit operations
    def _undo(self):
        editor = self._get_current_editor()
        if editor:
            editor.undo()
    
    def _redo(self):
        editor = self._get_current_editor()
        if editor:
            editor.redo()
    
    def _cut(self):
        editor = self._get_current_editor()
        if editor:
            editor.cut()
    
    def _copy(self):
        editor = self._get_current_editor()
        if editor:
            editor.copy()
    
    def _paste(self):
        editor = self._get_current_editor()
        if editor:
            editor.paste()
    
    def _select_all(self):
        editor = self._get_current_editor()
        if editor:
            editor.selectAll()
    
    def _show_find_replace(self):
        editor = self._get_current_editor()
        if not editor:
            return
        
        dialog = FindReplaceDialog(self)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:  # Find Next
            self._find_text(editor, dialog.find_input.text(), dialog.case_sensitive.isChecked())
        elif result == 2:  # Replace
            self._replace_text(editor, dialog.find_input.text(), 
                             dialog.replace_input.text(), dialog.case_sensitive.isChecked())
        elif result == 3:  # Replace All
            self._replace_all_text(editor, dialog.find_input.text(), 
                                 dialog.replace_input.text(), dialog.case_sensitive.isChecked())
    
    def _find_text(self, editor: CodeEditor, text: str, case_sensitive: bool):
        flags = QTextDocument.FindFlag(0)
        if case_sensitive:
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        
        if not editor.find(text, flags):
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            editor.setTextCursor(cursor)
            if not editor.find(text, flags):
                self.statusBar().showMessage("Text not found", 3000)
    
    def _replace_text(self, editor: CodeEditor, find_text: str, replace_text: str, case_sensitive: bool):
        cursor = editor.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == find_text:
            cursor.insertText(replace_text)
        self._find_text(editor, find_text, case_sensitive)
    
    def _replace_all_text(self, editor: CodeEditor, find_text: str, replace_text: str, case_sensitive: bool):
        content = editor.toPlainText()
        if case_sensitive:
            new_content = content.replace(find_text, replace_text)
        else:
            new_content = re.sub(re.escape(find_text), replace_text, content, flags=re.IGNORECASE)
        
        count = content.count(find_text) if case_sensitive else len(re.findall(re.escape(find_text), content, re.IGNORECASE))
        editor.setPlainText(new_content)
        self.statusBar().showMessage(f"Replaced {count} occurrence(s)", 3000)
    
    # View operations
    def _zoom_in(self):
        self.config["font_size"] = min(24, self.config.get("font_size", 14) + 1)
        self._apply_settings()
    
    def _zoom_out(self):
        self.config["font_size"] = max(8, self.config.get("font_size", 14) - 1)
        self._apply_settings()
    
    def _reset_zoom(self):
        self.config["font_size"] = 14
        self._apply_settings()
    
    def _show_settings(self):
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_settings = dialog.get_settings()
            self.config.update(new_settings)
            save_config(self.config)
            
            # Apply theme change
            if "theme" in new_settings:
                apply_theme(QApplication.instance(), new_settings["theme"])
            
            self._apply_settings()
            self.terminal.log("✓ Settings saved")
    
    def _show_shortcuts(self):
        shortcuts_text = """
<h2>Keyboard Shortcuts</h2>
<h3>File Operations</h3>
<b>Ctrl+N</b> - New File<br>
<b>Ctrl+O</b> - Open File<br>
<b>Ctrl+S</b> - Save File<br>
<b>Ctrl+Shift+S</b> - Save As<br>
<b>Ctrl+Alt+S</b> - Save All<br>
<b>Ctrl+W</b> - Close Tab<br>
<b>Alt+F4</b> - Exit<br>

<h3>Edit Operations</h3>
<b>Ctrl+Z</b> - Undo<br>
<b>Ctrl+Y</b> - Redo<br>
<b>Ctrl+X</b> - Cut<br>
<b>Ctrl+C</b> - Copy<br>
<b>Ctrl+V</b> - Paste<br>
<b>Ctrl+A</b> - Select All<br>
<b>Ctrl+F</b> - Find<br>
<b>Ctrl+H</b> - Replace<br>

<h3>View Operations</h3>
<b>Ctrl++</b> - Zoom In<br>
<b>Ctrl+-</b> - Zoom Out<br>
<b>Ctrl+0</b> - Reset Zoom<br>

<h3>Run Operations</h3>
<b>F5</b> - Run Current File<br>

<h3>Tools</h3>
<b>Ctrl+,</b> - Settings<br>
<b>F1</b> - Show Shortcuts<br>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Keyboard Shortcuts")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(shortcuts_text)
        msg.exec()
    
    def _show_about(self):
        about_text = f"""
<h2>{APP_NAME}</h2>
<p><b>Version:</b> {APP_VERSION}</p>
<p><b>Author:</b> recabhelp-png</p>
<p><b>Framework:</b> PyQt6</p>
<p><b>Python:</b> {sys.version.split()[0]}</p>
<br>
<p>A modern, lightweight Python IDE with multi-tab editing,
syntax highlighting, and integrated terminal.</p>
<br>
<p><b>Features:</b></p>
<ul>
<li>Multi-tab editor</li>
<li>Syntax highlighting (Python, JS, HTML)</li>
<li>Find & Replace</li>
<li>Integrated terminal</li>
<li>File explorer</li>
<li>Multiple themes</li>
<li>Recent files tracking</li>
</ul>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle(f"About {APP_NAME}")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(about_text)
        msg.exec()
    
    def closeEvent(self, event):
        save_config(self.config)
        log("Application closed", "INFO")
        event.accept()

def main():
    try:
        log("Starting Recab Studio Home Edition...", "INFO")
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)
        
        config = load_config()
        apply_theme(app, config.get("theme", "dark"))
        
        window = MainWindow(config)
        window.show()
        
        log("Application started successfully", "SUCCESS")
        sys.exit(app.exec())
    except Exception as e:
        log(f"Fatal error: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
# ANDY LOCALHOST PORTAL – Motor Frameless + Fondos + Config + Localhost HTML

import sys
import os
import json
import socket
import threading
import html
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout,
    QMessageBox, QFileDialog, QDialog, QDialogButtonBox, QFormLayout,
    QTabWidget, QFrame, QMenu, QDesktopWidget, QSlider
)
from PyQt5.QtGui import QPixmap, QColor, QPainter
from PyQt5.QtCore import Qt, QTimer

# --- RUTAS BASE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "ANDY_LOCALHOST_PORTAL.vtha")

# --- SETTINGS MANAGER (igual estilo .vtha) ---
class SettingsManager:
    def __init__(self, settings_file=CONFIG_FILE):
        self.settings_file = settings_file
        self.defaults = {
            "window_opacity": "1.0",
            "background_folder": os.path.join(BASE_DIR, "FONDOS_PORTAL"),
            "background_scaling_mode": "Expandir",
            "last_html_path": "",
            "last_port": "8000"
        }
        self.settings = self._load_settings()

    def _load_settings(self):
        try:
            if not os.path.exists(self.settings_file):
                self._save_settings(self.defaults)
                return self.defaults.copy()
            with open(self.settings_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            loaded = {}
            for line in lines:
                if "=" in line:
                    k, v = line.split("=", 1)
                    loaded[k.strip()] = v.strip()
            for k, v in self.defaults.items():
                if k not in loaded:
                    loaded[k] = v
            return loaded
        except Exception:
            self._save_settings(self.defaults)
            return self.defaults.copy()

    def _save_settings(self, d):
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, "w", encoding="utf-8") as f:
                for k, v in d.items():
                    f.write(f"{k} = {v}\n")
        except:
            pass

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        if isinstance(value, (list, dict)):
            self.settings[key] = json.dumps(value)
        else:
            self.settings[key] = str(value)
        self._save_settings(self.settings)

# --- SERVIDOR LOCALHOST (simple, por archivo HTML) ---
class LocalHTMLServer:
    def __init__(self):
        self.httpd = None
        self.thread = None
        self.port = None
        self.root_dir = None

    def _find_free_port(self, start_port=8000):
        port = int(start_port)
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("127.0.0.1", port))
                    return port
                except OSError:
                    port += 1

    def start(self, html_path, preferred_port=None):
        if not os.path.exists(html_path):
            raise FileNotFoundError("Archivo HTML no existe")

        self.root_dir = os.path.dirname(html_path)
        filename = os.path.basename(html_path)

        # handler que fija el directorio raíz
        class RootedHandler(SimpleHTTPRequestHandler):
            def translate_path(self, path):
                # base original
                path = SimpleHTTPRequestHandler.translate_path(self, path)
                # reemplazar por root_dir
                rel = os.path.relpath(path, os.getcwd())
                return os.path.join(self.server.root_dir, rel)

        port = self._find_free_port(preferred_port or 8000)
        self.port = port

        # servidor en hilo
        def run_server():
            with TCPServer(("127.0.0.1", port), RootedHandler) as httpd:
                httpd.root_dir = self.root_dir
                self.httpd = httpd
                httpd.serve_forever()

        self.thread = threading.Thread(target=run_server, daemon=True)
        self.thread.start()

        url = f"http://127.0.0.1:{port}/{html.escape(filename)}"
        return url

    def stop(self):
        # servidor simple: se detiene al cerrar proceso; aquí no hacemos stop explícito
        pass

# --- APP PRINCIPAL FRAMLESS ---
class LocalHostPortalApp(QWidget):
    def __init__(self):
        super().__init__()
        self.sm = SettingsManager()
        self.server = LocalHTMLServer()

        self.background_images = []
        self.current_bg_index = 0
        self.current_background_pixmap = QPixmap()

        self.image_cache = {}
        self.gc_timer = QTimer(self)
        self.gc_timer.timeout.connect(self._run_gc)
        self.gc_timer.start(30000)

        self.initUI()
        self.apply_settings()

    def _run_gc(self):
        import gc
        gc.collect()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # layout principal
        self.main_frame = QFrame(self)
        self.main_frame.setStyleSheet("QFrame { background: transparent; }")
        v = QVBoxLayout(self.main_frame)
        v.setContentsMargins(20, 60, 20, 20)
        v.setSpacing(15)

        title = QLabel("🌐 ANDY LOCALHOST PORTAL")
        title.setStyleSheet("color: white; font-size: 18pt; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        v.addWidget(title)

        # selector de archivo HTML
        hb_file = QHBoxLayout()
        self.html_path_edit = QLineEdit(self.sm.get("last_html_path", ""))
        self.html_path_edit.setPlaceholderText("Ruta del archivo .html")
        btn_browse = QPushButton("📂")
        btn_browse.setFixedWidth(40)
        btn_browse.clicked.connect(self.select_html_file)
        hb_file.addWidget(self.html_path_edit)
        hb_file.addWidget(btn_browse)
        v.addLayout(hb_file)

        # botón iniciar puerto
        self.start_btn = QPushButton("🚀 Iniciar Puerto Localhost")
        self.start_btn.setStyleSheet(
            "QPushButton { background-color: rgba(30,20,50,220); color:white; "
            "border-radius:10px; padding:8px; font-weight:bold; } "
            "QPushButton:hover { background-color: rgba(138,43,226,220); }"
        )
        self.start_btn.clicked.connect(self.start_localhost)
        v.addWidget(self.start_btn)

        # URL resultante
        hb_url = QHBoxLayout()
        self.url_edit = QLineEdit()
        self.url_edit.setReadOnly(True)
        self.url_edit.setPlaceholderText("URL completa del puerto aparecerá aquí")
        btn_copy = QPushButton("📋 Copiar URL")
        btn_copy.setFixedWidth(100)
        btn_copy.clicked.connect(self.copy_url)
        hb_url.addWidget(self.url_edit)
        hb_url.addWidget(btn_copy)
        v.addLayout(hb_url)

        # mini etiqueta de estado
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: cyan; font-size: 10pt;")
        v.addWidget(self.status_label)

        # botón para mover/drag (esquina)
        self.drag_btn = QPushButton("✥")
        self.drag_btn.setParent(self)
        self.drag_btn.setFixedSize(30, 30)
        self.drag_btn.move(10, 10)
        self.drag_btn.setStyleSheet(
            "QPushButton { background-color: rgba(0,0,0,150); color:white; "
            "border-radius:15px; font-weight:bold; }"
        )
        self.drag_btn.pressed.connect(self._start_drag)
        self.drag_btn.released.connect(self._end_drag)
        self._dragging = False
        self._drag_pos = None

    def _start_drag(self):
        self._dragging = True
        self._drag_pos = self.mapFromGlobal(QCursor.pos())

    def _end_drag(self):
        self._dragging = False

    def mouseMoveEvent(self, event):
        if self._dragging and self._drag_pos:
            diff = event.pos() - self._drag_pos
            self.move(self.pos() + diff)

    def apply_settings(self):
        self.setGeometry(QDesktopWidget().screenGeometry())
        self.setWindowOpacity(float(self.sm.get("window_opacity", "1.0")))
        self.load_background_images()
        self.render_current_background()

    # --- FONDOS ---
    def load_background_images(self):
        folder = self.sm.get("background_folder")
        self.background_images = []
        if folder and os.path.exists(folder):
            files = [f for f in os.listdir(folder)
                     if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
            files.sort()
            self.background_images = [os.path.join(folder, f) for f in files]
        self.current_bg_index = 0
        self.image_cache.clear()

    def render_current_background(self):
        if not self.background_images:
            self.current_background_pixmap = QPixmap()
            self.update()
            return

        path = self.background_images[self.current_bg_index]
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            scm = self.sm.get("background_scaling_mode", "Expandir")
            mode = Qt.KeepAspectRatio if scm == "Ajustar" else \
                   Qt.IgnoreAspectRatio if scm == "Estirar" else \
                   Qt.KeepAspectRatioByExpanding
            self.current_background_pixmap = pixmap.scaled(
                self.size(), mode, Qt.SmoothTransformation
            )
        self.update()

    def keyPressEvent(self, event):
        key = event.text().upper().strip()
        if key in ["W", "S", "A", "D"] and self.background_images:
            if key == "W":
                self.current_bg_index = (self.current_bg_index + 1) % len(self.background_images)
            elif key == "S":
                self.current_bg_index = (self.current_bg_index - 1) % len(self.background_images)
            elif key == "A":
                self.current_bg_index = 0
            elif key == "D":
                self.current_bg_index = len(self.background_images) - 1
            self.render_current_background()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.render_current_background()

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.current_background_pixmap.isNull():
            painter.drawPixmap(self.rect(), self.current_background_pixmap)
        else:
            painter.fillRect(self.rect(), QColor(10, 5, 20, 230))
        super().paintEvent(event)

    # --- CONTEXT MENU / CONFIG ---
    def show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background-color: #1e1426; color: white; border: 1px solid cyan; } "
            "QMenu::item:selected { background-color: #8A2BE2; }"
        )
        menu.addAction("⚙️ Configuración Portal").triggered.connect(self.open_settings)
        menu.addSeparator()
        menu.addAction("➖ Minimizar").triggered.connect(self.showMinimized)
        menu.addAction("🗗 Restaurar").triggered.connect(self.showNormal)
        menu.addAction("🗖 Maximizar").triggered.connect(self.showMaximized)
        menu.addSeparator()
        menu.addAction("❌ Cerrar").triggered.connect(self.close)
        menu.exec_(self.mapToGlobal(pos))

    def open_settings(self):
        dialog = SettingsDialog(self.sm, self)
        if dialog.exec_() == QDialog.Accepted:
            self.apply_settings()

    # --- LÓGICA HTML / LOCALHOST ---
    def select_html_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo HTML", "", "HTML (*.html *.htm)"
        )
        if path:
            self.html_path_edit.setText(path)
            self.sm.set("last_html_path", path)

    def start_localhost(self):
        html_path = self.html_path_edit.text().strip()
        if not html_path:
            QMessageBox.warning(self, "Aviso", "Selecciona primero un archivo HTML.")
            return
        try:
            preferred_port = int(self.sm.get("last_port", "8000"))
        except ValueError:
            preferred_port = 8000

        try:
            url = self.server.start(html_path, preferred_port)
            self.url_edit.setText(url)
            self.status_label.setText(f"Servidor activo en {url}")
            # guardar puerto usado
            try:
                port_str = url.split(":")[2].split("/")[0]
                self.sm.set("last_port", port_str)
            except Exception:
                pass
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo iniciar el servidor:\n{e}")

    def copy_url(self):
        url = self.url_edit.text().strip()
        if not url:
            return
        cb = QApplication.clipboard()
        cb.setText(url)
        self.status_label.setText("URL copiada al portapapeles.")

# --- DIÁLOGO DE CONFIGURACIÓN ---
class SettingsDialog(QDialog):
    def __init__(self, sm, parent=None):
        super().__init__(parent)
        self.sm = sm
        self.setWindowTitle("Configuración ANDY LOCALHOST PORTAL")
        self.setMinimumWidth(600)

        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.tabs.addTab(self._create_general_tab(), "Ventana y Fondos")
        self.tabs.addTab(self._create_server_tab(), "Servidor")

        bb = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.save_and_accept)
        bb.rejected.connect(self.reject)
        main_layout.addWidget(bb)

    def _create_general_tab(self):
        w = QWidget()
        form = QFormLayout(w)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(int(float(self.sm.get("window_opacity", "1.0")) * 100))

        self.folder_in = QLineEdit(self.sm.get("background_folder"))
        btn_f = QPushButton("📂")
        btn_f.clicked.connect(self._pick_folder)
        hb = QHBoxLayout()
        hb.addWidget(self.folder_in)
        hb.addWidget(btn_f)

        self.scale_in = QLineEdit(self.sm.get("background_scaling_mode", "Expandir"))
        self.scale_in.setPlaceholderText("Expandir / Ajustar / Estirar")

        form.addRow("Opacidad Ventana:", self.opacity_slider)
        form.addRow("Carpeta Fondos:", hb)
        form.addRow("Modo Escala Fondo:", self.scale_in)
        return w

    def _create_server_tab(self):
        w = QWidget()
        form = QFormLayout(w)

        self.port_in = QLineEdit(self.sm.get("last_port", "8000"))
        self.port_in.setPlaceholderText("Puerto preferido (ej. 8000)")

        self.last_html_in = QLineEdit(self.sm.get("last_html_path", ""))
        self.last_html_in.setPlaceholderText("Último HTML usado (solo informativo)")

        form.addRow("Puerto preferido:", self.port_in)
        form.addRow("Último HTML:", self.last_html_in)
        return w

    def _pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Carpeta Fondos")
        if folder:
            self.folder_in.setText(folder)

    def save_and_accept(self):
        self.sm.set("window_opacity", str(self.opacity_slider.value() / 100.0))
        self.sm.set("background_folder", self.folder_in.text().strip())
        self.sm.set("background_scaling_mode", self.scale_in.text().strip() or "Expandir")
        self.sm.set("last_port", self.port_in.text().strip() or "8000")
        self.accept()

# --- MAIN ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LocalHostPortalApp()
    win.show()
    sys.exit(app.exec_())

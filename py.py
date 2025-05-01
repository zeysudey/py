import sys
import cv2
import atexit
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSizePolicy
)
from PySide6.QtGui import QPainter, QPen, QImage, QPixmap
from PySide6.QtCore import Qt, QTimer


class CrosshairLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFixedSize(850, 500)
        self.frame = None

    def set_frame(self, frame):
        self.frame = frame
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.lightGray)

        if self.frame is not None:
            rgb_image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qimg = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg).scaled(self.size(), Qt.IgnoreAspectRatio, Qt.FastTransformation)
            painter.drawPixmap(0, 0, pixmap)

        pen = QPen(Qt.black, 8)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width(), self.height())


class TurretControlUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Turret Control Panel")
        self.setMinimumSize(1300, 750)
        self.setStyleSheet("background-color: #D3D3D3; border: 10px solid black;")

        self.cap = None  # Kamera sonra başlatılacak
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera_frame)

        self.initUI()

        QTimer.singleShot(100, self.start_camera)

        # Programdan çıkarken kamera düzgün kapansın
        atexit.register(self.cleanup_camera)

    def start_camera(self):
        if self.cap and self.cap.isOpened():
            return  # Zaten açık

        self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # veya cv2.CAP_MSMF
        if not self.cap.isOpened():
            print(" USB kamera (index 1) açılamadı.")
            return
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

        self.timer.start(33)  # 30 FPS

    def cleanup_camera(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            print("Kamera düzgün kapatıldı (atexit).")

    def initUI(self):
        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        left_layout.addStretch()
        self.manual_button = self.create_button_with_label("MANUEL MOD")
        self.semi_auto_button = self.create_button_with_label("YARI OTONOM MOD")
        self.auto_button = self.create_button_with_label("OTONOM MOD")
        self.engage_button = self.create_button_with_label("ANGAJMAN MOD")

        for btn in [self.manual_button, self.semi_auto_button, self.auto_button, self.engage_button]:
            left_layout.addWidget(btn, alignment=Qt.AlignCenter)
        left_layout.addStretch()

        center_layout = QVBoxLayout()
        self.camera_label = CrosshairLabel()
        self.camera_label.setStyleSheet("border: 8px solid black; background-color: lightgray; border-radius: 15px;")
        center_layout.addWidget(self.camera_label, stretch=2)

        right_layout = QVBoxLayout()
        self.emergency_button_right = QPushButton("EMERGENCY\nSTOP")
        self.emergency_button_right.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.emergency_button_right.setFixedSize(110, 110)
        self.emergency_button_right.setStyleSheet("""
            QPushButton {
                color: black;
                font-weight: bold;
                font-size: 16px;
                border-radius: 55px;
                border: 3px solid black;
                background: qradialgradient(
                    cx:0.5, cy:0.5, radius: 0.6,
                    fx:0.5, fy:0.35,
                    stop: 0 white,
                    stop: 0.3 #ff6666,
                    stop: 0.7 #cc0000,
                    stop: 1 black
                );
            }
            QPushButton:hover {
                background: qradialgradient(
                    cx:0.5, cy:0.5, radius: 0.6,
                    fx:0.5, fy:0.35,
                    stop: 0 white,
                    stop: 0.3 #ff3333,
                    stop: 0.7 #aa0000,
                    stop: 1 black
                );
            }
            QPushButton:pressed {
                background: qradialgradient(
                    cx:0.5, cy:0.5, radius: 0.6,
                    fx:0.5, fy:0.35,
                    stop: 0 #ff3333,
                    stop: 0.3 #cc0000,
                    stop: 0.7 #880000,
                    stop: 1 black
                );
            }
        """)
        self.emergency_button_right.clicked.connect(lambda: print("EMERGENCY STOP butonuna basıldı."))

        right_layout.addSpacing(300)
        right_layout.addWidget(self.emergency_button_right, alignment=Qt.AlignHCenter | Qt.AlignBottom)
        right_layout.addSpacing(120)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(center_layout, stretch=2)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

    def update_camera_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.camera_label.set_frame(frame)

    def closeEvent(self, event):
        self.cleanup_camera()
        event.accept()

    def create_button_with_label(self, text, bg_color="lightgray", text_color="black"):
        button = QPushButton()
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.setFixedSize(90, 90)
        button.clicked.connect(lambda: print(f"{text} butonuna basıldı."))

        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border-radius: 45px;
                border: 2px solid #A0A0A0;
                padding: 5px;
                background: qradialgradient(
                    cx:0.5, cy:0.5, radius: 0.6,
                    fx:0.5, fy:0.35,
                    stop: 0 white,
                    stop: 0.7 lightgray,
                    stop: 1 gray
                );
            }}
            QPushButton:hover {{
                background: qradialgradient(
                    cx:0.5, cy:0.5, radius: 0.6,
                    fx:0.5, fy:0.35,
                    stop: 0 white,
                    stop: 0.6 silver,
                    stop: 1 darkgray
                );
            }}
            QPushButton:pressed {{
                background: qradialgradient(
                    cx:0.5, cy:0.5, radius: 0.6,
                    fx:0.5, fy:0.35,
                    stop: 0 silver,
                    stop: 0.6 gray,
                    stop: 1 darkgray
                );
            }}
        """)

        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 14px; color: black; font-style: italic; border: none;")

        layout = QVBoxLayout()
        layout.addWidget(button, alignment=Qt.AlignCenter)
        layout.addWidget(label, alignment=Qt.AlignCenter)

        container = QWidget()
        container.setLayout(layout)
        container.setStyleSheet("border: none;")
        return container


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TurretControlUI()
    window.show()
    sys.exit(app.exec())

import sys
import serial
import threading
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import QTimer
from OpenGL.GL import *
from OpenGL.GLU import *


class CubeWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        self.setMinimumSize(500, 500)

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.18, 0.18, 0.18, 1.0)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / h if h != 0 else 1, 1.0, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -7.0)

        glRotatef(self.roll, 0.0, 0.0, 1.0)   # Z ekseni
        glRotatef(self.pitch, 1.0, 0.0, 0.0)  # X ekseni
        glRotatef(self.yaw, 0.0, 1.0, 0.0)    # Y ekseni

        self.draw_cube()

    def draw_cube(self):
        glBegin(GL_QUADS)
        glColor3f(1.0, 0.0, 0.0)  # Ön
        glVertex3f(1,1,1); glVertex3f(-1,1,1)
        glVertex3f(-1,-1,1); glVertex3f(1,-1,1)

        glColor3f(0.0, 1.0, 0.0)  # Arka
        glVertex3f(1,1,-1); glVertex3f(-1,1,-1)
        glVertex3f(-1,-1,-1); glVertex3f(1,-1,-1)

        glColor3f(0.0, 0.0, 1.0)  # Sol
        glVertex3f(-1,1,1); glVertex3f(-1,1,-1)
        glVertex3f(-1,-1,-1); glVertex3f(-1,-1,1)

        glColor3f(1.0, 1.0, 0.0)  # Sağ
        glVertex3f(1,1,-1); glVertex3f(1,1,1)
        glVertex3f(1,-1,1); glVertex3f(1,-1,-1)

        glColor3f(0.0, 1.0, 1.0)  # Üst
        glVertex3f(1,1,-1); glVertex3f(-1,1,-1)
        glVertex3f(-1,1,1); glVertex3f(1,1,1)

        glColor3f(1.0, 0.0, 1.0)  # Alt
        glVertex3f(1,-1,1); glVertex3f(-1,-1,1)
        glVertex3f(-1,-1,-1); glVertex3f(1,-1,-1)
        glEnd()

    def update_orientation(self, roll, pitch, yaw):
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        self.update()
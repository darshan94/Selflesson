# FINAL VERSION OF 2.0
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt,QTimer, pyqtSlot, pyqtSignal, QObject, QThread
from PyQt5.QtWidgets import QGridLayout,QDockWidget,QApplication,QWidget,QLabel, QVBoxLayout, QMainWindow, QGroupBox, QVBoxLayout, QHBoxLayout

from timeV2 import TimeWidget
from dateV2 import DateWidget
from weatherV2 import WeatherWindow
from emailV2 import emailWidget
from navigationV2 import Navigation

from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread

from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils

import numpy as np
import imutils
import dlib
import cv2
import time
import sys

class TestSignal(QObject):

    progress_signal = pyqtSignal(int)
    finished =pyqtSignal()

    def __init__(self, parent=None):
        super(TestSignal,self).__init__(parent)
        self.num =0
    
    def progress(self):
        for i in range(10):
            i+=self.num
            self.progress_signzl.emit(i)
            time.sleep(1)
        self.finished.emit()

    def setterNum(self,nuu):
        self.num = nuu

class MainWindow_V2(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow_V2,self).__init__(parent)
# TESTING PURPOSE

        
        self.timeWidg = TimeWidget(self)
        self.timeWidg.move(600,150)
        self.timeWidg.setStyleSheet(".QLabel{ color:white ; background-color:black ; font-size:60px }")

        self.dateWidg = DateWidget(self)
        self.dateWidg.move(250,5)
        self.dateWidg.setStyleSheet(".QLabel{ color:white ; background-color:black ; font-size:60px }")

        self.navObj = Navigation()
        self.navThread = QThread()

        self.navObj.Pattern_progress.connect(self.moduleSelection)
        self.navObj.finished.connect(self.naviFinished)
        self.navObj.moveToThread(self.navThread)
        self.navThread.started.connect(self.navObj.navigationMode_1)
        
        self.emailStack = emailWidget(self)
        self.emailStack.move(100,800)
        self.emailStack.hide()
        self.weatherStack = WeatherWindow(self)
        self.weatherStack.move(100,800)
        self.weatherStack.hide()
        #self.emailStack.startEmailBackend()
        self.setNaviMode("SubWin")
        self.startMainNav()

    def startMainNav(self):
        self.navThread.start()

    def naviFinished(self):
        self.navThread.quit()
        self.navThread.wait()

    def setNaviMode(self,_winType):
        self.navObj.setWindowType(_winType)

    def moduleSelection(self,value):
        if value == 'PATTERN_11':
            self.emailStack.show()
            self.emailStack.startEmailBackend()

        elif value == 'PATTERN_5':
            self.emailStack.show()
            self.weatherStack.startWeatherBackend()

        else:
            print("ERROR")
       

        QApplication.processEvents()
        


if __name__ == "__main__":
   
    app = QApplication(sys.argv)
    win_sts = MainWindow_V2()
    win_sts.showFullScreen()
    sys.exit(app.exec_())
    

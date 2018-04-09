# FINAL VERSION OF 2.0
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt,QTimer, pyqtSlot, pyqtSignal, QObject, QThread
from PyQt5.QtWidgets import QGridLayout,QStackedWidget, QDockWidget,QApplication,QWidget,QLabel, QVBoxLayout, QMainWindow, QGroupBox, QVBoxLayout, QHBoxLayout

from timeV2 import TimeWidget
from dateV2 import DateWidget
from weatherV2 import WeatherWindow
from emailV2 import emailWidget
from navigationV2 import Navigation
from Face_Recognition import FACE_RECOGNITION_GUI

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

class selectionWidget(QMainWindow): 

    start_Email_Signal = pyqtSignal()
    start_Weather_Signal = pyqtSignal()

    NEXT_PAGE_EMAIL = pyqtSignal()
    NEXT_PAGE_WEATHER = pyqtSignal()

    PREV_PAGE_EMAIL = pyqtSignal()
    PREV_PAGE_WEATHER = pyqtSignal()  
    
    
    def __init__(self, parent=None):
        super(selectionWidget,self).__init__(parent)

        self.FACE_AUTHENICATION = FACE_RECOGNITION_GUI(self)
        self.FACE_AUTHENICATION.face_Recognized.connect(self.FACERECOGNIZED)

        self.SECURITY_THREAD = QThread()
        self.FACE_AUTHENICATION.moveToThread(self.SECURITY_THREAD)
        self.SECURITY_THREAD.started.connect(self.FACE_AUTHENICATION.START_RECOGNIZATION)
        self.SECURITY_THREAD.start()
        self.FACE_AUTHENICATION.showFullScreen()

        self.currentWindow = 'None'

        self.timeWidg = TimeWidget(self)
        self.timeWidg.move(600,150)
        self.timeWidg.hide()
        self.timeWidg.setStyleSheet(".QLabel{ color:white ; background-color:black ; font-size:60px }")


        self.dateWidg = DateWidget(self)
        self.dateWidg.move(250,5)
        self.dateWidg.hide()
        self.dateWidg.setStyleSheet(".QLabel{ color:white ; background-color:black ; font-size:60px }")

        self.navObj = Navigation()
        self.navThread = QThread()

        self.emailStack = emailWidget(self)
        self.emailStack.move(100,800)
        self.emailStack.hide()
        self.weatherStack = WeatherWindow(self)
        self.weatherStack.hide()
        self.weatherStack.move(100,800)

        self.navObj.Pattern_progress.connect(self.moduleSelection)
        self.navObj.finished.connect(self.naviFinished)
        self.navObj.moveToThread(self.navThread)
        self.navThread.started.connect(self.navObj.navigationMode_1)

        self.start_Email_Signal.connect(self.emailStack.startEmailBackend)
        self.emailStack.done_Signal.connect(self.Finished_signalReceiverFromWidgets)

        self.start_Weather_Signal.connect(self.weatherStack.startWeatherBackend)
        self.weatherStack.done_Signal.connect(self.Finished_signalReceiverFromWidgets)

        self.setNaviMode("SubWin")


        self.setStyleSheet("QMainWindow{ background-color : black}")
        

    def FACERECOGNIZED(self):
        self.timeWidg.show()
        self.dateWidg.show()
        self.startMainNav()
        
    def CLOSE_ACTIVE_WINDOW(self):
        if self.currentWindow == 'EMAIL':
            self.emailStack.hide()

        elif self.currentWindow == 'WEATHER':
            self.weatherStack.hide()

        else:
            print("[SELECTION WINDOW STATUS] : NO WINDOW ACTIVE")


    def NEXT_PAGE(self):
        if self.currentWindow == 'EMAIL':
            self.NEXT_PAGE_EMAIL.emit()

        elif self.currentWindow == 'WEATHER':
            self.NEXT_PAGE_WEATHER.emit()

        else:
            print("[SELECTION WINDOW STATUS] : NO WINDOW ACTIVE")

    def PREVIOUS_PAGE(self):
        if self.currentWindow == 'EMAIL':
            self.PREV_PAGE_EMAIL.emit()

        elif self.currentWindow == 'WEATHER':
            self.PREV_PAGE_WEATHER.emit()

        else:
            print("[SELECTION WINDOW STATUS] : NO WINDOW ACTIVE")

    
    def patternSelection(self,patternType):
        print("[SELECTION WINDOW STATUS] : PATTERN SIGNAL FROM NAVIGATION CLASS RECEIVED")
        
        if patternType == 'PATTERN_1':
            print("[SELECTION WINDOW STATUS] : ACTIVE DEBUG WINDOW")

        elif patternType == 'PATTERN_2':
            print("[SELECTION WINDOW STATUS] : NO MODULE IS ASSIGNED FOR THIS")

        elif patternType == 'PATTERN_3':
            print("[SELECTION WINDOW STATUS] : NO MODULE IS ASSIGNED FOR THIS")

        elif patternType == 'BOTH_OPEN':
            print("[SELECTION WINDOW STATUS] : ACTIVE EMAIL MODULE")
            self.currentWindow = 'EMAIL'
            self.emailStack.show()
            self.start_Email_Signal.emit()

        elif patternType == 'PATTERN_5':
            print("[SELECTION WINDOW STATUS] : ACTIVE WEATHER INFO")
            self.currentWindow = 'WEATHER'
            self.weatherStack.show()
            self.start_Weather_Signal.emit()

        elif patternType == 'PATTERN_6':
            print("[SELECTION WINDOW STATUS] : ACTIVE CAMERA MODULE")

        elif patternType == 'PATTERN_7':
            print("[SELECTION WINDOW STATUS] : CLOSE ACTIVE WINDOW AND BACK TO MAIN WINDOW")

        elif patternType == 'PATTERN_8':
            print("[SELECTION WINDOW STATUS] : DEACTIVE DEBUG WINDOW")

        elif patternType == 'PATTERN_9':
            print("[SELECTION WINDOW STATUS] : MOVE TO PREV/DOWN")
            self.PREVIOUS_PAGE()

        elif patternType == 'PATTERN_10':
            print("[SELECTION WINDOW STATUS] : MOVE TO NEXT/UP")
            self.NEXT_PAGE()

        elif patternType == 'PATTERN_11':
            print("[SELECTION WINDOW STATUS] : CLOSE ACTIVE WINDOW AND BACK TO MAIN WINDOW")
            self.CLOSE_ACTIVE_WINDOW(self)

        else:
            print("[SELECTION WINDOW STATUS] : ERROR INPUT ")

    def Finished_signalReceiverFromWidgets(self):
        print("[SELECTION WINDOW STATUS] : FINISHED SIGNAL FROM WIDGETS RECEIVED")
        print("[SELECTION WINDOW STATUS] : NAVIGATION WILL START WITHIN 3 SECONDS")
        time.sleep(3)

        if self.currentWindow != 'MAINWIN':
            self.setNaviMode('SubWin')
        else:
            self.setNaviMode('MainWin') 
            
        print("[SELECTION WINDOW STATUS] : NAVIGATION WILL STARTING")
        self.startMainNav()
        
    def startMainNav(self):
        self.navThread.start()

    def naviFinished(self,value):
        print("[SELECTION WINDOW STATUS] : FINISHED SIGNAL FROM NAVIGATION CLASS RECEIVED")
        self.navThread.quit()
        self.navThread.wait()
        print("[SELECTION WINDOW STATUS] : PATTERN SIGNAL FROM NAVIGATION CLASS RECEIVED")
        print("[SELECTION WINDOW STATUS] : SEND INPUT TO THE SELECTION METHOD")
        self.patternSelection(value)

    def setNaviMode(self,_winType):
        self.navObj.setWindowType(_winType)

    def moduleSelection(self,value):
        print("[SELECTION WINDOW STATUS] : PATTERN SIGNAL FROM NAVIGATION CLASS RECEIVED")
        print("[SELECTION WINDOW STATUS] : SEND INPUT TO THE SELECTION METHOD")
        self.patternSelection(value)       

if __name__ == "__main__":
   
    app = QApplication(sys.argv)
    win_sts = selectionWidget()
    win_sts.showFullScreen()
    sys.exit(app.exec_())

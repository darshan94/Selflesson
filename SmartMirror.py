# FINAL VERSION OF 2.0
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt,QTimer, pyqtSlot, pyqtSignal, QObject, QThread
from PyQt5.QtWidgets import QGridLayout,QStackedWidget, QDockWidget,QApplication,QWidget,QLabel, QVBoxLayout, QMainWindow, QGroupBox, QVBoxLayout, QHBoxLayout

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


class selectionWidget(QMainWindow): # FUCK NO ANY MODULE WIDGET DECLARED HERE !

    start_Email_Signal = pyqtSignal()
    self.start_Weather_Signal = 

    self.NEXT_PAGE_EMAIL = 
    self.NEXT_PAGE_WEATHER =

    self.PREV_PAGE_EMAIL = 
    self.PREV_PAGE_WEATHER =  
    
    
    def __init__(self, parent=None):
        super(selectionWidget,self).__init__(parent)

        self.currentWindow = 'None'
        
        self.navObj = Navigation()
        self.navThread = QThread()

        self.emailStack = emailWidget(self)
        self.emailStack.move(100,800)
        self.weatherStack = WeatherWindow(self)
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
        self.startMainNav()                        
        
    def CLOSE_ACTIVE_WINDOW(self):
        if self.currentWindow == 'EMAIL':
            self.emailStack.close()

        elif self.currentWindow == 'WEATHER':
            self.weatherStack.close()

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
        if patternType == 'PATTERN_11':
            print("[SELECTION WINDOW STATUS] : EMAIL WIDGET IS CHOSEN")
            

        if patternType == 'PATTERN_1':
            print("[SELECTION WINDOW STATUS] : ACTIVE DEBUG WINDOW")

        elif patternType == 'PATTERN_2':
            print("[SELECTION WINDOW STATUS] : NO MODULE IS ASSIGNED FOR THIS")

        elif patternType == 'PATTERN_3':
            print("[SELECTION WINDOW STATUS] : NO MODULE IS ASSIGNED FOR THIS")

        elif patternType == 'PATTERN_4':
            print("[SELECTION WINDOW STATUS] : ACTIVE EMAIL MODULE")
            self.currentWindow = 'EMAIL'
            self.start_Email_Signal.emit()

        elif patternType == 'PATTERN_5':
            print("[SELECTION WINDOW STATUS] : ACTIVE WEATHER INFO")
            self.currentWindow = 'WEATHER'
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
            self.setNaviMode('SubWin'):
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

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
    
    
    def __init__(self, parent=None):
        super(selectionWidget,self).__init__(parent)

        self.currentWindow = 'None'
        
        self.navObj = Navigation()
        self.navThread = QThread()

        self.navObj.Pattern_progress.connect(self.moduleSelection)
        self.navObj.finished.connect(self.naviFinished)
        self.navObj.moveToThread(self.navThread)
        self.navThread.started.connect(self.navObj.navigationMode_1)

        self.emailStack = emailWidget(self)         # WIDGET B
        self.emailStack.move(100,800)
        self.emailStack.hide()

        self.weatherStack = WeatherWindow(self)
        self.weatherStack.move(100,800)
        self.weatherStack.hide()

        self.start_Email_Signal.connect(self.emailStack.startEmailBackend)
        self.emailStack.done_Signal.connect(self.signalReceiverFromEmailWidget)

        self.setNaviMode("SubWin")
        self.startMainNav()                         # START NAVIGATION
        
    def closeActiveWindow(self):
        if self.currentWindow == 'EMAIL':
            self.emailStack.close()

        elif self.currentWindow == 'WEATHER':
            self.weatherStack.close()

        else:
            print("[SELECTION WINDOW STATUS] : NO WINDOW ACTIVE")

    
    def patternSelection(self,patternType):
        print("[SELECTION WINDOW STATUS] : PATTERN SIGNAL FROM NAVIGATION CLASS RECEIVED")
        if patternType == 'PATTERN_11':
            print("[SELECTION WINDOW STATUS] : EMAIL WIDGET IS CHOSEN")
            self.currentWindow = 'EMAIL'
            self.emailStack.show()
            self.start_Email_Signal.emit()

        elif patternType == 'BOTH_OPEN':
            print("[SELECTION WINDOW STATUS] : WEATHER WIDGET IS CHOSEN")
            self.emailStack.close()

        else:
            print("ERROR")

    def signalReceiverFromEmailWidget(self):
        print("[SELECTION WINDOW STATUS] : FINISHED SIGNAL FROM EMAIL IS RECEIVED")
        print("[SELECTION WINDOW STATUS] : NAVIGATION WILL START WITHIN 3 SECONDS")
        time.sleep(3)
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

    
        
        
    

class MainWindow_V2(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow_V2,self).__init__(parent)
# TESTING PURPOSE


        self.navObj = Navigation()
        self.navThread = QThread()

        #self.navObj.Pattern_progress.connect(self.moduleSelection)
        self.navObj.finished.connect(self.naviFinished)
        self.navObj.moveToThread(self.navThread)
        self.navThread.started.connect(self.navObj.navigationMode_1)

        self.SELECTION_WIDGET = selectionWidget()   # WIDGET A
        self.SELECTION_WIDGET.show()
        self.SELECTION_WIDGET.move(100,800)
        self.setNaviMode("SubWin")
        self.startMainNav()                         # START NAVIGATION
        

    def startMainNav(self):
        self.navThread.start()

    def naviFinished(self,value):
        print("[MAIN WINDOW GUI STATUS] : FINISHED SIGNAL FROM NAVIGATION CLASS RECEIVED")
        self.navThread.quit()
        self.navThread.wait()
        print("[MAIN WINDOW GUI STATUS] : PATTERN SIGNAL FROM NAVIGATION CLASS RECEIVED")
        print("[MAIN WINDOW GUI STATUS] : SEND INPUT TO THE SELECTION WIDGET")
        self.SELECTION_WIDGET.patternSelection(value)

    def setNaviMode(self,_winType):
        self.navObj.setWindowType(_winType)

    def moduleSelection(self,value):
        print("[MAIN WINDOW GUI STATUS] : PATTERN SIGNAL FROM NAVIGATION CLASS RECEIVED")
        print("[MAIN WINDOW GUI STATUS] : SEND INPUT TO THE SELECTION WIDGET")
        self.SELECTION_WIDGET.patternSelection(value)

        QApplication.processEvents()

    def activeEmailWidget(self):
        print("[MAIN WINDOW GUI STATUS] : activeEmailWidget(self) CALLED")
        #self.emailStack.show()
        #self.emailStack.startEmailBackend()

    
        

if __name__ == "__main__":
   
    app = QApplication(sys.argv)
    win_sts = selectionWidget()
    win_sts.showFullScreen()
    sys.exit(app.exec_())

'''
class selectionWidget(QWidget): # FUCK NO ANY MODULE WIDGET DECLARED HERE !

    start_Email_Signal = pyqtSignal()
    
    
    def __init__(self, parent=None):
        super(selectionWidget,self).__init__(parent)

        self.emailStack = emailWidget(self)         # WIDGET B
        self.emailStack.move(100,800)


        self.weatherStack = WeatherWindow(self)
        self.weatherStack.move(100,800)
        #self.weatherStack.show()

        self.stackedWidget = QStackedWidget(self)

        self.stackedWidget.addWidget(self.emailStack)
        self.stackedWidget.addWidget(self.weatherStack)

        #self.leftList = QListWidget(self)
        #self.leftList.insert

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.stackedWidget)
        self.setLayout(self.layout)

        #self.start_Email_Signal.connect(self.emailStack.startEmailBackend)
        #self.emailStack.done_Signal.connect(self.signalReceiverFromEmailWidget)
        
    def patternSelection(self,patternType):
        print("[SELECTION WIDGET STATUS] : PATTERN SIGNAL FROM NAVIGATION CLASS RECEIVED")
        if patternType == 'PATTERN_11':
            print("[SELECTION WIDGET STATUS] : EMAIL WIDGET IS CHOSEN")
            #self.emailStack.show()
            #self.start_Email_Signal.emit()

        elif patternType == 'PATTERN_5':
            self.emailStack.show()
            self.weatherStack.startWeatherBackend()

        else:
            print("ERROR")

    def signalReceiverFromEmailWidget(self):
        print("[SELECTION WIDGET STATUS] : FINISHED SIGNAL FROM EMAIL IS RECEIVED")'''
        


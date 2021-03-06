# FINAL VERSION OF 2.0
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt,QTimer, pyqtSlot, pyqtSignal, QObject, QThread
from PyQt5.QtWidgets import QGridLayout,QDockWidget,QApplication,QWidget,QLabel, QVBoxLayout, QMainWindow, QGroupBox, QVBoxLayout, QHBoxLayout

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

class MainWindow_V2(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow_V2,self).__init__(parent)

        self.timeWidg = TimeWidget(self)
        self.timeWidg.move(600,150)
        self.timeWidg.setStyleSheet(".QLabel{ color:white ; background-color:black ; font-size:60px }")

        self.dateWidg = DateWidget(self)
        self.dateWidg.move(250,5)
        self.dateWidg.setStyleSheet(".QLabel{ color:white ; background-color:black ; font-size:60px }")

        self.debugWidg = DebugWindow(self)
        self.debugWidg.move(10,500)
        #self.debugWidg.setStyleSheet(".QLabel{ color:white ; background-color:black ; font-size:60px }")


class TimeWidget(QWidget):
    def __init__(self, parent=None):
        super(TimeWidget,self).__init__(parent)
        self.timeLabel = QLabel('Time',self)
        self.timeLabel.setAlignment(Qt.AlignCenter)
        self.setLayout = QVBoxLayout(self)
        self.layout().addWidget(self.timeLabel)
        
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.displayTimer)
        self.timer.start()
        QApplication.processEvents()
        self.setGeometry(40,40,400,120)


    def displayTimer(self):
        print("connected")
        timef =QTime.currentTime()
        print("middle")
        self.timeLabel.setText(timef.toString(Qt.ISODate))
        minuteTime = timef.minute()
        hourTime = timef.hour()
        secTime = timef.second()
        print(str(hourTime)+" : "+str(minuteTime))
        print("next")

class DateWidget(QWidget):
    def __init__(self, parent=None):
        super(DateWidget,self).__init__(parent)
        self.dateLabel = QLabel('Date',self)
        self.dateLabel.setAlignment(Qt.AlignCenter)
        self.setLayout = QVBoxLayout(self)
        self.layout().addWidget(self.dateLabel)
        
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.displayDate)
        self.timer.start()
        QApplication.processEvents()
        self.setGeometry(40,40,800,150)
        #self.setStyleSheet("background:black")

    def displayDate(self):
        print("connectedDate")
        datef =QDate.currentDate()
        print("middleDate")
        self.dateLabel.setText(datef.toString(Qt.DefaultLocaleLongDate))
        print("next")


class moduleWidget(QWidget):
    def __init__(self,parent=None):
        super(moduleWidget,self).__init__(parent)
        


#--------------------------BACKEND------------------------------------------------------------

class Navigation(QObject):

    Mouth_Open_progress = pyqtSignal(int)
    Mouth_Close_progress = pyqtSignal(int)
    Mouth_State_progress = pyqtSignal(str)
    LeftEye_Open_progress = pyqtSignal(int)
    LeftEye_Close_progress = pyqtSignal(int)
    LeftEye_State_progress = pyqtSignal(str)
    RightEye_Open_progress = pyqtSignal(int)
    RightEye_Close_progress = pyqtSignal(int)
    RightEye_State_progress = pyqtSignal(str)
    Pattern_progress = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self):
        super(Navigation,self).__init__()

        self.MOUTH_AR_THRESH_CLOSED = 0.10
        self.MOUTH_AR_THRESH_OPENED = 0.20
        self.MOUTH_AR_CONSEC_FRAME = 3
        self.EYE_AR_THRESH=0.3
        self.EYE_AR_CONSEC_FRAMES = 3

        self.LEFT_CLOSE_COUNTER  = 0 
        self.LEFT_OPEN_COUNTER = 0
        self.RIGHT_CLOSE_COUNTER = 0
        self.RIGHT_OPEN_COUNTER = 0
        self.CURRENT_LEFT_EYE_STATE = 0
        self.LEFT_EYE_OPEN_TOTAL = 0
        self.LEFT_EYE_CLOSE_TOTAL = 0
        self.CURRENT_RIGHT_EYE_STATE = 0
        self.RIGHT_EYE_OPEN_TOTAL = 0
        self.RIGHT_EYE_CLOSE_TOTAL = 0
        self.CURRENT_MOUTH_STATE = 0 
        self.TOTAL_MOUTH_OPEN_TOTAL = 0 
        self.TOTAL_MOUTH_CLOSE_TOTAL = 0

        self.patternCaller = 0
        self.patternResult= 'None'

        self.winType = "MainWin"

        print("[INFO-NAVIGATION FUNCTION CLASS] : Loading Necessary File")
        
        self.detector=dlib.get_frontal_face_detector()
        self.predictor=dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        (self.lStart,self.lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (self.rStart,self.rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
        (self.mStart,self.mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]
        
        print("[INFO-NAVIGATION FUNCTION CLASS]  : Files loaded into memory ")
        print("[INFO-NAVIGATION FUNCTION CLASS]  : Camera Initialization Started ")
        
        self.open_Counter = 0
        self.closed_Counter = 0
        self.camera = PiCamera()
        self.camera.resolution = (640,480)
        self.camera.framerate = 32
        self.rawCapture = PiRGBArray(self.camera, size=(640,480))
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port = True )
        
        print("[INFO-NAVIGATION FUNCTION CLASS]  : Camera Initialization Completed.Camera warming up to 4s")

        time.sleep(4)

    def __del__(self):
        self.wait()
        
    def _mouth_aspect_ratio(self,mouth):

        print("[INFO-NAVIGATION FUNCTION CLASS]  : _mouth_aspect_ratio(self,mouth) called.")
        
        A=dist.euclidean(mouth[13], mouth[19])
        B=dist.euclidean(mouth[14], mouth[18])
        C=dist.euclidean(mouth[15], mouth[17])
        D=dist.euclidean(mouth[12], mouth[16])
        mar=(A+B+C)/(2.0 * D)
        return mar

    def eye_aspect_ratio(self,eye):
        
        print("[INFO-NAVIGATION FUNCTION CLASS]  : eye_aspect_ratio(self,eye) called.")
        
        A=dist.euclidean(eye[1], eye[5])
        B=dist.euclidean(eye[2], eye[4])
        C=dist.euclidean(eye[0], eye[3])
        ear=(A+B)/(2.0 * C)
        return ear
    
    def eightCombo(self,left_Eye_state, right_Eye_state, mouth_state):

        print("[INFO-NAVIGATION FUNCTION CLASS]  : eightCombo(self,left_Eye_state, right_Eye_state, mouth_state) called.")
        
        EYES_STATE = threeCombo(left_Eye_state, right_Eye_state)
        
        if EYES_STATE == 'BOTH_OPEN' and mouth_state == 'OPEN':
            return 'PATTERN_1'
        elif EYES_STATE == 'PATTERN_10' and mouth_state == 'OPEN':
            return 'PATTERN_2'
        elif EYES_STATE == 'PATTERN_10' and mouth_state == 'CLOSED':
            return 'PATTERN_3'
        elif EYES_STATE == 'PATTERN_9' and mouth_state == 'OPEN':
            return 'PATTERN_4'
        elif EYES_STATE == 'PATTERN_9' and mouth_state == 'CLOSED':
            return 'PATTERN_5'
        elif EYES_STATE == 'BOTH_OPEN' and mouth_state == 'CLOSED':
            return 'PATTERN_6'
        elif EYES_STATE == 'PATTERN_11' and mouth_state == 'OPEN':
            return 'PATTERN_7'
        elif EYES_STATE == 'PATTERN_11' and mouth_state == 'CLOSED':
            return 'PATTERN_8'
        else:
            return 'VALUE_ERROR'    

    def threeCombo(self,left_Eye_state, right_Eye_state):

        print("[INFO-NAVIGATION FUNCTION CLASS]  : threeCombo(self,left_Eye_state, right_Eye_state) called.")
        
        if left_Eye_state == 'CLOSED' and right_Eye_state == 'CLOSED':
            return 'PATTERN_11'
        elif left_Eye_state == 'OPEN' and right_Eye_state == 'CLOSED':
            return 'PATTERN_10'
        elif left_Eye_state == 'CLOSED' and right_Eye_state == 'OPEN':
            return 'PATTERN_9'
        elif left_Eye_state == 'OPEN' and right_Eye_state == 'OPEN':
            return 'BOTH_OPEN'
        else:
            return 'INVALID VALUE'

    def setWindowType(self,windowType):
        self.winType = windowType

    def handlerSignalReceiver(self):

        print("[INFO-NAVIGATION FUNCTION CLASS]  : handlerSignalReceiver(self,winType) called.")
        
        if self.winType == "MainWin":
            print("DEBUG POINT 1")
            navigationMode_1(self)
        elif self.winType == "SubWin":
            navigationMode_2()
        else:
            print("ERROR SETTER")
    
    def navigationMode_1(self):

        print("[INFO-NAVIGATION FUNCTION CLASS] : navigationMode_1() is called")
        print("[STATUS] : NAVIGATION MODE 1 STARTED")
 
        for f in self.stream:
            self.image = f.array
            print("[STATUS] : Reading Frame")
            self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            print("[STATUS] : accesss opencv")
            self.rects=self.detector(self.gray, 0)
            print("[STATUS] : accesss detector")
            for rect in self.rects:
                self.shape=self.predictor(self.gray, rect)
                print("[STATUS] : LANDMARK POINT IS EXTRACTED")
                self.shape=face_utils.shape_to_np(self.shape)
                print("[STATUS] : LANDMARK POINT CONVERTED INTO NUMPY ARRAY")
                self.mouthPoint = self.shape[self.mStart:self.mEnd]
                print("[STATUS] : MOUTH PART IS EXTRACTED")
                self.leftEye=self.shape[self.lStart:self.lEnd]
                print("[STATUS] : LEFT EYE PART IS EXTRACTED")
                self.rightEye=self.shape[self.rStart:self.rEnd]
                print("[STATUS] : RIGHT EYE PART IS EXTRACTED")
                self.mouthMAR = self._mouth_aspect_ratio(self.mouthPoint)
                print("[STATUS] : MAR VALUE IS OBTAINED")
                self.leftEAR=self.eye_aspect_ratio(self.leftEye)
                print("[STATUS] : LEAR VALUE IS OBTAINED")
                self.rightEAR=self.eye_aspect_ratio(self.rightEye)
                print("[STATUS] : REAR VALUE IS OBTAINED")

#_____STAGE_1___________________________________________________________________________________________________


                print("[STATUS] : STAGE 1")
                
                if self.mouthMAR < self.MOUTH_AR_THRESH_CLOSED :
                    print("[STATUS] : MOUTH CLOSE FOR THIS FRAME")
                    self.closed_Counter+=1
                    self.open_Counter = 0
                    self.Mouth_Open_progress.emit(self.open_Counter)
                    self.Mouth_Close_progress.emit(self.closed_Counter)

                else:
                    if self.mouthMAR > self.MOUTH_AR_THRESH_OPENED :
                        print("[STATUS] : MOUTH OPEN FOR THIS FRAME")
                        self.open_Counter += 1
                        self.closed_Counter = 0
                        self.Mouth_Open_progress.emit(self.open_Counter)
                        self.Mouth_Close_progress.emit(self.closed_Counter)

                    else:
                        print("[STATUS] : NO MOUTH DATA FOR THIS FRAME")
                        self.closed_Counter = 0
                        self.open_Counter = 0
                        self.Mouth_Open_progress.emit(self.open_Counter)
                        self.Mouth_Close_progress.emit(self.closed_Counter)

                if self.leftEAR<self.EYE_AR_THRESH:
                    print("[STATUS] : LEFT EYE CLOSE FOR THIS FRAME")
                    self.LEFT_CLOSE_COUNTER+=1
                    self.LEFT_OPEN_COUNTER = 0
                    self.LeftEye_Open_progress.emit(self.LEFT_OPEN_COUNTER)
                    self.LeftEye_Close_progress.emit(self.LEFT_CLOSE_COUNTER)
                else:
                    print("[STATUS] : LEFT EYE OPEN FOR THIS FRAME")
                    self.LEFT_OPEN_COUNTER+=1
                    self.LEFT_CLOSE_COUNTER = 0
                    self.LeftEye_Open_progress.emit(self.LEFT_OPEN_COUNTER)
                    self.LeftEye_Close_progress.emit(self.LEFT_CLOSE_COUNTER)

                if self.rightEAR<self.EYE_AR_THRESH:
                    print("[STATUS] : RIGHT EYE CLOSE FOR THIS FRAME")
                    self.RIGHT_CLOSE_COUNTER+=1
                    self.RIGHT_OPEN_COUNTER = 0
                    self.RightEye_Open_progress.emit(self.RIGHT_OPEN_COUNTER)
                    self.RightEye_Close_progress.emit(self.RIGHT_CLOSE_COUNTER)

                else:
                    print("[STATUS] : RIGHT EYE OPEN FOR THIS FRAME")
                    self.RIGHT_OPEN_COUNTER += 1
                    self.RIGHT_CLOSE_COUNTER = 0
                    self.RightEye_Open_progress.emit(self.RIGHT_OPEN_COUNTER)
                    self.RightEye_Close_progress.emit(self.RIGHT_CLOSE_COUNTER)

#_____STAGE_2___________________________________________________________________________________________________

                print("[STATUS] : STAGE 2")
                
                if self.LEFT_CLOSE_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                    print("[STATUS] : LEFT EYE CLOSE VALIDATED")
                    self.CURRENT_LEFT_EYE_STATE = "OPEN"
                    self.LEFT_EYE_OPEN_TOTAL += 1
                    self.LEFT_EYE_CLOSE_TOTAL = 0
                    self.LEFT_CLOSE_COUNTER = 0
                    self.LEFT_OPEN_COUNTER = 0
                    self.LeftEye_State_progress.emit(self.CURRENT_LEFT_EYE_STATE)
                    
                else:
                    if self.LEFT_OPEN_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                        print("[STATUS] : LEFT EYE OPEN VALIDATED")
                        self.CURRENT_LEFT_EYE_STATE = "CLOSE"
                        self.LEFT_EYE_CLOSE_TOTAL += 1
                        self.LEFT_EYE_OPEN_TOTAL = 0
                        self.LEFT_OPEN_COUNTER = 0
                        self.LEFT_CLOSE_TOTAL = 0
                        self.LeftEye_State_progress.emit(self.CURRENT_LEFT_EYE_STATE)

                    else:
                        print("[STATUS] : LEFT EYE NOT DEFINED")
                        self.CURRENT_LEFT_EYE_STATE = "NOT DEFINED"
                        self.LeftEye_State_progress.emit(self.CURRENT_LEFT_EYE_STATE)

                if self.RIGHT_CLOSE_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                    print("[STATUS] : RIGHT EYE CLOSE VALIDATED")
                    self.CURRENT_RIGHT_EYE_STATE = "OPEN"
                    self.RIGHT_EYE_OPEN_TOTAL += 1
                    self.RIGHT_EYE_CLOSE_TOTAL = 0
                    self.RIGHT_CLOSE_COUNTER = 0
                    self.RIGHT_OPEN_COUNTER = 0
                    self.RightEye_State_progress.emit(self.CURRENT_RIGHT_EYE_STATE)
                    
                else:
                    if self.RIGHT_OPEN_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                        print("[STATUS] : RIGHT EYE OPEN VALIDATED")
                        self.CURRENT_RIGHT_EYE_STATE = "CLOSE"
                        self.RIGHT_EYE_CLOSE_TOTAL += 1
                        self.RIGHT_EYE_OPEN_TOTAL = 0
                        self.RIGHT_OPEN_COUNTER = 0
                        self.RIGHT_CLOSE_COUNTER = 0
                        self.RightEye_State_progress.emit(self.CURRENT_RIGHT_EYE_STATE)

                    else:
                        print("[STATUS] : RIGHT EYE NOT DEFINED")
                        self.CURRENT_RIGHT_EYE_STATE = "NOT DEFINED"
                        self.RightEye_State_progress.emit(self.CURRENT_RIGHT_EYE_STATE)
                        print("[STATUS] : RIGHT EYE NOT DEFINED SIGNAL SENT")
                
                if self.open_Counter >= self.MOUTH_AR_CONSEC_FRAME :     
                    print("[STATUS] : MOUTH OPEN VALIDATED")
                    self.CURRENT_MOUTH_STATE= "OPEN"
                    self.TOTAL_MOUTH_OPEN_TOTAL += 1
                    self.TOTAL_MOUTH_CLOSE_TOTAL = 0
                    self.Mouth_State_progress.emit(self.CURRENT_MOUTH_STATE)

                else:
                    if self.closed_Counter >= self.MOUTH_AR_CONSEC_FRAME:
                        print("[STATUS] : MOUTH CLOSE VALIDATED")
                        self.CURRENT_MOUTH_STATE = "CLOSE"
                        self.TOTAL_MOUTH_CLOSE_TOTAL += 1
                        self.TOTAL_MOUTH_OPEN_TOTAL = 0
                        self.Mouth_State_progress.emit(self.CURRENT_MOUTH_STATE)

                    else:
                        print("[STATUS] : MOUTH NOT DEFINED VALIDATED")
                        self.CURRENT_MOUTH_STATE = "NOT DEFINED"
                        print("[STATUS] : MOUTH NOT DEFINED VALIDATED SIGNAL WILL BE SENT")
                        self.Mouth_State_progress.emit(self.CURRENT_MOUTH_STATE)
                        print("[STATUS] : MOUTH NOT DEFINED VALIDATED SIGNAL SENT")

#_____STAGE_3___________________________________________________________________________________________________
                print("[STATUS] : DEBUGGER POINT 11_")


                if self.LEFT_EYE_OPEN_TOTAL != 1 or self.LEFT_EYE_CLOSE_TOTAL != 1 :
                    self.PREVIOUS_LEFT_EYE_STATE = self.CURRENT_LEFT_EYE_STATE
                if self.RIGHT_EYE_OPEN_TOTAL != 1 or self.RIGHT_EYE_CLOSE_TOTAL != 1 :
                    self.PREVIOUS_RIGHT_EYE_STATE = self.CURRENT_RIGHT_EYE_STATE
                if self.TOTAL_MOUTH_CLOSE_TOTAL != 1 or self.TOTAL_MOUTH_OPEN_TOTAL != 1 :
                    self.PREVIOUS_MOUTH_STATE = self.CURRENT_MOUTH_STATE
                

                if self.PREVIOUS_LEFT_EYE_STATE == self.CURRENT_LEFT_EYE_STATE and \
                  self.PREVIOUS_RIGHT_EYE_STATE == self.CURRENT_RIGHT_EYE_STATE and self.PREVIOUS_MOUTH_STATE == self.CURRENT_MOUTH_STATE :
                    self.patternCaller +=1
                else:
                    self.patternCaller =0

                if self.patternCaller > 4:
                    self.patternResult = eightCombo(self,CURRENT_LEFT_EYE_STATE, CURRENT_RIGHT_EYE_STATE, CURRENT_MOUTH_STATE)
                    self.Pattern_progress.emit(self.patternResult)
                    self.finished.emit()
                    self.rawCapture.close()
                    self.camera.close()

            self.rawCapture.truncate(0)
            print("[STATUS] : DONE THIS FRAME.NEXT FRAME")
            
        self.rawCapture.close()
        self.camera.close()


    def navigationMode_2(self):

        print("[INFO-NAVIGATION FUNCTION CLASS] : navigationMode_1() is called")
        print("[STATUS] : NAVIGATION MODE 2 STARTED")
 
        for f in self.stream:
            self.image = f.array
            print("[STATUS] : Reading Frame")
            self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            print("[STATUS] : accesss opencv")
            self.rects=self.detector(self.gray, 0)
            print("[STATUS] : accesss detector")
            for rect in self.rects:
                self.shape=self.predictor(self.gray, rect)
                print("[STATUS] : LANDMARK POINT IS EXTRACTED")
                self.shape=face_utils.shape_to_np(self.shape)
                print("[STATUS] : LANDMARK POINT CONVERTED INTO NUMPY ARRAY")
                
                self.leftEye=self.shape[self.lStart:self.lEnd]
                print("[STATUS] : LEFT EYE PART IS EXTRACTED")
                self.rightEye=self.shape[self.rStart:self.rEnd]
                print("[STATUS] : RIGHT EYE PART IS EXTRACTED")
                self.leftEAR=self.eye_aspect_ratio(self.leftEye)
                print("[STATUS] : LEAR VALUE IS OBTAINED")
                self.rightEAR=self.eye_aspect_ratio(self.rightEye)
                print("[STATUS] : REAR VALUE IS OBTAINED")

#_____STAGE_1___________________________________________________________________________________________________


                print("[STATUS] : STAGE 1")
                    
                if self.leftEAR<self.EYE_AR_THRESH:
                    print("[STATUS] : LEFT EYE CLOSE FOR THIS FRAME")
                    self.LEFT_CLOSE_COUNTER+=1
                    self.LEFT_OPEN_COUNTER = 0
                    self.LeftEye_Open_progress.emit(self.LEFT_OPEN_COUNTER)
                    self.LeftEye_Close_progress.emit(self.LEFT_CLOSE_COUNTER)
                else:
                    print("[STATUS] : LEFT EYE OPEN FOR THIS FRAME")
                    self.LEFT_OPEN_COUNTER+=1
                    self.LEFT_CLOSE_COUNTER = 0
                    self.LeftEye_Open_progress.emit(self.LEFT_OPEN_COUNTER)
                    self.LeftEye_Close_progress.emit(self.LEFT_CLOSE_COUNTER)

                if self.rightEAR<self.EYE_AR_THRESH:
                    print("[STATUS] : RIGHT EYE CLOSE FOR THIS FRAME")
                    self.RIGHT_CLOSE_COUNTER+=1
                    self.RIGHT_OPEN_COUNTER = 0
                    self.RightEye_Open_progress.emit(self.RIGHT_OPEN_COUNTER)
                    self.RightEye_Close_progress.emit(self.RIGHT_CLOSE_COUNTER)

                else:
                    print("[STATUS] : RIGHT EYE OPEN FOR THIS FRAME")
                    self.RIGHT_OPEN_COUNTER += 1
                    self.RIGHT_CLOSE_COUNTER = 0
                    self.RightEye_Open_progress.emit(self.RIGHT_OPEN_COUNTER)
                    self.RightEye_Close_progress.emit(self.RIGHT_CLOSE_COUNTER)


#_____STAGE_2___________________________________________________________________________________________________

                print("[STATUS] : STAGE 2")
                
                if self.LEFT_CLOSE_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                    print("[STATUS] : LEFT EYE CLOSE VALIDATED")
                    self.CURRENT_LEFT_EYE_STATE = "OPEN"
                    self.LEFT_EYE_OPEN_TOTAL += 1
                    self.LEFT_EYE_CLOSE_TOTAL = 0
                    self.LEFT_CLOSE_COUNTER = 0
                    self.LEFT_OPEN_COUNTER = 0
                    self.LeftEye_State_progress.emit(self.CURRENT_LEFT_EYE_STATE)
                    
                else:
                    if self.LEFT_OPEN_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                        print("[STATUS] : LEFT EYE OPEN VALIDATED")
                        self.CURRENT_LEFT_EYE_STATE = "CLOSE"
                        self.LEFT_EYE_CLOSE_TOTAL += 1
                        self.LEFT_EYE_OPEN_TOTAL = 0
                        self.LEFT_OPEN_COUNTER = 0
                        self.LEFT_CLOSE_TOTAL = 0
                        self.LeftEye_State_progress.emit(self.CURRENT_LEFT_EYE_STATE)

                    else:
                        print("[STATUS] : LEFT EYE NOT DEFINED")
                        self.CURRENT_LEFT_EYE_STATE = "NOT DEFINED"
                        self.LeftEye_State_progress.emit(self.CURRENT_LEFT_EYE_STATE)

                if self.RIGHT_CLOSE_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                    print("[STATUS] : RIGHT EYE CLOSE VALIDATED")
                    self.CURRENT_RIGHT_EYE_STATE = "OPEN"
                    self.RIGHT_EYE_OPEN_TOTAL += 1
                    self.RIGHT_EYE_CLOSE_TOTAL = 0
                    self.RIGHT_CLOSE_COUNTER = 0
                    self.RIGHT_OPEN_COUNTER = 0
                    self.RightEye_State_progress.emit(self.CURRENT_RIGHT_EYE_STATE)
                    
                else:
                    if self.RIGHT_OPEN_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                        print("[STATUS] : RIGHT EYE OPEN VALIDATED")
                        self.CURRENT_RIGHT_EYE_STATE = "CLOSE"
                        self.RIGHT_EYE_CLOSE_TOTAL += 1
                        self.RIGHT_EYE_OPEN_TOTAL = 0
                        self.RIGHT_OPEN_COUNTER = 0
                        self.RIGHT_CLOSE_COUNTER = 0
                        self.RightEye_State_progress.emit(self.CURRENT_RIGHT_EYE_STATE)

                    else:
                        print("[STATUS] : RIGHT EYE NOT DEFINED")
                        self.CURRENT_RIGHT_EYE_STATE = "NOT DEFINED"
                        self.RightEye_State_progress.emit(self.CURRENT_RIGHT_EYE_STATE)
                        print("[STATUS] : RIGHT EYE NOT DEFINED SIGNAL SENT")
                
                
#_____STAGE_3___________________________________________________________________________________________________
                print("[STATUS] : DEBUGGER POINT 11_")


                if self.LEFT_EYE_OPEN_TOTAL != 1 or self.LEFT_EYE_CLOSE_TOTAL != 1 :
                    self.PREVIOUS_LEFT_EYE_STATE = self.CURRENT_LEFT_EYE_STATE

                print("[STATUS] : DEBUGGER POINT 12_")
                    
                    
                if self.RIGHT_EYE_OPEN_TOTAL != 1 or self.RIGHT_EYE_CLOSE_TOTAL != 1 :
                    self.PREVIOUS_RIGHT_EYE_STATE = self.CURRENT_RIGHT_EYE_STATE

                print("[STATUS] : DEBUGGER POINT 13_")

                if self.PREVIOUS_LEFT_EYE_STATE == self.CURRENT_LEFT_EYE_STATE and \
                  self.PREVIOUS_RIGHT_EYE_STATE == self.CURRENT_RIGHT_EYE_STATE :
                    self.patternCaller +=1
                else:
                    self.patternCaller =0

                if self.patternCaller > 3:
                    self.patternResult = threeCombo(self,left_Eye_state, right_Eye_state)
                    if self.patternResult =='PATTERN_11':
                        self.rawCapture.close()
                        self.camera.close()

                    else:
                        print("signal emitter")

            self.rawCapture.truncate(0)
            print("[INFO] : DONE THIS FRAME.NEXT FRAME")
            
        self.rawCapture.close()
        self.camera.close()
#_____________________________________________________________________________________________

#DEBUGGER & TESTING PURPOSE
class DebugWindow(QWidget):

    
    def __init__(self, parent=None):
        super(DebugWindow,self).__init__(parent)
        
        grid = QGridLayout()

        self.groupBox=QGroupBox("FACE NAVIGATION")
        self.mouth_Open_Counter = QLabel("NO. MOUTH OPEN : ")
        self.mouth_Closed_Counter = QLabel("NO. MOUTH CLOSE : ")
        self.mouth_condition = QLabel("MOUTH CONDITION : ")
        self.leftEyeOpen = QLabel("LEFT EYE OPEN COUNTER : ")
        self.leftEyeClose = QLabel("LEFT EYE CLOSE COUNTER: ")
        self.rightEyeOpen = QLabel("RIGHT EYE OPEN COUNTER : ")
        self.rightEyeClose = QLabel("RIGHT EYE CLOSE COUNTER: ")
        self.leftEyeCondition= QLabel("LEFT EYE CONDITION: ")
        self.rightEyeCondition = QLabel("RIGHT EYE CONDITION: ")
        
        self.activateWindow = QLabel("ACTIVATED FRAME : ")    
        
        self.mouth_Open_Counter_Value = QLabel("#")
        self.mouth_Closed_Counter_Value = QLabel("#")
        self.mouth_condition_Value = QLabel("#")
        self.leftEyeOpenValue = QLabel("#")
        self.leftEyeCloseValue = QLabel("#")
        self.rightEyeOpenValue = QLabel("#")
        self.rightEyeCloseValue = QLabel("#")
        self.leftEyeConditionValue= QLabel("#")
        self.rightEyeConditionValue = QLabel("#")
        
        self.activateWindowValue = QLabel("MAIN")
        
        self.work = Navigation()
        self.thread = QThread()

        self.groupBox.setStyleSheet("color: white ;font: bold 12px")

        self.work.Mouth_Open_progress.connect(self.updateDataMO)
        self.work.Mouth_Close_progress.connect(self.updateDataMC)
        self.work.Mouth_State_progress.connect(self.updateDataMS)
        self.work.LeftEye_Open_progress.connect(self.updateDataLEO)
        self.work.LeftEye_Close_progress.connect(self.updateDataLEC)
        self.work.LeftEye_State_progress.connect(self.updateDataLES)
        self.work.RightEye_Open_progress.connect(self.updateDataREO)
        self.work.RightEye_Close_progress.connect(self.updateDataREC)
        self.work.RightEye_State_progress.connect(self.updateDataRES)
        self.work.Pattern_progress.connect(self.updateDataWIN)
       
        self.work.moveToThread(self.thread)
        self.work.finished.connect(self._finished)
        self.thread.started.connect(self.work.navigationMode_1)
        self.thread.start()  
        
        QApplication.processEvents()
        verticalLayout = QVBoxLayout()
        horizontalLayout = QHBoxLayout()
        horizontalLayout1 = QHBoxLayout()
        horizontalLayout2 = QHBoxLayout()
        horizontalLayout3 = QHBoxLayout()
        horizontalLayout4 = QHBoxLayout()
        horizontalLayout5 = QHBoxLayout()
        horizontalLayout6 = QHBoxLayout()
        horizontalLayout7 = QHBoxLayout()
        horizontalLayout8 = QHBoxLayout()
        horizontalLayout9 = QHBoxLayout()

        horizontalLayout.addWidget(self.mouth_Open_Counter)
        horizontalLayout.addWidget(self.mouth_Open_Counter_Value)
        horizontalLayout1.addWidget(self.mouth_Closed_Counter)
        horizontalLayout1.addWidget(self.mouth_Closed_Counter_Value)
        horizontalLayout2.addWidget(self.mouth_condition)
        horizontalLayout2.addWidget(self.mouth_condition_Value)
        horizontalLayout3.addWidget(self.leftEyeOpen)
        horizontalLayout3.addWidget(self.leftEyeOpenValue)
        horizontalLayout4.addWidget(self.leftEyeClose)
        horizontalLayout4.addWidget(self.leftEyeCloseValue)
        horizontalLayout5.addWidget(self.rightEyeOpen)
        horizontalLayout5.addWidget(self.rightEyeOpenValue)
        horizontalLayout6.addWidget(self.rightEyeClose)
        horizontalLayout6.addWidget(self.rightEyeCloseValue)
        horizontalLayout7.addWidget(self.leftEyeCondition)
        horizontalLayout7.addWidget(self.leftEyeConditionValue)
        horizontalLayout8.addWidget(self.rightEyeCondition)
        horizontalLayout8.addWidget(self.rightEyeConditionValue)
        horizontalLayout3.addWidget(self.activateWindow)
        horizontalLayout3.addWidget(self.activateWindowValue)
        
        verticalLayout.addLayout(horizontalLayout)
        verticalLayout.addLayout(horizontalLayout1)
        verticalLayout.addLayout(horizontalLayout2)
        verticalLayout.addLayout(horizontalLayout3)
        verticalLayout.addLayout(horizontalLayout4)
        verticalLayout.addLayout(horizontalLayout5)
        verticalLayout.addLayout(horizontalLayout6)
        verticalLayout.addLayout(horizontalLayout7)
        verticalLayout.addLayout(horizontalLayout8)
        verticalLayout.addLayout(horizontalLayout9)
   
        verticalLayout.addStretch(1)
        self.groupBox.setLayout(verticalLayout)
        
        grid.addWidget(self.groupBox,0,0)

        QApplication.processEvents()
        self.setLayout(grid)
        self.setWindowTitle("EXPRESSION DATA")
        self.resize(400,300)
        self.setStyleSheet("background-color : black ; font :white")
       
    def updateDataMO(self,value):
        print(str(value))
        self.mouth_Open_Counter_Value.setText(str(value))

    def updateDataMC(self,value):
        print(str(value))
        self.mouth_Closed_Counter_Value.setText(str(value))

    def updateDataMS(self,value):
        print(value)
        self.mouth_condition_Value.setText(value)

    def updateDataLEO(self,value):
        print(str(value))
        self.leftEyeOpenValue.setText(str(value))

    def updateDataLEC(self,value):
        print(str(value))
        self.leftEyeCloseValue.setText(str(value))

    def updateDataLES(self,value):
        print(value)
        self.leftEyeConditionValue.setText(value)

    def updateDataREO(self,value):
        print(str(value))
        self.rightEyeOpenValue.setText(str(value))

    def updateDataREC(self,value):
        print(str(value))
        self.rightEyeCloseValue.setText(str(value))

    def updateDataRES(self,value):
        print(value)
        self.rightEyeConditionValue.setText(value)

    def updateDataWIN(self,value):
        print(value)
        self.activateWindowValue.setText(value)

    def _finished(self):
        print("FINISHED.START AGAIN")
        self.thread.quit()
        self.thread.wait()
        self.work.setWindowType('SubWin')
        self.thread.start()


    

#=============================================================================================================

if __name__ == "__main__":
   
    app = QApplication(sys.argv)
    win_sts = MainWindow_V2()
    win_sts.showFullScreen()
    sys.exit(app.exec_())
    

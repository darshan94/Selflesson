from PyQt5.QtCore import QDate, QTime, QDateTime, Qt,QTimer, pyqtSlot, pyqtSignal, QObject, QThread
from PyQt5.QtWidgets import QGridLayout,QDockWidget,QApplication,QWidget,QLabel, QVBoxLayout, QMainWindow, QGroupBox, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap
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

    video_Signal = pyqtSignal(QImage)
    
    finished = pyqtSignal(str)

    def __init__(self):
        super(Navigation,self).__init__()

        self.resetter()

        self.Pbreak = False

        self.winType = "SubWin"

        print("[INFO-NAVIGATION FUNCTION CLASS] : Loading Necessary File")
        
        self.detector=dlib.get_frontal_face_detector()
        self.predictor=dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        (self.lStart,self.lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (self.rStart,self.rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
        (self.mStart,self.mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]
        
        print("[INFO-NAVIGATION FUNCTION CLASS]  : Files loaded into memory ")
        print("[INFO-NAVIGATION FUNCTION CLASS]  : Camera Initialization Started ")
        
        
        
        
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
    
    def eight_Combo(self,_left_Eye_state, _right_Eye_state, _mouth_state):

        print("[INFO-NAVIGATION FUNCTION CLASS]  : eightCombo(self,left_Eye_state, right_Eye_state, mouth_state) called.")
        
        EYES_STATE = self.threeCombo(_left_Eye_state, _right_Eye_state)
        
        if EYES_STATE == 'BOTH_OPEN' and _mouth_state == 'OPEN':
            pattern = 'PATTERN_1'
        elif EYES_STATE == 'PATTERN_10' and _mouth_state == 'OPEN':
            pattern = 'PATTERN_2'
        elif EYES_STATE == 'PATTERN_10' and _mouth_state == 'CLOSED':
            pattern = 'PATTERN_3'
        elif EYES_STATE == 'PATTERN_9' and _mouth_state == 'OPEN':
            pattern = 'PATTERN_4'
        elif EYES_STATE == 'PATTERN_9' and _mouth_state == 'CLOSED':
            pattern = 'PATTERN_5'
        elif EYES_STATE == 'BOTH_OPEN' and _mouth_state == 'CLOSED':
            pattern = 'PATTERN_6'
        elif EYES_STATE == 'PATTERN_11' and _mouth_state == 'OPEN':
            pattern = 'PATTERN_7'
        elif EYES_STATE == 'PATTERN_11' and _mouth_state == 'CLOSED':
            pattern = 'PATTERN_8'
        else:
            pattern = 'VALUE_ERROR'
        print("[INFO-NAVIGATION FUNCTION CLASS]  : "+ pattern )
        return pattern

    def threeCombo(self,left_Eye_state, right_Eye_state):

        print("[INFO-NAVIGATION FUNCTION CLASS]  : threeCombo(self,left_Eye_state, right_Eye_state) called.")
        
        if left_Eye_state == 'CLOSE' and right_Eye_state == 'CLOSE':
            eyePattern = 'PATTERN_11'
        elif left_Eye_state == 'OPEN' and right_Eye_state == 'CLOSE':
            eyePattern = 'PATTERN_10'
        elif left_Eye_state == 'CLOSE' and right_Eye_state == 'OPEN':
            eyePattern = 'PATTERN_9'
        elif left_Eye_state == 'OPEN' and right_Eye_state == 'OPEN':
            eyePattern = 'PATTERN_12'
        else:
            eyePattern = 'VALUE_ERROR'
        print("[INFO-NAVIGATION FUNCTION CLASS]  : "+eyePattern)
        return eyePattern

    def MOUTH_PATTERN(self,_mouth_state):

        print("[INFO-NAVIGATION FUNCTION CLASS]  : MOUTH_PATTERN(self,_mouth_state) called.")
        
        if _mouth_state == 'OPEN':
            mouthpattern = 'PATTERN_14'
        elif _mouth_state == 'CLOSE':
            mouthpattern = 'PATTERN_13'
        else:
            mouthpattern = 'VALUE_ERROR'
        print("[INFO-NAVIGATION FUNCTION CLASS]  : "+mouthpattern)
        return mouthpattern

    def resetter(self):
        print("DEFAULT VALUE IS RESTORED")
        self.MOUTH_AR_THRESH_CLOSED = 0.10
        self.MOUTH_AR_THRESH_OPENED = 0.20
        self.MOUTH_AR_CONSEC_FRAME = 5
        self.EYE_AR_THRESH=0.23
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
        self.open_Counter = 0
        self.closed_Counter = 0

        self.patternSender = 'NONE'
        self.Pbreak = False
       

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

        self.camera = PiCamera()
        self.camera.resolution = (640,480)
        self.camera.framerate = 32
        self.rawCapture = PiRGBArray(self.camera, size=(640,480))
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port = True )
        
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
                self.leftEAR = self.eye_aspect_ratio(self.leftEye)
                print("[STATUS] : LEAR VALUE IS OBTAINED")
                self.rightEAR=self.eye_aspect_ratio(self.rightEye)
                print("[STATUS] : REAR VALUE IS OBTAINED")
#_____QIMAGE____________________________________________________________________________________________________
                for (x,y) in self.shape:
                    cv2.circle(self.image, (x,y), 1,(0, 0, 255), -1)
                print("[STATUS] : CIRCLE LANDMARK DRAWN")
                self.leftEyeHull=cv2.convexHull(self.leftEye)
                self.rightEyeHull=cv2.convexHull(self.rightEye)
                self.mouthEyeHull=cv2.convexHull(self.mouthPoint)
                cv2.drawContours(self.image,[self.leftEyeHull], -1, (0, 255, 0), 1)
                cv2.drawContours(self.image,[self.rightEyeHull], -1, (0, 255, 0), 1)
                cv2.drawContours(self.image,[self.mouthEyeHull], -1, (0, 255, 0), 1)
                print("[STATUS] : CONTOUR DRAWN")
                qimage = QImage(self.image.data,640,480,QImage.Format_RGB888)
                print("[STATUS] : QIMAGE CREATED")
                self.video_Signal.emit(qimage)
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
                    #self.LeftEye_Open_progress.emit(self.LEFT_OPEN_COUNTER)
                    #self.LeftEye_Close_progress.emit(self.LEFT_CLOSE_COUNTER)
                else:
                    print("[STATUS] : LEFT EYE OPEN FOR THIS FRAME")
                    self.LEFT_OPEN_COUNTER+=1
                    self.LEFT_CLOSE_COUNTER = 0
                    #self.LeftEye_Open_progress.emit(self.LEFT_OPEN_COUNTER)
                    #self.LeftEye_Close_progress.emit(self.LEFT_CLOSE_COUNTER)

                if self.rightEAR<self.EYE_AR_THRESH:
                    print("[STATUS] : RIGHT EYE CLOSE FOR THIS FRAME")
                    self.RIGHT_CLOSE_COUNTER+=1
                    self.RIGHT_OPEN_COUNTER = 0
                    #self.RightEye_Open_progress.emit(self.RIGHT_OPEN_COUNTER)
                    #self.RightEye_Close_progress.emit(self.RIGHT_CLOSE_COUNTER)

                else:
                    print("[STATUS] : RIGHT EYE OPEN FOR THIS FRAME")
                    self.RIGHT_OPEN_COUNTER += 1
                    self.RIGHT_CLOSE_COUNTER = 0
                    #self.RightEye_Open_progress.emit(self.RIGHT_OPEN_COUNTER)
                    #self.RightEye_Close_progress.emit(self.RIGHT_CLOSE_COUNTER)

#_____STAGE_2___________________________________________________________________________________________________

                print("[STATUS] : STAGE 2")

                
                if self.LEFT_CLOSE_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                    print("[STATUS] : LEFT EYE CLOSE VALIDATED")
                    self.CURRENT_LEFT_EYE_STATE = "CLOSE"
                    self.LEFT_EYE_OPEN_TOTAL += 1
                    self.LEFT_EYE_CLOSE_TOTAL = 0
                    self.LEFT_CLOSE_COUNTER = 0
                    self.LEFT_OPEN_COUNTER = 0
                    #self.LeftEye_State_progress.emit(self.CURRENT_LEFT_EYE_STATE)
                    
                else:
                    if self.LEFT_OPEN_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                        print("[STATUS] : LEFT EYE OPEN VALIDATED")
                        self.CURRENT_LEFT_EYE_STATE = "OPEN"
                        self.LEFT_EYE_CLOSE_TOTAL += 1
                        self.LEFT_EYE_OPEN_TOTAL = 0
                        self.LEFT_OPEN_COUNTER = 0
                        self.LEFT_CLOSE_TOTAL = 0
                        #self.LeftEye_State_progress.emit(self.CURRENT_LEFT_EYE_STATE)

                    else:
                        print("[STATUS] : LEFT EYE NOT DEFINED")
                        self.CURRENT_LEFT_EYE_STATE = "NOT DEFINED"
                        #self.LeftEye_State_progress.emit(self.CURRENT_LEFT_EYE_STATE)

                if self.RIGHT_CLOSE_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                    print("[STATUS] : RIGHT EYE CLOSE VALIDATED")
                    self.CURRENT_RIGHT_EYE_STATE = "CLOSE"
                    self.RIGHT_EYE_OPEN_TOTAL += 1
                    self.RIGHT_EYE_CLOSE_TOTAL = 0
                    self.RIGHT_CLOSE_COUNTER = 0
                    self.RIGHT_OPEN_COUNTER = 0
                    #self.RightEye_State_progress.emit(self.CURRENT_RIGHT_EYE_STATE)
                    
                else:
                    if self.RIGHT_OPEN_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                        print("[STATUS] : RIGHT EYE OPEN VALIDATED")
                        self.CURRENT_RIGHT_EYE_STATE = "OPEN"
                        self.RIGHT_EYE_CLOSE_TOTAL += 1
                        self.RIGHT_EYE_OPEN_TOTAL = 0
                        self.RIGHT_OPEN_COUNTER = 0
                        self.RIGHT_CLOSE_COUNTER = 0
                        #self.RightEye_State_progress.emit(self.CURRENT_RIGHT_EYE_STATE)

                    else:
                        print("[STATUS] : RIGHT EYE NOT DEFINED")
                        self.CURRENT_RIGHT_EYE_STATE = "NOT DEFINED"
                        #self.RightEye_State_progress.emit(self.CURRENT_RIGHT_EYE_STATE)
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

                if self.winType == "MainWin":
                    self.patternSender = self.eight_Combo(self.CURRENT_LEFT_EYE_STATE, self.CURRENT_RIGHT_EYE_STATE, self.CURRENT_MOUTH_STATE)
                    if self.patternSender != 'VALUE_ERROR':
                        #self.Pattern_progress.emit(self.patternSender)
                        self.Pbreak = True
                        break

                elif self.winType == "SubWin":
                    print("[STATUS] : DEBUGGER POINT 11_11")
                    self.patternSender = self.threeCombo(self.CURRENT_LEFT_EYE_STATE, self.CURRENT_RIGHT_EYE_STATE)
                    if self.patternSender != 'VALUE_ERROR':
                        print(self.patternSender)
                        print("[STATUS] : PATTERN SIGNAL SENDING") 
                        #self.Pattern_progress.emit(self.patternSender)
                        print("[STATUS] : PATTERN SIGNAL SENT")
                        self.Pbreak = True
                        break

                else:
                    print("CONITNUE")
                    
            if self.Pbreak == True :
                break
            else:
                self.rawCapture.truncate(0)
                print("[STATUS] : DONE THIS FRAME.NEXT FRAME")
            
        self.rawCapture.close()
        self.camera.close()
        print("FINISHED")
        
        self.finished.emit(self.patternSender)
        self.resetter()


#_____________________________________________________________________________________________

#DEBUGGER & TESTING PURPOSE
class DebugWindow(QWidget):

    
    def __init__(self, parent=None):
        super(DebugWindow,self).__init__(parent)

        self.live = QLabel("IMAGE")
        #pixmap = QPixmap()
        
        grid = QGridLayout()

        self.groupBox=QGroupBox("FACE NAVIGATION")
        self.mouth_Open_Counter = QLabel("NO. MOUTH OPEN : ")
        self.mouth_Closed_Counter = QLabel("NO. MOUTH CLOSE : ")
        self.mouth_condition = QLabel("MOUTH CONDITION : ")
        self.eyes_Open_Counter = QLabel("NO. EYES OPEN : ")
        self.eyes_Closed_Counter = QLabel("NO. EYES CLOSE : ")
        self.eyes_condition = QLabel("EYES CONDITION : ")
        #self.leftEyeOpen = QLabel("LEFT EYE OPEN COUNTER : ")
        #self.leftEyeClose = QLabel("LEFT EYE CLOSE COUNTER: ")
        #self.rightEyeOpen = QLabel("RIGHT EYE OPEN COUNTER : ")
        #self.rightEyeClose = QLabel("RIGHT EYE CLOSE COUNTER: ")
        #self.leftEyeCondition= QLabel("LEFT EYE CONDITION: ")
        #self.rightEyeCondition = QLabel("RIGHT EYE CONDITION: ")

        
        
        self.activateWindow = QLabel("ACTIVATED FRAME : ")    
        
        self.mouth_Open_Counter_Value = QLabel("#")
        self.mouth_Closed_Counter_Value = QLabel("#")
        self.mouth_condition_Value = QLabel("#")
        self.eyes_Open_Counter_Value = QLabel("#")
        self.eyes_Closed_Counter_Value = QLabel("#")
        self.eyes_condition_Value = QLabel("#")

        
        #self.leftEyeOpenValue = QLabel("#")
        #self.leftEyeCloseValue = QLabel("#")
        #self.rightEyeOpenValue = QLabel("#")
        #self.rightEyeCloseValue = QLabel("#")
        #self.leftEyeConditionValue= QLabel("#")
       # self.rightEyeConditionValue = QLabel("#")
        
        self.activateWindowValue = QLabel("MAIN")
        
        self.work = Navigation()
        self.thread = QThread()

        self.groupBox.setStyleSheet("color: white ;font: bold 12px")

        self.work.Mouth_Open_progress.connect(self.updateDataMO)
        self.work.Mouth_Close_progress.connect(self.updateDataMC)
        self.work.Mouth_State_progress.connect(self.updateDataMS)
        #self.work.LeftEye_Open_progress.connect(self.updateDataLEO)
        #self.work.LeftEye_Close_progress.connect(self.updateDataLEC)
        #self.work.LeftEye_State_progress.connect(self.updateDataLES)
        #self.work.RightEye_Open_progress.connect(self.updateDataREO)
        #self.work.RightEye_Close_progress.connect(self.updateDataREC)
        #self.work.RightEye_State_progress.connect(self.updateDataRES)
        self.work.Pattern_progress.connect(self.updateDataWIN)

        self.work.video_Signal.connect(self.image_data_slot)
       
        self.work.moveToThread(self.thread)
        self.work.finished.connect(self._finished)
        self.thread.started.connect(self.work.navigationMode_1)
        self.work.setWindowType("SubWin")
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
        horizontalLayout10 = QHBoxLayout()
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
        horizontalLayout9.addWidget(self.activateWindow)
        horizontalLayout9.addWidget(self.activateWindowValue)
        horizontalLayout10.addWidget(self.live)
        
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
        verticalLayout.addLayout(horizontalLayout10)
   
        verticalLayout.addStretch(1)
        self.groupBox.setLayout(verticalLayout)
        
        grid.addWidget(self.groupBox,0,0)

        QApplication.processEvents()
        self.setLayout(grid)
        self.setWindowTitle("EXPRESSION DATA")
        self.resize(400,300)
        self.setStyleSheet("background-color : black ; font :white")

    def image_data_slot(self,image_data):
        print("IMAGE RECEIVED")
        pix = QPixmap.fromImage(image_data)
        pix_image = QPixmap(pix)
        self.live.setPixmap(pix_image)
        self.live.setAlignment(Qt.AlignCenter)
        print("IMAGE RECEIVED 2")
               
    def updateDataMO(self,value):
        #print(str(value))
        self.mouth_Open_Counter_Value.setText(str(value))

    def updateDataMC(self,value):
        #print(str(value))
        self.mouth_Closed_Counter_Value.setText(str(value))

    def updateDataMS(self,value):
        #print(value)
        self.mouth_condition_Value.setText(value)

    def updateDataLEO(self,value):
        #print(str(value))
        self.leftEyeOpenValue.setText(str(value))

    def updateDataLEC(self,value):
        #print(str(value))
        self.leftEyeCloseValue.setText(str(value))

    def updateDataLES(self,value):
        #print(value)
        self.leftEyeConditionValue.setText(value)

    def updateDataREO(self,value):
        #print(str(value))
        self.rightEyeOpenValue.setText(str(value))

    def updateDataREC(self,value):
        #print(str(value))
        self.rightEyeCloseValue.setText(str(value))

    def updateDataRES(self,value):
        #print(value)
        self.rightEyeConditionValue.setText(value)

    def updateDataWIN(self,value):
        #print(value)
        self.activateWindowValue.setText(value)

    def _finished(self):
        print("FINISHED.START AGAIN")
        self.thread.quit()
        self.thread.wait()
        self.work.setWindowType('SubWin')
        time.sleep(3)
        print("FINISHED.START AGAINsttt")
        self.thread.start()




class QStartLiveVideoWidget(QWidget):
    def __init__(self,parent=None):
        super(QStartLiveVideoWidget,self).__init__(parent)
        self.image = QImage()
        self._min_size = (30,30)

    def image_data_slot(self,image_data):
        print("IMAGE RECEIVED")
        self.image = image_data
        print("IMAGE RECEIVED 2")
        if self.image.size() != self.size():
            print("IMAGE RECEIVED 3 ")
            self.setFixedSize(self.image.size())
            print("IMAGE RECEIVED 3 ")
        print("IMAGE RECEIVED 4")
        self.update()
        print("IMAGE RECEIVED 5")

    def paintEvent(self,event):
        painter = QPainter(self)
        painter.drawImage(0,0,self.Image)
        self.image = QtGui.QImage()

                           
    

#=============================================================================================================

if __name__ == "__main__":
   
    app = QApplication(sys.argv)
    win_sts = DebugWindow()
    win_sts.show()
    sys.exit(app.exec_())



'''
                if self.patternCaller >= 4:
                    print("[STATUS] : DEBUGGER POINT 15_0")
                    #self.patternResult = eightCombo(self.CURRENT_LEFT_EYE_STATE, \
                    #                                self.CURRENT_RIGHT_EYE_STATE, self.CURRENT_MOUTH_STATE)
                    print("[STATUS] : DEBUGGER POINT 15_1")
                    self.Pattern_progress.emit(self.patternResult)
                    print("[STATUS] : DEBUGGER POINT 15_2")
                    self.finished.emit()
                    #self.rawCapture.close()
                    #self.camera.close()
                    print("[STATUS] : FINISHED")
                    break

                else:
                    print("[STATUS] : DEBUGGER POINT 16_") '''

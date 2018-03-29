#   CREATED BY DARSHAN
#   DATE : 19 MARCH && 5.15AM
#   PURPOSE : TO CREATE EMAIL WIDGET


from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread

from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import time
import imutils
import dlib
import cv2



class Navigation(QThread):

    Mouth_Open_progress = pyqtSignal(int)
    Mouth_Close_progress = pyqtSignal(int)
    Mouth_State_progress = pyqtSignal(str)
    LeftEye_Open_progress = pyqtSignal(int)
    LeftEye_Close_progress = pyqtSignal(int)
    LeftEye_State_progress = pyqtSignal(str)
    RightEye_Open_progress = pyqtSignal(int)
    RightEye_Close_progress = pyqtSignal(int)
    RightEye_State_progress = pyqtSignal(str)

    MOUTH_OPEN_TOTAL = 0 #TO KEEP TRACK ON NUMBER OF MOUTH CLOSED
    activate_Module_1 = False

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

        self.winSelect = 'mainWin'

        print("[INFO] : Loading Predictor...")
        self.detector=dlib.get_frontal_face_detector()
        self.predictor=dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        (self.lStart,self.lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (self.rStart,self.rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
        (self.mStart,self.mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]
        print("[INFO] : Done Loaded Predictor...")
        self.open_Counter = 0
        self.closed_Counter = 0
        self.camera = PiCamera()
        self.camera.resolution = (640,480)
        self.camera.framerate = 32
        self.rawCapture = PiRGBArray(self.camera, size=(640,480))
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port = True )
        print("[INFO] : Warming camera...")

        time.sleep(4)

    def __del__(self):
        self.wait()
        
    def _mouth_aspect_ratio(self,mouth):
        A=dist.euclidean(mouth[13], mouth[19])
        B=dist.euclidean(mouth[14], mouth[18])
        C=dist.euclidean(mouth[15], mouth[17])
        D=dist.euclidean(mouth[12], mouth[16])
        mar=(A+B+C)/(2.0 * D)
        return mar

    def eye_aspect_ratio(self,eye):
        A=dist.euclidean(eye[1], eye[5])
        B=dist.euclidean(eye[2], eye[4])
        C=dist.euclidean(eye[0], eye[3])
        ear=(A+B)/(2.0 * C)
        return ear       
    @pyqtSlot()
    def run(self):

        print("[INFO] : ENTERED RUN FUNCTION")
 
        for f in self.stream:
            self.image = f.array
            print("[INFO] : Reading Frame")
            self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            print("[INFO] : accesss opencv")
            self.rects=self.detector(self.gray, 0)
            print("[INFO] : accesss detector")
            for rect in self.rects:
                self.shape=self.predictor(self.gray, rect)
                print("[INFO] : LANDMARK POINT IS EXTRACTED")
                self.shape=face_utils.shape_to_np(self.shape)
                print("[INFO] : LANDMARK POINT CONVERTED INTO NUMPY ARRAY")
                self.mouthPoint = self.shape[self.mStart:self.mEnd]
                print("[INFO] : MOUTH PART IS EXTRACTED")
                self.leftEye=self.shape[self.lStart:self.lEnd]
                print("[INFO] : LEFT EYE PART IS EXTRACTED")
                self.rightEye=self.shape[self.rStart:self.rEnd]
                print("[INFO] : RIGHT EYE PART IS EXTRACTED")
                self.mouthMAR = self._mouth_aspect_ratio(self.mouthPoint)
                print("[INFO] : MAR VALUE IS OBTAINED")
                self.leftEAR=self.eye_aspect_ratio(self.leftEye)
                print("[INFO] : LEAR VALUE IS OBTAINED")
                self.rightEAR=self.eye_aspect_ratio(self.rightEye)
                print("[INFO] : REAR VALUE IS OBTAINED")

#_____STAGE_1___________________________________________________________________________________________________


                print("[INFO] : STAGE 1")
                
                if self.mouthMAR < self.MOUTH_AR_THRESH_CLOSED :
                    print("[INFO] : MOUTH CLOSE FOR THIS FRAME")
                    self.closed_Counter+=1
                    self.open_Counter = 0
                    self.Mouth_Open_progress.emit(self.open_Counter)
                    self.Mouth_Close_progress.emit(self.closed_Counter)

                else:
                    if self.mouthMAR > self.MOUTH_AR_THRESH_OPENED :
                        print("[INFO] : MOUTH OPEN FOR THIS FRAME")
                        self.open_Counter += 1
                        self.closed_Counter = 0
                        self.Mouth_Open_progress.emit(self.open_Counter)
                        self.Mouth_Close_progress.emit(self.closed_Counter)

                    else:
                        print("[INFO] : NO MOUTH DATA FOR THIS FRAME")
                        self.closed_Counter = 0
                        self.open_Counter = 0
                        self.Mouth_Open_progress.emit(self.open_Counter)
                        self.Mouth_Close_progress.emit(self.closed_Counter)

                if self.leftEAR<self.EYE_AR_THRESH:
                    print("[INFO] : LEFT EYE CLOSE FOR THIS FRAME")
                    self.LEFT_CLOSE_COUNTER+=1
                    self.LEFT_OPEN_COUNTER = 0
                    self.LeftEye_Open_progress.emit(self.LEFT_OPEN_COUNTER)
                    self.LeftEye_Close_progress.emit(self.LEFT_CLOSE_COUNTER)
                else:
                    print("[INFO] : LEFT EYE OPEN FOR THIS FRAME")
                    self.LEFT_OPEN_COUNTER+=1
                    self.LEFT_CLOSE_COUNTER = 0
                    self.LeftEye_Open_progress.emit(self.LEFT_OPEN_COUNTER)
                    self.LeftEye_Close_progress.emit(self.LEFT_CLOSE_COUNTER)

                if self.rightEAR<self.EYE_AR_THRESH:
                    print("[INFO] : RIGHT EYE CLOSE FOR THIS FRAME")
                    self.RIGHT_CLOSE_COUNTER+=1
                    self.RIGHT_OPEN_COUNTER = 0
                    self.RightEye_Open_progress.emit(self.RIGHT_OPEN_COUNTER)
                    self.RightEye_Close_progress.emit(self.RIGHT_CLOSE_COUNTER)

                else:
                    print("[INFO] : RIGHT EYE OPEN FOR THIS FRAME")
                    self.RIGHT_OPEN_COUNTER += 1
                    self.RIGHT_CLOSE_COUNTER = 0
                    self.RightEye_Open_progress.emit(self.RIGHT_OPEN_COUNTER)
                    self.RightEye_Close_progress.emit(self.RIGHT_CLOSE_COUNTER)




#_____STAGE_2___________________________________________________________________________________________________

                print("[INFO] : STAGE 2")
                
                if self.LEFT_CLOSE_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                    print("[INFO] : LEFT EYE CLOSE VALIDATED")
                    self.CURRENT_LEFT_EYE_STATE = "OPEN"
                    self.LEFT_EYE_OPEN_TOTAL += 1
                    self.LEFT_EYE_CLOSE_TOTAL = 0
                    self.LEFT_CLOSE_COUNTER = 0
                    self.LEFT_OPEN_COUNTER = 0
                    self.LeftEye_State_progress.emit(self.CURRENT_LEFT_EYE_STATE)
                    
                else:
                    if self.LEFT_OPEN_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                        print("[INFO] : LEFT EYE OPEN VALIDATED")
                        self.CURRENT_LEFT_EYE_STATE = "CLOSE"
                        self.LEFT_EYE_CLOSE_TOTAL += 1
                        self.LEFT_EYE_OPEN_TOTAL = 0
                        self.LEFT_OPEN_COUNTER = 0
                        self.LEFT_CLOSE_TOTAL = 0
                        self.LeftEye_State_progress.emit(self.CURRENT_LEFT_EYE_STATE)

                    else:
                        print("[INFO] : LEFT EYE NOT DEFINED")
                        self.CURRENT_LEFT_EYE_STATE = "NOT DEFINED"
                        self.LeftEye_State_progress.emit(self.CURRENT_LEFT_EYE_STATE)

                if self.RIGHT_CLOSE_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                    print("[INFO] : RIGHT EYE CLOSE VALIDATED")
                    self.CURRENT_RIGHT_EYE_STATE = "OPEN"
                    self.RIGHT_EYE_OPEN_TOTAL += 1
                    self.RIGHT_EYE_CLOSE_TOTAL = 0
                    self.RIGHT_CLOSE_COUNTER = 0
                    self.RIGHT_OPEN_COUNTER = 0
                    self.RightEye_State_progress.emit(self.CURRENT_RIGHT_EYE_STATE)
                    
                else:
                    if self.RIGHT_OPEN_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                        print("[INFO] : RIGHT EYE OPEN VALIDATED")
                        self.CURRENT_RIGHT_EYE_STATE = "CLOSE"
                        self.RIGHT_EYE_CLOSE_TOTAL += 1
                        self.RIGHT_EYE_OPEN_TOTAL = 0
                        self.RIGHT_OPEN_COUNTER = 0
                        self.RIGHT_CLOSE_COUNTER = 0
                        self.RightEye_State_progress.emit(self.CURRENT_RIGHT_EYE_STATE)

                    else:
                        print("[INFO] : RIGHT EYE NOT DEFINED")
                        self.CURRENT_RIGHT_EYE_STATE = "NOT DEFINED"
                        self.RightEye_State_progress.emit(self.CURRENT_RIGHT_EYE_STATE)
                        print("[INFO] : RIGHT EYE NOT DEFINED SIGNAL SENT")
                
                if self.open_Counter >= self.MOUTH_AR_CONSEC_FRAME :     
                    print("[INFO] : MOUTH OPEN VALIDATED")
                    self.CURRENT_MOUTH_STATE= "OPEN"
                    self.TOTAL_MOUTH_OPEN_TOTAL += 1
                    self.TOTAL_MOUTH_CLOSE_TOTAL = 0
                    self.Mouth_State_progress.emit(self.CURRENT_MOUTH_STATE)

                else:
                    if self.closed_Counter >= self.MOUTH_AR_CONSEC_FRAME:
                        print("[INFO] : MOUTH CLOSE VALIDATED")
                        self.CURRENT_MOUTH_STATE = "CLOSE"
                        self.TOTAL_MOUTH_CLOSE_TOTAL += 1
                        self.TOTAL_MOUTH_OPEN_TOTAL = 0
                        self.Mouth_State_progress.emit(self.CURRENT_MOUTH_STATE)

                    else:
                        print("[INFO] : MOUTH NOT DEFINED VALIDATED")
                        self.CURRENT_MOUTH_STATE = "NOT DEFINED"
                        print("[INFO] : MOUTH NOT DEFINED VALIDATED SIGNAL WILL BE SENT")
                        self.Mouth_State_progress.emit(self.CURRENT_MOUTH_STATE)
                        print("[INFO] : MOUTH NOT DEFINED VALIDATED SIGNAL SENT")

#_____STAGE_3___________________________________________________________________________________________________
               # print("[INFO] : DEBUGGER POINT 11_")


              #  if LEFT_EYE_OPEN_TOTAL != 1 or LEFT_EYE_CLOSE_TOTAL != 1 :
              #      PREVIOUS_LEFT_EYE_STATE = CURRENT_LEFT_EYE_STATE
              #  if RIGHT_EYE_OPEN_TOTAL != 1 or RIGHT_EYE_CLOSE_TOTAL != 1 :
             #       PREVIOUS_RIGHT_EYE_STATE = CURRENT_RIGHT_EYE_STATE
             #   if TOTAL_MOUTH_CLOSE_TOTAL != 1 or TOTAL_MOUTH_OPEN_TOTAL != 1 :
              #      PREVIOUS_MOUTH_STATE = CURRENT_MOUTH_STATE
                

             #   if PREVIOUS_LEFT_EYE_STATE == CURRENT_LEFT_EYE_STATE and \
             #     PREVIOUS_RIGHT_EYE_STATE == CURRENT_RIGHT_EYE_STATE and PREVIOUS_MOUTH_STATE == CURRENT_MOUTH_STATE :
             #       print("signal emitter")
                    

        

            self.rawCapture.truncate(0)
            print("[INFO] : DONE THIS FRAME.NEXT FRAME")
            
        self.rawCapture.close()
        self.camera.close()



class MainWindow(QWidget):

    
    def __init__(self, parent=None):
        super(MainWindow,self).__init__(parent)
        
        grid = QGridLayout()

        self.groupBox=QGroupBox("FACE NAVIGATION")
        self.mouth_Open_Counter = QLabel("MOUTH OPEN COUNTER : ")
        self.mouth_Closed_Counter = QLabel("MOUTH CLOSE COUNTER: ")
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


        self.groupBox.setStyleSheet("color: white ;font: bold 30px")

        #self.thread = QThread()
        self.thread = Navigation()
        #self.work.moveToThread(self.thread)
       # print(self.work.threadName)
        #self.thread.started.connect(self.work.runit)
        self.thread.Mouth_Open_progress.connect(self.updateMODate)
        self.thread.Mouth_Close_progress.connect(self.updateMCDate)
        self.thread.Mouth_State_progress.connect(self.updateMSDate)

        self.thread.LeftEye_Open_progress.connect(self.updateLEODate)
        self.thread.LeftEye_Close_progress.connect(self.updateLECDate)
        self.thread.LeftEye_State_progress.connect(self.updateLESDate)

        self.thread.RightEye_Open_progress.connect(self.updateREODate)
        self.thread.RightEye_Close_progress.connect(self.updateRECDate)
        self.thread.RightEye_State_progress.connect(self.updateRESDate) 
        
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
        horizontalLayout9.addWidget(self.activateWindow)
        horizontalLayout9.addWidget(self.activateWindowValue)
        
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

    @pyqtSlot(int)
    def updateMODate(self,value):
        print(str(value))
        self.mouth_Open_Counter_Value.setText(str(value))

    @pyqtSlot(int)
    def updateMCDate(self,value):
        print(str(value))
        self.mouth_Closed_Counter_Value.setText(str(value))

    @pyqtSlot(str)
    def updateMSDate(self,value):
        print("SIGNAL RECEIVED :"+value)
        self.mouth_condition_Value.setText(value)


    @pyqtSlot(int)
    def updateLEODate(self,value):
        print(str(value))
        self.leftEyeOpenValue.setText(str(value))

    @pyqtSlot(int)
    def updateLECDate(self,value):
        print(str(value))
        self.leftEyeCloseValue.setText(str(value))

    @pyqtSlot(str)
    def updateLESDate(self,value):
        print(value)
        self.leftEyeConditionValue.setText(value)

    @pyqtSlot(int)
    def updateREODate(self,value):
        print(str(value))
        self.rightEyeCloseValue.setText(str(value))

    @pyqtSlot(int)
    def updateRECDate(self,value):
        print(str(value))
        self.rightEyeCloseValue.setText(str(value))

    @pyqtSlot(str)
    def updateRESDate(self,value):
        print(value)
        self.rightEyeConditionValue.setText(value)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    analysisWin = MainWindow()
    analysisWin.show()
    #analysisWin.showFullScreen()
    sys.exit(app.exec_())


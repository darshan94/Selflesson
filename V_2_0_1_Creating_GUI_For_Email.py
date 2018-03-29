#   CREATED BY DARSHAN
#   DATE : 19 MARCH && 5.15AM
#   PURPOSE : TO CREATE EMAIL WIDGET


from PyQt5.QtCore import (Qt,QThread,pyqtSignal)
from PyQt5.QtWidgets import (QApplication, QGridLayout, QGroupBox, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QLineEdit)

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

    patternSignal = pyqtSignal(str)

    MOUTH_OPEN_TOTAL = 0 #TO KEEP TRACK ON NUMBER OF MOUTH CLOSED
    activate_Module_1 = False

    def __init__(self):
        QThread.__init__(self)
        self.MOUTH_AR_THRESH_CLOSED = 0.10
        self.MOUTH_AR_THRESH_OPENED = 0.20
        self.MOUTH_AR_CONSEC_FRAME = 96
        self.EYE_AR_THRESH=0.3
        self.EYE_AR_CONSEC_FRAMES = 3 

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

    def eightCombo(self,left_Eye_state, right_Eye_state, mouth_state):
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

    def signalEmitter(self,patternType):
        self.patternSignal.emit(self.patternType)

    def windowInfo(self,win_type):
        self.winSelect = win_type

    def patternSelector(self,left_Eye_state, right_Eye_state, mouth_state):
        
        self.patternOut = 'None'
        if self.winSelect == 'mainWin':
            self.patternOut = eightCombo(self,left_Eye_state, right_Eye_state, mouth_state)
        elif self.winSelect == 'subWin'
            self.patternOut = threeCombo(self,left_Eye_state, right_Eye_state)
        else:
            patternOut = 'ERROR WINDOW'

        signalEmitter(self.patternOut)
    
            
    
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

                if self.mouthMAR < self.MOUTH_AR_THRESH_CLOSED :
                    print("[INFO] : MOUTH MAR LESS THAN MOUTH_AR_THRESH_CLOSED")
                    self.closed_Counter+=1
                    self.open_Counter = 0
                    self.Mouth_Open_progress.emit(self.open_Counter)
                    self.Mouth_Close_progress.emit(self.closed_Counter)

                else:
                    if self.mouthMAR > self.MOUTH_AR_THRESH_OPENED :
                        print("[INFO] : DEBUGGER POINT 6")
                        self.open_Counter += 1
                        self.closed_Counter = 0
                        self.Mouth_Open_progress.emit(self.open_Counter)
                        self.Mouth_Close_progress.emit(self.closed_Counter)
                        print("[INFO] : DEBUGGER POINT 7")

                    else:
                        print("[INFO] : DEBUGGER POINT 8")
                        self.closed_Counter = 0
                        self.open_Counter = 0
                        self.Mouth_Open_progress.emit(self.open_Counter)
                        self.Mouth_Close_progress.emit(self.closed_Counter)

                if self.leftEAR<self.EYE_AR_THRESH:  
                    self.LEFT_CLOSE_COUNTER+=1
                    self.LEFT_OPEN_COUNTER = 0 
                else:
                    self.LEFT_OPEN_COUNTER+=1
                    self.LEFT_CLOSE_COUNTER = 0

                if self.rightEAR<self.EYE_AR_THRESH:  
                    self.RIGHT_CLOSE_COUNTER+=1
                    self.RIGHT_OPEN_COUNTER = 0

                else:
                    self.RIGHT_OPEN_COUNTER += 1
                    self.RIGHT_CLOSE_COUNTER = 0

#_____STAGE_2___________________________________________________________________________________________________

                if self.LEFT_CLOSE_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                    self.CURRENT_LEFT_EYE_STATE = "OPEN"
                    self.LEFT_EYE_OPEN_TOTAL += 1
                    self.LEFT_EYE_CLOSE_TOTAL = 0
                    self.LEFT_CLOSE_COUNTER = 0
                    self.LEFT_OPEN_COUNTER = 0

                    
                else:
                    if self.LEFT_OPEN_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                        self.CURRENT_LEFT_EYE_STATE = "CLOSE"
                        self.LEFT_EYE_CLOSE_TOTAL += 1
                        self.LEFT_EYE_OPEN_TOTAL = 0
                        self.LEFT_OPEN_COUNTER = 0
                        self.LEFT_CLOSE_TOTAL = 0

                    else
                        self.CURRENT_LEFT_EYE_STATE = "NOT DEFINED"

                if self.RIGHT_CLOSE_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                    self.CURRENT_RIGHT_EYE_STATE = "OPEN"
                    self.RIGHT_EYE_OPEN_TOTAL += 1
                    self.RIGHT_EYE_CLOSE_TOTAL = 0
                    self.RIGHT_CLOSE_COUNTER = 0
                    self.RIGHT_OPEN_COUNTER = 0
                    
                else:
                    if self.RIGHT_OPEN_COUNTER >=self.EYE_AR_CONSEC_FRAMES:
                        self.CURRENT_RIGHT_EYE_STATE = "CLOSE"
                        self.RIGHT_EYE_CLOSE_TOTAL += 1
                        self.RIGHT_EYE_OPEN_TOTAL = 0
                        self.RIGHT_OPEN_COUNTER = 0
                        self.RIGHT_CLOSE_COUNTER = 0

                    else
                        self.CURRENT_RIGHT_EYE_STATE = "NOT DEFINED"
                
                print("[INFO] : DEBUGGER POINT 9")
                if self.open_Counter >= self.MOUTH_AR_CONSEC_FRAME :     # IF MOUTH-OPEN FRAME EXCEEDED 2 SEC
                    print("[INFO] : DEBUGGER POINT 10")
                    self.CURRENT_MOUTH_STATE= "OPEN"
                    self.TOTAL_MOUTH_OPEN_TOTAL += 1
                    self.TOTAL_MOUTH_CLOSE_TOTAL = 0
                    self.Mouth_State_progress.emit(self.MOUTH_STATE)

                else:
                    if self.closed_Counter >= self.MOUTH_AR_CONSEC_FRAME:
                        self.CURRENT_MOUTH_STATE = "CLOSE"
                        self.TOTAL_MOUTH_CLOSE_TOTAL += 1
                        self.TOTAL_MOUTH_OPEN_TOTAL = 0
                        self.Mouth_State_progress.emit(self.MOUTH_STATE)

                    else:
                        print("[INFO] : DEBUGGER POINT 14_")
                        self.MOUTH_STATE = "NOT DEFINED"
                        self.Mouth_State_progress.emits(self.MOUTH_STATE)

#_____STAGE_3___________________________________________________________________________________________________
                print("[INFO] : DEBUGGER POINT 11_")


                if LEFT_EYE_OPEN_TOTAL != 1 or LEFT_EYE_CLOSE_TOTAL != 1 :
                    PREVIOUS_LEFT_EYE_STATE = CURRENT_LEFT_EYE_STATE
                if RIGHT_EYE_OPEN_TOTAL != 1 or RIGHT_EYE_CLOSE_TOTAL != 1 :
                    PREVIOUS_RIGHT_EYE_STATE = CURRENT_RIGHT_EYE_STATE
                if TOTAL_MOUTH_CLOSE_TOTAL != 1 or TOTAL_MOUTH_OPEN_TOTAL != 1 :
                    PREVIOUS_MOUTH_STATE = CURRENT_MOUTH_STATE
                

                if PREVIOUS_LEFT_EYE_STATE == CURRENT_LEFT_EYE_STATE and \
                   PREVIOUS_RIGHT_EYE_STATE == CURRENT_RIGHT_EYE_STATE and PREVIOUS_MOUTH_STATE == CURRENT_MOUTH_STATE :
                    

        
            print("[INFO] : DEBUGGER POINT 12_")
            self.rawCapture.truncate(0)
            print("[INFO] : DEBUGGER POINT 13_")
            
        self.rawCapture.close()
        self.camera.close()



class MainWindow(QWidget):

    
    def __init__(self, parent=None):
        super(MainWindow,self).__init__(parent)
        
        grid = QGridLayout()

        self.groupBox=QGroupBox("FACE NAVIGATION")
        self.mouth_Open_Counter = QLabel("NO. MOUTH OPEN : ")
        self.mouth_Closed_Counter = QLabel("NO. MOUTH CLOSE : ")
        self.mouth_condition = QLabel("MOUTH EXPRESSION : ")
        
        self.activateWindow = QLabel("ACTIVATED FRAME : ")    
        
        self.mouth_Open_Counter_Value = QLabel()
        self.mouth_Closed_Counter_Value = QLabel()
        self.mouth_condition_Value = QLabel()
        self.activateWindowValue = QLabel("MAIN")

        self.thread = Navigation()
        self.thread.Mouth_Open_progress.connect(self.updateMODate)
        self.thread.Mouth_Close_progress.connect(self.updateMCDate)
        self.thread.Mouth_State_progress.connect(self.updateMSDate)
        self.thread.start()
        QApplication.processEvents()
        verticalLayout = QVBoxLayout()
        horizontalLayout = QHBoxLayout()
        horizontalLayout1 = QHBoxLayout()
        horizontalLayout2 = QHBoxLayout()
        horizontalLayout3 = QHBoxLayout()

        horizontalLayout.addWidget(self.mouth_Open_Counter)
        horizontalLayout.addWidget(self.mouth_Open_Counter_Value)
        horizontalLayout1.addWidget(self.mouth_Closed_Counter)
        horizontalLayout1.addWidget(self.mouth_Closed_Counter_Value)
        horizontalLayout2.addWidget(self.mouth_condition)
        horizontalLayout2.addWidget(self.mouth_condition_Value)
        horizontalLayout3.addWidget(self.activateWindow)
        horizontalLayout3.addWidget(self.activateWindowValue)
        
        
        verticalLayout.addLayout(horizontalLayout)
        verticalLayout.addLayout(horizontalLayout1)
        verticalLayout.addLayout(horizontalLayout2)
        verticalLayout.addLayout(horizontalLayout3)
   
        verticalLayout.addStretch(1)
        self.groupBox.setLayout(verticalLayout)
        
        grid.addWidget(self.groupBox,0,0)

        QApplication.processEvents()
        self.setLayout(grid)
        self.setWindowTitle("EXPRESSION DATA")
        self.resize(400,300)


    def updateMODate(self,value):
        print(str(value))
        self.mouth_Open_Counter_Value.setText(str(value))

    def updateMCDate(self,value):
        print(str(value))
        self.mouth_Closed_Counter_Value.setText(str(value))

    def updateMSDate(self,value):
        print(value)
        self.mouth_condition_Value.setText(value)





if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    analysisWin = MainWindow()
    analysisWin.show()
    #analysisWin.showFullScreen()
    sys.exit(app.exec_())


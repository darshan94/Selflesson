#   CREATED BY DARSHAN
#   DATE : 18 MARCH & 5.55PM
#   PURPOSE : BugFix for v1.1.0
#   DONE : SENDING SIGNAL TO GUI SUCCESSFULLY



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

    MOUTH_OPEN_TOTAL = 0 #TO KEEP TRACK ON NUMBER OF MOUTH CLOSED
    activate_Module_1 = False

    def __init__(self):
        QThread.__init__(self)
        self.MOUTH_AR_THRESH_CLOSED = 0.10
        self.MOUTH_AR_THRESH_OPENED = 0.20
        self.MOUTH_AR_CONSEC_FRAME = 10
        self.MOUTH_OPEN = False
        self.MOUTH_CLOSED = False

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
                print("[INFO] : Loading Predictor On Loop")
                self.shape=face_utils.shape_to_np(self.shape)
                print("[INFO] : DEBUGGER POINT 1")
                self.mouthPoint = self.shape[self.mStart:self.mEnd]
                print("[INFO] : DEBUGGER POINT 2")
                self.mouthMAR = self._mouth_aspect_ratio(self.mouthPoint)
                print("[INFO] : DEBUGGER POINT 3")

                if self.mouthMAR < self.MOUTH_AR_THRESH_CLOSED :
                    print("[INFO] : DEBUGGER POINT 4")
                    self.closed_Counter+=1
                    #EXPRESSION_STATE = 'CLOSED'
                    self.open_Counter = 0
                    self.Mouth_Open_progress.emit(open_Counter)
                    self.Mouth_Close_progress.emit(closed_Counter)
                    

                else:
                    print("[INFO] : DEBUGGER POINT 5")
                    if self.mouthMAR > self.MOUTH_AR_THRESH_OPENED :
                        print("[INFO] : DEBUGGER POINT 6")
                        self.open_Counter += 1
                        #EXPRESSION_STATE = 'SMILE'
                        self.closed_Counter = 0
                        self.Mouth_Open_progress.emit(self.open_Counter)
                        self.Mouth_Close_progress.emit(self.closed_Counter)
                        print("[INFO] : DEBUGGER POINT 7")

                    else:
                        print("[INFO] : DEBUGGER POINT 8")
                        #EXPRESSION_STATE = 'NEUTRAL'
                        self.closed_Counter = 0
                        self.open_Counter = 0
                        self.Mouth_Open_progress.emit(open_Counter)
                        self.Mouth_Close_progress.emit(closed_Counter)

                print("[INFO] : DEBUGGER POINT 9")
                if self.open_Counter >= self.MOUTH_AR_CONSEC_FRAME :     # IF MOUTH-OPEN FRAME EXCEEDED 2 SEC
                    #MOUTH_OPEN = True
                    print("[INFO] : DEBUGGER POINT 10")
                    self.MOUTH_STATE= "OPEN"
                    #break
                    print("[STATE} : MOUTH OPEN")
                    self.Mouth_State_progress.emits(MOUTH_STATE)
                    #rawCapture.truncate(0)
                    #continue
                else:
                    if self.closed_Counter >= self.MOUTH_AR_CONSEC_FRAME:
                        #MOUTH_CLOSED = True
                        #MOUTH_STATE = "CLOSE"
                        #break
                        self.MOUTH_STATE = "CLOSE"
                        self.Mouth_State_progress.emits(MOUTH_STATE)
                        #rawCapture.truncate(0)
                        #continue
                print("[INFO] : DEBUGGER POINT 11_")
                    

        
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
        #grid.addWidget(self.createExampleGroup(),1,0)
        
        #self.label = QLabel("jju")  -- TESTING PURPOSE - TO CHECK GUI UPDATE 
        #grid.addWidget(self.label,0,0)
        #self.thread = TestSignal()
        #self.thread.progress.connect(self.updateDate)
        #self.thread.start()
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
        print(str(value))
        self.mouth_condition_Value.setText(str(value))

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    analysisWin = MainWindow()
    analysisWin.show()
    #analysisWin.showFullScreen()
    sys.exit(app.exec_())


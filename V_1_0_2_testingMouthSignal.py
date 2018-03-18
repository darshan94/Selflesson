#   CREATED BY DARSHAN
#   DATE : 18 MARCH & 5.55PM
#   PURPOSE : Test Signal receive from Mouth Detection in desire GUI



from PyQt5.QtCore import (Qt,QThread,pyqtSignal)
from PyQt5.QtWidgets import (QApplication, QGridLayout, QGroupBox, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QLineEdit)

from picamera.array import PiRGBArray
from picamera import PiCamera


from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import time
import imutils
import dlib
import cv2

class TestSignal(QThread):

    progress = pyqtSignal(int)
    
    def __init__(self):
        super(TestSignal,self).__init__()

    def __del__(self):
        self.wait()

    def run(self):
        for i in range(100):
            self.progress.emit(i)
            time.sleep(1)



    
class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow,self).__init__(parent)
        
        grid = QGridLayout()

        self.groupBox=QGroupBox("FACE NAVIGATION")
        self.patternPrediction = QLabel("PREDICTION : ")
        self.activateWindow = QLabel("ACTIVATED FRAME : ")    
        
        self.patternPredictionValue = QLabel()
        self.activateWindowValue = QLabel("MAIN")

        self.thread = TestSignal()
        self.thread.progress.connect(self.updateDate)
        self.thread.start()
        QApplication.processEvents()
        verticalLayout = QVBoxLayout()
        horizontalLayout = QHBoxLayout()
        horizontalLayout1 = QHBoxLayout()

        horizontalLayout.addWidget(self.patternPrediction)
        horizontalLayout.addWidget(self.patternPredictionValue)
        horizontalLayout1.addWidget(self.activateWindow)
        horizontalLayout1.addWidget(self.activateWindowValue)
        
        
        verticalLayout.addLayout(horizontalLayout)
        verticalLayout.addLayout(horizontalLayout1)
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


    def updateDate(self,value):
        print(str(value))
        self.patternPredictionValue.setText(str(value))

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    analysisWin = MainWindow()
    analysisWin.show()
    #analysisWin.showFullScreen()
    sys.exit(app.exec_())

'''
#ALGORITHM SECTION

#MOUTH CONFIGURATION

def mouth_aspect_ratio(mouth):
    A=dist.euclidean(mouth[13], mouth[19])
    B=dist.euclidean(mouth[14], mouth[18])
    C=dist.euclidean(mouth[15], mouth[17])
    D=dist.euclidean(mouth[12], mouth[16])
    mar=(A+B+C)/(2.0 * D)
    return mar

MOUTH_OPEN_TOTAL = 0 #TO KEEP TRACK ON NUMBER OF MOUTH CLOSED
activate_Module_1 = False
#-----------------------------------------------------------------------------


#==============================================================================

#PROGRAM START

class getMouthDate(QThread):

    progress = pyqtSignal(str)
    
    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()
        
    def run(self):

        MOUTH_AR_THRESH_CLOSED = 0.10
        MOUTH_AR_THRESH_OPENED = 0.20
        MOUTH_AR_CONSEC_FRAME = 10
        MOUTH_OPEN = False
        MOUTH_CLOSED = False

        open_Counter = 0
        closed_Counter = 0

        
        print("[INFO] : Loading Predictor...")
        detector=dlib.get_frontal_face_detector()
        predictor=dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        (lStart,lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (rStart,rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
        (mStart,mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]
        print("[INFO] : Warming camera...")

        camera = PiCamera()
        camera.resolution = (640,480)
        camera.framerate = 32
        rawCapture = PiRGBArray(camera, size=(640, 480))
        time.sleep(4)

        print("[INFO] : Camera ready...?")
        print("[INFO] : Rolliingggggg sirrr")

        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port = True ):
            image = frame.array
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            rects=detector(gray, 0)

            for rect in rects:
                shape=predictor(gray, rect)
                shape=face_utils.shape_to_np(shape)

                mouthPoint = shape[mStart:mEnd]      
                mouthMAR = mouth_aspect_ratio(mouthPoint)
                for (x,y) in shape:
                    cv2.circle(image, (x,y), 1,(0, 0, 255), -1)

                mouthEyeHull=cv2.convexHull(mouthPoint)
                cv2.drawContours(image,[mouthEyeHull], -1, (0, 255, 0), 1)

                cv2.putText(image, "EAR: {:.2F}".format(mouthMAR), (300,30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255),2)
            
                if mouthMAR < MOUTH_AR_THRESH_CLOSED :
                    closed_Counter+=1
                    EXPRESSION_STATE = 'CLOSED'
                    open_Counter = 0
                    

                else:
                    if mouthMAR > MOUTH_AR_THRESH_OPENED :
                        open_Counter += 1
                        EXPRESSION_STATE = 'SMILE'
                        closed_Counter = 0

                    else:
                        EXPRESSION_STATE = 'NEUTRAL'
                        closed_Counter = 0
                        open_Counter = 0

                
                if open_Counter >= MOUTH_AR_CONSEC_FRAME :     # IF MOUTH-OPEN FRAME EXCEEDED 2 SEC
                    #MOUTH_OPEN = True
                    #MOUTH_STATE= "OPEN"
                    #break
                    self.progress.emits(MOUTH_STATE)
                    rawCapture.truncate(0)
                    continue
                else:
                    if closed_Counter >= MOUTH_AR_CONSEC_FRAME:
                        #MOUTH_CLOSED = True
                        #MOUTH_STATE = "CLOSE"
                        #break
                        MOUTH_STATE = "CLOSE"
                        self.progress.emits(MOUTH_STATE)
                        rawCapture.truncate(0)
                        continue
                    
                    #else:
                      #  EXPRESSION_STATE = 'NEUTRAL'               # MAINTAIN THIS MAIN PROGRAM

            
                cv2.putText(image, "closed_Counter: {}".format(closed_Counter), (300,80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
                cv2.putText(image, "open_Counter: {}".format(open_Counter), (300,120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
                cv2.putText(image, "MOUTH STATE: {}".format(EXPRESSION_STATE), (10,30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)

        
            cv2.imshow("LIVE CAMERA",image)
            rawCapture.truncate(0)
            #if MOUTH_OPEN == True or MOUTH_CLOSED == True:
                #break
            key=cv2.waitKey(1)&0xFF
            if key == ord("q"):
                break
        
        camera.close()
        cv2.destroyAllWindows()
  #      return MOUTH_STATE



class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow,self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.label = QLabel(self)
        self.label.setText("MOUTH STATE: " )
        self.label1 = QLabel(self)
        self.label1.setText("EMPTY")

        self.thread = getMouthDate()
        self.thread.progress.connect(self.changeValue)
        self.thread.start()

        self.setWindowTitle("EXPRESSION DATA")
        self.resize(400,300)

    def changeValue(self, value):
        self.label1.setText(value)        
    

def main():
    app = QApplication(sys.argv)
    analysisWin = MainWindow()
    analysisWin.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
'''

#   CREATED BY DARSHAN
#   DATE : 18 MARCH & 5AM
#   PURPOSE : Deliverable 1



from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QApplication, QGridLayout, QGroupBox, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QLineEdit)

import numpy as np
import time


class TestSignal(QObject):

    progress_signzl = pyqtSignal(int)
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
        
    
class MainWindow(QWidget):
    
    def __init__(self, parent=None):
        super(MainWindow,self).__init__(parent)
        
        grid = QGridLayout()
        
        self.label = QLabel("jju")
        grid.addWidget(self.label,0,0)
        self.work = TestSignal()
        self.thread = QThread()
        self.work.progress_signzl.connect(self.updateDate)
        self.work.moveToThread(self.thread)
        self.work.finished.connect(self._finished)
        nuu=5
        self.thread.started.connect(self.work.progress)
        
        self.thread.start()      
        QApplication.processEvents()
        self.setLayout(grid)
        self.setWindowTitle("EXPRESSION DATA")
        self.resize(400,300)

    def updateDate(self,value):
        self.label.setText(str(value))

    def _finished(self):
        print("FINISHED.START AGAIN")
        self.thread.quit()
        self.thread.wait()
        self.work.setterNum(5)
        self.thread.start()

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

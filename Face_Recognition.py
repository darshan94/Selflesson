# By Darshan
# Integrate GUI qt with backend
# Version 4


from PyQt5.QtCore import QDate, QTime, QDateTime, Qt,QTimer, pyqtSlot, pyqtSignal, QObject, QThread
from PyQt5.QtWidgets import QGridLayout,QDockWidget,QApplication,QWidget,QLabel, QVBoxLayout, QMainWindow, QGroupBox, QVBoxLayout, QHBoxLayout


from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time
import dlib
import cv2


class FACE_AUTHENICATION(QObject):
    user_Recognized = pyqtSignal()
    user_Not_Recognized = pyqtSignal()
    no_face_detected = pyqtSignal()
    face_detected = pyqtSignal()
    process_Status = pyqtSignal(str)
    finished =pyqtSignal()

    def __init__(self, parent=None):
        super(FACE_AUTHENICATION,self).__init__(parent)

        print("[INFO_FACERECOGNITION] : FACE RECOGNITION CONSTRUCTOR CALLED")

        self.HAAR_FACES = 'haarcascade_frontalface.xml'
        self.TRAINING_FILE = 'training.xml'
        self.haar_faces = cv2.CascadeClassifier(self.HAAR_FACES)
        self.HAAR_SCALE_FACTOR = 1.3
        self.HAAR_MIN_NEIGHBORS = 4
        self.HAAR_MIN_SIZE = (30, 30)
        self.FACE_WIDTH = 92
        self.FACE_HEIGHT = 112

        self.recognitionAlgorithm = 1
        self.lbphThreshold = 80
        self.current_user = None
        self.last_match = 0
        self.detection_active = True
        self.same_user_detected_in_row = 0

        self.model = cv2.face.LBPHFaceRecognizer_create(self.lbphThreshold)
        self.model.read(self.TRAINING_FILE)

    def detect_single(self,image):

        self.faces = self.haar_faces.detectMultiScale(image, scaleFactor=self.HAAR_SCALE_FACTOR, minNeighbors=self.HAAR_MIN_NEIGHBORS, minSize=self.HAAR_MIN_SIZE, flags=cv2.CASCADE_SCALE_IMAGE)
        if len(self.faces) != 1:
            return None
        return self.faces[0]

    def crop(self,image, x, y, w, h):
        crop_height = int((self.FACE_HEIGHT // float(self.FACE_WIDTH)) * w)
        midy = y + h // 2
        y1 = max(0, midy - crop_height // 2)
        y2 = min(image.shape[0] - 1, midy + crop_height // 2)
        return image[y1:y2, x:x + w] 

    def resize(image):
        return cv2.resize(image, (FACE_WIDTH,FACE_HEIGHT), interpolation=cv2.INTER_LANCZOS4)

    
    def _FACE_RECOGNITION(self):
        
        
        print("[INFO_FACERECOGNITION] : CAMERA WARMING UP")
        
        self.camera = PiCamera()
        self.camera.resolution = (640,480)
        self.camera.framerate = 32
        self.rawCapture = PiRGBArray(self.camera, size=(640, 480))
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port = True )
        
        time.sleep(3)
        
        print("[INFO_FACERECOGNITION] : CAMERA READY")

        print("[INFO_FACERECOGNITION] : STREAMING STARTED")
        
        for frame in self.stream :
            self.Face_image = frame.array
            self.Face_image = cv2.cvtColor(self.Face_image, cv2.COLOR_RGB2GRAY)
            self.result = self.detect_single(self.Face_image)
            if self.result is None:                                                                                                              # Set x,y coordinates, height and width from face detection result
                print("[INFO_FACERECOGNITION] : NO FACE FOUND ")
                self.no_face_detected.emit()
                self.FaceDetect = "NO FACE FOUND"
                self.process_Status.emit(self.FaceDetect)
                self.rawCapture.truncate(0)
                continue

            self.FaceDetect = "FACE FOUND"
            self.process_Status.emit(self.FaceDetect)
            self.face_detected.emit()
            
            self.x, self.y, self.w, self.h = self.result # Crop image on face. If algorithm is not LBPH also resize because in all other algorithms image resolution has to be the same as training image resolution.

            if self.recognitionAlgorithm == 1:
                self.cropped = self.crop(self.Face_image, self.x, self.y, self.w, self.h)
            else:
                self.cropped = self.resize(crop(self.Face_image, self.x, self.y, self.w, self.h))
            # Test face against model.
            self.label, self.confidence = self.model.predict(self.cropped)
            # We have a match if the label is not "-1" which equals unknown because of exceeded threshold and is not "0" which are negtive training images (see training folder).
            if (self.label != -1 and self.label != 0):
                # Routine to count how many times the same user is detected
                if (self.label == self.last_match):
                    # if same user as last time increment same_user_detected_in_row +1
                    self.same_user_detected_in_row += 1
                    print("[STATUS] : INCREMENT 1")
                    self.STATUS = 'SAME MATCH FOUND.STAY IDLE'
                    self.process_Status.emit(self.STATUS)
                if self.label != self.last_match:
                    # if the user is diffrent reset same_user_detected_in_row back to 0
                    self.same_user_detected_in_row = 0
                    print("[STATUS] : RESET COUNTER ")
                    self.STATUS = 'DIFFERENT MATCH FOUND.STAY IDLE'
                    self.process_Status.emit(self.STATUS)
                # A user only gets logged in if he is predicted twice in a row minimizing prediction errors.
                if  (self.same_user_detected_in_row > 5):
                    print("[STATUS] : USER LOG IN ")
                    self.STATUS = 'USER LOG IN'
                    self.user_Recognized.emit()
                    self.process_Status.emit(self.STATUS)
                    break
                # set last_match to current prediction
                self.last_match = self.label
                print("[STATUS] : MATCH FOUND")
                self.STATUS = 'SAME MATCH FOUND.STAY IDLE'
                self.process_Status.emit(self.STATUS)

            else:
                print("[STATUS] : USER NOT RECOGNIZED  ")
                self.STATUS = 'USER NOT RECOGNIZED'
                self.process_Status.emit(self.STATUS)
                self.user_Not_Recognized.emit()
                self.rawCapture.truncate(0)
                break

            self.rawCapture.truncate(0)

        self.camera.close()
        self.finished.emit()  

class FACE_RECOGNITION_GUI(QWidget):

    face_Recognized = pyqtSignal()
    
    def __init__(self, parent=None):

        print("[FACE RECOGNITION WIDGET STATUS] : FACE_RECOGNITION_GUI CONSTRUCTOR CALLED")
        
        super(FACE_RECOGNITION_GUI,self).__init__(parent)

        self.USER_RECOGNIZED = False
        
        grid = QGridLayout()
        
        self.AUTHENICATION_STATUS = QLabel("STATUS : ")
        self.AUTHENICATION_STATUS.setAlignment(Qt.AlignCenter)
        grid.addWidget(self.AUTHENICATION_STATUS,0,0)


        self.FACE_AUTHENICATION_OBJ = FACE_AUTHENICATION()
        self.FACE_RECOG_THREAD = QThread()

        self.FACE_AUTHENICATION_OBJ.user_Recognized.connect(self.userRecognized)
        self.FACE_AUTHENICATION_OBJ.user_Not_Recognized.connect(self.userNotRecognized)
        self.FACE_AUTHENICATION_OBJ.process_Status.connect(self.updateStatusData)
        self.FACE_AUTHENICATION_OBJ.finished.connect(self._FINISHED)

        self.FACE_AUTHENICATION_OBJ.moveToThread(self.FACE_RECOG_THREAD)
        self.FACE_RECOG_THREAD.started.connect(self.FACE_AUTHENICATION_OBJ._FACE_RECOGNITION)
        

        
        QApplication.processEvents()

        self.setStyleSheet( """QLabel{ color : white ; font-size : 40px ; font-weight : bold }  QWidget{ background-color : black}""")

        
        self.setLayout(grid)
        self.resize(900,300)
        

    def START_RECOGNIZATION(self):
        self.FACE_RECOG_THREAD.start()

    def updateStatusData(self,value):
        self.AUTHENICATION_STATUS.setText("STATUS : "+ value)

    def _FINISHED(self):
        print("[INFO-FACE-RECOGNITION-GUI] : FINISH SIGNAL RECEIVED")
        self.FACE_RECOG_THREAD.quit()
        self.FACE_RECOG_THREAD.wait()
        if self.USER_RECOGNIZED == False:
            time.sleep(2)
            self.AUTHENICATION_STATUS.setText("STATUS : RECOGNIZATION STARTED AGAIN")
            time.sleep(1)                                  
            self.START_RECOGNIZATION()

        else:
            self.face_Recognized.emit()
            self.close()                                             
          
    def userNotRecognized(self):
        print("[INFO-FACE-RECOGNITION-GUI] : USER_NOT_RECOGNIZED SIGNAL RECEIVED")
        self.USER_RECOGNIZED = False

    def userRecognized(self):
        print("[INFO-FACE-RECOGNITION-GUI] : USER_RECOGNIZED SIGNAL RECEIVED")
        self.USER_RECOGNIZED = True

    def get_USER_STATE(self):
        return self.USER_RECOGNIZED

if __name__ == "__main__":
   
    import sys
    app = QApplication(sys.argv)

    FACE_RECOGNITION_GUI_OBJ = FACE_RECOGNITION_GUI()

    FACE_RECOGNITION_GUI_OBJ


    
    sys.exit(app.exec_())







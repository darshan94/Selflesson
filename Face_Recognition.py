# By Darshan
# Convert Normal Function into Class form
# Version 2

from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time
import dlib
import cv2


class FACE_AUTHENICATION():
    #user_Recognized = pyqtSignal(str)
    #user_Not_Recognized = pyqtSignal(str)
    #no_face_detected = pyqtSignal()
    #face_detected = pyqtSignal()
    #finished =pyqtSignal()

    def __init__(self, parent=None):
        super(FACE_AUTHENICATION,self).__init__()

        self.HAAR_FACES = 'haarcascade_frontalface.xml'
        self.TRAINING_FILE = 'training.xml'
        self.haar_faces = cv2.CascadeClassifier(self.HAAR_FACES)
        self.HAAR_SCALE_FACTOR = 1.3
        self.HAAR_MIN_NEIGHBORS = 4
        self.HAAR_MIN_SIZE = (30, 30)
        self.FACE_WIDTH = 92
        self.FACE_HEIGHT = 112

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
        
        self.recognitionAlgorithm = 1
        self.lbphThreshold = 80
        self.current_user = None
        self.last_match = 0
        self.detection_active = True
        self.same_user_detected_in_row = 0

    
        print("[INFO_FACERECOGNITION] : Loads resource for Face_Recognition")

        self.model = cv2.face.LBPHFaceRecognizer_create(self.lbphThreshold)
        self.model.read(self.TRAINING_FILE)
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
                print("[INFO_FACERECOGNITION] : No face is detected ")
                
                #self.no_face_detected.emit()
                self.rawCapture.truncate(0)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                continue
            
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
                    self.STATUS = 'SAME MATCH'
                if self.label != self.last_match:
                    # if the user is diffrent reset same_user_detected_in_row back to 0
                    self.same_user_detected_in_row = 0
                    print("[STATUS] : RESET COUNTER ")
                    self.STATUS = 'RESET COUNTER'
                # A user only gets logged in if he is predicted twice in a row minimizing prediction errors.
                if  (self.same_user_detected_in_row > 5):
                    
                    # Callback current user to node helper
                    print("[STATUS] : USER LOG IN ")
                    self.STATUS = 'USER LOG IN'
                    return True
                    break
                # set last_match to current prediction
                self.last_match = self.label
                print("[STATUS] : MATCH FOUND")
                self.STATUS = 'MATCH FOUND'

            else:
                print("[STATUS] : USER NOT RECOGNIZED  ")
                self.STATUS = 'USER NOT RECOGNIZED'
                return False
                cv2.imshow("FRAME", image)
                self.rawCapture.truncate(0)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                continue

            self.rawCapture.truncate(0)

        self.camera.close()
        cv2.destroyAllWindows()
   





if __name__ == "__main__":
   
    testObj = FACE_AUTHENICATION()
    testObj._FACE_RECOGNITION()







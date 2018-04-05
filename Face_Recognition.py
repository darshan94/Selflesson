from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time
import dlib
import cv2

FACE_WIDTH = 92
FACE_HEIGHT = 112
    
HAAR_FACES = 'haarcascade_frontalface.xml'
TRAINING_FILE = 'training.xml'
haar_faces = cv2.CascadeClassifier(HAAR_FACES)
HAAR_SCALE_FACTOR = 1.3
HAAR_MIN_NEIGHBORS = 4
HAAR_MIN_SIZE = (30, 30)


def detect_single(image):

    faces = haar_faces.detectMultiScale(image, scaleFactor=HAAR_SCALE_FACTOR, minNeighbors=HAAR_MIN_NEIGHBORS, minSize=HAAR_MIN_SIZE, flags=cv2.CASCADE_SCALE_IMAGE)
    if len(faces) != 1:
        return None
    return faces[0]

def crop(image, x, y, w, h):

    crop_height = int((FACE_HEIGHT // float(FACE_WIDTH)) * w)
    midy = y + h // 2
    y1 = max(0, midy - crop_height // 2)
    y2 = min(image.shape[0] - 1, midy + crop_height // 2)
    return image[y1:y2, x:x + w]

def resize(image):
 
    return cv2.resize(image, (FACE_WIDTH,FACE_HEIGHT), interpolation=cv2.INTER_LANCZOS4)

def FACE_RECOGNITION():
    recognitionAlgorithm = 1
    lbphThreshold = 80
    current_user = None
    last_match = 0
    detection_active = True
    same_user_detected_in_row = 0

    
    print("[INFO} : Loads resource for Face_Recognition")

    model = cv2.face.LBPHFaceRecognizer_create(lbphThreshold)
    model.read(TRAINING_FILE)
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
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        result = detect_single(image)
        if result is None:                                                                                                              # Set x,y coordinates, height and width from face detection result
            print("[STATUS] : No face is detected ")
            cv2.imshow("FRAME", image)
            rawCapture.truncate(0)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            continue
        x, y, w, h = result # Crop image on face. If algorithm is not LBPH also resize because in all other algorithms image resolution has to be the same as training image resolution.

        if recognitionAlgorithm == 1:
            cropped = crop(image, x, y, w, h)
        else:
            cropped = resize(crop(image, x, y, w, h))
        # Test face against model.
        label, confidence = model.predict(cropped)
        # We have a match if the label is not "-1" which equals unknown because of exceeded threshold and is not "0" which are negtive training images (see training folder).
        if (label != -1 and label != 0):
            # Routine to count how many times the same user is detected
            if (label == last_match):
                # if same user as last time increment same_user_detected_in_row +1
                same_user_detected_in_row += 1
                print("[STATUS] : INCREMENT 1")
                STATUS = 'SAME MATCH'
            if label != last_match:
                # if the user is diffrent reset same_user_detected_in_row back to 0
                same_user_detected_in_row = 0
                print("[STATUS] : RESET COUNTER ")
                STATUS = 'RESET COUNTER'
            # A user only gets logged in if he is predicted twice in a row minimizing prediction errors.
            if  (same_user_detected_in_row > 5):
                
                # Callback current user to node helper
                print("[STATUS] : USER LOG IN ")
                STATUS = 'USER LOG IN'
                return True
                break
            # set last_match to current prediction
            last_match = label
            print("[STATUS] : MATCH FOUND")
            STATUS = 'MATCH FOUND'

        else:
            print("[STATUS] : USER NOT RECOGNIZED  ")
            STATUS = 'USER NOT RECOGNIZED'
            return False
            cv2.imshow("FRAME", image)
            rawCapture.truncate(0)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            continue

        
        cv2.imshow("FRAME", image)
        rawCapture.truncate(0)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break


    camera.close()
    cv2.destroyAllWindows()


FACE_RECOGNITION()

import socket,os

import cv2
import numpy as np
import math
import ORM
# Camera settings
DEFAULT_CAM = 0 # Built-in camera
USB_CAM = 1 # External camera connected via USB port

CAM_SELECTED = DEFAULT_CAM
CAM_WIDTH = 1280
CAM_HEIGHT = 720
CAM_FPS = 30
FLIP_CAMERA_FRAME_HORIZONTALLY = True

# mediapipe parameters
MAX_HANDS = 2
DETECTION_CONF = 0.5
TRACKING_CONF = 0.5
MODEL_COMPLEX = 1
HAND_1 = 0
HAND_2 = 1
INDEX_FINGER_TIP = 8
X_COORD = 0
Y_COORD = 1
lEFT_CONTROL_UI_START = (100, 100)
lEFT_CONTROL_UI_END = (300, 500)
LEFT_CONTROL_CAP = (0,100)
RIGHT_CONTROL_UI_START = (1000, 100)
RIGHT_CONTROL_UI_END = (1200, 500)
RIGHT_CONTROL_CAP = (1000,100)




# Drawing parameters - for opencv
CIR_RADIUS = 50
CIR_COLOR = (252, 207,3 )
CIR_THICKNESS = 3

BORD_CIR_COLOR = (0, 255, 0)
BORD_CIR_THICKNESS = 3

SELECT_POINT = 300
SELECT_COLOR = (0, 0, 255)
SELECT_THICKNESS = 3

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
sock.bind(('127.0.0.1', 3939))  
sock.listen()  
cam = cv2.VideoCapture(CAM_SELECTED) # CAP_DSHOW enables direct show without buffering
cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)    # Set width of the frame
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)  # Set height of the frame
cam.set(cv2.CAP_PROP_FPS, CAM_FPS)  # Set fps of the camera
cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG')) # Set the codec as 'MJPG'
SendHand = False
findHands = ORM.MpHands()

class PyMain():
    LEFT_val = 0
    RIGHT_val = 0
    y_hold = (0,0)
    def __init__(self):
        self.cam = cv2.VideoCapture(CAM_SELECTED) # CAP_DSHOW enables direct show without buffering
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)    # Set width of the frame
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)  # Set height of the frame
        self.cam.set(cv2.CAP_PROP_FPS, CAM_FPS)  # Set fps of the camera
        self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG')) # Set the codec as 'MJPG'
    def waitClient(self):
        self.connection,self.address = sock.accept()  
        print('Connected by', self.address)
    def run(self):
        while True:
            success, frame = self.cam.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue
            if FLIP_CAMERA_FRAME_HORIZONTALLY:
                frame = cv2.flip(frame, 1)
            #frame = findHands.findHands(frame)
            lmList = findHands.marks(frame)
            
            self.frame = frame
            self.drawUI()
            frame = self.frame
            for hand in lmList:
                if len(hand) != 0:
                    x, y = hand[INDEX_FINGER_TIP][X_COORD], hand[INDEX_FINGER_TIP][Y_COORD]
                    cv2.circle(frame, (x, y), CIR_RADIUS, CIR_COLOR, CIR_THICKNESS)
                    chk = self.checkBound(x,y)
                    val = self.drawRECT(frame,x,y,CIR_COLOR,-1,chk)
                    print(val)
                    if chk == 'left':
                        PyMain.LEFT_val = val
                    elif chk == 'right':
                        PyMain.RIGHT_val = val
                
                
                
            cv2.imshow("frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
    def getResponse(self):
        try:
            data = self.connection.recv(1024)
            if not data:
                return None
            return data
        except:
            return None
    def drawRECT(self,frame, x, y, color,size,chk):
        if chk == "left":
            left_val = round(1 - (y - lEFT_CONTROL_UI_START[1]) / (lEFT_CONTROL_UI_END[1] - lEFT_CONTROL_UI_START[1]),2)
            print("left_val", left_val)
            #draw rect from start to left_val 
            cv2.rectangle(frame, lEFT_CONTROL_UI_END, (lEFT_CONTROL_UI_START[0], y), color, size)
            cv2.putText(frame, str(left_val), LEFT_CONTROL_CAP, cv2.FONT_HERSHEY_PLAIN, 3, CIR_COLOR, 3)
            return left_val
        elif chk == "right":
            right_val = round(1- (y - RIGHT_CONTROL_UI_START[1]) / (RIGHT_CONTROL_UI_END[1] - RIGHT_CONTROL_UI_START[1]),2)
            print("right_val", right_val)
            cv2.rectangle(frame, RIGHT_CONTROL_UI_END, (RIGHT_CONTROL_UI_START[0], y),color, size)
            cv2.putText(frame, str(right_val), RIGHT_CONTROL_CAP, cv2.FONT_HERSHEY_PLAIN, 3, CIR_COLOR, 3)
            return right_val
        return None
    def drawUI(self):
        cv2.rectangle(self.frame, lEFT_CONTROL_UI_START, lEFT_CONTROL_UI_END, CIR_COLOR, CIR_THICKNESS)
        cv2.rectangle(self.frame, RIGHT_CONTROL_UI_START, RIGHT_CONTROL_UI_END, CIR_COLOR, CIR_THICKNESS)
    def checkBound(self,x,y):
        #check if x,y is in the control ui
        if x > lEFT_CONTROL_UI_START[0] and x < lEFT_CONTROL_UI_END[0] and y > lEFT_CONTROL_UI_START[1] and y < lEFT_CONTROL_UI_END[1]:
            return "left"
        elif x > RIGHT_CONTROL_UI_START[0] and x < RIGHT_CONTROL_UI_END[0] and y > RIGHT_CONTROL_UI_START[1] and y < RIGHT_CONTROL_UI_END[1]:
            return "right"
        else:
            return "none"
if __name__ == "__main__":
    a = PyMain()
    a.run()
        
        

        
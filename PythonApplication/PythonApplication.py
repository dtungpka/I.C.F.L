import socket,os,sys
import time
import cv2
import numpy as np
import math
import ORM
import threading
from http.server import BaseHTTPRequestHandler,HTTPServer
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
LEFT_CONTROL_CAP = (100,100)
RIGHT_CONTROL_UI_START = (1000, 100)
RIGHT_CONTROL_UI_END = (1200, 500)
RIGHT_CONTROL_CAP = (1000,100)

COMMANDS_RESPOND = {

    'STOP':'Server stopped',
    'ORM_ENABLED':'Optical recognition module enabled',
    'ORM_DISABLED':'Optical recognition module disabled',
    }

COMMANDS_TO_SEND = {
    'LED':'Set LED to %d', #L20
    'FAN':'Set Fan to %d',
    'OMF':'', #ORM frame
    'SCH':"Create schedule" #WIP
}

# Drawing parameters - for opencv
CIR_RADIUS = 50
CIR_COLOR = (252, 207,3 )
CIR_THICKNESS = 3

BORD_CIR_COLOR = (0, 255, 0)
BORD_CIR_THICKNESS = 3

SELECT_POINT = 300
SELECT_COLOR = (0, 0, 255)
SELECT_THICKNESS = 3
IP = 'localhost'
PORT = 3939
MJPEG_PORT = 39399
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
sock.bind((IP, MJPEG_PORT))  
sock.listen()  
command_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
command_sock.bind((IP, PORT)) 
command_sock.listen() 
findHands = ORM.MpHands()



class mjpgServer(BaseHTTPRequestHandler):
    """
    A simple mjpeg server that either publishes images directly from a camera
    or republishes images from another pygecko process.
    """

    ip = None
    hostname = None
    
    def do_GET(self):
        print('connection from:', self.address_string())
        print(self.path)
        if self.ip is None or self.hostname is None:
            self.ip = IP
            self.hostname = socket.gethostname()
            
        if self.path == '/mjpeg':
            self.send_response(200)
            self.send_header(
                'Content-type',
                'multipart/x-mixed-replace; boundary=--jpgboundary'
            )
            self.end_headers()

            while True:
                
                    # print('cam')
                img = PyMain.cam_feed
                    
                
                if img is None:
                    print('no image from camera')
                    continue

                ret, jpg = cv2.imencode('.jpg', img)
                # print 'Compression ratio: %d4.0:1'%(compress(img.size,jpg.size))
                self.wfile.write("--jpgboundary".encode("utf-8"))
                self.send_header('Content-type', 'image/jpeg')
                # self.send_header('Content-length',str(tmpFile.len))
                self.send_header('Content-length', str(jpg.size))
                self.end_headers()
                self.wfile.write(jpg.tobytes())



        elif self.path == '/':
            # hn = self.server.server_address[0]
            port = self.server.server_address[1]
            ip = self.ip
            hostname = self.hostname

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<html><head></head><body>'.encode("utf-8"))
            self.wfile.write('<h1>{0!s}[{1!s}]:{2!s}</h1>'.format(hostname, ip, port).encode("utf-8"))
            self.wfile.write('<img src="http://{}:{}/mjpg"/>'.format(ip, port).encode("utf-8"))
            self.wfile.write('<p>{0!s}</p>'.format((self.version_string())).encode("utf-8"))
            # self.wfile.write('<p>The mjpg stream can be accessed directly at:<ul>')
            # self.wfile.write('<li>http://{0!s}:{1!s}/mjpg</li>'.format(ip, port))
            # self.wfile.write('<li><a href="http://{0!s}:{1!s}/mjpg"/>http://{0!s}:{1!s}/mjpg</a></li>'.format(hostname, port))
            # self.wfile.write('</p></ul>')
            self.wfile.write('<p>This only handles one connection at a time</p>'.encode("utf-8"))
            self.wfile.write('</body></html>'.encode("utf-8"))

        else:
            print('error', self.path)
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><head></head><body>')
            self.wfile.write(('<h1>{0!s} not found</h1>'.format(self.path)).tobytes())
            self.wfile.write(b'</body></html>')


class PyMain():
    SendHand = True
    LEFT_val = 0
    RIGHT_val = 0
    cam_feed = None
    jpg_bin = None
    y_hold = [lEFT_CONTROL_UI_END[1],RIGHT_CONTROL_UI_END[1]]
    def __init__(self):
        self.cam = cv2.VideoCapture(CAM_SELECTED) # CAP_DSHOW enables direct show without buffering
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)    # Set width of the frame
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)  # Set height of the frame
        self.cam.set(cv2.CAP_PROP_FPS, CAM_FPS)  # Set fps of the camera
        self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG')) # Set the codec as 'MJPG'
        self.MJPEG_Server()
    def run(self):
        print("Running..")
        thread = threading.Thread(target=self.TCPMJPEG)
        thread.start()
        thread = threading.Thread(target=self.TCP_COMMAND)
        thread.start()
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
            self.changing_val = "none leftnone right"
            for hand in lmList:
                if len(hand) != 0:
                    x, y = hand[INDEX_FINGER_TIP][X_COORD], hand[INDEX_FINGER_TIP][Y_COORD]
                    cv2.circle(frame, (x, y), CIR_RADIUS, CIR_COLOR, CIR_THICKNESS)
                    chk = self.checkBound(x,y)
                    val = self.drawRECT(frame,x,y,CIR_COLOR,-1,chk)
                    if chk == 'left':
                        PyMain.LEFT_val = val*100
                        self.changing_val= self.changing_val.replace("none left",'')
                    elif chk == 'right':
                        PyMain.RIGHT_val = val*100
                        self.changing_val= self.changing_val.replace("none right",'')
            if self.changing_val:
                self.drawRECT(frame,0,0,SELECT_COLOR,-1,self.changing_val)   
            if PyMain.SendHand:
                #resize to 360x203
                low_res = cv2.resize(frame,(360,203))
                PyMain.cam_feed = low_res
                self.convIMG(low_res)
                
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
    def getPacketSize(self,packet):
        return len(packet)
    def TCPMJPEG(self):
        print("MJPEG Server started at", sock.getsockname())
        with open('Connected','w') as cntd:
            cntd.write('')
            cntd.close()
        while True:
            self.mjpeg_connection,self.mjpeg_address = sock.accept()  
            print('Video stream connected by', self.mjpeg_address)
            #respond with "Hello"
            clearence = [False,False,False]
            curr_command = 0
            
            while True:
                commands = [
                [b'OMV',b'%d,%d' % (PyMain.LEFT_val,PyMain.RIGHT_val)],
                [b'OMF',PyMain.jpg_bin]
                ]
                if PyMain.jpg_bin is None:
                    continue
                
                try: 
                    data = self.mjpeg_connection.recv(3)
                except:
                    break
                if  data == b'RDY':
                    clearence[0] = True
                    try: 
                        self.mjpeg_connection.sendall(b'%05d' % len(commands[curr_command][1]))
                    except:
                        break
                if data == b'OK0':
                    clearence[1] = True
                    try:
                        self.mjpeg_connection.sendall(commands[curr_command][0])
                    except:
                        break
                if data == b'OK1':
                    clearence[2] = True
                if all(clearence):
                    try: 
                        self.mjpeg_connection.sendall(commands[curr_command][1])
                    except:
                        break
                    clearence = [False,False,False]
                if data == b'END':
                    clearence = [False,False,False]
                    curr_command = 0 if curr_command == len(commands) -1 else curr_command +1
                if data == b'ERO':
                    break
    def TCP_COMMAND(self):
            print("Command Server started at", command_sock.getsockname())
            while True:
                self.command_address,self.command_address = command_sock.accept()  
                print('Labview connected: ', self.command_address)
                clearence = [False,False,False]
                while True:
                    
                    to_send = b'%d,%d' % (PyMain.LEFT_val,PyMain.RIGHT_val)
                    try: 
                        data = self.mjpeg_connection.recv(3)
                    except:
                        break
                    if  data == b'RDY':
                        clearence[0] = True
                        try: 
                            self.mjpeg_connection.sendall(b'%05d' % len(to_send))
                        except:
                            break
                    if data == b'OK0':
                        clearence[1] = True
                        try:
                            self.mjpeg_connection.sendall(b'OMV')
                        except:
                            break
                    if data == b'OK1':
                        clearence[2] = True
                    if all(clearence):
                        try: 
                            self.mjpeg_connection.sendall(to_send)
                        except:
                            break
                        clearence = [False,False,False]
                    if data == b'END':
                        clearence = [False,False,False]
                    if data == b'ERO':
                        break
                
        
        

    def drawRECT(self,frame, x, y, color,size,chk):
        if chk == "left":
            left_val = round(1 - (y - lEFT_CONTROL_UI_START[1]) / (lEFT_CONTROL_UI_END[1] - lEFT_CONTROL_UI_START[1]),2)
            #draw rect from start to left_val 
            cv2.rectangle(frame, lEFT_CONTROL_UI_END, (lEFT_CONTROL_UI_START[0], y), color, size)
            cv2.putText(frame, str(left_val), LEFT_CONTROL_CAP, cv2.FONT_HERSHEY_PLAIN, 3, CIR_COLOR, 3)
            PyMain.y_hold[0] = y
            return left_val
        elif chk == "right":
            right_val = round(1- (y - RIGHT_CONTROL_UI_START[1]) / (RIGHT_CONTROL_UI_END[1] - RIGHT_CONTROL_UI_START[1]),2)
            cv2.rectangle(frame, RIGHT_CONTROL_UI_END, (RIGHT_CONTROL_UI_START[0], y),color, size)
            cv2.putText(frame, str(right_val), RIGHT_CONTROL_CAP, cv2.FONT_HERSHEY_PLAIN, 3, CIR_COLOR, 3)
            PyMain.y_hold[1] = y
            return right_val
        if "none left" in chk:
            cv2.rectangle(frame, lEFT_CONTROL_UI_END, (lEFT_CONTROL_UI_START[0], PyMain.y_hold[0]), color, size)
        if "none right" in chk:
            cv2.rectangle(frame, RIGHT_CONTROL_UI_END, (RIGHT_CONTROL_UI_START[0], PyMain.y_hold[1]),color, size)
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
    def convIMG(self,frame,dim = (360,203)):
        ret, PyMain.jpg_bin = cv2.imencode('.jpg', frame)
        
                
        
    def MJPEG_Server(self):
        server = HTTPServer((IP, 34534), mjpgServer)
        print("server started on {}:{}".format(IP, MJPEG_PORT))
        self.srvThread = threading.Thread(target=server.serve_forever,daemon=True )
        self.srvThread.start()
            
        
if __name__ == "__main__":
    a = PyMain()
    a.run()
        
        

        
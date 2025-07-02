#volume hand control
import cv2 as cv
import numpy as np
from pycaw.api.endpointvolume import IAudioEndpointVolume
import HandTrackingModule as htm
import math
from pycaw.pycaw import AudioUtilities
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER


cap = cv.VideoCapture(0)
detector = htm.handDetector(detectionCon=0.8)#to be more sure about it being a hand
#pycaw code
device = AudioUtilities.GetSpeakers()
interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#GetVolumeRange returns tuple (min, max, increment) in dB
volRange = volume.GetVolumeRange()
minVol, maxVol = volRange[0], volRange[1]
#print(volRange)
#to set volume
#volume.SetMasterVolumeLevel(-40.0, None)

while True:
    start = cv.getTickCount()
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv.flip(frame, 1)
    img = detector.findHands(frame)
    #list that contains id value and their corresponding x,y coodinates
    lmList = detector.findPosition(img, draw=False)
    #if list is empty and then we print, it will return error
    if len(lmList) != 0:
        #print(lmList[4],lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        #center of the above two point
        cx,cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv.circle(frame,(x1,y1), 10, (255,0,255),-1)
        cv.circle(frame, (x2, y2 ), 10, (255, 0, 255), -1)
        cv.circle(frame, (cx,cy), 7, (255, 0, 255), -1)

        # to find the length between the points
        length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        #print(lenght)
        cv.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
        if length < 25:
            #this will create a button like effect
            cv.circle(frame, (cx, cy), 7, (0, 255, 0), -1)

        #we saw our length range was varrying between 25-250
        #volume range is from -65-0 dB
        #to convert the ranges we use NumPy interp fucntion
        vol = np.interp(length,[25,150],[minVol, maxVol])
        volVB = np.interp(length,[25,150],[400,150])
        volPercentage = np.interp(length,[25,150],[0,100])
        print(vol)

        volume.SetMasterVolumeLevel(vol, None)

        cv.putText(frame, f'{int(volPercentage)}%', (40,430), cv.FONT_HERSHEY_SIMPLEX, 1, (255,0,0),2)
        #creating a volume bar
        cv.rectangle(frame,(50, int(volVB)),(75, 400), (0,0,255),-1)

    cv.rectangle(frame, (50, 150), (75, 400), (255, 0, 0), 2)
    end = cv.getTickCount()
    fps = cv.getTickFrequency() /(end - start)
    cv.putText(frame,"FPS: "+str(int(fps)), (20,30),cv.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
    cv.namedWindow("Tracking", cv.WINDOW_NORMAL)
    cv.imshow("Tracking", frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()

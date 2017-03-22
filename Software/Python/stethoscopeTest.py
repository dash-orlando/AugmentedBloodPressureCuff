
# Import
import sys
import os
import serial
from   os.path               import expanduser
from   configurationProtocol import *
from   bluetoothProtocol     import *
from   stethoscopeProtocol   import *

# =========
# OPERATION
# =========

deviceName = "SS"
deviceBTAddress = "00:06:66:86:60:3D"
rfObject = createPort(deviceName, deviceBTAddress, 115200, 5, 5)

time.sleep(1)
if rfObject.isOpen() == False:
    rfObject.open()
sdCardCheck(rfObject)
rfObject.close()


time.sleep(2)
if rfObject.isOpen() == False:
    rfObject.open()
startRecording(rfObject)
#startTrackingMicStream(rfObject)
rfObject.close()


time.sleep(30)

time.sleep(2)
if rfObject.isOpen() == False:
    rfObject.open()
stopRecording(rfObject)
#stopTrackingMicStream(rfObject)
rfObject.close()

"""
time.sleep(1)
if rfObject.isOpen() == False:
    rfObject.open()
sdCardCheck(rfObject)
rfObject.close()
"""

portRelease('rfcomm', 0)

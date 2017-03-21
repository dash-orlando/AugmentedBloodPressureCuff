
# Import
import sys
import os
from os.path import expanduser
import serial
from configurationProtocol import *
from bluetoothProtocol import *
from pressureCuffProtocol import *
import pressureCuffDefinitions as definitions

# Variables
# ----------------------------------------------
# B) Path/Directory Variables
# ----------------------------------------------
homeDir = expanduser("~")
rootDir = "/root"
if homeDir == rootDir:
          homeDir = "/home/pi"
          # This check and correction is needed for raspbian
# .../Python
consysPyDir = homeDir + "/csec/repos/ControlSystem/Software/Python"
# .../Python/data
consysPyDataDir = consysPyDir + "/data"
# .../Python/data/scenarios
scenarioConfigFilePath = consysPyDataDir + "/scenarios"

# Scenario File Name
scenarioFileName = "sc001.xml"

configFile = scenarioConfigFilePath + "/" + scenarioFileName
tree, root = readConfigFile(configFile)

# =========
# OPERATION
# =========

#deviceName, deviceBTAddress = pullInstruments(tree, root)   # pull instrument information from configuration file
deviceName = "hola"
deviceBTAddress = "B8:27:EB:7A:40:71"
#rfObject = createPortS(deviceName, 1, deviceBTAddress, 115200, 20)          # create rfObjects/ports

#statusEnquiry(rfObject, 5, 5)
#startSIMold(rfObject, 5, 5)
#deviceID(rfObject)

clientSocket(deviceBTAddress, definitions.SIM_000)


#portRelease('rfcomm', 0)                                    # Release port to avoid permanent connection

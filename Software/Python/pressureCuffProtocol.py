"""
#
# pressureCuffProtocol.py
#
# Access and command the (ABPC) project using the ControlSystem
# 
# Author: Mohammad Odeh
# Date: Mar. 20th, 2017
#
# Based on the original protocol written by Lobo, F. & Xynidis, M.
#
"""

# Import Libraries and/or Modules
import os
import sys
import serial
import time
from timeStamp import *
from configurationProtocol import *
from bluetoothProtocol import *
import pressureCuffDefinitions as definitions

# State Enquiry
#       This function requests the status of the thermometer
#       Input   ::      rfObject                {object}        serial object
#       Output  ::      terminal messages       {string}        terminal messages for logging
def statusEnquiry(rfObject):
        print fullStamp() + " statusEnquiry()"                                          # Print function name
        outByte = definitions.ENQ                                                       # Send ENQ / Status Enquiry command - see thermometerDefinitions.py
        rfObject.write(outByte)
        inByte = rfObject.read(size=1)
        if inByte == definitions.ACK:                                                   # Check for ACK / NAK response
                print fullStamp() + " ACK Device READY\n"                               # ACK, in this case, translates to DEVICE READY
        elif inByte == definitions.NAK:                                                 # Check for ACK / NAK response
                print fullStamp() + " NAK Device NOT READY\n"                           # NAK, in this case, translates to DEVICE NOT READY

'''
                                =============> FUNCTION IS OBSOLETE FOR NOW. WILL REPURPOSE LATER. <=============
# System Check
#       This function commands the connected thermometer to perform a "systems check", which may consist on a routine verification of remote features
#       Input   ::      rfObject                {object}        serial object
#       Output  ::      terminal messages       {string}        terminal messages for logging
def systemCheck(rfObject):
        print fullStamp() + " systemCheck()"                                            # Print function name
        outByte = definitions.CHK                                                       # Send CHK / System Check command - see thermometerDefinitions.py
        rfObject.write(outByte)
        inByte = rfObject.read(size=1)
        if inByte == definitions.ACK:                                                   # Check for ACK / NAK response
                print fullStamp() + " ACK Device READY\n"                               # ACK, in this case, translates to DEVICE READY
        elif inByte == definitions.NAK:                                                 # Check for ACK / NAK response
                print fullStamp() + " NAK Device NOT READY\n"                           # NAK, in this case, translates to DEVICE NOT READY
'''

def debugModeON(rfObject):
        print fullStamp() + " debugModeON()"                                            # Print function name
        outByte = definitions.DC1                                                       # Send DC1 / Device Control 1 command - see thermometerDefinitions.py
        rfObject.write(outByte)
        inByte = rfObject.read(size=1)
        if inByte == definitions.ACK:                                                   # Check for ACK / NAK response
                print fullStamp() + " ACK Device READY"                                 # ACK, in this case, translates to DEVICE READY
                outByte = definitions.DC1_DEBUGON                                       # Send DEBUGON / debugMode ON - see thermometerDefinitions.py
                rfObject.write(outByte)
                inByte = rfObject.read(size=1)
                if inByte == definitions.ACK:
                        print fullStamp() + " DEBUG MODE ON\n"
                elif inByte != definitions.ACK:
                        print fullStamp() + " Device NOT responding\n"
        
        elif inByte == definitions.NAK:                                                 # Check for ACK / NAK response
                print fullStamp() + " NAK Device NOT READY\n"                           # NAK, in this case, translates to DEVICE NOT READY


def debugModeOFF(rfObject):
        print fullStamp() + " debugModeOFF()"                                            # Print function name
        outByte = definitions.DC1                                                       # Send CHK / System Check command - see thermometerDefinitions.py
        rfObject.write(outByte)
        inByte = rfObject.read(size=1)
        if inByte == definitions.ACK:                                                   # Check for ACK / NAK response
                print fullStamp() + " ACK Device READY"                                 # ACK, in this case, translates to DEVICE READY
                outByte = definitions.DC1_DEBUGOFF                                           # Send SIM_000 / Simulate Scenario 1 - see thermometerDefinitions.py
                rfObject.write(outByte)
                inByte = rfObject.read(size=1)
                if inByte == definitions.ACK:
                        print fullStamp() + " DEBUG MODE OFF\n"
                elif inByte != definitions.ACK:
                        print fullStamp() + " Device NOT responding\n"
        
        elif inByte == definitions.NAK:                                                 # Check for ACK / NAK response
                print fullStamp() + " NAK Device NOT READY\n"                             # NAK, in this case, translates to DEVICE NOT READY

# Start Simulation
#       This function starts simulation
#       Input   ::      rfObject                {object}        serial object
#       Output  ::      terminal messages       {string}        terminal messages for logging
def startSIM_000(rfObject):
        print fullStamp() + " Command Sent..."
        outByte = definitions.SIM                                                       # Send SIM / Start Simulation - see thermometerDefinitions.py
        rfObject.write(outByte)
        inByte = rfObject.read(size=1)
        if inByte == definitions.ACK:   
                print fullStamp() + " Acknowledged! Starting Simulation"
                outByte = definitions.SIM_000                                           # Send SIM_000 / Simulate Scenario 1 - see thermometerDefinitions.py
                rfObject.write(outByte)
                inByte = rfObject.read(size=1)
                if inByte == definitions.ACK:
                        print fullStamp() + " Simulation 1 Running\n"
                elif inByte != definitions.ACK:
                        print fullStamp() + " Device NOT responding\n"

        elif inByte == definitions.NAK: 
                print fullStamp() + " NAK Device NOT READY\n"

        else: 
                print fullStamp() + " Device NOT Responding\n"



def startSIM_001(rfObject):
        print fullStamp() + " Command Sent..."
        outByte = definitions.SIM                                                       # Send SIM / Start Simulation - see thermometerDefinitions.py
        rfObject.write(outByte)
        inByte = rfObject.read(size=1)
        if inByte == definitions.ACK:                                                   # Check for ACK / NAK response
                print fullStamp() + " Acknowledged! Starting Simulation"
                outByte = definitions.SIM_001                                           # Send SIM_001 / Simulate Scenario 2 - see thermometerDefinitions.py
                rfObject.write(outByte)
                inByte = rfObject.read(size=1)
                if inByte == definitions.ACK:
                        print fullStamp() + " Simulation 2 Running\n"
                elif inByte != definitions.ACK:
                        print fullStamp() + " Device NOT responding\n"

        elif inByte == definitions.NAK:                                                 # Check for ACK / NAK response
                print fullStamp() + " NAK Device NOT READY\n"
        else: 
                print fullStamp() + " Device NOT Responding\n"

def normalOP(rfObject):
        print fullStamp() + " Command Sent..."
        outByte = definitions.NRMOP                                                     # Send NRMOP / Normal Operation - see thermometerDefinitions.py
        rfObject.write(outByte)
        inByte = rfObject.read(size=1)
        if inByte == definitions.ACK:
                print fullStamp() + " Acknowledged! Normal Operation ON\n"
        elif inByte == definitions.NAK:
                print fullStamp() + " NAK Device NOT READY\n"
        else: 
                print fullStamp() + " Device NOT Responding\n"

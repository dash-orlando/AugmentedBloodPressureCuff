"""
stethoscopeProtocol.py

The following module has been created to manage the device-specific interface between the stethoscope and the control system modules

Michael Xynidis
Fluvio L Lobo Fenoglietto
09/01/2016

"""

# Import Libraries and/or Modules
import os
import sys
import serial
from timeStamp import *
from configurationProtocol import *
from bluetoothProtocol_teensy32 import *
import stethoscopeDefinitions as definitions

# System Check
#       This function commands the connected stethoscope to perform a "systems check", which may consist on a routine verification of remote features
#       Input   ::      rfObject                {object}        serial object
#                       timeout                 {int}           maximum wait time for serial communication
#                       iterCheck               {int}           maximum number of iterations for serial communication
#       Output  ::      terminal messages       {string}        terminal messages for logging
def systemCheck(rfObject, timeout, iterCheck):
        print fullStamp() + " systemCheck()"                                                                    # Print function name
        outByte = definitions.CHK                                                                               # Send CHK / System Check command - see protocolDefinitions.py
        inByte = sendUntilRead(rfObject, outByte, timeout, iterCheck)                                           # Execute sendUntilRead() from bluetoothProtocol.py
        if inByte == definitions.ACK:                                                                           # Check for ACK / NAK response found through sendUntilRead()
                print fullStamp() + " ACK SD Card Check Passed"                                                 # If the SD card check is successful, the remote device sends a ACK
                print fullStamp() + " ACK Device Ready"                                                         # ACK, in this case, translates to DEVICE READY
        elif inByte == definitions.NAK:                                                                         # Check for ACK / NAK response found through sendUntilRead()
                print fullStamp() + " NAK SD Card Check Failed"                                                 # If the SD card check fails, the remote device sends a NAK
                print fullStamp() + " NAK Device NOT Ready"                                                     # NAK, in this case, translates to DEVICE NOT READY


# Diagnostic Functions
#       These functions deal with the status of the hardware

# Device Identification
#       This function requests the identification of the connected device
#       Input   ::      {object}                rfObject                serial object
#       Output  ::      {string}                terminal message        terminal message
def deviceID(rfObject):
        outBytes = [definitions.DC1, definitions.DC1_DEVICEID]                                                  # Store the sequence of bytes associated with the operation, function, feature
        inBytes = []
        for i in range(0,len(outBytes)):                                                                        # For loop for the sequential delivery of bytes using the length of the sequence for the range
                rfObject.write(outBytes[i])
                if i == (len(outBytes) - 1):                                                                    # On the last byte, the program reads the response
                        for i in range(0,3):
                                inBytes.append(rfObject.read(size=1))
        print inBytes

# SD Card Check
#       This function commands the connected stethoscope to perform a check on the connected sd card
#       Input   ::      rfObject                {object}        serial object
#       Output  ::      terminal messages       {string}        terminal messages for logging
def sdCardCheck(rfObject,attempts):
        print fullStamp() + " sdCardCheck()"
        if rfObject.isOpen() == False:
                rfObject.open()
        outBytes = [definitions.DC1, definitions.DC1_SDCHECK]
        for i in range(0,len(outBytes)):
                rfObject.write(outBytes[i])
                if i == (len(outBytes) - 1):
                        inByte = rfObject.read(size=1)
        if inByte == definitions.ACK:
                print fullStamp() + " ACK SD Card Check Passed"
                print fullStamp() + " ACK Device Ready"
        elif inByte == definitions.NAK:
                print fullStamp() + " NAK SD Card Check Failed"
                print fullStamp() + " NAK Device NOT Ready"
        else:
                rfObject.close()
                if attempts is not 0:
                        return sdCardCheck(rfObject,attempts-1)
                elif attempts is 0:
                        print fullStamp() + " Attempts limit reached"
                        print fullStamp() + " Please troubleshoot device"
        rfObject.close()

# State Enquiry
#       This function requests the status of then stethoscope
#       Input   ::      rfObject                {object}        serial object
#       Output  ::      terminal messages       {string}        terminal messages for logging
def statusEnquiry(rfObject,attempts):
        print fullStamp() + " statusEnquiry()"                                                                 # Print function name
        if rfObject.isOpen() == False:
                rfObject.open()
        outByte = definitions.ENQ                                                                               # Send ENQ / Status Enquiry command - see protocolDefinitions.py
        rfObject.write(outByte)
        inByte = rfObject.read(size=1)                                                                          # Execute sendUntilRead() from bluetoothProtocol.py
        if inByte == definitions.ACK:                                                                           # Check for ACK / NAK response found through sendUntilRead()
                print fullStamp() + " ACK Device READY"                                                         # ACK, in this case, translates to DEVICE READY
        elif inByte == definitions.NAK:
                print fullStamp() + " NAK Device NOT READY"
        else:
                rfObject.close()
                if attempts is not 0:
                        return statusEnquiry(rfObject,attempts-1)
                elif attempts is 0:
                        print fullStamp() + " Attempts limit reached"
                        print fullStamp() + " Please troubleshoot device"
        rfObject.close()

# Operational Functions
#       These functions deal with the normal operation of the device


# Device-Specific Functions
#       These functions deal with the device-specific operation or features

# Start Recording
#       This function commands the connected stethoscope to begin recording audio
#       The recorded audio is then stored in the local SD
#       Input   ::      rfObject                {object}        serial object
#       Output  ::      terminal messages       {string}        terminal messages for logging
def startRecording(rfObject,attempts):
        print fullStamp() + " startRecording()"
        if rfObject.isOpen() == False:
                rfObject.open()
        outByte = definitions.STARTREC
        rfObject.write(outByte)
        inByte = rfObject.read(size=1)
        if inByte == definitions.ACK:
                print fullStamp() + " ACK Stethoscope will START RECORDING"
        elif inByte == definitions.NAK:
                print fullStamp() + " NAK Stethoscope CANNOT START RECORDING"
        else:
                rfObject.close()
                if attempts is not 0:
                        return startRecording(rfObject,attempts-1)
                elif attempts is 0:
                        print fullStamp() + " Attempts limit reached"
                        print fullStamp() + " Please troubleshoot device"
        rfObject.close()

# Stop Recording
#       This function commands the connected stethoscope to stop recording audio
#       Input   ::      rfObject                {object}        serial object
#       Output  ::      terminal messages       {string}        terminal messages for logging
def stopRecording(rfObject,attempts):
        print fullStamp() + " stopRecording()"
        if rfObject.isOpen() == False:
                rfObject.open()
        outByte = definitions.STOPREC
        rfObject.write(outByte)
        inByte = rfObject.read(size=1)                                                                          
        if inByte == definitions.ACK:
                print fullStamp() + " ACK Stethoscope will STOP RECORDING"
        elif inByte == definitions.NAK:
                print fullStamp() + " NAK Stethoscope CANNOT STOP RECORDING"
        else:
                rfObject.close()
                if attempts is not 0:
                        return stopRecording(rfObject,attempts-1)
                elif attempts is 0:
                        print fullStamp() + " Attempts limit reached"
                        print fullStamp() + " Please troubleshoot device"
        rfObject.close()

# Start Heart Rate Monitoring
#       This function commands the connected stethoscope to begin streaming audio from the microphone and find/detect peaks
#       Input   ::      rfObject                {object}        serial object
#       Output  ::      terminal messages       {string}        terminal messages for logging
def startHBMonitoring(rfObject,attempts):
        print fullStamp() + " startHBMonitoring()"                                                                 # Print function name
        if rfObject.isOpen() == False:
                rfObject.open()
        outByte = definitions.STARTHBMONITOR                                                                              # Send ENQ / Status Enquiry command - see protocolDefinitions.py
        rfObject.write(outByte)
        inByte = rfObject.read(size=1)                                                                          # Execute sendUntilRead() from bluetoothProtocol.py
        if inByte == definitions.ACK:                                                                           # Check for ACK / NAK response found through sendUntilRead()
                print fullStamp() + " ACK Device will START Monitoring"                                                         # ACK, in this case, translates to DEVICE READY
        elif inByte == definitions.NAK:
                print fullStamp() + " NAK Device CANNOT START Monitoring"
        else:
                rfObject.close()
                if attempts is not 0:
                        return startTrackingMicStream(rfObject,attempts-1)
                elif attempts is 0:
                        print fullStamp() + " Attempts limit reached"
                        print fullStamp() + " Please troubleshoot device"
        rfObject.close()


# Start Heart Rate Monitoring
#       This function commands the connected stethoscope to stop streaming audio from the microphone and find/detect peaks
#       Input   ::      rfObject                {object}        serial object
#       Output  ::      terminal messages       {string}        terminal messages for logging
def stopHBMonitoring(rfObject,attempts):
        print fullStamp() + " stopHBMonitoring()"                                                                 # Print function name
        if rfObject.isOpen() == False:
                rfObject.open()
        outByte = definitions.STOPHBMONITOR                                                                            # Send ENQ / Status Enquiry command - see protocolDefinitions.py
        rfObject.write(outByte)
        inByte = rfObject.read(size=1)                                                                          # Execute sendUntilRead() from bluetoothProtocol.py
        if inByte == definitions.ACK:                                                                           # Check for ACK / NAK response found through sendUntilRead()
                print fullStamp() + " ACK Device will STOP Monitoring"                                                         # ACK, in this case, translates to DEVICE READY
        elif inByte == definitions.NAK:
                print fullStamp() + " NAK Device CANNOT STOP Monitoring"
        else:
                rfObject.close()
                if attempts is not 0:
                        return startTrackingMicStream(rfObject,attempts-1)
                elif attempts is 0:
                        print fullStamp() + " Attempts limit reached"
                        print fullStamp() + " Please troubleshoot device"
        rfObject.close()

# Simulation Functions
#       These functions deal with the simulations corresponding to the connected device

# Normal Hear Beat Playback
#       This function triggers the playback of a normal heart beat
def normalHBPlayback(rfObject, attempts):
        print fullStamp() + " normalHBPlayback()"                                                                 # Print function name
        if rfObject.isOpen() == False:
                rfObject.open()
        outByte = definitions.NORMALHB                                                                              # Send ENQ / Status Enquiry command - see protocolDefinitions.py
        rfObject.write(outByte)
        inByte = rfObject.read(size=1)                                                                          # Execute sendUntilRead() from bluetoothProtocol.py
        if inByte == definitions.ACK:                                                                           # Check for ACK / NAK response found through sendUntilRead()
                print fullStamp() + " ACK Stethoscope will START PLAYBACK of NORMAL HEARTBEAT"                                                        # ACK, in this case, translates to DEVICE READY
        elif inByte == definitions.NAK:
                print fullStamp() + " NAK Stethoscope CANNOT START PLAYBACK of NORMAL HEARTBEAT"
        else:
                rfObject.close()
                if attempts is not 0:
                        return normalHBPlayback(rfObject,attempts-1)
                elif attempts is 0:
                        print fullStamp() + " Attempts limit reached"
                        print fullStamp() + " Please troubleshoot device"
        rfObject.close()

# Early Systolic Heart Murmur
#       This function triggers the playback of an early systolic heart mumur
def earlyHMPlayback(rfObject, attempts):
        print fullStamp() + " earlyHMPlayback()"                                                                # Print function name
        if rfObject.isOpen() == False:
                rfObject.open()
        outByte = definitions.ESHMURMUR                                                                              # Send ENQ / Status Enquiry command - see protocolDefinitions.py
        rfObject.write(outByte)
        inByte = rfObject.read(size=1)                                                                          # Execute sendUntilRead() from bluetoothProtocol.py
        if inByte == definitions.ACK:                                                                           # Check for ACK / NAK response found through sendUntilRead()
                print fullStamp() + " ACK Stethoscope will START PLAYBACK of EARLY SYSTOLIC HEART MUMUR"                                                        # ACK, in this case, translates to DEVICE READY
        elif inByte == definitions.NAK:
                print fullStamp() + " NAK Stethoscope CANNOT START PLAYBACK of EARLY SYSTOLIC HEART MUMUR" 
        else:
                rfObject.close()
                if attempts is not 0:
                        return earlyHMPlayback(rfObject,attempts-1)
                elif attempts is 0:
                        print fullStamp() + " Attempts limit reached"
                        print fullStamp() + " Please troubleshoot device"
        rfObject.close()

# Stop Playback
#       This function commands the connected stethoscope to stop playing an audio filed stored within the SD card
#       Input   ::      rfObject                {object}        serial object
#                       timeout                 {int}           maximum wait time for serial communication
#                       iterCheck               {int}           maximum number of iterations for serial communication
#       Output  ::      terminal messages       {string}        terminal messages for logging
def stopPlayback(rfObject, attempts):
        print fullStamp() + " stopPlayback()"                                                                 # Print function name
        if rfObject.isOpen() == False:
                rfObject.open()
        outByte = definitions.STOPPLAY                                                                              # Send ENQ / Status Enquiry command - see protocolDefinitions.py
        rfObject.write(outByte)
        inByte = rfObject.read(size=1)                                                                          # Execute sendUntilRead() from bluetoothProtocol.py
        if inByte == definitions.ACK:                                                                           # Check for ACK / NAK response found through sendUntilRead()
                print fullStamp() + " ACK Stethoscope will STOP PLAYBACK"                                                         # ACK, in this case, translates to DEVICE READY
        elif inByte == definitions.NAK:
                print fullStamp() + " NAK Stethoscope CANNOT STOP PLAYBACK"
        else:
                rfObject.close()
                if attempts is not 0:
                        return stopPlayback(rfObject,attempts-1)
                elif attempts is 0:
                        print fullStamp() + " Attempts limit reached"
                        print fullStamp() + " Please troubleshoot device"
        rfObject.close()

# Early Systolic Heart Murmur
#       This function triggers the playback of an early systolic heart mumur
def earlyHMBlending(rfObject, attempts):
        print fullStamp() + " earlyHMBlending()"                                                                # Print function name
        if rfObject.isOpen() == False:
                rfObject.open()
        outByte = definitions.STARTBLEND                                                                              # Send ENQ / Status Enquiry command - see protocolDefinitions.py
        rfObject.write(outByte)
        inByte = rfObject.read(size=1)                                                                          # Execute sendUntilRead() from bluetoothProtocol.py
        if inByte == definitions.ACK:                                                                           # Check for ACK / NAK response found through sendUntilRead()
                print fullStamp() + " ACK Stethoscope will START BLENDING of EARLY SYSTOLIC HEART MUMUR"                                                        # ACK, in this case, translates to DEVICE READY
        elif inByte == definitions.NAK:
                print fullStamp() + " NAK Stethoscope CANNOT START BLENDING of EARLY SYSTOLIC HEART MUMUR" 
        else:
                rfObject.close()
                if attempts is not 0:
                        return earlyHMBlending(rfObject,attempts-1)
                elif attempts is 0:
                        print fullStamp() + " Attempts limit reached"
                        print fullStamp() + " Please troubleshoot device"
        rfObject.close()

def startBlending(rfObject,fileByte,attempts):
        print fullStamp() + " startBlending()"                                                                # Print function name
        if rfObject.isOpen() == False:
                rfObject.open()
        outByte = fileByte                                                                             # Send ENQ / Status Enquiry command - see protocolDefinitions.py
        rfObject.write(outByte)
        inByte = rfObject.read(size=1)                                                                          # Execute sendUntilRead() from bluetoothProtocol.py
        if inByte == definitions.ACK:                                                                           # Check for ACK / NAK response found through sendUntilRead()
                print fullStamp() + " ACK Stethoscope will START BLENDING of EARLY SYSTOLIC HEART MUMUR"                                                        # ACK, in this case, translates to DEVICE READY
        elif inByte == definitions.NAK:
                print fullStamp() + " NAK Stethoscope CANNOT START BLENDING of EARLY SYSTOLIC HEART MUMUR" 
        else:
                rfObject.close()
                if attempts is not 0:
                        return earlyHMBlending(rfObject,attempts-1)
                elif attempts is 0:
                        print fullStamp() + " Attempts limit reached"
                        print fullStamp() + " Please troubleshoot device"
        rfObject.close()

# Stop Playback
#       This function commands the connected stethoscope to stop playing an audio filed stored within the SD card
#       Input   ::      rfObject                {object}        serial object
#                       timeout                 {int}           maximum wait time for serial communication
#                       iterCheck               {int}           maximum number of iterations for serial communication
#       Output  ::      terminal messages       {string}        terminal messages for logging
def stopBlending(rfObject, attempts):
        print fullStamp() + " stopBlending()"                                                                 # Print function name
        if rfObject.isOpen() == False:
                rfObject.open()
        outByte = definitions.STOPBLEND                                                                              # Send ENQ / Status Enquiry command - see protocolDefinitions.py
        rfObject.write(outByte)
        inByte = rfObject.read(size=1)                                                                          # Execute sendUntilRead() from bluetoothProtocol.py
        if inByte == definitions.ACK:                                                                           # Check for ACK / NAK response found through sendUntilRead()
                print fullStamp() + " ACK Stethoscope will STOP BLENDING"                                                         # ACK, in this case, translates to DEVICE READY
        elif inByte == definitions.NAK:
                print fullStamp() + " NAK Stethoscope CANNOT STOP BLENDING"
        else:
                rfObject.close()
                if attempts is not 0:
                        return stopBlending(rfObject,attempts-1)
                elif attempts is 0:
                        print fullStamp() + " Attempts limit reached"
                        print fullStamp() + " Please troubleshoot device"
        rfObject.close()

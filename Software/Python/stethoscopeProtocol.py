"""
stethoscopeProtocol.py

The following module has been created to manage the device-specific interface between the stethoscope and the control system modules

Michael Xynidis
Fluvio L Lobo Fenoglietto
09/01/2016

Modified by : Mohammad Odeh
Date        : May 31st, 2017
Changes     : Modified protocol to use PyBluez instead of PySerial
"""

# Import Libraries and/or Modules
from    configurationProtocol       import  *
from    bluetoothProtocol_teensy32  import  *
from    timeStamp                   import  fullStamp
import  stethoscopeDefinitions      as      definitions
import  os, sys, serial

# System Check
#       This function commands the connected stethoscope to perform a "systems check", which may consist on a routine verification of remote features
#       Input   ::      rfObject                {object}        serial object
#                       timeout                 {int}           maximum wait time for serial communication
#                       iterCheck               {int}           maximum number of iterations for serial communication
#       Output  ::      terminal messages       {string}        terminal messages for logging
def systemCheck( rfObject ):
    print fullStamp() + " systemCheck()"                                                                # Print function name

    outByte = definitions.CHK                                                                           # Send CHK / System Check command - see protocolDefinitions.py                     
    rfObject.send(outByte)
    inByte = rfObject.recv(1)                                                                           # Check for response

    if inByte == definitions.ACK:                                                                       # Check for ACK / NAK response found through sendUntilRead()
        print fullStamp() + " ACK SD Card Check Passed"                                                 # If the SD card check is successful, the remote device sends a ACK
        print fullStamp() + " ACK Device Ready"                                                         # ACK, in this case, translates to DEVICE READY

    elif inByte == definitions.NAK:                                                                     # Check for ACK / NAK response found through sendUntilRead()
        print fullStamp() + " NAK SD Card Check Failed"                                                 # If the SD card check fails, the remote device sends a NAK
        print fullStamp() + " NAK Device NOT Ready"                                                     # NAK, in this case, translates to DEVICE NOT READY


# Diagnostic Functions
#       These functions deal with the status of the hardware

# Device Identification
#       This function requests the identification of the connected device
#       Input   ::      {object}                rfObject                serial object
#       Output  ::      {string}                terminal message        terminal message
def deviceID( rfObject ):
    outBytes = [definitions.DC1, definitions.DC1_DEVICEID]                                              # Store the sequence of bytes associated with the operation, function, feature
    inBytes = []
    for i in range(0,len(outBytes)):                                                                    # For loop for the sequential delivery of bytes using the length of the sequence for the range
        rfObject.send(outBytes[i])
        if i == (len(outBytes) - 1):                                                                    # On the last byte, the program reads the response
            for i in range(0,3):
                inBytes.append(rfObject.recv(1))

    print inBytes

# SD Card Check
#       This function commands the connected stethoscope to perform a check on the connected sd card
#       Input   ::      rfObject                {object}        serial object
#       Output  ::      terminal messages       {string}        terminal messages for logging
def sdCardCheck( rfObject ):
    print fullStamp() + " sdCardCheck()"

    outBytes = [definitions.DC1, definitions.DC1_SDCHECK]

    for i in range( 0, len(outBytes) ):
        rfObject.send( outBytes[i] )
        if i == (len(outBytes) - 1):
            inByte = rfObject.recv(1)

    if inByte == definitions.ACK:
        print fullStamp() + " ACK SD Card Check Passed"
        print fullStamp() + " ACK Device Ready"

    elif inByte == definitions.NAK:
        print fullStamp() + " NAK SD Card Check Failed"
        print fullStamp() + " NAK Device NOT Ready"

    else:
        print fullStamp() + " Please troubleshoot device"

# State Enquiry
#       This function requests the status of then stethoscope
#       Input   ::      rfObject                {object}        serial object
#       Output  ::      terminal messages       {string}        terminal messages for logging
def statusEnquiry( rfObject ):
    print fullStamp() + " statusEnquiry()"       

    outByte = definitions.ENQ                    
    rfObject.send(outByte)
    inByte = rfObject.recv(1)                      

    if inByte == definitions.ACK:                     
        print fullStamp() + " ACK Device READY"    
        return True
    
    elif inByte == definitions.NAK:
        print fullStamp() + " NAK Device NOT READY"

    else:
        print fullStamp() + " Please troubleshoot device"


# Operational Functions
#       These functions deal with the normal operation of the device


# Device-Specific Functions
#       These functions deal with the device-specific operation or features

# Start Recording
#       This function commands the connected stethoscope to begin recording audio
#       The recorded audio is then stored in the local SD
#       Input   ::      rfObject                {object}        serial object
#       Output  ::      terminal messages       {string}        terminal messages for logging
def startRecording( rfObject ):
    print fullStamp() + " startRecording()"                        

    outByte = definitions.STARTREC                  
    rfObject.send(outByte)
    inByte = rfObject.recv(1)
    
    if inByte == definitions.ACK:                   
        print fullStamp() + " ACK Stethoscope will START RECORDING"        

    elif inByte == definitions.NAK:
        print fullStamp() + " NAK Stethoscope CANNOT START RECORDING"

    else:
        print fullStamp() + " Please troubleshoot device"


# Stop Recording
#       This function commands the connected stethoscope to stop recording audio
#       Input   ::      rfObject                {object}        serial object
#       Output  ::      terminal messages       {string}        terminal messages for logging
def stopRecording( rfObject ):
    print fullStamp() + " stopRecording()"                  

    outByte = definitions.STOPREC                     
    rfObject.send(outByte)
    inByte = rfObject.recv(1)                          

    if inByte == definitions.ACK:                               
        print fullStamp() + " ACK Stethoscope will STOP RECORDING"       

    elif inByte == definitions.NAK:
        print fullStamp() + " NAK Stethoscope CANNOT STOP RECORDING"

    else:
        print fullStamp() + " Please troubleshoot device"

# Start Microphone Streaming
#       This function commands the connected stethoscope to begin streaming audio from the microphone to the connected speakers
#       Input   ::      rfObject                {object}        serial object
#                       timeout                 {int}           maximum wait time for serial communication
#                       iterCheck               {int}           maximum number of iterations for serial communication
#       Output  ::      terminal messages       {string}        terminal messages for logging
def startMicStream( rfObject ):
    print fullStamp() + " startMicStream()"                                 # ...

    outBytes = [definitions.DC3, definitions.DC3_STARTSTREAM]               # ...

    for i in range(0,len(outBytes)):                                        # ...
        rfObject.send(outBytes[i])                                          # ...
        if i == (len(outBytes) - 1):                                        # ...
            inByte = rfObject.recv(1)                                       # ...

    if inByte == definitions.ACK:                                           # ...
        print fullStamp() + " ACK Stethoscope will START STREAMING"         # If ACK, the stethoscope will START STREAMING

    elif inByte == definitions.NAK:                                         # ...
        print fullStamp() + " NAK Stethoscope CANNOT START STREAMING"       # NAK, in this case, translates to CANNOT START STREAMING

# Start Tracking Microphone Stream for Peaks
#       This function commands the connected stethoscope to begin streaming audio from the microphone and find/detect peaks
#       Input   ::      rfObject                {object}        serial object
#       Output  ::      terminal messages       {string}        terminal messages for logging
def startTrackingMicStream( rfObject ):
    print fullStamp() + " startTrackingMicStream()"      

    outByte = definitions.STARTTRACKING      
    rfObject.send(outByte)
    inByte = rfObject.recv(1)                  

    if inByte == definitions.ACK:                  
        print fullStamp() + " ACK Device will START Tracking"   

    elif inByte == definitions.NAK:
        print fullStamp() + " NAK Device CANNOT START Tracking"

    else:
        print fullStamp() + " Please troubleshoot device"


# Start Tracking Microphone Stream for Peaks
#       This function commands the connected stethoscope to stop streaming audio from the microphone and find/detect peaks
#       Input   ::      rfObject                {object}        serial object
#       Output  ::      terminal messages       {string}        terminal messages for logging
def stopTrackingMicStream( rfObject ):
    print fullStamp() + " stopTrackingMicStream()"            

    outByte = definitions.STOPTRACKING                 
    rfObject.send(outByte)
    inByte = rfObject.recv(1)                       

    if inByte == definitions.ACK:                                    
        print fullStamp() + " ACK Device will STOP Tracking"     

    elif inByte == definitions.NAK:
        print fullStamp() + " NAK Device CANNOT STOP Tracking"

    else:
        print fullStamp() + " Please troubleshoot device"


# Simulation Functions
#       These functions deal with the simulations corresponding to the connected device

# Normal Hear Beat Playback
#       This function triggers the playback of a normal heart beat
def normalHBPlayback( rfObject ):
    print fullStamp() + " normalHBPlayback()"        

    outByte = definitions.NORMALHB                   
    rfObject.send(outByte)
    inByte = rfObject.recv(1)                           

    if inByte == definitions.ACK:                
        print fullStamp() + " ACK Stethoscope will START PLAYBACK of NORMAL HEARTBEAT"

    elif inByte == definitions.NAK:
        print fullStamp() + " NAK Stethoscope CANNOT START PLAYBACK of NORMAL HEARTBEAT"

    else:
        print fullStamp() + " Please troubleshoot device"


# Early Systolic Heart Murmur
#       This function triggers the playback of an early systolic heart mumur
def earlyHMPlayback( rfObject ):
    print fullStamp() + " earlyHMPlayback()"    

    outByte = definitions.ESHMURMUR 
    rfObject.send(outByte)
    inByte = rfObject.recv(1)  

    if inByte == definitions.ACK:       
        print fullStamp() + " ACK Stethoscope will START PLAYBACK of EARLY SYSTOLIC HEART MUMUR"

    elif inByte == definitions.NAK:
        print fullStamp() + " NAK Stethoscope CANNOT START PLAYBACK of EARLY SYSTOLIC HEART MUMUR" 

    else:
        print fullStamp() + " Please troubleshoot device"

# Stop Playback
#       This function commands the connected stethoscope to stop playing an audio filed stored within the SD card
#       Input   ::      rfObject                {object}        serial object
#                       timeout                 {int}           maximum wait time for serial communication
#                       iterCheck               {int}           maximum number of iterations for serial communication
#       Output  ::      terminal messages       {string}        terminal messages for logging
def stopPlayback( rfObject ):
    print fullStamp() + " stopPlayback()"       

    outByte = definitions.STOPPLAY          
    rfObject.send(outByte)
    inByte = rfObject.recv(1)          

    if inByte == definitions.ACK:               
        print fullStamp() + " ACK Stethoscope will STOP PLAYBACK"                                                        

    elif inByte == definitions.NAK:
        print fullStamp() + " NAK Stethoscope CANNOT STOP PLAYBACK"

    else:
        print fullStamp() + " Please troubleshoot device"

# Early Systolic Heart Murmur
#       This function triggers the playback of an early systolic heart mumur
def earlyHMBlending( rfObject ):
    print fullStamp() + " earlyHMBlending()"

    outByte = definitions.STARTBLEND    
    rfObject.send(outByte)
    inByte = rfObject.recv(1)             

    if inByte == definitions.ACK:           
        print fullStamp() + " ACK Stethoscope will START BLENDING of EARLY SYSTOLIC HEART MUMUR"                                                        

    elif inByte == definitions.NAK:
        print fullStamp() + " NAK Stethoscope CANNOT START BLENDING of EARLY SYSTOLIC HEART MUMUR" 

    else:
        print fullStamp() + " Please troubleshoot device"

def startBlending( rfObject, fileByte ):
    print fullStamp() + " startBlending()"          

    outByte = fileByte                                  
    rfObject.send(outByte)
    inByte = rfObject.recv(1)              

    if inByte == definitions.ACK:               
        print fullStamp() + " ACK Stethoscope will START BLENDING of EARLY SYSTOLIC HEART MUMUR" 

    elif inByte == definitions.NAK:
        print fullStamp() + " NAK Stethoscope CANNOT START BLENDING of EARLY SYSTOLIC HEART MUMUR" 

    else:
        print fullStamp() + " Please troubleshoot device"


# Stop Playback
#       This function commands the connected stethoscope to stop playing an audio filed stored within the SD card
#       Input   ::      rfObject                {object}        serial object
#                       timeout                 {int}           maximum wait time for serial communication
#                       iterCheck               {int}           maximum number of iterations for serial communication
#       Output  ::      terminal messages       {string}        terminal messages for logging
def stopBlending( rfObject ):
    print fullStamp() + " stopBlending()"               

    outByte = definitions.STOPBLEND                     
    rfObject.send(outByte)
    inByte = rfObject.recv(1)                                 

    if inByte == definitions.ACK:                   
        print fullStamp() + " ACK Stethoscope will STOP BLENDING"

    elif inByte == definitions.NAK:
        print fullStamp() + " NAK Stethoscope CANNOT STOP BLENDING"

    else:
        print fullStamp() + " Please troubleshoot device"

# Normal Heartrate
#       This function starts Normal Heartrate playback
def startBPNorm( rfObject ):
    print fullStamp() + " startBPNorm()"

    outByte = definitions.STARTBPNORM
    rfObject.send(outByte)
    inByte = rfObject.recv(1)

    if inByte == definitions.ACK:
        print fullStamp() + " ACK Stethoscope will START NORMAL playback"     

    elif inByte == definitions.NAK:
        print fullStamp() + " NAK Stethoscope CANNOT START NORMAL playback" 

    else:
        print fullStamp() + " Please troubleshoot device"


# Bradycardia
#       This function starts Bradycardia playback
def startBPBrady( rfObject ):
    print fullStamp() + " startBPBrady()"

    outByte = definitions.STARTBPBRADY
    rfObject.send(outByte)
    inByte = rfObject.recv(1)
    
    if inByte == definitions.ACK:
        print fullStamp() + " ACK Stethoscope will START PLAYBACK of BRADYCARDIA"     

    elif inByte == definitions.NAK:
        print fullStamp() + " NAK Stethoscope CANNOT START BRADYCARDIA" 

    else:
        print fullStamp() + " Please troubleshoot device"

# Tachycardia
#       This function starts Tachycardia playback
def startBPTachy( rfObject ):
    print fullStamp() + " startBPTachy()"

    outByte = definitions.STARTBPTACHY
    rfObject.send(outByte)
    inByte = rfObject.recv(1)
    
    if inByte == definitions.ACK:
        print fullStamp() + " ACK Stethoscope will START PLAYBACK of TACHYCARDIA"
            
    elif inByte == definitions.NAK:
        print fullStamp() + " NAK Stethoscope CANNOT START TACHYCARDIA"

    else:
        print fullStamp() + " Please troubleshoot device"


# Stop All
#       This function stops all augmentation
def stopBPAll( rfObject ):
    print fullStamp() + " stopBPAll()"

    outByte = definitions.STOPBPALL
    rfObject.send(outByte)
    inByte = rfObject.recv(1)
    
    if inByte == definitions.ACK:
        print fullStamp() + " ACK Stethoscope will STOP AUGMENTING"
            
    elif inByte == definitions.NAK:
        print fullStamp() + " NAK Stethoscope CANNOT STOP AUGMENTING" 

    else:
        print fullStamp() + " Please troubleshoot device"

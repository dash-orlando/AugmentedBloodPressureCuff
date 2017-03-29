"""
bluetoothProtocol.py

The following module has been created to manage the bluetooth interface between the control system and the connected devices

Michael Xynidis
Fluvio L Lobo Fenoglietto
09/01/2016
"""

# Import Libraries and/or Modules
import bluetooth
"""
        Implementation of the "bluetooth" module may require the installation of the python-bluez package
        >> sudp apt-get install python-bluez
"""
import os
import serial
import time
from timeStamp import *
import protocolDefinitions as definitions
from    multiprocessing        import Process
from    multiprocessing        import Pipe, Queue

# Create a server socket (Incoming data)
#   PARAMATERS:
#   timeout: runtime duration before timing out (in seconds)
def serverSocket(timeout, attempts):
    print( fullStamp() + " Creating BlueTooth Socket")
    port = 1

    server_socket = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    # Empty string means any working BT adapter is fair game to use
    server_socket.bind(("",port))
    server_socket.listen(1)
    server_socket.settimeout(timeout)

    try:
        client_socket,address=server_socket.accept()
        print( fullStamp() + " Accepted connection from: ", address)
        inByte = client_socket.recv(4096)
        print( fullStamp() + " Recieved [%s]" % data)

        client_socket.close()
        server_socket.close()
        return(inByte)

    except:
        print( fullStamp() + " Connection failed")
        if attempts is not 1:
            print( fullStamp() + " Attempting..." )
            server_socket.close()
            serverSocket(timeout, attempts-1)
        

# Create a client socket (Outgoing data)
def clientSocket(bd_addr, byte):
    port = 1

    client_socket=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    client_socket.connect((bd_addr, port))

    client_socket.send(byte)

    client_socket.close()
    

# Find RF Device
#   This function uses the hardware of the peripheral device or control system to scan/find bluetooth enabled devices
#   This function does not differenciate among found devices
#   Input   ::  None
#   Output  ::  {array, list} "availableDeviceNames", "availableDeviceBTAddresses"
def findDevices():
    print fullStamp() + " findDevices()"
    devices = bluetooth.discover_devices(
        duration=20,                                                                        # Search timeout
        lookup_names=True)                                                                  # Search and acquire names of antennas
    Ndevices = len(devices)                                                                 # Number of detected devices
    availableDeviceNames = []                                                               # Initialized arrays/lists for device names...
    availableDeviceBTAddresses = []                                                         # ...and their bluetooth addresses
    for i in range(0,Ndevices):                                                             # Populate device name and bluetooth address arrays/lists with a for-loop
        availableDeviceNames.append(devices[i][1])
        availableDeviceBTAddresses.append(devices[i][0])
    print fullStamp() + " Devices found (names): " + str(availableDeviceNames)              # Print the list of devices found
    print fullStamp() + " Devices found (addresses): " + str(availableDeviceBTAddresses)    # Print the list of addresses for the devices found
    return availableDeviceNames, availableDeviceBTAddresses                                 # Return arrays/lists of devices and bluetooth addresses

# Identify Smart Devices - General
#   This function searches through the list of detected devices and finds the smart devices corresponding to the input identifier
#   Input   ::  {string}     "smartDeviceIdentifier"
#           ::  {array/list} "availableDeviceNames", "availableDeviceBTAddresses"
#   Output  ::  {array/list} "smartDeviceNames", "smartDeviceBTAddresses"
def findSmartDevices(smartDeviceIdentifier, availableDeviceNames, availableDeviceBTAddresses):
    print fullStamp() + " findSmartDevices()"
    Ndevices = len(availableDeviceNames)
    smartDeviceNames = []
    smartDeviceBTAddresses = []
    for i in range(0,Ndevices):
        deviceIdentifier = availableDeviceNames[i][0:4]
        if deviceIdentifier == smartDeviceIdentifier:
            smartDeviceNames.append(availableDeviceNames[i])
            smartDeviceBTAddresses.append(availableDeviceBTAddresses[i])
    print fullStamp() + " Smart Devices found (names): " + str(smartDeviceNames)
    print fullStamp() + " Smart Devices found (addresses): " + str(smartDeviceBTAddresses)
    return smartDeviceNames, smartDeviceBTAddresses

# Identify Smart Device - Specific
#   This function searches through the list of detected devices and finds the specific smart device corresponding to the input name
#   Input   ::  {string}     "smartDeviceName"
#           ::  {array/list} "availableDeviceNames", "availableDeviceBTAddresses"
#   Output  ::  {array/list} "smartDeviceNames", "smartDeviceBTAddresses"
def findSmartDevice(smartDeviceName, availableDeviceNames, availableDeviceBTAddresses):
    print fullStamp() + " findSmartDevices()"
    Ndevices = len(availableDeviceNames)
    smartDeviceNames = []
    smartDeviceBTAddresses = []
    for i in range(0,Ndevices):
        deviceName = availableDeviceNames[i]
        if deviceName == smartDeviceName:
            smartDeviceNames.append(availableDeviceNames[i])
            smartDeviceBTAddresses.append(availableDeviceBTAddresses[i])
    print fullStamp() + " Smart Devices found (names): " + str(smartDeviceNames)
    print fullStamp() + " Smart Devices found (addresses): " + str(smartDeviceBTAddresses)
    return smartDeviceNames, smartDeviceBTAddresses

# Create RFComm Ports
#   This function creates radio-frquency (bluetooth) communication ports for specific devices, using their corresponding address
#   Input   ::  {array/list} "deviceName", "deviceBTAddress"
#   Output  ::  {array/list} "btObjects"
def createPorts(deviceNames, deviceBTAddresses, baudrate, timeout):
    Ndevices = len(deviceNames)                                                              # Determines the number of devices listed
    rfObjects = []                                                                           # Create RF object variable/list (in case of multiple devices)
    for i in range(0,Ndevices):
        portRelease("rfcomm",i)                                                             # The program performs a port-release to ensure that the desired rf port is available
        portBind("rfcomm",i,deviceBTAddresses[i])
        rfObjects.append(serial.Serial(
            port = "/dev/rfcomm" + str(i),
            baudrate = baudrate,
            bytesize = serial.EIGHTBITS,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            timeout = timeout))
        time.sleep(1)
    return rfObjects

# Create Ports v2
#   This variation of the original create ports function creates multiple ports and verifies connectivity
def createPorts2(deviceNames, deviceBTAddresses, baudrate, timeout, attempts):
    print fullStamp() + " createPorts2()"
    Ndevices = len(deviceNames)
    print fullStamp() + " Connecting to " + str(Ndevices) + " device"
    rfObjects = []
    for i in range(0,Ndevices):
        portNumber = i
        portRelease('rfcomm',portNumber)
        portBind("rfcomm",portNumber,deviceBTAddresses[i])
        rfObjects.append(serial.Serial(
            port = "/dev/rfcomm" + str(portNumber),
            baudrate = baudrate,
            bytesize = serial.EIGHTBITS,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            timeout = timeout))
        time.sleep(1)
        #connectionChecks(rfObjects,deviceNames,deviceBTAddresses,baudrate,timeout,i,attempts)
        connectionCheck2(rfObjects,i,rfObjects[i],deviceNames[i],deviceBTAddresses[i],baudrate,timeout,attempts)
        rfObjects[i].close()
    return rfObjects

# Connection Checks
#   This variation of the connection check function handle multiple cases assuming that its embedded in a loop
#   This function has a recursive statement that triggers the reconnection of all ports listed, which is not desirable.
def connectionChecks(rfObjects,deviceNames,deviceBTAddresses,baudrate,timeout,index,attempts):
    print fullStamp() + " connectionCheck()"
    inString = rfObjects[index].readline()[:-1]
    if inString == deviceNames[index]:
        print fullStamp() + " Connection successfully established with " + deviceNames[index]
    else:
        rfObjects[index].close()
        if attempts is not 0:
            return createPorts2(deviceNames,deviceBTAddresses,baudrate,timeout,attempts-1)
        elif attempts is 0:
            print fullStamp() + " Connection Attempts Limit Reached"
            print fullStamp() + " Please troubleshoot " + deviceName

# Add Port
#   Solution to the dileman of connection checks. In its recursive call, this function only adds the port being checked
def addPort(rfObjects, index, deviceName, deviceBTAddress, baudrate, timeout, attempts):
    print fullStamp() + " addPort()"
    portNumber = index
    portRelease('rfcomm',portNumber)
    portBind("rfcomm",portNumber,deviceBTAddress)
    rfObjects.append(serial.Serial(
        port = "/dev/rfcomm" + str(portNumber),
        baudrate = baudrate,
        bytesize = serial.EIGHTBITS,
        parity = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE,
        timeout = timeout))
    time.sleep(1)
    connectionCheck2(rfObjects,index,rfObjects[index],deviceName,deviceBTAddress,baudrate,timeout,attempts)
    rfObjects[i].close()
    return rfObjects

# Connection Check v2
#   Working alternative to connection checks and add port functions
def connectionCheck2(rfObjects,index,rfObject,deviceName,deviceBTAddress,baudrate,timeout,attempts):
    print fullStamp() + " connectionCheck2()"
    if rfObject.isOpen == False:
        rfObject.open()
    inString = rfObject.readline()[:-1]
    if inString == deviceName:
        print fullStamp() + " Connection successfully established with " + deviceName
    else:
        rfObject.close()
        if attempts is not 0:
            return addPort(rfObjects,index,deviceName,deviceBTAddress,baudrate,timeout,attempts-1)
        elif attempts is 0:
            print fullStamp() + " Connection Attempts Limit Reached"
            print fullStamp() + " Please troubleshoot " + deviceName

# Create RFComm Port
#   This function establishes a RF serial communication port
#   Input   ::  {string}    device name
#           ::  {string}    device bluetooth address
#           ::  {int}       baudrate
#           ::  {int}       timeout
#   Output  ::  {object}    serial object

def createPort(deviceName,deviceBTAddress,baudrate,timeout,attempts, q):
    portRelease("rfcomm",0)                                                             # The program performs a port-release to ensure that the desired rf port is available
    portBind("rfcomm",0,deviceBTAddress)
    rfObject = serial.Serial(
        port = "/dev/rfcomm" + str(0),
        baudrate = baudrate,
        bytesize = serial.EIGHTBITS,
        parity = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE,
        timeout = timeout)
    time.sleep(1)
    outByte = definitions.ENQ                                                                               # Send SOH (Start of Heading) byte - see protocolDefinitions.py
    rfObject.write(outByte)
    inByte = rfObject.read(size=1)
    if inByte == definitions.ACK:                                                                           # Check for ACK / NAK response
        print fullStamp() + " ACK Connection Established"
        rfObject.close()
        #q.put_nowait(rfObject)
        return rfObject
        
    elif inByte == definitions.NAK:
        print fullStamp() + " NAK device NOT READY"
    else:
        rfObject.close()
        if attempts is not 0:
            return createPort(deviceName,deviceBTAddress,baudrate,timeout,attempts-1, q)
        elif attempts is 0:
            print fullStamp() + " Attempts limit reached"
            print fullStamp() + " Please troubleshoot devices"

# Create Port 2
#   This function is a variation of the standard create port function, which establishes a RF serial communication port
#   This variation performs a character or string-based verification with the control system
#   Input   ::  {string}    device name
#           ::  {string}    device bluetooth address
#           ::  {int}       baudrate                        --Communication speed, bits per minute (bpm)
#           ::  {int}       timeout                         --Connection timeout
#           ::  {int}       attempts                        --Number of recursive connection attempts the program will execute
#   Output  ::  {object}    serial object

def createPort2(deviceName,deviceBTAddress,baudrate,timeout,attempts):
    portRelease("rfcomm",0)
    portBind("rfcomm",0,deviceBTAddress)
    rfObject = serial.Serial(
        port = "/dev/rfcomm" + str(0),
        baudrate = baudrate,
        bytesize = serial.EIGHTBITS,
        parity = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE,
        timeout = timeout)
    time.sleep(1)
    connectionCheck(rfObject,deviceName,deviceBTAddress,baudrate,timeout,attempts)
    rfObject.close()
    return rfObject

# Create Port -Simple
#   Simplest varient of the create port function
def createPortS(deviceName,portNumber,deviceBTAddress,baudrate,attempts):
    print fullStamp() + " createPortS()"
    portRelease("rfcomm",portNumber)
    portBind("rfcomm",portNumber,deviceBTAddress)
    rfObject = serial.Serial(
        port = "/dev/rfcomm" + str(portNumber),
        baudrate = baudrate)
    time.sleep(1)
    #connectionCheckS(rfObject,deviceName,portNumber,deviceBTAddress,baudrate,attempts)
    rfObject.close()
    return rfObject

# Connection Check
#   The following function verifies the connection to the desired device.
#   The current iteration of this function uses character/string communication between the control system and the connected device.
#   Input   ::  {object}    serial object
#           ::  {string}    device name
#           ::  {int}       attempts
#   Output  ::  {string}    terminal messages

def connectionCheck(rfObject,deviceName,deviceBTAddress,baudrate,timeout,attempts):
    print fullStamp() + " connectionCheck()"
    inString = rfObject.readline()[:-1]
    if inString == deviceName:
        print fullStamp() + " Connection successfully established with " + deviceName
    else:
        rfObject.close()
        if attempts is not 0:
            return createPort2(deviceName,deviceBTAddress,baudrate,timeout,attempts-1)
        elif attempts is 0:
            print fullStamp() + " Connection Attempts Limit Reached"
            print fullStamp() + " Please troubleshoot " + deviceName

# Connection Check -Simple
#   Simplest variant of the connection check functions
def connectionCheckS(rfObject,deviceName,portNumber,deviceBTAddress,baudrate,attempts):
    print fullStamp() + " connectionCheck()"
    inString = rfObject.readline()[:-1]
    if inString == deviceName:
        print fullStamp() + " Connection successfully established with " + deviceName
    else:
        if rfObject.isOpen() == False:
            rfObject.open()
        print fullStamp() + " Sending Stopping Message"
        rfObject.write('s')
        rfObject.close()
        if attempts is not 0:
            return createPortS(deviceName,portNumber,deviceBTAddress,baudrate,attempts-1)
        elif attempts is 0:
            print fullStamp() + " Connection Attempts Limit Reached"
            print fullStamp() + " Please troubleshoot " + deviceName

# Port Bind
#   This function binds the specified bluetooth device to a rfcomm port
#   Input   ::  {string} port type, {int} port number, {string} bluetooth address of device
#   Output  ::  None -- Terminal messages
def portBind(portType, portNumber, deviceBTAddress):
    print fullStamp() + " Connecting device to " + portType + str(portNumber)                    # Terminal message, program status
    os.system("sudo " + portType + " bind /dev/" + portType + str(portNumber) + " " + deviceBTAddress)     # Bind bluetooth device to control system

# Port Release
#   This function releases the specified communication port (serial) given the type and the number
#   Input   ::  {string} "portType", {int} "portNumber"
#   Output  ::  None -- Terminal messages
def portRelease(portType, portNumber):
    print fullStamp() + " Releasing " + portType + str(portNumber)                               # Terminal message, program status
    os.system("sudo " + portType + " release " + str(portNumber))                           # Releasing port through terminal commands

# Port Message Check
#   Reads serial port and checks for a specific input message
#   Input   ::  {string} "inString" -- String to be compared

# Send Until ReaD
#       This function sends an input command through the rfcomm port to the remote device
#       The function sends such command persistently until a timeout or iteration check are met
#       Input   ::      rfObject                {object}        serial object
#                       outByte                 {chr}           command in characters/bytes
#                       timeout                 {int}           maximum wait time for serial communication
#                       iterCheck               {int}           maximum number of iterations for serial communication
#       Output  ::      inByte                  {chr}           response from remote device in characters/bytes
#                       terminal messages       {string}        terminal messages for logging      
def sendUntilRead(rfObject, outByte, timeout, iterCheck):
    print fullStamp() + " sendUntilRead()"                                                                  # Printing program name
    iterCount = 0
    startTime = time.time()                                                                                 # Initial time, instance before entering "while loop"
    while (time.time() - startTime) < timeout and iterCount <= iterCheck:                                   # While loop - will continue until either timeout or iteration check is reached
        print fullStamp() + " Communication attempt " + str(iterCount) + "/" + str(iterCheck)
        print fullStamp() + " Time = " + str(time.time()-startTime)
        rfObject.write(outByte)                                                                             # Send CHK / System Check request
        inByte = rfObject.read()                                                                            # Read response from remote device
        if inByte == definitions.ACK:                                                                       # If response equals ACK / Positive Acknowledgement
            # print fullStamp() + " ACK"                                                                    # Print terminal message, device READY / System Check Successful                                                                             
            return inByte                                                                                   # Return the byte read from the port
            break                                                                                           # Break out of the "while loop"
        elif inByte == definitions.NAK:                                                                     # If response equals NAK / Negative Acknowledgement
            # print fullStamp() + " NAK"                                                                    # Print terminal message, device NOT READY / System Check Failed
            return inByte                                                                                   # Return the byte read from the port
            break                                                                                           # Break out of the "while loop"

# Timed Read
#   This function reads information from the serial port for a given amount of time
#   Input   ::  {object} serial object, {int} time in seconds
#   Output  ::  None - terminal printsouts  
def timedRead(rfObject, timeout):
    startTime = time.time()
    while (time.time() - startTime) < timeout:
        print "Time = " + str(time.time() - startTime)
        inString = rfObject.read()
        if inString == chr(0x05):
            print "ENQ"
            break
        elif inString == chr(0x06):
            print "ACK"
            break

# Connect to paired device
#   Connects to the bluetooth devices specified by the scenario configuration file
#   Input   ::  {array/list} "deviceName", "deviceBTAddress"
#   Output  ::  {array/list} "btObjects"


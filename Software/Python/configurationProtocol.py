"""
configurationProtocol.py

The following python module contains fuctions specific to the management of configuration files within the control system

Fluvio L Lobo Fenoglietto
09/01/2016


List of functions ::

X - Read configuration (.XML) file
X - Write configuration (.XML) file

"""

# Import External Modules
from os.path import expanduser
from timeStamp import fullStamp
import xml.etree.ElementTree as etree

# Get MAC address
#   The following function returns the MAC address of the input interface
#   Input   ::  {string}    interface   eth0, wlan0
#   Output  ::  {string}    MAC address
def getMAC(interface):
    print fullStamp() + " getMAC()"
    print fullStamp() + " Searching MAC address for " + interface + " module"
    try:
        address = open("/sys/class/net/" + interface + "/address").read()[:-1]
        print fullStamp() + " MAC (" + interface + "): " + address
        return address
    except:
        print fullStamp() + " Failed to find address, check input interface"

# Define Path Variables
#   The following function defines the path variables for the relevant directories used throughout the control system functions
#   The program does not handle other operating systems
def definePaths():
    print fullStamp() + " definePaths()"
    homeDir = expanduser("~")                                                                   # Use expand-user to identify the home directory
    rootDir = "/root"                                                                           # This is the returnof expand-user if the function is executed within a raspbian system
    if homeDir == rootDir:
        print fullStamp() + " OS - Raspbian OS"
        homeDir = "/home/pi"                                                                    # if the two strings are equivalent, then the program must have been executed from a raspbian system. A correction to the home directory has to be made.
        pythonDir = homeDir + "/pd3d/csec/repos/ControlSystem/Software/Python"                  # Python directory
        configDir = pythonDir + "/configuration"                                                # Configuration directory
        configFile = configDir + "/config.xml"                                           # Configuration file
        dataDir = pythonDir + "/data"                                                           # Data directory
        outputDir = dataDir + "/output"                                                         # Output directory
    else:
        print fullStamp() + " User executed function on an OS that is not supported..."
        pythonDir = 0
        configDir = 0
        configFile = 0
        dataDir = 0
        outputDir = 0
    return pythonDir, configDir, configFile, dataDir, outputDir

# Read Configuration (.XML) File
#   Reads or imports information from configuration file into an object or structure
#   Input  :: path to configuration file (string)
#   Output :: configuration file structure
def readConfigFile(configFile):
    print fullStamp() + " readConfigFile()"
    tree = etree.parse(configFile)
    root = tree.getroot()
    return tree, root

# Self Identification
#   This function uses the MAC address of the control system to identify itself within the configuration XML file
#   Input   ::  {string}        MAC address
#           ::  {structure}     tree
#           ::  {structure}     root
#   Output  ::  {string}        terminal message
def selfID(address, tree, root):
    print fullStamp() + " selfID()"
    Npanels = len(root[1])
    print fullStamp() + " Found " + str(Npanels) + " instrument panels"
    for i in range(0,Npanels):
        mac_bt = root[1][i][0].get("mac_bt")
        mac_eth = root[1][i][0].get("mac_eth")
        mac_wlan = root[1][i][0].get("mac_wlan")
        panelID = root[1][i].get("id")
        if address == mac_bt:
            print fullStamp() + " Match on BT MAC address"
            panelIndex = i
            print fullStamp() + " Panel id = " + panelID
            print fullStamp() + " Panel index = " + str(panelIndex)
            return panelIndex, panelID
            break
        elif address == mac_eth:
            print fullStamp() + " Match on eth MAC address"
            panelIndex = i
            print fullStamp() + " Panel id = " + panelID
            print fullStamp() + " Panel index = " + str(panelIndex)
            return panelIndex, panelID
            break
        elif address == mac_wlan:
            print fullStamp() + " Match on wlan MAC address"
            panelIndex = i
            print fullStamp() + " Panel id = " + panelID
            print fullStamp() + " Panel index = " + str(panelIndex)
            return panelIndex, panelID
            break
        elif i == Npanels - 1:
            #print fullStamp() + " Panel " + str(number) + " NOT found"
            scenarioIndex = -1
            panelID = "NA"
            return panelIndex, panelID

# Find Scenario Index
#   The following function finds the configuration file index for the scenario number passed as an input
def findScenario(number, tree, root):
    print fullStamp() + " findScenario()"
    Nscenarios = len(root[2])
    print fullStamp() + " Found " + str(Nscenarios) + " scenarios"
    for i in range(0,Nscenarios):
        scenarioID = root[2][i].get("id")
        scenarioNumber = int(root[2][i].get("number"))
        if scenarioNumber == number:
            print fullStamp() + " Scenario " + str(number) + " found on index " + str(i)
            print fullStamp() + " Scenario id = " + scenarioID
            scenarioIndex = i
            scenarioNumber = number
            return scenarioIndex, scenarioNumber, scenarioID
            break
        elif i == Nscenarios - 1:
            print fullStamp() + " Scenario " + str(number) + " NOT found"
            scenarioIndex = -1
            scenarioNumber = number
            scenarioID = "NA"
            return scenarioIndex, scenarioNumber, scenarioID

# Pull Scenario Parameters
#   The following function pulls scenario parameters from the configuration XML
#   Input   ::  {int}           scenario index
#           ::  {structure}     tree
#           ::  {structure}     root
#   Output  ::  {array/list}    timers

def pullParameters(scenarioIndex, tree, root):
    print fullStamp() + " pullParameters()"
    parametersIndex = 1
    timers = []
    Nparameters = len(root[2][scenarioIndex][parametersIndex])
    for i in range(0,Nparameters):
        parameterType = root[2][scenarioIndex][parametersIndex][i].get("type")
        if parameterType == "timer":
            timerName = root[2][scenarioIndex][parametersIndex][i].get("name")
            timerValue = int(root[2][scenarioIndex][parametersIndex][i].text)
            timers.append(timerValue)
            print fullStamp() + " Timer found, " + timerName + " = " + str(timerValue)
        else:
            print fullStamp() + " Unknown parameter '" + parameterType + "' found"
    return timers

# Pull Scenario Instruments
#   The following function finds the devices listed under the scenario section of the configuration XML.
#   Input   ::  {int}           scenario index
#           ::  {structure}     tree
#           ::  {structure}     root
#   Output  ::  {array/list}    scenario devices

def pullInstruments(panelIndex, scenarioIndex, tree, root):
    print fullStamp() + " pullInstruments()"
    devicesIndex = 2
    scenarioDeviceNames = []
    Nscenariodevices = len(root[2][scenarioIndex][devicesIndex])
    for i in range(0, Nscenariodevices):
        deviceName = root[2][scenarioIndex][devicesIndex][i].get("name")
        scenarioDeviceNames.append(deviceName)
        print fullStamp() + " Device found, " + deviceName
    return scenarioDeviceNames

# Pull Panel Instruments
#   The following function finds the devices associated with a selected instrument panel
#   Input   ::  {int}           panel index
#           ::  {structure}     tree
#           ::  {structure}     root
#   Output  ::  {array/list}    panel devices

def pullPanelInstruments(panelIndex, tree, root):
    print fullStamp() + " pullPanelInstruments()"
    devicesIndex = 2
    panelDeviceIDs = []
    panelDeviceTypes = []
    panelDeviceNames = []
    panelDeviceBTAddresses = []
    panelDevicePortNums = []
    Npaneldevices = len(root[1][panelIndex])
    for i in range(0, Npaneldevices):
        deviceID = root[1][panelIndex][i].get("id")
        deviceType = root[1][panelIndex][i].get("type")
        deviceName = root[1][panelIndex][i].get("name")
        deviceBTAddress = root[1][panelIndex][i].get("mac_bt")
        devicePortNum = root[1][panelIndex][i].get("port_num")
        panelDeviceIDs.append(deviceID)
        panelDeviceTypes.append(deviceType)
        panelDeviceNames.append(deviceName)
        panelDeviceBTAddresses.append(deviceBTAddress)
        panelDevicePortNums.append(devicePortNum)
        print fullStamp() + " Device found, " + deviceName
    return panelDeviceIDs, panelDeviceTypes, panelDeviceNames, panelDeviceBTAddresses, panelDevicePortNums

# Instrument Cross Reference
#   The following function cross-references the scenario devices list with the devices listed under the connected instrument panel and control system.
#   Finally, the program generates lists with the specific devices to be triggered and their respective hardware addresses
#   Input   ::  {int}           panel index
#           ::  {array/list}    scenario devices
#           ::  {structure}     tree
#           ::  {structure}     root
#   Output  ::  {array/list}    device names
#           ::  {array/list}    device bluetooth addresses#

def instrumentCrossReference(panelIndex, scenarioDeviceNames, tree, root):
    print fullStamp() + " instrumentCrossReference()"
    deviceIndex = []
    deviceTypes = []
    deviceNames = []
    deviceAddresses = []
    Nscenariodevices = len(scenarioDeviceNames)
    Npaneldevices = len(root[1][panelIndex])
    for i in range(0,Nscenariodevices):
        scenarioDeviceName = scenarioDeviceNames[i]
        for j in range(0,Npaneldevices):
            panelDeviceType = root[1][panelIndex][j].get("type")
            panelDeviceName = root[1][panelIndex][j].get("name")
            panelDeviceAddress = root[1][panelIndex][j].get("mac_bt")
            if scenarioDeviceName == panelDeviceName:
                deviceIndex.append(j)
                deviceTypes.append(panelDeviceType)
                deviceNames.append(panelDeviceName)
                deviceAddresses.append(panelDeviceAddress)
                print fullStamp() + " Matched " + panelDeviceName + ", of type " + panelDeviceType + ", with address " + panelDeviceAddress + ", on index " + str(j)
    return deviceIndex, deviceTypes, deviceNames, deviceAddresses
  
"""
References

1- XML eTree elementTree - https://docs.python.org/2/library/xml.etree.elementtree.html
"""

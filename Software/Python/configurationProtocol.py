"""
Stethoscope Configuration Protocol

The following module contains functions used to link resources to the main device scripts

Fluvio L Lobo Fenoglietto 11/15/2017
"""

# ================================================================================= #
# Import Libraries and/or Modules
# ================================================================================= #

from    os.path     import expanduser
import  sys
from    timeStamp   import fullStamp

# ================================================================================= #
# Define Path
#
# Define single device path
#
# Fluvio L Lobo Fenoglietto 11/15/2017
# ================================================================================= #
def definePath(device):
    baseDir = expanduser("~")                                                       # get main/root or base directory for the operating system in use
    rootDir = "/root"                                                                           # root directory for Linux - Raspbian
    if baseDir == rootDir:
        homeDir     = "/home/pi"
        pythonDir   = homeDir + "/pd3d/csec/repos/ControlSystem/Software/Python"
        deviceDir   = pythonDir + "/" + device + "/"
        outputDir   = pythonDir + "/consys/output"
        dataDir     = pythonDir + "/consys/data"
    else:
        homeDir = "/home/pi"
        pythonDir = homeDir + "/pd3d/csec/repos/ControlSystem/Software/Python"
        deviceDir = pythonDir + "/" + device + "/"
        outputDir   = pythonDir + "/consys/output"
        dataDir     = pythonDir + "/consys/data"

    return homeDir, pythonDir, deviceDir, outputDir, dataDir

# ================================================================================= #
# Define Paths
#
# Define all paths of importance
#
# Fluvio L Lobo Fenoglietto 05/25/2018
# ================================================================================= #
def definePaths():
    print( fullStamp() + " definePaths()" )
    paths       = []
    paths.append( "/home/pi" )
    paths.append( paths[0] + "/pd3d/csec/repos/ControlSystem/Software/Python" )
    paths.append( paths[1] + "/consys/" )
    paths.append( paths[1] + "/stethoscope/" )
    paths.append( paths[1] + "/smarthandle/" )
    paths.append( paths[1] + "/smartholder/" )
    paths.append( paths[1] + "/bloodpressurecuff/" )
    paths.append( paths[1] + "/consys/output" )
    paths.append( paths[1] + "/consys/data" )

    pythonDir   = paths[1]
    consDir     = paths[2]
    stetDir     = paths[3]
    shanDir     = paths[4]
    sholDir     = paths[5]
    bpcuDir     = paths[6]
    outputDir   = paths[7]
    dataDir     = paths[8]

    return paths, pythonDir, consDir, stetDir, shanDir, sholDir, bpcuDir, outputDir, dataDir

# ================================================================================= #
# Insert Path
#
# Insert defined directory path into the python directory
#
# Fluvio L Lobo Fenoglietto 11/15/2017
# ================================================================================= #
def addPath(path):
    if isinstance(path, list):
        Npaths = len(path)
        for i in range(0, Npath):
            sys.path.insert(0, path[i])
        response = True
    else:
        sys.path.insert(0, path)
        response = False
    return response

# ================================================================================= #
# Insert Paths
#
# Insert all paths within input array python directory
#
# Fluvio L Lobo Fenoglietto 05/25/2018
# ================================================================================= #
def addPaths(paths):
    if isinstance(paths, list):
        Npaths = len(paths)
        for i in range(0, Npaths):
            sys.path.insert(0, paths[i])
        response = True
    else:
        sys.path.insert(0, paths)
        response = False
    return response


# ================================================================================= #
# Get MAC address
#
# Function to retrieve MAC address
#
# Fluvio L Lobo Fenoglietto 05/25/2018
# ================================================================================= #
def getMAC(interface):
    print( fullStamp() + " getMAC()" )
    print( fullStamp() + " Searching MAC address for " + interface + " module" )
    try:
        address = open("/sys/class/net/" + interface + "/address").read()[:-1]
        print( fullStamp() + " MAC (" + interface + "): " + address )
        return address
    except:
        print( fullStamp() + " Failed to find address, check input interface" )

# ================================================================================= #
# Self Identification
#
# Function to self-identify the panel using a MAC address
#
# Fluvio L Lobo Fenoglietto 05/28/2018
# ================================================================================= #
def panelSelfID(id_file_path, device_address):
    print( fullStamp() + " panelSelfID()" )                                         # signals execution of the function

    dataFile = open( id_file_path, 'r' )                                            # opens data file with panel information
    line_num             = 0
    panel_id_list        = []                                                       # define array variable
    panel_address_list   = []
    for line in dataFile:                                                           # for each line in the file ...
        if len(line) <= 1:                                                          # if nothing in line ... pass
            pass
        elif line[0] == "#":                                                        # if line starts with number sign (= comment) ... pass
            pass
        else:                                                                       # in any other case ...
            trim_line = line[:-1]                                                   # trim line by ignoring "end of line" character
            split_line = trim_line.split(",")                                       # split line with comma delimiter (default)
            panel_id_list.append( split_line[0] )                                   # append the first element as the number id
            panel_address_list.append( split_line[1] )                              # append the second element as the MAC address
            if split_line[1] == device_address:                                     # compare each address to the input panel/device MAC address
                panel_id        = panel_id_list[line_num]                           # if so ... store id number
                panel_address   = panel_address_list[line_num]                      # if so ... associate address too ...
                print( fullStamp() + " Self identified as PANEL" + str(panel_id) )

            line_num = line_num + 1

    return panel_id_list, panel_address_list, panel_id, panel_address
    
# ================================================================================= #
# Device Identification
#
# Function to identify devices associated with the operating panel
#
# Fluvio L Lobo Fenoglietto 05/28/2018
# ================================================================================= #
def panelDeviceID(id_file_path, panel_id):
    print( fullStamp() + " panelDeviceID()" )

    dataFile = open( id_file_path, 'r' )
    
    line_num                = 0
    device_id_list          = []
    device_name_list        = []
    device_bt_address_list  = []
    
    for line in dataFile:                                                           # for each line in the file ...
        if len(line) <= 1:                                                          # if nothing in line ... pass
            pass
        elif line[0] == "#":                                                        # if line starts with number sign (= comment) ... pass
            pass
        else:
            trim_line = line[:-1]                                                   # trim line by ignoring "end of line" character
            split_line = trim_line.split(",")                                       # split line with comma delimiter (default)
            device_id_list.append( split_line[0] )
            device_name_list.append( split_line[1] )
            device_bt_address_list.append( split_line[2] )

            line_num = line_num + 1

    return device_id_list, device_name_list, device_bt_address_list
            







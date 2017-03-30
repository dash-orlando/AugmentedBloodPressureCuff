'''
#
# A script that automates launching of pressureDialGauge.py on boot
# Script must live in the same working directory as launchOnBoot.sh
#
# Author: Mohammad Odeh
# Date: Mar. 9th, 2017
#
'''

import sys, os, platform, argparse
from os import path, listdir, lseek
from shutil import copy, copytree, rmtree, ignore_patterns

# Construct Argument Parser
ap = argparse.ArgumentParser()
ap.add_argument("-u", "--update", action="store_true", required=False,
                help="Update current folder with all the files present in the Github repository")
args = vars(ap.parse_args())


print'''
# ************************************************************************
#                               AUTOLAUNCH SCRIPT
# ************************************************************************
'''

if platform.system()=='Linux':

    # Define useful paths
    homeDir = "/home/pi"
    src = os.getcwd() + "/launchOnBoot.sh"
    dst = homeDir
    PATH = homeDir + "/.config/lxsession/LXDE-pi/autostart"

# If autolaunch has been configured, do nothing
if (os.path.isfile(dst + "/launchOnBoot.sh")):
    print(">>> Autolaunch on boot is already enabled.")
    print(">>> No further action is required.")

# If autolaunch has NOT been configured, configure it
else:
    print(">>> Configuring autolaunch.")
    
    # Copy launchOnBoot.py to the home directory
    copy(src, dst)

    # Append the launch command to the autostart file
    with open(PATH, "a") as f:
        f.write("./launchOnBoot.sh\n")
        f.close()

    print(">>> Successful.\n>>> Please reboot.\n")


print'''
# ************************************************************************
#                       COPY FILES/DIRECTORIES + MODULES
# ************************************************************************
'''

'''
# Enumerate expected files to be present at directory
files = ["bluetoothProtocol.py",
         "bluetoothProtocol_teens32.py",
         "configurationProtocol.py",
         "dial.py",
         "pressureCuffDefinitions.py",
         "pressureCuffProtocol.py",
         "pressureCuffTest.py",
         "pressureDialGauge.py",
         "protocolDefinitions.py",
         "readPressure.py",
         "stethoscopeDefinitions.py",
         "stethoscopeProtocol.py",
         "stethoscopeTest.py",
         "timeStamp.py"]
'''

if platform.system()=='Linux':

    # Define useful paths
    homeDir = "/home/pi"
    src = os.getcwd() + "/Python"
    dst = homeDir + "/Desktop/AugmentedBloodPressureCuff"
    srcContent = listdir(src)

# If files have already been copied, do nothing
if (path.exists(dst)):
    print(">>> AugmentedBloodPressureCuff Directory exists.\n>>> Checking files...")

    # If update argument is provided, update folder
    if args["update"]:
        print(">>> Cleaning up...")
        rmtree(dst)
        print(">>> Removed old files...")
        copytree(src, dst, ignore=ignore_patterns('*.pyc', 'tmp*'))
        print(">>> Updated current USER folder.")

    # Compare sizes of both folders
    dstContent = listdir(dst)
    if len(srcContent) > len(dstContent):          
        print(">>> The Github folder is ahead by %i file" %(len(srcContent)-len(dstContent)) )
        print(">>> Run this script using -u/--update to update USER folder.")
        print(">>> WARNING: Running the update WILL OVERWRITE current files.")
    else:
        print(">>> No further action is required.")
    

# If files have NOT been copied, copy them
else:
    print(">>> Copying files and directories...")
    
    # Copy files and directories to the home directory
    copytree(src, dst, ignore=ignore_patterns('*.pyc', 'tmp*'))

    print(">>> Files and directories have been successfuly copied.")



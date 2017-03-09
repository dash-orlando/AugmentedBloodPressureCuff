'''
#
# A script that automates launching of pressureDialGauge.py on boot
# Script must live in the same working directory as launchOnBoot.sh
#
# Author: Mohammad Odeh
# Date: Mar. 9th, 2017
#
'''

import sys, os, platform
import os.path
from shutil import copy

if platform.system()=='Linux':

    # Define useful paths
    homeDir = "/home/pi"
    src = os.getcwd() + "/launchOnBoot.sh"
    dst = homeDir
    PATH = homeDir + "/.config/lxsession/LXDE-pi/autostart"

# If autolaunch has been configured, do nothing
if (os.path.isfile(dst + "/launchOnBoot.sh")):
    print("Autolaunch on boot is already enabled.")
    print("No further action is required.")

# If autolaunch has NOT been configured, configure it
else:
    print("Configuring autolaunch.")
    
    # Copy launchOnBoot.py to the home directory
    copy(src, dst)

    # Append the launch command to the autostart file
    with open(PATH, "a") as f:
        f.write("./launchOnBoot.sh\n")
        f.close()

    print("Successful\nPlease reboot")






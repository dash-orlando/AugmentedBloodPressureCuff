'''
#
# Read pressure sensor and display readings on a dial gauge
#
# Adapted from: John Harrison's original work
# Link: http://cratel.wichita.edu/cratel/python/code/SimpleVoltMeter
#
# Modified by: Mohammad Odeh
# Date       : Mar. 7th, 2017
# Updated    : Jun. 1st, 2017
#
# VERSION 0.4.1
#
# CHANGELOG:
#   1- Switched entire communication protocol from PySerial in favor of PyBluez
#   2- Program now closes BT port on exit
#   3- Added option to change sampling frequency
#
# KNOWN ISSUES:
#   1- Searching for stethoscope puts everything on hold (inherit limitation of PyBluez)
#   2- If no BT device is connected, pushing exit will throw an error (but still closes program)
#
'''

# ************************************************************************
# IMPORT MODULES
# ************************************************************************

# Python modules
import  sys, time, bluetooth, serial, argparse                  # 'nuff said
import  Adafruit_ADS1x15                                        # Required library for ADC converter
from    PyQt4               import QtCore, QtGui, Qt            # PyQt4 libraries required to render display
from    PyQt4.Qwt5          import Qwt                          # Same here, boo-boo!
from    numpy               import interp                       # Required for mapping values
from    threading           import Thread                       # Run functions in "parallel"
from    os                  import getcwd, path, makedirs       # Pathname manipulation for saving data output

# PD3D modules
from    dial                        import Ui_MainWindow        # Imports pre-built dial guage from dial.py
from    timeStamp                   import fullStamp            # Show date/time on console output
from    stethoscopeProtocol         import *					# import all functions from the stethoscope protocol
from    bluetoothProtocol_teensy32  import *					# import all functions from the bluetooth protocol -teensy3.2

# ************************************************************************
# CONSTRUCT ARGUMENT PARSER 
# ************************************************************************
ap = argparse.ArgumentParser()

ap.add_argument("-f", "--frequency", type=int, default=1,
                help="set sampling frequency (in secs).\nDefault=1")
ap.add_argument("-d", "--debug", action='store_true',
                help="invoke flag to enable debugging")

args = vars( ap.parse_args() )

# ************************************************************************
# SETUP PROGRAM
# ************************************************************************

class MyWindow(QtGui.QMainWindow):

    pressureValue = 0
    lastPressureValue = 0
    
    def __init__(self, parent=None):

        # Initialize program and extract dial GUI
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.thread = Worker(self)

        # Close rfObject socket on exit
        self.ui.pushButtonQuit.clicked.connect( lambda: closeBTPort(self.thread.rfObject) )

        # Setup gauge-needle dimensions
        self.ui.Dial.setOrigin(90.0)
        self.ui.Dial.setScaleArc(0.0,340.0)
        self.ui.Dial.update()
        self.ui.Dial.setNeedle( Qwt.QwtDialSimpleNeedle(
                                                        Qwt.QwtDialSimpleNeedle.Arrow,
                                                        True, Qt.QColor(Qt.Qt.red),
                                                        Qt.QColor(Qt.Qt.gray).light(130)
                                                        )
                                )

        self.ui.Dial.setScaleOptions( Qwt.QwtDial.ScaleTicks |
                                      Qwt.QwtDial.ScaleLabel | Qwt.QwtDial.ScaleBackbone )

        # Small ticks are length 5, medium are 15, large are 20
        self.ui.Dial.setScaleTicks(5, 15, 20)
        
        # Large ticks show every 20, put 10 small ticks between
        # each large tick and every 5 small ticks make a medium tick
        self.ui.Dial.setScale(10.0,10.0,20.0)
        self.ui.Dial.setRange(0.0, 300.0)
        self.ui.Dial.setValue(0)

        # List all available BT devices
        address = deviceBTAddress[1]
        self.ui.pushButtonPair.setEnabled(True)
        self.ui.pushButtonPair.setText(QtGui.QApplication.translate("MainWindow", "Click to Connect", None, QtGui.QApplication.UnicodeUTF8))
        self.ui.pushButtonPair.clicked.connect(lambda: self.connectStethoscope(address))
##        for name,address in self.scan_rfObject():
##            if address is not None:
##                self.ui.pushButtonPair.setEnabled(True)
##                self.ui.pushButtonPair.setText(QtGui.QApplication.translate("MainWindow", "Click to Connect", None, QtGui.QApplication.UnicodeUTF8))
##                self.ui.pushButtonPair.clicked.connect(lambda: self.connectStethoscope(address))
##            #self.ui.rfObjectSelect.addItem(address)

    # Connect to stethoscope
    def connectStethoscope(self, address):
        self.thread.deviceBTAddress = str( address )
        self.ui.Dial.setEnabled(True)
        self.ui.pushButtonPair.setEnabled(False)

        # ************************************************* #
        #               DATA STORAGE: START                 #
        # ************************************************* #

        # Create data output folder/file
        self.dataFileDir = getcwd() + "/dataOutput/" + fullStamp()
        self.dataFileName = self.dataFileDir + "/output.txt"
        if(path.exists(self.dataFileDir)) == False:
            makedirs(self.dataFileDir)
            print( fullStamp() + " Created data output folder" )

        # Write basic information to the header of the data output file
        with open(self.dataFileName, "a") as dataFile:
            dataFile.write( "Date/Time: " + fullStamp() + "\n" )
            dataFile.write( "Scenario: #" + str(scenarioNumber) + "\n" )
            dataFile.write( "Device Name: " + deviceName + "\n" )
            dataFile.write( "Units: seconds, kPa, mmHg" + "\n" )
            dataFile.close()
            print( fullStamp() + " Created data output .txt file" )
            
        # ************************************************* #
        #               DATA STORAGE: END                   #
        # ************************************************* #
        
        # set timeout function for updates
        self.ctimer = QtCore.QTimer()
        self.ctimer.start(10)
        QtCore.QObject.connect(self.ctimer, QtCore.SIGNAL( "timeout()" ), self.UpdateDisplay)

    # Update Dial Gauge display   
    def UpdateDisplay(self):
        if self.pressureValue != self.lastPressureValue:
            self.ui.Dial.setValue(self.pressureValue)
            self.lastPressureValue = self.pressureValue

    # Scan for available BT devices
    def scan_rfObject(self):
        """scan for available BT devices. return a list of tuples (num, name)"""
        available = []
        BT_name, BT_address = findSmartDevice( deviceBTAddress[1] )
        if BT_name != 0:
            available.append( (BT_name[0], BT_address[0]) )
            return available

##    # TESTING STUFF HERE!
##    def populateList(self):
##        # List all available BT devices
##        for name,address in self.scan_rfObject():
##            self.ui.rfObjectSelect.addItem(address)

# ************************************************************************
# CLASS FOR OPTIONAL INDEPENDENT THREAD
# ************************************************************************

class Worker(QtCore.QThread):

    deviceBTAddress = 'none'

    # Create flags for what mode we are running
    normal = True
    playback = False
    
    # Define sasmpling frequency (units: sec) controls writing frequency
    wFreq = args["frequency"]
    wFreqTrigger = time.time()
    
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        # self.exiting = False # not sure what this line is for
        print( fullStamp() + " Initializing Worker Thread" )
        self.owner = parent
        self.start()

    def __del__(self):
        print( fullStamp() + " Exiting Worker Thread" )

    def run(self):
        # this method is called by self.start() in __init__()
        # Do nothing until device is selected from dropdown list
        while self.deviceBTAddress == 'none':
            time.sleep(0.1)

        # Establish communication after a device is selected
        try:
            self.rfObject = createBTPort( self.deviceBTAddress, port )
            print( fullStamp() + " Opened " + str(self.deviceBTAddress) )

            #Delay for stability
            QtCore.QThread.sleep(2)

            # Send an enquiry byte
            self.status = statusEnquiry( self.rfObject )

            if self.status == True:
                # Update labels
                self.owner.ui.pushButtonPair.setText(QtGui.QApplication.translate("MainWindow", "Paired", None, QtGui.QApplication.UnicodeUTF8))
                #self.owner.ui.CommandLabel.setText( "Successfully Paired" )
            
            # Save initial time since script launch
            # Used to timestamp the readings
            self.startTime = time.time()
            
            while True:
                self.owner.pressureValue = self.readPressure()

        except Exception as instance:
            print( fullStamp() + " Failed to connect" )
            print( fullStamp() + " Exception or Error Caught" )
            print( fullStamp() + " Error Type " + str(type(instance)) )
            print( fullStamp() + " Error Arguments " + str(instance.args) )
            
    def readPressure(self):

        # Perform pressure readings and convert value to mmHg
        V_analogRead = ADC.read_adc(0, gain=GAIN)
        V_out = interp(V_analogRead, [1235,19279.4116], [0.16,2.41])
        pressure = (V_out/V_supply - 0.04)/0.018
        mmHg = pressure*760/101.3

        # Check if we should write to file or not yet
        if (time.time() - self.wFreqTrigger) >= self.wFreq:
            # Reset wFreqTrigger
            self.wFreqTrigger = time.time()

            # Format string
            dataStream = ("%.02f, %.2f, %.2f\n" %((time.time()-self.startTime), pressure, mmHg) )

            # Write to file
            with open(self.owner.dataFileName, "a") as dataFile:
                dataFile.write(dataStream)
                dataFile.close()

        # Error handling in case BT communication fails (1)    
        try:
            # Start augmenting when entering the specified pressure interval
            if (mmHg >= 55) and (mmHg <= 105) and (self.playback == False):
                self.normal = False
                self.playback = True

                # Send start playback command from a separate thread
                Thread( target=startBPTachy, args=(self.rfObject,) ).start()

            # Stop augmenting when leaving the specified pressure interval
            elif ((mmHg < 55) or (mmHg > 105)) and (self.normal == False):
                self.normal = True
                self.playback = False

                # Send stop playback command from a separate thread
                Thread( target=stopBPAll, args=(self.rfObject,) ).start()
                
        # Error handling in case BT communication fails (2)        
        except Exception as instance:
            print( "" )
            print( fullStamp() + " Exception or Error Caught" )
            print( fullStamp() + " Error Type " + str(type(instance)) )
            print( fullStamp() + " Error Arguments " + str(instance.args) )
            print( fullStamp() + " Closing/Reopening Ports..." )

            # Close port then reopen
            self.rfObject.close()
            self.rfObject = createBTPort( self.deviceBTAddress, port )

            print( fullStamp() + " Successful" )

        # Return pressure readings in either case
        finally:
            return(mmHg)


# ************************************************************************
# ESTABLISH COMMUNICATION
# ************************************************************************
port = 1
deviceName = "ABPC"
deviceBTAddress = ["00:06:66:86:60:02", "00:06:66:8C:D3:F6", "00:06:66:86:77:09"] # [ Dev.I (Moe), Dev.II (Moe), Lab Demos ]
scenarioNumber = 1

# ************************************************************************
# MAKE IT ALL HAPPEN
# ************************************************************************

# Define the value of the supply voltage of the pressure sensor
V_supply = 3.3

# Initialize ADC
ADC = Adafruit_ADS1x15.ADS1115()
GAIN = 1    # Reads values in the range of +/-4.096V

if __name__ == "__main__":
    print( fullStamp() + " Booting DialGauge" )
    app = QtGui.QApplication(sys.argv)
    MyApp = MyWindow()
    MyApp.show()
    sys.exit(app.exec_())



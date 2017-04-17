'''
#
# Read pressure sensor and display readings on a dial gauge
#
# Modified by: Mohammad Odeh
# Date: March 7th, 2017
#
# Adapted from: John Harrison's original work
# Link: http://cratel.wichita.edu/cratel/python/code/SimpleVoltMeter
#
# VERSION 0.3.5
#
# CHANGELOG:
#   1- Added the ability to choose from multiple devices to pair to
#   2- If not paired, gauge will be greyed out and readings will take place
#
# KNOWN ISSUES:
#   1- Dial screen will NOT appear until communication is established (look into threading)
#
'''

# ************************************************************************
# DEBUG FLAG.
# Developmental purposes ONLY!
# ************************************************************************
debug=0


# ************************************************************************
# IMPORT MODULES
# ************************************************************************

# Python modules
import  sys, time, bluetooth, serial                        # 'nuff said
import  Adafruit_ADS1x15                                    # Required library for ADC converter
from    PyQt4               import QtCore, QtGui, Qt        # PyQt4 libraries required to render display
from    PyQt4.Qwt5          import Qwt                      # Same here, boo-boo!
from    numpy               import interp                   # Required for mapping values
from    multiprocessing     import Process, Queue           # Run functions in parallel
from    os                  import getcwd, path, makedirs   # Pathname manipulation for saving data output

# PD3D modules
from    dial                        import Ui_MainWindow        # Imports pre-built dial guage from dial.py
from    timeStamp                   import fullStamp            # Show date/time on console output
from    stethoscopeProtocol         import startBPTachy         # Tachycardia
from    stethoscopeProtocol         import startBPBrady         # Bradycardia
from    stethoscopeProtocol         import stopBPAll            # Read the function's name
from    bluetoothProtocol_teensy32  import findSmartDevice      # Scan for stethoscope of interest
from    bluetoothProtocol_teensy32  import createPort           # Open BlueTooth port


# ************************************************************************
# SETUP PROGRAM
# ************************************************************************

class MyWindow(QtGui.QMainWindow):

    pressureValue = 0
    lastPressureValue = 0
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.thread = Worker(self)

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
        for name,address in self.scan_rfObject():
            #self.ui.rfObjectSelect.addItem(name)
            self.ui.rfObjectSelect.addItem(address)

    # Connect to stethoscope
    def connectStethoscope(self, address):
        #self.thread.comport = str( deviceName )
        self.thread.deviceBTAddress = str( address )
        self.ui.CommandLabel.setText( " Successfully Paired" )
        self.ui.Dial.setEnabled(True)
        self.ui.rfObjectSelect.setEnabled(False)
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
        #BT_name, BT_address = findSmartDevice('00:06:66:86:77:09')
        BT_name, BT_address = findSmartDevice('00:06:66:7D:99:D9')
        if BT_name != 0:
            available.append( (BT_name[0], BT_address[0]) )
        # return (name, btaddress)
        return available
    
# ************************************************************************
# CLASS FOR OPTIONAL INDEPENDENT THREAD
# ************************************************************************

class Worker(QtCore.QThread):

    deviceBTAddress = 'none'

    # Create flags for what mode we are running
    normal = True
    playback = False
    
    # Check if the sampling frequency criteria is met
    wFreqTrigger = time.time()
    
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        # self.exiting = False # not sure what this line is for
        print( fullStamp() + " Initializing worker thread..." )
        self.owner = parent
        self.start()

    def __del__(self):
        print( fullStamp() + " Exiting worker thread..." )

    def run(self):
        # this method is called by self.start() in __init__()
        # Do nothing until device is selected from dropdown list
        while self.deviceBTAddress == 'none':
            time.sleep(0.1)

        # Establish communication after a device is selected
        try:
            self.rfObject = createPort( deviceName, port, self.deviceBTAddress, baudrate, attempts )
            print( fullStamp() + " Opened " + str(self.deviceBTAddress) )

            # Save initial time since script launch
            # Used to timestamp the readings
            self.startTime = time.time()
            
            while True:
                self.owner.pressureValue = self.readPressure()
                
        except:
            print( fullStamp() + " Failed to connect." )
            #self.deviceBTAddress = 'none'
            #self.owner.ui.Dial.setEnabled(False)
            #self.owner.ui.rfObjectSelect.setEnabled(True)
           
            
    def readPressure(self):

        # Perform pressure readings and convert value to mmHg
        V_analogRead = ADC.read_adc(0, gain=GAIN)
        V_out = interp(V_analogRead, [1235,19279.4116], [0.16,2.41])
        pressure = (V_out/V_supply - 0.04)/0.018
        mmHg = pressure*760/101.3

        # Check if we should write to file or not yet
        if (time.time() - self.wFreqTrigger) >= wFreq:
            # Reset wFreqTrigger
            self.wFreqTrigger = time.time()

            # Format string
            dataStream = ("%.02f, %.2f, %.2f\n" %((time.time()-self.startTime), pressure, mmHg) )

            # Write to file
            with open(dataFileName, "a") as dataFile:
                dataFile.write(dataStream)
                dataFile.close()

        # Error handling in case BT communication fails (1)    
        try:
            # Start augmenting when entering the specified pressure interval
            if (mmHg >= 60) and (mmHg <= 100) and (self.playback == False):
                self.normal = False
                self.playback = True
                if self.rfObject.isOpen == False:
                    self.rfObject.open()
                # Send start playback command as a background process
                u = Process( target=startBPTachy, args=(self.rfObject, 3,) )
                u.start()
                self.rfObject.close()

            # Stop augmenting when leaving the specified pressure interval
            elif ((mmHg < 60) or (mmHg > 100)) and (self.normal == False):
                self.normal = True
                self.playback = False
                if self.rfObject.isOpen == False:
                    self.rfObject.open()
                # Send stop playback command as a background process
                v = Process( target=stopBPAll, args=(self.rfObject, 3,) )
                v.start()
                self.rfObject.close()
                
        # Error handling in case BT communication fails (2)        
        except Exception as instance:
            print( "" )
            print( fullStamp() + " Exception or Error Caught" )
            print( fullStamp() + " Error Type " + str(type(instance)) )
            print( fullStamp() + " Error Arguments " + str(instance.args) )
            print( fullStamp() + " Closing Open Ports..." )

            if self.rfObject.isOpen == True:
                self.rfObject.close()
                print( fullStamp() + " ...Success!\n" )
                
        return(mmHg)


# ************************************************************************
# ESTABLISH COMMUNICATION
# ************************************************************************
port = 0
deviceName = "ABPC"
#deviceBTAddress = ["00:06:66:86:76:E6", "00:06:66:7D:99:D9", "00:06:66:86:77:09"] # [ Dev.I (Moe), Dev.II (Moe), Lab Demos ]
baudrate = 115200
attempts = 5
'''
try:
    rfObject = createPort(deviceName, port, deviceBTAddress[1], 115200, 5)
except:
    print( fullStamp() + " No Stethoscope detected." )
    print( fullStamp() + " Please pair stethoscope to continue..." )
'''
# ************************************************************************
# DATA STORAGE
# wFreq (units: sec) controls writing frequency of data output
# ************************************************************************
wFreq = 1 # CHANGE ME!!!
scenarioNumber = 1

# Create data output folder/file
dataFileDir = getcwd() + "/dataOutput/" + fullStamp()
dataFileName = dataFileDir + "/output.txt"
if(path.exists(dataFileDir)) == False:
    makedirs(dataFileDir)
    print( fullStamp() + " Created data output folder" )

# Write basic information to the header of the data output file
with open(dataFileName, "a") as dataFile:
    dataFile.write( "Date/Time: " + fullStamp() + "\n" )
    dataFile.write( "Scenario: #" + str(scenarioNumber) + "\n" )
    dataFile.write( "Device Name: " + deviceName + "\n" )
    dataFile.write( "Units: seconds, kPa, mmHg" + "\n" )
    dataFile.close()
    print( fullStamp() + " Created data output .txt file" )

# ************************************************************************
# MAKE IT ALL HAPPEN
# ************************************************************************

# Define the value of the supply voltage of the pressure sensor
V_supply = 3.3

# Initialize ADC
ADC = Adafruit_ADS1x15.ADS1115()
GAIN = 1    # Reads values in the range of +/-4.096V

if __name__ == "__main__":
    print( fullStamp() + " DialGauge booting..." )
    app = QtGui.QApplication(sys.argv)
    MyApp = MyWindow()
    MyApp.show()
    sys.exit(app.exec_())



'''
#
# Read pressure sensor and display readings on a dial guage
#
# Modified by: Mohammad Odeh
# Date: March 7th, 2017
#
# Adapted from: John Harrison's original work
# Link: I'll provide it later as I lost it
#
# VERSION 0.3
#
# CHANGELOG:
#   1- Improved boot up time (still needs some work)
#   2- rfcomm port is now released when clicking the EXIT button
#   3- Cleaned up code
#
# KNOWN ISSUES:
#   1- Small time lag in updating needle position when sending bluetooth commands (look into threading)
#   2- Sending multiple bytes back and forth (say 5 times in a row) crashes the program (look into try-except)
#   3- Dial screen will NOT appear until communication is established (look into threading)
#
'''

###
# DEBUG FLAG.
# Developmental purposes ONLY!
###
debug=0

import  sys, time, bluetooth                            # 'nuff said
import  Adafruit_ADS1x15                                # Required library for ADC converter
from    stethoscopeProtocol import earlyHMPlayback      # Early Systolic Heart Murmur
from    stethoscopeProtocol import stopBlending         # Read the function's name
from    bluetoothProtocol   import createPort           # Open BlueTooth port 
from    timeStamp           import fullStamp            # Show date/time on console output
from    PyQt4               import QtCore, QtGui, Qt    # PyQt4 libraries required to render display
from    PyQt4.Qwt5          import Qwt                  # Same here, boo-boo!
from    dial                import Ui_MainWindow        # Imports pre-build dial guage from dial.py
from    numpy               import interp               # Required for mapping values

# Define the value of the supply voltage of the pressure sensor
V_supply = 3.3

# Initialize ADC
ADC = Adafruit_ADS1x15.ADS1115()
GAIN = 1        # Reads values in the range of +/-4.096V

# Create BTooth port
deviceName = "SS"
deviceBTAddress = "00:06:66:86:77:09"
rfObject = createPort(deviceName, deviceBTAddress, 115200, 5, 5)

time.sleep(0.1) # Stability
 

class MyWindow(QtGui.QMainWindow):

    pressureValue = 0
    lastPressureValue = 0
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.thread = Worker(self)

        self.ui.Dial.setOrigin(90.0)
        self.ui.Dial.setScaleArc(0.0,340.0)
        self.ui.Dial.update()
        self.ui.Dial.setNeedle( Qwt.QwtDialSimpleNeedle(
                                                        Qwt.QwtDialSimpleNeedle.Arrow,
                                                        True, Qt.QColor(Qt.Qt.red),
                                                        Qt.QColor(Qt.Qt.gray).light(130)
                                                        )
                                )

        self.ui.Dial.setScaleOptions(Qwt.QwtDial.ScaleTicks | Qwt.QwtDial.ScaleLabel | Qwt.QwtDial.ScaleBackbone)
        # small ticks are length 5, medium are 15, large are 20
        self.ui.Dial.setScaleTicks(5, 15, 20)
        # large ticks show every 20, put 10 small ticks between each large tick and every 5 small ticks make a medium tick
        self.ui.Dial.setScale(10.0,10.0,20.0)
        self.ui.Dial.setRange(0.0, 300.0)
        self.ui.Dial.setValue(0)
        self.ui.Dial.setEnabled(True)

        # set timeout function for updates
        self.ctimer = QtCore.QTimer()
        self.ctimer.start(10)
        QtCore.QObject.connect(self.ctimer, QtCore.SIGNAL("timeout()"), self.UpdateDisplay)
        
       
    def UpdateDisplay(self):
        if self.pressureValue != self.lastPressureValue:
            self.ui.Dial.setValue(self.pressureValue)
            self.lastPressureValue = self.pressureValue



#************************************************************************
# CLASS FOR OPTIONAL INDEPENDENT THREAD
#************************************************************************

class Worker(QtCore.QThread):

    channel = 'none1'

    # Create flags for what mode we are running
    normal = True
    abnormal = False
    
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        # self.exiting = False # not sure what this line is for
        print( fullStamp() + " Initializing worker thread!")
        self.owner = parent
        self.start()

    def __del__(self):
        print "worker thread dieing"
    
    def run(self):
        # this method is called by self.start() in __init__()
        '''
        while self.channel == 'none':
            time.sleep(.1)
        '''
        while True:
            self.owner.pressureValue = self.readPressure()
            
            
    def readPressure(self):

        V_analogRead = ADC.read_adc(0, gain=GAIN)
        V_out = interp(V_analogRead, [1235,19279.4116], [0.16,2.41])
        pressure = (V_out/V_supply - 0.04)/0.018
        mmHg = pressure*760/101.3
        
        if debug==1:
            print("Pressure: %.2fkPa ||  %.2fmmHg" %(pressure, mmHg))
            print("AnalogRead: %i  || V_out: %.2f" %(V_analogRead, V_out))
            print("-------------------------------")
            time.sleep(0.25)
        
        if (mmHg > 70) and (self.abnormal == False):
            self.normal = False
            self.abnormal = True
            if rfObject.isOpen() == False:
                rfObject.open()
            earlyHMPlayback(rfObject, 3)
            rfObject.close()

        elif (mmHg <= 70) and (self.normal == False):
            self.normal = True
            self.abnormal = False
            if rfObject.isOpen() == False:
                rfObject.open()
            stopBlending(rfObject, 3)
            rfObject.close()
            
        return(mmHg)


#************************************************************************
# MAKE IT ALL HAPPEN
#************************************************************************

if __name__ == "__main__":
 
    app = QtGui.QApplication(sys.argv)
    MyApp = MyWindow()
    MyApp.show()
    sys.exit(app.exec_())


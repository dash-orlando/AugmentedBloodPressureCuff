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
'''

###
# DEBUG FLAG.
# Developmental purposes ONLY!
###
debug=0

import  sys, time, bluetooth                    # 'nuff said
import  Adafruit_ADS1x15                        # Required library for ADC converter
import  pressureCuffDefinitions as definitions
from    bluetoothProtocol import *
from    PyQt4       import QtCore, QtGui, Qt    # PyQt4 libraries required to render display
from    PyQt4.Qwt5  import Qwt                  # Same here, boo-boo!
from    dial        import Ui_MainWindow        # Imports pre-build dial guage from dial.py
from    numpy       import interp               # Required for mapping values

# Define the value of the supply voltage of the pressure sensor
V_supply = 3.3

# Initialize ADC
ADC = Adafruit_ADS1x15.ADS1115()
GAIN = 1 # Reads values in the range of +/-4.096V

# Create BTooth port
rfObject = createPortS("ABPC", 1, "B8:27:EB:75:5E:A5", 115200, 10)  

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
        # large ticks show every 1, put 10 small ticks between each large tick and every 5 small ticks make a medium tick
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
    
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        # self.exiting = False # not sure what this line is for
        print "Worker thread initializing!"
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
            time.sleep(.25)

        if mode == NRMOP:
            return(mmHg)
        
        elif mode==SIM_000:
            mmHg = mmHg + mmHg*0.7
            
        elif mode==SIM_001:
            mmHg = mmHg - mmHg*0.7
        
        return(mmHg)


#************************************************************************
# MAKE IT ALL HAPPEN
#************************************************************************

if __name__ == "__main__":
    # Obtain sent command, if any
    inByte = rfObject.read(size=1)
    if inByte > 0:
        if inByte == definitions.NRMOP:
            mode = NRMOP
        elif inByte == definitions.SIM_000:
            mode = SIM_000
        elif inByte == definitions.SIM_001:
            mode = SIM_001
    else:
        mode = NRMOP
        
    app = QtGui.QApplication(sys.argv)
    MyApp = MyWindow()
    MyApp.show()
    sys.exit(app.exec_())


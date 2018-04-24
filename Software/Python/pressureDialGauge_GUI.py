'''
*
* CUSTOMIZED VERSION FOR DEMO PURPOSES
*
* Read pressure sensor and display readings on a dial gauge
*
* Adapted from: John Harrison's original work
* Link: http://cratel.wichita.edu/cratel/python/code/SimpleVoltMeter
*
* VERSION: 0.5
*   - MODIFIED: This iteration of the pressureDialGauge is not intended
*               as a standalone program. It is meant to work in conjunction
*               with the appJar GUI. Attempting to run this program as a
*               standalone will throw so many errors at you you will regret it!!!
*
* KNOWN ISSUES:
*   - Nada so far.
* 
* AUTHOR                    :   Mohammad Odeh
* DATE                      :   Mar. 07th, 2017 Year of Our Lord
* LAST CONTRIBUTION DATE    :   Feb. 16th, 2018 Year of Our Lord
*
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
from    stethoscopeProtocol         import *			# import all functions from the stethoscope protocol
from    bluetoothProtocol_teensy32  import *			# import all functions from the bluetooth protocol -teensy3.2
import  stethoscopeDefinitions      as     definitions

# ************************************************************************
# CONSTRUCT ARGUMENT PARSER 
# ************************************************************************
ap = argparse.ArgumentParser()

ap.add_argument( "-f", "--frequency", type=int, default=0.25,
                help="Set sampling frequency (in secs).\nDefault=1" )
ap.add_argument( "-d", "--debug", action='store_true',
                help="Invoke flag to enable debugging" )
ap.add_argument( "--directory", type=str, default='output',
                help="Set directory" )
ap.add_argument( "--destination", type=str, default="output.txt",
                help="Set destination" )
ap.add_argument( "--stethoscope", type=str, default="00:06:66:D0:E4:94",
                help="Choose stethoscope" )
ap.add_argument( "-m", "--mode", type=str, default="REC",
                help="Mode to operate under; SIM: Simulation || REC: Recording" )

args = vars( ap.parse_args() )

# ************************************************************************
# SETUP PROGRAM
# ************************************************************************

class MyWindow(QtGui.QMainWindow):

    pressureValue = 0
    lastPressureValue = 0
    
    def __init__( self, parent=None ):

        # Initialize program and extract dial GUI
        QtGui.QWidget.__init__( self, parent )
        self.ui = Ui_MainWindow()
        self.ui.setupUi( self )
        self.thread = Worker( self )

        # Close rfObject socket on exit
        self.ui.pushButtonQuit.clicked.connect( self.cleanUp )

        # Setup gauge-needle dimensions
        self.ui.Dial.setOrigin( 90.0 )
        self.ui.Dial.setScaleArc( 0.0, 340.0 )
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
        self.ui.Dial.setScaleTicks( 5, 15, 20 )
        
        # Large ticks show every 20, put 10 small ticks between
        # each large tick and every 5 small ticks make a medium tick
        self.ui.Dial.setScale( 10.0, 10.0, 20.0 )
        self.ui.Dial.setRange( 0.0, 300.0 )
        self.ui.Dial.setValue( 0 )

        # Unpack argumnet parser parameters as attributes
        self.directory = args["directory"]
        self.destination = args["destination"]
        self.address = args["stethoscope"]
        self.mode = args["mode"]

        # Boolean to control recording function
        self.init_rec = True

        # List all available BT devices
        self.ui.Dial.setEnabled( True )
        self.ui.pushButtonPair.setEnabled( False )
        self.ui.pushButtonPair.setText(QtGui.QApplication.translate("MainWindow", "Paired", None, QtGui.QApplication.UnicodeUTF8))
        
        # set timeout function for updates
        self.ctimer = QtCore.QTimer()
        self.ctimer.start( 10 )
        QtCore.QObject.connect( self.ctimer, QtCore.SIGNAL( "timeout()" ), self.UpdateDisplay )

        # Create logfile
        self.setup_log()

# ------------------------------------------------------------------------

    def connectStethoscope( self ):
        """
        Connects to stethoscope.
        """
        self.thread.deviceBTAddress = str( self.address )
        self.ui.Dial.setEnabled( True )
        self.ui.pushButtonPair.setEnabled( False )

        # Create logfile
        self.setup_log()
        
        # set timeout function for updates
        self.ctimer = QtCore.QTimer()
        self.ctimer.start( 10 )
        QtCore.QObject.connect( self.ctimer, QtCore.SIGNAL( "timeout()" ), self.UpdateDisplay )

# ------------------------------------------------------------------------
 
    def UpdateDisplay(self):
        """
        Updates DialGauge display with the most recent pressure readings.
        """
        
        if self.pressureValue != self.lastPressureValue:
            self.ui.Dial.setValue( self.pressureValue )
            self.lastPressureValue = self.pressureValue

# ------------------------------------------------------------------------

    def scan_rfObject( self ):
        """
        Scan for available BT devices.
        Returns a list of tuples (num, name)
        """
        available = []
        BT_name, BT_address = findSmartDevice( self.address )
        if BT_name != 0:
            available.append( (BT_name[0], BT_address[0]) )
            return( available )

# ------------------------------------------------------------------------

    def setup_log( self ):
        """
        Setup directory and create logfile.
        """
        
        # Create data output folder/file
        self.dataFileDir = getcwd() + "/dataOutput/" + self.directory
        self.dataFileName = self.dataFileDir + "/" + self.destination
        if( path.exists(self.dataFileDir) ) == False:
            makedirs( self.dataFileDir )
            print( fullStamp() + " Created data output folder" )

        # Write basic information to the header of the data output file
        with open( self.dataFileName, "w" ) as f:
            f.write( "Date/Time: " + fullStamp() + "\n" )
            f.write( "Scenario: #" + str(scenarioNumber) + "\n" )
            f.write( "Device Name: " + deviceName + "\n" )
            f.write( "Stethoscope ID: " + self.address + "\n" )
            f.write( "Units: seconds, kPa, mmHg" + "\n" )
            f.close()
            print( fullStamp() + " Created data output .txt file" )

# ------------------------------------------------------------------------

    def cleanUp( self ):
        """
        Clean up at program exit.
        Stops recording and closes communication with device
        """
        
        print( fullStamp() + " Goodbye!" )
        QtCore.QThread.sleep( 2 )                               # this delay may be essential


# ************************************************************************
# CLASS FOR OPTIONAL INDEPENDENT THREAD
# ************************************************************************

class Worker( QtCore.QThread ):

    # Create flags for what mode we are running
    normal = True
    playback = False
    
    # Define sasmpling frequency (units: sec) controls writing frequency
    wFreq = args["frequency"]
    wFreqTrigger = time.time()
    
    def __init__( self, parent = None ):
        QtCore.QThread.__init__( self, parent )
        # self.exiting = False # not sure what this line is for
        print( fullStamp() + " Initializing Worker Thread" )
        self.owner = parent
        self.start()

# ------------------------------------------------------------------------

    def __del__(self):
        print( fullStamp() + " Exiting Worker Thread" )

# ------------------------------------------------------------------------

    def run(self):
        """
        This method is called by self.start() in __init__()
        """
        
        try:
            
            self.startTime = time.time()                                            # Time since the initial reading
            
            while True:
                self.owner.pressureValue = self.readPressure()                      # 

        except Exception as instance:
            print( fullStamp() + " Failed to connect" )                             # Indicate error
            print( fullStamp() + " Exception or Error Caught" )                     # ...
            print( fullStamp() + " Error Type " + str(type(instance)) )             # ...
            print( fullStamp() + " Error Arguments " + str(instance.args) )         # ...

# ------------------------------------------------------------------------

    def readPressure(self):

        # Compute pressure
        V_analog  = ADC.read_adc( 0, gain=GAIN )                                    # Convert analog readings to digital
        V_digital = interp( V_analog, [1235, 19279.4116], [0.16, 2.41] )            # Map the readings
        P_Pscl  = ( V_digital/V_supply - 0.04 )/0.018                               # Convert voltage to SI pressure readings
        P_mmHg = P_Pscl*760/101.3                                                   # Convert SI pressure to mmHg
        
        # Check if we should write to file or not yet
        if( time.time() - self.wFreqTrigger ) >= self.wFreq:
            
            self.wFreqTrigger = time.time()                                         # Reset wFreqTrigger

            #print( "SIM %r" %(self.playback) )                                      # Print to STDOUT
            
            # Write to file
            dataStream = "%.02f, %.2f, %.2f\n" %( time.time()-self.startTime,       # Format readings
                                                  P_Pscl, P_mmHg )                  # into desired form
            with open( self.owner.dataFileName, "a" ) as f:
                f.write( dataStream )                                               # Write to file
                f.close()                                                           # Close file

        if( self.owner.mode == "SIM" ): self.sim_mode( P_mmHg )                     # Trigger simulations mode (if --mode SIM)
        else: self.rec_mode()                                                       # Trigger recording   mode (if --mide REC)
        
        return( P_mmHg )                                                            # Return pressure readings in mmHg

# ------------------------------------------------------------------------

    def sim_mode( self, P ):
        """
        In charge of triggering simulations
        """
        
        # Error handling (1)
        try:
            # Entering simulation pressure interval
            if (P >= 75) and (P <= 125) and (self.playback == False):
                self.normal = False                                                 # Turn OFF normal playback
                self.playback = True                                                # Turn on simulation

            # Leaving simulation pressure interval
            elif ((P < 75) or (P > 125)) and (self.normal == False):
                self.normal = True                                                  # Turn ON normal playback
                self.playback = False                                               # Turn OFF simulation

        # Error handling (2)        
        except Exception as instance:
            print( "" )                                                             # ...
            print( fullStamp() + " Exception or Error Caught" )                     # ...
            print( fullStamp() + " Error Type " + str(type(instance)) )             # Indicate the error
            print( fullStamp() + " Error Arguments " + str(instance.args) )         # ...

# ------------------------------------------------------------------------

    def rec_mode( self ):
        """
        In charge of triggering recordings
        """
        
        if( self.owner.init_rec == True ):
            self.owner.init_rec = False
            startCustomRecording( self.rfObject, self.owner.destination )           # If all is good, start recording

        else: pass
            
            
# ************************************************************************
# ===========================> SETUP PROGRAM <===========================
# ************************************************************************
port = 1                                                                            # Port number to use in communication
deviceName = "ABPC"                                                                 # Designated device name
scenarioNumber = 1                                                                  # Device number

V_supply = 3.3                                                                      # Supply voltage to the pressure sensor

ADC = Adafruit_ADS1x15.ADS1115()                                                    # Initialize ADC
GAIN = 1                                                                            # Read values in the range of +/-4.096V

# ************************************************************************
# =========================> MAKE IT ALL HAPPEN <=========================
# ************************************************************************

def main():
    
    print( fullStamp() + " Booting DialGauge" )
    app = QtGui.QApplication(sys.argv)
    MyApp = MyWindow()
    MyApp.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    sys.exit( main() )

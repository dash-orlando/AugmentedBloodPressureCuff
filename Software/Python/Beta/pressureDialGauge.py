'''
*
* Read pressure sensor and display readings on a dial gauge
*
* Adapted from: John Harrison's original work
* Link: http://cratel.wichita.edu/cratel/python/code/SimpleVoltMeter
*
* VERSION: 0.4.5
*   - MODIFIED: Switched entire communication protocol from PySerial in favor of PyBluez
*   - MODIFIED: Modified code to go along with the 2 I2C addresses
*               fix provided by Danny
*   - ADDED   : Program now closes BT port on exit
*   - ADDED   : Change sampling frequency
*
* KNOWN ISSUES:
*   - Searching for stethoscope puts everything on hold.    (Inherent limitation of PyBluez)
*   - If no BT device is connected, pushing exit will
*     throw an error.                                       (Program still closes fine)
* 
* AUTHOR                    :   Mohammad Odeh
* DATE                      :   Mar. 07th, 2017 Year of Our Lord
* LAST CONTRIBUTION DATE    :   Nov. 11th, 2017 Year of Our Lord
*
'''

# ************************************************************************
# IMPORT MODULES
# ************************************************************************

# Python modules
import  sys, time, bluetooth, serial, argparse                  # 'nuff said
import  Adafruit_ADS1x15                                        # Required library for ADC converter
import  numpy               as      np                          # Required for LobOdeh method
from    PyQt4               import  QtCore, QtGui, Qt           # PyQt4 libraries required to render display
from    PyQt4.Qwt5          import  Qwt                         # Same here, boo-boo!
from    numpy               import  interp                      # Required for mapping values
from    threading           import  Thread                      # Run functions in "parallel"
from    os                  import  getcwd, path, makedirs      # Pathname manipulation for saving data output

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

ap.add_argument( "-f", "--frequency", type=float, default=0.05,
                help="set sampling frequency (in secs).\nDefault=1" )
ap.add_argument( "-d", "--debug", action='store_true',
                help="invoke flag to enable debugging" )
ap.add_argument( "--directory", type=str, default='output',
                help="Set directory" )

args = vars( ap.parse_args() )

# ************************************************************************
# SETUP PROGRAM
# ************************************************************************

class MyWindow( QtGui.QMainWindow ):

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

        # List all available BT devices
        address = deviceBTAddress[0]
        self.ui.pushButtonPair.setEnabled( True )
        self.ui.pushButtonPair.setText( QtGui.QApplication.translate("MainWindow", "Click to Connect", None, QtGui.QApplication.UnicodeUTF8) )
        self.ui.pushButtonPair.clicked.connect( lambda: self.connectStethoscope(address) )

# ------------------------------------------------------------------------

    def connectStethoscope( self, address ):
        """
        Connect to stethoscope.
        """
        
        self.thread.deviceBTAddress = str( address )
        self.ui.Dial.setEnabled( True )
        self.ui.pushButtonPair.setEnabled( False )

        # Create logfile
        self.setup_log()
        
        # set timeout function for updates
        self.ctimer = QtCore.QTimer()
        self.ctimer.start( 10 )
        QtCore.QObject.connect( self.ctimer, QtCore.SIGNAL( "timeout()" ), self.UpdateDisplay )

# ------------------------------------------------------------------------

    def UpdateDisplay( self ):
        """
        Update DialGauge display with the most recent pressure readings.
        """
        
        if( self.pressureValue != self.lastPressureValue ):
            self.ui.Dial.setValue( self.pressureValue )
            self.lastPressureValue = self.pressureValue

# ------------------------------------------------------------------------

    def scan_rfObject( self ):
        """
        Scan for available BT devices.
        Returns a list of tuples (num, name)
        """
        
        available = []
        BT_name, BT_address = findSmartDevice( deviceBTAddress[0] )
        if BT_name != 0:
            available.append( (BT_name[0], BT_address[0]) )
            return available

# ------------------------------------------------------------------------

    def setup_log( self ):
        """
        Setup directory and create logfile.
        """
        
        # Create data output folder/file
        self.dataFileDir = getcwd() + "/dataOutput/" + args["directory"]
        self.dataFileName = self.dataFileDir + "/output.txt"
        if( path.exists(self.dataFileDir) ) == False:
            makedirs( self.dataFileDir )
            print( fullStamp() + " Created data output folder" )

        # Write basic information to the header of the data output file
        with open( self.dataFileName, "w" ) as f:
            f.write( "Date/Time: " + fullStamp() + "\n" )
            f.write( "Scenario: #" + str(scenarioNumber) + "\n" )
            f.write( "Device Name: " + deviceName + "\n" )
            f.write( "Units: seconds, kPa, mmHg" + "\n" )
            f.close()
            print( fullStamp() + " Created data output .txt file\n" )

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

    deviceBTAddress = 'none'

    # Create flags for what mode we are running
    normal = True
    playback = False
    
    # Define sampling frequency (units: sec) controls writing frequency
    wFreq = args["frequency"]
    wFreqTrigger = time.time()
    
    def __init__( self, parent = None ):
        QtCore.QThread.__init__( self, parent )
        # self.exiting = False # not sure what this line is for
        print( fullStamp() + " Initializing Worker Thread" )

        # Lobodeh stuff
        self.m, self.last_m = 0, 0                                  # Slopes
        self.b, self.last_b = 0, 0                                  # y-intercepts
        self.t, self.last_t = 0, 0                                  # Time step (x-axis)
        self.initialRun = True                                      # Store initial values at first run
        self.filterON   = False
        self.at_marker  = True
        self.owner = parent
        self.start()
        
# ------------------------------------------------------------------------

    def __del__( self ):
        print( fullStamp() + " Exiting Worker Thread" )

# ------------------------------------------------------------------------

    def run( self ):

        while self.deviceBTAddress == 'none':                       # Do nothing until
            time.sleep( 0.01 )                                      # a device is paired

        # Establish communication after a device is selected
        try:

            #Delay for stability
            QtCore.QThread.sleep( 2 )

            # Send an enquiry byte
            self.status = True#statusEnquiry( self.rfObject )

            if( self.status == True ):
                # Update labels
                self.owner.ui.pushButtonPair.setText(QtGui.QApplication.translate("MainWindow", "Paired", None, QtGui.QApplication.UnicodeUTF8))
            
            # Save initial time since script launch
            # Used to timestamp the readings
            self.startTime = time.time()
            
            while( True ):
                self.owner.pressureValue = self.readPressure()

        except Exception as instance:
            print( fullStamp() + " Failed to connect" )
            print( fullStamp() + " Exception or Error Caught" )
            print( fullStamp() + " Error Type " + str(type(instance)) )
            print( fullStamp() + " Error Arguments " + str(instance.args) )

# ------------------------------------------------------------------------
            
    def readPressure( self ):

        # Compute pressure
        V_analog  = ADC.read_adc( 0, gain=GAIN )                                    # Convert analog readings to digital
        V_digital = interp( V_analog, [1235, 19279.4116], [0.16, 2.41] )            # Map the readings
        P_Pscl  = ( V_digital/V_supply - 0.04 )/0.018                               # Convert voltage to SI pressure readings
        P_mmHg = P_Pscl*760/101.3                                                   # Convert SI pressure to mmHg

        # Apply filter
        if( P_mmHg >= 180 and self.at_marker):
            self.filterON = True
            self.at_marker = False
            print( "[INFO] Filter ON" )

        elif( P_mmHg <= 40 and self.at_marker==False and self.filterON ):
            self.filterON = False
            self.at_marker = True
            self.initialRun = True                                                  # Store initial values at first run
            print( "[INFO] Filter OFF" )

        if( self.filterON ):
            self.t = time.time() - self.startTime
            P_mmHg = self.EMA(P_mmHg) #self.lobOdeh( P_mmHg )
        
        # Check if we should write to file or not yet
        if( time.time() - self.wFreqTrigger >= self.wFreq ):
            
            self.wFreqTrigger = time.time()                                         # Reset wFreqTrigger

            # Write to file
            dataStream = "%.02f, %.2f, %.2f\n" %( time.time()-self.startTime,       # Format readings
                                                  P_Pscl, P_mmHg )                  # into desired form

            with open( self.owner.dataFileName, "a" ) as f:
                f.write( dataStream )                                               # Write to file
                f.close()                                                           # Close file

##        self.sim_mode( P_mmHg )                                                     # Trigger simulations mode
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

                # Send start playback command from a separate thread
                Thread( target=startBlending, args=(self.rfObject, definitions.KOROT,) ).start()
                
            # Leaving simulation pressure interval
            elif ((P < 75) or (P > 125)) and (self.normal == False):
                self.normal = True                                                  # Turn ON normal playback
                self.playback = False                                               # Turn OFF simulation

                # Send stop playback command from a separate thread
                Thread( target=stopBlending, args=(self.rfObject,) ).start()
                
        # Error handling (2)        
        except Exception as instance:
            print( "" )                                                             # ...
            print( fullStamp() + " Exception or Error Caught" )                     # ...
            print( fullStamp() + " Error Type " + str(type(instance)) )             # Indicate the error
            print( fullStamp() + " Error Arguments " + str(instance.args) )         # ...

            print( fullStamp() + " Closing/Reopening Ports..." )                    # ...
            self.rfObject.close()                                                   # Reset BlueTooth
            self.rfObject = createBTPort( self.deviceBTAddress, port )              # communications
            print( fullStamp() + " Successful" )                                    # ...

# ------------------------------------------------------------------------

    def lobOdeh( self, y, ytol_min=0.01, ytol_max=2.0 ):

        
        dy      = y - self.owner.lastPressureValue                                  # Calculate slope
        dx      = self.t - self.last_t                                              # ...
        self.m  = dy/dx                                                             # ...
        
        self.b  = self.owner.lastPressureValue - self.m * self.t                    # Calculate intercept
        
        if( self.initialRun ):
            self.initialRun = False                                                 # Initial values stored, set to false
            pass
        
        else:
            y_prime = self.last_m * self.t + self.last_b                            # Calculate predicted value
            if( ytol_min <= y - y_prime and y - y_prime <= ytol_max ):
                y       = y_prime - 0.05                                            # Attenuate
                dy      = y - self.owner.lastPressureValue                          # Calculate slope
                dx      = self.t - self.last_t                                      # ...
                self.m  = dy/dx                                                     # ...

                self.b = self.owner.lastPressureValue - self.m*self.t               # Update intercept

        # Update variables
        self.last_m = self.m
        self.last_b = self.b
        self.last_t = self.t
            
        return( y )

# ------------------------------------------------------------------------

    def EMA(self, data_in, ALPHA=0.03):
        
        if( self.initialRun ):
            self.ema        = data_in
            self.initialRun = False

        else:
            self.ema        = ALPHA * data_in + (1.0-ALPHA)*self.ema

        return( self.ema )


# ************************************************************************
# ===========================> SETUP PROGRAM <===========================
# ************************************************************************
port = 1                                                                            # Port number to use in communication
deviceName = "ABPC"                                                                 # Designated device name
deviceBTAddress = ["00:06:66:D0:E4:94", "00:06:66:8C:D3:F6", "00:06:66:86:77:09"]   # [ Dev.I (Moe), Dev.II (Moe), Lab Demos ]
scenarioNumber = 1                                                                  # Device number

V_supply = 3.3                                                                      # Supply voltage to the pressure sensor

ADC = Adafruit_ADS1x15.ADS1115()                                                    # Initialize ADC
GAIN = 1                                                                            # Read values in the range of +/-4.096V


# ************************************************************************
# =========================> MAKE IT ALL HAPPEN <=========================
# ************************************************************************

if __name__ == "__main__":
    print( fullStamp() + " Booting DialGauge" )
    app = QtGui.QApplication( sys.argv )
    MyApp = MyWindow()
    MyApp.show()
    sys.exit(app.exec_())

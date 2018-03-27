'''
*
* CUSTOMIZED VERSION FOR DEMO PURPOSES
*
* GUI using appJar for Augmented Blood Pressure Cuff
*
* VERSION: 0.2.6
*   - ADDED   : GUI is now in a class format (and all is gucci)
*
* KNOWN ISSUES:
*   - Extensive testing not performed
*
* AUTHOR                    :   Mohammad Odeh
* DATE                      :   Nov. 15th, 2017 Year of Our Lord
* LAST CONTRIBUTION DATE    :   Feb. 16th, 2018 Year of Our Lord
*
'''

# Import the library
from    appJar                      import  gui                         # Import GUI
from    timeStamp                   import  fullStamp                   # Show date/time on console output
from    stethoscopeProtocol         import  *		                # import all functions from the stethoscope protocol
from    bluetoothProtocol_teensy32  import  *		                # import all functions from the bluetooth protocol -teensy3.2
import  stethoscopeDefinitions      as      definitions                 # Import definiotns [Are we even using those???]
import  sys, time, bluetooth, serial, argparse                          # 'nuff said
import  pexpect                                                         # Child process spawning and STDOUT redirection
#import  pressureDialGauge_GUI                                           # Import pressureDialGauge


class GUI(object):

    def __init__( self, logo, img, addr ):
        '''
        Create a GUI for interfacing Stethoscope and Blood Pressure Cuff.

        INPUTS:
            - logo : Absolute path to the pd3d logo as a string.
            - img  : Absolute path to the instructional image as a string.
            - addr : A list containing the mac addresses of stethoscopes.
        '''

        # Load images
        self.logo   = logo                                              # Store logo as an attribute
        self.image  = img                                               # Store image as an attribute

        # Name the windows for easier referencing
        self.win_name = { '1' : "SP ID"      ,                          # SubWindow 1
                          '2' : "Intructions",                          # SubWindow 2
                          '3' : "Launch ABPC"  }                        # SubWindow 3 (Not used)

        # Store stethoscopes in a dictionary
        self.stt_addr = dict()                                          # Create empty dictionary
        for i in range( len(addr) ):                                    # Loop over addresses 
            handle = "AS%03d" %(i+1)                                    # Construct handle
            self.stt_addr[ handle ] = addr[i]                           # Store into dictionary

        # ProceedS
        self.main()                                                     # Launch the main window

# ------------------------------------------------------------------------

    def main( self ):
        '''
        Create main window GUI for setup.
        
        INPUTS:
            - NON

        OUTPUT:
            - NON
        '''
        
        ttl_name = "main_title"                                         # Title name
        lgo_name= "main_logo"                                           # Logo name
        
        self.app = gui( "Setup" )                                       # Create GUI variable
##        self.app.setSize( "fullscreen" )                                # Launch in fullscreen
        self.app.setBg( "black" )                                       # Set GLOBAL background color
        self.app.setFont( size=20 )                                     # Set GLOBAL font size

        # Add labels
        self.app.addLabel( ttl_name, "CSEC", colspan=2 )                # Create a label
        self.app.setLabelBg( ttl_name, "gold" )                         # Set label's background color
        self.app.setLabelFg( ttl_name, "black" )                        # Set label's font color

        self.app.setPadding( [20, 20] )                                 # Pad outside the widgets

        # Add boxes
        self.app.addLabelOptionBox( "City\t\t",                         # Create a dropdown menu for city
                                   [ "FL",                              # ...
                                     "TX",                              # ...
                                     "GA",                              # Populate with cities
                                     "PA",                              # ...
                                     "CA" ],                            # ...
                                     colspan=2 )                        # Fill entire span
        self.app.setLabelFg( "City\t\t", "gold" )                       # Set the color of 'City'
        self.app.setOptionBoxState( "City\t\t", "disabled" )

        self.app.addLabelOptionBox( "Steth.\t",                         # Create a dropdown menu for stethoscopes
                                   [ "AS001"  ,                         # ...
                                     "AS002"  ,                         # Populate with stehtoscopes
                                     "AS003" ],                         # ...
                                     colspan=2  )                       # Fill entire span
        self.app.setLabelFg( "Steth.\t", "gold" )                       # Set the color of 'Stethoscope'

        self.app.addLabelOptionBox( "Mode  \t",                         # Create a dropdown menu for Modes
                                   [ "SIM",                             # Populate with modes
                                     "REC" ],                           # ...
                                     colspan=2 )                        # Fill entire span
        self.app.setLabelFg( "Mode  \t", "gold" )                       # Set the color of 'Mode'
        self.app.setOptionBoxState( "Mode  \t", "disabled" )

        # Add PD3D logo image
        self.app.addImage( lgo_name, self.logo, colspan=2 )             # Add PD3D Logo


        # Add buttons and link them to actions
        row = self.app.getRow()                                         # Get current row we are working on
        
        self.app.addNamedButton( "Submit", "Submit",                    # Link Submit to launch_win()
                                 self.launch_win, row, 0 )              # Place to the left
        
        self.app.addNamedButton( "Quit", "Quit",                        # Link Cancel to gui.stop()
                                 self.app.stop, row, 1  )               # Place to the right

        # Start GUI
        self.app.go()                                                   # Make window visible

# ------------------------------------------------------------------------

    def launch_win( self, prompt ):
        '''
        Subwindow (1) - This is where we enter the SP ID
        
        INPUTS:
            - prompt: Indicate whether the appropriate button was pressed or not

        OUTPUT:
            - NON
        '''

        # Store chosen city, stethoscope, and mode
        self.cty = self.app.getOptionBox( "City\t\t" )                  # Get City
        self.stt = self.stt_addr[self.app.getOptionBox( "Steth.\t" )]   # Get Stethoscope
        self.mde = self.app.getOptionBox( "Mode  \t" )                  # Get Mode

        # Give titles names for easier referencing
        ttl_name  = { '1' : "subWindow1_title1",                        # ...
                      '2' : "subWindow1_title2",                        # Title name
                      '3' : "subWindow1_title3" }                       # ...

        self. str_name = { '1' : "subWindow1_string1",                  # ...
                           '2' : "subWindow1_string2",                  # String name
                           '3' : "subWindow1_string3" }                 # ...
        
        message  = { '1' : "Hail to the king  ",                        # ...
                     '2' : "Hail to the one   ",                        # Message to print
                     '3' : "Kneel to the crown" }                       # ...
        
        if( prompt == "Submit" ):

            self.app.thread( self.start_bpc )                           # Start ABPC GUI in the background
            
            # Create a sub window
            self.app.startSubWindow( self.win_name['1'],                # Start subwindow
                                     modal = True )                     # [Modal] disables previous window
            self.app.setBg( "black" )                                   # Set background color
            self.app.setFont( size=20 )                                 # Set font size
            self.app.setPadding( [20, 20] )                             # Pad outside the widgets
            self.app.setSize( 472, 1048 )                               # 1888, 1048 (width, height)
            self.app.setLocation( 1416, 0 )                             

            ###
            # PROXIMITY STUFF
            ###
            self.app.addMessage( self.str_name['1'],                    # Create a message box
                                 message['1'],                          # Insert message
                                 colspan = 2 )                          # Define the span
            self.app.setMessageBg( self.str_name['1'], "white" )        # Set background
            self.app.setMessageFg( self.str_name['1'], "black" )        # Set font color
            self.app.setMessageRelief( self.str_name['1'], "ridge" )    # Set relief
            self.app.setMessageWidth( self.str_name['1'], "600" )       # Set the allowed width of the box

            self.app.addLabel( ttl_name['1'], "Proximity",              # Create a label
                               colspan = 2 )                            # Fill entire span        
            self.app.setLabelFg( ttl_name['1'], "gold" )                # Set label's font color
            self.app.setLabelRelief( ttl_name['1'], "raised" )          # Set relief to raised

            ###
            # ROTATION STUFF
            ###
            self.app.addMessage( self.str_name['2'],                    # Create a message box
                                 message['2'],                          # Insert message
                                 colspan = 2 )                          # Define the span
            self.app.setMessageBg( self.str_name['2'], "white" )        # Set background
            self.app.setMessageFg( self.str_name['2'], "black" )        # Set font color
            self.app.setMessageRelief( self.str_name['2'], "ridge" )    # Set relief
            self.app.setMessageWidth( self.str_name['2'], "600" )       # Set the allowed width of the box

            self.app.addLabel( ttl_name['2'], "Rotation",               # Create a label
                               colspan = 2 )                            # Fill entire span        
            self.app.setLabelFg( ttl_name['2'], "gold" )                # Set label's font color
            self.app.setLabelRelief( ttl_name['2'], "raised" )          # Set relief to raised

            ###
            # PRESSURE STUFF
            ###
            self.app.addMessage( self.str_name['3'],                    # Create a message box
                                 message['3'],                          # Insert message
                                 colspan = 2 )                          # Define the span
            self.app.setMessageBg( self.str_name['3'], "white" )        # Set background
            self.app.setMessageFg( self.str_name['3'], "black" )        # Set font color
            self.app.setMessageRelief( self.str_name['3'], "ridge" )    # Set relief
            self.app.setMessageWidth( self.str_name['3'], "600" )       # Set the allowed width of the box

            self.app.addLabel( ttl_name['3'], "Pressure",               # Create a label
                               colspan = 2 )                            # Fill entire span        
            self.app.setLabelFg( ttl_name['3'], "gold" )                # Set label's font color
            self.app.setLabelRelief( ttl_name['3'], "raised" )          # Set relief to raised
            
            # Add buttons and link them to actions
            row = self.app.getRow()                                     # Get current row we are working on
            self.app.addNamedButton( "Exit", "Exit",                    # Link button to ...
                                     self.app.stop )                    # ... inst_win() [SubWindow 2]

            # Start subWindow
            self.app.showSubWindow( self.win_name['1'] )                # Make subWindow visible

        else: self.app.stop()                                           # Kill program
        
# ------------------------------------------------------------------------

    def start_bpc( self ):
        '''
        Start Blood Pressure Cuff.
        
        INPUTS:
            - NON

        OUTPUT:
            - NON
        '''

        # Print diagnostic information
        print( "Using Stethoscope %s with address %s"                   # Inform user which ...
               %(self.app.getOptionBox( "Steth.\t" ), self.stt) )       # ... stethoscope is used

        # Establish connection
        port = 1                                                        # Specify port to connect through
        self.rfObject = createBTPort( self.stt, port )                  # Connect to device
        self.status   = statusEnquiry( self.rfObject )                  # Send an enquiry byte

        if( self.status != 1 ):                                         # ...
            print( "Device reported back NAK. Troublshoot device" )     # ...
            print( "Program will now exit." )                           # If the device reports back NAK
            closeBTPort( self.rfObject )                                # Kill everything
            sleep( 5.0 )                                                # ...
            self.app.stop()                                             # ...

        else:
            pass
        
        # Construct command to pass to shell
        cmd = "python pressureDialGauge_GUI.py --stethoscope %s --mode %s" %( self.stt, self.mde )

        # Start BloodPressureCuff meter
        child = pexpect.spawn(cmd, timeout=None)                        # Spawn child

        for line in child:                                              # Read STDOUT ...
            out = line.strip('\n\r')                                    # ... of spawned child ...
            print( out )                                                # ... process and print.

            out_SIM = out.split()                                       # Here is where we read pressure
            if( out_SIM[0] == "SIM" ):                                  # ABPC GUI has "pressure" printed ...
                SIM = out_SIM[1]                                        # ... before the numerical value

                # We update the value on the message box
                self.app.queueFunction( self.app.setMessage(self.str_name['3'], SIM) )
                '''
                We could also do many other things here, like
                check if we are in a specified interval.
                Or maybe send bytes to the stethoscope.
                Or God knows what we want to do.
                Your imagination is the limit (...and computing power)

                if( (mmHg >= 75 and mmHg <=100) and ( rot >= 1 and rot <= 2) and ( prox >=0.1 and prox<= 1.0 ) ):
                    startBlending( self.rfObject, definitions.ESMSYN )

                else: I would like to have Jennifer Aniston's babies
                '''
                
        child.close()                                                   # Kill child process
        closeBTPort( self.rfObject )                                    # Close BT connection
        
# ------------------------------------------------------------------------    

# Define required parameters
steth_addr = [ "00:06:66:8C:D3:F6",                                     # ...
               "00:06:66:8C:9C:2E",                                     # BT Mac address
               "00:06:66:D0:E4:94" ]                                    # ...
logo = "pd3d_inverted_with_title.gif"                                   # Logo name
img = "image.gif"                                                       # Image name

# START!
GuI = GUI( logo, img, steth_addr )

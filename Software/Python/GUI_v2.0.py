'''
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
* LAST CONTRIBUTION DATE    :   Feb. 05th, 2018 Year of Our Lord
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
import  pressureDialGauge_GUI                                           # Import pressureDialGauge


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
        self.app.setSize( "fullscreen" )                                # Launch in fullscreen
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

        self.app.addLabelOptionBox( "Steth.\t",                         # Create a dropdown menu for stethoscopes
                                   [ "AS001"  ,                         # ...
                                     "AS002"  ,                         # Populate with stehtoscopes
                                     "AS003" ],                         # ...
                                     colspan=2  )                       # Fill entire span
        self.app.setLabelFg( "Steth.\t", "gold" )                       # Set the color of 'Stethoscope'

        self.app.addLabelOptionBox( "Mode  \t",                         # Create a dropdown menu for Modes
                                   [ "REC",                             # Populate with modes
                                     "SIM" ],                           # ...
                                     colspan=2 )                        # Fill entire span
        self.app.setLabelFg( "Mode  \t", "gold" )                       # Set the color of 'Mode'

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

        # Give title & logo names for easier referencing
        ttl_name = "subWindow1_title"                                   # Title name
        lgo_name = "subWindow1_logo"                                    # Logo name
        
        if( prompt == "Submit" ):

            # Create a sub window
            self.app.startSubWindow( self.win_name['1'],                # Start subwindow
                                     modal = True )                     # [Modal] disables previous window
            self.app.setBg( "black" )                                   # Set background color
            self.app.setFont( size=20 )                                 # Set font size
            self.app.setPadding( [20, 20] )                             # Pad outside the widgets
            self.app.setSize( "fullscreen" )                            # Set geometry to fullscreen

            # Add labels
            self.app.addLabel( ttl_name, "Enter SP ID" )                # Create a label
            self.app.setLabelFg( ttl_name, "gold" )                     # Set label's font color
            self.app.setLabelRelief( ttl_name, "raised" )               # Set relief to raised


            # Add boxes
            self.app.addLabelEntry( "ID\t\t" )                          # Add an ID entry box
            self.app.setLabelFg( "ID\t\t", "gold" )                     # Set the color of 'Stethoscope'

            # Add buttons and link them to actions
            row = self.app.getRow()                                     # Get current row we are working on
            self.app.addNamedButton( "Begin", "Begin",                  # Link button to ...
                                     self.inst_win  )                   # ... inst_win() [SubWindow 2]

            # Add PD3D logo image
            self.app.addImage( lgo_name, self.logo )                    # Add PD3D Logo

            # Start subWindow
            self.app.showSubWindow( self.win_name['1'] )                # Make subWindow visible

        else: self.app.stop()                                           # Kill program

# ------------------------------------------------------------------------

    def inst_win( self, prompt ):
        '''
        Subwindow (2) - This is where we instruct heart auscultation
        
        INPUTS:
            - prompt: Indicate whether the appropriate button was pressed or not

        OUTPUT:
            - NON
        '''

        # Store SP ID
        self.usr = self.app.getEntry( "ID\t\t" )                        # Get SP ID

        # Give title, logo, and message box names for easier referencing
        ttl_name = "subWindow2_title"                                   # Title name
        lgo_name = "subWindow2_logo"                                    # Logo name
        str_name = "subWindow2_string"                                  # String name

        # Define what message to print on the instructions window
        message  = "Hello world!"                                       # Message to print
        
        self.app.hideSubWindow( self.win_name['1'] )                    # Hide previous SubWindow
        
        if( prompt == 'Begin' ):

            # Create a sub window
            self.app.startSubWindow( self.win_name['2'],                # Start subwindow
                                     modal=True )         
            self.app.setBg( "black" )                                   # Set background color
            self.app.setFont( size=20 )                                 # Set font size
            self.app.setPadding( [20, 20] )                             # Pad outside the widgets
            self.app.setSize( "fullscreen" )                            # Set geometry to fullscreen
            
            # Add labels
            self.app.addLabel( ttl_name, "Instructions",                # Create a label
                               colspan = 2 )                            # Fill entire span        
            self.app.setLabelFg( ttl_name, "gold" )                     # Set label's font color
            self.app.setLabelRelief( ttl_name, "raised" )               # Set relief to raised

            # Add image
            self.app.addImage( self.win_name['2'],                      # ...
                               self.image,                              # Add image
                               colspan = 2)                             # Fill entire span
            
            # Write down instructions
            self.app.addMessage( str_name,                              # Create a message box
                                 message,                               # Insert message
                                 colspan = 2 )                          # Define the span
            self.app.setMessageBg( str_name, "white" )                  # Set background
            self.app.setMessageFg( str_name, "black" )                  # Set font color
            self.app.setMessageRelief( str_name, "ridge" )              # Set relief
            self.app.setMessageWidth( str_name, "600" )                 # Set the allowed width of the box
            
            # Add buttons and link them to actions
            row = self.app.getRow()                                     # Get current row we are working on
            
            self.app.addNamedButton( "Start", "Start",                  # Link 'Start' to start_stt()
                                     self.start_stt, row, 0 )           # Place to the left.

            # Start subWindow
            self.app.showSubWindow( self.win_name['2'] )                # Make subWindow visible
            
        else: self.app.stop()                                           # Kill program

# ------------------------------------------------------------------------

    def start_stt( self, prompt ):
        '''
        Start stethoscope for recording.
        
        INPUTS:
            - prompt: Indicate whether the appropriate button was pressed or not

        OUTPUT:
            - NON
        '''

        # Define important variables
        port = 1                                                        # Specify port to connect through
        snd  = 'H'                                                      # 'H'eartbeat sound

        # Construct destination
        self.dst = "%s%s%s%s" %( snd,                                   # Sound
                                 self.usr,                              # SP ID
                                 self.cty,                              # City
                                 fullStamp()[2:4] )                     # Time

        # Establish connection
        self.rfObject = createBTPort( self.stt, port )                  # Connect to device
        self.status   = statusEnquiry( self.rfObject )                  # Send an enquiry byte

        # Check returned byte
        if( self.status == True ):
            if( self.mde == "REC" ):
                startCustomRecording( self.rfObject, self.dst )         # Start recording
            else: startBlending( self.rfObject, definitions.ESMSYN )    # Start simulation
##            else: startBlending( self.rfObject, definitions.EHBREC )    # Start simulation

            startTime = time.time()                                     # Start timer

        else:                                                           # Else ...
            closeBTPort( self.rfObject )                                # Close connection
            self.app.stop()                                             # Kill program

        # This is me wasting time
        while( time.time() - startTime < 10 ):                           # Ensure that user records at least this much time
##            print( time.time() - startTime )
            pass

        # Proceed
        row = self.app.getRow()-1                                       # Get current row and go up one
        self.app.addNamedButton( "Stop", "Stop",                        # Make 'Stop' visitble and link to start_bpc()
                                 self.start_bpc, row, 1  )              # Place to the right.
        
# ------------------------------------------------------------------------

    def start_bpc( self, prompt ):
        '''
        Start Blood Pressure Cuff.
        
        INPUTS:
            - prompt: Indicate whether the appropriate button was pressed or not

        OUTPUT:
            - NON
        '''

        # Define important variables
        snd = 'K'                                                       # 'K'orotkoff sound

        # Construct destination
        self.dst = "%s%s%s%s" %( snd,                                   # Sound
                                 self.usr,                              # SP ID
                                 self.cty,                              # City
                                 fullStamp()[2:4] )                     # Time

        if( prompt == "Stop" ):

            # Disconnect device
            if( self.mde == "REC" ): stopRecording( self.rfObject )     # Stop recording
            else: stopBlending( self.rfObject )                         # Stop simulation

            closeBTPort( self.rfObject )                                # Close connection

            # Print diagnostic information
            print( "Using Stethoscope %s with address %s"               # Inform user which ...
                   %(self.app.getOptionBox( "Steth.\t" ), self.stt) )   # ... stethoscope is used
            print( "Storing under: %s\n" %self.dst )                    # Inform of destination

            # Construct command to pass to shell
            cmd = "python pressureDialGauge_GUI.py --directory %s --destination %s --stethoscope %s --mode %s" %( self.cty,
                                                                                                                  self.dst,
                                                                                                                  self.stt,
                                                                                                                  self.mde )

            # Start BloodPressureCuff meter
            child = pexpect.spawn(cmd, timeout=None)                    # Spawn child

            for line in child:                                          # Read STDOUT ...
                out = line.strip('\n\r')                                # ... of spawned child ...
                print( out )                                            # ... process and print.

            child.close()                                               # Kill child process

        else: self.app.stop()                                           # Kill program

        # Cleanup and return to previous window
        self.app.destroySubWindow( self.win_name['2'] )                 # Destroy subWindow (2)
        self.app.showSubWindow( self.win_name['1'] )                    # Reopen  subWindow (1)
        
# ------------------------------------------------------------------------    

# Define required parameters
steth_addr = [ "00:06:66:8C:D3:F6",                 # ...
               "00:06:66:8C:9C:2E",                 # BT Mac address
               "00:06:66:D0:E4:94" ]                # ...
logo = "pd3d_inverted_with_title.gif"               # Logo name
img = "image.gif"                                   # Image name

# START!
GuI = GUI( logo, img, steth_addr )

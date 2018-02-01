'''
*
* GUI using appJar for Augmented Blood Pressure Cuff
*
* VERSION: 0.2.5
*   - ADDED   : GUI is now in a class format
*
* KNOWN ISSUES:
*   - Code needs tidying up
*   - Extensive testing not performed
*
* AUTHOR                    :   Mohammad Odeh
* DATE                      :   Nov. 15th, 2017 Year of Our Lord
* LAST CONTRIBUTION DATE    :   Feb. 01st, 2018 Year of Our Lord
*
'''

# Import the library
from    appJar                      import  gui                 # Import GUI
from    timeStamp                   import  fullStamp           # Show date/time on console output
from    stethoscopeProtocol         import  *		        # import all functions from the stethoscope protocol
from    bluetoothProtocol_teensy32  import  *		        # import all functions from the bluetooth protocol -teensy3.2
import  stethoscopeDefinitions      as      definitions
import  sys, time, bluetooth, serial, argparse                  # 'nuff said
import  pexpect                                                 # Child process spawning and STDOUT redirection
#import  pressureDialGauge_GUI                                   # Import pressureDialGauge


class GUI(object):

    def __init__( self, logo, img ):
        '''
        Create a GUI for interfacing Stethoscope and Blood Pressure Cuff.

        INPUTS:
            - logo : Absolute path to the pd3d logo as a string.
            - img  : Absolute path to the instructional image as a string.
        '''

        # Load images
        self.logo   = logo                                      # Store logo as an attribute
        self.image  = img                                       # Store image as an attribute

        # Name the windows for easier referencing
        self.win_name = { '1' : "SP ID"      ,                  # SubWindow 1
                          '2' : "Intructions",                  # SubWindow 2
                          '3' : "Launch ABPC"  }                # SubWindow 3 (Not used)

        # Store stethoscopes in a dictionary
        self.stt_addr = { 'AS001': "00:06:66:8C:D3:F6",         # ...
                          'AS002': "00:06:66:8C:9C:2E",         # BT Mac address
                          'AS003': "00:06:66:D0:E4:94" }        # ...

        self.main()                                             # Launch the main window

# ------------------------------------------------------------------------

    def main( self ):
        '''
        Create main window GUI for setup.
        
        INPUTS:
            - NON

        OUTPUT:
            - NON
        '''
        
        ttl_name = "main_title"                                 # Title name
        lgo_name= "main_logo"                                   # Logo name
        
        self.app = gui( "Setup" )                               # Create GUI variable
##        self.app.setSize( "fullscreen" )                        # Launch in fullscreen
        self.app.setBg( "black" )                               # Set GLOBAL background color
        self.app.setFont( size=20 )                             # Set GLOBAL font size

        # Add labels
        self.app.addLabel( ttl_name, "CSEC", colspan=2 )        # Create a label
        self.app.setLabelBg( ttl_name, "gold" )                 # Set label's background color
        self.app.setLabelFg( ttl_name, "black" )                # Set label's font color

        self.app.setPadding( [20, 20] )                         # Pad outside the widgets

        # Add boxes
        self.app.addLabelOptionBox( "City\t\t",                 # Create a dropdown menu for city
                                   [ "FL",                      # ...
                                     "TX",                      # ...
                                     "GA",                      # Populate with cities
                                     "PA",                      # ...
                                     "CA" ],                    # ...
                                     colspan=2 )                # Fill entire span
        self.app.setLabelFg( "City\t\t", "gold" )               # Set the color of 'City'

        self.app.addLabelOptionBox( "Steth.\t",                 # Create a dropdown menu for stethoscopes
                                   [ "AS001"  ,                 # ...
                                     "AS002"  ,                 # Populate with stehtoscopes
                                     "AS003" ],                 # ...
                                     colspan=2  )               # Fill entire span
        self.app.setLabelFg( "Steth.\t", "gold" )               # Set the color of 'Stethoscope'

        # Add PD3D logo image
        self.app.addImage( lgo_name, self.logo, colspan=2 )     # Add PD3D Logo


        # Add buttons and link them to actions
        row = self.app.getRow()                                 # Get current row we are working on
        
        self.app.addNamedButton( "Submit", "Submit",            # Link Submit to launch_win()
                                 self.launch_win, row, 0 )      # Place to the left
        
        self.app.addNamedButton( "Quit", "Quit",                # Link Cancel to gui.stop()
                                 self.app.stop, row, 1  )       # Place to the right

        # Start GUI
        self.app.go()                                           # Make window visible

# ------------------------------------------------------------------------

    def launch_win( self, prompt ):
        '''
        Subwindow (1) - This is where we enter the SP ID
        
        INPUTS:
            - prompt: Indicate whether the appropriate button was pressed or not

        OUTPUT:
            - NON
        '''

        ttl_name = "subWindow1_title"                           # Title name
        lgo_name = "subWindow1_logo"                            # Logo name
        
        if( prompt == "Submit" ):

            # Create a sub window
            self.app.startSubWindow( self.win_name['1'],        # Start subwindow
                                     modal = True )             # [Modal] disables previous window
            self.app.setBg( "black" )                           # Set background color
            self.app.setFont( size=20 )                         # Set font size
##            self.app.setSize( "fullscreen" )                    # Set geometry to fullscreen

            # Add labels
            self.app.addLabel( ttl_name, "Enter SP ID" )        # Create a label
            self.app.setLabelFg( ttl_name, "gold" )             # Set label's font color
            self.app.setLabelRelief( ttl_name, "raised" )       # Set relief to raised

            # Add boxes
            self.app.addLabelEntry( "ID\t\t" )                  # Add an ID entry box
            self.app.setLabelFg( "ID\t\t", "gold" )             # Set the color of 'Stethoscope'

            # Add buttons and link them to actions
            row = self.app.getRow()                             # Get current row we are working on
            self.app.addNamedButton( "Begin", "Begin",          # Link button to ...
                                     self.inst_win  )           # ... inst_win() [SubWindow 2]

            # Add PD3D logo image
            self.app.addImage( lgo_name, self.logo )            # Add PD3D Logo

            # Start subWindow
            self.app.showSubWindow( self.win_name['1'] )        # Make subWindow visible

        else: self.app.stop()                                   # Kill program

# ------------------------------------------------------------------------

    def inst_win( self, prompt ):
        '''
        Subwindow (2) - This is where we instruct heart auscultation
        
        INPUTS:
            - prompt: Indicate whether the appropriate button was pressed or not

        OUTPUT:
            - NON
        '''
        
        ttl_name = "subWindow2_title"                           # Title name
        lgo_name = "subWindow2_logo"                            # Logo name
        str_name = "subWindow2_string"                          # String name
        message  = "Hello world!"                               # Message to print
        
        self.app.hideSubWindow( self.win_name['1'] )            # Hide previous SubWindow
        
        if( prompt == 'Begin' ):

            # Create a sub window
            self.app.startSubWindow( self.win_name['2'],        # Start subwindow
                                     modal=True )         
            self.app.setBg( "black" )                           # Set background color
            self.app.setFont( size=20 )                         # Set font size
##            self.app.setSize( "fullscreen" )                    # Set geometry to fullscreen
            
            # Add labels
            self.app.addLabel( ttl_name, "Instructions",        # Create a label
                               colspan = 2 )                    # Fill entire span        
            self.app.setLabelFg( ttl_name, "gold" )             # Set label's font color
            self.app.setLabelRelief( ttl_name, "raised" )       # Set relief to raised

            # Add image
            self.app.addImage( self.win_name['2'],              # ...
                               self.image,                      # Add image
                               colspan = 2)                     # Fill entire span
            
            # Write down instructions
            self.app.addMessage( str_name,                      # Create a message box
                                 message,                       # Insert message
                                 colspan = 2 )                  # Define the span
            self.app.setMessageBg( str_name, "white" )          # Set background
            self.app.setMessageFg( str_name, "black" )          # Set font color
            self.app.setMessageRelief( str_name, "ridge" )      # Set relief
            self.app.setMessageWidth( str_name, "600" )         # Set the allowed width of the box
            
            # Add buttons and link them to actions
            row = self.app.getRow()                             # Get current row we are working on
            
            self.app.addNamedButton( "Start", "Start",          # Link 'Start' to start_stt()
                                     self.start_stt, row, 0 )   # Place to the left.
            
            self.app.addNamedButton( "Stop", "Stop",            # Link 'Stop' to start_bpc()
                                     self.start_bpc, row, 1  )  # Place to the right.

            # Start subWindow
            self.app.showSubWindow( self.win_name['2'] )        # Make subWindow visible

        else: app.stop()                                        # Kill program

# ------------------------------------------------------------------------

    def start_stt( self, prompt ):
        '''
        Start stethoscope for recording.
        
        INPUTS:
            - prompt: Indicate whether the appropriate button was pressed or not

        OUTPUT:
            - NON
        '''

        port = 1
        addr = self.stt_addr[ self.app.getOptionBox( "Steth.\t" ) ]
        print( addr )
        rfObject = createBTPort( addr, port )
        # Send an enquiry byte
        status = statusEnquiry( rfObject )
        print( status )
        time.sleep( 1.5 )
        closeBTPort( rfObject )
        
# ------------------------------------------------------------------------

    def start_bpc( self, prompt ):
        '''
        Start Blood Pressure Cuff.
        
        INPUTS:
            - prompt: Indicate whether the appropriate button was pressed or not

        OUTPUT:
            - NON
        '''
        
        if( prompt == "Stop" ):

            usr = self.app.getEntry( "ID\t\t" )                      # Store ID
            cty = self.app.getOptionBox( "City\t\t" )                # Store City
            stt = self.stt_addr[self.app.getOptionBox( "Steth.\t" )] # Store Stethoscope
##            snd = self.app.getOptionBox( "Sound.\t" )                # Store Sound type
            snd = 'H'

            dst = "%s%s%s%s" %(snd, usr, cty, fullStamp()[2:4])
            
            print( "Using Stethoscope %s with address %s"
                   %(self.app.getOptionBox( "Steth.\t" ), stt) ) 
            print( "Storing under: %s\n" %dst )
            
            cmd = "python pressureDialGauge_GUI.py --directory %s --destination %s --stethoscope %s" %( cty, dst, stt )

            child = pexpect.spawn(cmd, timeout=None)                # Spawn child

            for line in child:                                      # Read STDOUT ...
                out = line.strip('\n\r')                            # ... of spawned child ...
                print( out )                                        # ... process and print.

            child.close()                                           # Kill child process

        else: self.app.stop()                                       # Kill program

        self.app.destroySubWindow( self.win_name['2'] )             # Destroy subWindow (2)
        self.app.showSubWindow( self.win_name['1'] )                # Reopen  subWindow (1)
        
# ------------------------------------------------------------------------    

logo = "pd3d_inverted_with_title.gif"
img = "image.gif"
GuI = GUI( logo, img )

"""
#
# pressureCuffDefinitions.py
#
# List of command defenitions used in communicating (ABPC) and ControlSystem
# 
# Author: Mohammad Odeh
# Date: Mar. 20th, 2017
#
# Based on the original protocol written by Lobo, F. & Xynidis, M.
#
"""

# Definition                            Name                                            Value       Class
# ----------                            ----                                            -----       -----
SOH = chr(0x01)			#	Start of Heading				0x01	    STD
ENQ = chr(0x05)                 #       Enquiry                                         0x05        STD
EOT = chr(0x04)                 #       End of Transmission                             0x04        STD
ACK = chr(0x06)                 #       Positive Acknowledgement                        0x06        STD
NAK = chr(0x15)                 #       Negative Acknowledgement                        0x15        STD
CAN = chr(0x18)                 #       Cancel Current Command                          0x18        STD

# Device Control Commands
#   We have extended the four (4) standard "device control" commands
#   by means of a two-byte communication protocol

DC1           = chr(0x11)       #       Device Control 1: Diagnostic Functions          0x11        STD
DC1_DEBUGON   = chr(0x00)       #           Debug Mode ON			        0x00	    ORG
DC1_DEBUGOFF  = chr(0x01)	#	    Debug Mode OFF                              0x01        ORG
#                                                                                       0xFF        ORG

DC2 	= chr(0x12)         	#       Device Control 2: Operational Functions         0x12        STD
DC2_ST0 = chr(0x00)         	#           Something here			        0x00        ORG
#                                                                                       0xFF        ORG

DC3 	= chr(0x13)         	#       Device Control 3: Device-Specific Functions     0x13        STD
DC3_ST0 = chr(0x00)        	#           Something here			        0x00        ORG
DC3_ST1 = chr(0x01)         	#           Something here	        	    	0x01        ORG
DC3_ST2 = chr(0x02)       	#           Something here	    		        0x02        ORG
#                                                                                       0xFF        ORG

DC4 	= chr(0x14)             #       Device Control 4: Simulation Functions          0x14        STD
DC4_ST0 = chr(0x00)        	#           Something here				0x00        ORG
DC4_ST1 = chr(0x01)       	#           Something here				0x01        ORG
#                                                                                       0xFF        ORG

NRMOP 	= chr(0x20)		#	Normal Operation Mode  				0x20 	    ORG
SIM 	= chr(0x21)         	#       Simulation Mode             			0x21        ORG
SIM_000 = chr(0x30)     	#           Simulate Scenario 0         		0x30        ORG
SIM_001 = chr(0x31)     	#           Simulate Scenario 1         		0x31        ORG

# Legend
# STD - Standard terminology / Standard reference for command
# ORG - Original or custom-made command and reference

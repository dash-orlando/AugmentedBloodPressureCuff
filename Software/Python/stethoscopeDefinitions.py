"""
protocolDefinitions.py

The following module consists of a list of commands or definitions to be used in the communication between devices and the control system

Michael Xynidis
Fluvio L Lobo Fenoglietto
09/26/2016
"""
# Definition                            Name                                                Value           Class
# ----------                            ----                                                -----           -----
ENQ = chr(0x05)                 #       Enquiry                                             0x05            STD
ACK = chr(0x06)                 #       Positive Acknowledgement                            0x06            STD
NAK = chr(0x15)                 #       Negative Acknowledgement                            0x15            STD

# Device Control Commands
#   We have extended the four (4) standard "device control" commands by means of a two-byte communication protocol

DEVICEID = chr(0x11)        #           Device Identification
SDCHECK = chr(0x12)         #           SD Card Check                                   0x00            ORG
SENDWAV = chr(0x13)         #           Send .WAV File                                  0x00            ORG
DELVOLATILE = chr(0x14)     #           Delete Volatile Files                           0x01            ORG
STARTREC = chr(0x16)        #           Start Recording                                 0x00            ORG
STOPREC = chr(0x17)         #           Stop Recording                                  0x01            ORG
STARTPLAY = chr(0x18)       #           Start Playback                                  0x02            ORG
STOPPLAY = chr(0x19)        #           Stop Playback                                   0x03            ORG
STARTSTREAM = chr(0x1A)     #           Start Microphone Stream                         0x04            ORG
STARTTRACKING = chr(0x1B)   #           Start Tracking Microphone Stream for Peaks      0x05            ORG
STOPTRACKING = chr(0x1C)    #           Stop Tracking Microphone Stream for Peaks       0x06            ORG
NORMALHB = chr(0x1D)        #           Playback of Normal Heart Beat                   0x00            ORG
ESHMURMUR = chr(0x1E)       #           Playback of Early Systolic Heart Beat           0x01            ORG
STARTBLEND = chr(0x1F)
STOPBLEND = chr(0x20)
ESHMUR = chr(0x21)
EDHMUR = chr(0x22)
PEJECT = chr(0x23)
PSPLITP = chr(0x24)
ASYSL = chr(0x25)

# Legend
# STD - Standard terminology / Standard reference for command
# ORG - Original or custom-made command and reference

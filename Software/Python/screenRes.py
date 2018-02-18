'''
* screenRes.py
*
* Dynamically discovers the resolution of the screen on any machine.
* INTEGRATE USING PEXPECT, OTHERWISE EXPECT ISSUES
*
* VERSION: 0.1
*
* AUTHOR                    :   Edward Nichols
* DATE                      :   Feb. 17th, 2018 Year of Our Lord
*
* NOTES:
*   - Got the idea from someone on Stack Exchange.
*   - Thank you, Anon.
*
'''

from    PyQt4  import QtGui
import  sys

main = QtGui.QApplication(sys.argv)
size = main.desktop().screenGeometry()
h = size.height()
w = size.width()

print h, w

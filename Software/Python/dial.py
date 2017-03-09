'''
#
# Pressure Cuff Dial Gauge Window Setup
#
# Adapted by: Mohammad Odeh
# Date: March 7th, 2017
#
'''

from PyQt4 import QtCore, QtGui

# Get screen resolution for automatic sizing

app=QtGui.QApplication([])
screen_resolution = app.desktop().screenGeometry()
width, height = screen_resolution.width(), screen_resolution.height()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(width, height-100)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        # Setup label (display mmHg)
        self.label = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        # Setup Dial
        self.Dial = Qwt5.QwtDial(self.centralwidget)
        self.Dial.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setWeight(75)
        font.setBold(True)
        self.Dial.setFont(font)
        self.Dial.setOrientation(QtCore.Qt.Vertical)
        self.Dial.setProperty("visibleBackground", QtCore.QVariant(True))
        self.Dial.setLineWidth(4)
        self.Dial.setObjectName("Dial")
        self.verticalLayout.addWidget(self.Dial)

        # Setup Labels (CSEC, PD3D, etc...)
        self.csecLabel = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.csecLabel.sizePolicy().hasHeightForWidth())
        self.csecLabel.setSizePolicy(sizePolicy)
        self.csecLabel.setObjectName("csecLabel")
        self.verticalLayout.addWidget(self.csecLabel)
        #self.csecLabel.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.csecLabel.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setWeight(75)
        font.setBold(False)
        self.csecLabel.setFont(font)
        
        
        MainWindow.setCentralWidget(self.centralwidget)
        

        self.retranslateUi(MainWindow)


    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Sphygnomanometer", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "mmHg", None, QtGui.QApplication.UnicodeUTF8))
        self.csecLabel.setText(QtGui.QApplication.translate("MainWindow", "CSEC\nPD3D", None, QtGui.QApplication.UnicodeUTF8))
        
from PyQt4 import Qwt5


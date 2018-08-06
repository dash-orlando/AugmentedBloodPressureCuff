'''
#
# Pressure Cuff Dial Gauge Window Setup
#
# Adapted by : Mohammad Odeh
# Date       : Mar. 7th,    2017
# Updated    : Apr. 24th,   2018 --version without bluetooth device connection
#
'''

from PyQt4              import QtCore, QtGui

# Get screen resolution for automatic sizing

app=QtGui.QApplication([])
screen_resolution = app.desktop().screenGeometry()
width, height = screen_resolution.width(), screen_resolution.height()

available_resolution = app.desktop().availableGeometry()    # Minuse the taskbar
w_avlbl, h_avlbl = available_resolution.width(), available_resolution.height()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
#        MainWindow.setGeometry( 0, 0, width*3/4, h_avlbl )
        MainWindow.showFullScreen()
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
        font.setPointSize(24)
        font.setWeight(75)
        font.setBold(True)
        self.Dial.setFont(font)
        self.Dial.setOrientation(QtCore.Qt.Vertical)
        self.Dial.setProperty("visibleBackground", QtCore.QVariant(True))
        self.Dial.setLineWidth(4)
        self.Dial.setObjectName("Dial")
        self.verticalLayout.addWidget(self.Dial)

        # Setup pushbutton to quit program
        self.pushButtonQuit = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButtonQuit.sizePolicy().hasHeightForWidth())
        self.pushButtonQuit.setSizePolicy(sizePolicy)
        self.pushButtonQuit.setMaximumSize(QtCore.QSize(190, 16777215))
        self.pushButtonQuit.setObjectName("pushButtonQuit")
        self.verticalLayout.addWidget(self.pushButtonQuit)
        
        # Release ports and close window on shutdown
        self.pushButtonQuit.clicked.connect(MainWindow.close)

        # Add final touches
        self.retranslateUi(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)
        QtCore.QObject.connect(self.pushButtonQuit, QtCore.SIGNAL("triggered()"), MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Sphygnomanometer", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "mmHg", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonQuit.setText(QtGui.QApplication.translate("MainWindow", "EXIT", None, QtGui.QApplication.UnicodeUTF8))
        
from PyQt4 import Qwt5

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.

# Nachträgliche Importiere Libaries 
from PyQt6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout, 
    QGridLayout, 
    QTableWidget, 
    QTableWidgetItem, 
    QPushButton
    
)


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mainContentFrame = QtWidgets.QFrame(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainContentFrame.sizePolicy().hasHeightForWidth())
        self.mainContentFrame.setSizePolicy(sizePolicy)
        self.mainContentFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.mainContentFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.mainContentFrame.setObjectName("mainContentFrame")
        self.gridLayout = QtWidgets.QGridLayout(self.mainContentFrame)
        self.gridLayout.setObjectName("gridLayout")
        self.mainContentLabel = QtWidgets.QLabel(parent=self.mainContentFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainContentLabel.sizePolicy().hasHeightForWidth())
        self.mainContentLabel.setSizePolicy(sizePolicy)
        self.mainContentLabel.setMaximumSize(QtCore.QSize(400, 50))
        self.mainContentLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.mainContentLabel.setObjectName("mainContentLabel")
        self.gridLayout.addWidget(self.mainContentLabel, 2, 0, 1, 1)
        self.breadcrumplabel = QtWidgets.QLabel(parent=self.mainContentFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.breadcrumplabel.sizePolicy().hasHeightForWidth())
        self.breadcrumplabel.setSizePolicy(sizePolicy)
        self.breadcrumplabel.setMinimumSize(QtCore.QSize(30, 0))
        self.breadcrumplabel.setMaximumSize(QtCore.QSize(16777215, 30))
        self.breadcrumplabel.setObjectName("breadcrumplabel")
        self.gridLayout.addWidget(self.breadcrumplabel, 1, 0, 1, 1)
        self.horizontalLayout.addWidget(self.mainContentFrame)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1920, 24))
        self.menubar.setObjectName("menubar")
        self.menu_Analysen = QtWidgets.QMenu(parent=self.menubar)
        self.menu_Analysen.setObjectName("menu_Analysen")
        self.menu_Vergleich = QtWidgets.QMenu(parent=self.menubar)
        self.menu_Vergleich.setObjectName("menu_Vergleich")
        self.menu_Import = QtWidgets.QMenu(parent=self.menubar)
        self.menu_Import.setObjectName("menu_Import")
        self.menu_Export = QtWidgets.QMenu(parent=self.menubar)
        self.menu_Export.setObjectName("menu_Export")
        self.menu_Einstellungen = QtWidgets.QMenu(parent=self.menubar)
        self.menu_Einstellungen.setObjectName("menu_Einstellungen")
        self.menu_Themes = QtWidgets.QMenu(parent=self.menubar)
        self.menu_Themes.setObjectName("menu_Themes")
        self.menu_Dashboard = QtWidgets.QMenu(parent=self.menubar)
        self.menu_Dashboard.setObjectName("menu_Dashboard")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menu_Dashboard.menuAction())
        self.menubar.addAction(self.menu_Analysen.menuAction())
        self.menubar.addAction(self.menu_Vergleich.menuAction())
        self.menubar.addAction(self.menu_Import.menuAction())
        self.menubar.addAction(self.menu_Export.menuAction())
        self.menubar.addAction(self.menu_Einstellungen.menuAction())
        self.menubar.addAction(self.menu_Themes.menuAction())
        
        
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.mainContentLabel.setText(_translate("MainWindow", "Wilkommen in Meinem Abschlussprojekt"))
        self.breadcrumplabel.setText(_translate("MainWindow", "🏠 Startseite"))
        self.menu_Analysen.setTitle(_translate("MainWindow", "📊 Analysen"))
        self.menu_Vergleich.setTitle(_translate("MainWindow", "📈 Vergleich"))
        self.menu_Import.setTitle(_translate("MainWindow", "📥 Import"))
        self.menu_Export.setTitle(_translate("MainWindow", "📤 Export"))
        self.menu_Einstellungen.setTitle(_translate("MainWindow", "⚙️ Einstellungen"))
        self.menu_Themes.setTitle(_translate("MainWindow", "🎨 Themes"))
        self.menu_Dashboard.setTitle(_translate("MainWindow", "🏠 Dashboard"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())

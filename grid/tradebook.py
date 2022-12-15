
from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_tradebook(object):
    def setupUi(self, tradebook):
        tradebook.setObjectName("tradebook")
        tradebook.resize(561, 340)
        tradebook.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.centralwidget = QtWidgets.QWidget(tradebook)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(430, 280, 101, 34))
        self.pushButton.setStyleSheet("background-color: rgb(0, 0, 127);")
        self.pushButton.setObjectName("pushButton")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(230, 10, 91, 20))
        self.label.setStyleSheet("font: 11pt \"Noto Sans\";\n"
"font: 10pt \"Noto Sans\";\n"
"color: rgb(0, 0, 0);\n"
"font: 81 14pt \"Noto Sans\";")
        self.label.setObjectName("label")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(20, 60, 521, 201))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.tableWidget = QtWidgets.QTableWidget(self.gridLayoutWidget)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)
        tradebook.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(tradebook)
        self.statusbar.setObjectName("statusbar")
        tradebook.setStatusBar(self.statusbar)

        self.retranslateUi(tradebook)
        QtCore.QMetaObject.connectSlotsByName(tradebook)

    def retranslateUi(self, tradebook):
        _translate = QtCore.QCoreApplication.translate
        tradebook.setWindowTitle(_translate("tradebook", "Trade book"))
        self.pushButton.setText(_translate("tradebook", "Export to csv"))
        self.label.setText(_translate("tradebook", "Tradebook"))



from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QTimer, QTime, Qt
from time import strftime
import time,pyotp,configparser,tradebook
from api_helper import ShoonyaApiPy
from pathlib import Path
import pandas as pd

config = configparser.ConfigParser()
config.read('config.ini')

authotp = pyotp.TOTP(config.get("CRED","authenticator")).now() #copy the authenticator code here in quote.

api = ShoonyaApiPy()

buy_orders = []
loginData = 0

class Ui_myApp(object):

    def startApp(self):
        self.showTime()
        self.loginBtn.clicked.connect(self.loginApp)
        self.placeorderBtn.clicked.connect(self.placeOrder)
        self.refreshBtn.clicked.connect(self.Refresh)
        self.logsBtn.clicked.connect(self.tradeBook)
        self.posBtn.clicked.connect(self.showPositions)
        self.squreofforderBtn.clicked.connect(self.squreOff)

        self.exchangeComboBox.currentTextChanged.connect(self.getData)
        self.stockSelectionComboBox.currentTextChanged.connect(self.getData)
        self.unitslineEdit.textChanged.connect(self.getData)
        self.gridlineEdit.textChanged.connect(self.getData)
        self.gridSizelineEdit.textChanged.connect(self.getData)


        self.getData()

    def setupUi(self, myApp):
        myApp.setObjectName("myApp")
        myApp.resize(590, 376)
        myApp.setMaximumSize(QtCore.QSize(590, 376))
        myApp.setStyleSheet("background-color: White;")
        self.loginBtn = QtWidgets.QPushButton(myApp)
        self.loginBtn.setGeometry(QtCore.QRect(20, 10, 61, 34))
        self.loginBtn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.loginBtn.setStyleSheet("background-color: darkBlue;")
        self.loginBtn.setObjectName("loginBtn")
        self.logsBtn = QtWidgets.QPushButton(myApp)
        self.logsBtn.setGeometry(QtCore.QRect(510, 10, 70, 34))
        self.logsBtn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.logsBtn.setObjectName("logsBtn")
        self.logsBtn.setStyleSheet("background-color: darkBlue;")
        self.refreshBtn = QtWidgets.QPushButton(myApp)
        self.refreshBtn.setGeometry(QtCore.QRect(440, 10, 61, 34))
        self.refreshBtn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.refreshBtn.setStyleSheet("background-color: darkBlue;")
        self.refreshBtn.setObjectName("refreshBtn")
        self.exchangeComboBox = QtWidgets.QComboBox(myApp)
        self.exchangeComboBox.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.exchangeComboBox.setGeometry(QtCore.QRect(20, 60, 87, 32))
        self.exchangeComboBox.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);\n"
"selection-background-color: rgb(255, 255, 127);")
        self.exchangeComboBox.setObjectName("exchangeComboBox")
        self.exchangeComboBox.addItem("")
        self.exchangeComboBox.addItem("")
        self.stockSelectionComboBox = QtWidgets.QComboBox(myApp)
        self.stockSelectionComboBox.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.stockSelectionComboBox.setGeometry(QtCore.QRect(120, 60, 121, 32))
        self.stockSelectionComboBox.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);\n"
"selection-background-color: rgb(255, 255, 127);")

        my_list =config['Stocks']['values']
        my_list = my_list.split(',')
        self.stockSelectionComboBox.addItems(my_list)
        self.stockSelectionComboBox.setObjectName("stockSelectionComboBox")
        self.msgLbl = QtWidgets.QLabel(myApp)
        self.msgLbl.setGeometry(QtCore.QRect(110, 20, 141, 18))
        self.msgLbl.setStyleSheet("color: Red;")
        self.msgLbl.setObjectName("msgLbl")
        self.timeLbl = QtWidgets.QLabel(myApp)
        self.timeLbl.setGeometry(QtCore.QRect(350, 20, 65, 18))
        self.timeLbl.setObjectName("timeLbl")
        self.timeLbl.setStyleSheet("background-color: darkGreen; \n")
        self.unitslineEdit = QtWidgets.QLineEdit(myApp)
        self.unitslineEdit.setGeometry(QtCore.QRect(70, 120,60,25))
        self.unitslineEdit.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.unitslineEdit.setObjectName("unitslineEdit")
        self.gridlineEdit = QtWidgets.QLineEdit(myApp)
        self.gridlineEdit.setGeometry(QtCore.QRect(70, 165, 60,25))
        self.gridlineEdit.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.gridlineEdit.setObjectName("gridlineEdit")
        self.gridSizelineEdit = QtWidgets.QLineEdit(myApp)
        self.gridSizelineEdit.setGeometry(QtCore.QRect(220,120,60,25))
        self.gridSizelineEdit.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.gridSizelineEdit.setObjectName("gridSizelineEdit")
        self.gridSizeLbl = QtWidgets.QLabel(myApp)
        self.gridSizeLbl.setGeometry(QtCore.QRect(150,120,60,18))
        self.gridSizeLbl.setStyleSheet("color: Black;")
        self.gridSizeLbl.setObjectName("gridSizeLbl")
        self.unitsLbl = QtWidgets.QLabel(myApp)
        self.unitsLbl.setGeometry(QtCore.QRect(20, 120, 41, 18))
        self.unitsLbl.setStyleSheet("color: Black;")
        self.unitsLbl.setObjectName("unitsLbl")
        self.gridLbl = QtWidgets.QLabel(myApp)
        self.gridLbl.setGeometry(QtCore.QRect(20, 170, 31, 18))
        self.gridLbl.setStyleSheet("color: Black;")
        self.gridLbl.setObjectName("gridLbl")
        self.marginavblLabel = QtWidgets.QLabel(myApp)
        self.marginavblLabel.setGeometry(QtCore.QRect(280, 60, 41, 18))
        self.marginavblLabel.setStyleSheet("color: Black;")
        self.marginavblLabel.setObjectName("marginavblLabel")
        self.m2mLabel = QtWidgets.QLabel(myApp)
        self.m2mLabel.setGeometry(QtCore.QRect(280, 90, 51, 18))
        self.m2mLabel.setStyleSheet("color: Black;")
        self.m2mLabel.setObjectName("m2mLabel")
        self.marginavblLabel2 = QtWidgets.QLabel(myApp)
        self.marginavblLabel2.setGeometry(QtCore.QRect(330, 60, 65, 18))
        self.marginavblLabel2.setStyleSheet("color: Black;" "border: 1px solid black;\n" 
        "qproperty-alignment:  AlignCenter;")
        self.marginavblLabel2.setObjectName("marginavblLabel2")
        self.m2mLabel2 = QtWidgets.QLabel(myApp)
        self.m2mLabel2.setGeometry(QtCore.QRect(330, 90, 65, 18))
        self.m2mLabel2.setStyleSheet("color: Black; \n" "border: 1px solid black; \n" "qproperty-alignment:  AlignCenter;")
        self.m2mLabel2.setObjectName("m2mLabel2")
        self.placeorderBtn = QtWidgets.QPushButton(myApp)
        self.placeorderBtn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.placeorderBtn.setGeometry(QtCore.QRect(150, 160, 91, 34))
        self.placeorderBtn.setStyleSheet("background-color: darkBlue;")
        self.placeorderBtn.setObjectName("placeorderBtn")
        self.squreofforderBtn = QtWidgets.QPushButton(myApp)
        self.squreofforderBtn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.squreofforderBtn.setGeometry(QtCore.QRect(250, 160, 91, 34))
        self.squreofforderBtn.setStyleSheet("background-color: darkBlue;")
        self.squreofforderBtn.setObjectName("squreofforderBtn")
        self.posBtn = QtWidgets.QPushButton(myApp)
        self.posBtn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.posBtn.setGeometry(QtCore.QRect(350, 160, 91, 34))
        self.posBtn.setStyleSheet("background-color: darkBlue;")
        self.posBtn.setObjectName("posBtn")
        self.gridLayoutWidget = QtWidgets.QWidget(myApp)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(19, 219, 551, 141))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.tableWidget = QtWidgets.QTableWidget(self.gridLayoutWidget)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)
        timer = QTimer(myApp)
        timer.timeout.connect(self.showTime)
        timer.start(1000) # update every second

        self.loginBtn.raise_()
        self.retranslateUi(myApp)
        QtCore.QMetaObject.connectSlotsByName(myApp)

    def retranslateUi(self, myApp):
        _translate = QtCore.QCoreApplication.translate
        myApp.setWindowTitle(_translate("myApp", "GridApp"))
        self.loginBtn.setText(_translate("myApp", "Login"))
        self.logsBtn.setText(_translate("myApp", "Tradebook"))
        self.refreshBtn.setText(_translate("myApp", "Refresh"))
        self.exchangeComboBox.setItemText(0, _translate("myApp", "NSE"))
        self.exchangeComboBox.setItemText(1, _translate("myApp", "BSE"))
        self.unitsLbl.setText(_translate("myApp", "Units:"))
        self.gridLbl.setText(_translate("myApp", "Grid:"))
        self.marginavblLabel.setText(_translate("myApp", "Cash:"))
        self.m2mLabel.setText(_translate("myApp", "m2m:"))
        self.placeorderBtn.setText(_translate("myApp", "Place Orders"))
        self.squreofforderBtn.setText(_translate("myApp", "Squreoff"))
        self.gridSizeLbl.setText(_translate("myApp", "Grid Size:"))
        self.posBtn.setText(_translate("myApp", "Positions"))

    def showTime(self):
        currentTime = QTime.currentTime()
        displayTxt = currentTime.toString('hh:mm:ss')
        self.timeLbl.setText(displayTxt)
    
    def loginApp(self):
        global ret, loginData
        try:
                ret = api.login(userid = config.get("CRED","user"), password=config.get("CRED","pwd"),twoFA=authotp,vendor_code=config.get("CRED","vc"),api_secret=config.get("CRED","app_key"),imei=config.get("CRED","imei") )
                username = ret['uname']
                loginData = 1
                self.msgLbl.setText(f'Login Sucess!')
        except Exception as e:
                self.msgLbl.setText(f'Login Failed!')

    def getData(self):
        global exchange, grid, grid_size, units, token, tsym
        units = self.unitslineEdit.text()
        grid = self.gridlineEdit.text()
        grid_size = self.gridSizelineEdit.text()
        exchange = self.exchangeComboBox.currentText()
        symbol = self.stockSelectionComboBox.currentText()
        if loginData == 1:
            output = api.searchscrip(exchange=exchange,searchtext=symbol)
            token=  output['values'][0]['token']
            tsym = output['values'][0]['tsym']
    
    def Refresh (self):
        pos_data=api.get_positions()
        if pos_data == None:
            lmsg = 'No open Positions'
        else:
            mtm = 0
            pnl = 0
            for i in pos_data:
                mtm += float(i['urmtom'])
                pnl += float(i['rpnl'])
                day_m2m = mtm + pnl
                day_m2m_total = "{:.2f}".format(day_m2m)
                self.m2mLabel2.setText(str(day_m2m_total))
            #Profit m2m
          
                if day_m2m > 0:
                    self.m2mLabel2.setStyleSheet("color: Green; \n" "border: 1px solid black;")
                else:
                    self.m2mLabel2.setStyleSheet("color: Red; \n" "border: 1px solid black;")
    
        limit = api.get_limits()
        try:
            marginused = (float((limit['marginused'])))
        except KeyError:
            marginused = 0
    
        margin_available = round(((float((limit['cash']))) - marginused),2)


        self.marginavblLabel2.setText(str(margin_available))

    def placeOrder(self):

        get_ltp = api.get_quotes(exchange=exchange,token=token)
        price=float(get_ltp['lp'])
        NUM_OF_BUY = int(units) / int(grid)
        print(f'first no:{NUM_OF_BUY} {price}')

        order = api.place_order(buy_or_sell='B', product_type='I',
                        exchange=exchange, tradingsymbol=tsym, 
                        quantity=grid, discloseqty=0,price_type='LMT', price=price, trigger_price=None,
                        retention='DAY', remarks='my_order_001')
        lmsg = 'Buy order placed!'
        self.msgLbl.setText(lmsg)
        print("submitting market limit buy order at {}".format(price)) 
        buy_orders.append(order['norenordno'])
        NUM_OF_BUY = NUM_OF_BUY - 1
        for i in range (int(NUM_OF_BUY)):
                price_cal = price - (int(grid_size) * (i+1))
                print("submitting market limit buy order at {}".format(price_cal))
                order = api.place_order(buy_or_sell='B', product_type='I',
                        exchange=exchange, tradingsymbol=tsym, 
                        quantity=grid, discloseqty=0,price_type='LMT', price=price_cal, trigger_price=None,
                        retention='DAY', remarks='my_order_001')
                lmsg = 'Buy Order Place!'
                self.msgLbl.setText(lmsg)
                buy_orders.append(order['norenordno'])
    
    def squreOff(self):
        try:
            squreoff_Pos=api.get_positions()
            squreoff_Pos=pd.DataFrame(squreoff_Pos)
            row=0
            for row in squreoff_Pos.to_dict("records"):
                if int(row["netqty"])>0:
                    print(row["tsym"])
                    api.place_order(buy_or_sell='S', product_type='I', exchange=exchange, tradingsymbol=row["tsym"], quantity=int(row["netqty"]),discloseqty=0,price_type='MKT',price=0,trigger_price=None, retention='DAY',remarks='my_order_001')
                    print('there is issue here')
                    lmsg = 'Squred off the pos'
                    self.msgLbl.setText(lmsg)
        except Exception as e:
            print(e)
    
    def tradeBook(self):
        self.mytradebook = QtWidgets.QMainWindow()
        self.mytradeui = tradebook.Ui_tradebook()
        self.mytradeui.setupUi(self.mytradebook)
        self.showTradebook()
        self.mytradebook.show()

    def showTradebook(self):
        trades = 5
        if trades > 0:
            tb_header = ('Symbol', 'Buy Qty', 'Avg. Buy','Realized P&L')
            self.mytradeui.tableWidget.setColumnCount(5)
            self.mytradeui.tableWidget.setRowCount(trades)
            self.mytradeui.tableWidget.setHorizontalHeaderLabels(tb_header)
            self.mytradeui.tableWidget.setColumnWidth(0, 150)

    def hideposTable(self):
        self.tableWidget.hide()

    def showPositions(self):

        if loginData == 1:
            my_pos = api.get_positions()
            my_pos=pd.DataFrame(my_pos)
            row=0
            for row in my_pos.to_dict("records"):
                if int(row["netqty"])>0:
                    symbol=row["tsym"]
                    Avg=row["netavgprc"]
                    liveprice=row["lp"]
                    pnlpos=float(row["urmtom"])
                    netqty=float(row["netqty"])
                    exch=row["exch"]
                    po_table_header = ('Symbol', 'But Qty', 'AvgPrice', 'Ltp','PNL')
                    self.tableWidget.setColumnCount(5)
                    #self.tableWidget.setRowCount()
                    self.tableWidget.setHorizontalHeaderLabels(po_table_header)
                    self.tableWidget.setColumnWidth(0, 200)
                    self.tableWidget.setColumnWidth(1, 80)
                    self.tableWidget.setColumnWidth(2, 80)
                    self.tableWidget.setColumnWidth(3, 80)
                    self.tableWidget.setColumnWidth(4, 80)
                    
        else:
            self.hideposTable()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    myApp = QtWidgets.QWidget()
    ui = Ui_myApp()
    ui.setupUi(myApp)
    myApp.show()
    ui.startApp()
    sys.exit(app.exec())

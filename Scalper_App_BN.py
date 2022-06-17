## Scalper App to buy the option with one click with SL & Target
from cProfile import label
from time import sleep
from tkinter import *
import tkinter as tk
from tkinter import ttk
import threading,json,math,sqlite3,logging,config
from datetime import datetime, timedelta
from datetime import datetime as dt
from datetime import timedelta as td
from time import strftime
from api_helper import ShoonyaApiPy
import pandas as pd
import time


start = datetime.now()
print(start)

logfile = dt.now().strftime("%d-%m-%Y_%H%M%S")+"App.log"
print(logfile)
logging.basicConfig(level=logging.INFO, filename=logfile, filemode='w')

def log(msg, *args):
    logging.info(msg, *args)
    print(msg, *args)

#enable dbug to see request and responses
#logging.basicConfig(level=logging.DEBUG)

api = ShoonyaApiPy()


def Login(): #Login function get the api login + username and cash margin
    global ret
    ret = api.login(userid = config.user, password = config.pwd, twoFA=config.factor2, vendor_code=config.vc, api_secret=config.app_key, imei=config.imei)
    usersession=ret['susertoken']
    print(usersession)
    username = ret['uname']
    username = "WELCOME" + " " + username + "!"
    Welcome_lbl2 = Label(root, text=username, fg="white", bg="green")
    Welcome_lbl2.place(x=130, y=20)
    log(f'Login to the account {username}')

def Refresh_clicked(): # Function get the BN last price so the code can calculate the Strikes 

    global bn_nifty_lp
    global bn_lis
    bn_nifty_lp=api.get_quotes('NSE', 'Nifty Bank') 
    bn_nifty_lp=float(bn_nifty_lp['lp'])
    print(bn_nifty_lp)
    pos_data=api.get_positions()
    if pos_data == None:
        print("No Positions Data available today")
        log(f'No Positions Data available today')
    else:
        mtm = 0
        pnl = 0
        for i in pos_data:
            mtm += float(i['urmtom'])
            pnl += float(i['rpnl'])
            day_m2m = mtm + pnl
            day_m2m_total = "{:.2f}".format(day_m2m)
            m2m = Label(root, text=day_m2m_total, bg="black",font=("Arial Black",10))
            m2m.place(x=260, y=210)

            if day_m2m > 0:
                m2m.config(fg="Green")
            else:
                m2m.config(fg="Red")
    
    limit = api.get_limits()
    try:
        marginused = (float((limit['marginused'])))
    except KeyError:
        marginused = 0
    
    margin_available = round(((float((limit['cash']))) - marginused),2)
    margin_available_1lot=margin_available/25
    print("With the fund avialble you can get lot of BN with price:",margin_available_1lot)

    Label(root, text=margin_available,bg="green",fg="white").grid(row=1, padx=415, pady=20)
    # Margin Avbl Label
    Margin_Avbl_lbl1 = Label(root, text='Avbl_Margin:',bg="floral white")
    Margin_Avbl_lbl1.place(x=320, y=20)
    log(f'BN last price updated  {bn_nifty_lp}')
    log(f'The fund balance updated {margin_available}')

    
def startThread(thread): # Start the Thread (Thread Manager)
    match thread:
        case 0:
            t1=threading.Thread(target=Login)
            t1.start()
        case 1:
            t1=threading.Thread(target=trade_book)
            t1.start()
        case 2:
            t1=threading.Thread(target=placeCallOrder())
            t1.start()
        case 3:
            t1=threading.Thread(target=Refresh_clicked)
            t1.start()
        case 4:
            t1=threading.Thread(target=placePutOrder())
            t1.start()
        case 5:
            t1=threading.Thread(target=squreoff)
            t1.start()
        case 6:
            t1=threading.Thread(target=pos,daemon='true')
            t1.start()
        case 7:
            t1=threading.Thread(target=my_update)
            t1.start()
#testing the stopthread
def stopThread():
    global stopPos
    stopPos=True
# def stopThread(thread):  # Stop the Thread (Thread Manager)
#     global stopPos,stopStrat
#     match thread:
#         case 0:
#             stopPos=True
#         case 1:
#             stopStrat=True

def check_order_stat(): # Check the order details to place the SL order
    
    global order_status
    try:
        ret = api.get_order_book()
        #print(ret)
        ret=pd.DataFrame(ret)
        row=0
        for row in ret.to_dict("records"):
            if order_no==row["norenordno"]:
                order_status=row["status"]
                print("orderstatus:", order_status)
                log(f'Checking order status for order number {order_no} and order status is {order_status}')
                #print(row["status"],row["tsym"])

    # #order status to displayed in GUI
        ord_stat_entry.delete(0,"end")
        ord_stat_entry.insert(0,order_status)
    except Exception as e:
        log(f'an exception occurred :: {e}')

Symbol_Name = []
order_no=[]

def placeCallOrder():  # Place the Call option order 
    global order_no
    global stoploss_limit_ce
    global stoploss_limit_trigger_ce

    # global target_limit
    price_ltp = api.get_quotes(exchange='NFO', token=token_ce)
    price_ltp=price_ltp['bp1']
    stoploss_limit_ce=float(price_ltp)-float(sl)
    stoploss_limit_trigger_ce=float(stoploss_limit_ce) + float(1.0)
    # # Place call order
    order_no=api.place_order(buy_or_sell='B', product_type='I',
                        exchange='NFO', tradingsymbol=tsym_ce, 
                        quantity=qty, discloseqty=0,price_type='LMT', price=price_ltp, trigger_price=None,
                        retention='DAY', remarks='my_order_001')
    order_no=order_no['norenordno']
    log(f'Placed call order and order number is {order_no}')
    place_sl_order_call()
def place_sl_order_call():
    global sl_order_number
    check_order_stat()
    sleep(1)
    try:
        if order_status=='COMPLETE':
            print("Placed SELL SL order")
            sl_order_number=api.place_order(buy_or_sell='S', product_type='I',exchange='NFO', tradingsymbol=tsym_ce, quantity=qty, discloseqty=0,
                                        price_type='SL-LMT', price=stoploss_limit_ce, trigger_price=stoploss_limit_trigger_ce,retention='DAY', remarks='my_order_001')
            sl_order_number=sl_order_number['norenordno']
            log(f'Placed SL order for call position and order number is {sl_order_number}')
        elif order_status=='OPEN':
            place_sl_order_call()
            log(f'Order Still open, loop continue')
        elif order_status=='REJECTED':
            log(f'Order Rejected')
            
    except:
        print("error placing SL order")

def placePutOrder():   # Place the Put option order
    global order_no
    global stoploss_limit_pe
    global stoploss_limit_trigger_pe

    price_ltp = api.get_quotes(exchange='NFO', token=token_pe)
    price_ltp=price_ltp['bp1']
    stoploss_limit_pe=float(price_ltp)-float(sl)
    stoploss_limit_trigger_pe=float(stoploss_limit_pe) + float(1.0)
    order_no=api.place_order(buy_or_sell='B', product_type='I',
                        exchange='NFO', tradingsymbol=tsym_pe, 
                        quantity=qty, discloseqty=0,price_type='LMT', price=price_ltp, trigger_price=None,
                        retention='DAY', remarks='my_order_001')
    order_no=order_no['norenordno']
    log(f'Placed Put order and order number is {order_no}')
    place_sl_order_put()

def place_sl_order_put():
    global sl_order_number
    check_order_stat()
    sleep(1)
    try:
        if order_status=='COMPLETE':
            print("Placed SELL SL order")
            sl_order_number=api.place_order(buy_or_sell='S', product_type='I',exchange='NFO', tradingsymbol=tsym_pe, quantity=qty, discloseqty=0,
                                        price_type='SL-LMT', price=stoploss_limit_pe, trigger_price=stoploss_limit_trigger_pe,retention='DAY', remarks='my_order_001')
            sl_order_number=sl_order_number['norenordno']
            log(f'Placed SL order for put position and order number is {sl_order_number}')
        elif order_status=='OPEN':
            place_sl_order_call()
            log(f'Order Still open, loop continue')
        elif order_status=='REJECTED':
            log(f'order rejected')
    except:
        print ("error placing SL order")

def cancel_sl_order():
    try:
        cancel_sl_order=api.cancel_order(orderno=sl_order_number)
        log(f'cancelled SL order {sl_order_number}, before squre off the position')
    except Exception as e:
        log(f'an exception occurred :: {e}')

def squreoff(): # squreoff all the open order manually
    cancel_sl_order()
    log(f'squre off the open postions')
    squreoff_Pos=api.get_positions()
    squreoff_Pos=pd.DataFrame(squreoff_Pos)
    row=0
    for row in squreoff_Pos.to_dict("records"):
        if int(row["netqty"])>0:
            print(row["tsym"])
            api.place_order(buy_or_sell='S', product_type='I', exchange='NFO', tradingsymbol=row["tsym"], quantity=int(row["netqty"]),discloseqty=0,price_type='MKT',price=0,trigger_price=None, retention='DAY',remarks='my_order_001')

stopPos=False
def pos(): # Display the Position Details
    global profitLabel
    global netqty
    try:
        netqty =0 
        while True:
            orders=api.get_positions()
            orders=pd.DataFrame(orders)
            row=0
            for row in orders.to_dict("records"):
                if int(row["netqty"])>0:
                    symbol=row["tsym"]
                    Avg=row["netavgprc"]
                    liveprice=row["lp"]
                    pnlpos=float(row["urmtom"])
                    netqty=float(row["netqty"])

                Label(root,text='Symbol',width=23,bg="cornsilk3",fg="black",font=("Arial Black",10)).place(x=40,y=250)       
                Label(root,text='Avg',width=8,bg="cornsilk3",fg="black",font=("Arial Black",10)).place(x=235,y=250)
                Label(root,text='LTP',width=10,bg="cornsilk3",fg="black",font=("Arial Black",10)).place(x=310,y=250)
                Label(root,text='QTY',width=10,bg="cornsilk3",fg="black",font=("Arial Black",10)).place(x=400,y=250)
                Label(root,text='Pnl',width=10,bg="cornsilk3",fg="black",font=("Arial Black",10)).place(x=490,y=250)
            if netqty != 0:
                pos_symbol=Label(root,text=symbol,width=23,bg="cornsilk3",fg="black",font=("Arial Black",10))
                pos_symbol.place(x=40,y=280) 
                pos_Avg=Label(root,text=Avg,width=8,bg="cornsilk3",fg="black",font=("Arial Black",10))
                pos_Avg.place(x=235,y=280)
                pos_ltp=Label(root,text=liveprice,width=10,bg="cornsilk3",fg="black",font=("Arial Black",10))
                pos_ltp.place(x=310,y=280)
                pos_netqty=Label(root,text=netqty,width=10,bg="cornsilk3",fg="black",font=("Arial Black",10))
                pos_netqty.place(x=400,y=280)
                profitLabel=Label(root, text=pnlpos, width=10,fg="black",font=("Arial Black",10))
                profitLabel.place(x=490, y=280)
                if pnlpos > 0:
                    profitLabel.config(bg="Green")
                else:
                    profitLabel.config(bg="Red")
            elif netqty == 0:
                print("the loop broken since no open Pos")
                log(f'No Open Position since the loop broken')
                global stopPos
                if(stopPos==True):
                    stopPos=False
                    break
                break
                
             
                   
    except Exception as e:
        log(f'an exception occurred :: {e}')
#orderData funtion to collect sl,tager,qty data

def orderData(*args): # Get the orderData like SL,Target,QTY
    global sl
    #global target
    global qty

    try:
        sl=float(stoploss.get())
        #qty=qtycalldata.get()
        log(f'collected the SL: {sl}, QTY:{qty}')
    except Exception as e:
        log(f'an exception occurred :: {e}')
    
    try: 
        qty_value=qty_combo_box1.get()
        qty_to_lot={"1": 25, "2": 50, "3": 75, "4": 100, "5": 125}

        if qty_value == "1":
            qty=qty_to_lot.get('1')
        elif qty_value == "2":
            qty=qty_to_lot.get('2')
        elif qty_value == "3":
            qty=qty_to_lot.get('3')
        elif qty_value == "4":
            qty=qty_to_lot.get('4')
        elif qty_value == "5":
            qty=qty_to_lot.get('5')
        
    except Exception as e:
        log(f'an exception occurred :: {e}')

    try:
        maxloss = sl * qty
        maxloss_lbl1 = Label(root, text='Max Loss',font=("Helvatical bold",11))
        maxloss_lbl1.place(x=250, y=120)
        maxloss_lbl2 = Label(root, text=maxloss,font=("Helvatical bold",11))
        maxloss_lbl2.place(x=325, y=120)
        
    except Exception as e:
        log(f'an exception occurred :: {e}')


    
bn_nifty_lp=[]

def my_expiry_update(*args): # Get the expiry date from Combobox
    global Expiry_day
    try:
        Expiry_day=Expiry_day_combo_box1.get()
        log(f'Expiry day selected {Expiry_day}')
    except Exception as e:
        log(f'an exception occurred :: {e}')

def my_update(*args): # Get the token details according to the Comobox selection & update the call & pur strike
    global tsym_ce
    global tsym_pe
    global token_ce
    global token_pe

    try:
        Strike_selection=Strike_combo_box1.get()    
        round_number = math.fmod(bn_nifty_lp, 100) # round the strike
        atm = bn_nifty_lp - round_number
        itm = atm - 100
        itm1= atm - 200
        otm = atm + 100
        otm1 = atm + 200
        in_the_money1 = 'itm1'
        in_the_money = 'itm'
        at_the_money = 'atm'
        out_of_the_money = 'otm'
        out_of_the_money1 = 'otm1'
        bn_list={"itm1": itm1, "itm": itm, "atm": atm, "otm": otm, "otm1": otm1}
        in_the_money1 = 'itm1'
        in_the_money = 'itm'
        at_the_money = 'atm'
        out_of_the_money = 'otm'
        out_of_the_money1 = 'otm1'
        combo_value = Strike_selection

        if combo_value == "ATM":
            strike_price_Ce=bn_list.get(at_the_money)
            strike_price_Pe=bn_list.get(at_the_money)
        elif combo_value == "ITM":
            strike_price_Ce=bn_list.get(in_the_money)
            strike_price_Pe=bn_list.get(out_of_the_money)
        elif combo_value == "ITM1":
            strike_price_Ce=bn_list.get(in_the_money1)
            strike_price_Pe=bn_list.get(out_of_the_money1)
        elif combo_value == "OTM":
            strike_price_Ce=bn_list.get(out_of_the_money)
            strike_price_Pe=bn_list.get(in_the_money)
        elif combo_value == "OTM2":
            strike_price_Ce=bn_list.get(out_of_the_money1)
            strike_price_Pe=bn_list.get(in_the_money1)
    
        log(f'call option strike:{strike_price_Ce}, put option strike:{strike_price_Pe}')

        call_strike.delete(0,"end")
        call_strike.insert(0,strike_price_Ce)
        put_strike.delete(0,"end")
        put_strike.insert(0,strike_price_Pe)

# write the logic here to get the token 
        Symbol_strike = strike_price_Ce
        Symbol_index = index
        Symbol_Expiry_day = Expiry_day
        ScripName_CE=f'{Symbol_index} {Symbol_Expiry_day} {Symbol_strike}'+" "+'CE'
        res_ce = api.searchscrip('NFO',searchtext=ScripName_CE)
        tsym_ce=res_ce['values'][0]['tsym']
        token_ce=res_ce['values'][0]['token']
        Symbol_strike = strike_price_Pe
        Symbol_index = index
        Symbol_Expiry_day = Expiry_day
        ScripName_PE=f'{Symbol_index} {Symbol_Expiry_day} {Symbol_strike}'+" "+'PE'
        res_pe = api.searchscrip('NFO',searchtext=ScripName_PE)
        tsym_pe=res_pe['values'][0]['tsym']
        token_pe=res_pe['values'][0]['token']
        update_ltp()
    except Exception as e:
        log(f'an exception occurred :: {e}')
    
def trade_book(): # Display the Help child window
   
    try:
        top= Toplevel(root)
        top.geometry("750x250")
        top.title("Trade book")
        
        Label(root, text='Work in Progress',font=("Helvatical bold",15))
        trade_b = api.get_trade_book()
        trade_b=pd.DataFrame(trade_b)
        

    except Exception as e:
        log(f'an exception occurred :: {e}')


def update_ltp(): # Update the strike price in tkinter window
    try:

        call_strike_ltp=api.get_quotes(exchange='NFO', token=token_ce)
        call_strike_ltp=call_strike_ltp['lp']
        display_call_ltp=Label(root,text=call_strike_ltp,width=5)
        display_call_ltp.place(x=500,y=120)
        put_strike_ltp=api.get_quotes(exchange='NFO', token=token_pe)
        put_strike_ltp=put_strike_ltp['lp']
        display_put_ltp=Label(root,text=put_strike_ltp,width=5)
        display_put_ltp.place(x=560,y=120)
        log(f'call ltp:{tsym_ce}  {call_strike_ltp} and put ltp: {tsym_pe} {put_strike_ltp}')
    except Exception as e:
        log(f'an exception occurred :: {e}')

root=Tk()
root.geometry("650x350")
root.config(background="#ffffe6")
root.title('Richdotcom Scalper App')
style= ttk.Style()
style.theme_use('clam')
root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file='richdotcom.png'))

def time():
    string = strftime('%H:%M:%S %p')
    lbl.config(text = string)
    lbl.after(1000, time)
  
# Styling the label widget so that clock
# will look more attractive
lbl = Label(root, font = ('Arial Black', 10, 'bold'),
            background = 'green',
            foreground = 'white')
lbl.place(x=530,y=310)
time()

# Login button
Login_btn1 = Button(root, text='Login',fg="white",bg="black",command=lambda:startThread(0))
Login_btn1.place(x=40, y=10)
#Refresh button
Refresh_btn1 = Button(root, text='Refresh',width=4,fg="white",bg="black",command=lambda:startThread(3))
Refresh_btn1.place(x=490, y=10)
#Help Button
tb_btn1 = Button(root, text='Orders',width=4,fg="white",bg="black",command=lambda:startThread(1))
tb_btn1.place(x=570, y=10)
# CE BUY button
CE_BUY_Btn1 = Button(root, text='BUY',width=3,fg="white",bg="black",command=lambda:startThread(2))
CE_BUY_Btn1.place(x=500, y=150)
# PE BUY button
PE_BUY_Btn1 = Button(root, text='BUY',width=3,fg="white",bg="black",command=lambda:startThread(4))
PE_BUY_Btn1.place(x=560, y=150)
#SL text & entry box
stoploss=IntVar()
sl_text = Label(root, text='SL:',font=("Helvatical bold",11))
sl_text.place(x=250, y=80)
loss=Entry(root, width=5,textvariable=stoploss)
loss.place(x=320, y=80)
stoploss.trace("w", orderData)
#Target text $ entry box
# targetdata=tk.IntVar()
# target_text = Label(root, text='Target:',font=("Helvatical bold",11))
# target_text.place(x=250, y=110)
# target_entry=Entry(root,width=5,textvariable=targetdata)
# target_entry.place(x=320, y=110)
# targetdata.trace("w", orderData)
## qty side
# qtycalldata=tk.IntVar()
# qty_call_entry=tk.Entry(root,width=3,textvariable=qtycalldata)
# qty_call_entry.place(x=440, y=150)
# qtycalldata.trace("w", orderData)
# Symbol Label
Symbol_lbl1 = Label(root, text='Symbol:',font=("Helvatical bold",11))
Symbol_lbl1.place(x=40, y=60)
# Expiry day Label
Expiry_date_lbl1 = Label(root, text='Expiry:',font=("Helvatical bold",11))
Expiry_date_lbl1.place(x=40, y=110)
# Strike Label
Strike_lbl1 = Label(root, text='Strike:',font=("Helvatical bold",11))
Strike_lbl1.place(x=40, y=160)
###
ord_stat = Label(root, text='Order Stat:',font=("Helvatical bold",11))
ord_stat.place(x=40, y=310)
ord_stat_entry=Entry(root,width=10)
ord_stat_entry.place(x=130,y=310)
# Positions button
Positions_btn = Button(root, text='Positions',width=5,font=("Helvatical bold",11),bg="black",fg="white",command=lambda:startThread(6))
Positions_btn.place(x=40, y=200)
#Profit m2m
m2m_lbl1 = Label(root, text='m2m:',font=("Helvatical bold",11))
m2m_lbl1.place(x=200, y=210)
#squreoff button 
squreoff_Btn1 = Button(root, text='SqureOff',width=5,fg="white",bg="black",command=lambda:startThread(5))
squreoff_Btn1.place(x=120, y=200)
# CALL Label
CALL_lbl1 = Label(root, text='CALL',font=("Helvatical bold",11))
CALL_lbl1.place(x=500, y=60)
call_strike=Entry(root,width=5)
call_strike.place(x=500,y=90)
# PUT Label
PUT_lbl1 = Label(root, text='PUT',font=("Helvatical bold",11))
PUT_lbl1.place(x=560, y=60)
put_strike=Entry(root,width=5)
put_strike.place(x=560,y=90)
# Strike Price Label
Strike_price_lbl1 = Label(root, text='Strike:',font=("Helvatical bold",11))
Strike_price_lbl1.place(x=400, y=90)
# Strike Label
price_lable = Label(root, text='Price:',font=("Helvatical bold",11))
price_lable.place(x=400, y=120)
# QTY Label
QTY_lbl1 = Label(root, text='Lot:',font=("Helvatical bold",11))
QTY_lbl1.place(x=400, y=150)

# Combobox 0
Symbol_combo_box1 = ttk.Combobox(root,width=10)
Symbol_combo_box1['values'] = ("BANKNIFTY")
Symbol_combo_box1.place(x=120, y=60)
Symbol_combo_box1.current(0)
index=Symbol_combo_box1.get()
#Combobox 1
Expiry_day_combo=tk.StringVar() # string variable 
Expiry_day_combo_box1 =ttk.Combobox(root, values=["Select Expiry","23 JUN22","30 JUN22","JUN","7 JUL22"],width=10,textvariable=Expiry_day_combo)
Expiry_day_combo_box1.place(x=120, y=110)
Expiry_day_combo_box1.current(0)
Expiry_day_combo.trace('w',my_expiry_update)
# Combobox 2
BN_Combo_values=["ITM1","ITM","ATM","OTM","OTM2"]
Strike_combo=tk.StringVar()
Strike_combo_box1 = ttk.Combobox(root, values=BN_Combo_values,width=10,textvariable=Strike_combo)
Strike_combo_box1.place(x=120, y=160)
Strike_combo_box1.current(2)
Strike_combo.trace('w',my_update)
# Combobox 3
qty_combo_value=["1","2","3","4","5"]
qty_combo=tk.StringVar()
qty_combo_box1 = ttk.Combobox(root, values=qty_combo_value,width=3,textvariable=qty_combo)
qty_combo_box1.place(x=440, y=150)
qty_combo_box1.current(0)
qty_combo.trace('w',orderData)

root.mainloop()


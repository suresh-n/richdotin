from time import sleep
from tkinter import *
import tkinter as tk
from tkinter import ttk
import threading,json,math,sqlite3,logging,config
from numpy import empty
from datetime import datetime, timedelta
from datetime import datetime as dt
from datetime import timedelta as td
from time import strftime
from api_helper import ShoonyaApiPy
import pandas as pd
import time
#from threading import Timer

import configparser
from pathlib import Path
config = configparser.ConfigParser()
config.read('config.ini')


start = datetime.now()
print(start)

logfile = dt.now().strftime("%d-%m-%Y_%H%M%S")+"App.log"
print(logfile)
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.INFO, 
                    filename=logfile, 
                    filemode='w',
                    datefmt='%Y-%m-%d %H:%M:%S')

def log(msg, *args):
    logging.info(msg, *args)
    #print(msg, *args)
def errorlog(msg1,*args):
    logging.error(msg1, *args)
    #print(msg1,*args)

#enable dbug to see request and responses
#logging.basicConfig(level=logging.DEBUG)

api = ShoonyaApiPy()

##Style 

lbl_fonts=("Helvatical bold",10)
btn_fonts=("Helvatical bold",10)
btn_fg="white"
btn_bg="black"
lbl_fg='white'
lbl_bg='#ffffe6'
m2m_fonts=("Helvatical bold",11)
time_font=('Helvatical bold', 10, 'bold')
time_bg='green'
time_fg='white'
top_lbl_fg="black"
top_lbl_bg='#ffffe6'
top_lbl_font=("Helvatical bold",11)
def write_test():
        get_user=get_username.get()
        get_password=get_pwd.get()
        get_factor2_1=get_factor2.get()
        get_vc_1=get_vc.get()
        get_apikey_1=get_apikey.get()
        config.set("CRED", "user", get_user )
        config.set("CRED", "pwd", get_password)
        config.set("CRED", "factor2",get_factor2_1)
        config.set("CRED", "vc",get_vc_1)
        config.set("CRED", "app_key",get_apikey_1)
        with open('test.ini', 'w') as configfile:
            config.write(configfile)
            log(f'The test.ini file filled with the Credential details')
        top.destroy()
        
def Login(): #Login function get the api login + username and cash margin

    global ret
    global get_username,get_pwd,get_factor2,get_vc,get_apikey
    global top
    if not config.get("CRED","user"):
        log("CRED Variable is empty so getting variable")

        top= Toplevel(root)
        top.geometry("300x280")
        top.title("Richdotin Scalping App")
        top.config(background="#ffffe6")
        lbl_username=Label(top,text="User:",fg=top_lbl_fg,font=top_lbl_font, bg=top_lbl_bg)
        lbl_username.place(x=30,y=20)
        lbl_password=Label(top,text="Password:",fg=top_lbl_fg,font=top_lbl_font, bg=top_lbl_bg)
        lbl_password.place(x=30,y=60)
        lbl_factor2=Label(top,text="Factor2:",fg=top_lbl_fg,font=top_lbl_font, bg=top_lbl_bg)
        lbl_factor2.place(x=30,y=100)
        lbl_vc=Label(top,text="VC:",fg=top_lbl_fg,font=top_lbl_font, bg=top_lbl_bg)
        lbl_vc.place(x=30,y=140)
        lbl_api_key=Label(top,text="api_key:",fg=top_lbl_fg,font=top_lbl_font, bg=top_lbl_bg)
        lbl_api_key.place(x=30,y=180)
        get_username=Entry(top,width=15,borderwidth=0)
        get_username.place(x=120,y=20)
        get_pwd=Entry(top,width=15,show="*",borderwidth=0)
        get_pwd.place(x=120,y=60)
        get_factor2=Entry(top,width=15,borderwidth=0)
        get_factor2.place(x=120,y=100)
        get_vc=Entry(top,width=15,borderwidth=0)
        get_vc.place(x=120,y=140)
        get_apikey=Entry(top,width=20,show="*",borderwidth=0)
        get_apikey.place(x=120,y=180)

        submit_btn1 = Button(top, 
                    text='Submit',
                    font=btn_fonts,
                    fg=btn_fg,
                    bg=btn_bg,
                    bd=0,
                    activeforeground="Green",
                    command=write_test
                    )
        submit_btn1.place(x=130, 
                 y=220)

    else:

        try:
            #ret = api.login(userid = config.user, password = config.pwd, twoFA=config.factor2, vendor_code=config.vc, api_secret=config.app_key, imei=config.imei)
            ret = api.login(userid = config.get("CRED","user"), password=config.get("CRED","pwd"),twoFA=config.get("CRED","factor2"),vendor_code=config.get("CRED","vc"),api_secret=config.get("CRED","app_key"),imei=config.get("CRED","imei") )
            usersession=ret['susertoken']
            username = ret['uname']
            username = "Welcome" + " " + username + "!"
            Welcome_lbl2 = Label(root, text=username, fg=lbl_fg,font=lbl_fonts, bg="Green")
            Welcome_lbl2.place(x=130, y=20)
            log(f'Sucessfully Login to the account {username}')
        except Exception as e:
            errorlog(f'an exception occurred :: {e}')

def Refresh_clicked(): # Function get the BN last price so the code can calculate the Strikes 
    pos_data=api.get_positions()
    if pos_data == None:
        log(f'No Positions Data available for today')
    else:
        mtm = 0
        pnl = 0
        for i in pos_data:
            mtm += float(i['urmtom'])
            pnl += float(i['rpnl'])
            day_m2m = mtm + pnl
            day_m2m_total = "{:.2f}".format(day_m2m)
            m2m = Label(root, text=day_m2m_total,bg=lbl_fg,font=lbl_fonts,width=10)
            m2m.place(x=280, y=210)

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
    print("With the avialble fund you can get one lot of BN with price:",margin_available_1lot)

    Label(root, text=margin_available,bg="green",fg="white").grid(row=1, padx=415, pady=20)
    # Margin Avbl Label
    Margin_Avbl_lbl1 = Label(root, text='Avbl_Margin:',font=lbl_fonts,bg=lbl_bg)
    Margin_Avbl_lbl1.place(x=320, y=20)
    log(f'BN last price updated  {bn_nifty_lp}')
    log(f'The fund balance updated {margin_available}')
    #sh=Timer(30,Refresh_clicked)
    #sh.start()
   
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
        # case 7:
        #     t1=threading.Thread(target=my_update)
        #     t1.start()
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
                log(f'[OrderStatus]Checking order status for order number {order_no} and the order status is {order_status}')
                #print(row["status"],row["tsym"])

    # #order status to displayed in GUI
        ord_stat_entry.delete(0,"end")
        ord_stat_entry.insert(0,order_status)
    except Exception as e:
        errorlog(f'an exception occurred :: {e}')

Symbol_Name = []
order_no=[]

def placeCallOrder():  # Place the Call option order 
    global order_no
    global stoploss_limit_ce
    global stoploss_limit_trigger_ce
    try:
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
        log(f'[OrderPlaced] Placed call { tsym_ce } order at {price_ltp} x Quantity  {qty} and order number is {order_no}')
        place_sl_order_call()
    except Exception as e:
        errorlog(f'an exception occurred :: {e}')

def place_sl_order_call():
    global sl_order_number
    check_order_stat()
    try:
        if order_status=='COMPLETE':
            print("Placed SELL SL order")
            sl_order_number=api.place_order(buy_or_sell='S', product_type='I',exchange='NFO', tradingsymbol=tsym_ce, quantity=qty, discloseqty=0,
                                        price_type='SL-LMT', price=stoploss_limit_ce, trigger_price=stoploss_limit_trigger_ce,retention='DAY', remarks='my_order_001')
            sl_order_number=sl_order_number['norenordno']
            log(f'[SLOrderPlaced] Placed SL order for call position and order number is {sl_order_number}')
        elif order_status=='OPEN':
            ret = api.cancel_order(orderno=order_no)
            check_order_stat()
            log(f'[OrderCancelled] Order Still open, since cancelled {order_no} to avoid the loop.Place the order again')
            pass
        elif order_status=='REJECTED':
            log(f'[OrderRejected] Order Rejected')
            
    except Exception as e:
        errorlog(f'an exception occurred :: {e}')

def placePutOrder():   # Place the Put option order
    global order_no
    global stoploss_limit_pe
    global stoploss_limit_trigger_pe
    try:

        price_ltp = api.get_quotes(exchange='NFO', token=token_pe)
        price_ltp=price_ltp['bp1']
        stoploss_limit_pe=float(price_ltp)-float(sl)
        stoploss_limit_trigger_pe=float(stoploss_limit_pe) + float(1.0)
        order_no=api.place_order(buy_or_sell='B', product_type='I',
                        exchange='NFO', tradingsymbol=tsym_pe, 
                        quantity=qty, discloseqty=0,price_type='LMT', price=price_ltp, trigger_price=None,
                        retention='DAY', remarks='my_order_001')
        order_no=order_no['norenordno']
        log(f'[OrderPlaced] Placed Put { tsym_pe } order at {price_ltp} x Quantity  {qty} and order number is {order_no}')
        place_sl_order_put()
    except Exception as e:
        errorlog(f'an exception occurred :: {e}')

def place_sl_order_put():
    global sl_order_number
    check_order_stat()
    try:
        if order_status=='COMPLETE':
            print("Placed SELL SL order")
            sl_order_number=api.place_order(buy_or_sell='S', product_type='I',exchange='NFO', tradingsymbol=tsym_pe, quantity=qty, discloseqty=0,
                                        price_type='SL-LMT', price=stoploss_limit_pe, trigger_price=stoploss_limit_trigger_pe,retention='DAY', remarks='my_order_001')
            sl_order_number=sl_order_number['norenordno']
            log(f'[SLOrderPlaced] Placed SL order for put position and order number is {sl_order_number}')
        elif order_status=='OPEN':
            cancel_ord = api.cancel_order(orderno=order_no)
            check_order_stat()
            log(f'[OrderCancelled] Order Still open, since cancelled {order_no} to avoid the loop.Place the order again')
            pass
        elif order_status=='REJECTED':
            log(f'[OrderRejected]order rejected')
    except Exception as e:
        errorlog(f'an exception occurred :: {e}')

def cancel_sl_order():
    try:
        cancel_sl_order=api.cancel_order(orderno=sl_order_number)
        log(f'cancelled SL order {sl_order_number}, before squre off the position')
    except Exception as e:
        errorlog(f'an exception occurred :: {e}')

def squreoff(): # squreoff all the open order manually
    try:
        cancel_sl_order()
        log(f'squre off the open postions')
        squreoff_Pos=api.get_positions()
        squreoff_Pos=pd.DataFrame(squreoff_Pos)
        row=0
        for row in squreoff_Pos.to_dict("records"):
            if int(row["netqty"])>0:
                print(row["tsym"])
                api.place_order(buy_or_sell='S', product_type='I', exchange='NFO', tradingsymbol=row["tsym"], quantity=int(row["netqty"]),discloseqty=0,price_type='MKT',price=0,trigger_price=None, retention='DAY',remarks='my_order_001')
    except Exception as e:
        errorlog(f'an exception occurred :: {e}')
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


            if netqty != 0:
                pos_symbol=Label(root,text=symbol,width=24,bg="cornsilk3",fg="black",font=("Arial Black",10))
                pos_symbol.place(x=40,y=280) 
                pos_Avg=Label(root,text=Avg,width=8,bg="cornsilk3",fg="black",font=("Arial Black",10))
                pos_Avg.place(x=240,y=280)
                pos_ltp=Label(root,text=liveprice,width=10,bg="cornsilk3",fg="black",font=("Arial Black",10))
                pos_ltp.place(x=315,y=280)
                pos_netqty=Label(root,text=netqty,width=10,bg="cornsilk3",fg="black",font=("Arial Black",10))
                pos_netqty.place(x=405,y=280)
                profitLabel=Label(root, text=pnlpos, width=10,fg="black",font=("Arial Black",10))
                profitLabel.place(x=493, y=280)
                if pnlpos > 0:
                    profitLabel.config(bg="Green")
                else:
                    profitLabel.config(bg="Red")
            elif netqty == 0:
                log(f'No Open Position since the loop brokened')
                global stopPos
                if(stopPos==True):
                    stopPos=False
                    break
                break
    except Exception as e:
        errorlog(f'an exception occurred :: {e}')
#orderData funtion to collect sl,tager,qty data

bn_nifty_lp=[]

def my_expiry_update(*args): # Get the expiry date from Combobox
    global Expiry_day
    try:
        Expiry_day=Expiry_day_combo_box1.get()
        log(f'Expiry day selected {Expiry_day}')
    except Exception as e:
        errorlog(f'an exception occurred :: {e}')

def my_index (*args):
    global index_symbol
    global qty

    try:
        index_symbol=index_combo1box.get()
        log(f'index selected is: {index_symbol}')
    except Exception as e:
        errorlog(f'an exception occurred :: {e}')

    try: 
        if index_symbol == "NIFTY":
            qty_value=qty_combo_box1.get()
            qty_to_lot={"1": 50, "2": 100, "3": 150, "4": 200, "5": 250}
        elif index_symbol == "BANKNIFTY":
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
        
        log(f'Qty selected is: {qty}')   
    except Exception as e:
        errorlog(f'an exception occurred :: {e}')
    

def my_strike(*args): # Get the token details according to the Comobox selection & update the call & pur strike
    global tsym_ce
    global tsym_pe
    global token_ce
    global token_pe

    Strike_selection=Strike_combo_box1.get()    

    bn_nifty_lp=api.get_quotes('NSE', 'Nifty Bank') 
    nifty_lp=api.get_quotes('NSE', 'Nifty 50')
    bn_nifty_lp=float(bn_nifty_lp['lp'])
    nifty_lp=float(nifty_lp['lp'])

    try:
        if index_symbol == "NIFTY":
            nf_round_number = math.fmod(nifty_lp, 50)
            nf_atm = nifty_lp - nf_round_number
            nf_itm = nf_atm - 50
            nf_itm1= nf_atm - 100
            nf_itm2= nf_atm - 150
            nf_otm = nf_atm + 50
            nf_otm1 = nf_atm + 100
            nf_otm2 = nf_atm + 150
            in_the_money1 = 'itm2'
            in_the_money1 = 'itm1'
            in_the_money = 'itm'
            at_the_money = 'atm'
            out_of_the_money = 'otm'
            out_of_the_money1 = 'otm1'
            out_of_the_money1 = 'otm2'

            bn_list={"itm2": nf_itm2,"itm1": nf_itm1, "itm": nf_itm, "atm": nf_atm, "otm": nf_otm, "otm1": nf_otm1,"otm2": nf_otm2}
            in_the_money2 = 'itm2'
            in_the_money1 = 'itm1'
            in_the_money = 'itm'
            at_the_money = 'atm'
            out_of_the_money = 'otm'
            out_of_the_money1 = 'otm1'
            out_of_the_money2 = 'otm2'

        elif index_symbol == "BANKNIFTY":
            bn_round_number = math.fmod(bn_nifty_lp, 100) # round the strike
            bn_atm = bn_nifty_lp - bn_round_number
            bn_itm = bn_atm - 100
            bn_itm1= bn_atm - 200
            bn_itm2= bn_atm - 300
            bn_otm = bn_atm + 100
            bn_otm1 =bn_atm + 200
            bn_otm2 =bn_atm + 300

            in_the_money1 = 'itm2'
            in_the_money1 = 'itm1'
            in_the_money = 'itm'
            at_the_money = 'atm'
            out_of_the_money = 'otm'
            out_of_the_money1 = 'otm1'
            out_of_the_money1 = 'otm2'

            bn_list={"itm2": bn_itm2,"itm1": bn_itm1, "itm": bn_itm, "atm": bn_atm, "otm": bn_otm, "otm1": bn_otm1,"otm2": bn_otm2}
            in_the_money2 = 'itm2'
            in_the_money1 = 'itm1'
            in_the_money = 'itm'
            at_the_money = 'atm'
            out_of_the_money = 'otm'
            out_of_the_money1 = 'otm1'
            out_of_the_money2 = 'otm2'
     
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
        elif combo_value == "ITM2":
            strike_price_Ce=bn_list.get(in_the_money2)
            strike_price_Pe=bn_list.get(out_of_the_money2)
        elif combo_value == "OTM":
            strike_price_Ce=bn_list.get(out_of_the_money)
            strike_price_Pe=bn_list.get(in_the_money)
        elif combo_value == "OTM1":
            strike_price_Ce=bn_list.get(out_of_the_money1)
            strike_price_Pe=bn_list.get(in_the_money1)
        elif combo_value == "OTM2":
            strike_price_Ce=bn_list.get(out_of_the_money2)
            strike_price_Pe=bn_list.get(in_the_money2)
    
        log(f'call option strike:{strike_price_Ce}, put option strike:{strike_price_Pe}')

        call_strike.delete(0,"end")
        call_strike.insert(0,strike_price_Ce)
        put_strike.delete(0,"end")
        put_strike.insert(0,strike_price_Pe)
    except Exception as e:
        errorlog(f'an exception occurred :: {e}')


# write the logic here to get the token 
    try:
        Symbol_strike = strike_price_Ce
        Symbol_index = index_symbol
        Symbol_Expiry_day = Expiry_day
        ScripName_CE=f'{Symbol_index} {Symbol_Expiry_day} {Symbol_strike}'+" "+'CE'
        res_ce = api.searchscrip('NFO',searchtext=ScripName_CE)
        tsym_ce=res_ce['values'][0]['tsym']
        token_ce=res_ce['values'][0]['token']
        Symbol_strike = strike_price_Pe
        Symbol_index = index_symbol
        Symbol_Expiry_day = Expiry_day
        ScripName_PE=f'{Symbol_index} {Symbol_Expiry_day} {Symbol_strike}'+" "+'PE'
        res_pe = api.searchscrip('NFO',searchtext=ScripName_PE)
        tsym_pe=res_pe['values'][0]['tsym']
        token_pe=res_pe['values'][0]['token']
        update_ltp()
    except Exception as e:
        errorlog(f'an exception occurred :: {e}')

#qty_value=0    
def loss_stop(*args):
    global sl

    try:
        sl=float(stoploss.get())
        #qty=qtycalldata.get()
        log(f'collected the SL: {sl}')
    except Exception as e:
        errorlog(f'an exception occurred :: {e}')


#def orderData(*args): # Get the orderData like SL,Target,QTY
    #global target

def trade_book(): # Display the Help child window
   
    try:
        top= Toplevel(root)
        top.geometry("750x250")
        top.title("Trade book")

        #Label(root, text='Work in Progress',font=("Helvatical bold",15))
        trade_b = api.get_trade_book()
        trade_b=pd.DataFrame(trade_b)
        
    except Exception as e:
        errorlog(f'an exception occurred :: {e}')


def update_ltp(): # Update the strike price in tkinter window
    try:

        call_strike_ltp=api.get_quotes(exchange='NFO', token=token_ce)
        call_strike_ltp=call_strike_ltp['lp']
        display_call_ltp=Label(root,text=call_strike_ltp,width=5,bg='Orange')
        display_call_ltp.place(x=500,y=120)
        put_strike_ltp=api.get_quotes(exchange='NFO', token=token_pe)
        put_strike_ltp=put_strike_ltp['lp']
        display_put_ltp=Label(root,text=put_strike_ltp,width=5,bg='Orange')
        display_put_ltp.place(x=560,y=120)
        log(f'call ltp:{tsym_ce}  {call_strike_ltp} and put ltp: {tsym_pe} {put_strike_ltp}')
    except Exception as e:
        errorlog(f'an exception occurred :: {e}')

root=Tk()
root.geometry("650x350")
root.config(background="#ffffe6")
root.title('Richdotin Scalper App')
style= ttk.Style()
style.theme_use('clam')
#style.theme_use('winnative') ## enable this for windows
root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file='richdotcom.png'))
#root.iconbitmap(r'c:\Users\SN\exe\ShoonyaApi-py\richdotcom.ico')

def time():
    string = strftime('%H:%M:%S %p')
    lbl.config(text = string)
    lbl.after(1000, time)
  
lbl = Label(root, font = time_font,
            background = time_bg,
            foreground = time_fg)
lbl.place(x=530,y=310)
time()

#### BUTTONS####
# Login button
Login_btn1 = Button(root, 
                    text='Login',
                    font=btn_fonts,
                    fg=btn_fg,
                    bg=btn_bg,
                    bd=0,
                    activeforeground="Green",
                    command=lambda:startThread(0))
Login_btn1.place(x=40, 
                 y=10)
#Orders Button
tb_btn1 = Button(root,
                 text='Logs',
                 font=btn_fonts,
                 fg=btn_fg,
                 bg=btn_bg,
                 bd=0,
                 activeforeground="Green",
                 command=lambda:startThread(1))
tb_btn1.place(x=570, 
              y=10)
# CE BUY button
CE_BUY_Btn1 = Button(root, 
                     text='Buy',
                     font=btn_fonts,
                     fg=btn_fg,
                     bg=btn_bg,
                     bd=0,
                     activeforeground="Green",
                     command=lambda:startThread(2))
CE_BUY_Btn1.place(x=500, 
                  y=150)
#Refresh button
Refresh_btn1 = Button(root,
                      text='Refresh',
                      font=btn_fonts,
                      fg=btn_fg,
                      bg=btn_bg,
                      bd=0,
                      activeforeground="Green",
                      command=lambda:startThread(3))
Refresh_btn1.place(x=490,
                   y=10)
# PE BUY button
PE_BUY_Btn1 = Button(root,
                     text='Buy',
                     font=btn_fonts,
                     fg=btn_fg,
                     bg=btn_bg,
                     bd=0,
                     activeforeground="Green",
                     command=lambda:startThread(4))
PE_BUY_Btn1.place(x=560,
                  y=150)
#squreoff button 
squreoff_Btn1 = Button(root,
                       text='SqureOff',
                       font=btn_fonts,
                       fg=btn_fg,
                       bg=btn_bg,
                       bd=0,
                       activeforeground="Green",
                       command=lambda:startThread(5))
squreoff_Btn1.place(x=130,
                    y=200)
# Positions button
Positions_btn = Button(root,
                       text='Positions',
                       font=btn_fonts,
                       bg=btn_bg,
                       fg=btn_fg,
                       bd=0,
                       activeforeground="Green",
                       command=lambda:startThread(6))
Positions_btn.place(x=40,
                    y=200)

### LABEL 

#POS LABELS
lab_symbol=Label(root,
                 text='Symbol',
                 width=24,
                 bg="cornsilk3",
                 fg="black",
                 font=("Arial Black",10))
lab_symbol.place(x=40,
                 y=250)       
lab_Avg=Label(root,
              text='Avg',
              width=8,
              bg="cornsilk3",
              fg="black",
              font=("Arial Black",10))
lab_Avg.place(x=240,
              y=250)
lab_ltp=Label(root,
              text='Ltp',
              width=10,
              bg="cornsilk3",
              fg="black",
              font=("Arial Black",10))
lab_ltp.place(x=313,
              y=250)
lab_qty=Label(root,
              text='Qty',
              width=10,
              bg="cornsilk3",
              fg="black",
              font=("Arial Black",10))
lab_qty.place(x=403,
              y=250)
lab_pnl=Label(root,
              text='Pnl',
              width=10,
              bg="cornsilk3",
              fg="black",
              font=("Arial Black",10))
lab_pnl.place(x=493,
              y=250)
# Symbol Label
Symbol_lbl1 = Label(root,
                    text='Symbol:',
                    bg=lbl_bg,
                    font=lbl_fonts)
Symbol_lbl1.place(x=40,
                  y=110)
# Expiry day Label
Expiry_date_lbl1 = Label(root,
                         text='Expiry:',
                         bg=lbl_bg,
                         font=lbl_fonts)
Expiry_date_lbl1.place(x=40,
                       y=60)
# Strike Label
Strike_lbl1 = Label(root,
                    text='Strike:',
                    bg=lbl_bg,
                    font=lbl_fonts)
Strike_lbl1.place(x=40,
                  y=160)
#Profit m2m
m2m_lbl1 = Label(root,
                 text='m2m:',
                 bg=lbl_bg,
                 font=m2m_fonts)
m2m_lbl1.place(x=230,
               y=210)
#SL Label 
sl_text = Label(root,
                text='SL:',
                bg=lbl_bg,
                font=lbl_fonts)
sl_text.place(x=250,
              y=80)
#Order Stat Label
ord_stat = Label(root,
                 text='Order Stat:',
                 bg=lbl_bg,
                 font=lbl_fonts)
ord_stat.place(x=40,
               y=310)
# CALL Label
CALL_lbl1 = Label(root,
                  text='CALL',
                  bg=lbl_bg,
                  font=lbl_fonts)
CALL_lbl1.place(x=500,
                y=60)
# PUT Label
PUT_lbl1 = Label(root,
                 text='PUT',
                 bg=lbl_bg,
                 font=lbl_fonts)
PUT_lbl1.place(x=565,
               y=60)

# Strike Price Label
Strike_price_lbl1 = Label(root,
                          text='Strike:',
                          bg=lbl_bg,
                          font=lbl_fonts)
Strike_price_lbl1.place(x=400,
                        y=90)
# Strike Label
price_lable = Label(root, 
                    text='Price:',
                    bg=lbl_bg,
                    font=lbl_fonts)
price_lable.place(x=400,
                  y=120)
# QTY Label
QTY_lbl1 = Label(root, 
                 text='Lot:',
                 bg=lbl_bg,
                 font=lbl_fonts)
QTY_lbl1.place(x=400, 
               y=150)

### Entry box
### SL Entry
stoploss=IntVar()
loss=Entry(root,
           width=5,
           textvariable=stoploss,
           borderwidth=0)
loss.place(x=320,
           y=80)
stoploss.trace("w", loss_stop)

### Order Stat
ord_stat_entry=Entry(root,
                     width=10,
                     borderwidth=0)
ord_stat_entry.place(x=130,
                     y=310)
## CALL Entry box 
call_strike=Entry(root,
                  width=5,
                  borderwidth=0)
call_strike.place(x=500,
                  y=90)
## PUT Entry box
put_strike=Entry(root,
                 width=5,
                 borderwidth=0)
put_strike.place(x=560,
                 y=90)

### Combobox
# Combobox 0
index_values1=["Select Index","NIFTY","BANKNIFTY"]
index_combo1=tk.StringVar()
index_combo1box=ttk.Combobox(root, values=index_values1,width=11,textvariable=index_combo1)
index_combo1box.place(x=120,y=110)
index_combo1box.current(0)
index_combo1.trace('w', my_index)

#Combobox 1

expiry_date=config.get("expiry","values") # The details expiry details need to be updated in ini file.
Expiry_day_combo=tk.StringVar() # string variable 
Expiry_day_combo_box1 =ttk.Combobox(root, values=expiry_date,width=11,textvariable=Expiry_day_combo)
Expiry_day_combo_box1.place(x=120, y=60)
Expiry_day_combo_box1.current(0)
Expiry_day_combo.trace('w',my_expiry_update)
# Combobox 2
BN_Combo_values=["ITM2","ITM1","ITM","ATM","OTM","OTM1","OTM2"]
Strike_combo=tk.StringVar()
Strike_combo_box1 = ttk.Combobox(root, values=BN_Combo_values,width=11,textvariable=Strike_combo)
Strike_combo_box1.place(x=120, y=160)
Strike_combo_box1.current(3)
Strike_combo.trace('w',my_strike)
# Combobox 3
qty_combo_value=["1","2","3","4","5"]
qty_combo=tk.StringVar()
qty_combo_box1 = ttk.Combobox(root, values=qty_combo_value,width=3,textvariable=qty_combo)
qty_combo_box1.place(x=440, y=150)
qty_combo_box1.current(0)
qty_combo.trace('w',my_index)

## Main loop
root.mainloop()

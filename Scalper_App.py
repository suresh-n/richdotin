## Scalper App to buy the option with one click with SL & Target
from time import sleep
from tkinter import *
import tkinter as tk
from tkinter import ttk
import threading,json,math,sqlite3,logging,config
from datetime import datetime, timedelta
from api_helper import ShoonyaApiPy
import pandas as pd
import time

#enable dbug to see request and responses
#logging.basicConfig(level=logging.DEBUG)


api = ShoonyaApiPy()

def Login(): #Login function get the api login + username and cash margin
    global ret
    ret = api.login(userid = config.user, password = config.pwd, twoFA=config.factor2, vendor_code=config.vc, api_secret=config.app_key, imei=config.imei)
    usersession=ret['susertoken']
    print(usersession)
    balance = api.get_limits()['cash']
    Label(root, text=balance,bg="green",fg="white").grid(row=1, column=3, padx=220, pady=20)
    # Margin Avbl Label
    Margin_Avbl_lbl1 = Label(root, text='Avbl_Margin:',bg="floral white")
    Margin_Avbl_lbl1.place(x=130, y=20)
    username = ret['uname']
    username = "WELCOME" + " " + username + "!"
    Welcome_lbl2 = Label(root, text=username, fg="white", bg="green")
    Welcome_lbl2.place(x=320, y=20)

def Refresh_clicked(): # Function get the BN last price so the code can calculate the Strikes 
    global bn_nifty_lp
    global bn_list
    while True:

        bn_nifty_lp=api.get_quotes('NSE', 'Nifty Bank') 
        bn_nifty_lp=float(bn_nifty_lp['lp'])
        print(bn_nifty_lp)
        pos_data=api.get_positions()
        if pos_data == None:
            print("No Positions Data available today")
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
        if netqty == 0:
            sleep(10)
        break

def startThread(thread): # Start the Thread (Thread Manager)
    match thread:
        case 0:
            t1=threading.Thread(target=Login)
            t1.start()
        case 1:
            t1=threading.Thread(target=help)
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
            t1=threading.Thread(target=pos)
            t1.start()

def stopThread(thread):  # Stop the Thread (Thread Manager)
    global stopPos,stopStrat
    match thread:
        case 0:
            stopPos=True
        case 1:
            stopStrat=True

def check_order_stat(): # Check the order details to place the SL order
    global order_status
    ret = api.get_order_book()
    #print(ret)
    ret=pd.DataFrame(ret)
    row=0
    for row in ret.to_dict("records"):
        if order_no==row["norenordno"]:
            order_status=row["status"]
            print("orderstatus:", order_status)
            #print(row["status"],row["tsym"])

Symbol_Name = []

order_no=[]

def placeCallOrder():  # Place the Call option order 
    global order_no
    global sl_order_number
    price_ltp = api.get_quotes(exchange='NFO', token=token_ce)
    price_ltp=price_ltp['bp1']
    trigger_order_input=float(price_ltp)-float(1.0)
    stop_lossinput_order = float(price_ltp) - float(sl) 
    trigger_lossinput = float(stop_lossinput_order) -float(1.0)
    target_input_order = float(target) + float(price_ltp)
    trigger_target=float(target_input_order)+float(1.0)
    
    # make order
    order_no=api.place_order(buy_or_sell='B', product_type='I',
                        exchange='NFO', tradingsymbol=tsym_ce, 
                        quantity=qty, discloseqty=0,price_type='LMT', price=price_ltp, trigger_price=None,
                        retention='DAY', remarks='my_order_001')
    print(order_no)
    order_no=order_no['norenordno']

    sl_order_number = ""
    while True:
        check_order_stat()
        if order_status=='COMPLETE':
            print("Place SL/Target order")
            sl_order_number=api.place_order(buy_or_sell='S', product_type='I',exchange='NFO', tradingsymbol=tsym_ce, 
                         quantity=qty, discloseqty=0,price_type='SL-LMT', price=stop_lossinput_order, trigger_price=trigger_lossinput,
                         retention='DAY', remarks='my_order_001')
            print(sl_order_number)
        elif order_status=='OPEN':
            print("please wait order is still open")
        elif order_status=='REJECTED':
            print("order has been Rejected")
            print ("enter new while loop")
                
            if sl_order_number:
                ltp=api.get_quotes(exchange='NFO', token=token_ce)
                price_ltp=ltp['lp']
                print(price_ltp)
                sleep (3)
                if float(price_ltp) > float(target_input_order):
                    target_order = api.modify_order(exchange='NFO', tradingsymbol=tsym_ce, orderno=sl_order_number,
                                    newquantity=qty, newprice_type='SL-LMT', newprice=target_input_order, newtrigger_price=trigger_target)
                    print(target_order)
                    print("Target order placed in system")
        

def placePutOrder():   # Place the Put option order
    global order_no
    price_ltp = api.get_quotes(exchange='NFO', token=token_pe)
    price_ltp=price_ltp['bp1']
    print(price_ltp)
    # trigger_order_input=float(price_ltp)-float(1.0)

    # stop_lossinput_order = float(price_ltp) - float(sl) 
    # print(stop_lossinput_order)
    # trigger_lossinput = float(stop_lossinput_order) -float(4.0)
    # print(trigger_lossinput)
    # target_input_order = float(target) + float(price_ltp)
    # print(target_input_order)
    # trigger_target=float(target_input_order)+float(2.0)
    # print(trigger_target)
    

    order_no=api.place_order(buy_or_sell='B', product_type='I',
                        exchange='NFO', tradingsymbol=tsym_pe, 
                        quantity=qty, discloseqty=0,price_type='LMT', price=price_ltp, trigger_price=None,
                        retention='DAY', remarks='my_order_001')
    print(order_no)
    order_no=order_no['norenordno']

    # sl_order_number = ""
    # while True:
    #     check_order_stat()
    #     if order_status=='COMPLETE':
    #         print("Place SL/Target order")
    #         sl_order_number=api.place_order(buy_or_sell='S', product_type='I',exchange='NFO', tradingsymbol=tsym_pe, 
    #                      quantity=qty, discloseqty=0,price_type='SL-LMT', price=stop_lossinput_order,
    #                      retention='DAY', remarks='my_order_001')
    #     elif order_status=='OPEN':
    #         print("please wait order is still open")
    #     elif order_status=='REJECTED':
    #          print("order has been Rejected")
    #          print(sl_order_number)
    #     break 
    # while True: 
    #     if  sl_order_number:
    #         ltp=api.get_quotes(exchange='NFO', token=token_pe)
    #         price_ltp=ltp['lp']
    #         print(price_ltp)
    #         sleep (3)
    #         if float(price_ltp) > float(target_input_order):
    #             ret = api.modify_order(exchange='NFO', tradingsymbol=tsym_pe, orderno=sl_order_number,
    #                                 newquantity=qty, newprice_type='SL-LMT', newprice=target_input_order, newtrigger_price=trigger_target)
    #             print("Target order placed in system")
    #         else:
    #             continue
    #     else :
    #         print ("tested worked")
    #     break

def squreoff(): # squreoff all the open order manually
    squreoff_Pos=api.get_positions()
    squreoff_Pos=pd.DataFrame(squreoff_Pos)
    row=0
    for row in squreoff_Pos.to_dict("records"):
        if int(row["netqty"])>0:
            print(row["tsym"])
            api.place_order(buy_or_sell='S', product_type='I', exchange='NFO', tradingsymbol=row["tsym"], quantity=int(row["netqty"]),discloseqty=0,price_type='MKT',price=0,trigger_price=None, retention='DAY',remarks='my_order_001')

def pos(): # Display the Position Details
    global profitLabel
    global netqty
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
            Label(root,text=symbol,width=23,bg="cornsilk3",fg="black",font=("Arial Black",10)).place(x=40,y=280) 
            Label(root,text=Avg,width=8,bg="cornsilk3",fg="black",font=("Arial Black",10)).place(x=235,y=280)
            Label(root,text=liveprice,width=10,bg="cornsilk3",fg="black",font=("Arial Black",10)).place(x=310,y=280)
            Label(root,text=netqty,width=10,bg="cornsilk3",fg="black",font=("Arial Black",10)).place(x=400,y=280)
        #profitLabel=Label(root,text=pnlpos,width=10,bg="cornsilk3",font=("Arial Black",10)).place(x=380,y=280)
            profitLabel=Label(root, text=pnlpos, width=10,fg="black",font=("Arial Black",10))
            profitLabel.place(x=490, y=280)
            if pnlpos > 0:
                profitLabel.config(bg="Green")
            else:
                profitLabel.config(bg="Red")
        if netqty == 0:
                time.sleep(3)
                break
        break 

#orderData funtion to collect sl,tager,qty data

def orderData(*args): # Get the orderData like SL,Target,QTY
    global sl
    global target
    global qty
    sl=stoploss.get()
    print(sl)
    target=targetdata.get()
    qty=qtycalldata.get()

bn_nifty_lp=[]

def my_expiry_update(*args): # Get the expiry date from Combobox
    global Expiry_day
    Expiry_day=Expiry_day_combo_box1.get()
    print(Expiry_day)

def my_update(*args): # Get the token details according to the Comobox selection & update the call & pur strike
    global tsym_ce
    global tsym_pe
    global token_ce
    global token_pe
    minute_close = []
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
        print(strike_price_Ce,strike_price_Pe)
    elif combo_value == "ITM":
        strike_price_Ce=bn_list.get(in_the_money)
        strike_price_Pe=bn_list.get(out_of_the_money)
        print(strike_price_Ce,strike_price_Pe)
    elif combo_value == "ITM1":
        strike_price_Ce=bn_list.get(in_the_money1)
        strike_price_Pe=bn_list.get(out_of_the_money1)
        print(strike_price_Ce,strike_price_Pe) 
    elif combo_value == "OTM":
        strike_price_Ce=bn_list.get(out_of_the_money)
        strike_price_Pe=bn_list.get(in_the_money)
        print(strike_price_Ce,strike_price_Pe) 
    elif combo_value == "OTM2":
        strike_price_Ce=bn_list.get(out_of_the_money1)
        strike_price_Pe=bn_list.get(in_the_money1)
        print(strike_price_Ce,strike_price_Pe) 
    
    call_strike.delete(0,"end")
    call_strike.insert(0,strike_price_Ce)
    put_strike.delete(0,"end")
    put_strike.insert(0,strike_price_Pe)

# write the logic here to get the token 
    begin = time.time()
    Symbol_strike = strike_price_Ce
    Symbol_index = index
    Symbol_Expiry_day = Expiry_day
    ScripName_CE=f'{Symbol_index} {Symbol_Expiry_day} {Symbol_strike}'+" "+'CE'
    res_ce = api.searchscrip('NFO',searchtext=ScripName_CE)
    tsym_ce=res_ce['values'][0]['tsym']
    token_ce=res_ce['values'][0]['token']
    print( "call symbol is:", tsym_ce )
    print("call option token is:", token_ce)
    Symbol_strike = strike_price_Pe
    Symbol_index = index
    Symbol_Expiry_day = Expiry_day
    ScripName_PE=f'{Symbol_index} {Symbol_Expiry_day} {Symbol_strike}'+" "+'PE'
    res_pe = api.searchscrip('NFO',searchtext=ScripName_PE)
    tsym_pe=res_pe['values'][0]['tsym']
    token_pe=res_pe['values'][0]['token']
    print("work put symbol is:", tsym_pe )
    print("put option token is:", token_pe)
    update_ltp()
    end = time.time()
    print(f"Total runtime of the program is {end - begin}")
    

def help(): # Display the Help child window
   top= Toplevel(root)
   top.geometry("750x250")
   top.title("Help")
   with open('help.txt') as f:
       lines = f.read()
   Label(top, text= lines, font=('Arial Black', 10)).place(x=150,y=80)

root=Tk()
root.geometry("650x350")
root.config(background="floral white")
root.title('Richdotcom Scalper App')
style= ttk.Style()
style.theme_use('clam')
  
# Login button
Login_btn1 = Button(root, text='Login',fg="white",bg="black",command=lambda:startThread(0))
Login_btn1.place(x=40, y=10)
#Refresh button
Refresh_btn1 = Button(root, text='Refresh',width=4,fg="white",bg="black",command=lambda:startThread(3))
Refresh_btn1.place(x=490, y=10)

#Help Button
Help_btn1 = Button(root, text='Help',width=4,fg="white",bg="black",command=lambda:startThread(1))
Help_btn1.place(x=570, y=10)
# CE BUY button
CE_BUY_Btn1 = Button(root, text='BUY',width=3,fg="white",bg="black",command=lambda:startThread(2))
CE_BUY_Btn1.place(x=480, y=150)
# PE BUY button
PE_BUY_Btn1 = Button(root, text='BUY',width=3,fg="white",bg="black",command=lambda:startThread(4))
PE_BUY_Btn1.place(x=550, y=150)


#SL text & entry box
stoploss=DoubleVar()
sl_text = Label(root, text='SL:',font=("Helvatical bold",11))
sl_text.place(x=250, y=80)
loss=Entry(root, width=5,textvariable=stoploss)
loss.place(x=320, y=80)
stoploss.trace("w", orderData)


#Target text $ entry box
targetdata=DoubleVar()
target_text = Label(root, text='Target:',font=("Helvatical bold",11))
target_text.place(x=250, y=110)
target_entry=Entry(root,width=5,textvariable=targetdata)
target_entry.place(x=320, y=110)
targetdata.trace("w", orderData)

# qty side
qtycalldata=IntVar()
qty_call_entry=Entry(root,width=3,textvariable=qtycalldata)
qty_call_entry.place(x=440, y=150)
qtycalldata.trace("w", orderData)



# Symbol Label
Symbol_lbl1 = Label(root, text='Symbol:',font=("Helvatical bold",11))
Symbol_lbl1.place(x=40, y=60)

# Strike Label
Strike_lbl1 = Label(root, text='Strike:',font=("Helvatical bold",11))
Strike_lbl1.place(x=40, y=110)


# Expiry day Label
Expiry_date_lbl1 = Label(root, text='Expiry:',font=("Helvatical bold",11))
Expiry_date_lbl1.place(x=40, y=160)



# Positions button
Positions_btn = Button(root, text='Positions',width=5,font=("Helvatical bold",11),bg="black",fg="white",command=lambda:startThread(6))
Positions_btn.place(x=40, y=200)

#Profit m2m
m2m_lbl1 = Label(root, text='m2m:',font=("Helvatical bold",11))
m2m_lbl1.place(x=200, y=210)


#squreoff button 

squreoff_Btn1 = Button(root, text='SqureOff',width=4,fg="white",bg="black",command=lambda:startThread(5))
squreoff_Btn1.place(x=120, y=200)

# CALL Label
CALL_lbl1 = Label(root, text='CALL',font=("Helvatical bold",11))
CALL_lbl1.place(x=480, y=60)
call_strike=Entry(root,width=5)
call_strike.place(x=480,y=90)

# PUT Label
PUT_lbl1 = Label(root, text='PUT',font=("Helvatical bold",11))
PUT_lbl1.place(x=560, y=60)
put_strike=Entry(root,width=5)
put_strike.place(x=550,y=90)
# Strike Price Label
Strike_price_lbl1 = Label(root, text='Strike:',font=("Helvatical bold",11))
Strike_price_lbl1.place(x=400, y=90)
def update_ltp(): # Update the strike price in tkinter window
    call_strike_ltp=api.get_quotes(exchange='NFO', token=token_ce)
    call_strike_ltp=call_strike_ltp['lp']
    display_call_ltp=Label(root,text=call_strike_ltp,width=5)
    display_call_ltp.place(x=480,y=120)

    put_strike_ltp=api.get_quotes(exchange='NFO', token=token_pe)
    display_put_ltp=Label(root,text=put_strike_ltp['lp'],width=5)
    display_put_ltp.place(x=550,y=120)

# Strike Label
price_lable = Label(root, text='Price:',font=("Helvatical bold",11))
price_lable.place(x=400, y=120)

# QTY Label
QTY_lbl1 = Label(root, text='Qty:',font=("Helvatical bold",11))
QTY_lbl1.place(x=400, y=150)


# Combobox 1
Symbol_combo_box1 = ttk.Combobox(root,width=10)
Symbol_combo_box1['values'] = ("BANKNIFTY")
Symbol_combo_box1.place(x=120, y=60)
Symbol_combo_box1.current(0)

index=Symbol_combo_box1.get()


# Combobox 2

BN_Combo_values=["ITM1","ITM","ATM","OTM","OTM2"]
Strike_combo=tk.StringVar()
Strike_combo_box1 = ttk.Combobox(root, values=BN_Combo_values,width=10,textvariable=Strike_combo)
Strike_combo_box1.place(x=120, y=110)
Strike_combo_box1.current(2)
Strike_combo.trace('w',my_update)



#Combox Expiry Day

Expiry_day_combo=tk.StringVar() # string variable 
Expiry_day_combo_box1 =ttk.Combobox(root, values=["Select Expiry","9 JUN22","16 JUN22","JUN"],width=10,textvariable=Expiry_day_combo)
Expiry_day_combo_box1.place(x=120, y=160)
Expiry_day_combo_box1.current(0)
Expiry_day_combo.trace('w',my_expiry_update)

root.mainloop()

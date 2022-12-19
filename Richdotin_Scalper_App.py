from time import sleep
from tkinter import *
import tkinter as tk
from tkinter import ttk
import threading, json, math, sqlite3, logging, os, csv, time
from datetime import datetime, timedelta
from datetime import datetime as dt
from datetime import timedelta as td
from time import strftime
from api_helper import ShoonyaApiPy
import pandas as pd
from tkinter import simpledialog, filedialog, messagebox
import pyotp

import configparser
from pathlib import Path

config = configparser.ConfigParser()
config.read("config.ini")

authotp = pyotp.TOTP(
    config.get("CRED", "authenticator")
).now()  # copy the authenticator code here in quote.

start = datetime.now()
print(start)

logfile = dt.now().strftime("%d-%m-%Y_%H%M%S") + "_Scalper_App.log"
print(logfile)
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    filename=logfile,
    filemode="w",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def log(msg, *args):
    logging.info(msg, *args)
    # print(msg, *args)


def errorlog(msg1, *args):
    logging.error(msg1, *args)
    # print(msg1,*args)


# enable dbug to see request and responses
# logging.basicConfig(level=logging.DEBUG)

api = ShoonyaApiPy()

call_strike_ltp = 0.0
put_strike_ltp = 0.0
token_ce = 0
token_pe = 0
bn_nifty_lp = 0.0
nifty_lp = 0.0

##Style

lbl_fonts = ("Helvatical bold", 10)
btn_fonts = ("Helvatical bold", 10)
btn_fg = "White"
btn_bg = "Black"
lbl_fg = "white"
lbl_bg = "#ffffe6"
m2m_fonts = ("Helvatical bold", 10)
time_font = ("Helvatical bold", 10, "bold")
time_bg = "Green"
time_fg = "White"
top_lbl_fg = "Black"
top_lbl_bg = "Grey"
top_lbl_font = ("Helvatical bold", 10)
welcome_font = ("Helvatical bold", 10)
welcome_bg = "White"
welcome_fg = "Green"
refresh_font = ("Helvatical bold", 10)
refresh_bg = "White"
refresh_fg = "Green"


def write_test():
    get_user = get_username.get()
    get_password = get_pwd.get()
    get_Auth_2_1 = get_Auth.get()
    get_vc_1 = get_vc.get()
    get_apikey_1 = get_apikey.get()
    config.set("CRED", "user", get_user)
    config.set("CRED", "pwd", get_password)
    config.set("CRED", "authenticator", get_Auth_2_1)
    config.set("CRED", "vc", get_vc_1)
    config.set("CRED", "app_key", get_apikey_1)
    with open("config.ini", "w") as configfile:
        config.write(configfile)
        log(f"The test.ini file filled with the Credential details")
    top.destroy()


def Logout():
    global ret, api, display_call_ltp, display_put_ltp

    try:
        api.unsubscribe(["NSE|26009", "NSE|26000"])
        api.unsubscribe([f"NFO|{token_ce}", f"NFO|{token_pe}"])
        print("closing websocket")
        api.close_websocket()
        print("Logging out from API")
        api.logout()
        username = ret["uname"]
        username = "Bye Bye" + " " + str(username[:-10]) + "!"
        welcome_lbl["text"] = username

        display_call_ltp["text"] = 0.0
        display_put_ltp["text"] = 0.0
        Expiry_day_combo_box1.current(0)
        index_combo1box.current(0)
        Strike_combo_box1.current(0)
        qty_combo_box1.current(0)
        nifty_price_lbl["text"] = 0.0
        bnf_price_lbl["text"] = 0.0

        log(f"Sucessfully Logged out from the account {username}")

    except Exception as e:
        errorlog(f"an exception occurred :: {e} API ERROR")


def Login():  # Login function get the api login + username and cash margin
    global ret
    global get_username, get_pwd, get_Auth, get_vc, get_apikey
    global top
    if not config.get("CRED", "user"):
        log("CRED Variable is empty so getting variable")

        top = Toplevel(root)
        top.geometry("310x270")
        top.title("Richdotin Scalping App")
        top.config(background="Grey")
        lbl_username = Label(
            top, text="User:", fg=top_lbl_fg, font=top_lbl_font, bg=top_lbl_bg
        )
        lbl_username.place(x=30, y=20)
        lbl_password = Label(
            top, text="Password:", fg=top_lbl_fg, font=top_lbl_font, bg=top_lbl_bg
        )
        lbl_password.place(x=30, y=60)
        lbl_Auth = Label(
            top, text="Authenticator:", fg=top_lbl_fg, font=top_lbl_font, bg=top_lbl_bg
        )
        lbl_Auth.place(x=30, y=100)
        lbl_vc = Label(top, text="VC:", fg=top_lbl_fg, font=top_lbl_font, bg=top_lbl_bg)
        lbl_vc.place(x=30, y=140)
        lbl_api_key = Label(
            top, text="api_key:", fg=top_lbl_fg, font=top_lbl_font, bg=top_lbl_bg
        )
        lbl_api_key.place(x=30, y=180)
        get_username = Entry(top, width=15, borderwidth=0)
        get_username.place(x=130, y=20)
        get_pwd = Entry(top, width=15, show="*", borderwidth=0)
        get_pwd.place(x=130, y=60)
        get_Auth = Entry(top, width=20, borderwidth=0)
        get_Auth.place(x=130, y=100)
        get_vc = Entry(top, width=15, borderwidth=0)
        get_vc.place(x=130, y=140)
        get_apikey = Entry(top, width=20, show="*", borderwidth=0)
        get_apikey.place(x=130, y=180)

        submit_btn1 = Button(
            top,
            text="Submit",
            font=btn_fonts,
            fg=btn_fg,
            bg=btn_bg,
            bd=0,
            activeforeground="Green",
            command=write_test,
        )
        submit_btn1.place(x=130, y=220)

    else:

        try:
            # ret = api.login(userid = config.user, password = config.pwd, twoFA=config.factor2, vendor_code=config.vc, api_secret=config.app_key, imei=config.imei)
            ret = api.login(
                userid=config.get("CRED", "user"),
                password=config.get("CRED", "pwd"),
                twoFA=authotp,
                vendor_code=config.get("CRED", "vc"),
                api_secret=config.get("CRED", "app_key"),
                imei=config.get("CRED", "imei"),
            )
            usersession = ret["susertoken"]
            username = ret["uname"]
            log(f"Sucessfully Login to the account {username}")

            username = (
                "Welcome" + " " + str(username[:-10]) + "!"
            )  # Just for hiding full name
            welcome_lbl["text"] = username

            setupwebsocket()
            sleep(0.5)
            api.subscribe(["NSE|26009", "NSE|26000"])

        except Exception as e:
            errorlog(f"an exception occurred :: {e} API ERROR")


feed_opened = False
live_data = {}
SYMBOLDICT = {}


def event_handler_quote_update(inmessage):
    global live_data, token_ce, token_pe, bn_nifty_lp, nifty_lp

    print(inmessage["tk"], inmessage["lp"], inmessage["ts"])

    global SYMBOLDICT

    # e   Exchange
    # tk  Token
    # lp  LTP
    # pc  Percentage change
    # v   volume
    # o   Open price
    # h   High price
    # l   Low price
    # c   Close price
    # ap  Average trade price

    fields = [
        "ts",
        "lp",
        "pc",
        "c",
        "o",
        "h",
        "l",
        "v",
        "ltq",
        "ltp",
        "bp1",
        "sp1",
        "ap",
        "oi",
        "ap",
        "poi",
        "toi",
    ]

    message = {field: inmessage[field] for field in set(fields) & set(inmessage.keys())}
    # print(message)
    key = inmessage["e"] + "|" + inmessage["tk"]

    if key in SYMBOLDICT:
        symbol_info = SYMBOLDICT[key]
        symbol_info.update(message)
        SYMBOLDICT[key] = symbol_info
        live_data[key] = symbol_info
    else:
        SYMBOLDICT[key] = message
        live_data[key] = message

    update_idx_price()
    update_ce_ltp()
    update_pe_ltp()


def event_handler_order_update(tick_data):
    # print(f"Order update {tick_data}")
    print("order update")


def open_callback():
    global feed_opened
    feed_opened = True


def setupwebsocket():
    global feed_opened
    api.start_websocket(
        order_update_callback=event_handler_order_update,
        subscribe_callback=event_handler_quote_update,
        socket_open_callback=open_callback,
    )
    print("websocket connected")
    sleep(1)
    while feed_opened == False:
        print(feed_opened)
        pass
    return True


def Refresh():  # Function get the BN last price so the code can calculate the Strikes
    global api
    pos_data = api.get_positions()
    if pos_data == None:
        log(f"No Positions Data available for today")
    else:
        mtm = 0
        pnl = 0
        for i in pos_data:
            mtm += float(i["urmtom"])
            pnl += float(i["rpnl"])
            day_m2m = mtm + pnl
            day_m2m_total = "{:.2f}".format(day_m2m)
            m2m["text"] = day_m2m_total

            if day_m2m > 0:
                m2m.config(fg="Green")
            else:
                m2m.config(fg="Red")

    limit = api.get_limits()
    try:
        marginused = float((limit["marginused"]))
    except KeyError:
        marginused = 0

    margin_available = round(((float((limit["cash"]))) - marginused), 2)
    margin_available_1lotbn = margin_available / 25
    margin_available_1lotnf = margin_available / 50

    print(
        "With the avialble fund you can get one lot of BN with price:",
        margin_available_1lotbn,
    )
    print(
        "With the avialble fund you can get one lot of NF with price:",
        margin_available_1lotnf,
    )

    available_margin_price["text"] = margin_available

    log(f"BN last price updated  {bn_nifty_lp}")
    log(f"The fund balance updated {margin_available}")

    try:
        show_SL_order()
        log(f"checked if there is any SL order")
    except Exception as e:
        errorlog(f"an exception occurred :: {e}")
    root.update()


stopPos = False
stopStrat = False


def startThread(thread):  # Start the Thread (Thread Manager)
    match thread:
        case 0:
            t1 = threading.Thread(target=Login)
            t1.start()
        case 1:
            t1 = threading.Thread(target=trade_book)
            t1.start()
        case 2:
            t1 = threading.Thread(target=placeCallOrder())
            t1.start()
        case 3:
            t1 = threading.Thread(target=Refresh)
            t1.start()
        case 4:
            t1 = threading.Thread(target=placePutOrder())
            t1.start()
        case 5:
            t1 = threading.Thread(target=squareoff)
            t1.start()
        case 6:
            t1 = threading.Thread(target=pos, daemon="true")
            t1.start()
        case 7:
            t1 = threading.Thread(target=Logout)
            t1.start()


def stopThread(thread):  # Stop the Thread (Thread Manager)
    global stopPos, stopStrat
    match thread:
        case 0:
            stopPos = True
        case 1:
            stopStrat = True


def check_order_stat():  # Check the order details to place the SL order

    global order_status
    try:
        ret = api.get_order_book()
        # print(ret)
        ret = pd.DataFrame(ret)
        row = 0
        for row in ret.to_dict("records"):
            if order_no == row["norenordno"]:
                order_status = row["status"]
                print("orderstatus:", order_status)
                log(
                    f"[OrderStatus]Checking order status for order number {order_no} and the order status is {order_status}"
                )
                # print(row["status"],row["tsym"])

        # #order status to displayed in GUI
        ord_stat_entry.delete(0, "end")
        ord_stat_entry.insert(0, order_status)
    except Exception as e:
        errorlog(f"an exception occurred :: {e}")


Symbol_Name = []
order_no = []


def placeCallOrder():  # Place the Call option order
    global order_no
    global price_ltp

    try:
        # global target_limit
        price_ltp = api.get_quotes(exchange="NFO", token=token_ce)
        price_ltp = price_ltp["bp1"]

        # # Place call order
        order_no = api.place_order(
            buy_or_sell="B",
            product_type="I",
            exchange="NFO",
            tradingsymbol=tsym_ce,
            quantity=qty,
            discloseqty=0,
            price_type="LMT",
            price=price_ltp,
            trigger_price=None,
            retention="DAY",
            remarks="my_order_001",
        )
        order_no = order_no["norenordno"]
        log(
            f"[OrderPlaced] Placed call { tsym_ce } order at {price_ltp} x Quantity  {qty} and order number is {order_no}"
        )
        check_order_stat()
        if order_status == "OPEN":
            cancel_ord = api.cancel_order(orderno=order_no)
            check_order_stat()
        else:
            pass

    except Exception as e:
        errorlog(f"an exception occurred :: {e}")


def placePutOrder():  # Place the Put option order
    global order_no
    global price_ltp
    try:

        price_ltp = api.get_quotes(exchange="NFO", token=token_pe)
        price_ltp = price_ltp["bp1"]

        order_no = api.place_order(
            buy_or_sell="B",
            product_type="I",
            exchange="NFO",
            tradingsymbol=tsym_pe,
            quantity=qty,
            discloseqty=0,
            price_type="LMT",
            price=price_ltp,
            trigger_price=None,
            retention="DAY",
            remarks="my_order_001",
        )
        order_no = order_no["norenordno"]
        log(
            f"[OrderPlaced] Placed Put { tsym_pe } order at {price_ltp} x Quantity  {qty} and order number is {order_no}"
        )
        check_order_stat()
        if order_status == "OPEN":
            cancel_ord = api.cancel_order(orderno=order_no)
            check_order_stat()
        else:
            pass

    except Exception as e:
        errorlog(f"an exception occurred :: {e}")


def destroy_sl_show():
    sl_symbol_lbl1.destroy()
    sl_price_lbl1.destroy()
    sl_qty_lbl1.destroy()
    sl_status_lbl1.destroy()


def cancel_sl_order():
    try:
        cancel_sl_order = api.cancel_order(orderno=sl_order_number)
        log(f"cancelled SL order {sl_order_number}, before squre off the position")
        destroy_sl_show()

    except Exception as e:
        errorlog(f"an exception occurred :: {e}")


def squareoff():  # squareoff all the open order manually
    try:
        cancel_sl_order()
        log(f"square off the open postions")
        squareoff_Pos = api.get_positions()
        squareoff_Pos = pd.DataFrame(squareoff_Pos)
        row = 0
        for row in squareoff_Pos.to_dict("records"):
            if int(row["netqty"]) > 0:
                print(row["tsym"])
                api.place_order(
                    buy_or_sell="S",
                    product_type="I",
                    exchange=exch,
                    tradingsymbol=row["tsym"],
                    quantity=int(row["netqty"]),
                    discloseqty=0,
                    price_type="MKT",
                    price=0,
                    trigger_price=None,
                    retention="DAY",
                    remarks="my_order_001",
                )
    except Exception as e:
        errorlog(f"an exception occurred :: {e}")


stopPos = False


def do_popmenu(event):
    try:
        right_menu.tk_popup(event.x_root, event.y_root)
    finally:
        right_menu.grab_release


def manual_exit():
    try:
        cancel_sl_order()
        destroy_sl_show()
    except Exception as e:
        errorlog(f"an exception occurred :: {e}")
    try:
        api.place_order(
            buy_or_sell="S",
            product_type="I",
            exchange=exch,
            tradingsymbol=symbol,
            quantity=netqty,
            discloseqty=0,
            price_type="MKT",
            price=0,
            trigger_price=None,
            retention="DAY",
            remarks="my_order_001",
        )
        log(f"The open position exited,{symbol} {netqty} at market price")
        # destroy_pos_lbl()
        pos()

    except Exception as e:
        errorlog(f"an exception occurred :: {e}")


def do_popmenu1(event):
    try:
        right_menu1.tk_popup(event.x_root, event.y_root)
    finally:
        right_menu1.grab_release


def popup_sl():
    global sl_manual, sl_trigger
    try:
        manual_sl = simpledialog.askinteger(title="Add SL", prompt="SL")
        avg_round = round(float(Avg))
        sl_manual = float(avg_round) - float(manual_sl)
        sl_trigger = float(sl_manual) + float(1.0)
        log(f"manual SL is:{sl_manual}")
        place_manual_SL()

    except Exception as e:
        errorlog(f"an exception occurred :: {e}")


def show_SL_order():
    global right_menu1, sl_symbol_lbl1, sl_price_lbl1, sl_qty_lbl1, sl_status_lbl1, sl_order_number
    try:
        trail_sl = api.get_order_book()
        trail_sl = pd.DataFrame(trail_sl)
        row = 0
        for row in trail_sl.to_dict("records"):
            if row["status"] == "TRIGGER_PENDING":
                sl_order_number = row["norenordno"]
                sl_symbol_lbl1 = Label(
                    root,
                    text=row["tsym"],
                    width=25,
                    bg="cornsilk3",
                    fg="black",
                    font=("Arial Black", 10),
                )
                sl_symbol_lbl1.place(x=10, y=310)
                sl_price_lbl1 = Label(
                    root,
                    text=row["prc"],
                    width=10,
                    bg="cornsilk3",
                    fg="black",
                    font=("Arial Black", 10),
                )
                sl_price_lbl1.place(x=220, y=310)
                sl_qty_lbl1 = Label(
                    root,
                    text=row["qty"],
                    width=10,
                    bg="cornsilk3",
                    fg="black",
                    font=("Arial Black", 10),
                )
                sl_qty_lbl1.place(x=310, y=310)
                sl_status_lbl1 = Label(
                    root,
                    text=row["status"],
                    width=15,
                    bg="cornsilk3",
                    fg="black",
                    font=("Arial Black", 10),
                )
                sl_status_lbl1.place(x=400, y=310)

                right_menu1 = Menu(root, tearoff=0)
                right_menu1.config(
                    background="black", fg="white", activeforeground="Green"
                )
                right_menu1.add_command(
                    label="Trail SL", command=lambda: trail_sl_pop()
                )
                right_menu1.add_command(
                    label="Calcel Order", command=lambda: cancel_sl_order()
                )
                sl_symbol_lbl1.bind("<Button-3>", do_popmenu1)

    except Exception as e:
        errorlog(f"an exception occurred :: {e}")


def place_manual_SL():
    global sl_order_number
    try:
        sl_order_number = api.place_order(
            buy_or_sell="S",
            product_type="I",
            exchange=exch,
            tradingsymbol=symbol,
            quantity=netqty,
            discloseqty=0,
            price_type="SL-LMT",
            price=sl_manual,
            trigger_price=sl_trigger,
            retention="DAY",
            remarks="my_order_001",
        )
        sl_order_number = sl_order_number["norenordno"]

        log(f"Placed manual SL order: the order number is {sl_order_number}")
        show_SL_order()
    except Exception as e:
        errorlog(f"an exception occurred :: {e}")


def trail_sl_pop():
    global trail_sl_manual, trail_sl_trigger
    get_live_ltp = api.get_quotes(exchange=exch, token=symbol)
    get_live_ltp = get_live_ltp["lp"]

    try:
        trail_manual_sl = simpledialog.askinteger(title="Add Trail SL", prompt="SL")
        avg_round = round(float(get_live_ltp))
        trail_sl_manual = float(avg_round) - float(trail_manual_sl)
        trail_sl_trigger = float(trail_sl_manual) + float(2.0)
        log(f"trail manual SL is:{trail_sl_manual}")
        modify_sl_order()
    except Exception as e:
        errorlog(f"an exception occurred :: {e}")


def modify_sl_order():

    try:
        trail_sl = api.get_order_book()
        trail_sl = pd.DataFrame(trail_sl)
        row = 0
        for row in trail_sl.to_dict("records"):
            if row["status"] == "TRIGGER_PENDING":
                trail_exch = row["exch"]
                trail_symbol = row["tsym"]
                trail_order = row["norenordno"]
                trail_qty = row["qty"]
                trail_sl = api.modify_order(
                    exchange=trail_exch,
                    tradingsymbol=trail_symbol,
                    orderno=trail_order,
                    newquantity=trail_qty,
                    newprice_type="SL-LMT",
                    newprice=trail_sl_manual,
                    newtrigger_price=trail_sl_trigger,
                )
                log(
                    f"SL Order modified with trail price {trail_symbol} x {trail_qty}x{trail_order}x{trail_sl_manual}x{trail_sl_trigger}"
                )
                show_SL_order()
    except Exception as e:
        errorlog(f"an exception occurred :: {e}")


def destroy_pos_lbl():
    pos_symbol.destroy()
    pos_Avg.destroy()
    pos_ltp.destroy()
    pos_netqty.destroy()
    profitLabel.destroy()


def pos():
    global profitLabel, Avg, netqty, symbol, exch
    global pos_symbol, pos_Avg, pos_ltp, pos_netqty, profitLabel
    global right_menu

    try:
        netqty = 0
        while True:
            Refresh()
            orders = api.get_positions()
            orders = pd.DataFrame(orders)
            row = 0

            for row in orders.to_dict("records"):
                if int(row["netqty"]) > 0:
                    symbol = row["tsym"]
                    Avg = row["netavgprc"]
                    liveprice = row["lp"]
                    pnlpos = float(row["urmtom"])
                    netqty = float(row["netqty"])
                    exch = row["exch"]
            if netqty > 0:
                pos_symbol = Label(
                    root,
                    text=symbol,
                    width=25,
                    bg="cornsilk3",
                    fg="black",
                    font=("Arial Black", 10),
                )
                pos_symbol.place(x=10, y=250)
                pos_Avg = Label(
                    root,
                    text=Avg,
                    width=10,
                    bg="cornsilk3",
                    fg="black",
                    font=("Arial Black", 10),
                )
                pos_Avg.place(x=220, y=250)
                pos_ltp = Label(
                    root,
                    text=liveprice,
                    width=10,
                    bg="cornsilk3",
                    fg="black",
                    font=("Arial Black", 10),
                )
                pos_ltp.place(x=310, y=250)
                pos_netqty = Label(
                    root,
                    text=netqty,
                    width=10,
                    bg="cornsilk3",
                    fg="black",
                    font=("Arial Black", 10),
                )
                pos_netqty.place(x=400, y=250)
                profitLabel = Label(
                    root, text=pnlpos, width=10, fg="black", font=("Arial Black", 10)
                )
                profitLabel.place(x=490, y=250)

                right_menu = Menu(root, tearoff=0)
                right_menu.config(
                    background="black", fg="white", activeforeground="Green"
                )
                right_menu.add_command(label="Stop Loss", command=lambda: popup_sl())
                right_menu.add_command(label="Exit", command=lambda: manual_exit())

                pos_symbol.bind("<Button-3>", do_popmenu)

                if pnlpos > 0:
                    profitLabel.config(bg="Green")
                else:
                    profitLabel.config(bg="Red")
            elif netqty == 0:
                log(f"No Open Position since the loop brokened")
                break
                # global stopPos
                # if(stopPos==True):
                #     stopPos=False
                #     break
                # break

    except Exception as e:
        errorlog(f"an exception occurred :: {e}")


def my_expiry_update(*args):  # Get the expiry date from Combobox
    global Expiry_day
    try:
        Expiry_day = Expiry_day_combo_box1.get()
        log(f"Expiry day selected {Expiry_day}")
    except Exception as e:
        errorlog(f"an exception occurred :: {e}")


def my_index(*args):
    global index_symbol
    global qty

    try:
        index_symbol = index_combo1box.get()
        log(f"index selected is: {index_symbol}")
    except Exception as e:
        errorlog(f"an exception occurred :: {e}")

    try:
        if index_symbol == "NIFTY":
            qty_value = qty_combo_box1.get()
            qty_to_lot = {"1": 50, "2": 100, "3": 150, "4": 200, "5": 250}
        elif index_symbol == "BANKNIFTY":
            qty_value = qty_combo_box1.get()
            qty_to_lot = {"1": 25, "2": 50, "3": 75, "4": 100, "5": 125}

        if qty_value == "1":
            qty = qty_to_lot.get("1")
        elif qty_value == "2":
            qty = qty_to_lot.get("2")
        elif qty_value == "3":
            qty = qty_to_lot.get("3")
        elif qty_value == "4":
            qty = qty_to_lot.get("4")
        elif qty_value == "5":
            qty = qty_to_lot.get("5")

        log(f"Qty selected is: {qty}")
    except Exception as e:
        errorlog(f"an exception occurred :: {e}")


def my_strike(
    *args,
):  # Get the token details according to the Comobox selection & update the call & pur strike
    global tsym_ce
    global tsym_pe
    global token_ce
    global token_pe
    global call_strike_ltp
    global put_strike_ltp

    Strike_selection = Strike_combo_box1.get()
    bn_TokenKey = "NSE|26009"
    nf_TokenKey = "NSE|26000"
    bn_nifty_lp = float(live_data[bn_TokenKey].get("lp"))
    nifty_lp = float(live_data[nf_TokenKey].get("lp"))
    update_idx_price()

    try:
        if index_symbol == "NIFTY":
            nf_round_number = math.fmod(nifty_lp, 50)
            nf_atm = nifty_lp - nf_round_number
            nf_itm = nf_atm - 50
            nf_itm1 = nf_atm - 100
            nf_itm2 = nf_atm - 150
            nf_itm3 = nf_atm - 200
            nf_itm4 = nf_atm - 250
            nf_otm = nf_atm + 50
            nf_otm1 = nf_atm + 100
            nf_otm2 = nf_atm + 150
            nf_otm3 = nf_atm + 200
            nf_otm4 = nf_atm + 250
            in_the_money4 = "itm4"
            in_the_money3 = "itm3"
            in_the_money2 = "itm2"
            in_the_money1 = "itm1"
            in_the_money = "itm"
            at_the_money = "atm"
            out_of_the_money = "otm"
            out_of_the_money1 = "otm1"
            out_of_the_money2 = "otm2"
            out_of_the_money3 = "otm3"
            out_of_the_money4 = "otm4"

            bn_list = {
                "itm4": nf_itm4,
                "itm3": nf_itm3,
                "itm2": nf_itm2,
                "itm1": nf_itm1,
                "itm": nf_itm,
                "atm": nf_atm,
                "otm": nf_otm,
                "otm1": nf_otm1,
                "otm2": nf_otm2,
                "otm3": nf_otm3,
                "otm4": nf_otm4,
            }
            in_the_money4 = "itm4"
            in_the_money3 = "itm3"
            in_the_money2 = "itm2"
            in_the_money1 = "itm1"
            in_the_money = "itm"
            at_the_money = "atm"
            out_of_the_money = "otm"
            out_of_the_money1 = "otm1"
            out_of_the_money2 = "otm2"
            out_of_the_money3 = "otm3"
            out_of_the_money4 = "otm4"

        elif index_symbol == "BANKNIFTY":
            bn_round_number = math.fmod(bn_nifty_lp, 100)  # round the strike
            bn_atm = bn_nifty_lp - bn_round_number
            bn_itm = bn_atm - 100
            bn_itm1 = bn_atm - 200
            bn_itm2 = bn_atm - 300
            bn_itm3 = bn_atm - 400
            bn_itm4 = bn_atm - 500
            bn_otm = bn_atm + 100
            bn_otm1 = bn_atm + 200
            bn_otm2 = bn_atm + 300
            bn_otm3 = bn_atm + 400
            bn_otm4 = bn_atm + 500

            in_the_money4 = "itm4"
            in_the_money3 = "itm3"
            in_the_money2 = "itm2"
            in_the_money1 = "itm1"
            in_the_money = "itm"
            at_the_money = "atm"
            out_of_the_money = "otm"
            out_of_the_money1 = "otm1"
            out_of_the_money2 = "otm2"
            out_of_the_money3 = "otm3"
            out_of_the_money4 = "otm4"

            bn_list = {
                "itm4": bn_itm4,
                "itm3": bn_itm3,
                "itm2": bn_itm2,
                "itm1": bn_itm1,
                "itm": bn_itm,
                "atm": bn_atm,
                "otm": bn_otm,
                "otm1": bn_otm1,
                "otm2": bn_otm2,
                "otm3": bn_otm3,
                "otm4": bn_otm4,
            }
            in_the_money4 = "itm4"
            in_the_money3 = "itm3"
            in_the_money2 = "itm2"
            in_the_money1 = "itm1"
            in_the_money = "itm"
            at_the_money = "atm"
            out_of_the_money = "otm"
            out_of_the_money1 = "otm1"
            out_of_the_money2 = "otm2"
            out_of_the_money3 = "otm3"
            out_of_the_money4 = "otm4"

        combo_value = Strike_selection

        if combo_value == "ATM":
            strike_price_Ce = bn_list.get(at_the_money)
            strike_price_Pe = bn_list.get(at_the_money)
        elif combo_value == "ITM":
            strike_price_Ce = bn_list.get(in_the_money)
            strike_price_Pe = bn_list.get(out_of_the_money)
        elif combo_value == "ITM1":
            strike_price_Ce = bn_list.get(in_the_money1)
            strike_price_Pe = bn_list.get(out_of_the_money1)
        elif combo_value == "ITM2":
            strike_price_Ce = bn_list.get(in_the_money2)
            strike_price_Pe = bn_list.get(out_of_the_money2)
        elif combo_value == "ITM3":
            strike_price_Ce = bn_list.get(in_the_money3)
            strike_price_Pe = bn_list.get(out_of_the_money3)
        elif combo_value == "ITM4":
            strike_price_Ce = bn_list.get(in_the_money4)
            strike_price_Pe = bn_list.get(out_of_the_money4)
        elif combo_value == "OTM":
            strike_price_Ce = bn_list.get(out_of_the_money)
            strike_price_Pe = bn_list.get(in_the_money)
        elif combo_value == "OTM1":
            strike_price_Ce = bn_list.get(out_of_the_money1)
            strike_price_Pe = bn_list.get(in_the_money1)
        elif combo_value == "OTM2":
            strike_price_Ce = bn_list.get(out_of_the_money2)
            strike_price_Pe = bn_list.get(in_the_money2)
        elif combo_value == "OTM3":
            strike_price_Ce = bn_list.get(out_of_the_money3)
            strike_price_Pe = bn_list.get(in_the_money3)
        elif combo_value == "OTM4":
            strike_price_Ce = bn_list.get(out_of_the_money4)
            strike_price_Pe = bn_list.get(in_the_money4)

        log(
            f"call option strike:{strike_price_Ce}, put option strike:{strike_price_Pe}"
        )

        call_strike.delete(0, "end")
        call_strike.insert(0, strike_price_Ce)
        put_strike.delete(0, "end")
        put_strike.insert(0, strike_price_Pe)
    except Exception as e:
        errorlog(f"an exception occurred :: {e}")

    # write the logic here to get the token
    try:
        Symbol_strike = strike_price_Ce
        Symbol_index = index_symbol
        Symbol_Expiry_day = Expiry_day
        ScripName_CE = (
            f"{Symbol_index} {Symbol_Expiry_day} {Symbol_strike}" + " " + "CE"
        )
        res_ce = api.searchscrip("NFO", searchtext=ScripName_CE)
        tsym_ce = res_ce["values"][0]["tsym"]
        token_ce = res_ce["values"][0]["token"]
        Symbol_strike = strike_price_Pe
        Symbol_index = index_symbol
        Symbol_Expiry_day = Expiry_day
        ScripName_PE = (
            f"{Symbol_index} {Symbol_Expiry_day} {Symbol_strike}" + " " + "PE"
        )
        res_pe = api.searchscrip("NFO", searchtext=ScripName_PE)
        tsym_pe = res_pe["values"][0]["tsym"]
        token_pe = res_pe["values"][0]["token"]
        exchange = "NFO"
        symbol_sub = []
        symbol_sub.append(f"{exchange}|{token_ce}")
        symbol_sub.append(f"{exchange}|{token_pe}")
        api.subscribe(symbol_sub)

    except Exception as e:
        errorlog(f"an exception occurred :: {e}")


def export_log_to_excel():
    if len(tv.get_children()) < 1:
        messagebox.showinfo("No Data", "No Data Available to export")
        return False
    file = filedialog.asksaveasfilename(
        initialdir=os.getcwd(),
        title="Save CSV",
        filetypes=(("CSV File", "*.csv"), ("All Files", "*.*")),
    )
    with open(file, mode="w", newline="") as myfile:
        exp_writer = csv.writer(myfile, delimiter="\t")
        for i in tv.get_children():
            row = tv.item(i)["values"]
            exp_writer.writerow(row)
    messagebox.showinfo("Message", " Export Successful")
    log(f"exporeted the csv file")


def trade_book():  # Display the Help child window
    global tv
    try:
        top = Toplevel(root)
        # top.geometry("700x300")
        top.title("Trade book")
        top.config(background="#ffffe6")
        trade_b = api.get_trade_book()
        trade_b = pd.DataFrame(trade_b)

        tv = ttk.Treeview(top)
        tv["columns"] = ("Instrument", "Type", "Time", "Qty", "Price", "OrderNo")
        tv.column("#0", width=40, minwidth=25, anchor=CENTER)
        tv.column("Instrument", width=120, minwidth=25, anchor=CENTER)
        tv.column("Type", width=50, minwidth=25, anchor=CENTER)
        tv.column("Time", width=150, minwidth=25, anchor=CENTER)
        tv.column("Qty", width=50, minwidth=25, anchor=CENTER)
        tv.column("Price", width=100, minwidth=25, anchor=CENTER)
        tv.column("OrderNo", width=120, minwidth=25, anchor=CENTER)
        tv.heading("#0", text="ID", anchor=W)
        tv.heading("Instrument", text="Instrument")
        tv.heading("Type", text="Type")
        tv.heading("Time", text="Time")
        tv.heading("Qty", text="Qty")
        tv.heading("Price", text="Price")
        tv.heading("OrderNo", text="OrderNo")
        i = 0
        row = 0
        for row in trade_b.to_dict("records"):
            tv.insert(
                "",
                "end",
                values=(
                    row["tsym"],
                    row["trantype"],
                    row["norentm"],
                    row["qty"],
                    row["flprc"],
                    row["norenordno"],
                ),
            )

        tv.pack(pady=30)
        export_to_csv = Button(
            top,
            text="Export CSV",
            font=btn_fonts,
            fg=btn_fg,
            bg=btn_bg,
            bd=0,
            activeforeground="Green",
            command=lambda: export_log_to_excel(),
        )
        export_to_csv.pack()

    except Exception as e:
        errorlog(f"an exception occurred :: {e}")


def update_ltp():  # Update the strike price in tkinter window
    global display_call_ltp, display_put_ltp, token_ce, token_pe

    try:
        call_strike_ltp = api.get_quotes(exchange="NFO", token=token_ce)
        call_strike_ltp = call_strike_ltp["lp"]
        # call_strike_ltp = float(live_data[f"NFO|{token_ce}"].get("lp"))
        display_call_ltp["text"] = call_strike_ltp

        put_strike_ltp = api.get_quotes(exchange="NFO", token=token_pe)
        put_strike_ltp = put_strike_ltp["lp"]
        display_put_ltp["text"] = put_strike_ltp

        log(
            f"call ltp:{tsym_ce} {call_strike_ltp} and put ltp: {tsym_pe} {put_strike_ltp}"
        )
    except Exception as e:
        errorlog(f"an exception occurred :: {e}")


root = Tk()
root.geometry("590x350")
# Set the resizable property False
root.resizable(False, False)
root.config(background="#ffffe6")
root.title("Richdotin Scalper App")
# root.wait_visibility(root)
# root.wm_attributes("-alpha", 0.5)
style = ttk.Style()
style.theme_use("default")
style.theme_use("winnative")  ## enable this for windows
root.tk.call("wm", "iconphoto", root._w, tk.PhotoImage(file="richdotin.png"))
# root.iconbitmap(r'c:\Users\SN\exe\ShoonyaApi-py\richdotcom.ico')


def update_idx_price():
    global bn_nifty_lp, nifty_lp
    if live_data:
        nifty_lp = float(live_data[f"NSE|26000"].get("lp"))
        nifty_price_lbl["text"] = nifty_lp
        bn_nifty_lp = float(live_data[f"NSE|26009"].get("lp"))
        bnf_price_lbl["text"] = bn_nifty_lp


def update_ce_ltp():
    global call_strike_ltp, token_ce
    exchange = "NFO"
    if live_data:
        call_strike_ltp = float(live_data[f"{exchange}|{token_ce}"].get("lp"))
        # print(f"ce price :: {call_strike_ltp}")
        display_call_ltp["text"] = call_strike_ltp


def update_pe_ltp():
    global put_strike_ltp, token_pe
    exchange = "NFO"
    if live_data:
        put_strike_ltp = float(live_data[f"{exchange}|{token_pe}"].get("lp"))
        # print(f"pe price :: {put_strike_ltp}")
        display_put_ltp["text"] = put_strike_ltp


display_call_ltp = Label(root, text=call_strike_ltp, width=5, bg="Orange")
display_call_ltp.place(x=450, y=110)
display_put_ltp = Label(root, text=put_strike_ltp, width=5, bg="Orange")
display_put_ltp.place(x=510, y=110)


def time():
    string = strftime("%H:%M:%S %p")
    lbl.config(text=string)
    lbl.after(1000, time)


lbl = Label(root, font=time_font, background=time_bg, foreground=time_fg)
lbl.place(x=350, y=10)

time()

welcome_lbl = Label(root, text="", fg="Green", font=lbl_fonts, bg="White")
welcome_lbl.place(x=125, y=10)

available_margin_price = Label(
    root,
    text=0.0,
    bg=refresh_bg,
    font=refresh_font,
    width=8,
    fg=refresh_fg,
    relief="solid",
)
available_margin_price.place(x=270, y=60)
# Margin Available Label
available_margin_lbl = Label(root, text="Available Margin:", font=lbl_fonts, bg=lbl_bg)
available_margin_lbl.place(x=165, y=60)

m2m = Label(
    root,
    text=0.0,
    bg=refresh_bg,
    font=refresh_font,
    width=8,
    relief="solid",
)
m2m.place(x=270, y=100)
# Profit m2m
m2m_lbl1 = Label(root, text="MTM:", bg=lbl_bg, font=m2m_fonts)
m2m_lbl1.place(x=165, y=100)


#### BUTTONS####
# Login button
Login_btn = Button(
    root,
    text="Login",
    font=btn_fonts,
    fg=btn_fg,
    bg=btn_bg,
    bd=0,
    activeforeground="Green",
    command=lambda: startThread(0),
)
Login_btn.place(x=10, y=10)

# Login button
Logout_btn = Button(
    root,
    text="Logout",
    font=btn_fonts,
    fg=btn_fg,
    bg=btn_bg,
    bd=0,
    activeforeground="Green",
    command=lambda: startThread(7),
)
Logout_btn.place(x=60, y=10)


# Orders Button
tb_btn1 = Button(
    root,
    text="Logs",
    font=btn_fonts,
    fg=btn_fg,
    bg=btn_bg,
    bd=0,
    activeforeground="Green",
    command=lambda: startThread(1),
)
tb_btn1.place(x=520, y=10)
# CE BUY button
CE_BUY_Btn1 = Button(
    root,
    text="Buy",
    font=btn_fonts,
    fg=btn_fg,
    bg=btn_bg,
    bd=0,
    activeforeground="Green",
    command=lambda: startThread(2),
)
CE_BUY_Btn1.place(x=450, y=140)
# Refresh button
Refresh_btn1 = Button(
    root,
    text="Refresh",
    font=btn_fonts,
    fg=btn_fg,
    bg=btn_bg,
    bd=0,
    activeforeground="Green",
    command=lambda: startThread(3),
)
Refresh_btn1.place(x=440, y=10)
# PE BUY button
PE_BUY_Btn1 = Button(
    root,
    text="Buy",
    font=btn_fonts,
    fg=btn_fg,
    bg=btn_bg,
    bd=0,
    activeforeground="Green",
    command=lambda: startThread(4),
)
PE_BUY_Btn1.place(x=510, y=140)
# squareoff button
squareoff_Btn1 = Button(
    root,
    text="Square Off",
    font=btn_fonts,
    fg=btn_fg,
    bg=btn_bg,
    bd=0,
    activeforeground="Green",
    command=lambda: startThread(5),
)
squareoff_Btn1.place(x=100, y=180)
# Positions button
Positions_btn = Button(
    root,
    text="Positions",
    font=btn_fonts,
    bg=btn_bg,
    fg=btn_fg,
    bd=0,
    activeforeground="Green",
    command=lambda: startThread(6),
)
Positions_btn.place(x=10, y=180)

### LABEL

# POS LABELS
lab_symbol = Label(
    root, text="Symbol", width=25, bg="cornsilk3", fg="black", font=("Arial Black", 10)
)
lab_symbol.place(x=10, y=220)
lab_Avg = Label(
    root, text="Avg", width=10, bg="cornsilk3", fg="black", font=("Arial Black", 10)
)
lab_Avg.place(x=220, y=220)
lab_ltp = Label(
    root, text="Ltp", width=10, bg="cornsilk3", fg="black", font=("Arial Black", 10)
)
lab_ltp.place(x=310, y=220)
lab_qty = Label(
    root, text="Qty", width=10, bg="cornsilk3", fg="black", font=("Arial Black", 10)
)
lab_qty.place(x=400, y=220)
lab_pnl = Label(
    root, text="Pnl", width=10, bg="cornsilk3", fg="black", font=("Arial Black", 10)
)
lab_pnl.place(x=490, y=220)

# Sl order Lables
sl_symbol_lbl2 = Label(
    root, text="Symbol", width=25, bg="cornsilk3", fg="black", font=("Arial Black", 10)
)
sl_symbol_lbl2.place(x=10, y=280)

sl_price_Avg_lbl2 = Label(
    root, text="Price", width=10, bg="cornsilk3", fg="black", font=("Arial Black", 10)
)
sl_price_Avg_lbl2.place(x=220, y=280)

sl_price_tprice_lbl2 = Label(
    root, text="Qty", width=10, bg="cornsilk3", fg="black", font=("Arial Black", 10)
)
sl_price_tprice_lbl2.place(x=310, y=280)
sl_price_qty_lbl2 = Label(
    root, text="Status", width=15, bg="cornsilk3", fg="black", font=("Arial Black", 10)
)
sl_price_qty_lbl2.place(x=400, y=280)

# Symbol Label
Symbol_lbl1 = Label(root, text="Symbol:", bg=lbl_bg, font=lbl_fonts)
Symbol_lbl1.place(x=10, y=100)
# Expiry day Label
Expiry_date_lbl1 = Label(root, text="Expiry:", bg=lbl_bg, font=lbl_fonts)
Expiry_date_lbl1.place(x=10, y=60)
# Strike Label
Strike_lbl1 = Label(root, text="Strike:", bg=lbl_bg, font=lbl_fonts)
Strike_lbl1.place(x=10, y=140)

# NIFTY BANKNIFTY PRICE LABELS
nifty_lbl = Label(root, text="NIFTY 50", bg="Yellow", font=lbl_fonts)
nifty_lbl.place(x=180, y=150, width=70)

bnf_lbl = Label(root, text="Nifty Bank", bg="Yellow", font=lbl_fonts)
bnf_lbl.place(x=260, y=150, width=70)

nifty_price_lbl = Label(root, text=nifty_lp, bg="Orange", font=lbl_fonts)
nifty_price_lbl.place(x=180, y=180, width=70)

bnf_price_lbl = Label(root, text=bn_nifty_lp, bg="Orange", font=lbl_fonts)
bnf_price_lbl.place(x=260, y=180, width=70)

ord_stat = Label(root, text="Order Stat:", bg=lbl_bg, font=lbl_fonts)
ord_stat.place(x=390, y=190)
# CALL Label
CALL_lbl1 = Label(root, text="CALL", bg=lbl_bg, font=lbl_fonts)
CALL_lbl1.place(x=455, y=50)
# PUT Label
PUT_lbl1 = Label(root, text="PUT", bg=lbl_bg, font=lbl_fonts)
PUT_lbl1.place(x=515, y=50)

# Strike Price Label
Strike_price_lbl1 = Label(root, text="Strike:", bg=lbl_bg, font=lbl_fonts)
Strike_price_lbl1.place(x=360, y=80)
# Strike Label
price_lable = Label(root, text="Price:", bg=lbl_bg, font=lbl_fonts)
price_lable.place(x=360, y=110)


### Order Stat
ord_stat_entry = Entry(root, width=10, borderwidth=0)
ord_stat_entry.place(x=480, y=190)
## CALL Entry box
call_strike = Entry(root, width=5, borderwidth=0)
call_strike.place(x=450, y=80)
## PUT Entry box
put_strike = Entry(root, width=5, borderwidth=0)
put_strike.place(x=510, y=80)

### Combobox
# Combobox 0
index_values1 = ["Select Index", "NIFTY", "BANKNIFTY"]
index_combo1 = tk.StringVar()
index_combo1box = ttk.Combobox(
    root, values=index_values1, width=11, textvariable=index_combo1
)
index_combo1box.place(x=70, y=100)
index_combo1box.current(0)
index_combo1.trace("w", my_index)

# Combobox 1

expiry_date = config.get(
    "expiry", "values"
)  # The details expiry details need to be updated in ini file.
Expiry_day_combo = tk.StringVar()  # string variable
Expiry_day_combo_box1 = ttk.Combobox(
    root, values=expiry_date, width=11, textvariable=Expiry_day_combo
)
Expiry_day_combo_box1.place(x=70, y=60)
Expiry_day_combo_box1.current(0)
Expiry_day_combo.trace("w", my_expiry_update)
# Combobox 2
BN_Combo_values = [
    "Select Strike",
    "ITM4",
    "ITM3",
    "ITM2",
    "ITM1",
    "ITM",
    "ATM",
    "OTM",
    "OTM1",
    "OTM2",
    "OTM3",
    "OTM4",
]
Strike_combo = tk.StringVar()
Strike_combo_box1 = ttk.Combobox(
    root, values=BN_Combo_values, width=11, textvariable=Strike_combo
)
Strike_combo_box1.place(x=70, y=140)
Strike_combo_box1.current(0)
Strike_combo.trace("w", my_strike)
# Combobox 3
qty_combo_value = ["Select Lot", "1", "2", "3", "4", "5"]
qty_combo = tk.StringVar()
qty_combo_box1 = ttk.Combobox(
    root, values=qty_combo_value, width=10, textvariable=qty_combo
)
qty_combo_box1.place(x=360, y=140)
qty_combo_box1.current(0)
qty_combo.trace("w", my_index)

## Main loop

root.mainloop()

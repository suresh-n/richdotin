# Richdotin Scalper App

The Scalping App can be used to send orders to finvaisa broker using api without look much calculation about strikes. We can just select the strike like ATM , ITM and OTM and click buy to place limit buy order easily with desired stoploss and qty. We can also manully add stoploss and trail it when the price above your buy avg price. 

![](https://i.imgur.com/DcLxofj.png)


##### How to setup the scalper app 

1. clone the shoonya-py repo 

```
$ git clone https://github.com/Shoonya-Dev/ShoonyaApi-py.git

```
2. Create a python virtual env before install the requirement.

```
$ python3 -m venv venv
```

3. Activate the virtual environment

```
Source venv/bin/activate
```

2. install required python packages  

`$ pip install -r requirements.txt`

3. download the richdotcom repo files 

```
$wget https://github.com/suresh-n/richdotin/blob/706afca61657aa954efdc7f04100c073b806eccf/Richdotin_Scalper_App.py
```

```
$wget https://github.com/suresh-n/richdotin/blob/706afca61657aa954efdc7f04100c073b806eccf/config.ini

$wget https://github.com/suresh-n/richdotin/blob/706afca61657aa954efdc7f04100c073b806eccf/richdotin.png

```
4. Run the Richdotin_Scalper_App.py file. 

```
$python Richdotin_Scalper_App.py

```

5. Step 4 will launch the tkinter app shown in the picture above. just click Login Button it will open another window when you can enter the login and API info the same will be added to config.ini file. We check that manual when you login again the config details will be fetched from config.ini

6. only thing we need to edit in config.ini file is the expiry dates, we need to replace the current month expiry date there [expiry] values

#### How to use the Richdotcom Scalper App 

* Launch the python file and click Login.

* Click **Login** button, will call the api and get the your account name details which mean the api call is sucess and app & Api is working fine.

* Click **refresh** button which will  refresh the m2m & the margin availble to trade.

* Select the expiry day.

* Now select the symbol the App now support NIFTY & BN both. 

* Select the **strike** which you wanna make order like ATM,ITM,OTM. once you selected on right side of the App the strike details + ltp is displayed. 

* Select the Lot size you would like to buy. 

* click **BUY** button to place the order on the CALL or PUT side.

* Once the order placed the order send to broker and the order status updated into **order sat** text box like Completed/Rejected/Cancelled. We can see the position details by clicking the postion button. 

* When we are ready to exit the position we can simply right  click the position symbol and exit.

* To place the SL we can right click the position symbol and add SL and add points tool will auto calculate and place the SL order. 
> for example you wanna loss only 10 point just add 10 in SL field so the tool will minus 10 point from current price and place SL order in broker system. 

* To trail the SL order right click position symbol below the position details bottom and select modify SL to trail the SL. 


##### Issues to fix

* Tool hung  when running position while for longer. 
* When the SL hit the details not updated in the App. 


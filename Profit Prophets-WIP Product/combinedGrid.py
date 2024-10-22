''' THIS WILL BE USED WITH EACH STOCK'S OWN BUY AND SELL METHODS'''

import requests, json ##edited
from config import * # config file
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import tkinter.ttk as ttk
import time

BASE_URL = 'https://paper-api.alpaca.markets'
ACCOUNT_URL = '{}/v2/account'.format(BASE_URL)
ORDERS_URL = '{}/v2/orders'.format(BASE_URL)
ALL_ORDERS = '{}?status=all'.format(ORDERS_URL)
CLOSED_ORDERS = '{}?status=closed'.format(ORDERS_URL)
NEW_ORDERS = '{}?status=filled'.format(ORDERS_URL)

AAPLTRADE_PRICE = 'https://data.alpaca.markets/v2/stocks/AAPL/trades/latest?feed=iex'
TSLATRADE_PRICE = 'https://data.alpaca.markets/v2/stocks/TSLA/trades/latest?feed=iex'
AMZNTRADE_PRICE = 'https://data.alpaca.markets/v2/stocks/AMZN/trades/latest?feed=iex'
MSFTTRADE_PRICE = 'https://data.alpaca.markets/v2/stocks/MSFT/trades/latest?feed=iex'
METATRADE_PRICE = 'https://data.alpaca.markets/v2/stocks/META/trades/latest?feed=iex'
GOOGTRADE_PRICE = 'https://data.alpaca.markets/v2/stocks/GOOG/trades/latest?feed=iex'
HEADERS = {'APCA-API-KEY-ID': API_KEY,'APCA-API-SECRET-KEY': SECRET_KEY}


def get_account():
     r = requests.get(ACCOUNT_URL,headers=HEADERS)
     return json.loads(r.content)

def get_cash():

     r = requests.get(ACCOUNT_URL, headers=HEADERS)
     response = json.loads(r.content)
     cash = response['cash']
     #print(f'Your cash amount is: ${cash}')
     return cash

def get_tradePrice(stock):
     r = requests.get(stock, headers=HEADERS)
     response = json.loads(r.content)
     price = response['trade']['p']

     return price

# Function to create an order
def create_order(symbol, qty, side, type, time_in_force):
    data = {
        'symbol': symbol,
        'qty': qty,
        'side': side,
        'type': type,
        'time_in_force': time_in_force
    }
    r = requests.post(ORDERS_URL, json=data, headers=HEADERS)
    response = json.loads(r.content)
    print(response)


def get_orders():
     r = requests.get(ALL_ORDERS, headers=HEADERS)
     return json.loads(r.content)

# Function to check if the current time is within trading hours
def is_trading_hours():
    current_time = time.localtime()
    if current_time.tm_hour >= 9 and current_time.tm_hour < 16:
        return True
    else:
        return False

# Function to activate the bot at market opening
def activate_bot():
    if is_trading_hours():
         # Make purchases of specified stocks
         buy_stocks()
         schedule_sell_before_market_close()
    else:
         print("Market is closed. Cannot activate bot.")

# Function to deactivate the bot at market closing
def deactivate_bot():
    if is_trading_hours():
        # Sell all stocks before market closes
        sell_all_stocks()
    else:
        print("Market is closed. Bot is already deactivated.")

# Function to buy specified stocks
def buy_stocks():
    stocks_to_buy = ['AAPL', 'TSLA', 'AMZN', 'GOOG', 'META', 'MSFT']
    for stock in stocks_to_buy:
        create_order(symbol=stock, qty=1, side='buy', type='market', time_in_force='day') 

def sell_stocks_if_price_change():
    orders = get_orders()
    current_time = time.localtime()
    for order in orders:
        symbol = order['symbol']
        # Retrieve current price of the stock
        current_price = get_current_price(symbol)
        # Calculate percentage change
        purchase_price = get_purchase_price(symbol)
        percentage_change = ((current_price - purchase_price) / purchase_price) * 100
        if abs(percentage_change) >= 0.5:  # If price change is >= 0.5% in either direction
            create_order(symbol=symbol, qty=order['qty'], side='sell', type='market', time_in_force='day')
        elif current_time.tm_hour == 10 and current_time.tm_min == 1:
            create_order(symbol=symbol, qty=order['qty'], side='sell', type='market', time_in_force='day')
        deactivate_bot()


# Function to get the current price of a stock
def get_current_price(symbol):
    BASE_URL = 'https://data.alpaca.markets/v2/stocks/{}/quote'.format(symbol)
    HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY}
    r = requests.get(BASE_URL, headers=HEADERS)
    response = json.loads(r.content)
    current_price = response['last']['price']
    return current_price

# Function to get the purchase price of a stock
def get_purchase_price(symbol):
    BASE_URL = 'https://paper-api.alpaca.markets/v2/orders'
    HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY}
    r = requests.get(BASE_URL, headers=HEADERS)
    orders = json.loads(r.content)
    for order in orders:
        if order['symbol'] == symbol and order['side'] == 'buy':
            return order['filled_avg_price']
    return None  # If no buy order found for the symbol

# Function to schedule selling of stocks 15 minutes before market close
def schedule_sell_before_market_close():
    while True:
        # Check if it is 15 minutes before market close
        print('Checking Time')
        current_time = time.localtime()
        # 14 52
        if current_time.tm_hour == 14 and current_time.tm_min == 52:
            sell_all_stocks()
            break
        else:
            time.sleep(60)  

# Function to sell all stocks
def sell_all_stocks():
    stocks_to_sell = ['AAPL', 'TSLA', 'AMZN', 'GOOGL', 'META', 'MSFT']
    for stock in stocks_to_sell:
        create_order(symbol=stock, qty=1, side='sell', type='market', time_in_force='day')
    # orders = get_orders()
    # for order in orders:
    #   create_order(symbol=order['symbol'], qty=order['qty'], side='sell', type='market', time_in_force='day')

def get_closedorders():
     r = requests.get(CLOSED_ORDERS, headers=HEADERS)
     return json.loads(r.content)

def get_neworders():
    r = requests.get(NEW_ORDERS, headers=HEADERS)
    return json.loads(r.content)


def mainWindow():
     welcome.destroy()
     orderingGUI()
     #orderingGUI()
     get_cash()
     
def orderingGUI():
    global root
    root = tk.Tk()
     #root.state('zoomed')
     #root.attributes('-fullscreen', True)
    root.geometry('{}x{}'.format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.title('Code Craft - Ordering Stocks')
    #root.state('zoomed')
    global entry1, spin, v, j, k
    

    empty = tk.Label(root, text=' \n   ', width=10)
    empty.grid(column=1, row=0)
    empty = tk.Label(root, text=' \n   ', width=10)
    empty.grid(column=2, row=0)

    empty = tk.Label(root, text=' \n   ', width=10)
    empty.grid(column=3, row=5)

    empty = tk.Label(root, text=' \n   ', width=10)
    empty.grid(column=4, row=0)

    empty = tk.Label(root, text=' \n   ', width=10)
    empty.grid(column=5, row=0)

    # Display the user's cash amount
    cash = get_cash()
    cashAmount = tk.Label(root, text=f'You currently have: ${cash}', font=('TkDefaultFont', 18, 'bold'))
    #cashAmount.pack(pady=10,fill='x')
    cashAmount.grid(column=6, row=3)

    
    genmess = tk.Label(root, text='Currently buying one share at market price using: day time in force ',font=('TkDefaultFont', 18, 'bold'))
    genmess.grid(column=6, row=4)

    empty = tk.Label(root, text=' \n   ', width=10)
    empty.grid(column=6, row=5)

    empty = tk.Label(root, text=' \n   ', width=10)
    empty.grid(column=6, row=6)
    #empty = tk.Label(root, text=' \n   ')
    #empty.grid(column=2, row=0)

    # AAPL
    AAPLprice = get_tradePrice(AAPLTRADE_PRICE)
    buymess = tk.Label(root, text=f'AAPL at ${(AAPLprice)}',font=('TkDefaultFont', 18, 'bold'))
    buymess.grid(column=6, row=7)

    # MSFt
    MSFTprice = get_tradePrice(MSFTTRADE_PRICE)
    buymess = tk.Label(root, text=f'MSFT at ${(MSFTprice)}',font=('TkDefaultFont', 18, 'bold'))
    buymess.grid(column=6, row=8)
    
    # META
    METAprice = get_tradePrice(METATRADE_PRICE)
    buymess = tk.Label(root, text=f'META at ${(METAprice)}',font=('TkDefaultFont', 18, 'bold'))
    buymess.grid(column=6, row=9)

    # TSLA
    TSLAprice = get_tradePrice(TSLATRADE_PRICE)
    buymess = tk.Label(root, text=f'TSLA at ${(TSLAprice)}',font=('TkDefaultFont', 18, 'bold'))
    buymess.grid(column=6, row=10)

    # AMZN
    AMZNprice = get_tradePrice(AMZNTRADE_PRICE)
    buymess = tk.Label(root, text=f'AMZN at ${(AMZNprice)}',font=('TkDefaultFont', 18, 'bold'))
    buymess.grid(column=6, row=11)

    # GOOG
    GOOGprice = get_tradePrice(GOOGTRADE_PRICE)
    buymess = tk.Label(root, text=f'GOOG at ${(GOOGprice)}',font=('TkDefaultFont', 18, 'bold'))
    buymess.grid(column=6, row=12)

     #root.pack(side=RIGHT, fill='none', expand=True)
    root.after(10000, congratScreen)
     

def congratScreen():
    global congrat, selection, today
    congrat = tk.Tk()
    congrat.title('Congratulations')
    congrat.geometry('{}x{}'.format(congrat.winfo_screenwidth(), congrat.winfo_screenheight()))

    # Creating the two frames: top and bottom
    topframe = Frame(congrat)
    topframe.pack(side=TOP, fill='none')
    bottomframe = Frame(congrat)
    bottomframe.pack(side=BOTTOM, fill='none', expand=True)
    
    message = tk.Label(topframe, text='Would you like to make another order?',font=('TkDefaultFont', 18))
    message.pack()
    
    yesbtn = Button(congrat, text='Yes', bd=5, command=lambda: [congrat.destroy(), welcomeScr()], font=('TkDefaultFont', 18))
    nobtn = Button(congrat, text='No', bd=5,command=lambda: [congrat.destroy()], font=('TkDefaultFont', 18))
    yesbtn.pack()
    nobtn.pack()

    message2 = tk.Label(bottomframe, text='OPEN ORDERS',font=('TkDefaultFont', 18))
    message2.pack()


    
    response = get_neworders()

    #table = ttk.Treeview(lframe)
    columns = ('Symbol', 'Quantity', 'Side', 'Status')
    table = ttk.Treeview(bottomframe, columns=columns, show='headings')
    #table['columns'] = ('Symbol', 'Quantity', 'Side', 'Status')
    table.heading('Symbol', text='Symbol')
    table.heading('Quantity', text='Quantity')
    table.heading('Side', text='Side')
    table.heading('Status', text='Status')


    # symbol, qty, side, status
    for order in response:
        symbol = order['symbol']
        qty = order['qty']
        side = order['side']
        status = order['status']
        table.insert('', 'end', values=(symbol, qty, side, status))

    table.pack()
    root.destroy()

    #select.destroy()

def welcomeScr():
    welcome = tk.Tk()
    welcome.title('Profit Prophets - Alpaca Trading API')
    welcome.state('zoomed')
    image = Image.open('Profit Prophets.jpg')
    image = ImageTk.PhotoImage(image)

    top = Frame(welcome)
    top.pack(side=TOP)
    left = Frame(welcome)
    left.pack(side=LEFT)
    right = Frame(welcome)
    right.pack(side=RIGHT)

    image_label = tk.Label(top, image=image)
    image_label.pack()

    # activate_bot, orderingGui, welcome.destroy
    buyBtn = Button(left, text='BUY Stocks', bd='5', command=lambda:[orderingGUI(), welcome.destroy(), activate_bot()],font=('TkDefaultFont', 18))
    buyBtn.pack(pady=40)

    btn_deactivate = Button(left, text='SELL Stocks', bd='5', command=lambda:[deactivate_bot(), congratScreen()], font=('TkDefaultFont', 18))
    btn_deactivate.pack(pady=40)


    welcome.title('Profit Prophets - Order Table')
    welcome.geometry('{}x{}'.format(welcome.winfo_screenwidth(), welcome.winfo_screenheight()))

    # Table to list orders
    response = get_closedorders()

    #table = ttk.Treeview(lframe)
    columns = ('Symbol', 'Quantity', 'Side', 'Status')
    table = ttk.Treeview(welcome, columns=columns, show='headings')
    #table['columns'] = ('Symbol', 'Quantity', 'Side', 'Status')
    table.heading('Symbol', text='Symbol')
    table.heading('Quantity', text='Quantity')
    table.heading('Side', text='Side')
    table.heading('Status', text='Status')


    # symbol, qty, side, status
    for order in response:
        symbol = order['symbol']
        qty = order['qty']
        side = order['side']
        status = order['status']
        table.insert('', 'end', values=(symbol, qty, side, status))

    table.pack()


# Welcome screen
welcome = tk.Tk()
welcome.title('Profit Prophets - Alpaca Trading API')
welcome.state('zoomed')
image = Image.open('Profit Prophets.jpg')
image = ImageTk.PhotoImage(image)

top = Frame(welcome)
top.pack(side=TOP)
left = Frame(welcome)
left.pack(side=LEFT)
right = Frame(welcome)
right.pack(side=RIGHT)

image_label = tk.Label(top, image=image)
image_label.pack()


buyBtn = Button(left, text='BUY Stocks', bd='5', command=lambda:[orderingGUI(), welcome.destroy(), activate_bot()],font=('TkDefaultFont', 18))
buyBtn.pack(pady=40)

btn_deactivate = Button(left, text='SELL Stocks', bd='5', command=lambda:[deactivate_bot(), congratScreen()], font=('TkDefaultFont', 18))
btn_deactivate.pack(pady=40)


welcome.title('Profit Prophets - Order Table')
welcome.geometry('{}x{}'.format(welcome.winfo_screenwidth(), welcome.winfo_screenheight()))

# Table to list orders
response = get_closedorders()

#table = ttk.Treeview(lframe)
columns = ('Symbol', 'Quantity', 'Side', 'Status')
table = ttk.Treeview(welcome, columns=columns, show='headings')
#table['columns'] = ('Symbol', 'Quantity', 'Side', 'Status')
table.heading('Symbol', text='Symbol')
table.heading('Quantity', text='Quantity')
table.heading('Side', text='Side')
table.heading('Status', text='Status')


# symbol, qty, side, status
#for order in response:
 #   symbol = order['symbol']
  #  qty = order['qty']
   # side = order['side']
    #status = order['status']
    #table.insert('', 'end', values=(symbol, qty, side, status))

table.pack()

# Calling the GUI
#mainWindow()
#orderingGUI()

welcome.mainloop()
#root.mainloop()




'''
def price_increased(current_price, previous_price):
    return current_price > previous_price

def price_decreased(current_price, previous_price):
    return current_price < previous_price

previous_price = {}
'''

'''
# Function to sell all stocks
def sell_all_stocks():
    orders = get_orders()
    current_time = time.localtime()
    for order in orders:
        symbol = order['symbol']
        price = order['price']
        if symbol not in previous_price:
            previous_price[symbol] = price
            continue

        price_change = (price - previous_price[symbol]) / previous_price[symbol] * 100
        if price_change >= 1:
            create_order(symbol=order['symbol'], qty=order['qty'], side='sell', type='market', time_in_force='day')
            previous_price[symbol] = price
        elif price_change <= -1:
            create_order(symbol=order['symbol'], qty=order['qty'], side='sell', type='market', time_in_force='day')
            previous_price[symbol] = price
        elif current_time.tm_hour == 15  and current_time.tm_min == 55:
            create_order(symbol=order['symbol'], qty=order['qty'], side='sell', type='market', time_in_force='day')
        deactivate_bot()
'''

'''
# DOESNT WORK YET
# Function to monitor stock prices and adjust strategies
def monitor_stock_prices():
    while True:
        if is_trading_hours():
            # Implement your monitoring and strategy adjustment logic here
            pass
        else:
            break
        time.sleep(60)
'''




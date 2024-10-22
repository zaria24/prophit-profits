#this version update is supposed to update the amount of cash user has 

import requests
import json
from config import *  # config file
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import tkinter.ttk as ttk
import time
import threading

BASE_URL = 'https://paper-api.alpaca.markets'
ACCOUNT_URL = f'{BASE_URL}/v2/account'
ORDERS_URL = f'{BASE_URL}/v2/orders'
ALL_ORDERS = f'{ORDERS_URL}?status=all'
CLOSED_ORDERS = f'{ORDERS_URL}?status=closed'
NEW_ORDERS = f'{ORDERS_URL}?status=filled'

# Stock trade price URLs
STOCK_URLS = {
    'AAPL': 'https://data.alpaca.markets/v2/stocks/AAPL/trades/latest?feed=iex',
    'TSLA': 'https://data.alpaca.markets/v2/stocks/TSLA/trades/latest?feed=iex',
    'AMZN': 'https://data.alpaca.markets/v2/stocks/AMZN/trades/latest?feed=iex',
    'MSFT': 'https://data.alpaca.markets/v2/stocks/MSFT/trades/latest?feed=iex',
    'META': 'https://data.alpaca.markets/v2/stocks/META/trades/latest?feed=iex',
    'GOOG': 'https://data.alpaca.markets/v2/stocks/GOOG/trades/latest?feed=iex',
}

HEADERS = {
    'APCA-API-KEY-ID': API_KEY,
    'APCA-API-SECRET-KEY': SECRET_KEY
}


def get_account():
    r = requests.get(ACCOUNT_URL, headers=HEADERS)
    return json.loads(r.content)


def get_cash():
    r = requests.get(ACCOUNT_URL, headers=HEADERS)
    response = json.loads(r.content)
    return response['cash']


def get_tradePrice(stock):
    r = requests.get(stock, headers=HEADERS)
    response = json.loads(r.content)
    return response['trade']['p']


def create_order(symbol, qty, side, order_type='market', time_in_force='day'):
    data = {
        'symbol': symbol,
        'qty': qty,
        'side': side,
        'type': order_type,
        'time_in_force': time_in_force
    }
    r = requests.post(ORDERS_URL, json=data, headers=HEADERS)
    response = json.loads(r.content)
    print(response)
    
#new code to update cash amount
    if r.status_code == 200:
        print (f"Order for {side} {symbol} placed successfully")
        update_cash_label()
    else: 
        print (f"Error placing order: {response}")

def update_cash_label():
    cash = get_cash()
    cash_label.config(text=f"Available Cash: ${float(cash):,.2f}")

def get_orders():
    r = requests.get(ALL_ORDERS, headers=HEADERS)
    return json.loads(r.content)


def is_trading_hours():
    current_time = time.localtime()
    return 9 <= current_time.tm_hour < 16


def activate_bot():
    if is_trading_hours():
        print("Activating trading bot...")
        buy_stocks()
        schedule_sell_before_market_close()
    else:
        print("Market is closed. Cannot activate bot.")


def deactivate_bot():
    if is_trading_hours():
        sell_all_stocks()
    else:
        print("Market is closed. Bot is already deactivated.")


def buy_stocks():
    stocks_to_buy = ['AAPL', 'TSLA', 'AMZN', 'GOOG', 'META', 'MSFT']
    for stock in stocks_to_buy:
        create_order(symbol=stock, qty=1, side='buy')


def sell_all_stocks():
    stocks_to_sell = ['AAPL', 'TSLA', 'AMZN', 'GOOG', 'META', 'MSFT']
    for stock in stocks_to_sell:
        create_order(symbol=stock, qty=1, side='sell')


def schedule_sell_before_market_close():
    while True:
        current_time = time.localtime()
        if current_time.tm_hour == 14 and current_time.tm_min == 52:
            sell_all_stocks()
            break
        else:
            time.sleep(60)


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


def sell_stocks_if_price_change():
    orders = get_orders()
    current_time = time.localtime()
    for order in orders:
        symbol = order['symbol']
        current_price = get_current_price(symbol)
        purchase_price = get_purchase_price(symbol)
        percentage_change = ((current_price - purchase_price) / purchase_price) * 100
        if abs(percentage_change) >= 0.5:
            create_order(symbol=symbol, qty=order['qty'], side='sell')
        elif current_time.tm_hour == 10 and current_time.tm_min == 1:
            create_order(symbol=symbol, qty=order['qty'], side='sell')
    deactivate_bot()


def activate_range_trading():
    threading.Thread(target=range_trading).start()


def range_trading():
    PRICE_RANGES = {
        'AAPL': {'low': 130, 'high': 150},
        'TSLA': {'low': 600, 'high': 700},
        'AMZN': {'low': 3200, 'high': 3400},
        'MSFT': {'low': 290, 'high': 310},
        'META': {'low': 320, 'high': 350},
        'GOOG': {'low': 2800, 'high': 3000},
    }

    results = [] #intializes list
    for stock, price_range in PRICE_RANGES.items():
        current_price = get_tradePrice(STOCK_URLS[stock])
        if current_price is None:
            print("None")
            results.append((stock, "N/A", price_range['low'], price_range['high'], "No action")) #appends list
            continue

        if current_price <= price_range['low']:
            create_order(stock, qty=1, side='buy')
            print("bought")
            results.append((stock, current_price, price_range['low'], price_range['high'], "Bought")) #appends list

        elif current_price >= price_range['high']:
            create_order(stock, qty=1, side='sell')
            print("sold")
            results.append((stock, current_price, price_range['low'], price_range['high'], "Sold")) #appends list
        else:
            print("None")
            results.append((stock, current_price, price_range['low'], price_range['high'], "No action")) #appends list

    print("Range Trading Results:", results) #prints list
    return results #ensures there is a results table printed

def show_results_table(results, title):
    # Placeholder for a function to show results in a GUI or console
    print(title)
    for result in results:
        print(result)


def mainWindow():
    welcome.destroy()
    orderingGUI()

# Adding a function to show the Bound Trading Screen
def range_trading_screen():
    # Create a new window for the Bound Trading
    range_window = tk.Toplevel(root)
    range_window.title('Range Trading')
    range_window.geometry('800x600')

    # Create a label for the screen title
    range_label = tk.Label(range_window, text="Range Trading Results", font=('TkDefaultFont', 18, 'bold'))
    range_label.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

    # Call range trading and capture the results
    results = range_trading()
    print(results)


 # Display results in a table format
    for idx, (stock, current_price, low_range, high_range, action) in enumerate(results, start=2):
        stock_label = tk.Label(range_window, text=stock, font=('TkDefaultFont', 12))
        stock_label.grid(row=idx, column=0, padx=10, pady=5)

        price_label = tk.Label(range_window, text=f"${current_price:.2f}" if current_price != "N/A" else "N/A", font=('TkDefaultFont', 12))
        price_label.grid(row=idx, column=1, padx=10, pady=5)

        low_range_label = tk.Label(range_window, text=f"${low_range}", font=('TkDefaultFont', 12))
        low_range_label.grid(row=idx, column=2, padx=10, pady=5)

        high_range_label = tk.Label(range_window, text=f"${high_range}", font=('TkDefaultFont', 12))
        high_range_label.grid(row=idx, column=3, padx=10, pady=5)

        action_label = tk.Label(range_window, text=action, font=('TkDefaultFont', 12, 'bold'))
        action_label.grid(row=idx, column=4, padx=10, pady=5)



def orderingGUI():
    global root, cash_label
    root = tk.Tk()
    root.geometry('{}x{}'.format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.title('Profit Prophets - Ordering Stocks')

    cash_label = tk.Label(root, text="Available Cash: $10000", font=('TkDefaultFont', 18, 'bold'))
    cash_label.grid(column=0, row=0, padx=10, pady=10)

    update_cash_label() #updating amount of cash

    stock_label = tk.Label(root, text="Stock Prices", font=('TkDefaultFont', 18, 'bold'))
    stock_label.grid(column=0, row=1, padx=10, pady=10)

    for i, stock in enumerate(STOCK_URLS.keys()):
        current_price = get_tradePrice(STOCK_URLS[stock])
        stock_info = f"{stock}: ${current_price}"
        stock_price_label = tk.Label(root, text=stock_info, font=('TkDefaultFont', 14))
        stock_price_label.grid(column=0, row=2 + i, padx=10, pady=5)

        # Buy and Sell buttons
        buy_btn = Button(root, text=f'Buy {stock}', bd='5', command=lambda s=stock: create_order(s, qty=1, side='buy'), font=('TkDefaultFont', 14))
        buy_btn.grid(column=1, row=2 + i, padx=5, pady=5)

        sell_btn = Button(root, text=f'Sell {stock}', bd='5', command=lambda s=stock: create_order(s, qty=1, side='sell'), font=('TkDefaultFont', 14))  #command=showLabel (uncomment when func show label is uncommented in line 263)
        sell_btn.grid(column=2, row=2 + i, padx=5, pady=5)

    # Button for Bound Trading
    range_trade_btn = tk.Button(root, text='RANGE TRADE', bd='5', command=range_trading_screen, font=('TkDefaultFont', 18))
    range_trade_btn.grid(column=0, row=10, padx=10, pady=10)

    root.mainloop()


#show label func
#def showLabel():
    
    #current_price = get_tradePrice(STOCK_URLS[stock])
    #if 
        #BSlabel = tk.Label(root, text= "Stock Sold {stock}", font=('TkDefaultFont', 20, 'bold'))
        #BSlabel.grid(column=20, row=20, padx=50, pady=80)
    #elif text=f'Buy'
        #BSlabel = tk.Label(root, text= "Stock Sold", font=('TkDefaultFont', 20, 'bold'))
        #BSlabel.grid(column=20, row=20, padx=50, pady=80)



# Welcome screen
welcome = tk.Tk()
welcome.title('Profit Prophets - Alpaca Trading API')
welcome.state('zoomed')
image = Image.open('Profit Prophets.jpg')
image = ImageTk.PhotoImage(image)

# Set up frames for layout
top_frame = Frame(welcome)
top_frame.pack(side=TOP)
left_frame = Frame(welcome)
left_frame.pack(side=LEFT)

# Load logo
try:
    image = Image.open('Profit Prophets.jpg')
    image = ImageTk.PhotoImage(image)
    image_label = tk.Label(top_frame, image=image)
    image_label.pack(pady=20)
except FileNotFoundError:
    print("Image file not found. Skipping logo display.")

# Add buttons
activate_button = Button(left_frame, text="Activate Trading Bot", command=activate_bot, font=('TkDefaultFont', 18))
activate_button.pack(pady=10)

deactivate_button = Button(left_frame, text="Deactivate Trading Bot", command=deactivate_bot, font=('TkDefaultFont', 18))
deactivate_button.pack(pady=10)

ordering_button = Button(left_frame, text="Order Stocks", command=mainWindow, font=('TkDefaultFont', 18))
ordering_button.pack(pady=10)

welcome.mainloop()

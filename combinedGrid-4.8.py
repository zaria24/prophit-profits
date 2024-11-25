import requests
import json
from config import *  # config file
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import tkinter.ttk as ttk
import time
import threading
import sys
import config
from tkinter import simpledialog #for user input

BASE_URL = 'https://paper-api.alpaca.markets'
ACCOUNT_URL = f'{BASE_URL}/v2/account'
ORDERS_URL = f'{BASE_URL}/v2/orders'
ALL_ORDERS = f'{ORDERS_URL}?status=all'
CLOSED_ORDERS = f'{ORDERS_URL}?status=closed'
NEW_ORDERS = f'{ORDERS_URL}?status=filled'

amountstock = 100000
amountStockString = "The final amount is:"


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

#PP- this function allows the cash label to only show a rounded verison
def round_cash_decimal(new_value):
    global amountstock
    amountstock = round(amountstock, 2)

def update_cash_label():
    round_cash_decimal(amountstock)
    cash_label.config(text="Available Cash: $" + str(amountstock))

#Stock trade price updates every 30seconds
#stock_price = get_tradePrice(STOCK_URLS[HEADERS])

def create_order(symbol, qty, side, order_type='market', time_in_force='day'):
    global amountstock

    # Get the current price of the stock
    stock_price = get_tradePrice(STOCK_URLS[symbol])

    if side == 'buy':
        total_cost = stock_price * qty
        if amountstock >= total_cost:  # Check if there's enough cash to make the purchase
            amountstock -= total_cost  # Deduct the cost from available cash
            update_cash_label()  # Update the displayed cash
            print(f"Bought {qty} of {symbol} at ${stock_price} each. Remaining cash: ${amountstock}")
        else:
            print("Not enough cash to complete the purchase!")
    
    elif side == 'sell':
        total_sale = stock_price * qty
        amountstock += total_sale  # Add the proceeds from the sale to available cash
        update_cash_label()  # Update the displayed cash after selling
        print(f"Sold {qty} of {symbol} at ${stock_price} each. New cash balance: ${amountstock}")

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

    sys.exit()

   

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
            time.sleep(60) #allows prog to check time in one min before selling


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
    HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY' : SECRET_KEY}
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

#update the range values for each stock
def change_ranges(stock, current_value, label):

    try:
        #ask user to insert for specfic stock a low or high value
        user_input = input(f"Enter the new {label} range for {stock} (current: {current_value}): ")
        return int(user_input) if user_input else current_value
    except ValueError:
        print(f"Invalid input. Keeping the current value {current_value}.")
    return current_value

    


def range_trading():


    # Default variables for stock ranges
    aapl_low, aapl_high = 130, 150
    tsla_low, tsla_high = 600, 700
    amzn_low, amzn_high = 3200, 3400
    msft_low, msft_high = 290, 310
    meta_low, meta_high = 320, 350
    goog_low, goog_high = 2800, 3000

    PRICE_RANGE = {
        #'stock_price_label': {'low':low_range_label, 'high': high_range_label},
        'AAPL': {'low': aapl_low, 'high': aapl_high},
        'TSLA': {'low': tsla_low, 'high': tsla_high},
        'AMZN': {'low': amzn_low, 'high': amzn_high},
        'MSFT': {'low': msft_low, 'high': msft_high},
        'META': {'low': meta_low, 'high': meta_high},
        'GOOG': {'low': goog_low, 'high': goog_high},
    }

    #updates stock prices for low and high
    for stock, ranges in PRICE_RANGE.items():
        ranges['low'] = change_ranges(stock, ranges['low'], "low")
        ranges['high'] = change_ranges(stock, ranges['high'], "high")


    results = [] #intializes list
    for stock, price_range in PRICE_RANGE.items():
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


# Adding a function to show the INTIAL Range Trading Screen
def range_trading_screen(): 
    # Create a new window for the Range Trading
    range_trade_window = tk.Toplevel(root)
    range_trade_window.title('Range Trading')
    range_trade_window.geometry('800x600')

#PRICE_RANGE = {
        #'stock_price_label': {'low':low_range_label, 'high': high_range_label},
#       'AAPL': {'low': aapl_low, 'high': aapl_high},
#      'TSLA': {'low': tsla_low, 'high': tsla_high},
#     'AMZN': {'low': amzn_low, 'high': amzn_high},
#        'MSFT': {'low': msft_low, 'high': msft_high},
#        'META': {'low': meta_low, 'high': meta_high},
#        'GOOG': {'low': goog_low, 'high': goog_high},
#    }

# 
#entries = {}
#for idx, (stock, ranges) in enumerate(PRICE_RANGE.items(), start = 1):
#    tk.Label(range_trade_window, text = stock, font=('TkDefaultFont', 12, 'bold')).grid(row=idx, column=0, padx=10, pady=5))




    # Create a label for the screen title
    range_label = tk.Label(range_trade_window, text="Range Trading", font=('TkDefaultFont', 18, 'bold'))
    range_label.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

    # Button for Range Trading Results
    range_trade_results_btn = tk.Button(range_trade_window, text='RANGE TRADE RESULTS', bd='5', command=range_results_screen, font=('TkDefaultFont', 18))
    range_trade_results_btn.grid(column=0, row=10, padx=10, pady=100)

    results = range_trading()
    print(results)

    global stock_price_label, low_range_label, high_range_label
    stock_price_label = tk.Label(range_trade_window, text="Stock Price", font=('TkDefaultFont', 12, 'bold'))
    stock_price_label.grid(row=0, column=1, padx=10, pady=5)

    low_range_label = tk.Label(range_trade_window, text="Low Range", font=('TkDefaultFont', 12, 'bold'))
    low_range_label.grid(row=0, column=2, padx=10, pady=5)

    high_range_label = tk.Label(range_trade_window, text="High Range", font=('TkDefaultFont', 12, 'bold'))
    high_range_label.grid(row=0, column=3, padx=10, pady=5)
    
    # Column headers
    #headers = ["Stock", "Current Price", "Low Range", "High Range", "Action"]
    #for col, header in enumerate(headers):
        #header_label = tk.Label(range_trade_window, text=header, font=('TkDefaultFont', 12, 'bold'))
        #header_label.grid(row=1, column=col, padx=10, pady=5)


    # Display results in a table format
    for idx, (stock, current_price, low_range, high_range, action) in enumerate(results, start=2):
            label = tk.Label(range_trade_window, text=stock, font=('TkDefaultFont', 12))
            stock_label = tk.Label(range_trade_window, text=stock, font=('TkDefaultFont', 12))
            stock_label.grid(row=idx, column=0, padx=10, pady=5)

            price_label = tk.Label(range_trade_window, text=f"${current_price:.2f}" if current_price != "N/A" else "N/A", font=('TkDefaultFont', 12))
            price_label.grid(row=idx, column=1, padx=10, pady=5)

            low_range = tk.Label(range_trade_window, text=f"${low_range}", font=('TkDefaultFont', 12))
            low_range.grid(row=idx, column=2, padx=10, pady=5)

            high_range = tk.Label(range_trade_window, text=f"${high_range}", font=('TkDefaultFont', 12))
            high_range.grid(row=idx, column=3, padx=10, pady=5)

        #action_label = tk.Label(range_trade_window, text=action, font=('TkDefaultFont', 12, 'bold'))
        #action_label.grid(row=idx, column=4, padx=10, pady=5)


# Adding a function to show the Range Results Screen
def range_results_screen(): 
    # Create a new window for the Range Trading
    range_window = tk.Toplevel(root)
    range_window.title('Range Trading Results')
    range_window.geometry('800x600')

    # Create a label for the screen title
    range_label = tk.Label(range_window, text="Range Trading Results", font=('TkDefaultFont', 18, 'bold'))
    range_label.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

    # Call range trading and capture the results
    results = range_trading()
    print(results)


 # Display results in a table format
 
    for idx, (stock, current_price, low_range, high_range, action) in enumerate(results, start=2):
        label = tk.Label(range_window, text=stock, font=('TkDefaultFont', 12))
        stock_label = tk.Label(range_window, text=stock, font=('TkDefaultFont', 12))
        stock_label.grid(row=idx, column=0, padx=10, pady=5)

        price_label = tk.Label(range_window, text=f"${current_price:.2f}" if current_price != "N/A" else "N/A", font=('TkDefaultFont', 12))
        price_label.grid(row=idx, column=1, padx=10, pady=5)

        low_range = tk.Label(range_window, text=f"${low_range}", font=('TkDefaultFont', 12))
        low_range.grid(row=idx, column=2, padx=10, pady=5)

        high_range = tk.Label(range_window, text=f"${high_range}", font=('TkDefaultFont', 12))
        high_range.grid(row=idx, column=3, padx=10, pady=5)

        action_label = tk.Label(range_window, text=action, font=('TkDefaultFont', 12, 'bold'))
        action_label.grid(row=idx, column=4, padx=10, pady=5)



def orderingGUI():
    global root, cash_label
    root = tk.Tk()
    root.geometry('{}x{}'.format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.title('Profit Prophets - Ordering Stocks')

    # Label to show available cash
    cash_label = tk.Label(root, text="Available Cash: $" + str(amountstock), font=('TkDefaultFont', 18, 'bold'))
    cash_label.grid(column=0, row=0, padx=10, pady=10)

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

        sell_btn = Button(root, text=f'Sell {stock}', bd='5', command=lambda s=stock: create_order(s, qty=1, side='sell'), font=('TkDefaultFont', 14))
        sell_btn.grid(column=2, row=2 + i, padx=5, pady=5)
  
        # Button for Range Trading
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

# Define both file paths
#user_directory_path = r'"E:\Profit Prophets - 4.1\Profit Prophets.jpg"'
flash_drive_path = 'E:\Profit Prophets - 4.1\Profit Prophets.jpg'

import os
from PIL import Image

# Get the directory of the currently running script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the image file using the current directory
image_path = os.path.join(current_directory, 'Profit Prophets.jpg')

# Open the image
image = Image.open(image_path)

 

#try:
    #image = Image.open(flash_drive_path)
    # Do something with the image if it opens successfully
   # image.show()
#except FileNotFoundError:
    #print("Error: The file was not found. Please check the file path and try again.")
#except Exception as e:
    #print(f"An unexpected error occurred: {e}")

#prev image open it was on line 305
#image = Image.open(r'E:\Profit Prophets - 4.1\Profit Prophets.jpg') changed to flash drive
#image = ImageTk.PhotoImage(image)


# Set up frames for layout
top_frame = Frame(welcome)
top_frame.pack(side=TOP)
left_frame = Frame(welcome)
left_frame.pack(side=LEFT)

# Load logo
try:
    #image = Image.open(r'E:\Profit Prophets - 4.1\Profit Prophets.jpg') changed to flash drive
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
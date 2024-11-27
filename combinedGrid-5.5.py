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
global stock


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

      
def range_trading():

    #making low and high stocks global
    global aapl_low, aapl_high, tsla_low, tsla_high, amzn_low, amzn_high, msft_low, msft_high, meta_low, meta_high, goog_low, goog_high

    # Default variables for stock ranges
    aapl_low, aapl_high = 130, 150
    tsla_low, tsla_high = 600, 700
    amzn_low, amzn_high = 3200, 3400
    msft_low, msft_high = 290, 310
    meta_low, meta_high = 320, 350
    goog_low, goog_high = 2800, 3000

    global PRICE_RANGE
    PRICE_RANGE = {
        #'stock_price_label': {'low':low_range_label, 'high': high_range_label},
        'AAPL': {'low': aapl_low, 'high': aapl_high},
        'AMZN': {'low': amzn_low, 'high': amzn_high},
        'MSFT': {'low': msft_low, 'high': msft_high},
        'META': {'low': meta_low, 'high': meta_high},
        'GOOG': {'low': goog_low, 'high': goog_high},
    }


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

    

# def show_results_table(results):
#     # Placeholder for a function to show results in a GUI or console
#     for result in results:
#         print(result)


def mainWindow():
    #welcome.destroy() #closes the welcome screen

    def login_screen():
        def validate_login():
            username = username_entry.get()
            password = password_entry.get()
        
            # Fake credentials for demonstration purposes
            fake_username = "csc_user"
            fake_password = "csc_password" 

            if username == fake_username and password == fake_password:
                login_window.destroy()
                orderingGUI()  # Proceed to the main application
            else:
                error_label.config(text="Invalid username or password!", fg="red")

        # Create the login window
        login_window = tk.Tk()
        login_window.title("Login - Prophet Profits")
        login_window.geometry("600x500")

        tk.Label(login_window, text="Login", font=('TkDefaultFont', 18, 'bold')).pack(pady=10)
        tk.Label(login_window, text="Username:").pack(pady=5)
        username_entry = tk.Entry(login_window, width=30)
        username_entry.pack(pady=5)
        tk.Label(login_window, text="Password:").pack(pady=5)
        password_entry = tk.Entry(login_window, width=30, show="*")
        password_entry.pack(pady=5)

        error_label = tk.Label(login_window, text="")
        error_label.pack(pady=5)

        login_button = tk.Button(login_window, text="Login", command=validate_login)
        login_button.pack(pady=10)

        login_window.mainloop()

    login_screen()
    


# Adding a function to show the INTIAL Range Trading Screen
# R A N G E   S C R E E N  #1
def range_trading_screen(): 
    # Create a new window for the Range Trading
    global range_trade_window
    range_trade_window = tk.Toplevel(root)
    range_trade_window.title('Range Trading')
    range_trade_window.geometry('1000x600')
    range_trade_window.configure(bg = "bisque")

    # Create a label for the screen title
    range_label = tk.Label(range_trade_window, text="Range Trading", font=('Georgia', 18, 'bold'), bg = "bisque")
    range_label.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

    # Button for Range Trading Results
    range_trade_results_btn = tk.Button(range_trade_window, text='RANGE TRADE RESULTS', bd='5', command = range_results_screen, font=('Georgia', 18))
    range_trade_results_btn.grid(column=20, row=10, padx=10, pady=100)

    # Back button to ordering gui
    back_btn = tk.Button(range_trade_window, text='BACK', bd='5', command = lambda: [range_trade_window.destroy()], font=('Georgia', 18))
    back_btn.grid(column=0, row=10, padx=10, pady=100)

    #results
    results = range_trading()
    print(results)

    global stock_price_label, low_range_label, high_range_label
    
    # Column headers
    headers = ["Stock", "Current Price", "Low Range", "High Range"]
    for col, header in enumerate(headers):
        header_label = tk.Label(range_trade_window, text=header, font=('Georgia', 12, 'bold'), bg = "bisque")
        header_label.grid(row=1, column=col, padx=10, pady=5)

    #entry and label for stockpric einput
    global entry, label
    entry = tk.Entry(range_trade_window)
    label = tk.Label(range_trade_window, text="$0.00", font=('Georgia', 14))
    



    # Display results in a table format
    for idx, (stock, current_price, low_range, high_range, action) in enumerate(results, start=2):

            # Stock column
            label = tk.Label(range_trade_window, text=stock, font=('Georgia', 12), bg = "bisque")
            stock_label = tk.Label(range_trade_window, text=stock, font=('Georgia', 12), bg = "bisque")
            stock_label.grid(row=idx, column=0, padx=10, pady=5)


            # Price column
            price_label = tk.Label(range_trade_window, text=f"${current_price:.2f}" if current_price != "N/A" else "N/A", font=('Georgia', 12), bg = "bisque")
            price_label.grid(row=idx, column=1, padx=10, pady=5)

            # Low column
            low_range_label = tk.Label(range_trade_window, text=f"${low_range}", font=('Georgia', 12), bg = "bisque")
            low_range_label.grid(row=idx, column=2, padx=10, pady=5)

            low_entry = tk.Entry(range_trade_window, font=("Georgia", 14))
            low_entry.grid_remove()  # Hide the entry widget initially

            #low_range.bind("<Button-1>", lambda event, entry=low_entry, label=low_range, stock=stock: start_edit(event, entry, label, stock, 'low'))
            low_range_label.bind("<Button-1>", lambda event, entry=low_entry, label=low_range_label, stock=stock: start_edit(event, entry, label, range_trade_window, stock, 'low'))
            
            # High column
            high_range_label = tk.Label(range_trade_window, text=f"${high_range}", font=('Georgia', 12), bg = "bisque")
            high_range_label.grid(row=idx, column=3, padx=10, pady=5)
            
            high_entry = tk.Entry(range_trade_window, font=("Georgia", 14))
            high_entry.grid_remove()  # Hide the entry widget initially

            #high_range.bind("<Button-1>", lambda event, entry=high_entry, label=high_range, stock=stock: start_edit(event, entry, label, stock, 'high'))
            # Pass variables explicitly to lambda
            high_range_label.bind("<Button-1>", lambda event, entry=high_entry, label=high_range_label, stock=stock: start_edit(event, entry, label, range_trade_window, stock, 'high'))
            

        
def start_edit(event, entry, label, window, stock, range_type):
        
        entry_var = tk.StringVar(value=label.cget("text"))
        entry.config(textvariable=entry_var)
        entry.grid(row=label.grid_info()['row'], column=label.grid_info()['column'])  # Show the entry widget
        label.grid_remove()  # Hide the label
        entry.focus_set()  # Focus the entry for editing

        
        def finish_edit(entry, label, window, stock, range_type):
            #global PRICE_RANGE
            global new_value, transfer_value
            new_value = entry.get()  # Get the new value
            if new_value.isdigit() or (new_value.replace('.', '', 1).isdigit() and new_value.count('.') < 2):  # Validate input
                label.config(text=f"${new_value}")  # Update the label's text
                
                # Update the global stock price or range values based on what was edited
                
                if range_type == "low":
                    PRICE_RANGE[stock]['low'] = float(new_value)  # Update low range for the stock
                elif range_type == "high":
                    PRICE_RANGE[stock]['high'] = float(new_value)  # Update high range for the stock
                #update_results_table()
            
            
            transfer_value = new_value
                
            entry.grid_remove()  # Hide the entry widget
            label.grid()  # Show the label again
            #update_results_table()
            #window.focus_set()
            update_results_table()
            return new_value
        entry.bind("<Return>", lambda event: (finish_edit(entry, label, range_results_screen, stock, range_type)))
        #update_results_table()
       
def refresh_canvas_chart(results):
    global chart_canvas

    # Clear the canvas
    chart_canvas.delete("all")

    # Dimensions for the table
    row_height = 30
    col_widths = [100, 150, 150, 150, 150]  # Widths for Stock, Current Price, Low, High, Action
    x_start = 10  # Starting x-coordinate
    y_start = 10  # Starting y-coordinate

    # Draw headers
    headers = ["Stock", "Current Price", "Low Range", "High Range", "Action"]
    for col_index, header in enumerate(headers):
        chart_canvas.create_text(
            x_start + sum(col_widths[:col_index]) + col_widths[col_index] // 2,
            y_start,
            text=header,
            font=("Arial", 12, "bold"),
            anchor="center"
        )

    # Horizontal line for headers
    chart_canvas.create_line(
        x_start, y_start + 15,
        x_start + sum(col_widths), y_start + 15,
        fill="black", width=2
    )

    # Draw rows for each stock
    for row_index, (stock, current_price, low_range, high_range, action) in enumerate(results):
        y_pos = y_start + (row_index + 1) * row_height

        # Stock name
        chart_canvas.create_text(
            x_start + col_widths[0] // 2,
            y_pos,
            text=stock,
            font=("Arial", 10),
            anchor="center"
        )

        # Current price
        chart_canvas.create_text(
            x_start + col_widths[0] + col_widths[1] // 2,
            y_pos,
            text=f"${current_price:.2f}" if current_price != "N/A" else "N/A",
            font=("Arial", 10),
            anchor="center"
        )

        # Low range
        chart_canvas.create_text(
            x_start + sum(col_widths[:2]) + col_widths[2] // 2,
            y_pos,
            text=f"${low_range:.2f}",
            font=("Arial", 10),
            anchor="center"
        )

        # High range
        chart_canvas.create_text(
            x_start + sum(col_widths[:3]) + col_widths[3] // 2,
            y_pos,
            text=f"${high_range:.2f}",
            font=("Arial", 10),
            anchor="center"
        )

        # Action
        chart_canvas.create_text(
            x_start + sum(col_widths[:4]) + col_widths[4] // 2,
            y_pos,
            text=action,
            font=("Arial", 10),
            anchor="center"
        )

    # Adjust the canvas scroll region to fit the content
    chart_canvas.config(scrollregion=chart_canvas.bbox("all"))



def update_results_table():

    global PRICE_RANGE

    # Calculate updated results
    results = []
    for stock, price_range in PRICE_RANGE.items():
        current_price = get_tradePrice(STOCK_URLS[stock])
        if current_price is None:
            results.append((stock, "N/A", price_range['low'], price_range['high'], "No action"))
            continue

        if current_price <= price_range['low']:
            results.append((stock, current_price, price_range['low'], price_range['high'], "Buy"))
        elif current_price >= price_range['high']:
            results.append((stock, current_price, price_range['low'], price_range['high'], "Sell"))
        else:
            results.append((stock, current_price, price_range['low'], price_range['high'], "Hold"))

    # Refresh the chart with the new results
    refresh_canvas_chart(results)

    return results

    # for stock, price_range in PRICE_RANGE.items():
    #     #current price of stock
    #     current_price = get_tradePrice(STOCK_URLS[stock])
    #     #price_range['low'] = float(new_value)
    #     #current_price = float(new_value)

                
    #     if current_price is None:
    #         print("None")
    #         results.append((stock, "N/A", price_range['low'], price_range['high'], "No action")) #appends list
    #         continue

    #     if current_price <= price_range['low']:
    #         create_order(stock, qty=1, side='buy')
    #         print("bought")
    #         results.append((stock, current_price, price_range['low'], price_range['high'], "Bought")) #appends list

    #     elif current_price >= price_range['high']:
    #         create_order(stock, qty=1, side='sell')
    #         print("sold")
    #         results.append((stock, current_price, price_range['low'], price_range['high'], "Sold")) #appends list
    #     else:
    #         print("None")
    #         results.append((stock, current_price, price_range['low'], price_range['high'], "No action")) #appends list

    # print("Range Trading Results:", results) #prints list
    # return results #ensures there is a results table printed




# Adding a function to show the Range Results Screen
def range_results_screen(): 
    global range_window, chart_canvas

    # Create the results window
    range_window = tk.Toplevel(root)
    range_window.title('Range Trading Results')
    range_window.geometry('800x600')
    range_window.configure(bg="bisque")

    # Create the Canvas for the chart
    chart_canvas = tk.Canvas(range_window, width=750, height=400, bg="white")
    chart_canvas.pack(pady=20)

    # Back button
    back_btn = tk.Button(range_window, text="BACK", command=range_window.destroy, font=('Georgia', 18, 'bold'))
    back_btn.pack(pady=10)

    # Update the chart initially
    update_results_table()

    # Create a label for the screen title
    range_label = tk.Label(range_window, text="Range Trading Results", font=('Georgia', 18, 'bold'), bg = "bisque")
    range_label.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

    # Back button to ordering gui
    back_btn = tk.Button(range_window, text='BACK', bd='5', command = lambda: [range_window.destroy()], font=('Georgia', 18))
    back_btn.grid(column=0, row=10, padx=10, pady=100)

    headers = ["Stock", "Current Price", "Low Range", "High Range", "Action"]
    for col, header in enumerate(headers):
        header_label = tk.Label(range_window, text=header, font=('Georgia', 12, 'bold'), bg = "bisque")
        header_label.grid(row=1, column=col, padx=10, pady=5)

#Display results in a table format
    results = update_results_table()
    print("LOOK AT THIS LOOK HERE-------")
    print(results)

    for idx, (stock, current_price, low_range, high_range, action) in enumerate(results, start=2):
        label = tk.Label(range_window, text=stock, font=('Georgia', 12), bg = "bisque")
        stock_label = tk.Label(range_window, text=stock, font=('Georgia', 12), bg = "bisque")
        stock_label.grid(row=idx, column=0, padx=10, pady=5)

        price_label = tk.Label(range_window, text=f"${current_price:.2f}" if current_price != "N/A" else "N/A", font=('Georgia', 12), bg = "bisque")
        price_label.grid(row=idx, column=1, padx=10, pady=5)

        low_range = tk.Label(range_window, text=f"${low_range}", font=('Georgia', 12), bg = "bisque")
        low_range.grid(row=idx, column=2, padx=10, pady=5)

        high_range = tk.Label(range_window, text=f"${high_range}", font=('Georgia', 12), bg = "bisque")
        high_range.grid(row=idx, column=3, padx=10, pady=5)

        action_label = tk.Label(range_window, text=action, font=('Georgia', 12, 'bold'), bg = "bisque")
        action_label.grid(row=idx, column=4, padx=10, pady=5)

    #Go back button to range trading screen
    back_btn = tk.Button(range_results_screen, text='Back', bd='5', command = lambda: [root.destroy(), range_trading_screen()], font=('Georgia', 18, 'bold'))
    back_btn.grid(column=0, row=500, padx=0, pady = 0)


def orderingGUI():
    global root, cash_label
    root = tk.Tk()
    root.geometry('{}x{}'.format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.title('Profit Prophets - Ordering Stocks')
    root.configure(bg = "light blue")

    # Label to show available cash
    cash_label = tk.Label(root, text="Available Cash: $" + str(amountstock), font=('Georgia', 18, 'bold'),fg = "black",bg = "light blue")
    cash_label.grid(column=1, row=0, padx=10, pady=10)

    stock_label = tk.Label(root, text="Stock Prices", font=('Georgia', 18, 'bold'),bg = "light blue")
    stock_label.grid(column=0, row=1, padx=10, pady=10)

    for i, stock in enumerate(STOCK_URLS.keys()):
        current_price = get_tradePrice(STOCK_URLS[stock])
        stock_info = f"{stock}: ${current_price}"
        stock_price_label = tk.Label(root, text=stock_info, font=('Georgia', 16), bg = "light blue")
        stock_price_label.grid(column=0, row=2 + i, padx=10, pady=5)

        # Buy and Sell buttons
        buy_btn = Button(root, text=f'Buy {stock}', bd='5', command=lambda s=stock: create_order(s, qty=1, side='buy'), font=('Georgia', 14), bg = "sea green")
        buy_btn.grid(column=1, row=2 + i, padx=5, pady=5)

        sell_btn = Button(root, text=f'Sell {stock}', bd='5', command=lambda s=stock: create_order(s, qty=1, side='sell'), font=('Georgia', 14), bg = "tomato")
        sell_btn.grid(column=2, row=2 + i, padx=5, pady=5)
  
        # Button for Range Trading
        range_trade_btn = tk.Button(root, text='RANGE TRADE', bd='5', command=range_trading_screen, font=('Georgia', 18, 'bold'))
        range_trade_btn.grid(column=0, row=10, padx=0, pady=20)

        # go back button for editting Range trading
        back_btn = tk.Button(root, text='BACK', bd='5', command = lambda: [root.destroy(), welcome()], font=('Georgia', 18, 'bold'))
        back_btn.grid(column=0, row=500, padx=0, pady = 0)
    root.mainloop()
# command = lambda: [root.destroy(), welcome()]

#show label func
#def showLabel():
    
    #current_price = get_tradePrice(STOCK_URLS[stock])
    #if 
        #BSlabel = tk.Label(root, text= "Stock Sold {stock}", font=('Georgia', 20, 'bold'))
        #BSlabel.grid(column=20, row=20, padx=50, pady=80)
    #elif text=f'Buy'
        #BSlabel = tk.Label(root, text= "Stock Sold", font=('Georgia', 20, 'bold'))
        #BSlabel.grid(column=20, row=20, padx=50, pady=80)



# Welcome screen
welcome = tk.Tk()
welcome.title('Profit Prophets - Alpaca Trading API')
welcome.state('zoomed')
welcome.configure(bg = "light blue")

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
left_frame.config(bg = "light blue")

# Load logo
try:
    #image = Image.open(r'E:\Profit Prophets - 4.1\Profit Prophets.jpg') changed to flash drive
    image = ImageTk.PhotoImage(image)
    image_label = tk.Label(top_frame, image=image,bg = "light blue")
    image_label.pack(pady=0)
except FileNotFoundError:
    print("Image file not found. Skipping logo display.")

# Add buttons
activate_button = Button(left_frame, text="Activate Trading Bot", command=activate_bot, font=('Georiga', 18, 'bold'))
activate_button.pack(pady=10)

deactivate_button = Button(left_frame, text="Deactivate Trading Bot", command=deactivate_bot, font=('Georgia', 18, 'bold'))
deactivate_button.pack(pady=10)

ordering_button = Button(left_frame, text="Order Stocks", command=mainWindow, font=('Georgia', 18, 'bold'))
ordering_button.pack(pady=10)

welcome.mainloop()
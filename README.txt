Profit Prophets: Advanced Stock Trading Platform
Description
Profit Prophets is an intuitive and powerful stock trading platform that automates the buying and selling of popular stocks like Amazon, Apple, Google, Meta, Microsoft, and Tesla. Built for efficiency and ease of use, it caters to both novice and seasoned investors by offering a streamlined interface backed by cutting-edge technology.
 
Table of Contents
1. Tools
        A list of software and frameworks used to create, install, and run the platform.        
2. Installation Guide
        Detailed steps to install and set up Profit Prophets on your device.
3. User Guide
        Instructions on how to navigate the platform and execute trades effectively.
4. System Overview 
        A breakdown of the platform's core functionality and the underlying technology driving the trading process.
5. Credits
    Acknowledgements to the development team and contributors.
 
Tools
* Visual Studio Code
* Alpaca API
* Python 3.8+
* Flask (for backend functionality)
* SQLite (for data storage)
 
Installation Guide
1. Download Visual Studio Code 
* Visit the official Visual Studio Code website and download the latest version for your operating system.
2. Clone the Profit Prophets repository 
* Download or clone the Profit Prophets source code from the GitHub repository.
3. Open in Visual Studio Code 
* Open the cloned folder in Visual Studio Code.
4. Alpaca API Setup 
*  Visit [Alpaca Markets](https://app.alpaca.markets/account/login) to create an account and generate your API keys.
* Copy the API keys (Endpoint, Key ID, and Secret Key) and add them to the `config.py` file in the appropriate fields.
5. Install Dependencies 
* Open the terminal in Visual Studio Code and run the following command to install all required packages:
         pip install -r requirements.txt
6. Run the Application 
* Once the setup is complete, run the platform by executing the following command:
         python trade.py
 
User Guide
1. Starting the Application
* Launch the Profit Prophets application by running `trade.py` in Visual Studio Code.
2. Activating the Trading Bot
* On the Welcome screen, click the Activate Bot button to initiate the automated trading process.
3. Tracking Orders
* Once activated, the next screen will display your orders, including stock purchases, the total available balance, and the price per share.
4. Reactivating the Bot
* After completing a trade, the Congratulations screen will provide two options:
   * Click Yes to purchase another stock and return to the Welcome screen.
   * Click No to quit the application.
5. Deactivating the Bot
* You can deactivate the bot at any time by clicking the Deactivate button on the main screen.
System Overview
1. Backend Process
* Upon activation, the Profit Prophets bot sends API requests to Alpaca to execute stock purchases. The platform fetches real-time stock prices and displays your balance and order details on the screen.
2. Stock Purchase Verification
* The second screen, Order Confirmation, provides details such as the number of stocks purchased, their respective prices, and the total amount spent.
3. Session Continuation or Exit
* After each trade session, users can either continue trading or exit the platform. Profit Prophets ensures an easy and hassle-free trading cycle.
 
Credits
* Development Team: Profit Prophets was developed by a team of experienced Computer Science Analysts specializing in financial technology and automation.
Group Members:
Zaria Ascue
Harlem Morton
Simisola Mumuni
Jayden Price
Angelina Woodard
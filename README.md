# Profit Prophets Stock Trading Platform


## **Description**
This application is an easy to use stock trading software that automates the buying and selling of stocks - Amazon, Apple, Google, META, Microstoft, Tesla.  

## **Table of Contents**
1)  Tools

    Software used to create, install, and use application
    
2)  How To Install And Run

    Instructions for how to load the application on your device
    
3) How To Use

    Instructions for how to implement the application
    
4)  How It Works

    A description of what happens behind the UI
    
5) Credits

    Computer Science Analysts


## **Tools**
- Visual Studio Code
- Alpaca

## **How To Install And Run**
- Download Visual Studio Code
- Download the zip file that includes each file  
- Open the folder in Visual Studio Code

- Go to https://app.alpaca.markets/account/login
  - Log in
  - click 'Home'
  - click 'Generate' or 'Regenerate' under API keys
  - copy Endpoint and Key
- Put your API key credentials from Alpaca into the config.py file

- Run this command to install the required packages:
  - pip install -r requirements.txt

- Run trade.py to start the application

## **How To Use**
- Run the application in Visual Studio Code

To Activate Bot:
- Click Activate button
  
To Deactivate Bot:
- Click Deactivate button

To Reactivate Bot:
- Click 'Yes' on the Congratulations Screen

To Quit Application:
- Click 'No' on the Congratulations Screen

## **How It Works**
- After the user clicks 'Activate Bot' on the welcome screen, this sends the command to the backend that purchases each stock. 
- The next screen called Ordering Stocks shows a verifcation of what the users ordered.
  - This screen shows the total balance the user has, the day time in force, and the price that each stock was purchased at
- The next screen called Congratulations shows the option for users to purchase another stock or not
    - If the user chooses to purchase another stock, clicking 'Yes', they will be taken back to the Welcome Screen, allowing them to restart the process
    - If the user chooses **NOT** to purchase another stock, clicking 'No', the program will quit

## **Credits**
Angela Darden

Darius Davenport

Winter Keemer

Casby Robinson

Jaden Smith

Fayed Troy

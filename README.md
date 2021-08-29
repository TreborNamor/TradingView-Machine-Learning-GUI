# TradeView GUI

TradeView is a free and open source Trading View bot written in Python. It is designed to support all major exchanges. It contains back testing, money management tools as well as strategy optimization by machine learning. [Here is live example of TradeView](https://vimeo.com/594029262)

![image](https://github.com/TreborNamor/TradingView_Machine_Learning/blob/16ab9d3fae94258a715965e271d5c80b6517051c/pictures/TradeViewGUI.png)
![image](https://github.com/TreborNamor/TradingView_Machine_Learning/blob/16ab9d3fae94258a715965e271d5c80b6517051c/pictures/TradeViewResultsExample.png)

## Disclaimer

This software is for educational purposes only. Do not risk money which
you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS
AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.

We strongly recommend you to have coding and Python knowledge. Do not
hesitate to read the source code and understand the mechanism of this bot.

## Features

- [x] **Based on Python 3.8+**: The bot will work on any operating system - Windows, macOS and Linux.
- [x] **SL/TP Generator**: Let the bot decide what stop loss or take profit you should use.
- [x] **Functions**: A growing library of functions you can use to optimize your script.

## Installation

#1. Download Pycharm, Firefox, and TradingView_Machine_Learning folder here.

[PyCharm Community Edition](https://www.jetbrains.com/pycharm/download)

[FireFox](https://www.mozilla.org/en-US/firefox/new/)

[TradingView_Machine Learning](https://github.com/TreborNamor/TradingView_Machine_Learning/archive/master.zip)

#2. Extract zip file to Desktop and Execute TradeViewGUI.exe file.
![image](https://github.com/TreborNamor/TradingView_Machine_Learning/blob/bd4a703fb0b3ec964c305dd7c720b17b111535fc/pictures/extractZip.png)

#3. Copy and Paste Firefox Profile Path to App.
![image](https://github.com/TreborNamor/TradingView_Machine_Learning/blob/16ab9d3fae94258a715965e271d5c80b6517051c/pictures/FindFirefoxPath.png)
![image](https://github.com/TreborNamor/TradingView_Machine_Learning/blob/bd4a703fb0b3ec964c305dd7c720b17b111535fc/pictures/addPath.png)

#4. Inside Firefox, login into your TradingView profile. Go to your TradingView chart and add the TradingView strategy you want to optimize. When you add the strategy to chart make sure to press CTRL + S on your keyboard to save your chart. I have a TradingView Strategy that is ready to use. You can browse the strategy source code [here.](https://github.com/TreborNamor/TradingView-Machine-Learning-GUI/blob/master/strategies/MACD-RSI%20%20Strategy)
If you want to create a custom TradingView Strategy click [here.](https://github.com/TreborNamor/TradingView-Machine-Learning-GUI/blob/master/strategies/Create%20Your%20Own%20Strategy%20For%20Optimization.txt)
![image](https://github.com/TreborNamor/TradingView-Machine-Learning-GUI/blob/cee46135f1f0d8656c9f1614abb334d8205a6110/pictures/addStrategy.png)

#5. Enter Your long and short parameters and click Run button.
![image](https://github.com/TreborNamor/TradingView_Machine_Learning/blob/bd4a703fb0b3ec964c305dd7c720b17b111535fc/pictures/parameters.png)

# Tips:
- CheckBox: You can hide Firefox browser when checkbox is enabled.
- Minimum Long Stoploss: The minimum percentage you are willing to risk for your strategy. For example, a 1% minimum risk.
- Maximum Long Stoploss: The maximum percentage you are willing to risk for your strategy. For example, a 30% maximum risk.
- Minimum Long Takeprofit: The minimum percentage you are willing to risk for your strategy. For example, a 1% minimum risk.
- Maximum Long Takeprofit: The maximum percentage you are willing to risk for your strategy. For example, a 30% maximum risk.
-Long Increment: When option is available, do you want the strategy to increment in steps of 1 or .1 during parameter search. (Default is set to .1)

- Minimum Short Stoploss: The minimum percentage you are willing to risk for your strategy. For example, a 1% minimum risk.
- Maximum Short Stoploss: The maximum percentage you are willing to risk for your strategy. For example, a 30% maximum risk.
- Minimum Short Takeprofit: The minimum percentage you are willing to risk for your strategy. For example, a 1% minimum risk.
- Maximum Short Takeprofit: The maximum percentage you are willing to risk for your strategy. For example, a 30% maximum risk.
- Short Increment: When option is available, do you want the strategy to increment in steps of 1 or .1 during parameter search. (Default is set to .1)

- Decimal Place: When option is available, by what decimal place would you like during strategy search. (Default is set to 1)
- Max Attempts: What is the maximum amount of attempts would you like the strategy try. (Default is set to 30)
- Firefox Path: The path used to run selenium webdriver.


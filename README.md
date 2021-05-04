# TradingView Machine Learning

TradeView is a free and open source Trading View bot written in Python. It is designed to support all major exchanges. It contains back testing, money management tools as well as strategy optimization by machine learning.

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

#2. Extract Zip File And Open The Folder With Pycharm.

#3. Go to Terminal And type code below to get pip packages.
- pip install beautifulsoup4
- pip install selenium
- pip install webdriver-manager==3.4.0
- pip install numpy
- pip install termcolor

#3. Go To functions folder in PyCharm, and click webdriver.py
You'll need to put your firefox profile in that file to make sure Python can find your web browser.
- profile = webdriver.FirefoxProfile(r'C:\Users\Robert\AppData\Roaming\Mozilla\Firefox\Profiles\kwftlp36.default-release')
- if you need help finding firefox profile go to this website and copy the root directory folder into script.
- it should look like this. "C:\Users\Robert\AppData\Roaming\Mozilla\Firefox\Profiles\kwftlp36.default-release"
- [Find Profile](https://support.mozilla.org/en-US/kb/profile-manager-create-remove-switch-firefox-profiles)

#4. Go To Scripts Folder

- In the scripts folder you'll find scripts to optimize stoploss, take profit, or both files.

#5. Click A Script And Run It.

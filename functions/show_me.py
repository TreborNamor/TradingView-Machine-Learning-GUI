from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import bs4
import time
from termcolor import colored

from database.profit import profits
from functions.webdriver import driver


def max_stoploss():
    try:
        max_stoploss = max(profits, key=profits.get)
        max_percentage = profits[max_stoploss]
        if max_percentage > 0:
            print(colored(f"Max Stoploss: " + str(max_stoploss) + "%", 'green'))
        else:
            print(colored(f"Max Stoploss: " + str(max_stoploss) + "%", 'red'))

    except (UnboundLocalError, ValueError):
        print("error printing stoploss.")


def max_takeprofit():
    try:
        max_take_profit = max(profits, key=profits.get)
        max_percentage = profits[max_take_profit]
        if max_percentage > 0:
            print(colored(f"Max Take Profit: " + str(max_take_profit) + "%", 'green'))
        else:
            print(colored(f"Max Take Profit: " + str(max_take_profit) + "%", 'red'))

    except (UnboundLocalError, ValueError):
        print("error printing stoploss.")


def netprofit():
    try:
        max_stoploss = max(profits, key=profits.get)
        max_percentage = profits[max_stoploss]
        if max_percentage > 0:
            print(colored(f"Net Profit: " + str(max_percentage) + "%", 'green'))
        else:
            print(colored(f"Net Profit: " + str(max_percentage) + "%", 'red'))

    except (UnboundLocalError, ValueError):
        print("error printing net profit.")


def total_trades():
    total_trades = driver.find_elements_by_xpath("//*[@class='data-item']")[1].text.split("Total Closed Trades")[0]
    print(f"Total Trades: " + str(total_trades.replace(" ", "")), end="")


def percent_profitable():
    percent_profitable = driver.find_elements_by_xpath("//*[@class='data-item']")[2].text.split("%\n Percent "
                                                                                                "Profitable")[0]
    if float(percent_profitable) <= 30:
        print(colored(f"Percent Profitable: " + str(percent_profitable) + "%", 'red'))
    elif 49 >= float(percent_profitable) > 30:
        print(colored(f"Percent Profitable: " + str(percent_profitable) + "%", 'yellow'))
    else:
        print(colored(f"Percent Profitable: " + str(percent_profitable) + "%", 'green'))


def profit_factor():
    profit_factor = driver.find_elements_by_xpath("//*[@class='data-item']")[3].text.split("Profit Factor")[0]
    print(f"Profit Factor: " + str(profit_factor), end="")


def max_drawdown():
    try:
        check = driver.find_elements_by_class_name("additional_percent_value")[1]
        check.find_element_by_xpath('./span[contains(@class, "neg")]')
        negative = True
    except NoSuchElementException:
        negative = False
    if negative:
        max_drawdown = driver.find_elements_by_class_name("additional_percent_value")[1].text.split("Max Drawdown")[0]
        print(colored(f'Max Drawdown: {max_drawdown}', 'red'))
    else:
        max_drawdown = driver.find_elements_by_class_name("additional_percent_value")[1].text.split("Max Drawdown")[0]
        print(colored(f'Max Drawdown: {max_drawdown}', 'green'))


def avg_trade():
    try:
        check = driver.find_elements_by_class_name("additional_percent_value")[2]
        check.find_element_by_xpath('./span[contains(@class, "neg")]')
        negative = True
    except NoSuchElementException:
        negative = False
    if negative:
        avg_trade = driver.find_elements_by_class_name("additional_percent_value")[2].text.split("Avg Trade")[0]
        print(colored(f'Average Trade: {avg_trade}', 'red'))
    else:
        avg_trade = driver.find_elements_by_class_name("additional_percent_value")[2].text.split("Avg Trade")[0]
        print(colored(f'Average Trade: {avg_trade}', 'green'))


def avg_bars():
    avg_bars = driver.find_elements_by_xpath("//*[@class='data-item']")[6].text.split("Avg # Bars in Trades")[0]
    print(f"Average # Bars in Trades: " + str(avg_bars))
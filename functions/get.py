from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
import time
from termcolor import colored

from database.profit import profits
from functions.webdriver import driver


def net_all(long_stoploss_value, long_takeprofit_value, short_stoploss_value, short_takeprofit_value, wait):
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "additional_percent_value")))
    try:
        time.sleep(.5)
        check = driver.find_elements_by_class_name("additional_percent_value")[0]
        check.find_element_by_xpath('./span[contains(@class, "neg")]')
        negative = True
    except NoSuchElementException:
        negative = False

    if negative:
        net_profit = driver.find_elements_by_class_name("additional_percent_value")[0].text.split(" %")
        net_value = -float(net_profit[0])
        profits.update({-net_value: ["Long Stoploss:", long_stoploss_value, "Long Take Profit:", long_takeprofit_value, "Short Stoploss:", short_stoploss_value, "Short Take Profit:", short_takeprofit_value]})
        print(colored(f'Net Profit: -{net_value}% --> Long Stoploss: {long_stoploss_value}, Long Take Profit: {long_takeprofit_value}, Short Stoploss: {short_stoploss_value}, Short Take Profit: {short_takeprofit_value}', 'red'))
    else:
        net_profit = driver.find_elements_by_class_name("additional_percent_value")[0].text.split(" %")
        net_value = float(net_profit[0])
        profits.update({net_value: ["Long Stoploss:", long_stoploss_value, "Long Take Profit:", long_takeprofit_value, "Short Stoploss:", short_stoploss_value, "Short Take Profit:", short_takeprofit_value]})
        print(colored(f'Net Profit: {net_value}% --> Long Stoploss: {long_stoploss_value}, Long Take Profit: {long_takeprofit_value}, Short Stoploss: {short_stoploss_value}, Short Take Profit: {short_takeprofit_value}', 'green'))
    return net_profit


def net_both(stoploss_value, takeprofit_value, wait):
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "additional_percent_value")))
    try:
        time.sleep(.5)
        check = driver.find_elements_by_class_name("additional_percent_value")[0]
        check.find_element_by_xpath('./span[contains(@class, "neg")]')
        negative = True
    except NoSuchElementException:
        negative = False

    if negative:
        net_profit = driver.find_elements_by_class_name("additional_percent_value")[0].text.split(" %")
        net_value = -float(net_profit[0])
        profits.update({-net_value: ["Stoploss:", stoploss_value, "Take Profit:", takeprofit_value]})
        print(colored(f'Net Profit: -{net_value}% --> Stoploss: {stoploss_value}, Take Profit: {takeprofit_value}', 'red'))
    else:
        net_profit = driver.find_elements_by_class_name("additional_percent_value")[0].text.split(" %")
        net_value = float(net_profit[0])
        profits.update({net_value: ["Stoploss:", stoploss_value, "Take Profit:", takeprofit_value]})
        print(colored(f'Net Profit: {net_value}% --> Stoploss: {stoploss_value}, Take Profit: {takeprofit_value}', 'green'))
    return net_profit


def net_profit_stoploss(count, wait):
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "additional_percent_value")))
    try:
        time.sleep(.5)
        check = driver.find_elements_by_class_name("additional_percent_value")[0]
        check.find_element_by_xpath('./span[contains(@class, "neg")]')
        negative = True
    except NoSuchElementException:
        negative = False

    if negative:
        net_profit = driver.find_elements_by_class_name("additional_percent_value")[0].text.split(" %")
        net_value = -float(net_profit[0])
        profits.update({count: -net_value})
        print(colored(f'Stoploss: {count}%, Net Profit: {net_value}%', 'red'))
    else:
        net_profit = driver.find_elements_by_class_name("additional_percent_value")[0].text.split(" %")
        net_value = float(net_profit[0])
        profits.update({count: net_value})
        print(colored(f'Stoploss: {count}%, Net Profit: {net_value}%', 'green'))
    return net_profit


def net_profit_takeprofit(count, wait):
    try:
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "additional_percent_value")))
        time.sleep(.5)
        check = driver.find_elements_by_class_name("additional_percent_value")[0]
        check.find_element_by_xpath('./span[contains(@class, "neg")]')
        negative = True
    except (NoSuchElementException, IndexError):
        negative = False

    if negative:
        net_profit = driver.find_elements_by_class_name("additional_percent_value")[0].text.split(" %")
        net_value = -float(net_profit[0])
        profits.update({count: -net_value})
        print(colored(f'Take Profit: {count}%, Net Profit: {net_value}%', 'red'))
    else:
        net_profit = driver.find_elements_by_class_name("additional_percent_value")[0].text.split(" %")
        net_value = float(net_profit[0])
        profits.update({count: net_value})
        print(colored(f'Take Profit: {count}%, Net Profit: {net_value}%', 'green'))
    return net_profit


def win_rate(count, wait):
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "additional_percent_value")))
    try:
        win_rate = driver.find_elements_by_class_name("additional_percent_value")[1]
        win_rate.find_element_by_xpath('./span[contains(@class, "neg")]')
        negative = True
    except NoSuchElementException:
        negative = False

    if negative:
        win_rate = driver.find_elements_by_class_name("additional_percent_value")[1].text.split(" %")
        net_value = float(win_rate[0])
        profits.update({count: -net_value})
        negative_color = {count: net_value}
        print(colored(f'{negative_color}', 'red'))
    else:
        win_rate = driver.find_elements_by_class_name("additional_percent_value")[1].text.split(" %")
        net_value = float(win_rate[0])
        profits.update({count: net_value})
        positive_color = {count: net_value}
        print(colored(f'{positive_color}', 'green'))
    return win_rate

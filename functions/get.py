from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from termcolor import colored

from database.profit import profits
from functions.webdriver import driver


def net_value(count, wait):
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@class='additional_percent_value']")))
    try:
        time.sleep(1)
        check = driver.find_elements_by_class_name("additional_percent_value")[0]
        check.find_element_by_xpath('./span[contains(@class, "neg")]')
        negative = True
    except NoSuchElementException:
        negative = False

    if negative:
        net_profit = driver.find_elements_by_class_name("additional_percent_value")[0].text.split(" %")
        net_value = float(net_profit[0])
        profits.update({count: -net_value})
        negative_color = {count: net_value}
        print(colored(f'{negative_color}', 'red'))
    else:
        net_profit = driver.find_elements_by_class_name("additional_percent_value")[0].text.split(" %")
        net_value = float(net_profit[0])
        profits.update({count: net_value})
        positive_color = {count: net_value}
        print(colored(f'{positive_color}', 'green'))
    return net_value

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

from functions.webdriver import driver


def strategy_tester():
    """check if strategy tester tab is active if not click to open tab."""
    strategy_tester = driver.find_elements_by_xpath("//*[@class='title-1C5azoXt']")[2]
    active = strategy_tester.get_attribute('data-active')
    if active == 'false':
        strategy_tester.click()


def settings_button(wait):
    """click settings button and check duplicate."""
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@class='icon-button "
                                                           "js-backtesting-open-format-dialog "
                                                           "apply-common-tooltip']")))
    duplicate_check = driver.find_elements_by_class_name("additional_percent_value")[0].text.split(" %")
    duplicate = float(duplicate_check[0])
    settings_button = driver.find_element_by_xpath(
        "//*[@class='icon-button js-backtesting-open-format-dialog "
        "apply-common-tooltip']")
    settings_button.click()
    return duplicate


def stoploss_input(count, wait):
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@class='innerInput-29Ku0bwF']")))
    stoploss_input_box = driver.find_elements_by_xpath("//*[@class='innerInput-29Ku0bwF']")[0]
    stoploss_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    stoploss_input_box.send_keys(str(count))
    stoploss_input_box.send_keys(Keys.ENTER)
    ok_button = driver.find_element_by_name("submit")
    ok_button.click()


def takeprofit_input(count, wait):
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@class='innerInput-29Ku0bwF']")))
    takeprofit_input_box = driver.find_elements_by_xpath("//*[@class='innerInput-29Ku0bwF']")[1]
    takeprofit_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    takeprofit_input_box.send_keys(str(count))
    takeprofit_input_box.send_keys(Keys.ENTER)
    ok_button = driver.find_element_by_name("submit")
    ok_button.click()


def both_inputs(stoploss_value, takeprofit_value, wait):
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@class='innerInput-29Ku0bwF']")))
    stoploss_input_box = driver.find_elements_by_xpath("//*[@class='innerInput-29Ku0bwF']")[0]
    takeprofit_input_box = driver.find_elements_by_xpath("//*[@class='innerInput-29Ku0bwF']")[1]
    stoploss_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    stoploss_input_box.send_keys(str(stoploss_value))
    takeprofit_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    takeprofit_input_box.send_keys(str(takeprofit_value))
    takeprofit_input_box.send_keys(Keys.ENTER)
    time.sleep(.5)
    ok_button = driver.find_element_by_name("submit")
    ok_button.click()
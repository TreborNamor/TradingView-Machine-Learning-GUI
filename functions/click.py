from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
import time

from functions.webdriver import driver


def settings_button(wait):
    """click settings button."""
    try:
        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@class='icon-button "
                                                               "js-backtesting-open-format-dialog "
                                                               "apply-common-tooltip']")))
        settings_button = driver.find_element_by_xpath(
            "//*[@class='icon-button js-backtesting-open-format-dialog "
            "apply-common-tooltip']")
        settings_button.click()
    except AttributeError:
        pass


def strategy_tester():
    """check if strategy tester tab is active if not click to open tab."""
    try:
        strategy_tester_tab = driver.find_elements_by_xpath("//*[@class='title-37voAVwR']")
        for index, web_element in enumerate(strategy_tester_tab):
            if web_element.text == 'Strategy Tester':
                active_tab = strategy_tester_tab[index].get_attribute('data-active')
                if active_tab == 'false':
                    strategy_tester_tab[index].click()
                break
    except (IndexError, NoSuchElementException, ElementNotInteractableException):
        print("Could Not Click Strategy Tester Tab. Please Check web element XPATH.")


def overview():
    try:
        strategy_tester_tab = driver.find_elements_by_xpath("//*[@class='title-37voAVwR']")
        for index, web_element in enumerate(strategy_tester_tab):
            if web_element.text == 'Strategy Tester':
                active_tab = strategy_tester_tab[index].get_attribute('data-active')
                if active_tab == 'false':
                    strategy_tester_tab[index].click()
                    # time.sleep(.3)
                    overview = driver.find_element_by_class_name("report-tabs").find_elements_by_tag_name("li")[0]
                    overview.click()
                else:
                    overview = driver.find_element_by_class_name("report-tabs").find_elements_by_tag_name("li")[0]
                    overview.click()
                break
    except (IndexError, NoSuchElementException, ElementNotInteractableException):
        print("Could Not Click Strategy Tester Tab. Please Check web element XPATH.")


def performance_summary():
    try:
        strategy_tester_tab = driver.find_elements_by_xpath("//*[@class='title-37voAVwR']")
        for index, web_element in enumerate(strategy_tester_tab):
            if web_element.text == 'Strategy Tester':
                active_tab = strategy_tester_tab[index].get_attribute('data-active')
                if active_tab == 'false':
                    strategy_tester_tab[index].click()
                    # time.sleep(.3)
                    performance_tab = driver.find_elements_by_class_name("report-tabs").find_elements_by_tag_name("li")[1]
                    performance_tab.click()
                else:
                    performance_tab = driver.find_element_by_class_name("report-tabs").find_elements_by_tag_name("li")[1]
                    performance_tab.click()
                break
    except (IndexError, NoSuchElementException, ElementNotInteractableException):
        print("Could Not Click Strategy Tester Tab. Please Check web element XPATH.")


def list_of_trades():
    try:
        strategy_tester_tab = driver.find_elements_by_xpath("//*[@class='title-37voAVwR']")
        for index, web_element in enumerate(strategy_tester_tab):
            if web_element.text == 'Strategy Tester':
                active_tab = strategy_tester_tab[index].get_attribute('data-active')
                if active_tab == 'false':
                    strategy_tester_tab[index].click()
                    # time.sleep(.3)
                    list_of_trades = driver.find_element_by_class_name("report-tabs").find_elements_by_tag_name("li")[2]
                    list_of_trades.click()
                else:
                    list_of_trades = driver.find_element_by_class_name("report-tabs").find_elements_by_tag_name("li")[2]
                    list_of_trades.click()
                break
    except (IndexError, NoSuchElementException, ElementNotInteractableException):
        print("Could Not Click Strategy Tester Tab. Please Check web element XPATH.")


def stoploss_input(count, wait):
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")))
    stoploss_input_box = driver.find_elements_by_xpath("//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")[0]
    stoploss_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    stoploss_input_box.send_keys(str(count))
    stoploss_input_box.send_keys(Keys.ENTER)
    ok_button = driver.find_element_by_name("submit")
    ok_button.click()


def takeprofit_input(count, wait):
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")))
    takeprofit_input_box = driver.find_elements_by_xpath("//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")[1]
    takeprofit_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    takeprofit_input_box.send_keys(str(count))
    takeprofit_input_box.send_keys(Keys.ENTER)
    ok_button = driver.find_element_by_name("submit")
    ok_button.click()


def both_inputs(stoploss_value, takeprofit_value, wait):
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")))
    stoploss_input_box = driver.find_elements_by_xpath("//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")[0]
    takeprofit_input_box = driver.find_elements_by_xpath("//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")[1]
    stoploss_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    stoploss_input_box.send_keys(str(stoploss_value))
    takeprofit_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    takeprofit_input_box.send_keys(str(takeprofit_value))
    takeprofit_input_box.send_keys(Keys.ENTER)
    time.sleep(.5)
    ok_button = driver.find_element_by_name("submit")
    ok_button.click()

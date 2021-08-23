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
    """click perfromance summary tab."""
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
    """click list of trades tab."""
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


def long_stoploss_input(count, wait):
    """click short stoploss input."""
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")))
    stoploss_input_box = driver.find_elements_by_xpath("//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")[0]
    stoploss_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    stoploss_input_box.send_keys(str(count))
    stoploss_input_box.send_keys(Keys.ENTER)
    time.sleep(.5)
    ok_button = driver.find_element_by_name("submit")
    ok_button.click()


def long_takeprofit_input(count, wait):
    """click long take profit input."""
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")))
    takeprofit_input_box = driver.find_elements_by_xpath("//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")[1]
    takeprofit_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    takeprofit_input_box.send_keys(str(count))
    takeprofit_input_box.send_keys(Keys.ENTER)
    time.sleep(.5)
    ok_button = driver.find_element_by_name("submit")
    ok_button.click()


def short_stoploss_input(count, wait):
    """click short stoploss input."""
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")))
    stoploss_input_box = driver.find_elements_by_xpath("//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")[2]
    stoploss_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    stoploss_input_box.send_keys(str(count))
    stoploss_input_box.send_keys(Keys.ENTER)
    time.sleep(.5)
    ok_button = driver.find_element_by_name("submit")
    ok_button.click()


def short_takeprofit_input(count, wait):
    """click short take profit input."""
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")))
    stoploss_input_box = driver.find_elements_by_xpath("//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")[3]
    stoploss_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    stoploss_input_box.send_keys(str(count))
    stoploss_input_box.send_keys(Keys.ENTER)
    time.sleep(.5)
    ok_button = driver.find_element_by_name("submit")
    ok_button.click()


def long_inputs(long_stoploss_value, long_takeprofit_value, wait):
    """click both long inputs."""
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")))
    stoploss_input_box = driver.find_elements_by_xpath("//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")[0]
    takeprofit_input_box = driver.find_elements_by_xpath("//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")[1]
    stoploss_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    stoploss_input_box.send_keys(str(long_stoploss_value))
    takeprofit_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    takeprofit_input_box.send_keys(str(long_takeprofit_value))
    takeprofit_input_box.send_keys(Keys.ENTER)
    time.sleep(.5)
    ok_button = driver.find_element_by_name("submit")
    ok_button.click()


def short_inputs(short_stoploss_value, short_takeprofit_value, wait):
    """click both short inputs."""
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")))
    stoploss_input_box = driver.find_elements_by_xpath("//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")[2]
    takeprofit_input_box = driver.find_elements_by_xpath("//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")[3]
    stoploss_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    stoploss_input_box.send_keys(str(short_stoploss_value))
    takeprofit_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    takeprofit_input_box.send_keys(str(short_takeprofit_value))
    takeprofit_input_box.send_keys(Keys.ENTER)
    time.sleep(.5)
    ok_button = driver.find_element_by_name("submit")
    ok_button.click()


def all_inputs(long_stoploss_value, long_takeprofit_value, short_stoploss_value, short_takeprofit_value, wait):
    """click short stoploss input."""
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")))
    long_stoploss_input_box = driver.find_elements_by_xpath("//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")[0]
    long_takeprofit_input_box = driver.find_elements_by_xpath("//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")[1]
    short_stoploss_input_box = driver.find_elements_by_xpath("//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")[2]
    short_takeprofit_input_box = driver.find_elements_by_xpath("//*[@class='input-3bEGcMc9 with-end-slot-S5RrC8PC']")[3]
    long_stoploss_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    long_stoploss_input_box.send_keys(str(long_stoploss_value))
    long_takeprofit_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    long_takeprofit_input_box.send_keys(str(long_takeprofit_value))
    short_stoploss_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    short_stoploss_input_box.send_keys(str(short_stoploss_value))
    short_takeprofit_input_box.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE)
    short_takeprofit_input_box.send_keys(str(short_takeprofit_value))
    short_takeprofit_input_box.send_keys(Keys.ENTER)
    time.sleep(.5)
    ok_button = driver.find_element_by_name("submit")
    ok_button.click()


def input_tab():
    """making sure the input tab is clicked."""
    try:
        input_tab = driver.find_elements_by_xpath("//*[@class='tab-1KEqJy8_ withHover-1KEqJy8_ tab-3I2ohC86']")[0]
        if input_tab.get_attribute("data-value") == "inputs":
            input_tab.click()
    except IndexError:
        pass


def ok_button():
    time.sleep(.5)
    ok_button = driver.find_element_by_name("submit")
    ok_button.click()

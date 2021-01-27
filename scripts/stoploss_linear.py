from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from functions import click, webdriver, show_me, get, find, check
import time
import numpy as np

url = 'https://www.tradingview.com/chart/H5Sc6piM/#'  # enter your trading view profile link here.
min_stoploss = 0
max_stoploss = 20
increment = 1
take_profit_range = np.arange(min_stoploss, max_stoploss, increment)


def run_script(driver):
    """find the best stop loss value."""
    wait = WebDriverWait(driver, 5)
    driver.get(url)

    # Click Strategy Tester tab then extracting data from webpage.
    click.strategy_tester()
    print("Generating Max Profit For Stop Loss.\n")
    print("Loading script...")
    for number in take_profit_range:
        count = round(number, 2)
        try:
            # click settings button and check duplicate values.
            previous_net_profit = click.settings_button(wait)

            # click stop loss input text box and enter number.
            click.stoploss_input(count, wait)

            # extract the net profit percentage.
            current_net_profit = get.net_value(count, wait)

            # check if duplicate Net Profit values.
            if check.duplicate(count, previous_net_profit, current_net_profit):
                break

        except (StaleElementReferenceException, TimeoutException, NoSuchElementException):
            print("script has timed out.")
            break

    # adding new take profit to your strategy.
    click.settings_button(wait)
    best_key = find.best_key()
    click.stoploss_input(best_key, wait)
    time.sleep(.5)

    print("\n----------Results----------\n")
    show_me.total_trades()
    show_me.max_stoploss()
    show_me.netprofit()
    show_me.percent_profitable()
    show_me.max_drawdown()
    show_me.avg_trade()


if __name__ == '__main__':
    run_script(webdriver.driver)

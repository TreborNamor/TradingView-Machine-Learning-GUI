import random
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
import time
from functions import click, webdriver, show_me, get, find
from database.profit import profits

# Welcome to my SL/TP generator.
# Feel free to contribute to this project if you like.
# Follow me on TradingView at https://www.tradingview.com/u/Bunghole
# Follow my AI Bot on Telegram https://t.me/joinchat/BPVwDm2L-QQ0OTI5
# Donate TP for Bunghole (Bitcoin Address): 384RSWF69Zk4pfGvAc7dyeZ1XrcVH8K6GF

url = 'https://www.tradingview.com/chart/H5Sc6piM/'  # enter your trading view profile link here.

# Enter your minimum and maximum values for stop loss and take profit.
min_stoploss_value = 0
max_stoploss_value = 15
min_takeprofit_value = 0
max_takeprofit_value = 30

decimal_place = 1  # enter decimal place of values. (Default 1st decimal place)
max_attempts = 30  # For example, 30 attempts to find best stop loss and take profit values.


def run_script(driver):
    """find the best stop loss value."""
    wait = WebDriverWait(driver, 5)
    driver.get(url)
    time.sleep(1)
    click.strategy_tester()
    try:
        click.overview()
    except NoSuchElementException:
        time.sleep(1)
        click.overview()
    print("Generating Max Profit For Stop Loss.")
    print("Loading script...\n")
    click.settings_button(wait)
    click.input_tab()
    click.ok_button()

    count = 0
    while count < max_attempts:
        count += 1
        stoploss_value = round(random.uniform(min_stoploss_value, max_stoploss_value), decimal_place)
        takeprofit_value = round(random.uniform(min_takeprofit_value, max_takeprofit_value), decimal_place)
        try:
            # click settings button
            click.settings_button(wait)

            # click both input boxes and add values.
            click.short_inputs(stoploss_value, takeprofit_value, wait)

            # extract the net profit percentage.
            get.net_both(stoploss_value, takeprofit_value, wait)

        except (StaleElementReferenceException, TimeoutException, NoSuchElementException):
            print("script has timed out.")
            break

    # adding new takeprofit to your strategy.
    click.settings_button(wait)
    best_key = find.best_key_both()
    click.short_inputs(profits[best_key][1], profits[best_key][3], wait)
    time.sleep(.5)

    print("\n----------Results----------\n")
    click.overview()
    show_me.best_both()
    click.performance_summary()
    show_me.total_closed_trades()
    show_me.net_profit()
    show_me.win_rate()
    show_me.max_drawdown()
    show_me.sharpe_ratio()
    show_me.sortino_ratio()
    show_me.win_loss_ratio()
    show_me.avg_win_trade()
    show_me.avg_loss_trade()
    show_me.avg_bars_in_winning_trades()
    # show_me.gross_profit()
    # show_me.gross_loss()
    # show_me.buy_and_hold_return()
    # show_me.max_contracts_held()
    # show_me.open_pl()
    # show_me.commission_paid()
    # show_me.total_open_trades()
    # show_me.number_winning_trades()
    # show_me.number_losing_trades()
    # show_me.percent_profitable()
    # show_me.avg_trade()
    # show_me.largest_win_trade()
    # show_me.largest_loss_trade()
    # show_me.avg_bars_in_trades()
    # show_me.avg_bars_in_losing_trades()


if __name__ == '__main__':
    run_script(webdriver.driver)

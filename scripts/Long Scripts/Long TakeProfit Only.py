from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from functions import click, webdriver, show_me, get, find
import time
import numpy as np

# Welcome to my SL/TP generator.
# Feel free to contribute to this project if you like.
# Follow me on TradingView at https://www.tradingview.com/u/Bunghole
# Follow my AI Bot on Telegram https://t.me/joinchat/BPVwDm2L-QQ0OTI5
# Donate TP for Bunghole (Bitcoin Address): 384RSWF69Zk4pfGvAc7dyeZ1XrcVH8K6GF

url = ''  # enter your trading view profile link here.
min_value = 0  # enter your minimum take profit value.
max_value = 20  # enter your maximum take profit value.
increment = 1  # You can increment count in decimals or in whole numbers.
range = np.arange(min_value, max_value, increment)


def run_script(driver):
    """find the best take profit value."""

    # Loading Webpage.
    wait = WebDriverWait(driver, 10)
    driver.get(url)
    click.strategy_tester()
    try:
        click.overview()
    except NoSuchElementException:
        time.sleep(1)
        click.overview()
    print("Generating Max Profit For Take Profit.")
    print("Loading script...\n")
    click.settings_button(wait)
    click.input_tab()
    click.ok_button()

    # Searching for best take profit for your strategy.
    for number in range:
        count = round(number, 2)
        try:
            click.settings_button(wait)
            click.long_takeprofit_input(count, wait)
            get.net_profit_takeprofit(count, wait)
        except (StaleElementReferenceException, TimeoutException, NoSuchElementException):
            print("script has timed out.")
            break

    # adding the best take profit to your strategy on TradingView.
    click.settings_button(wait)
    best_key = find.best_takeprofit()
    click.long_takeprofit_input(best_key, wait)
    time.sleep(1)

    # Printing Results of the best take profit value found.
    print("\n----------Results----------\n")
    click.overview()
    show_me.best_takeprofit()
    click.performance_summary()
    show_me.total_closed_trades()
    show_me.win_rate()
    show_me.net_profit()
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

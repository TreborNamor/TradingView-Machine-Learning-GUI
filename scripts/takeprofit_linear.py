from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from functions import click, webdriver, show_me, get, find
import time
import numpy as np

url = 'https://www.tradingview.com/chart/H5Sc6piM/#'  # enter your trading view profile link here.
min_value = 0  # enter your minimum take profit value.
max_value = 10  # enter your maximum take profit value.
increment = .1  # You can increment count in decimals or in whole numbers.
range = np.arange(min_value, max_value, increment)


def run_script(driver):
    """find the best stop loss value."""
    wait = WebDriverWait(driver, 5)
    driver.get(url)

    click.strategy_tester()
    try:
        click.overview()
    except NoSuchElementException:
        time.sleep(1)
        click.overview()

    print("Generating Max Profit For Stop Loss.\n")
    print("Loading script...")
    for number in range:
        count = round(number, 2)
        try:
            click.settings_button(wait)
            click.takeprofit_input(count, wait)  # clicking stop loss input text box and entering number.
            get.net_value(count, wait)

        except (StaleElementReferenceException, TimeoutException, NoSuchElementException):
            print("script has timed out.")
            break

    # adding the new value to your strategy.
    click.settings_button(wait)
    best_key = find.best_key()
    click.takeprofit_input(best_key, wait)
    time.sleep(.5)

    print("\n----------Results----------\n")
    click.overview()
    show_me.best_takeprofit()
    click.performance_summary()
    show_me.total_closed_trades()
    show_me.win_rate()
    show_me.net_profit()
    show_me.max_drawdown()
    show_me.sharpe_ratio()
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

from selenium.common.exceptions import NoSuchElementException
from termcolor import colored
from database.profit import profits
from functions.webdriver import driver
from functions import find


def best_stoploss():
    try:
        best_stoploss = max(profits, key=profits.get)
        max_percentage = profits[best_stoploss]
        if max_percentage > 0:
            profitable = colored(str(best_stoploss) + " %", 'green')
            print(f"Best Stoploss: " + str(profitable))
        else:
            profitable = colored(str(best_stoploss) + " %", 'red')
            print(f"Best Stoploss: " + str(profitable))
    except (UnboundLocalError, ValueError):
        print("error printing stoploss.")


def best_takeprofit():
    try:
        best_takeprofit = max(profits, key=profits.get)
        max_percentage = profits[best_takeprofit]
        if max_percentage > 0:
            profitable = colored(str(best_takeprofit) + " %", 'green')
            print(f"Best Take Profit: " + str(profitable))
        else:
            profitable = colored(str(best_takeprofit) + " %", 'red')
            print(f"Best Take Profit: " + str(profitable))
    except (UnboundLocalError, ValueError):
        print("error printing take profit.")


def best_both():
    try:
        best_key = find.best_key_both()
        best_stoploss = profits[best_key][1]
        best_takeprofit = profits[best_key][3]
        print(f"Best Stop Loss: {best_stoploss}")
        print(f"Best Take Profit: {best_takeprofit}\n")
    except (UnboundLocalError, ValueError):
        print("error printing stoploss.")


def best_all():
    try:
        best_key = find.best_key_both()
        best_long_stoploss = profits[best_key][1]
        best_long_takeprofit = profits[best_key][3]
        best_short_stoploss = profits[best_key][5]
        best_short_takeprofit = profits[best_key][7]
        print(f"Best Long Stop Loss: {best_long_stoploss}")
        print(f"Best Long Take Profit: {best_long_takeprofit}")
        print(f"Best Short Stop Loss: {best_short_stoploss}")
        print(f"Best Short Take Profit: {best_short_takeprofit}\n")
    except (UnboundLocalError, ValueError):
        print("error printing stoploss.")


def net_profit():
    net_profit = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[0].find_element_by_class_name("additional_percent_value")
    try:
        negative = net_profit.find_element_by_class_name("neg")
        if negative:
            display = colored(f'{net_profit.text}', 'red')
            print(f'Net Profit: {display}')
    except NoSuchElementException:
        display = colored(f'{net_profit.text}', 'green')
        print(f'Net Profit: {display}')


def gross_profit():
    gross_profit = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[1].find_element_by_class_name("additional_percent_value")
    try:
        negative = gross_profit.find_element_by_class_name("neg")
        if negative:
            display = colored(f'{gross_profit.text}', 'red')
            print(f'Gross Profit: {display}')
    except NoSuchElementException:
        display = colored(f'{gross_profit.text}', 'green')
        print(f'Gross Profit: {display}')


def gross_loss():
    gross_loss = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[2].find_element_by_class_name("additional_percent_value")
    try:
        negative = gross_loss.find_element_by_class_name("neg")
        if negative:
            display = colored(f'{gross_loss.text}', 'red')
            print(f'Gross Loss: {display}')
    except NoSuchElementException:
        display = colored(f'{gross_loss.text}', 'green')
        print(f'Gross Loss: {display}')


def max_drawdown():
    max_drawdown = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[3].find_element_by_class_name("additional_percent_value")
    try:
        negative = max_drawdown.find_element_by_class_name("neg")
        if negative:
            display = colored(f'{max_drawdown.text}', 'red')
            print(f'Max Drawdown: {display}')
    except NoSuchElementException:
        display = colored(f'{max_drawdown.text}', 'green')
        print(f'Max Drawdown: {display}')


def buy_and_hold_return():
    buy_and_hold_return = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[4].find_element_by_class_name("additional_percent_value")
    try:
        negative = buy_and_hold_return.find_element_by_class_name("neg")
        if negative:
            display = colored(f'{buy_and_hold_return.text}', 'red')
            print(f'Buy & Hold Return: {display}')
    except NoSuchElementException:
        display = colored(f'{buy_and_hold_return.text}', 'green')
        print(f'Buy & Hold Return: {display}')


def sharpe_ratio():
    sharpe_ratio = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[5].find_elements_by_tag_name("td")[1]
    try:
        negative = sharpe_ratio.find_element_by_class_name("neg")
        if negative:
            display = colored(f'{sharpe_ratio.text}', 'red')
            print(f'Sharpe Ratio: {display}')
    except NoSuchElementException:
        display = colored(f'{sharpe_ratio.text}', 'green')
        print(f'Sharpe Ratio: {display}')


def sortino_ratio():
    sortino_ratio = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[6].find_elements_by_tag_name("td")[1]
    try:
        negative = sortino_ratio.find_element_by_class_name("neg")
        if negative:
            display = colored(f'{sortino_ratio.text}', 'red')
            print(f'Sortino Ratio: {display}')
    except NoSuchElementException:
        display = colored(f'{sortino_ratio.text}', 'green')
        print(f'Sortino Ratio: {display}')


def profit_factor():
    profit_factor = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[7].find_elements_by_tag_name("td")[1]
    try:
        negative = profit_factor.find_element_by_class_name("neg")
        if negative:
            display = colored(f'{profit_factor.text}', 'red')
            print(f'Profit Factor: {display}')
    except NoSuchElementException:
        display = colored(f'{profit_factor.text}', 'green')
        print(f'Profit Factor: {display}')


def max_contracts_held():
    max_contracts_held = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[8].find_elements_by_tag_name("td")[1]
    try:
        negative = max_contracts_held.find_element_by_class_name("neg")
        if negative:
            display = colored(f'{max_contracts_held.text}', 'red')
            print(f'Max Contracts Held: {display}')
    except NoSuchElementException:
        display = colored(f'{max_contracts_held.text}', 'green')
        print(f'Max Contracts Held: {display}')


def open_pl():
    open_pl = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[9].find_element_by_class_name("additional_percent_value")
    try:
        negative = open_pl.find_element_by_class_name("neg")
        if negative:
            display = colored(f'{open_pl.text}', 'red')
            print(f'Open PL: {display}')
    except NoSuchElementException:
        display = colored(f'{open_pl.text}', 'green')
        print(f'Open PL: {display}')


def commission_paid():
    commission_paid = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[10].find_elements_by_tag_name("td")[1]
    print(f'Commission Paid: {commission_paid.text}')


def total_closed_trades():
    total_closed_trades = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[11].find_elements_by_tag_name("td")[1]
    print(f'Total Closed Trades: {total_closed_trades.text}')


def total_open_trades():
    total_open_trades = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[12].find_elements_by_tag_name("td")[1]
    print(f'Total Open Trades: {total_open_trades.text}')


def number_winning_trades():
    number_winning_trades = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[13].find_elements_by_tag_name("td")[1]
    print(f'Number Winning Trades: {number_winning_trades.text}')


def number_losing_trades():
    number_losing_trades = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[14].find_elements_by_tag_name("td")[1]
    print(f'Number Losing Trades: {number_losing_trades.text}')


def percent_profitable():
    percent_profitable = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[15].find_elements_by_tag_name("td")[1]
    print(f'Percent Profitable: {percent_profitable.text}')


def avg_trade():
    avg_trade = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[16].find_element_by_class_name("additional_percent_value")
    try:
        negative = avg_trade.find_element_by_class_name("neg")
        if negative:
            display = colored(f'{avg_trade.text}', 'red')
            print(f'Avg Trade: {display}')
    except NoSuchElementException:
        display = colored(f'{avg_trade.text}', 'green')
        print(f'Avg Trade: {display}')


def avg_win_trade():
    avg_win_trade = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[17].find_element_by_class_name("additional_percent_value")
    try:
        negative = avg_win_trade.find_element_by_class_name("neg")
        if negative:
            display = colored(f'{avg_win_trade.text}', 'red')
            print(f'Avg Win Trade: {display}')
    except NoSuchElementException:
        display = colored(f'{avg_win_trade.text}', 'green')
        print(f'Avg Win Trade: {display}')


def avg_loss_trade():
    avg_loss_trade = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[18].find_element_by_class_name("additional_percent_value")
    try:
        negative = avg_loss_trade.find_element_by_class_name("neg")
        if negative:
            display = colored(f'{avg_loss_trade.text}', 'red')
            print(f'Avg Loss Trade: {display}')
    except NoSuchElementException:
        display = colored(f'{avg_loss_trade.text}', 'green')
        print(f'Avg Loss Trade: {display}')


def win_loss_ratio():
    win_loss_ratio = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[19].find_elements_by_tag_name("td")[1]
    print(f'Win/Loss Ratio: {win_loss_ratio.text}')


def largest_winning_trade():
    largest_winning_trade = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[20].find_element_by_class_name("additional_percent_value")
    try:
        negative = largest_winning_trade.find_element_by_class_name("neg")
        if negative:
            display = colored(f'{largest_winning_trade.text}', 'red')
            print(f'Largest Win Trade: {display}')
    except NoSuchElementException:
        display = colored(f'{largest_winning_trade.text}', 'green')
        print(f'Largest Win Trade: {display}')


def largest_losing_trade():
    largest_losing_trade = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[21].find_element_by_class_name("additional_percent_value")
    try:
        negative = largest_losing_trade.find_element_by_class_name("neg")
        if negative:
            display = colored(f'{largest_losing_trade.text}', 'red')
            print(f'Largest Loss Trade: {display}')
    except NoSuchElementException:
        display = colored(f'{largest_losing_trade.text}', 'green')
        print(f'Largest Loss Trade: {display}')


def avg_bars_in_trades():
    avg_bars_in_trades = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[22].find_elements_by_tag_name("td")[1]
    print(f'Avg Bars In Trades: {avg_bars_in_trades.text}')


def avg_bars_in_winning_trades():
    avg_bars_in_winning_trades = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[23].find_elements_by_tag_name("td")[1]
    print(f'Avg Bars In Winning Trades: {avg_bars_in_winning_trades.text}')


def avg_bars_in_losing_trades():
    avg_bars_in_losing_trades = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[24].find_elements_by_tag_name("td")[1]
    print(f'Avg Bars In Losing Trades: {avg_bars_in_losing_trades.text}')


def margin_calls():
    margin_calls = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[25].find_elements_by_tag_name("td")[1]
    print(f'Avg Bars In Losing Trades: {margin_calls.text}')


def win_rate():
    win_rate = driver.find_element_by_class_name("report-data").find_element_by_tag_name("table").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[15].find_elements_by_tag_name("td")[1]
    print(f'Win Rate: {win_rate.text}')

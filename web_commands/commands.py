import time
from web_commands.profit import profits
from TradeViewGUI import Main
from termcolor import colored
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC


class Functions(Main):
    """In this class you have all the selenium web commands I've created to navigate through Trading View's website.
    These web commands control your web browser to do certain task.
    Currently uou will find the click, get, find, and show_me web commands here.
    More web commands will be added as this project grows."""

    # Find Commands
    """ The find commands search for the best stoploss or take profit values inside the profits variable. 
    The profits variable is a declared dictionary imported from the web_commands folder. 
    This is where the stoploss and take profit values are stored. """

    def find_best_stoploss(self):
        best_in_dict = max(profits, key=profits.get)
        return best_in_dict

    def find_best_takeprofit(self):
        best_in_dict = max(profits, key=profits.get)
        return best_in_dict

    def find_best_key_both(self):
        best_in_dict = max(profits)
        return best_in_dict

    # Click Commands
    """ The click web commands will use selenium to click on certain sections of the webpage. 
    These commands help the script click certain buttons or text boxes on the website. 
    They can also insert data on to the website through automation. """

    def click_strategy_tester(self, wait):
        """check if strategy tester tab is the active tab. If it's not, click to open tab."""
        try:
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "title-uqXh1Q3i"))
            )

            strategy_tester_tab = self.driver.find_elements(
                By.CLASS_NAME, "title-uqXh1Q3i"
            )
            for index, web_element in enumerate(strategy_tester_tab):
                if web_element.text == "Strategy Tester":
                    active_tab = strategy_tester_tab[index].get_attribute("data-active")
                    if active_tab == "false":
                        strategy_tester_tab[index].click()
                        break

        except Exception:
            print(
                "Could Not Click Strategy Tester Tab. Please Check web element's class name in commands.py file."
            )

    def click_overview(self, wait):
        """click overview tab."""
        try:
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "tab-button-diDiUvd9"))
            )

            overview_tab = self.driver.find_elements(
                By.CLASS_NAME, "tab-button-diDiUvd9"
            )
            for index, web_element in enumerate(overview_tab):
                if web_element.text == "Overview":
                    overview_tab[index].click()
                    break

        except Exception:
            print(
                "Could Not click Overview Tab. Please Check web element's class name in commands.py file."
            )

    def click_settings_button(self, wait):
        """click settings button."""
        try:
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "light-button-msfP1I4t"))
            )

            settings_button = self.driver.find_element(
                By.CLASS_NAME, "light-button-msfP1I4t"
            )
            settings_button.click()

        except Exception:
            print(
                "Could not click settings button. Please check web_element's in commands.py file."
            )

    def click_input_tab(self):
        """click the input tab."""
        try:
            input_tab = self.driver.find_element(By.CLASS_NAME, "tab-Rf5MOAG5")
            if input_tab.get_attribute("data-value") == "inputs":
                input_tab.click()

        except IndexError:
            print(
                "Could not input tab button. Please check web_element's in commands.py file."
            )

    def click_performance_summary(self):
        """click performance summary tab."""
        try:
            performance_tab = self.driver.find_elements(
                By.CLASS_NAME, "tab-button-diDiUvd9"
            )
            for index, web_element in enumerate(performance_tab):
                if web_element.text == "Performance Summary":
                    performance_tab[index].click()
                    break

        except IndexError:
            print(
                "Could Not Click Performance Summary Tab. Please check web_element's in commands.py file."
            )

    def click_list_of_trades(self):
        """click list of trades tab."""
        try:
            list_of_trades_tab = self.driver.find_elements(
                By.CLASS_NAME, "tab-button-diDiUvd9"
            )
            for index, web_element in enumerate(list_of_trades_tab):
                if web_element.text == "List of Trades":
                    list_of_trades_tab[index].click()
                    break

        except IndexError:
            print(
                "Could Not Click List Of Trades Tab. Please check web_element's in commands.py file."
            )

    def click_long_stoploss_input(self, count, wait):
        """click long stoploss input text box."""
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "input-oiYdY6I4")))

        stoploss_input_box = self.driver.find_elements(By.CLASS_NAME, "input-oiYdY6I4")[
            2
        ]
        stoploss_input_box.send_keys(Keys.BACK_SPACE * 4)
        stoploss_input_box.send_keys(str(count))
        stoploss_input_box.send_keys(Keys.ENTER)
        time.sleep(0.5)
        ok_button = self.driver.find_element(By.NAME, "submit")
        ok_button.click()

    def click_long_takeprofit_input(self, count, wait):
        """click long take profit input text box."""
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "input-oiYdY6I4")))

        takeprofit_input_box = self.driver.find_elements(
            By.CLASS_NAME, "input-oiYdY6I4"
        )[3]
        takeprofit_input_box.send_keys(Keys.BACK_SPACE * 4)
        takeprofit_input_box.send_keys(str(count))
        takeprofit_input_box.send_keys(Keys.ENTER)
        time.sleep(0.5)
        ok_button = self.driver.find_element(By.NAME, "submit")
        ok_button.click()

    def click_short_stoploss_input(self, count, wait):
        """click short stoploss input text box."""
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "input-oiYdY6I4")))

        stoploss_input_box = self.driver.find_elements(By.CLASS_NAME, "input-oiYdY6I4")[
            4
        ]
        stoploss_input_box.send_keys(Keys.BACK_SPACE * 4)
        stoploss_input_box.send_keys(str(count))
        stoploss_input_box.send_keys(Keys.ENTER)
        time.sleep(0.5)
        ok_button = self.driver.find_element(By.NAME, "submit")
        ok_button.click()

    def click_short_takeprofit_input(self, count, wait):
        """click short take profit input text box."""
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "input-oiYdY6I4")))

        stoploss_input_box = self.driver.find_elements(By.CLASS_NAME, "input-oiYdY6I4")[
            5
        ]
        stoploss_input_box.send_keys(Keys.BACK_SPACE * 4)
        stoploss_input_box.send_keys(str(count))
        stoploss_input_box.send_keys(Keys.ENTER)
        time.sleep(0.5)
        ok_button = self.driver.find_element(By.NAME, "submit")
        ok_button.click()

    def click_long_inputs(self, long_stoploss_value, long_takeprofit_value, wait):
        """click both long input text boxes."""
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "input-oiYdY6I4")))

        stoploss_input_box = self.driver.find_elements(By.CLASS_NAME, "input-oiYdY6I4")[
            2
        ]
        takeprofit_input_box = self.driver.find_elements(
            By.CLASS_NAME, "input-oiYdY6I4"
        )[3]
        stoploss_input_box.send_keys(Keys.BACK_SPACE * 4)
        stoploss_input_box.send_keys(str(long_stoploss_value))
        takeprofit_input_box.send_keys(Keys.BACK_SPACE * 4)
        takeprofit_input_box.send_keys(str(long_takeprofit_value))
        takeprofit_input_box.send_keys(Keys.ENTER)
        time.sleep(0.5)
        ok_button = self.driver.find_element(By.NAME, "submit")
        ok_button.click()

    def click_short_inputs(self, short_stoploss_value, short_takeprofit_value, wait):
        """click both short input text boxes."""
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "input-oiYdY6I4")))

        stoploss_input_box = self.driver.find_elements(By.CLASS_NAME, "input-oiYdY6I4")[
            4
        ]
        takeprofit_input_box = self.driver.find_elements(
            By.CLASS_NAME, "input-oiYdY6I4"
        )[5]
        stoploss_input_box.send_keys(Keys.BACK_SPACE * 4)
        stoploss_input_box.send_keys(str(short_stoploss_value))
        takeprofit_input_box.send_keys(Keys.BACK_SPACE * 4)
        takeprofit_input_box.send_keys(str(short_takeprofit_value))
        takeprofit_input_box.send_keys(Keys.ENTER)
        time.sleep(0.5)
        ok_button = self.driver.find_element(By.NAME, "submit")
        ok_button.click()

    def click_all_inputs(
        self,
        long_stoploss_value,
        long_takeprofit_value,
        short_stoploss_value,
        short_takeprofit_value,
        wait,
    ):
        """click all input text boxes."""
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "input-oiYdY6I4")))

        long_stoploss_input_box = self.driver.find_elements(
            By.CLASS_NAME, "input-oiYdY6I4"
        )[2]
        long_takeprofit_input_box = self.driver.find_elements(
            By.CLASS_NAME, "input-oiYdY6I4"
        )[3]
        short_stoploss_input_box = self.driver.find_elements(
            By.CLASS_NAME, "input-oiYdY6I4"
        )[4]
        short_takeprofit_input_box = self.driver.find_elements(
            By.CLASS_NAME, "input-oiYdY6I4"
        )[5]

        long_stoploss_input_box.send_keys(Keys.BACK_SPACE * 4)
        long_stoploss_input_box.send_keys(str(long_stoploss_value))
        long_takeprofit_input_box.send_keys(Keys.BACK_SPACE * 4)
        long_takeprofit_input_box.send_keys(str(long_takeprofit_value))
        short_stoploss_input_box.send_keys(Keys.BACK_SPACE * 4)
        short_stoploss_input_box.send_keys(str(short_stoploss_value))
        short_takeprofit_input_box.send_keys(Keys.BACK_SPACE * 4)
        short_takeprofit_input_box.send_keys(str(short_takeprofit_value))
        short_takeprofit_input_box.send_keys(Keys.ENTER)

        ok_button = self.driver.find_element(By.NAME, "submit")
        ok_button.click()

    def click_ok_button(self):
        """click the ok button inside settings."""
        time.sleep(0.5)
        ok_button = self.driver.find_element(By.NAME, "submit")
        ok_button.click()

    def click_enable_both_checkboxes(self):
        """click both long and short checkboxes."""
        long_checkbox = self.driver.find_element(By.CLASS_NAME, "input-bUw_gKIQ")
        short_checkbox = self.driver.find_elements(By.CLASS_NAME, "input-bUw_gKIQ")[1]
        if not long_checkbox.get_attribute("checked"):
            click_long_checkbox = self.driver.find_element(
                By.CLASS_NAME, "check-bUw_gKIQ"
            )
            click_long_checkbox.click()
        if not short_checkbox.get_attribute("checked"):
            click_short_checkbox = self.driver.find_elements(
                By.CLASS_NAME, "check-bUw_gKIQ"
            )[1]
            click_short_checkbox.click()

    def click_enable_long_strategy_checkbox(self):
        """click enable on the long checkbox."""
        long_checkbox = self.driver.find_element(By.CLASS_NAME, "input-bUw_gKIQ")
        short_checkbox = self.driver.find_elements(By.CLASS_NAME, "input-bUw_gKIQ")[1]
        if not long_checkbox.get_attribute("checked"):
            click_long_checkbox = self.driver.find_element(
                By.CLASS_NAME, "check-bUw_gKIQ"
            )
            click_long_checkbox.click()
        if short_checkbox.get_attribute("checked"):
            click_short_checkbox = self.driver.find_elements(
                By.CLASS_NAME, "check-bUw_gKIQ"
            )[1]
            click_short_checkbox.click()

    def click_enable_short_strategy_checkbox(self):
        """click enable on the short checkbox."""
        long_checkbox = self.driver.find_element(By.CLASS_NAME, "input-bUw_gKIQ")
        short_checkbox = self.driver.find_elements(By.CLASS_NAME, "input-bUw_gKIQ")[1]
        if long_checkbox.get_attribute("checked"):
            click_long_checkbox = self.driver.find_element(
                By.CLASS_NAME, "check-bUw_gKIQ"
            )
            click_long_checkbox.click()
        if not short_checkbox.get_attribute("checked"):
            click_short_checkbox = self.driver.find_elements(
                By.CLASS_NAME, "check-bUw_gKIQ"
            )[1]
            click_short_checkbox.click()

    def click_reset_all_inputs(self, wait):
        """click and reset all input text boxes to 50."""
        wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "input-oiYdY6I4"))
        )
        long_stoploss_input_box = self.driver.find_elements(
            By.CLASS_NAME, "input-oiYdY6I4"
        )[2]
        long_takeprofit_input_box = self.driver.find_elements(
            By.CLASS_NAME, "input-oiYdY6I4"
        )[3]
        short_stoploss_input_box = self.driver.find_elements(
            By.CLASS_NAME, "input-oiYdY6I4"
        )[4]
        short_takeprofit_input_box = self.driver.find_elements(
            By.CLASS_NAME, "input-oiYdY6I4"
        )[5]
        long_stoploss_input_box.send_keys(Keys.BACK_SPACE * 4)
        long_stoploss_input_box.send_keys(str("20"))
        long_takeprofit_input_box.send_keys(Keys.BACK_SPACE * 4)
        long_takeprofit_input_box.send_keys(str("20"))
        short_stoploss_input_box.send_keys(Keys.BACK_SPACE * 4)
        short_stoploss_input_box.send_keys(str("20"))
        short_takeprofit_input_box.send_keys(Keys.BACK_SPACE * 4)
        short_takeprofit_input_box.send_keys(str("20"))
        short_takeprofit_input_box.send_keys(Keys.ENTER)

    # Get Commands
    """ The get commands will get the stoploss and take profit data that tradingview returns to user. """

    def get_webpage(self):
        try:
            self.driver.get("https://www.tradingview.com/chart/")
        except Exception:
            print(
                "WebDriver Error: Please Check Your FireFox Profile Path Is Correct.\n"
            )
            print(
                "Find Your Firefox Path Instructions. https://imgur.com/gallery/rdCqeT5 "
            )
            return

    def get_net_all(
        self,
        long_stoploss_value,
        long_takeprofit_value,
        short_stoploss_value,
        short_takeprofit_value,
        wait,
    ):
        """will get the net profit of all four values."""
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "secondRow-b1pZpka9"))
        )
        try:
            check = self.driver.find_element(By.CLASS_NAME, "negativeValue-b1pZpka9")
            if check:
                negative = True
        except NoSuchElementException:
            negative = False

        if negative:
            net_profit = self.driver.find_element(
                By.CLASS_NAME, "additionalPercent-b1pZpka9"
            ).text.split("%")
            net_value = float(net_profit[0][1:])
            profits.update(
                {
                    -net_value: [
                        "Long Stoploss:",
                        long_stoploss_value,
                        "Long Take Profit:",
                        long_takeprofit_value,
                        "Short Stoploss:",
                        short_stoploss_value,
                        "Short Take Profit:",
                        short_takeprofit_value,
                    ]
                }
            )
            print(
                colored(
                    f"Net Profit: -{net_value}% --> Long Stoploss: {long_stoploss_value}, Long Take Profit: {long_takeprofit_value}, Short Stoploss: {short_stoploss_value}, Short Take Profit: {short_takeprofit_value}",
                    "red",
                )
            )
        else:
            net_profit = self.driver.find_element(
                By.CLASS_NAME, "additionalPercent-b1pZpka9"
            ).text.split("%")
            net_value = float(net_profit[0])
            profits.update(
                {
                    net_value: [
                        "Long Stoploss:",
                        long_stoploss_value,
                        "Long Take Profit:",
                        long_takeprofit_value,
                        "Short Stoploss:",
                        short_stoploss_value,
                        "Short Take Profit:",
                        short_takeprofit_value,
                    ]
                }
            )
            print(
                colored(
                    f"Net Profit: {net_value}% --> Long Stoploss: {long_stoploss_value}, Long Take Profit: {long_takeprofit_value}, Short Stoploss: {short_stoploss_value}, Short Take Profit: {short_takeprofit_value}",
                    "green",
                )
            )
        return net_profit

    def get_net_both(self, stoploss_value, takeprofit_value, wait):
        """will get the net profit of two values."""
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "secondRow-b1pZpka9"))
        )
        try:
            check = self.driver.find_element(By.CLASS_NAME, "negativeValue-b1pZpka9")
            if check:
                negative = True
        except NoSuchElementException:
            negative = False

        if negative:
            net_profit = self.driver.find_element(
                By.CLASS_NAME, "additionalPercent-b1pZpka9"
            ).text.split("%")
            net_value = float(net_profit[0][1:])
            profits.update(
                {
                    -net_value: [
                        "Stoploss:",
                        stoploss_value,
                        "Take Profit:",
                        takeprofit_value,
                    ]
                }
            )
            print(
                colored(
                    f"Net Profit: -{net_value}% --> Stoploss: {stoploss_value}, Take Profit: {takeprofit_value}",
                    "red",
                )
            )
        else:
            net_profit = self.driver.find_element(
                By.CLASS_NAME, "additionalPercent-b1pZpka9"
            ).text.split(" %")
            net_value = float(net_profit[0])
            profits.update(
                {
                    net_value: [
                        "Stoploss:",
                        stoploss_value,
                        "Take Profit:",
                        takeprofit_value,
                    ]
                }
            )
            print(
                colored(
                    f"Net Profit: {net_value}% --> Stoploss: {stoploss_value}, Take Profit: {takeprofit_value}",
                    "green",
                )
            )
        return net_profit

    def get_net_profit_stoploss(self, count, wait):
        """will get the net profit of stoploss values."""
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "secondRow-b1pZpka9"))
        )
        try:
            check = self.driver.find_element(By.CLASS_NAME, "negativeValue-b1pZpka9")
            if check:
                negative = True
        except NoSuchElementException:
            negative = False

        if negative:
            net_profit = self.driver.find_element(
                By.CLASS_NAME, "additionalPercent-b1pZpka9"
            ).text.split("%")
            net_value = float(net_profit[0][1:])
            profits.update({count: -net_value})
            print(colored(f"Stoploss: {count}%, Net Profit: {net_value}%", "red"))
        else:
            net_profit = self.driver.find_element(
                By.CLASS_NAME, "additionalPercent-b1pZpka9"
            ).text.split(" %")
            net_value = float(net_profit[0])
            profits.update({count: net_value})
            print(colored(f"Stoploss: {count}%, Net Profit: {net_value}%", "green"))
        return net_profit

    def get_net_profit_takeprofit(self, count, wait):
        """will get the net profit of take profit values."""
        try:
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "secondRow-b1pZpka9"))
            )
            check = self.driver.find_element(By.CLASS_NAME, "negativeValue-b1pZpka9")
            if check:
                negative = True
        except NoSuchElementException:
            negative = False

        if negative:
            net_profit = self.driver.find_element(
                By.CLASS_NAME, "additionalPercent-b1pZpka9"
            ).text.split(" %")
            net_value = float(net_profit[0][1:])
            profits.update({count: -net_value})
            print(colored(f"Take Profit: {count}%, Net Profit: {net_value}%", "red"))
        else:
            net_profit = self.driver.find_element(
                By.CLASS_NAME, "additionalPercent-b1pZpka9"
            ).text.split(" %")
            net_value = float(net_profit[0])
            profits.update({count: net_value})
            print(colored(f"Take Profit: {count}%, Net Profit: {net_value}%", "green"))
        return net_profit

    def get_win_rate(self, count, wait):
        """will get the winrate value."""
        wait.until(
            EC.visibility_of_element_located(
                (By.CLASS_NAME, "additional_percent_value")
            )
        )
        try:
            win_rate = self.driver.find_elements(
                By.CLASS_NAME, "additional_percent_value"
            )[1]
            win_rate.find_element(By.CLASS_NAME, "neg")
            negative = True
        except NoSuchElementException:
            negative = False

        if negative:
            win_rate = self.driver.find_elements(
                By.CLASS_NAME, "additional_percent_value"
            )[1].text.split(" %")
            net_value = float(win_rate[0])
            profits.update({count: -net_value})
            negative_color = {count: net_value}
            print(colored(f"{negative_color}", "red"))
        else:
            win_rate = self.driver.find_elements(
                By.CLASS_NAME, "additional_percent_value"
            )[1].text.split(" %")
            net_value = float(win_rate[0])
            profits.update({count: net_value})
            positive_color = {count: net_value}
            print(colored(f"{positive_color}", "green"))
        return win_rate

    # Show Me Commands
    """ The show me commands will print important data to the console. It will shows the end results of the script. """

    def print_best_stoploss(self):
        """print best stoploss to console."""
        try:
            best_stoploss = max(profits, key=profits.get)
            max_percentage = profits[best_stoploss]
            if max_percentage > 0:
                profitable = colored(str(best_stoploss) + " %", "green")
                print(f"Best Stoploss: " + str(profitable) + "\n")
            else:
                profitable = colored(str(best_stoploss) + " %", "red")
                print(f"Best Stoploss: " + str(profitable) + "\n")
        except (UnboundLocalError, ValueError):
            print("error printing stoploss.")

    def print_best_takeprofit(self):
        """print best take profit to console."""
        try:
            best_takeprofit = max(profits, key=profits.get)
            max_percentage = profits[best_takeprofit]
            if max_percentage > 0:
                profitable = colored(str(best_takeprofit) + " %", "green")
                print(f"Best Take Profit: " + str(profitable) + "\n")
            else:
                profitable = colored(str(best_takeprofit) + " %", "red")
                print(f"Best Take Profit: " + str(profitable) + "\n")
        except (UnboundLocalError, ValueError):
            print("error printing take profit.")

    def print_best_both(self):
        """print best stoploss and take profit to console."""
        try:
            best_key = self.find_best_key_both()
            best_stoploss = profits[best_key][1]
            best_takeprofit = profits[best_key][3]
            print(f"Best Stop Loss: {best_stoploss}")
            print(f"Best Take Profit: {best_takeprofit}\n")
        except (UnboundLocalError, ValueError):
            print("error printing stoploss and take profit.")

    def print_best_all(self):
        """print all four of the best stoploss and take profit to console."""
        try:
            best_key = self.find_best_key_both()
            best_long_stoploss = profits[best_key][1]
            best_long_takeprofit = profits[best_key][3]
            best_short_stoploss = profits[best_key][5]
            best_short_takeprofit = profits[best_key][7]
            print(f"Best Long Stop Loss: {best_long_stoploss}")
            print(f"Best Long Take Profit: {best_long_takeprofit}")
            print(f"Best Short Stop Loss: {best_short_stoploss}")
            print(f"Best Short Take Profit: {best_short_takeprofit}\n")
        except (UnboundLocalError, ValueError):
            print("error printing stoploss and take profit.")

    def print_net_profit(self):
        """print net profit to console."""
        net_profit = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_element(By.TAG_NAME, "tr")
            .find_elements(By.TAG_NAME, "td")[1]
            .find_elements(By.TAG_NAME, "div")[2]
        )
        print(f"Net Profit: {net_profit.text}")

    def print_gross_profit(self):
        """print gross profit to console."""
        gross_profit = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[1]
            .find_elements(By.TAG_NAME, "td")[1]
            .find_elements(By.TAG_NAME, "div")[2]
        )
        print(f"Gross Profit: {gross_profit.text}")

    def print_gross_loss(self):
        """print gross loss to console."""
        gross_loss = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[2]
            .find_elements(By.TAG_NAME, "td")[1]
            .find_elements(By.TAG_NAME, "div")[2]
        )
        print(f"Gross Loss: {gross_loss.text}")

    def print_max_runup(self):
        """print max run up to console."""
        max_runup = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[3]
            .find_elements(By.TAG_NAME, "td")[1]
            .find_elements(By.TAG_NAME, "div")[2]
        )
        print(f"Max Run Up: {max_runup.text}")

    def print_max_drawdown(self):
        """print max drawdown to console."""
        max_drawdown = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[4]
            .find_elements(By.TAG_NAME, "td")[1]
            .find_elements(By.TAG_NAME, "div")[2]
        )
        print(f"Max Drawdown: {max_drawdown.text}")

    def print_buy_and_hold_return(self):
        """print buy and hold return to console."""
        buy_and_hold_return = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[5]
            .find_elements(By.TAG_NAME, "td")[1]
            .find_elements(By.TAG_NAME, "div")[2]
        )
        print(f"Buy & Hold Return: {buy_and_hold_return.text}")

    def print_sharpe_ratio(self):
        """print sharpe ratio to console."""
        sharpe_ratio = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[6]
            .find_elements(By.TAG_NAME, "td")[1]
        )
        print(f"Sharpe Ratio: {sharpe_ratio.text}")

    def print_sortino_ratio(self):
        """print sortino ratio to console."""
        sortino_ratio = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[7]
            .find_elements(By.TAG_NAME, "td")[1]
        )
        print(f"Sortino Ratio: {sortino_ratio.text}")

    def print_profit_factor(self):
        """print profit factor to console."""
        profit_factor = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[8]
            .find_elements(By.TAG_NAME, "td")[1]
        )
        print(f"Profit Factor: {profit_factor.text}")

    def print_max_contracts_held(self):
        """print max contract to console."""
        max_contracts_held = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[9]
            .find_elements(By.TAG_NAME, "td")[1]
        )
        print(f"Max Contracts Held: {max_contracts_held.text}")

    def print_open_pl(self):
        """print open pl to console."""
        open_pl = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[10]
            .find_elements(By.TAG_NAME, "td")[1]
            .find_elements(By.TAG_NAME, "div")[2]
        )
        print(f"Open PL: {open_pl.text}")

    def print_commission_paid(self):
        """print commission paid to console."""
        commission_paid = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[11]
            .find_elements(By.TAG_NAME, "td")[1]
        )
        print(f"Commission Paid: {commission_paid.text}")

    def print_total_closed_trades(self):
        """print total closed trades to console."""
        total_closed_trades = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[12]
            .find_elements(By.TAG_NAME, "td")[1]
        )
        print(f"Total Closed Trades: {total_closed_trades.text}")

    def print_total_open_trades(self):
        """print total open trades to console."""
        total_open_trades = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[13]
            .find_elements(By.TAG_NAME, "td")[1]
        )
        print(f"Total Open Trades: {total_open_trades.text}")

    def print_number_winning_trades(self):
        """print number of winning trades to console."""
        number_winning_trades = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[14]
            .find_elements(By.TAG_NAME, "td")[1]
        )
        print(f"Number Winning Trades: {number_winning_trades.text}")

    def print_number_losing_trades(self):
        """print number of losing trades to console."""
        number_losing_trades = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[15]
            .find_elements(By.TAG_NAME, "td")[1]
        )
        print(f"Number Losing Trades: {number_losing_trades.text}")

    def print_percent_profitable(self):
        """print percent profitable to console."""
        percent_profitable = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[16]
            .find_elements(By.TAG_NAME, "td")[1]
        )
        print(f"Percent Profitable: {percent_profitable.text}")

    def print_avg_trade(self):
        """print average trade to console."""
        avg_trade = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[17]
            .find_elements(By.TAG_NAME, "td")[1]
            .find_elements(By.TAG_NAME, "div")[2]
        )
        print(f"Avg Trade: {avg_trade.text}")

    def print_avg_win_trade(self):
        """print average winning trades to console."""
        avg_win_ratio = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[18]
            .find_elements(By.TAG_NAME, "td")[1]
            .find_elements(By.TAG_NAME, "div")[2]
        )
        print(f"Avg Win Trade: {avg_win_ratio.text}")

    def print_avg_loss_trade(self):
        """print average losing trades to console."""
        avg_loss_ratio = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[19]
            .find_elements(By.TAG_NAME, "td")[1]
            .find_elements(By.TAG_NAME, "div")[2]
        )
        print(f"Avg Loss Trade: {avg_loss_ratio.text}")

    def print_win_loss_ratio(self):
        """print win/loss ratio to console."""
        win_loss_ratio = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[20]
            .find_elements(By.TAG_NAME, "td")[1]
            .find_element(By.TAG_NAME, "div")
        )
        print(f"Win/Loss Ratio: {win_loss_ratio.text}")

    def print_largest_winning_trade(self):
        """print largest winning trade to console."""
        largest_winning_trade = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[21]
            .find_elements(By.TAG_NAME, "td")[1]
            .find_elements(By.TAG_NAME, "div")[2]
        )
        print(f"Largest Win Trade: {largest_winning_trade.text}")

    def print_largest_losing_trade(self):
        """print largest losing trade to console."""
        largest_losing_trade = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[22]
            .find_elements(By.TAG_NAME, "td")[1]
            .find_elements(By.TAG_NAME, "div")[2]
        )
        print(f"Largest Loss Trade: {largest_losing_trade.text}")

    def print_avg_bars_in_trades(self):
        """print average bars to console."""
        avg_bars_in_trades = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[23]
            .find_elements(By.TAG_NAME, "td")[1]
        )
        print(f"Avg Bars In Trades: {avg_bars_in_trades.text}")

    def print_avg_bars_in_winning_trades(self):
        """print average bars of winning trades to console."""
        avg_bars_in_winning_trades = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[24]
            .find_elements(By.TAG_NAME, "td")[1]
        )
        print(f"Avg Bars In Winning Trades: {avg_bars_in_winning_trades.text}")

    def print_avg_bars_in_losing_trades(self):
        """print average bars of losing trades to console."""
        avg_bars_in_losing_trades = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[25]
            .find_elements(By.TAG_NAME, "td")[1]
        )
        print(f"Avg Bars In Losing Trades: {avg_bars_in_losing_trades.text}")

    def print_win_rate(self):
        """print win rate to console."""
        win_rate = (
            self.driver.find_element(By.CLASS_NAME, "ka-tbody")
            .find_elements(By.TAG_NAME, "tr")[16]
            .find_elements(By.TAG_NAME, "td")[1]
        )
        print(f"Win Rate: {win_rate.text}")

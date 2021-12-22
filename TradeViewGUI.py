import json

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager


class Main:
    def __init__(self):
        self.driver = self.create_driver()
        self.optimize_longs_shorts()

    def create_driver(self):
        """Creating driver."""
        options = Options()
        options.headless = False
        profile = webdriver.FirefoxProfile("/Users/m/Library/Application Support/Firefox/Profiles/8uuc8ma2.default")
        driver = webdriver.Firefox(
            profile, options=options, executable_path=GeckoDriverManager().install()
        )
        return driver

    def optimize_longs_shorts(self):
        import OptimizeLongsShorts
        params = self.loadIndicatorParams()
        OptimizeLongsShorts.LongShortScript(self.driver, params)


    def loadIndicatorParams(self):
        with open('indicator-params/test-stg.json') as json_file:
            return json.load(json_file)


def main():
    Main()


if __name__ == "__main__":
    main()

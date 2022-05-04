import sys
from distutils.util import strtobool

from PyQt5 import uic
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QWidget,
)
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("tradingview.ui", self)
        self.settings = QSettings("TradingviewOptimizer", "Strategy Parameters")
        self.gui_restore()
        self.pushButton.clicked.connect(self.optimize_longs_shorts)
        self.pushButton.clicked.connect(self.optimize_long)
        self.pushButton.clicked.connect(self.optimize_long_stoploss)
        self.pushButton.clicked.connect(self.optimize_long_takeprofit)
        self.pushButton.clicked.connect(self.optimize_short)
        self.pushButton.clicked.connect(self.optimize_short_stoploss)
        self.pushButton.clicked.connect(self.optimize_short_takeprofit)
        self.minLongStoplossValue.textChanged.connect(self.gui_save)
        self.maxLongStoplossValue.textChanged.connect(self.gui_save)
        self.minLongTakeprofitValue.textChanged.connect(self.gui_save)
        self.maxLongTakeprofitValue.textChanged.connect(self.gui_save)
        self.LongIncrementValue.textChanged.connect(self.gui_save)
        self.minShortStoplossValue.textChanged.connect(self.gui_save)
        self.maxShortStoplossValue.textChanged.connect(self.gui_save)
        self.minShortTakeprofitValue.textChanged.connect(self.gui_save)
        self.maxShortTakeprofitValue.textChanged.connect(self.gui_save)
        self.ShortIncrementValue.textChanged.connect(self.gui_save)
        self.decimalPlaceValue.textChanged.connect(self.gui_save)
        self.maxAttemptsValue.textChanged.connect(self.gui_save)
        self.firefoxProfileString.textChanged.connect(self.gui_save)
        self.FirefoxcheckBox.stateChanged.connect(self.gui_save)
        self.comboBox.currentTextChanged.connect(self.comboBoxSelection)

        if self.comboBox.currentIndex() == 0:
            self.minLongStoplossValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxLongStoplossValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.minLongTakeprofitValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxLongTakeprofitValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.LongIncrementValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.minShortStoplossValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxShortStoplossValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.minShortTakeprofitValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxShortTakeprofitValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.ShortIncrementValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.decimalPlaceValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxAttemptsValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.minLongStoplossValue.setEnabled(True)
            self.maxLongStoplossValue.setEnabled(True)
            self.minLongTakeprofitValue.setEnabled(True)
            self.maxLongTakeprofitValue.setEnabled(True)
            self.minShortStoplossValue.setEnabled(True)
            self.maxShortStoplossValue.setEnabled(True)
            self.minShortTakeprofitValue.setEnabled(True)
            self.maxShortTakeprofitValue.setEnabled(True)
            self.decimalPlaceValue.setEnabled(True)
            self.maxAttemptsValue.setEnabled(True)
            self.LongIncrementValue.setEnabled(False)
            self.ShortIncrementValue.setEnabled(False)

    def create_driver(self):
        """Creating driver."""
        try:
            options = Options()
            if self.FirefoxcheckBox.isChecked():
                options.headless = True
            elif not self.FirefoxcheckBox.isChecked():
                options.headless = False
            profile = webdriver.FirefoxProfile(self.firefoxProfileString.text())
            driver = webdriver.Firefox(
                profile, options=options, executable_path=GeckoDriverManager().install()
            )
            return driver
        except Exception:
            pass

    def gui_save(self):
        for obj in self.findChildren(QWidget):
            if isinstance(obj, QLineEdit):
                name = obj.objectName()
                value = obj.text()
                self.settings.setValue(name, value)
            if isinstance(obj, QCheckBox):
                name = obj.objectName()
                state = obj.isChecked()
                self.settings.setValue(name, state)

    def gui_restore(self):
        for obj in self.findChildren(QWidget):
            if isinstance(obj, QLineEdit):
                name = obj.objectName()
                value = self.settings.value(name)
                obj.setText(value)
            if isinstance(obj, QCheckBox):
                name = obj.objectName()
                value = self.settings.value(name)  # get stored value from registry
                if value is not None:
                    obj.setChecked(strtobool(value))  # restore checkbox

    def closeEvent(self, event):
        msgBox = QMessageBox(
            QMessageBox.Warning,
            "Window Close",
            "Are you sure you want to close the window?",
            buttons=QMessageBox.Yes | QMessageBox.No,
        )
        msgBox.setDefaultButton(QMessageBox.No)
        msgBox.exec_()
        reply = msgBox.standardButton(msgBox.clickedButton())
        if reply == QMessageBox.Yes:
            event.accept()
            self.gui_save()
        else:
            event.ignore()

    def optimize_longs_shorts(self):
        if self.comboBox.currentIndex() == 0:
            from scripts import OptimizeLongsShorts

            OptimizeLongsShorts.LongShortScript()

    def optimize_long(self):
        if self.comboBox.currentIndex() == 1:
            from scripts import OptimizeLong

            OptimizeLong.LongScript()

    def optimize_short(self):
        if self.comboBox.currentIndex() == 2:
            from scripts import OptimizeShort

            OptimizeShort.ShortScript()

    def optimize_long_stoploss(self):
        if self.comboBox.currentIndex() == 3:
            from scripts import OptimizeLongStoploss

            OptimizeLongStoploss.LongStoploss()

    def optimize_long_takeprofit(self):
        if self.comboBox.currentIndex() == 4:
            from scripts import OptimizeLongTakeprofit

            OptimizeLongTakeprofit.LongTakeProfit()

    def optimize_short_stoploss(self):
        if self.comboBox.currentIndex() == 5:
            from scripts import OptimizeShortStoploss

            OptimizeShortStoploss.ShortStoploss()

    def optimize_short_takeprofit(self):
        if self.comboBox.currentIndex() == 6:
            from scripts import OptimizeShortTakeprofit

            OptimizeShortTakeprofit.ShortTakeProfit()

    def comboBoxSelection(self):
        if self.comboBox.currentIndex() == 0:
            self.minLongStoplossValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxLongStoplossValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.minLongTakeprofitValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxLongTakeprofitValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.LongIncrementValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.minShortStoplossValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxShortStoplossValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.minShortTakeprofitValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxShortTakeprofitValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.ShortIncrementValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.decimalPlaceValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxAttemptsValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.minLongStoplossValue.setEnabled(True)
            self.maxLongStoplossValue.setEnabled(True)
            self.minLongTakeprofitValue.setEnabled(True)
            self.maxLongTakeprofitValue.setEnabled(True)
            self.minShortStoplossValue.setEnabled(True)
            self.maxShortStoplossValue.setEnabled(True)
            self.minShortTakeprofitValue.setEnabled(True)
            self.maxShortTakeprofitValue.setEnabled(True)
            self.decimalPlaceValue.setEnabled(True)
            self.maxAttemptsValue.setEnabled(True)
            self.LongIncrementValue.setEnabled(False)
            self.ShortIncrementValue.setEnabled(False)

        if self.comboBox.currentIndex() == 1:
            self.minLongStoplossValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxLongStoplossValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.minLongTakeprofitValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxLongTakeprofitValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.LongIncrementValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.minShortStoplossValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxShortStoplossValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.minShortTakeprofitValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxShortTakeprofitValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.ShortIncrementValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.decimalPlaceValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxAttemptsValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.minLongStoplossValue.setEnabled(True)
            self.maxLongStoplossValue.setEnabled(True)
            self.minLongTakeprofitValue.setEnabled(True)
            self.maxLongTakeprofitValue.setEnabled(True)
            self.LongIncrementValue.setEnabled(False)
            self.minShortStoplossValue.setEnabled(False)
            self.maxShortStoplossValue.setEnabled(False)
            self.minShortTakeprofitValue.setEnabled(False)
            self.maxShortTakeprofitValue.setEnabled(False)
            self.ShortIncrementValue.setEnabled(False)
            self.decimalPlaceValue.setEnabled(True)
            self.maxAttemptsValue.setEnabled(True)

        if self.comboBox.currentIndex() == 2:
            self.minLongStoplossValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxLongStoplossValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.minLongTakeprofitValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxLongTakeprofitValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.LongIncrementValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.minShortStoplossValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxShortStoplossValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.minShortTakeprofitValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxShortTakeprofitValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.ShortIncrementValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.decimalPlaceValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxAttemptsValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.minLongStoplossValue.setEnabled(False)
            self.maxLongStoplossValue.setEnabled(False)
            self.minLongTakeprofitValue.setEnabled(False)
            self.maxLongTakeprofitValue.setEnabled(False)
            self.LongIncrementValue.setEnabled(False)
            self.minShortStoplossValue.setEnabled(True)
            self.maxShortStoplossValue.setEnabled(True)
            self.minShortTakeprofitValue.setEnabled(True)
            self.maxShortTakeprofitValue.setEnabled(True)
            self.ShortIncrementValue.setEnabled(False)
            self.decimalPlaceValue.setEnabled(True)
            self.maxAttemptsValue.setEnabled(True)

        if self.comboBox.currentIndex() == 3:
            self.minLongStoplossValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxLongStoplossValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.minLongTakeprofitValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxLongTakeprofitValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.LongIncrementValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )

            self.minShortStoplossValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxShortStoplossValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.minShortTakeprofitValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxShortTakeprofitValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.ShortIncrementValue.setStyleSheet("color: rgb(21, 21, 47)")

            self.decimalPlaceValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxAttemptsValue.setStyleSheet("color: rgb(21, 21, 47)")

            self.minLongStoplossValue.setEnabled(True)
            self.maxLongStoplossValue.setEnabled(True)
            self.minLongTakeprofitValue.setEnabled(False)
            self.maxLongTakeprofitValue.setEnabled(False)
            self.LongIncrementValue.setEnabled(True)

            self.minShortStoplossValue.setEnabled(False)
            self.maxShortStoplossValue.setEnabled(False)
            self.minShortTakeprofitValue.setEnabled(False)
            self.maxShortTakeprofitValue.setEnabled(False)
            self.ShortIncrementValue.setEnabled(False)

            self.decimalPlaceValue.setEnabled(False)
            self.maxAttemptsValue.setEnabled(False)

        if self.comboBox.currentIndex() == 4:
            self.minLongStoplossValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxLongStoplossValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.minLongTakeprofitValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxLongTakeprofitValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.LongIncrementValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.minShortStoplossValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxShortStoplossValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.minShortTakeprofitValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxShortTakeprofitValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.ShortIncrementValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.decimalPlaceValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxAttemptsValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.minLongStoplossValue.setEnabled(False)
            self.maxLongStoplossValue.setEnabled(False)
            self.minLongTakeprofitValue.setEnabled(True)
            self.maxLongTakeprofitValue.setEnabled(True)
            self.LongIncrementValue.setEnabled(True)
            self.minShortStoplossValue.setEnabled(False)
            self.maxShortStoplossValue.setEnabled(False)
            self.minShortTakeprofitValue.setEnabled(False)
            self.maxShortTakeprofitValue.setEnabled(False)
            self.ShortIncrementValue.setEnabled(False)
            self.decimalPlaceValue.setEnabled(False)
            self.maxAttemptsValue.setEnabled(False)

        if self.comboBox.currentIndex() == 5:
            self.minLongStoplossValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxLongStoplossValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.minLongTakeprofitValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxLongTakeprofitValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.LongIncrementValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.minShortStoplossValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxShortStoplossValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.minShortTakeprofitValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxShortTakeprofitValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.ShortIncrementValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.decimalPlaceValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxAttemptsValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.minLongStoplossValue.setEnabled(False)
            self.maxLongStoplossValue.setEnabled(False)
            self.minLongTakeprofitValue.setEnabled(False)
            self.maxLongTakeprofitValue.setEnabled(False)
            self.LongIncrementValue.setEnabled(False)
            self.minShortStoplossValue.setEnabled(True)
            self.maxShortStoplossValue.setEnabled(True)
            self.minShortTakeprofitValue.setEnabled(False)
            self.maxShortTakeprofitValue.setEnabled(False)
            self.ShortIncrementValue.setEnabled(True)
            self.decimalPlaceValue.setEnabled(False)
            self.maxAttemptsValue.setEnabled(False)

        if self.comboBox.currentIndex() == 6:
            self.minLongStoplossValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxLongStoplossValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.minLongTakeprofitValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxLongTakeprofitValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.LongIncrementValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.minShortStoplossValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxShortStoplossValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.minShortTakeprofitValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.maxShortTakeprofitValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.ShortIncrementValue.setStyleSheet(
                "background-color: rgb(21, 21, 47); color: rgb(170, 255, 255);"
            )
            self.decimalPlaceValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.maxAttemptsValue.setStyleSheet("color: rgb(21, 21, 47)")
            self.minLongStoplossValue.setEnabled(False)
            self.maxLongStoplossValue.setEnabled(False)
            self.minLongTakeprofitValue.setEnabled(False)
            self.maxLongTakeprofitValue.setEnabled(False)
            self.LongIncrementValue.setEnabled(False)
            self.minShortStoplossValue.setEnabled(False)
            self.maxShortStoplossValue.setEnabled(False)
            self.minShortTakeprofitValue.setEnabled(True)
            self.maxShortTakeprofitValue.setEnabled(True)
            self.ShortIncrementValue.setEnabled(True)
            self.decimalPlaceValue.setEnabled(False)
            self.maxAttemptsValue.setEnabled(False)


def main():
    app = QApplication(sys.argv)
    win = Main()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

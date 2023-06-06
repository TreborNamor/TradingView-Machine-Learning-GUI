# TradingView Machine Learning GUI

## Project Overview

This project primarily features a stop loss/take profit generator capable of determining the optimal parameters for your TradingView strategy. Additionally, it incorporates machine learning algorithms, using sklearn, to hyper-optimize your TradingView strategy. The project includes a comprehensive range of ratios, such as Sharpe, Sortino, Calmar, Information, Treynor, and Max Profit, providing a multifaceted approach to strategy optimization. Another key feature is the next-day closing price predictor, a script that empowers you to forecast the following day's closing price accurately. Please refer to the machine learning directory to access the stored pictures or examine the comments in the source code for a clearer understanding. To ensure user-friendliness and accessibility for traders of all expertise levels, the project includes a Graphical User Interface (GUI). [Here is live example of TradeView](https://vimeo.com/594037879)

![image](https://github.com/TreborNamor/TradingView_Machine_Learning/blob/16ab9d3fae94258a715965e271d5c80b6517051c/pictures/TradeViewGUI.png)
![image](https://github.com/TreborNamor/TradingView_Machine_Learning/blob/16ab9d3fae94258a715965e271d5c80b6517051c/pictures/TradeViewResultsExample.png)

## Disclaimer

This software is for educational purposes only. Do not risk money which
you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS
AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.

We strongly recommend you to have coding and Python knowledge. Do not
hesitate to read the source code and understand the mechanism of this bot.

## Installation Instructions

#1. Download Firefox, and TradingView_Machine_Learning folder here.

[FireFox](https://www.mozilla.org/en-US/firefox/new/)

[TradingView_Machine Learning](https://github.com/TreborNamor/TradingView_Machine_Learning/archive/master.zip)

#2. Extract zip file to Desktop and Execute TradeViewGUI.exe file.

![image](https://github.com/TreborNamor/TradingView_Machine_Learning/blob/bd4a703fb0b3ec964c305dd7c720b17b111535fc/pictures/extractZip.png)

#3. Copy and Paste Firefox Profile Path to App.
![image](https://github.com/TreborNamor/TradingView_Machine_Learning/blob/16ab9d3fae94258a715965e271d5c80b6517051c/pictures/FindFirefoxPath.png)
![image](https://github.com/TreborNamor/TradingView_Machine_Learning/blob/bd4a703fb0b3ec964c305dd7c720b17b111535fc/pictures/addPath.png)

#4. Inside Firefox, login into your TradingView profile. Go to your TradingView chart and add the TradingView strategy you want to optimize. When you add the strategy to chart make sure to press CTRL + S on your keyboard to save your chart. I have a TradingView Strategy that is ready to use. You can browse the strategy source code [here.](https://github.com/TreborNamor/TradingView-Machine-Learning-GUI/blob/master/tv_strategies/MACD-RSI%20%20Strategy)
If you want to create a custom TradingView Strategy click [here.](https://github.com/TreborNamor/TradingView-Machine-Learning-GUI/blob/master/tv_strategies/Create%20Your%20Own%20Strategy%20For%20Optimization.txt)
![image](https://github.com/TreborNamor/TradingView-Machine-Learning-GUI/blob/cee46135f1f0d8656c9f1614abb334d8205a6110/pictures/addStrategy.png)

#5. Enter Your long and short parameters and click Run button.
![image](https://github.com/TreborNamor/TradingView_Machine_Learning/blob/bd4a703fb0b3ec964c305dd7c720b17b111535fc/pictures/parameters.png)

## Tips:
- CheckBox: You can hide Firefox browser when checkbox is enabled.
- Minimum Long Stoploss: The minimum percentage you are willing to risk for your strategy. For example, a 1% minimum risk.
- Maximum Long Stoploss: The maximum percentage you are willing to risk for your strategy. For example, a 30% maximum risk.
- Minimum Long Takeprofit: The minimum percentage you are willing to risk for your strategy. For example, a 1% minimum risk.
- Maximum Long Takeprofit: The maximum percentage you are willing to risk for your strategy. For example, a 30% maximum risk.
-Long Increment: When option is available, do you want the strategy to increment in steps of 1 or .1 during parameter search. (Default is set to .1)

- Minimum Short Stoploss: The minimum percentage you are willing to risk for your strategy. For example, a 1% minimum risk.
- Maximum Short Stoploss: The maximum percentage you are willing to risk for your strategy. For example, a 30% maximum risk.
- Minimum Short Takeprofit: The minimum percentage you are willing to risk for your strategy. For example, a 1% minimum risk.
- Maximum Short Takeprofit: The maximum percentage you are willing to risk for your strategy. For example, a 30% maximum risk.
- Short Increment: When option is available, do you want the strategy to increment in steps of 1 or .1 during parameter search. (Default is set to .1)

- Decimal Place: When option is available, by what decimal place would you like during strategy search. (Default is set to 1)
- Max Attempts: What is the maximum amount of attempts would you like the strategy try. (Default is set to 30)
- Firefox Path: The path used to run selenium webdriver.

## Contributing

We welcome contributions from the community. If you wish to contribute:

1. Fork the repository.
2. Create a new branch for your changes.
3. Make the changes/additions.
4. Commit your changes.
5. Push the changes to your forked repository.
6. Open a pull request from your forked repository to this repository.

Please ensure your code adheres to our coding standards and passes all tests before submitting a pull request.

## License

This project is licensed under the [MIT License](https://github.com/TreborNamor/TradingView-Machine-Learning-GUI/blob/master/LICENSE). 

## Contact Information

For any questions, feedback, or discussions, feel free to reach out to me:

- Email: robertroman7@gmail.com
- LinkedIn: [Profile](https://www.linkedin.com/in/robert-roman7/)

## Acknowledgements

Thanks to all contributors and users for making this project possible. If you find this project helpful, please consider starring the repository to show your support.

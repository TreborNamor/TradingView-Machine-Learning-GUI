"""
    This code reads historical stock price data from a CSV file and processes it to extract relevant features such as open,
    high, low, and close prices. It then trains an Extra Trees Regressor model using these features to predict the close
    price of the stock for the next day. The model is built using the best hyperparameters obtained through a previous
    GridSearchCV process. After training the model with stock_predictions grid parameters, input the best params into
    this model then input the current day's open, high, low, and close prices to predict the close price for the next day.
    The predicted closing price is then printed as output. In simple terms, this code learns from historical stock price
    patterns and uses that knowledge to predict the future closing price of the stock based on the current day's price movements.
"""

import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor


"""
With the day's current price information of 4/20/2023, an attempt was made to predict the close price for 4/21/2023.
Results:
- Predicted Close Price: 412.27
- Actual Close Price: 412.20
"""

# You can find SPY historical prices for free on https://finance.yahoo.com/quote/SPY/history?p=SPY
historical_open = 411.21  # Enter the day's current open price for the model to predict its close price.
historical_high = 413.70  # Enter the day's current high price.
historical_low = 410.27   # Enter the day's current low price.
historical_close = 411.88 # Enter the day's current close price.

# Preprocessing DataFrame
df = pd.read_csv('../datasets/SPY_DATA_20_YEARS/SPX_1day.csv')
df['time'] = pd.to_datetime(df['time'], unit='s')
df.set_index(pd.DatetimeIndex(df['time']), inplace=True)
del df['time']

# Set Features and Labels
X = df[['open', 'high', 'low', 'close']]
y = df['close'].shift(-1)[:-1]
X = X[:-1]

# Remove feature names from the input DataFrame
X.columns = [None] * len(X.columns)

# Define the best hyperparameters found by GridSearchCV
best_params = {
    'n_estimators': 300,  # Use the best value found by GridSearchCV
    'max_depth': 40,     # Use the best value found by GridSearchCV
    'min_samples_split': 15,  # Use the best value found by GridSearchCV
    'min_samples_leaf': 2,   # Use the best value found by GridSearchCV
    'bootstrap': True,      # Use the best value found by GridSearchCV
    'max_features': 1.0,  # Use the best value found by GridSearchCV
}

# Create Final Model
final_model = ExtraTreesRegressor(**best_params, n_jobs=-1)

# Initialize a list to store the predictions
predictions = []

# Train the model and make predictions 10 times
for _ in range(10):
    final_model.fit(X, y)
    final_prediction = final_model.predict([[historical_open, historical_high, historical_low, historical_close]])
    predictions.append(final_prediction[0])

# Calculate the average prediction
average_prediction = sum(predictions) / len(predictions)

# Print the average predicted close price
print('Predicted Close Price:', round(average_prediction, 2))

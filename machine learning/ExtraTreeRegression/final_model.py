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

predicted_open = 422.99  # Enter the day's current open price for the model to predict its close price.
predicted_high = 424.50  # Enter the day's current high price.
predicted_low = 421.80   # Enter the day's current low price.
predicted_close = 423.25  # Enter the day's current close price.

# Preprocessing DataFrame
df = pd.read_csv('../datasets/BATS_SPY, 1D.csv')
df['time'] = pd.to_datetime(df['time'], unit='s')
df.set_index(pd.DatetimeIndex(df['time']), inplace=True)
del df['time']

# Set Features and Labels
X = df[['open', 'high', 'low', 'close']]
y = df['close'].shift(-1)[:-1]
X = X[:-1]

# Define the best hyperparameters found by GridSearchCV
best_params = {
    'n_estimators': 1000,  # Use the best value found by GridSearchCV
    'max_depth': None,     # Use the best value found by GridSearchCV
    'min_samples_split': 2,  # Use the best value found by GridSearchCV
    'min_samples_leaf': 1,   # Use the best value found by GridSearchCV
    'bootstrap': False,      # Use the best value found by GridSearchCV
    'max_features': 'sqrt',  # Use the best value found by GridSearchCV
}

# Create Final Model
final_model = ExtraTreesRegressor(**best_params, n_jobs=-1)
final_model.fit(X, y)

# Print Predicted Close Price
final_prediction = final_model.predict([[predicted_open, predicted_high, predicted_low, predicted_close]])
print('Predicted Close Price:', round(final_prediction[0], 2))

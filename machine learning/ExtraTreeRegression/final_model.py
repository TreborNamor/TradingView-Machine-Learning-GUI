"""
    The final model is intended to predict SP500 close price only.
    Use final model To predict the stock markets close price for that day.
    The final model will predict the close price based on what price the stock market opens that day.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import ExtraTreesRegressor

predicted_open = [422.99]  # Enter the days current open price for model to price its close price.

# Preprocessing DataFrame
df = pd.read_csv('../datasets/Final_SPY, 1D.csv')
df['time'] = pd.to_datetime(df['time'], unit='s')
df.set_index(pd.DatetimeIndex(df['time']), inplace=True)
del df['time']

# Set Features and Labels
X = np.array(df[['open']])
y = df['close']

# Create Final Model
final_model = ExtraTreesRegressor(n_estimators=1000, bootstrap=False, n_jobs=-1, warm_start=True)
final_model.fit(X, y)

# Print Predicted Close Price
final_prediction = final_model.predict([predicted_open])
print('Predicted Close Price: ', round(final_prediction[0], 2))

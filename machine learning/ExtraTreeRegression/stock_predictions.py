"""
    The script reads the stock data from a CSV file, preprocesses the data, splits it into training and testing sets,
    defines an Extra Trees Regressor model, performs hyperparameter tuning using GridSearchCV, trains the model with the
    best parameters, and predicts the close prices for the test set. It then calculates evaluation metrics (RMSE, MAE, and R^2),
    prints the results, and creates a candlestick chart to visualize the actual and predicted close prices, saving it as an HTML file.
"""
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split, GridSearchCV


def create_and_save_candlestick_chart(df, y_test, y_pred, filename):
    # Create candlestick chart with actual and predicted values
    candlestick = go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'],
                                 name='Candlestick Chart')

    actual_trace = go.Scatter(x=y_test.index, y=y_test, mode='markers', name='Actual Close',
                              marker=dict(color='gray', symbol='circle-open', size=9))

    predicted_trace = go.Scatter(x=y_test.index, y=y_pred, mode='markers', name='Predicted Close',
                                 marker=dict(color='purple', symbol='x'))

    data = [candlestick, actual_trace, predicted_trace]

    layout = go.Layout(title='Actual vs Predicted Close Prices', xaxis=dict(title='Time'),
                       yaxis=dict(title='Close Price'))
    fig = go.Figure(data=data, layout=layout)

    # Save Plot to HTML File
    fig.write_html(filename)

if __name__ == "__main__":
    # Read data from CSV file
    filename = '../datasets/BATS_SPY, 1D.csv'
    df = pd.read_csv(filename)

    # Prepare the input (open, high, low, close prices) and output (next day close prices) data
    X = df[['open', 'high', 'low', 'close']]
    y = df['close'].shift(-1)[:-1]

    # Remove the last row from X to match the length of y
    X = X[:-1]

    # Split the data into training and testing sets
    test_size = int(len(X) * 0.3)
    X_train, X_test = X[:-test_size], X[-test_size:]
    y_train, y_test = y[:-test_size], y[-test_size:]

    # Define the Extra Trees Regressor model with some initial parameters
    model = ExtraTreesRegressor(n_estimators=100, bootstrap=True, n_jobs=-1)

    # Define a grid of parameters to search for the best combination
    param_grid = {
        'n_estimators': [50, 100, 200, 300, 500],
        'max_depth': [None, 10, 20, 30, 40, 50],
        'min_samples_split': [2, 5, 10, 15, 20],
        'min_samples_leaf': [1, 2, 4, 6, 8],
        'bootstrap': [True, False],
        'max_features': [1.0, 'sqrt', 'log2']
    }

    # Perform GridSearchCV to find the best parameters
    grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=5, scoring='neg_mean_squared_error',
                               verbose=1, n_jobs=-1)
    grid_search.fit(X_train, y_train)

    # Print the best parameters
    best_params = grid_search.best_params_
    print("Best Parameters:", best_params)

    # Train the model with the best parameters
    best_model = ExtraTreesRegressor(**best_params, n_jobs=-1)
    best_model.fit(X_train, y_train)

    # Predict the close prices for the test set
    y_pred = best_model.predict(X_test)

    # Calculate evaluation metrics (RMSE, MAE, R^2) and print them
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"RMSE: {rmse:.2f}")
    print(f"MAE: {mae:.2f}")
    print(f"R^2: {r2:.2f}")

    # Call the function with the appropriate arguments
    filename = 'pictures/actual_vs_predicted_close_prices.html'
    create_and_save_candlestick_chart(df, y_test, y_pred, filename)

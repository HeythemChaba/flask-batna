import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

class ForecastingModel:
    def __init__(self, df, date_col, sales_col):
        """
        Initialize the forecasting model with a DataFrame.
        :param df: DataFrame containing the dataset.
        :param date_col: Column name for the date.
        :param sales_col: Column name for the sales.
        """
        self.df = df
        self.date_col = date_col
        self.sales_col = sales_col
        self.model = None
        self.daily_sales = None

    def preprocess_data(self):
        """
        Groups the data by day, summing the sales.
        """
        # Ensure date column is in datetime format
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])

        # Group by day and sum sales
        self.daily_sales = self.df.groupby(self.date_col)[self.sales_col].sum().reset_index()
        self.daily_sales.columns = ["date", "total_sales"]

    def train_model(self):
        """
        Trains an XGBoost model to forecast daily sales.
        :return: Trained XGBRegressor model, RMSE score, and test predictions.
        """
        # Generate lag features
        for lag in range(1, 8):  # Create lags for the past 7 days
            self.daily_sales[f"lag_{lag}"] = self.daily_sales["total_sales"].shift(lag)

        # Drop NaN values caused by lagging
        self.daily_sales.dropna(inplace=True)

        # Prepare features and target
        X = self.daily_sales.drop(columns=["date", "total_sales"])
        y = self.daily_sales["total_sales"]

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

        # Train XGBoost model
        self.model = XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)

        # Make predictions
        y_pred = self.model.predict(X_test)

        # Evaluate the model
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        return rmse, pd.DataFrame({"date": self.daily_sales["date"].iloc[y_test.index],
                                   "actual": y_test, "predicted": y_pred})

    def get_forecast_results(self):
        """
        Processes data, trains the model, and returns results.
        :return: RMSE score and DataFrame of predictions.
        """
        self.preprocess_data()
        rmse, predictions = self.train_model()
        return rmse, predictions.to_dict(orient="records")

    def forecast_next_period(self, periods, freq='D'):
        """
        Forecast future sales for a given number of periods.
        :param periods: Number of future periods to predict.
        :param freq: Frequency of the periods ('D' for daily, 'W' for weekly, etc.).
        :return: DataFrame containing the forecasted values.
        """
        future_dates = pd.date_range(start=self.daily_sales["date"].iloc[-1] + pd.Timedelta(days=1), periods=periods, freq=freq)
        forecast_df = pd.DataFrame({"date": future_dates})

        last_known_values = self.daily_sales.iloc[-7:]["total_sales"].values.tolist()

        forecasts = []
        for _ in range(periods):
            # Prepare input features for the next prediction
            features = np.array(last_known_values[-7:]).reshape(1, -1)

            # Predict the next value
            next_forecast = self.model.predict(features)[0]
            forecasts.append(next_forecast)

            # Update the known values with the predicted value
            last_known_values.append(next_forecast)

        forecast_df["forecasted_sales"] = forecasts
        return forecast_df

    def forecast_next_week(self):
        """
        Forecast sales for the next 7 days.
        :return: DataFrame containing the forecasted values for the next week.
        """
        return self.forecast_next_period(periods=7, freq='D')

    def forecast_next_month(self):
        """
        Forecast sales for the next month (30 days).
        :return: DataFrame containing the forecasted values for the next month.
        """
        return self.forecast_next_period(periods=30, freq='D')

    def forecast_next_year(self):
        """
        Forecast sales for the next year (365 days).
        :return: DataFrame containing the forecasted values for the next year.
        """
        return self.forecast_next_period(periods=365, freq='D')

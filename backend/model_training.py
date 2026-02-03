import yfinance as yf
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from xgboost import XGBRegressor

class StockDataProcessor:
    def __init__(self, ticker, start_date='2020-01-01'):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = pd.Timestamp.today().strftime('%Y-%m-%d')
        self.data = None

    def load_data(self):
        self.data = yf.download(self.ticker, start=self.start_date, end=self.end_date)
        if self.data.empty:
            raise ValueError(f"No data for {self.ticker}")
        return True

    def add_features(self):
        self.data['MA50'] = self.data['Close'].rolling(50).mean()
        self.data['MA100'] = self.data['Close'].rolling(100).mean()
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))
        self.data.dropna(inplace=True)
        features = ['Open', 'High', 'Low', 'Volume', 'MA50', 'MA100', 'RSI']
        self.data = self.data[features + ['Close']]
        return self.data

class StockPredictor:
    def __init__(self):
        self.models = {
            'lr': LinearRegression(),
            'rf': RandomForestRegressor(n_estimators=100, random_state=42),
            'xgb': XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
        }
        self.best_model = None

    def train_models(self, df):
        X = df.drop('Close', axis=1)
        y = df['Close']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        best_score = float('-inf')
        for name, model in self.models.items():
            model.fit(X_train, y_train)
            score = r2_score(y_test, model.predict(X_test))
            if score > best_score:
                best_score = score
                self.best_model = model

    def predict_future(self, last_features):
        results = {}
        current_features = last_features.copy()
        for horizon in [3,6,9,12]:
            pred = self.best_model.predict([current_features])[0]
            results[f"{horizon} months"] = float(pred)
            current_features[0] = pred
            current_features[1] = pred
            current_features[2] = pred
        return results

class StockPredictionSystem:
    def __init__(self, ticker):
        self.processor = StockDataProcessor(ticker)
        self.predictor = StockPredictor()
        self.initialized = False

    def initialize(self):
        self.processor.load_data()
        self.processor.add_features()
        self.predictor.train_models(self.processor.data)
        self.initialized = True

    def predict_future_prices(self):
        if not self.initialized:
            raise ValueError("System not initialized")
        last_features = self.processor.data.drop('Close', axis=1).iloc[-1].values
        return self.predictor.predict_future(last_features)

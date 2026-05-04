import pandas as pd
from sklearn.preprocessing import MinMaxScaler, LabelEncoder


class BaseDatasetLoader:

    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None

    def load(self):
        self.df = pd.read_csv(self.file_path)
        return self.df

    def clean(self):
        # Remove duplicates & NaN
        self.df = self.df.drop_duplicates()
        self.df = self.df.dropna()
        return self.df

    def encode(self):
        for col in self.df.select_dtypes(include=['object']).columns:
            le = LabelEncoder()
            self.df[col] = le.fit_transform(self.df[col])
        return self.df

    def normalize(self):
        scaler = MinMaxScaler()
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
        self.df[numeric_cols] = scaler.fit_transform(self.df[numeric_cols])
        return self.df

    def preprocess(self):
        self.load()
        self.clean()
        self.encode()
        self.normalize()
        return self.df
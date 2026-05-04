from .base_loader import BaseDatasetLoader


class CICIoTLoader(BaseDatasetLoader):

    def __init__(self, path):
        super().__init__(path)

    def get_features_labels(self):
        df = self.preprocess()

        X = df.drop(columns=["label"])
        y = df["label"]

        return X.values, y.values
import pandas as pd
from src.preprocess import clean_data, engineer_features


def test_clean_data_removes_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2], "b": [3, 3, 4]})
    result = clean_data(df)
    assert len(result) == 2


def test_engineer_features_returns_dataframe():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    result = engineer_features(df)
    assert isinstance(result, pd.DataFrame)

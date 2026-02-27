import pandas as pd
import numpy as np


def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    # TODO: drop duplicates, handle nulls, fix dtypes
    df = df.drop_duplicates()
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    # TODO: encode categoricals, extract amenity counts, etc.
    return df


def preprocess(input_path: str, output_path: str) -> pd.DataFrame:
    df = load_data(input_path)
    df = clean_data(df)
    df = engineer_features(df)
    df.to_csv(output_path, index=False)
    return df


if __name__ == "__main__":
    preprocess("data/raw/listings.csv", "data/processed/listings_clean.csv")

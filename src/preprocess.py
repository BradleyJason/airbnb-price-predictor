import re
import warnings
import pandas as pd

COLUMNS = [
    "price",
    "room_type",
    "neighbourhood_cleansed",
    "accommodates",
    "bedrooms",
    "bathrooms_text",
    "number_of_reviews",
    "review_scores_rating",
    "availability_365",
    "minimum_nights",
]


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    return df


def select_columns(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in dataset: {missing}")
    return df[COLUMNS].copy()


def clean_price(df: pd.DataFrame) -> pd.DataFrame:
    """Remove '$' and ',' then cast to float. Drop rows where price is null."""
    df["price"] = (
        df["price"]
        .str.replace(r"[\$,]", "", regex=True)
        .str.strip()
        .replace("", pd.NA)
    )
    before = len(df)
    df = df.dropna(subset=["price"])
    df["price"] = df["price"].astype(float)
    dropped = before - len(df)
    if dropped > 0:
        warnings.warn(
            f"Dropped {dropped} rows with missing price "
            f"({dropped / before:.1%} of dataset)."
        )
    if len(df) == 0:
        raise ValueError(
            "The 'price' column is empty for all rows. "
            "Download a listings.csv that includes price data "
            "(e.g. from insideairbnb.com — some recent scrapes omit prices)."
        )
    return df


def clean_bathrooms(df: pd.DataFrame) -> pd.DataFrame:
    """Extract numeric value from 'bathrooms_text' (e.g. '1.5 baths' → 1.5).
    'Half-bath' / 'Private half-bath' → 0.5, missing → median."""
    def parse(val):
        if pd.isna(val) or str(val).strip() == "":
            return None
        val = str(val).strip().lower()
        if val in ("half-bath", "private half-bath"):
            return 0.5
        match = re.search(r"(\d+\.?\d*)", val)
        return float(match.group(1)) if match else None

    df["bathrooms"] = df["bathrooms_text"].apply(parse)
    median_baths = df["bathrooms"].median()
    df["bathrooms"] = df["bathrooms"].fillna(median_baths)
    df = df.drop(columns=["bathrooms_text"])
    return df


def fill_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Fill nulls: numeric columns with median, others already handled."""
    df["bedrooms"] = pd.to_numeric(df["bedrooms"], errors="coerce")
    df["bedrooms"] = df["bedrooms"].fillna(df["bedrooms"].median())

    df["review_scores_rating"] = pd.to_numeric(
        df["review_scores_rating"], errors="coerce"
    )
    df["review_scores_rating"] = df["review_scores_rating"].fillna(
        df["review_scores_rating"].median()
    )

    numeric_cols = ["accommodates", "number_of_reviews", "availability_365", "minimum_nights"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].median())

    return df


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """Label-encode room_type and neighbourhood_cleansed."""
    df["room_type"] = df["room_type"].astype("category").cat.codes
    df["neighbourhood_cleansed"] = df["neighbourhood_cleansed"].astype("category").cat.codes
    return df


def preprocess(
    input_path: str = "data/raw/listings.csv",
    output_path: str = "data/processed/listings_clean.csv",
) -> pd.DataFrame:
    print(f"Loading data from {input_path}...")
    df = load_data(input_path)
    print(f"  Raw shape: {df.shape}")

    df = select_columns(df)
    df = clean_price(df)
    df = clean_bathrooms(df)
    df = fill_missing(df)
    df = encode_categoricals(df)

    df.to_csv(output_path, index=False)
    print(f"\nSaved cleaned data to {output_path}")
    print(f"  Final shape: {df.shape}")
    print("\n--- describe() ---")
    print(df.describe().to_string())
    return df


if __name__ == "__main__":
    preprocess()

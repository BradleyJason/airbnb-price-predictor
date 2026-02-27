"""Shared pytest fixtures for unit, integration, and e2e tests."""
import os
import sys
import pytest
import pandas as pd

# Make src/ and api/ importable without pip install
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def raw_price_df() -> pd.DataFrame:
    """Minimal DataFrame mimicking raw CSV output for price-cleaning tests."""
    return pd.DataFrame({
        "price": ["$100.00", "$1,200.00", None, "$75.50"],
    })


@pytest.fixture
def raw_bathrooms_df() -> pd.DataFrame:
    """Minimal DataFrame mimicking raw CSV output for bathrooms-cleaning tests."""
    return pd.DataFrame({
        "bathrooms_text": ["1 bath", "2 baths", "Half-bath", None],
    })


@pytest.fixture
def raw_categoricals_df() -> pd.DataFrame:
    """Minimal DataFrame with categorical columns for encoding tests."""
    return pd.DataFrame({
        "room_type": ["Entire home/apt", "Private room", "Shared room"],
        "neighbourhood_cleansed": ["Louvre", "Opéra", "Louvre"],
    })


@pytest.fixture
def full_raw_df() -> pd.DataFrame:
    """10-row DataFrame with all columns required by preprocess(), used by e2e tests."""
    return pd.DataFrame({
        "price":                  ["$100.00", "$150.00", "$200.00", "$80.00",  "$120.00",
                                   "$95.00",  "$175.00", "$60.00",  "$300.00", "$110.00"],
        "room_type":              ["Entire home/apt", "Private room", "Entire home/apt",
                                   "Shared room", "Private room", "Entire home/apt",
                                   "Hotel room", "Private room", "Entire home/apt", "Private room"],
        "neighbourhood_cleansed": ["Louvre", "Opéra", "Passy", "Louvre", "Opéra",
                                   "Passy", "Louvre", "Opéra", "Passy", "Louvre"],
        "accommodates":           ["2", "1", "4", "1", "2", "3", "2", "1", "6", "2"],
        "bedrooms":               ["1", "1", "2", None, "1", "1", "1", "1", "3", "1"],
        "bathrooms_text":         ["1 bath", "1 bath", "2 baths", "Half-bath",
                                   "1 bath", "1 bath", "1 bath", "1 bath", "2 baths", "1 bath"],
        "number_of_reviews":      ["10", "5", "20", "0", "15", "8", "3", "50", "2", "12"],
        "review_scores_rating":   ["4.5", "4.8", "4.2", None, "4.9", "4.3", "4.7", "4.1", "5.0", "4.6"],
        "availability_365":       ["100", "200", "50", "365", "0", "180", "90", "120", "30", "75"],
        "minimum_nights":         ["2", "1", "3", "1", "2", "1", "2", "1", "5", "2"],
    })

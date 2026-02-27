"""Unit tests for src/preprocess.py — no MLflow, no DagsHub, no file I/O."""
import warnings
import pytest
import pandas as pd

from src.preprocess import clean_price, clean_bathrooms, encode_categoricals


class TestCleanPrice:
    def test_values_are_floats(self, raw_price_df):
        result = clean_price(raw_price_df.copy())
        assert result["price"].dtype == float

    def test_nan_row_is_dropped(self, raw_price_df):
        # Input has 4 rows, 1 is NaN → expect 3 rows back
        result = clean_price(raw_price_df.copy())
        assert len(result) == 3

    def test_dollar_sign_and_comma_removed(self, raw_price_df):
        result = clean_price(raw_price_df.copy())
        assert 1200.0 in result["price"].values

    def test_simple_price_parsed_correctly(self, raw_price_df):
        result = clean_price(raw_price_df.copy())
        assert 75.5 in result["price"].values
        assert 100.0 in result["price"].values

    def test_all_null_raises(self):
        df = pd.DataFrame({"price": [None, None]})
        with pytest.raises(ValueError, match="empty for all rows"):
            clean_price(df)

    def test_warns_on_dropped_rows(self, raw_price_df):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            clean_price(raw_price_df.copy())
        assert any("Dropped" in str(w.message) for w in caught)


class TestCleanBathrooms:
    def test_values_are_floats(self, raw_bathrooms_df):
        result = clean_bathrooms(raw_bathrooms_df.copy())
        assert result["bathrooms"].dtype == float

    def test_half_bath_becomes_point_five(self, raw_bathrooms_df):
        result = clean_bathrooms(raw_bathrooms_df.copy())
        assert 0.5 in result["bathrooms"].values

    def test_nan_replaced_by_median(self, raw_bathrooms_df):
        result = clean_bathrooms(raw_bathrooms_df.copy())
        # No NaN should remain
        assert result["bathrooms"].isna().sum() == 0

    def test_standard_values_parsed(self, raw_bathrooms_df):
        result = clean_bathrooms(raw_bathrooms_df.copy())
        assert 1.0 in result["bathrooms"].values
        assert 2.0 in result["bathrooms"].values

    def test_bathrooms_text_column_dropped(self, raw_bathrooms_df):
        result = clean_bathrooms(raw_bathrooms_df.copy())
        assert "bathrooms_text" not in result.columns
        assert "bathrooms" in result.columns


class TestEncodeCategoricals:
    def test_room_type_is_numeric(self, raw_categoricals_df):
        result = encode_categoricals(raw_categoricals_df.copy())
        assert pd.api.types.is_numeric_dtype(result["room_type"])

    def test_neighbourhood_is_numeric(self, raw_categoricals_df):
        result = encode_categoricals(raw_categoricals_df.copy())
        assert pd.api.types.is_numeric_dtype(result["neighbourhood_cleansed"])

    def test_column_count_unchanged(self, raw_categoricals_df):
        n_cols_before = len(raw_categoricals_df.columns)
        result = encode_categoricals(raw_categoricals_df.copy())
        assert len(result.columns) == n_cols_before

    def test_codes_are_non_negative(self, raw_categoricals_df):
        result = encode_categoricals(raw_categoricals_df.copy())
        assert (result["room_type"] >= 0).all()
        assert (result["neighbourhood_cleansed"] >= 0).all()

    def test_same_category_gets_same_code(self, raw_categoricals_df):
        result = encode_categoricals(raw_categoricals_df.copy())
        # "Louvre" appears at index 0 and 2 → same code
        assert result["neighbourhood_cleansed"].iloc[0] == result["neighbourhood_cleansed"].iloc[2]

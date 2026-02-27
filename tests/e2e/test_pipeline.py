"""End-to-end test for the full preprocessing pipeline.

Runs preprocess() on a 10-row in-memory CSV (no real dataset needed)
and validates the output file's shape, columns, and data quality.
"""
import os
import tempfile
import pytest
import pandas as pd

from src.preprocess import preprocess

EXPECTED_COLUMNS = {
    "price",
    "room_type",
    "neighbourhood_cleansed",
    "accommodates",
    "bedrooms",
    "number_of_reviews",
    "review_scores_rating",
    "availability_365",
    "minimum_nights",
    "bathrooms",
}


class TestFullPipeline:
    def test_output_file_is_created(self, full_raw_df, tmp_path):
        input_csv  = tmp_path / "listings.csv"
        output_csv = tmp_path / "listings_clean.csv"
        full_raw_df.to_csv(input_csv, index=False)

        preprocess(str(input_csv), str(output_csv))

        assert output_csv.exists(), "Output CSV was not created by preprocess()"

    def test_output_has_expected_columns(self, full_raw_df, tmp_path):
        input_csv  = tmp_path / "listings.csv"
        output_csv = tmp_path / "listings_clean.csv"
        full_raw_df.to_csv(input_csv, index=False)

        preprocess(str(input_csv), str(output_csv))
        result = pd.read_csv(output_csv)

        assert set(result.columns) == EXPECTED_COLUMNS

    def test_no_nan_values_in_output(self, full_raw_df, tmp_path):
        input_csv  = tmp_path / "listings.csv"
        output_csv = tmp_path / "listings_clean.csv"
        full_raw_df.to_csv(input_csv, index=False)

        preprocess(str(input_csv), str(output_csv))
        result = pd.read_csv(output_csv)

        nan_counts = result.isna().sum()
        assert nan_counts.sum() == 0, f"NaN values found after preprocessing:\n{nan_counts[nan_counts > 0]}"

    def test_all_columns_are_numeric(self, full_raw_df, tmp_path):
        input_csv  = tmp_path / "listings.csv"
        output_csv = tmp_path / "listings_clean.csv"
        full_raw_df.to_csv(input_csv, index=False)

        preprocess(str(input_csv), str(output_csv))
        result = pd.read_csv(output_csv)

        non_numeric = [col for col in result.columns if not pd.api.types.is_numeric_dtype(result[col])]
        assert non_numeric == [], f"Non-numeric columns found: {non_numeric}"

    def test_price_column_is_positive(self, full_raw_df, tmp_path):
        input_csv  = tmp_path / "listings.csv"
        output_csv = tmp_path / "listings_clean.csv"
        full_raw_df.to_csv(input_csv, index=False)

        preprocess(str(input_csv), str(output_csv))
        result = pd.read_csv(output_csv)

        assert (result["price"] > 0).all(), "price column contains non-positive values"

    def test_output_row_count_reasonable(self, full_raw_df, tmp_path):
        input_csv  = tmp_path / "listings.csv"
        output_csv = tmp_path / "listings_clean.csv"
        full_raw_df.to_csv(input_csv, index=False)

        preprocess(str(input_csv), str(output_csv))
        result = pd.read_csv(output_csv)

        # All 10 rows have valid prices → none should be dropped
        assert len(result) == len(full_raw_df), (
            f"Expected {len(full_raw_df)} rows, got {len(result)}"
        )

    def test_preprocess_returns_dataframe(self, full_raw_df, tmp_path):
        input_csv  = tmp_path / "listings.csv"
        output_csv = tmp_path / "listings_clean.csv"
        full_raw_df.to_csv(input_csv, index=False)

        result = preprocess(str(input_csv), str(output_csv))

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

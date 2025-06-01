import pytest
import pandas as pd
import json
from datagen.core.export import DataExporter

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, None, 30],
        "join_date": pd.to_datetime(["2020-01-01", "2020-06-15", None])
    })

def test_to_csv(sample_df):
    exporter = DataExporter()
    csv_str = exporter.to_csv(sample_df)
    assert isinstance(csv_str, str)
    assert "id,name,age,join_date" in csv_str
    assert "Alice" in csv_str

def test_to_excel(sample_df):
    exporter = DataExporter()
    excel_bytes = exporter.to_excel(sample_df)
    assert isinstance(excel_bytes, bytes)
    # Optional: test content by reading with pd.read_excel
    df_read = pd.read_excel(pd.io.common.BytesIO(excel_bytes))
    pd.testing.assert_frame_equal(df_read, sample_df, check_dtype=False)

def test_to_json(sample_df):
    exporter = DataExporter()
    json_str = exporter.to_json(sample_df)
    assert isinstance(json_str, str)
    data = json.loads(json_str)
    assert isinstance(data, list)
    assert data[0]["name"] == "Alice"

def test_to_parquet(sample_df):
    exporter = DataExporter()
    parquet_bytes = exporter.to_parquet(sample_df)
    assert isinstance(parquet_bytes, bytes)
    df_read = pd.read_parquet(pd.io.common.BytesIO(parquet_bytes))
    pd.testing.assert_frame_equal(df_read, sample_df, check_dtype=False)

def test_export_with_metadata_json(sample_df):
    exporter = DataExporter()
    output = exporter.export_with_metadata(sample_df, "test_schema", format_type="json")
    result = json.loads(output)
    assert "metadata" in result
    assert "data" in result
    assert result["metadata"]["schema_name"] == "test_schema"
    assert result["metadata"]["record_count"] == len(sample_df)
    assert isinstance(result["data"], list)
    assert result["data"][0]["name"] == "Alice"

def test_export_with_metadata_other_format(sample_df):
    exporter = DataExporter()
    output = exporter.export_with_metadata(sample_df, "test_schema", format_type="other")
    metadata = json.loads(output)
    assert "schema_name" in metadata
    assert metadata["schema_name"] == "test_schema"
    assert "record_count" in metadata

import pandas as pd
import json
from io import BytesIO, StringIO
from typing import Dict, Any, List


class DataExporter:
    """Export data to various formats"""

    def to_csv(self, df: pd.DataFrame) -> str:
        """Export DataFrame to CSV string"""
        return df.to_csv(index=False)

    def to_excel(self, df: pd.DataFrame, sheet_name: str = "Data") -> bytes:
        """Export DataFrame to Excel bytes"""
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        return buffer.getvalue()

    def to_json(self, df: pd.DataFrame, orient: str = "records") -> str:
        """Export DataFrame to JSON string"""
        return df.to_json(orient=orient, date_format="iso", indent=2)

    def to_parquet(self, df: pd.DataFrame) -> bytes:
        """Export DataFrame to Parquet bytes"""
        buffer = BytesIO()
        df.to_parquet(buffer, index=False)
        return buffer.getvalue()

    def export_with_metadata(
        self, df: pd.DataFrame, schema_name: str, format_type: str = "json"
    ) -> str:
        """Export data with metadata information"""
        metadata = {
            "schema_name": schema_name,
            "record_count": len(df),
            "field_count": len(df.columns),
            "export_timestamp": pd.Timestamp.now().isoformat(),
            "missing_values": df.isnull().sum().to_dict(),
            "data_types": df.dtypes.astype(str).to_dict(),
        }

        if format_type == "json":
            result = {"metadata": metadata, "data": df.to_dict(orient="records")}
            return json.dumps(result, indent=2, default=str)
        else:
            return json.dumps(metadata, indent=2, default=str)

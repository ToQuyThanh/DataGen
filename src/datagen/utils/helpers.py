"""
Helper functions and utilities
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

def setup_logging(level: str = 'INFO') -> logging.Logger:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def validate_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze data quality metrics"""
    total_cells = df.size
    missing_cells = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()
    
    quality_report = {
        'total_records': len(df),
        'total_fields': len(df.columns),
        'missing_values': {
            'count': int(missing_cells),
            'percentage': round((missing_cells / total_cells) * 100, 2) if total_cells > 0 else 0,
            'by_field': df.isnull().sum().to_dict()
        },
        'duplicates': {
            'count': int(duplicate_rows),
            'percentage': round((duplicate_rows / len(df)) * 100, 2) if len(df) > 0 else 0
        },
        'data_types': df.dtypes.astype(str).to_dict(),
        'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
    }
    
    return quality_report

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize column names"""
    df = df.copy()
    df.columns = (df.columns
                  .str.strip()
                  .str.lower() 
                  .str.replace(' ', '_')
                  .str.replace(r'[^\w\s]', '', regex=True))
    return df

def detect_data_types(df: pd.DataFrame) -> Dict[str, str]:
    """Detect and suggest appropriate data types"""
    suggestions = {}
    
    for col in df.columns:
        series = df[col].dropna()
        
        if series.empty:
            suggestions[col] = 'object'
            continue
            
        # Try to infer numeric types
        if pd.api.types.is_numeric_dtype(series):
            if all(series == series.astype(int)):
                suggestions[col] = 'int64'
            else:
                suggestions[col] = 'float64'
        # Try to infer datetime
        elif series.dtype == 'object':
            try:
                pd.to_datetime(series.iloc[:min(100, len(series))], format="%Y-%m-%d")
                suggestions[col] = 'datetime64[ns]'
            except:
                suggestions[col] = 'object'
        else:
            suggestions[col] = str(series.dtype)
            
    return suggestions
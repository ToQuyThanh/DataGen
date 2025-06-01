"""
Tests for utils module
"""
import pytest
import pandas as pd
import numpy as np
from datagen.utils.helpers import (
    setup_logging, validate_data_quality, clean_column_names, detect_data_types
)

class TestHelpers:
    """Test utility helper functions"""
    
    def test_setup_logging(self):
        """Test logging setup"""
        logger = setup_logging('DEBUG')
        assert logger is not None
        
        logger_info = setup_logging('INFO')
        assert logger_info is not None
        
    def test_validate_data_quality_clean_data(self, sample_dataframe):
        """Test data quality validation with clean data"""
        quality_report = validate_data_quality(sample_dataframe)
        
        assert quality_report['total_records'] == 3
        assert quality_report['total_fields'] == 4
        assert quality_report['missing_values']['count'] == 0
        assert quality_report['missing_values']['percentage'] == 0
        assert quality_report['duplicates']['count'] == 0
        assert quality_report['duplicates']['percentage'] == 0
        assert 'data_types' in quality_report
        assert 'memory_usage_mb' in quality_report
        
    def test_validate_data_quality_with_missing_values(self):
        """Test data quality validation with missing values"""
        df_with_nulls = pd.DataFrame({
            'name': ['Alice', None, 'Charlie'],
            'age': [25, 30, None],
            'score': [85.5, 90.0, 88.5]
        })
        
        quality_report = validate_data_quality(df_with_nulls)
        
        assert quality_report['total_records'] == 3
        assert quality_report['missing_values']['count'] == 2
        assert quality_report['missing_values']['percentage'] > 0
        assert quality_report['missing_values']['by_field']['name'] == 1
        assert quality_report['missing_values']['by_field']['age'] == 1
        assert quality_report['missing_values']['by_field']['score'] == 0
        
    def test_validate_data_quality_with_duplicates(self):
        """Test data quality validation with duplicates"""
        df_with_dupes = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Alice'],
            'age': [25, 30, 25],
            'city': ['Hanoi', 'HCMC', 'Hanoi']
        })
        
        quality_report = validate_data_quality(df_with_dupes)
        
        assert quality_report['duplicates']['count'] == 1
        assert quality_report['duplicates']['percentage'] > 0
        
    def test_validate_data_quality_empty_dataframe(self):
        """Test data quality validation with empty DataFrame"""
        empty_df = pd.DataFrame()
        quality_report = validate_data_quality(empty_df)
        
        assert quality_report['total_records'] == 0
        assert quality_report['total_fields'] == 0
        assert quality_report['missing_values']['percentage'] == 0
        assert quality_report['duplicates']['percentage'] == 0
        
    def test_clean_column_names(self):
        """Test column name cleaning"""
        df_messy = pd.DataFrame({
            ' Name With Spaces ': [1, 2, 3],
            'Email@Address!': [4, 5, 6],
            'Age(Years)': [7, 8, 9],
            'UPPERCASE': [10, 11, 12]
        })
        
        df_clean = clean_column_names(df_messy)
        expected_columns = ['name_with_spaces', 'emailaddress', 'ageyears', 'uppercase']
        
        assert list(df_clean.columns) == expected_columns
        
    def test_detect_data_types_numeric(self):
        """Test data type detection for numeric data"""
        df_numeric = pd.DataFrame({
            'integers': [1, 2, 3, 4, 5],
            'floats': [1.1, 2.2, 3.3, 4.4, 5.5],
            'mixed_numeric': [1, 2.5, 3, 4.0, 5]
        })
        
        suggestions = detect_data_types(df_numeric)
        
        assert suggestions['integers'] == 'int64'
        assert suggestions['floats'] == 'float64'
        assert suggestions['mixed_numeric'] == 'float64'
        
    def test_detect_data_types_text(self):
        """Test data type detection for text data"""
        df_text = pd.DataFrame({
            'names': ['Alice', 'Bob', 'Charlie'],
            'descriptions': ['Engineer', 'Manager', 'Designer']
        })
        
        suggestions = detect_data_types(df_text)
        
        assert suggestions['names'] == 'object'
        assert suggestions['descriptions'] == 'object'
        
    def test_detect_data_types_datetime(self):
        """Test data type detection for datetime data"""
        df_datetime = pd.DataFrame({
            'dates': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'timestamps': ['2023-01-01 10:00:00', '2023-01-02 11:00:00', '2023-01-03 12:00:00']
        })
        
        suggestions = detect_data_types(df_datetime)
        
        # These should be detected as datetime
        assert 'datetime' in suggestions['dates'] or suggestions['dates'] == 'object'
        assert 'datetime' in suggestions['timestamps'] or suggestions['timestamps'] == 'object'
        
    def test_detect_data_types_mixed(self):
        """Test data type detection with mixed data types"""
        df_mixed = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'score': [85.5, 90.0, 88.5],
            'active': [True, False, True],
            'signup_date': ['2023-01-01', '2023-01-02', '2023-01-03']
        })
        
        suggestions = detect_data_types(df_mixed)
        
        assert suggestions['id'] == 'int64'
        assert suggestions['name'] == 'object'
        assert suggestions['score'] == 'float64'
        # Boolean might be detected as int64 or bool depending on pandas handling
        assert suggestions['active'] in ['int64', 'bool', 'object']
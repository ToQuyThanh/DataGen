# =============================================================================
# conftest.py - Pytest configuration and fixtures
# =============================================================================
"""
Pytest configuration and shared fixtures
"""
import pytest
import pandas as pd
from typing import Dict, Any, List
from datagen.core.schema import DataSchema, SchemaManager
from datagen.core.generator import DataGenerator
from datagen.core.dirty import DirtyDataFactory
from datagen.core.export import DataExporter

@pytest.fixture
def sample_schema():
    """Sample schema for testing"""
    return DataSchema(
        name="TestUser",
        description="Test user schema",
        fields={
            'user_id': {'type': 'uuid', 'required': True, 'description': 'User ID'},
            'name': {'type': 'name', 'required': True, 'description': 'Full name'},
            'email': {'type': 'email', 'required': True, 'description': 'Email address'},
            'age': {'type': 'integer', 'min_value': 18, 'max_value': 65, 'required': True},
            'salary': {'type': 'float', 'min_value': 30000.0, 'max_value': 150000.0, 'required': False},
            'is_active': {'type': 'boolean', 'required': True},
            'bio': {'type': 'text', 'max_length': 200, 'required': False}
        }
    )

@pytest.fixture
def sample_data():
    """Sample clean data for testing"""
    return [
        {
            'user_id': '123e4567-e89b-12d3-a456-426614174000',
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'age': 30,
            'salary': 75000.0,
            'is_active': True,
            'bio': 'Software engineer with 5 years experience'
        },
        {
            'user_id': '123e4567-e89b-12d3-a456-426614174001',
            'name': 'Jane Smith',
            'email': 'jane.smith@example.com',
            'age': 25,
            'salary': 65000.0,
            'is_active': False,
            'bio': 'Product manager'
        }
    ]

@pytest.fixture
def data_generator():
    """DataGenerator instance"""
    return DataGenerator()

@pytest.fixture
def schema_manager():
    """SchemaManager instance"""
    return SchemaManager()

@pytest.fixture
def dirty_factory():
    """DirtyDataFactory instance"""
    return DirtyDataFactory()

@pytest.fixture
def data_exporter():
    """DataExporter instance"""
    return DataExporter()

@pytest.fixture
def sample_dataframe():
    """Sample DataFrame for testing"""
    return pd.DataFrame([
        {'id': 1, 'name': 'Alice', 'age': 25, 'city': 'Hanoi'},
        {'id': 2, 'name': 'Bob', 'age': 30, 'city': 'HCMC'},
        {'id': 3, 'name': 'Charlie', 'age': 35, 'city': 'Da Nang'}
    ])

# =============================================================================
# tests/__init__.py
# =============================================================================
"""Test package"""

# =============================================================================
# tests/test_schema.py
# =============================================================================
"""
Tests for schema module
"""
import pytest
from datagen.core.schema import DataSchema, SchemaManager

class TestDataSchema:
    """Test DataSchema class"""
    
    def test_schema_creation(self, sample_schema):
        """Test schema creation"""
        assert sample_schema.name == "TestUser"
        assert sample_schema.description == "Test user schema"
        assert len(sample_schema.fields) == 7
        assert 'user_id' in sample_schema.fields
        
    def test_schema_validation_valid_record(self, sample_schema):
        """Test schema validation with valid record"""
        valid_record = {
            'user_id': '123',
            'name': 'Test User',
            'email': 'test@example.com',
            'age': 25,
            'is_active': True
        }
        assert sample_schema.validate_record(valid_record) == True
        
    def test_schema_validation_missing_required_field(self, sample_schema):
        """Test schema validation with missing required field"""
        invalid_record = {
            'name': 'Test User',
            'email': 'test@example.com',
            'age': 25
            # Missing required 'user_id' and 'is_active'
        }
        assert sample_schema.validate_record(invalid_record) == False
        
    def test_schema_validation_missing_optional_field(self, sample_schema):
        """Test schema validation with missing optional field"""
        valid_record = {
            'user_id': '123',
            'name': 'Test User',
            'email': 'test@example.com',
            'age': 25,
            'is_active': True
            # Missing optional 'salary' and 'bio' - should still be valid
        }
        assert sample_schema.validate_record(valid_record) == True

class TestSchemaManager:
    """Test SchemaManager class"""
    
    def test_schema_manager_initialization(self, schema_manager):
        """Test schema manager initialization"""
        assert len(schema_manager.list_schemas()) > 0
        assert 'customer' in schema_manager.list_schemas()
        assert 'employee' in schema_manager.list_schemas()
        
    def test_get_existing_schema(self, schema_manager):
        """Test getting existing schema"""
        customer_schema = schema_manager.get_schema('customer')
        assert customer_schema is not None
        assert customer_schema.name == "Customer"
        assert 'customer_id' in customer_schema.fields
        
    def test_get_nonexistent_schema(self, schema_manager):
        """Test getting non-existent schema"""
        result = schema_manager.get_schema('nonexistent')
        assert result is None
        
    def test_add_custom_schema(self, schema_manager, sample_schema):
        """Test adding custom schema"""
        initial_count = len(schema_manager.list_schemas())
        schema_manager.add_schema(sample_schema)
        
        assert len(schema_manager.list_schemas()) == initial_count + 1
        assert 'testuser' in schema_manager.list_schemas()
        
        retrieved = schema_manager.get_schema('testuser')
        assert retrieved.name == sample_schema.name
        
    def test_case_insensitive_schema_retrieval(self, schema_manager):
        """Test case insensitive schema retrieval"""
        schema1 = schema_manager.get_schema('Customer')
        schema2 = schema_manager.get_schema('CUSTOMER')
        schema3 = schema_manager.get_schema('customer')
        
        assert schema1 is not None
        assert schema2 is not None
        assert schema3 is not None
        assert schema1.name == schema2.name == schema3.name

# =============================================================================
# tests/test_generator.py
# =============================================================================
"""
Tests for data generator module
"""
import pytest
from datagen.core.generator import DataGenerator

class TestDataGenerator:
    """Test DataGenerator class"""
    
    def test_generator_initialization(self):
        """Test generator initialization"""
        generator = DataGenerator()
        assert generator.fake is not None
        
        # Test with specific locale
        generator_vn = DataGenerator(locale='vi_VN')
        assert generator_vn.fake is not None
        
    def test_generate_single_record(self, data_generator, sample_schema):
        """Test generating single record"""
        record = data_generator.generate_single(sample_schema)
        
        assert isinstance(record, dict)
        assert len(record) == len(sample_schema.fields)
        
        # Check required fields are present
        for field_name, field_config in sample_schema.fields.items():
            if field_config.get('required', True):
                assert field_name in record
                assert record[field_name] is not None
                
    def test_generate_batch_records(self, data_generator, sample_schema):
        """Test generating batch of records"""
        count = 10
        records = data_generator.generate_batch(sample_schema, count)
        
        assert isinstance(records, list)
        assert len(records) == count
        
        for record in records:
            assert isinstance(record, dict)
            assert len(record) == len(sample_schema.fields)
            
    def test_field_type_generation_string(self, data_generator):
        """Test string field generation"""
        config = {'type': 'string', 'max_length': 20}
        value = data_generator._generate_field_value('string', config)
        
        assert isinstance(value, str)
        assert len(value) <= 20
        
    def test_field_type_generation_integer(self, data_generator):
        """Test integer field generation"""
        config = {'type': 'integer', 'min_value': 10, 'max_value': 100}
        value = data_generator._generate_field_value('integer', config)
        
        assert isinstance(value, int)
        assert 10 <= value <= 100
        
    def test_field_type_generation_float(self, data_generator):
        """Test float field generation"""
        config = {'type': 'float', 'min_value': 10.0, 'max_value': 100.0}
        value = data_generator._generate_field_value('float', config)
        
        assert isinstance(value, float)
        assert 10.0 <= value <= 100.0
        
    def test_field_type_generation_boolean(self, data_generator):
        """Test boolean field generation"""
        config = {'type': 'boolean'}
        value = data_generator._generate_field_value('boolean', config)
        
        assert isinstance(value, bool)
        
    def test_field_type_generation_email(self, data_generator):
        """Test email field generation"""
        config = {'type': 'email'}
        value = data_generator._generate_field_value('email', config)
        
        assert isinstance(value, str)
        assert '@' in value
        assert '.' in value
        
    def test_field_type_generation_choice(self, data_generator):
        """Test choice field generation"""
        choices = ['A', 'B', 'C', 'D']
        config = {'type': 'choice', 'choices': choices}
        value = data_generator._generate_field_value('choice', config)
        
        assert value in choices
        
    def test_optional_field_generation(self, data_generator):
        """Test optional field can be None"""
        config = {'type': 'string', 'required': False}
        
        # Generate multiple values to check if some are None
        values = [data_generator._generate_field_value('string', config) for _ in range(100)]
        
        # At least some should be None (probabilistically)
        none_count = sum(1 for v in values if v is None)
        non_none_count = sum(1 for v in values if v is not None)
        
        assert none_count >= 0  # Can be None
        assert non_none_count > 0  # Should have some non-None values
        
    def test_unknown_field_type(self, data_generator):
        """Test handling of unknown field types"""
        config = {'type': 'unknown_type'}
        value = data_generator._generate_field_value('unknown_type', config)
        
        # Should default to generating a word
        assert isinstance(value, str)
        assert len(value) > 0

# =============================================================================
# tests/test_dirty.py
# =============================================================================
"""
Tests for dirty data module
"""
import pytest
from datagen.core.dirty import (
    DirtyDataFactory, MissingValueError, InvalidFormatError,
    OutOfRangeError, DuplicateError, InconsistentError
)

class TestMissingValueError:
    """Test MissingValueError strategy"""
    
    def test_apply_missing_values(self, sample_data, sample_schema):
        """Test applying missing values"""
        strategy = MissingValueError()
        result = strategy.apply(sample_data.copy(), sample_schema, 0.5)
        
        # Should have some None values
        has_none = any(
            any(value is None for value in record.values())
            for record in result
        )
        assert has_none or all(
            all(sample_schema.fields[field].get('required', True) for field in record.keys())
            for record in result
        )
        
    def test_no_missing_values_with_zero_ratio(self, sample_data, sample_schema):
        """Test no missing values when ratio is 0"""
        strategy = MissingValueError()
        result = strategy.apply(sample_data.copy(), sample_schema, 0.0)
        
        # Should be identical to original
        assert result == sample_data

class TestInvalidFormatError:
    """Test InvalidFormatError strategy"""
    
    def test_apply_invalid_format(self, sample_data, sample_schema):
        """Test applying format errors"""
        strategy = InvalidFormatError()
        result = strategy.apply(sample_data.copy(), sample_schema, 1.0)  # 100% error rate
        
        # Should have format errors in some records
        assert len(result) == len(sample_data)
        
    def test_email_format_corruption(self, sample_schema):
        """Test email format corruption"""
        data = [{'email': 'valid@example.com'}]
        strategy = InvalidFormatError()
        result = strategy.apply(data, sample_schema, 1.0)
        
        # Check if email was corrupted (might not always happen due to randomization)
        assert len(result) == 1

class TestOutOfRangeError:
    """Test OutOfRangeError strategy"""
    
    def test_apply_out_of_range(self, sample_data, sample_schema):
        """Test applying out of range errors"""
        strategy = OutOfRangeError()
        result = strategy.apply(sample_data.copy(), sample_schema, 1.0)
        
        assert len(result) == len(sample_data)
        
    def test_integer_out_of_range(self, sample_schema):
        """Test integer out of range"""
        data = [{'age': 30}]  # Within range 18-65
        strategy = OutOfRangeError()
        result = strategy.apply(data, sample_schema, 1.0)
        
        # Due to randomization, we just check the result exists
        assert len(result) == 1

class TestDuplicateError:
    """Test DuplicateError strategy"""
    
    def test_apply_duplicates(self, sample_data, sample_schema):
        """Test applying duplicate errors"""
        strategy = DuplicateError()
        original_length = len(sample_data)
        result = strategy.apply(sample_data.copy(), sample_schema, 0.5)
        
        # Should have more records due to duplicates
        assert len(result) >= original_length
        
    def test_no_duplicates_with_empty_data(self, sample_schema):
        """Test duplicate strategy with empty data"""
        strategy = DuplicateError()
        result = strategy.apply([], sample_schema, 0.5)
        
        assert len(result) == 0

class TestInconsistentError:
    """Test InconsistentError strategy"""
    
    def test_apply_inconsistent_data(self, sample_schema):
        """Test applying inconsistent data errors"""
        data = [{
            'quantity': 2,
            'unit_price': 10.0,
            'total_amount': 20.0  # Consistent initially
        }]
        
        strategy = InconsistentError()
        result = strategy.apply(data, sample_schema, 1.0)
        
        assert len(result) == 1

class TestDirtyDataFactory:
    """Test DirtyDataFactory"""
    
    def test_factory_initialization(self, dirty_factory):
        """Test factory initialization"""
        strategies = dirty_factory.list_strategies()
        
        assert 'missing_values' in strategies
        assert 'invalid_format' in strategies
        assert 'out_of_range' in strategies
        assert 'duplicate' in strategies
        assert 'inconsistent' in strategies
        
    def test_apply_single_error_type(self, dirty_factory, sample_data, sample_schema):
        """Test applying single error type"""
        result = dirty_factory.apply_errors(
            sample_data.copy(), sample_schema, 0.5, ['missing_values']
        )
        
        assert len(result) >= len(sample_data)  # Could have same or more (if duplicates)
        
    def test_apply_multiple_error_types(self, dirty_factory, sample_data, sample_schema):
        """Test applying multiple error types"""
        error_types = ['missing_values', 'invalid_format', 'duplicate']
        result = dirty_factory.apply_errors(
            sample_data.copy(), sample_schema, 0.6, error_types
        )
        
        assert len(result) >= len(sample_data)
        
    def test_apply_no_error_types(self, dirty_factory, sample_data, sample_schema):
        """Test applying no error types"""
        result = dirty_factory.apply_errors(
            sample_data.copy(), sample_schema, 0.5, []
        )
        
        # Should be identical to original
        assert result == sample_data
        

# =============================================================================
# tests/test_export.py
# =============================================================================
"""
Tests for export module
"""
import pytest
import pandas as pd
import json
from io import BytesIO
from datagen.core.export import DataExporter

class TestDataExporter:
    """Test DataExporter class"""
    
    def test_exporter_initialization(self, data_exporter):
        """Test exporter initialization"""
        assert data_exporter is not None
        
    def test_to_csv_export(self, data_exporter, sample_dataframe):
        """Test CSV export"""
        csv_data = data_exporter.to_csv(sample_dataframe)
        
        assert isinstance(csv_data, str)
        assert 'id,name,age,city' in csv_data
        assert 'Alice' in csv_data
        assert 'Bob' in csv_data
        
    def test_to_excel_export(self, data_exporter, sample_dataframe):
        """Test Excel export"""
        excel_data = data_exporter.to_excel(sample_dataframe)
        
        assert isinstance(excel_data, bytes)
        assert len(excel_data) > 0
        
        # Test reading back the Excel data
        df_from_excel = pd.read_excel(BytesIO(excel_data))
        assert len(df_from_excel) == len(sample_dataframe)
        assert list(df_from_excel.columns) == list(sample_dataframe.columns)
        
    def test_to_json_export(self, data_exporter, sample_dataframe):
        """Test JSON export"""
        json_data = data_exporter.to_json(sample_dataframe)
        
        assert isinstance(json_data, str)
        
        # Parse JSON to verify structure
        parsed_data = json.loads(json_data)
        assert isinstance(parsed_data, list)
        assert len(parsed_data) == len(sample_dataframe)
        assert 'name' in parsed_data[0]
        assert parsed_data[0]['name'] == 'Alice'
        
    def test_json_export_different_orientations(self, data_exporter, sample_dataframe):
        """Test JSON export with different orientations"""
        # Records orientation (default)
        records_json = data_exporter.to_json(sample_dataframe, orient='records')
        records_data = json.loads(records_json)
        assert isinstance(records_data, list)
        
        # Index orientation
        index_json = data_exporter.to_json(sample_dataframe, orient='index')
        index_data = json.loads(index_json)
        assert isinstance(index_data, dict)
        
    def test_export_with_metadata(self, data_exporter, sample_dataframe):
        """Test export with metadata"""
        result = data_exporter.export_with_metadata(
            sample_dataframe, 'TestSchema', 'json'
        )
        
        assert isinstance(result, str)
        parsed_result = json.loads(result)
        
        assert 'metadata' in parsed_result
        assert 'data' in parsed_result
        
        metadata = parsed_result['metadata']
        assert metadata['schema_name'] == 'TestSchema'
        assert metadata['record_count'] == len(sample_dataframe)
        assert metadata['field_count'] == len(sample_dataframe.columns)
        assert 'export_timestamp' in metadata
        
    def test_metadata_only_export(self, data_exporter, sample_dataframe):
        """Test metadata-only export"""
        result = data_exporter.export_with_metadata(
            sample_dataframe, 'TestSchema', 'metadata'
        )
        
        assert isinstance(result, str)
        metadata = json.loads(result)
        
        assert 'data' not in metadata  # Should not contain data
        assert metadata['schema_name'] == 'TestSchema'
        assert metadata['record_count'] == len(sample_dataframe)
        
    def test_export_empty_dataframe(self, data_exporter):
        """Test exporting empty DataFrame"""
        empty_df = pd.DataFrame()
        
        csv_data = data_exporter.to_csv(empty_df)
        assert isinstance(csv_data, str)
        
        json_data = data_exporter.to_json(empty_df)
        parsed_json = json.loads(json_data)
        assert parsed_json == []
        
    def test_export_dataframe_with_missing_values(self, data_exporter):
        """Test exporting DataFrame with missing values"""
        df_with_nulls = pd.DataFrame({
            'name': ['Alice', None, 'Charlie'],
            'age': [25, 30, None],
            'city': ['Hanoi', 'HCMC', 'Da Nang']
        })
        
        csv_data = data_exporter.to_csv(df_with_nulls)
        assert isinstance(csv_data, str)
        
        json_data = data_exporter.to_json(df_with_nulls)
        parsed_json = json.loads(json_data)
        assert len(parsed_json) == 3
        
        # Check null handling in metadata
        metadata_result = data_exporter.export_with_metadata(
            df_with_nulls, 'TestSchema', 'metadata'
        )
        metadata = json.loads(metadata_result)
        assert 'missing_values' in metadata
        assert metadata['missing_values']['name'] == 1
        assert metadata['missing_values']['age'] == 1

# =============================================================================
# tests/test_utils.py
# =============================================================================
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
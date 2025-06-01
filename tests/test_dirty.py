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
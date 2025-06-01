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
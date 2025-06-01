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
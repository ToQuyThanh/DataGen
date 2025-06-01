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
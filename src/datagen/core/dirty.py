"""
Dirty Data Factory - Apply various types of errors to clean data
"""
import random
import pandas as pd
from typing import List, Dict, Any, Protocol, Optional, Union
from abc import ABC, abstractmethod
from datagen.core.schema import DataSchema

class ErrorStrategy(Protocol):
    """Protocol for error strategies"""
    def apply(self, data: List[Dict[str, Any]], schema: DataSchema, 
             ratio: float, target_field: Optional[str] = None) -> List[Dict[str, Any]]:
        """Apply specific error type to data"""
        pass

class MissingValueError:
    """Strategy for creating missing values"""
    def apply(self, data: List[Dict[str, Any]], schema: DataSchema, 
             ratio: float, target_field: Optional[str] = None) -> List[Dict[str, Any]]:
        """Apply missing values to data"""
        num_errors = int(len(data) * ratio)
        error_indices = random.sample(range(len(data)), min(num_errors, len(data)))
        
        for idx in error_indices:
            if target_field:
                # Apply to specific target field
                if target_field in data[idx]:
                    data[idx][target_field] = None
            else:
                # Original behavior - choose field based on requirements
                optional_fields = [
                    field for field, config in schema.fields.items() 
                    if not config.get('required', True)
                ]
                if optional_fields:
                    field_to_null = random.choice(optional_fields)
                    data[idx][field_to_null] = None
                elif schema.fields:  # Make a required field null for dirty data
                    field_to_null = random.choice(list(schema.fields.keys()))
                    data[idx][field_to_null] = None
                
        return data

class InvalidFormatError:
    """Strategy for creating format errors"""
    def apply(self, data: List[Dict[str, Any]], schema: DataSchema,
              ratio: float, target_field: Optional[str] = None) -> List[Dict[str, Any]]:
        """Apply format errors to exactly ratio% of records"""
        num_errors = int(len(data) * ratio)
        error_indices = random.sample(range(len(data)), min(num_errors, len(data)))

        if target_field:
            # Apply to specific target field
            if target_field not in schema.fields:
                return data  # Target field doesn't exist in schema
            
            field_type = schema.fields[target_field]['type']
            if field_type not in ['email', 'phone', 'date', 'integer', 'float']:
                return data  # Field type doesn't support format errors
            
            for idx in error_indices:
                if target_field in data[idx]:
                    data[idx][target_field] = self._corrupt_field_value(field_type)
        else:
            # Original behavior - choose from corruptible fields
            corruptible_fields = [
                (name, config['type']) for name, config in schema.fields.items()
                if config['type'] in ['email', 'phone', 'date', 'integer', 'float']
            ]

            if not corruptible_fields:
                return data

            for idx in error_indices:
                field_name, field_type = random.choice(corruptible_fields)
                data[idx][field_name] = self._corrupt_field_value(field_type)

        return data
    
    def _corrupt_field_value(self, field_type: str) -> str:
        """Generate corrupted value based on field type"""
        corruption_map = {
            'email': "invalid-email-format",
            'phone': "123-invalid",
            'date': "invalid-date",
            'integer': "not-a-number",
            'float': "not-a-float"
        }
        return corruption_map.get(field_type, "corrupted-value")

class OutOfRangeError:
    """Strategy for creating out-of-range values"""
    def apply(self, data: List[Dict[str, Any]], schema: DataSchema, 
             ratio: float, target_field: Optional[str] = None) -> List[Dict[str, Any]]:
        """Apply out-of-range errors to data"""
        num_errors = int(len(data) * ratio)
        error_indices = random.sample(range(len(data)), min(num_errors, len(data)))
        
        for idx in error_indices:
            if target_field:
                # Apply to specific target field
                if target_field in schema.fields and target_field in data[idx]:
                    field_config = schema.fields[target_field]
                    corrupted_value = self._generate_out_of_range_value(field_config)
                    if corrupted_value is not None:
                        data[idx][target_field] = corrupted_value
            else:
                # Original behavior - random field selection
                for field_name, field_config in schema.fields.items():
                    if random.random() < 0.3:  # 30% chance to make this field out of range
                        corrupted_value = self._generate_out_of_range_value(field_config)
                        if corrupted_value is not None:
                            data[idx][field_name] = corrupted_value
                        break
                    
        return data
    
    def _generate_out_of_range_value(self, field_config: Dict[str, Any]) -> Any:
        """Generate out-of-range value based on field configuration"""
        field_type = field_config['type']
        
        if field_type == 'integer':
            max_val = field_config.get('max_value', 1000)
            return max_val + random.randint(100, 1000)
        elif field_type == 'float':
            max_val = field_config.get('max_value', 1000.0)
            return max_val + random.uniform(100, 1000)
        elif field_type == 'string':
            max_len = field_config.get('max_length', 50)
            return "x" * (max_len + 10)
        
        return None

class DuplicateError:
    """Strategy for creating duplicate records"""
    def apply(self, data: List[Dict[str, Any]], schema: DataSchema, 
             ratio: float, target_field: Optional[str] = None) -> List[Dict[str, Any]]:
        """Create duplicate records"""
        num_duplicates = int(len(data) * ratio)
        
        for _ in range(num_duplicates):
            if data:
                original_idx = random.randint(0, len(data) - 1)
                duplicate = data[original_idx].copy()
                
                if target_field and target_field in duplicate:
                    # For target field, create partial duplicate (same target field value)
                    # but modify other fields to make it more realistic
                    target_value = duplicate[target_field]
                    # Create a new record with different values but same target field
                    new_record = {}
                    for field_name in duplicate.keys():
                        if field_name == target_field:
                            new_record[field_name] = target_value
                        else:
                            # Modify other fields slightly
                            if isinstance(duplicate[field_name], str):
                                new_record[field_name] = duplicate[field_name] + "_dup"
                            elif isinstance(duplicate[field_name], (int, float)):
                                new_record[field_name] = duplicate[field_name] + random.randint(1, 10)
                            else:
                                new_record[field_name] = duplicate[field_name]
                    data.append(new_record)
                else:
                    # Full duplicate
                    data.append(duplicate)
                
        return data

class InconsistentError:
    """Strategy for creating inconsistent data"""
    def apply(self, data: List[Dict[str, Any]], schema: DataSchema, 
             ratio: float, target_field: Optional[str] = None) -> List[Dict[str, Any]]:
        """Create inconsistent data patterns"""
        num_errors = int(len(data) * ratio)
        error_indices = random.sample(range(len(data)), min(num_errors, len(data)))
        
        for idx in error_indices:
            if target_field:
                # Apply inconsistency to target field
                if target_field in data[idx]:
                    # Create inconsistency based on field relationships
                    self._create_target_inconsistency(data[idx], target_field)
            else:
                # Original behavior - standard inconsistency patterns
                self._create_standard_inconsistency(data[idx])
                
        return data
    
    def _create_target_inconsistency(self, record: Dict[str, Any], target_field: str):
        """Create inconsistency involving the target field"""
        # Example patterns based on common field relationships
        if target_field == 'total_amount':
            if 'quantity' in record and 'unit_price' in record:
                # Make total different from quantity * unit_price
                record[target_field] = random.uniform(1.0, 100.0)
        elif target_field == 'age':
            if 'birth_date' in record:
                # Make age inconsistent with birth date
                record[target_field] = random.randint(1, 100)
        elif target_field == 'email':
            if 'name' in record:
                # Make email inconsistent with name
                record[target_field] = "wrong@email.com"
        else:
            # Generic inconsistency - make field value unrealistic
            if isinstance(record[target_field], (int, float)):
                record[target_field] = -999999  # Unrealistic value
            elif isinstance(record[target_field], str):
                record[target_field] = "INCONSISTENT_VALUE"
    
    def _create_standard_inconsistency(self, record: Dict[str, Any]):
        """Create standard inconsistency patterns"""
        # Example: Make total_amount inconsistent with quantity * unit_price
        if 'total_amount' in record and 'quantity' in record and 'unit_price' in record:
            record['total_amount'] = random.uniform(1.0, 100.0)

class DirtyDataFactory:
    """Factory for creating different types of dirty data"""
    
    def __init__(self):
        self.strategies = {
            'missing_values': MissingValueError(),
            'invalid_format': InvalidFormatError(), 
            'out_of_range': OutOfRangeError(),
            'duplicate': DuplicateError(),
            'inconsistent': InconsistentError()
        }
    def apply_errors(self, data: List[Dict[str, Any]], schema: DataSchema, 
                    ratio: float, error_types: List[str], 
                    target_field: Optional[Union[str, List[str]]] = None) -> List[Dict[str, Any]]:
        """Apply multiple error types to data
        
        Args:
            data: List of records to corrupt
            schema: Data schema definition
            ratio: Overall error ratio (0.0 to 1.0)
            error_types: List of error types to apply
            target_field: Optional specific field(s) to target for errors.
                        Can be a single field name (str) or list of field names (List[str]).
                        If None, errors will be applied to random fields.
        """
        result_data = data.copy()
        
        # Normalize target_field to always be a list for consistent processing
        target_fields = None
        if target_field is not None:
            if isinstance(target_field, str):
                target_fields = [target_field]
            elif isinstance(target_field, list):
                target_fields = target_field
            else:
                # Handle unexpected types gracefully
                target_fields = None
        
        # Validate target fields exist in schema
        if target_fields:
            valid_fields = []
            for field in target_fields:
                if field in schema.fields:
                    valid_fields.append(field)
                else:
                    print(f"Warning: Target field '{field}' not found in schema. Skipping.")
            
            target_fields = valid_fields if valid_fields else None
        
        # Distribute ratio among selected error types
        ratio_per_type = ratio / len(error_types) if error_types else 0
        
        # Apply each error type
        for error_type in error_types:
            if error_type in self.strategies:
                if target_fields:
                    # Apply errors to each target field
                    for field in target_fields:
                        # Distribute ratio among target fields to maintain overall error rate
                        field_ratio = ratio_per_type / len(target_fields)
                        result_data = self.strategies[error_type].apply(
                            result_data, schema, field_ratio, field
                        )
                else:
                    # Apply to random fields (existing behavior)
                    result_data = self.strategies[error_type].apply(
                        result_data, schema, ratio_per_type, None
                    )
                    
        return result_data
    
    def apply_single_error(self, data: List[Dict[str, Any]], schema: DataSchema,
                          error_type: str, ratio: float, 
                          target_field: Optional[str] = None) -> List[Dict[str, Any]]:
        """Apply a single error type to data
        
        Args:
            data: List of records to corrupt
            schema: Data schema definition
            error_type: Type of error to apply
            ratio: Error ratio (0.0 to 1.0)
            target_field: Optional specific field to target for errors
        """
        if error_type not in self.strategies:
            raise ValueError(f"Unknown error type: {error_type}")
        
        return self.strategies[error_type].apply(data, schema, ratio, target_field)

    def register_strategy(self, name: str, strategy: ErrorStrategy):
        """Register new error strategy"""
        if not isinstance(strategy, ErrorStrategy) and not (hasattr(strategy, 'apply') and callable(strategy.apply)):
             # Check if it's an instance of the Protocol or at least has an 'apply' method
             raise TypeError(f"Strategy must implement the ErrorStrategy protocol or have an 'apply' method.")
        
        self.strategies[name] = strategy

    def list_strategies(self) -> List[str]:
        """List available error strategies"""
        return list(self.strategies.keys())
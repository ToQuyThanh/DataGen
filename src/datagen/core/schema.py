"""
Schema definition and management - Implemented with Singleton SchemaManager
"""
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from datetime import date

# The DataSchema class remains the same, as it doesn't need to be a singleton
class DataSchema(BaseModel):
    name: str
    description: str
    fields: Dict[str, Dict[str, Any]]

    def validate_record(self, record: Dict[str, Any]) -> bool:
        """Validate a record against this schema"""
        print(f"Validating record against schema '{self.name}'...")
        # Basic validation: Check for required fields presence
        for field_name, field_config in self.fields.items():
            if field_config.get('required', True) and field_name not in record:
                print(f"Validation failed: Missing required field '{field_name}'")
                return False

        print("Validation successful.")
        return True

class SchemaManager:
    # Class variable to hold the single instance
    _instance = None
    # Flag to ensure __init__ runs only once
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """
        Override __new__ to control instance creation and ensure only one exists.
        """
        print("SchemaManager: Entering __new__")
        if cls._instance is None:
            print("SchemaManager: No instance exists. Creating a new one.")
            # Call the parent class's __new__ to create the actual instance
            cls._instance = super(SchemaManager, cls).__new__(cls)
            # The instance is created, __init__ will be called next automatically
        else:
            print("SchemaManager: Instance already exists. Returning the existing one.")
            # If instance already exists, just return it. __init__ will still be called,
            # but we will handle re-initialization prevention inside __init__.

        print("SchemaManager: Exiting __new__")
        return cls._instance

    def __init__(self):
        """
        Initialize the manager, only performing setup logic once.
        """
        print("SchemaManager: Entering __init__")
        if not self._initialized:
            print("SchemaManager: First time initialization.")
            # Perform the one-time initialization here
            self._schemas: Dict[str, DataSchema] = self._load_default_schemas()
            # Set the flag to prevent re-initialization
            self._initialized = True
            print("SchemaManager: Initialization complete.")
        else:
            print("SchemaManager: Already initialized. Skipping initialization logic.")
            # If already initialized, do nothing (or handle args/kwargs if __init__ accepted any)

        print("SchemaManager: Exiting __init__")


    def _load_default_schemas(self) -> Dict[str, DataSchema]:
        """Load predefined schemas"""
        print("SchemaManager: Loading default schemas...")
        schemas = {}

        # Customer schema
        schemas['customer'] = DataSchema(
            name="Customer",
            description="Customer information schema",
            fields={
                'customer_id': {'type': 'uuid', 'required': True, 'description': 'Unique customer ID'},
                'first_name': {'type': 'first_name', 'required': True, 'description': 'Customer first name'},
                'last_name': {'type': 'last_name', 'required': True, 'description': 'Customer last name'},
                'email': {'type': 'email', 'required': True, 'description': 'Email address'},
                'phone': {'type': 'phone', 'required': False, 'description': 'Phone number'},
                'address': {'type': 'address', 'required': False, 'description': 'Full address'},
                'city': {'type': 'city', 'required': True, 'description': 'City'},
                'age': {'type': 'integer', 'min_value': 18, 'max_value': 80, 'required': True},
                'registration_date': {'type': 'date', 'start_date': '-2y', 'required': True},
                'is_active': {'type': 'boolean', 'required': True}
            }
        )

        # Employee schema
        schemas['employee'] = DataSchema(
            name="Employee",
            description="Employee information schema",
            fields={
                'employee_id': {'type': 'uuid', 'required': True, 'description': 'Employee ID'},
                'first_name': {'type': 'first_name', 'required': True, 'description': 'First name'},
                'last_name': {'type': 'last_name', 'required': True, 'description': 'Last name'},
                'email': {'type': 'email', 'required': True, 'description': 'Work email'},
                'department': {'type': 'choice', 'choices': ['IT', 'HR', 'Finance', 'Marketing', 'Sales'], 'required': True},
                'job_title': {'type': 'job_title', 'required': True, 'description': 'Job position'},
                'salary': {'type': 'float', 'min_value': 10000, 'max_value': 100000, 'required': True},
                'hire_date': {'type': 'date', 'start_date': '-5y', 'required': True},
                'is_manager': {'type': 'boolean', 'required': True}
            }
        )

        # Product schema
        schemas['product'] = DataSchema(
            name="Product",
            description="Product information schema",
            fields={
                'product_id': {'type': 'uuid', 'required': True, 'description': 'Product ID'},
                'product_name': {'type': 'string', 'max_length': 100, 'required': True, 'description': 'Product name'},
                'category': {'type': 'choice', 'choices': ['Electronics', 'Clothing', 'Books', 'Home', 'Sports'], 'required': True},
                'price': {'type': 'float', 'min_value': 1.0, 'max_value': 2000.0, 'required': True},
                'stock_quantity': {'type': 'integer', 'min_value': 0, 'max_value': 1000, 'required': True},
                'description': {'type': 'text', 'max_length': 500, 'required': False},
                'created_date': {'type': 'datetime', 'start_date': '-1y', 'required': True},
                'is_available': {'type': 'boolean', 'required': True}
            }
        )

        # Transaction schema
        schemas['transaction'] = DataSchema(
            name="Transaction",
            description="Transaction information schema",
            fields={
                'transaction_id': {'type': 'uuid', 'required': True, 'description': 'Transaction ID'},
                'customer_id': {'type': 'uuid', 'required': True, 'description': 'Customer ID'},
                'product_id': {'type': 'uuid', 'required': True, 'description': 'Product ID'},
                'quantity': {'type': 'integer', 'min_value': 1, 'max_value': 10, 'required': True},
                'unit_price': {'type': 'float', 'min_value': 1.0, 'max_value': 2000.0, 'required': True},
                'total_amount': {'type': 'float', 'min_value': 1.0, 'max_value': 20000.0, 'required': True},
                'transaction_date': {'type': 'datetime', 'start_date': '-6m', 'required': True},
                'payment_method': {'type': 'choice', 'choices': ['Credit Card', 'Cash', 'Bank Transfer', 'E-wallet'], 'required': True},
                'status': {'type': 'choice', 'choices': ['Pending', 'Completed', 'Cancelled', 'Refunded'], 'required': True}
            }
        )
        print("SchemaManager: Default schemas loaded.")
        return schemas

    def get_schema(self, name: str) -> DataSchema:
        """Get schema by name"""
        return self._schemas.get(name.lower())

    def list_schemas(self) -> List[str]:
        """List available schema names"""
        return list(self._schemas.keys())

    def add_schema(self, schema: DataSchema):
        """Add a new schema"""
        self._schemas[schema.name.lower()] = schema

    def remove_schema(self, name: str):
        """Remove a schema by name"""
        if name.lower() in self._schemas:
            del self._schemas[name.lower()]
        else:
            raise ValueError(f"Schema '{name}' does not exist.")

    def update_schema(self, name: str, schema: DataSchema):
        """Update an existing schema"""
        if name.lower() in self._schemas:
            self._schemas[name.lower()] = schema
        else:
            raise ValueError(f"Schema '{name}' does not exist.")

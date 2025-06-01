"""
Data Generator using Faker
"""
from faker import Faker
from typing import Dict, List, Any
import random
from datetime import datetime, timedelta
from datagen.core.schema import DataSchema

class DataGenerator:
    def __init__(self, locale: str = 'vi_VN'):
        self.fake = Faker([locale])
        
    def generate_single(self, schema: DataSchema) -> Dict[str, Any]:
        """Generate a single record based on schema"""
        record = {}
        
        for field_name, field_config in schema.fields.items():
            field_type = field_config['type']
            record[field_name] = self._generate_field_value(field_type, field_config)
            
        return record
    
    def generate_batch(self, schema: DataSchema, count: int) -> List[Dict[str, Any]]:
        """Generate multiple records"""
        return [self.generate_single(schema) for _ in range(count)]
    
    def _generate_field_value(self, field_type: str, config: Dict[str, Any]) -> Any:
        """Generate value for a specific field type"""
        
        # Handle required vs optional fields
        if not config.get('required', True) and random.random() < 0.1:
            return None
            
        generators = {
            'string': lambda: self.fake.text(max_nb_chars=config.get('max_length', 50)),
            'name': lambda: self.fake.name(),   
            'user_name': lambda: self.fake.user_name(),   
            'first_name': lambda: self.fake.first_name(),
            'last_name': lambda: self.fake.last_name(),
            'email': lambda: self.fake.email(),
            'phone': lambda: self.fake.phone_number(),
            'address': lambda: self.fake.address(),
            'address_detail': lambda: self.fake.address_detail(),
            'ipv4': lambda: self.fake.ipv4(),
            'city': lambda: self.fake.city(),
            'country': lambda: self.fake.country(),
            'company': lambda: self.fake.company(),
            'job_title': lambda: self.fake.job(),
            'integer': lambda: self.fake.random_int(
                min=config.get('min_value', 0),
                max=config.get('max_value', 1000)
            ),
            'float': lambda: round(
                random.uniform(
                    config.get('min_value', 0.0),
                    config.get('max_value', 1000.0)
                ), 2
            ),
            'boolean': lambda: self.fake.boolean(),
            'date_of_birth': lambda: self.fake.date_of_birth(),
            'date': lambda: self.fake.date_between(
                start_date=config.get('start_date', '-1y'),
                end_date=config.get('end_date', 'today')
            ),
            'datetime': lambda: self.fake.date_time_between(
                start_date=config.get('start_date', '-1y'),
                end_date=config.get('end_date', 'now')
            ),
            'uuid': lambda: str(self.fake.uuid4()),
            'url': lambda: self.fake.url(),
            'text': lambda: self.fake.text(max_nb_chars=config.get('max_length', 200)),
            'choice': lambda: self.fake.random_element(config.get('choices', ['A', 'B', 'C'])),
        }
        
        generator = generators.get(field_type, lambda: self.fake.word())
        return generator()
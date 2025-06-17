from pydantic import BaseModel, Field, validator
from typing import List, Optional
import re
import uuid

class Prop(BaseModel):
    name: str
    value: str
    ns: str

class Annotation(BaseModel):
    name: str
    value: List[str]
    ns: str

class Statement(BaseModel):
    statement_id: str = Field(..., alias="statement-id")
    uuid: str
    description: str

class ControlMapping(BaseModel):
    uuid: str
    control_id: str = Field(..., alias="control-id")
    props: List[Prop]
    annotations: Optional[List[Annotation]] = None
    statements: Optional[List[Statement]] = None

    @validator('uuid')
    def validate_uuid(cls, v):
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError('Invalid UUID format')

    @validator('props')
    def validate_required_props(cls, props):
        required_props = {
            'control-status',
            'control-name',
            'control-description',
            'control-explanation',
            'control-configuration'
        }
        prop_names = {p.name for p in props}
        missing = required_props - prop_names
        if missing:
            raise ValueError(f'Missing required properties: {missing}')
        return props

    @validator('props')
    def validate_configuration_file_extensions(cls, props):
        for prop in props:
            if prop.name == 'control-configuration' and prop.value:
                # Extract file paths from the configuration value
                file_paths = re.findall(r'File:?\s*([^\n,]+)', prop.value)
                for path in file_paths:
                    path = path.strip()
                    if path and not path.endswith(('.json', '.yaml', '.yml')):
                        raise ValueError(f'Invalid file extension in configuration: {path}')
        return props

def validate_control_mapping(data: dict) -> tuple[bool, Optional[str]]:
    """
    Validate a control mapping dictionary against the schema.
    
    Args:
        data: The control mapping dictionary to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        ControlMapping(**data)
        return True, None
    except Exception as e:
        return False, str(e)

def validate_unique_uuids(mappings: List[dict]) -> tuple[bool, Optional[str]]:
    """
    Validate that all UUIDs in a list of control mappings are unique.
    
    Args:
        mappings: List of control mapping dictionaries
        
    Returns:
        tuple: (is_valid, error_message)
    """
    uuids = set()
    for mapping in mappings:
        # Check main UUID
        if mapping['uuid'] in uuids:
            return False, f'Duplicate UUID found: {mapping["uuid"]}'
        uuids.add(mapping['uuid'])
        
        # Check statement UUIDs
        for statement in mapping.get('statements', []):
            if statement['uuid'] in uuids:
                return False, f'Duplicate UUID found in statement: {statement["uuid"]}'
            uuids.add(statement['uuid'])
    
    return True, None 
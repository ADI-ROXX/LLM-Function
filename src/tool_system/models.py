from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field


class ParameterType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NUMBER = "number"


class Parameter(BaseModel):
    name: str
    type: ParameterType
    description: str
    required: bool = False
    enum: Optional[List[Any]] = None
    default: Optional[Any] = None
    items: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = None


class Tool(BaseModel):
    name: str
    description: str
    parameters: List[Parameter] = Field(default_factory=list)
    returns: Optional[str] = None
    use_cases: List[str] = Field(default_factory=list)

    def get_required_parameters(self) -> List[Parameter]:
        return [p for p in self.parameters if p.required]

    def get_optional_parameters(self) -> List[Parameter]:
        return [p for p in self.parameters if not p.required]

    def validate_arguments(self, arguments: Dict[str, Any]) -> List[str]:
        errors = []
        
        required_params = {p.name for p in self.get_required_parameters()}
        provided_params = set(arguments.keys())
        
        missing = required_params - provided_params
        if missing:
            errors.append(f"Missing required parameters: {missing}")
        
        for param in self.parameters:
            if param.name in arguments:
                value = arguments[param.name]
                if not self._validate_type(value, param):
                    errors.append(f"Invalid type for {param.name}: expected {param.type.value}")
                
                if param.enum and value not in param.enum:
                    errors.append(f"Invalid value for {param.name}: must be one of {param.enum}")
        
        return errors

    def _validate_type(self, value: Any, param: Parameter) -> bool:
        type_map = {
            ParameterType.STRING: str,
            ParameterType.INTEGER: int,
            ParameterType.BOOLEAN: bool,
            ParameterType.ARRAY: list,
            ParameterType.OBJECT: dict,
            ParameterType.NUMBER: (int, float),
        }
        
        expected_type = type_map.get(param.type)
        if expected_type is None:
            return True
        
        return isinstance(value, expected_type)


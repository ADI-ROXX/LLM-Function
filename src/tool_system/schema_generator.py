from typing import List, Dict, Any
from .models import Tool, Parameter


class SchemaGenerator:
    @staticmethod
    def to_openai_format(tool: Tool) -> Dict[str, Any]:
        properties = {}
        required = []
        
        for param in tool.parameters:
            param_schema = {
                "type": param.type.value,
                "description": param.description,
            }
            
            if param.enum:
                param_schema["enum"] = param.enum
            
            if param.items:
                param_schema["items"] = param.items
            
            if param.properties:
                param_schema["properties"] = param.properties
            
            properties[param.name] = param_schema
            
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    @staticmethod
    def to_ollama_format(tool: Tool) -> Dict[str, Any]:
        return SchemaGenerator.to_openai_format(tool)

    @staticmethod
    def to_deepseek_format(tool: Tool) -> Dict[str, Any]:
        return SchemaGenerator.to_openai_format(tool)

    @staticmethod
    def tools_to_openai_format(tools: List[Tool]) -> List[Dict[str, Any]]:
        return [SchemaGenerator.to_openai_format(tool) for tool in tools]

    @staticmethod
    def tools_to_ollama_format(tools: List[Tool]) -> List[Dict[str, Any]]:
        return [SchemaGenerator.to_ollama_format(tool) for tool in tools]

    @staticmethod
    def tools_to_deepseek_format(tools: List[Tool]) -> List[Dict[str, Any]]:
        return [SchemaGenerator.to_deepseek_format(tool) for tool in tools]

    @staticmethod
    def generate_tool_documentation(tool: Tool) -> str:
        doc = f"Tool: {tool.name}\n"
        doc += f"Description: {tool.description}\n"
        doc += "\nParameters:\n"
        
        for param in tool.parameters:
            required_str = "required" if param.required else "optional"
            doc += f"  - {param.name} ({param.type.value}, {required_str}): {param.description}\n"
            
            if param.enum:
                doc += f"    Allowed values: {param.enum}\n"
            
            if param.default is not None:
                doc += f"    Default: {param.default}\n"
        
        if tool.returns:
            doc += f"\nReturns: {tool.returns}\n"
        
        if tool.use_cases:
            doc += f"\nUse cases: {', '.join(tool.use_cases)}\n"
        
        return doc


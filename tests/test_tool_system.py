import pytest
from src.tool_system import (
    Tool,
    Parameter,
    ParameterType,
    ToolRegistry,
    get_standard_tools,
    SchemaGenerator,
)


def test_tool_creation():
    tool = Tool(
        name="test_tool",
        description="A test tool",
        parameters=[
            Parameter(
                name="param1",
                type=ParameterType.STRING,
                description="First parameter",
                required=True,
            )
        ],
    )
    assert tool.name == "test_tool"
    assert len(tool.parameters) == 1


def test_parameter_validation():
    tool = Tool(
        name="test_tool",
        description="A test tool",
        parameters=[
            Parameter(
                name="param1",
                type=ParameterType.STRING,
                description="First parameter",
                required=True,
            ),
            Parameter(
                name="param2",
                type=ParameterType.INTEGER,
                description="Second parameter",
                required=False,
            ),
        ],
    )
    
    errors = tool.validate_arguments({"param1": "value"})
    assert len(errors) == 0
    
    errors = tool.validate_arguments({})
    assert len(errors) > 0
    assert "Missing required parameters" in errors[0]


def test_tool_registry():
    registry = ToolRegistry()
    
    tool = Tool(
        name="test_tool",
        description="A test tool",
        parameters=[],
    )
    
    registry.register(tool)
    assert registry.exists("test_tool")
    assert len(registry) == 1
    
    retrieved = registry.get("test_tool")
    assert retrieved.name == "test_tool"


def test_registry_duplicate():
    registry = ToolRegistry()
    
    tool = Tool(name="test_tool", description="A test tool", parameters=[])
    
    registry.register(tool)
    
    with pytest.raises(ValueError):
        registry.register(tool)


def test_standard_tools():
    tools = get_standard_tools()
    assert len(tools) == 7
    
    tool_names = [t.name for t in tools]
    assert "read_file" in tool_names
    assert "write_file" in tool_names
    assert "edit_file" in tool_names


def test_openai_schema_generation():
    tool = Tool(
        name="test_tool",
        description="A test tool",
        parameters=[
            Parameter(
                name="param1",
                type=ParameterType.STRING,
                description="First parameter",
                required=True,
            )
        ],
    )
    
    schema = SchemaGenerator.to_openai_format(tool)
    
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "test_tool"
    assert "param1" in schema["function"]["parameters"]["properties"]
    assert "param1" in schema["function"]["parameters"]["required"]


def test_ollama_schema_generation():
    tool = Tool(
        name="test_tool",
        description="A test tool",
        parameters=[],
    )
    
    schema = SchemaGenerator.to_ollama_format(tool)
    assert schema["type"] == "function"


def test_deepseek_schema_generation():
    tool = Tool(
        name="test_tool",
        description="A test tool",
        parameters=[],
    )
    
    schema = SchemaGenerator.to_deepseek_format(tool)
    assert schema["type"] == "function"


def test_multiple_tools_schema():
    tools = get_standard_tools()[:3]
    schemas = SchemaGenerator.tools_to_openai_format(tools)
    
    assert len(schemas) == 3
    assert all(s["type"] == "function" for s in schemas)


def test_tool_validation():
    tool = Tool(
        name="test_tool",
        description="A test tool",
        parameters=[
            Parameter(
                name="count",
                type=ParameterType.INTEGER,
                description="A count",
                required=True,
            )
        ],
    )
    
    errors = tool.validate_arguments({"count": "not_an_int"})
    assert len(errors) > 0
    assert "Invalid type" in errors[0]


def test_enum_validation():
    tool = Tool(
        name="test_tool",
        description="A test tool",
        parameters=[
            Parameter(
                name="option",
                type=ParameterType.STRING,
                description="An option",
                required=True,
                enum=["option1", "option2"],
            )
        ],
    )
    
    errors = tool.validate_arguments({"option": "option1"})
    assert len(errors) == 0
    
    errors = tool.validate_arguments({"option": "invalid"})
    assert len(errors) > 0


def test_tool_documentation():
    tool = Tool(
        name="test_tool",
        description="A test tool",
        parameters=[
            Parameter(
                name="param1",
                type=ParameterType.STRING,
                description="First parameter",
                required=True,
            )
        ],
        returns="A string",
        use_cases=["Testing"],
    )
    
    doc = SchemaGenerator.generate_tool_documentation(tool)
    assert "test_tool" in doc
    assert "param1" in doc
    assert "required" in doc


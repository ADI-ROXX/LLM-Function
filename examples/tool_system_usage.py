from src.tool_system import (
    ToolRegistry,
    get_standard_tools,
    SchemaGenerator,
)


def main():
    print("=== Tool System Demo ===\n")
    
    registry = ToolRegistry()
    tools = get_standard_tools()
    registry.register_multiple(tools)
    
    print(f"Registered {len(registry)} tools:")
    for name in registry.get_names():
        print(f"  - {name}")
    
    print("\n=== Tool Details ===\n")
    
    read_file_tool = registry.get("read_file")
    if read_file_tool:
        doc = SchemaGenerator.generate_tool_documentation(read_file_tool)
        print(doc)
    
    print("\n=== OpenAI Format Schema ===\n")
    
    schema = SchemaGenerator.to_openai_format(read_file_tool)
    import json
    print(json.dumps(schema, indent=2))
    
    print("\n=== Validation Example ===\n")
    
    valid_args = {"file_path": "test.txt"}
    errors = registry.validate_tool_call("read_file", valid_args)
    print(f"Valid args {valid_args}: {len(errors)} errors")
    
    invalid_args = {}
    errors = registry.validate_tool_call("read_file", invalid_args)
    print(f"Invalid args {invalid_args}: {len(errors)} errors")
    for error in errors:
        print(f"  - {error}")
    
    print("\n=== All Tools in OpenAI Format ===\n")
    
    all_schemas = SchemaGenerator.tools_to_openai_format(tools)
    print(f"Generated {len(all_schemas)} schemas")


if __name__ == "__main__":
    main()


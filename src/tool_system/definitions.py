from typing import List
from .models import Tool, Parameter, ParameterType


def get_standard_tools() -> List[Tool]:
    return [
        Tool(
            name="read_file",
            description="Read contents of a file from the filesystem",
            parameters=[
                Parameter(
                    name="file_path",
                    type=ParameterType.STRING,
                    description="Path to the file",
                    required=True,
                ),
                Parameter(
                    name="line_start",
                    type=ParameterType.INTEGER,
                    description="First line to read (optional)",
                    required=False,
                ),
                Parameter(
                    name="line_end",
                    type=ParameterType.INTEGER,
                    description="Last line to read (optional)",
                    required=False,
                ),
            ],
            returns="File contents as string",
            use_cases=["Examining code", "Reading configs", "Viewing data"],
        ),
        Tool(
            name="write_file",
            description="Write or overwrite a file",
            parameters=[
                Parameter(
                    name="file_path",
                    type=ParameterType.STRING,
                    description="Path to the file",
                    required=True,
                ),
                Parameter(
                    name="contents",
                    type=ParameterType.STRING,
                    description="Content to write",
                    required=True,
                ),
            ],
            returns="Success/failure message",
            use_cases=["Creating files", "Saving edits"],
        ),
        Tool(
            name="edit_file",
            description="Search and replace within a file",
            parameters=[
                Parameter(
                    name="file_path",
                    type=ParameterType.STRING,
                    description="Path to the file",
                    required=True,
                ),
                Parameter(
                    name="old_text",
                    type=ParameterType.STRING,
                    description="Text to find",
                    required=True,
                ),
                Parameter(
                    name="new_text",
                    type=ParameterType.STRING,
                    description="Replacement text",
                    required=True,
                ),
            ],
            returns="Success/failure with line numbers",
            use_cases=["Bug fixes", "Refactoring"],
        ),
        Tool(
            name="search_code",
            description="Search for patterns in code using regex",
            parameters=[
                Parameter(
                    name="pattern",
                    type=ParameterType.STRING,
                    description="Regex pattern",
                    required=True,
                ),
                Parameter(
                    name="file_path",
                    type=ParameterType.STRING,
                    description="Specific file to search",
                    required=False,
                ),
                Parameter(
                    name="directory",
                    type=ParameterType.STRING,
                    description="Directory to search in",
                    required=False,
                ),
            ],
            returns="List of matches with file paths and line numbers",
            use_cases=["Finding definitions", "Locating TODOs"],
        ),
        Tool(
            name="run_terminal_command",
            description="Execute a shell command",
            parameters=[
                Parameter(
                    name="command",
                    type=ParameterType.STRING,
                    description="Shell command to run",
                    required=True,
                ),
                Parameter(
                    name="working_directory",
                    type=ParameterType.STRING,
                    description="Where to run it",
                    required=False,
                ),
                Parameter(
                    name="timeout",
                    type=ParameterType.INTEGER,
                    description="Max execution time in seconds",
                    required=False,
                ),
            ],
            returns="stdout, stderr, exit code",
            use_cases=["Running tests", "Installing packages"],
        ),
        Tool(
            name="list_directory",
            description="List files in a directory",
            parameters=[
                Parameter(
                    name="directory_path",
                    type=ParameterType.STRING,
                    description="Path to list",
                    required=True,
                ),
                Parameter(
                    name="recursive",
                    type=ParameterType.BOOLEAN,
                    description="Include subdirectories",
                    required=False,
                    default=False,
                ),
            ],
            returns="List of file paths",
            use_cases=["Exploring project structure"],
        ),
        Tool(
            name="get_function_definition",
            description="Get the full definition of a function",
            parameters=[
                Parameter(
                    name="function_name",
                    type=ParameterType.STRING,
                    description="Name of function",
                    required=True,
                ),
                Parameter(
                    name="file_path",
                    type=ParameterType.STRING,
                    description="File containing function",
                    required=False,
                ),
            ],
            returns="Function code with line numbers",
            use_cases=["Understanding code behavior"],
        ),
    ]


def get_tool_by_name(name: str) -> Tool:
    tools = get_standard_tools()
    for tool in tools:
        if tool.name == name:
            return tool
    raise ValueError(f"Tool '{name}' not found in standard tools")


from typing import List, Optional, Dict, Any
from .models import Tool


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' already registered")
        self._tools[tool.name] = tool

    def register_multiple(self, tools: List[Tool]) -> None:
        for tool in tools:
            self.register(tool)

    def get(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def get_all(self) -> List[Tool]:
        return list(self._tools.values())

    def get_names(self) -> List[str]:
        return list(self._tools.keys())

    def exists(self, name: str) -> bool:
        return name in self._tools

    def unregister(self, name: str) -> bool:
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def clear(self) -> None:
        self._tools.clear()

    def validate_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> List[str]:
        tool = self.get(tool_name)
        if tool is None:
            return [f"Tool '{tool_name}' not found in registry"]
        
        return tool.validate_arguments(arguments)

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return self.exists(name)


"""Tool registry for managing interpreter-callable tools."""

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ToolDefinition:
    """Definition of a tool that can be called from the Python interpreter."""

    name: str
    func: Callable
    description: str
    parameters: dict = field(default_factory=dict)


class ToolRegistry:
    """Central registry for interpreter-callable tools.

    Tools registered here are injected into the Python interpreter's namespace,
    making them callable as regular Python functions within executed code.

    Example:
        registry = ToolRegistry()
        registry.register("web_search", web_search_func, "Search the web", {...})

        # In executed code, web_search becomes a callable:
        # results = web_search("query")
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: dict | None = None,
    ) -> None:
        """Register a tool.

        Args:
            name: Name of the tool (how it will be called in Python code)
            func: The callable function
            description: Human-readable description for documentation
            parameters: JSON schema-style dict describing parameters
        """
        if parameters is None:
            parameters = self._extract_parameters(func)
        self._tools[name] = ToolDefinition(name, func, description, parameters)

    def _extract_parameters(self, func: Callable) -> dict:
        """Extract parameter info from function signature."""
        sig = inspect.signature(func)
        properties = {}
        required = []

        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
        }

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            param_info: dict[str, Any] = {}

            # Get type annotation
            if param.annotation != inspect.Parameter.empty:
                py_type = param.annotation
                # Handle Optional types
                if hasattr(py_type, "__origin__"):
                    if py_type.__origin__ is type(None):
                        py_type = str
                    else:
                        py_type = py_type.__args__[0] if py_type.__args__ else str
                param_info["type"] = type_map.get(py_type, "string")
            else:
                param_info["type"] = "string"

            # Check if required (no default)
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
            else:
                param_info["default"] = param.default

            properties[param_name] = param_info

        return {"type": "object", "properties": properties, "required": required}

    def get_namespace(self) -> dict[str, Callable]:
        """Return dict of tool_name -> callable for globals.

        Returns:
            Dictionary mapping tool names to their callable functions
        """
        return {name: tool.func for name, tool in self._tools.items()}

    def generate_instructions(self) -> str:
        """Generate markdown documentation of available tools.

        Returns:
            Formatted markdown string documenting all registered tools
        """
        if not self._tools:
            return ""

        lines = [
            "## Available Python Tools",
            "",
            "These functions are available in the Python interpreter.",
            "Call them directly in your code (no imports needed):",
            "",
        ]

        for name, tool in self._tools.items():
            lines.append(f"### `{name}`")
            lines.append(f"{tool.description}")
            lines.append("")

            props = tool.parameters.get("properties", {})
            required = tool.parameters.get("required", [])

            if props:
                lines.append("**Parameters:**")
                for param_name, param_info in props.items():
                    param_type = param_info.get("type", "any")
                    default = param_info.get("default")
                    is_required = param_name in required

                    if is_required:
                        lines.append(f"- `{param_name}` ({param_type}, required)")
                    elif default is not None:
                        lines.append(f"- `{param_name}` ({param_type}, default={default!r})")
                    else:
                        lines.append(f"- `{param_name}` ({param_type}, optional)")
                lines.append("")

        return "\n".join(lines)

    def list_tools(self) -> list[str]:
        """Return list of registered tool names."""
        return list(self._tools.keys())

    def get_tool(self, name: str) -> ToolDefinition | None:
        """Get a tool definition by name."""
        return self._tools.get(name)

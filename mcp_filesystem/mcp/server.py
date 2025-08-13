"""
MCP Server implementation for filesystem operations.

This module implements a Model Context Protocol server that exposes
filesystem operations through the standard MCP protocol over stdio.
"""

import logging
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool

from mcp_filesystem.mcp.controller import McpFilesystemController

logger = logging.getLogger(__name__)


async def start_server(allowed_directories: List[str]) -> None:
    """
    Start the MCP filesystem server.

    Args:
        allowed_directories: List of directories where operations are permitted.
    """
    controller = McpFilesystemController(allowed_directories)
    server = Server("mcp-filesystem")

    @server.list_tools()
    async def handle_list_tools() -> List[Tool]:
        """Handle tools list request."""
        tools = controller.get_tools()
        mcp_tools = []

        for tool_info in tools:
            tool = Tool(
                name=tool_info["name"],
                description=(
                    tool_info["description"] or f"Execute {tool_info['name']} operation"
                ),
                inputSchema=tool_info.get("input_schema", {}),
            )
            mcp_tools.append(tool)
        return mcp_tools

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle tool execution request."""
        try:
            result = controller.execute_tool(name, arguments)

            if "error" in result:
                error_msg = f"Error in {name}: {result['error']}"
                logger.error(error_msg)
                return [TextContent(type="text", text=error_msg)]
            if "content" in result:
                content = result["content"]
            elif "result" in result:
                if isinstance(result["result"], str):
                    content = result["result"]
                else:
                    import json

                    content = json.dumps(result["result"], indent=2, ensure_ascii=False)
            else:
                content = str(result)
            return [TextContent(type="text", text=content)]
        except Exception as e:
            error_msg = f"Unexpected error in {name}: {str(e)}"
            logger.exception(error_msg)
            return [TextContent(type="text", text=error_msg)]

    @server.list_resources()
    async def handle_list_resources() -> List[Resource]:
        """Handle resources list request."""
        # For now, return empty list. Could be extended to expose
        # directory listings as resources in the future.
        return []

    logger.info("Starting MCP Filesystem Server")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )

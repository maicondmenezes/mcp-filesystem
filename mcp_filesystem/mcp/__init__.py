"""
MCP module for mcp_filesystem.

Contains the main controller that coordinates between the MCP protocol
and the filesystem service.
"""

from mcp_filesystem.mcp.controller import McpFilesystemController

__all__ = ["McpFilesystemController"]

"""
MCP Filesystem - Sistema de arquivos para Model Context Protocol.

Este módulo fornece funcionalidades de sistema de arquivos através do
protocolo MCP, incluindo leitura, escrita, listagem e manipulação de arquivos.
"""

__version__ = "0.1.0"
__author__ = "Frank Team"
__email__ = "team@frank.dev"

from mcp_filesystem.mcp.controller import McpFilesystemController
from mcp_filesystem.mcp.core.entities import (
    CreateDirectoryArgs,
    EditFileArgs,
    GetFileInfoArgs,
    ListDirectoryArgs,
    MoveFileArgs,
    ReadTextFileArgs,
    SearchFilesArgs,
    WriteFileArgs,
)
from mcp_filesystem.services.filesystem_service import FilesystemService

__all__ = [
    "ReadTextFileArgs",
    "WriteFileArgs",
    "EditFileArgs",
    "CreateDirectoryArgs",
    "ListDirectoryArgs",
    "GetFileInfoArgs",
    "SearchFilesArgs",
    "MoveFileArgs",
    "FilesystemService",
    "McpFilesystemController",
]

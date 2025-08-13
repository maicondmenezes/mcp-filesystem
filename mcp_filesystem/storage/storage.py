from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from mcp_filesystem.mcp.core.entities import DirectoryListing, FileInfo, SearchResult


class StorageInterface(ABC):
    """
    Abstract interface for filesystem storage operations.
    """

    @abstractmethod
    def read_text_file(
        self, path: str, head: Optional[int] = None, tail: Optional[int] = None
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def read_multiple_files(self, paths: List[str]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def write_file(self, path: str, content: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def edit_file(
        self, path: str, edits: List[Dict[str, str]], dry_run: bool = False
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def create_directory(self, path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_directory(self, path: str) -> List[FileInfo]:
        raise NotImplementedError

    @abstractmethod
    def list_directory_with_sizes(self, path: str) -> DirectoryListing:
        raise NotImplementedError

    @abstractmethod
    def get_file_info(self, path: str) -> FileInfo:
        raise NotImplementedError

    @abstractmethod
    def search_files(
        self, path: str, pattern: str, recursive: bool = False
    ) -> SearchResult:
        raise NotImplementedError

    @abstractmethod
    def move_file(self, source: str, destination: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_file(self, path: str, recursive: bool = False) -> None:
        raise NotImplementedError

import difflib
import fnmatch
import os
import shutil
import stat
from typing import Any, Dict, List, Optional

from mcp_filesystem.mcp.core.entities import DirectoryListing, FileInfo, SearchResult
from mcp_filesystem.storage.storage import StorageInterface
from mcp_filesystem.utils.path_validation import ensure_directory_exists, validate_path


class FilesystemStorage(StorageInterface):
    """
    Concrete implementation of the StorageInterface for the local filesystem.
    """

    def __init__(self, allowed_directories: List[str]):
        self.allowed_directories = [os.path.abspath(d) for d in allowed_directories]

    def read_text_file(
        self, path: str, head: Optional[int] = None, tail: Optional[int] = None
    ) -> str:
        valid_path = validate_path(path, self.allowed_directories)
        with open(valid_path, "r", encoding="utf-8") as file:
            if tail:
                lines = file.readlines()
                return "".join(lines[-tail:])
            if head:
                lines = []
                for i, line in enumerate(file):
                    if i >= head:
                        break
                    lines.append(line)
                return "".join(lines)
            return file.read()

    def read_multiple_files(self, paths: List[str]) -> Dict[str, Any]:
        results = {}
        errors = {}
        for path in paths:
            try:
                valid_path = validate_path(path, self.allowed_directories)
                with open(valid_path, "r", encoding="utf-8") as file:
                    results[path] = file.read()
            except Exception as e:
                errors[path] = str(e)
        return {"files": results, "errors": errors}

    def write_file(self, path: str, content: str) -> None:
        valid_path = validate_path(path, self.allowed_directories)
        parent_dir = os.path.dirname(valid_path)
        ensure_directory_exists(parent_dir)
        with open(valid_path, "w", encoding="utf-8") as file:
            file.write(content)

    def edit_file(
        self, path: str, edits: List[Dict[str, str]], dry_run: bool = False
    ) -> str:
        valid_path = validate_path(path, self.allowed_directories)
        with open(valid_path, "r", encoding="utf-8") as file:
            original_content = file.read()
        modified_content = original_content
        changes = []
        for edit in edits:
            if edit["old_text"] in modified_content:
                modified_content = modified_content.replace(
                    edit["old_text"], edit["new_text"]
                )
                changes.append(
                    f"Replaced: '{edit['old_text'][:50]}' with '{edit['new_text'][:50]}'"
                )
            else:
                changes.append(f"Not found: '{edit['old_text'][:50]}'")
        if dry_run:
            diff = list(
                difflib.unified_diff(
                    original_content.splitlines(keepends=True),
                    modified_content.splitlines(keepends=True),
                    fromfile=f"{path} (original)",
                    tofile=f"{path} (modified)",
                )
            )
            return f"Preview of changes:\n{''.join(diff)}"
        else:
            with open(valid_path, "w", encoding="utf-8") as file:
                file.write(modified_content)
            return "File edited successfully."

    def create_directory(self, path: str) -> None:
        valid_path = validate_path(path, self.allowed_directories)
        if not os.path.exists(valid_path):
            ensure_directory_exists(valid_path)

    def list_directory(self, path: str) -> List[FileInfo]:
        valid_path = validate_path(path, self.allowed_directories)
        if not os.path.isdir(valid_path):
            raise NotADirectoryError(f"'{path}' is not a directory.")
        entries = []
        for entry in os.listdir(valid_path):
            entry_path = os.path.join(valid_path, entry)
            entries.append(self._get_file_info(entry_path))
        return sorted(entries, key=lambda x: (not x.is_directory, x.name.lower()))

    def list_directory_with_sizes(self, path: str) -> DirectoryListing:
        entries = self.list_directory(path)
        return DirectoryListing(path=path, entries=entries, total_count=len(entries))

    def get_file_info(self, path: str) -> FileInfo:
        valid_path = validate_path(path, self.allowed_directories)
        return self._get_file_info(valid_path, path)

    def search_files(
        self, path: str, pattern: str, recursive: bool = False
    ) -> SearchResult:
        valid_base_path = validate_path(path, self.allowed_directories)
        matches = []
        if recursive:
            for root, _, files in os.walk(valid_base_path):
                for file in files:
                    if fnmatch.fnmatch(file, pattern):
                        file_path = os.path.join(root, file)
                        matches.append(self._get_file_info(file_path))
        else:
            for entry in os.listdir(valid_base_path):
                if fnmatch.fnmatch(entry, pattern):
                    entry_path = os.path.join(valid_base_path, entry)
                    if os.path.isfile(entry_path):
                        matches.append(self._get_file_info(entry_path))
        return SearchResult(
            query=pattern, base_path=path, matches=matches, total_matches=len(matches)
        )

    def move_file(self, source: str, destination: str) -> None:
        valid_source = validate_path(source, self.allowed_directories)
        valid_destination = validate_path(destination, self.allowed_directories)
        dest_parent = os.path.dirname(valid_destination)
        ensure_directory_exists(dest_parent)
        shutil.move(valid_source, valid_destination)

    def delete_file(self, path: str, recursive: bool = False) -> None:
        valid_path = validate_path(path, self.allowed_directories)
        if os.path.isdir(valid_path):
            if recursive:
                shutil.rmtree(valid_path)
            else:
                os.rmdir(valid_path)
        else:
            os.remove(valid_path)

    def _get_file_info(self, path: str, display_path: Optional[str] = None) -> FileInfo:
        stats = os.stat(path)
        return FileInfo(
            path=display_path or path,
            name=os.path.basename(path),
            size=stats.st_size,
            is_directory=os.path.isdir(path),
            created=stats.st_ctime,
            modified=stats.st_mtime,
            permissions=stat.filemode(stats.st_mode),
        )

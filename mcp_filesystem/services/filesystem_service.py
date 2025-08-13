"""
Define os serviços e a lógica de negócios para o mcp_filesystem.
"""

from mcp_filesystem.mcp.core.entities import (
    CreateDirectoryArgs,
    DeleteFileArgs,
    DirectoryListing,
    EditFileArgs,
    FileInfo,
    GetFileInfoArgs,
    ListDirectoryArgs,
    ListDirectoryWithSizesArgs,
    MoveFileArgs,
    ReadMultipleFilesArgs,
    ReadTextFileArgs,
    SearchFilesArgs,
    SearchResult,
    WriteFileArgs,
)
from mcp_filesystem.storage.storage import StorageInterface


class FilesystemService:
    """
    Serviço que implementa a lógica para as ferramentas de filesystem.
    Delega as operações de baixo nível para a camada de armazenamento.
    """

    def __init__(self, storage: StorageInterface):
        """
        Inicializa o serviço de filesystem.

        Args:
            storage: Uma implementação da StorageInterface.
        """
        self._storage = storage

    def read_text_file(self, args: ReadTextFileArgs) -> str:
        return self._storage.read_text_file(args.path, args.head, args.tail)

    def read_multiple_files(self, args: ReadMultipleFilesArgs) -> dict:
        return self._storage.read_multiple_files(args.paths)

    def write_file(self, args: WriteFileArgs) -> str:
        self._storage.write_file(args.path, args.content)
        return f"Arquivo escrito com sucesso: {args.path}"

    def edit_file(self, args: EditFileArgs) -> str:
        return self._storage.edit_file(
            args.path, [e.dict() for e in args.edits], args.dry_run
        )

    def create_directory(self, args: CreateDirectoryArgs) -> str:
        self._storage.create_directory(args.path)
        return f"Diretório criado com sucesso: {args.path}"

    def list_directory(self, args: ListDirectoryArgs) -> list:
        return self._storage.list_directory(args.path)

    def list_directory_with_sizes(
        self, args: ListDirectoryWithSizesArgs
    ) -> DirectoryListing:
        return self._storage.list_directory_with_sizes(args.path)

    def get_file_info(self, args: GetFileInfoArgs) -> FileInfo:
        return self._storage.get_file_info(args.path)

    def search_files(self, args: SearchFilesArgs) -> SearchResult:
        return self._storage.search_files(args.path, args.pattern, args.recursive)

    def move_file(self, args: MoveFileArgs) -> str:
        self._storage.move_file(args.source, args.destination)
        return f"Movido com sucesso: {args.source} → {args.destination}"

    def delete_file(self, args: DeleteFileArgs) -> str:
        self._storage.delete_file(args.path, args.recursive)
        if args.recursive:
            return f"Diretório removido recursivamente: {args.path}"
        return f"Arquivo/Diretório removido: {args.path}"

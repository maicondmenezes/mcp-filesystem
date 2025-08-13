"""
Define as entidades e modelos de dados para o mcp_filesystem.

Este módulo contém todas as classes Pydantic que definem os argumentos
e estruturas de dados utilizadas pelas ferramentas do MCP filesystem.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ReadTextFileArgs(BaseModel):
    """Argumentos para leitura de arquivo de texto."""

    path: str = Field(..., description="Caminho para o arquivo a ser lido")
    tail: Optional[int] = Field(
        None, description="Se fornecido, retorna apenas as últimas N linhas do arquivo"
    )
    head: Optional[int] = Field(
        None,
        description="Se fornecido, retorna apenas as primeiras N linhas do arquivo",
    )


class ReadMediaFileArgs(BaseModel):
    """Argumentos para leitura de arquivo de mídia."""

    path: str = Field(..., description="Caminho para o arquivo de mídia")


class ReadMultipleFilesArgs(BaseModel):
    """Argumentos para leitura de múltiplos arquivos."""

    paths: List[str] = Field(..., description="Lista de caminhos para arquivos")


class WriteFileArgs(BaseModel):
    """Argumentos para escrita de arquivo."""

    path: str = Field(..., description="Caminho onde o arquivo será criado/sobrescrito")
    content: str = Field(..., description="Conteúdo a ser escrito no arquivo")


class EditOperation(BaseModel):
    """Define uma operação de edição no arquivo."""

    old_text: str = Field(..., description="Texto a ser procurado e substituído")
    new_text: str = Field(..., description="Texto que substituirá o texto antigo")


class EditFileArgs(BaseModel):
    """Argumentos para edição de arquivo."""

    path: str = Field(..., description="Caminho para o arquivo a ser editado")
    edits: List[EditOperation] = Field(..., description="Lista de operações de edição")
    dry_run: bool = Field(False, description="Visualiza as alterações sem aplicar")


class CreateDirectoryArgs(BaseModel):
    """Argumentos para criação de diretório."""

    path: str = Field(..., description="Caminho do diretório a ser criado")


class ListDirectoryArgs(BaseModel):
    """Argumentos para listagem de diretório."""

    path: str = Field(..., description="Caminho do diretório a ser listado")


class ListDirectoryWithSizesArgs(BaseModel):
    """Argumentos para listagem de diretório com tamanhos."""

    path: str = Field(..., description="Caminho do diretório a ser listado")


class GetFileInfoArgs(BaseModel):
    """Argumentos para obter informações de arquivo."""

    path: str = Field(..., description="Caminho do arquivo/diretório")


class SearchFilesArgs(BaseModel):
    """Argumentos para busca de arquivos."""

    pattern: str = Field(..., description="Padrão de busca (glob ou regex)")
    path: str = Field(".", description="Diretório base para busca")
    recursive: bool = Field(True, description="Busca recursiva em subdiretórios")


class MoveFileArgs(BaseModel):
    """Argumentos para mover/renomear arquivo."""

    source: str = Field(..., description="Caminho origem")
    destination: str = Field(..., description="Caminho destino")


class DeleteFileArgs(BaseModel):
    """Argumentos para deletar arquivo ou diretório."""

    path: str = Field(..., description="Caminho do arquivo/diretório a ser deletado")
    recursive: bool = Field(
        False, description="Deletar recursivamente (para diretórios)"
    )


class FileInfo(BaseModel):
    """Informações sobre um arquivo ou diretório."""

    path: str = Field(..., description="Caminho completo")
    name: str = Field(..., description="Nome do arquivo/diretório")
    size: int = Field(..., description="Tamanho em bytes")
    is_directory: bool = Field(..., description="Se é um diretório")
    created: float = Field(..., description="Timestamp de criação")
    modified: float = Field(..., description="Timestamp de modificação")
    permissions: str = Field(..., description="Permissões do arquivo")


class DirectoryListing(BaseModel):
    """Resultado da listagem de um diretório."""

    path: str = Field(..., description="Caminho do diretório listado")
    entries: List[FileInfo] = Field(..., description="Lista de arquivos e diretórios")
    total_count: int = Field(..., description="Total de itens")


class SearchResult(BaseModel):
    """Resultado de uma busca de arquivos."""

    query: str = Field(..., description="Padrão de busca utilizado")
    base_path: str = Field(..., description="Diretório base da busca")
    matches: List[FileInfo] = Field(..., description="Arquivos encontrados")
    total_matches: int = Field(..., description="Total de arquivos encontrados")


class ToolInfo(BaseModel):
    """Informações sobre uma ferramenta, incluindo seu esquema de entrada."""

    name: str
    description: str
    input_schema: Optional[Dict[str, Any]]

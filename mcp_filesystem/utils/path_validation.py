"""
Utilitários para validação e manipulação de caminhos de arquivos.

Fornece funções de segurança para validar caminhos e prevenir
acessos não autorizados ao sistema de arquivos.
"""

import fnmatch
import os
from pathlib import Path
from typing import List, Optional


class PathValidationError(Exception):
    """Exceção lançada quando um caminho não é válido ou não é permitido."""

    pass


def validate_path(path: str, allowed_directories: List[str]) -> str:
    """
    Valida se um caminho está dentro dos diretórios permitidos.

    Args:
        path: Caminho a ser validado
        allowed_directories: Lista de diretórios permitidos

    Returns:
        Caminho absoluto validado

    Raises:
        PathValidationError: Se o caminho não for válido ou permitido
    """
    if not path:
        raise PathValidationError("Caminho não pode estar vazio")

    try:
        abs_path = os.path.abspath(path)
    except (OSError, ValueError) as e:
        raise PathValidationError(f"Caminho inválido: {e}")

    path_allowed = False
    for allowed_dir in allowed_directories:
        try:
            allowed_abs = os.path.abspath(allowed_dir)
            if abs_path.startswith(allowed_abs + os.sep) or abs_path == allowed_abs:
                path_allowed = True
                break
        except (OSError, ValueError):
            continue

    if not path_allowed:
        raise PathValidationError(
            f"Caminho '{abs_path}' não está dentro dos diretórios permitidos: {allowed_directories}"
        )

    return abs_path


def is_safe_path(path: str) -> bool:
    """
    Verifica se um caminho é seguro (não contém sequências perigosas).

    Args:
        path: Caminho a ser verificado

    Returns:
        True se o caminho for seguro, False caso contrário
    """
    dangerous_patterns = [
        "..",
        "~",
        "/etc/",
        "/proc/",
        "/sys/",
        "/dev/",
    ]

    normalized_path = os.path.normpath(path).lower()

    for pattern in dangerous_patterns:
        if pattern in normalized_path:
            return False

    return True


def ensure_directory_exists(path: str) -> None:
    """
    Garante que um diretório existe, criando-o se necessário.

    Args:
        path: Caminho do diretório

    Raises:
        OSError: Se não for possível criar o diretório
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def get_safe_filename(filename: str) -> str:
    """
    Retorna um nome de arquivo seguro removendo caracteres perigosos.

    Args:
        filename: Nome do arquivo original

    Returns:
        Nome do arquivo seguro
    """
    dangerous_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
    safe_name = filename

    for char in dangerous_chars:
        safe_name = safe_name.replace(char, "_")

    safe_name = " ".join(safe_name.split())
    safe_name = "_".join(safe_name.split("_"))

    safe_name = safe_name.strip(".")

    return safe_name or "unnamed_file"


def match_patterns(path: str, patterns: List[str]) -> bool:
    """
    Verifica se um caminho corresponde a algum dos padrões fornecidos.

    Args:
        path: Caminho a ser verificado
        patterns: Lista de padrões (suporta wildcards)

    Returns:
        True se corresponder a algum padrão, False caso contrário
    """
    path_name = os.path.basename(path)

    for pattern in patterns:
        if fnmatch.fnmatch(path_name, pattern) or fnmatch.fnmatch(path, pattern):
            return True

    return False


def get_relative_path(path: str, base_path: str) -> Optional[str]:
    """
    Obtém o caminho relativo de um arquivo em relação a um diretório base.

    Args:
        path: Caminho absoluto do arquivo
        base_path: Diretório base

    Returns:
        Caminho relativo ou None se não for possível calcular
    """
    try:
        return os.path.relpath(path, base_path)
    except ValueError:
        return None

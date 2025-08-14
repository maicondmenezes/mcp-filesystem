#!/usr/bin/env python3
"""
Script para configurar automaticamente o MCP em diferentes clientes AI:
- GitHub Copilot (VS Code)
- Gemini Code Assist (VS Code)
- Cline (VS Code Extension)
"""
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict

SETTINGS_FILENAME = "settings.json"
COPILOT_KEY = "github.copilot.mcp.servers"
GEMINI_KEY = "gemini.mcp.servers"


def _remove_line_comment(line: str) -> str:
    """Remove comentários de linha (//) ignorando dentro de strings"""
    in_string = False
    escape = False
    i = 0
    while i < len(line):
        char = line[i]
        if escape:
            escape = False
        elif char == "\\":
            escape = True
        elif char == '"':
            in_string = not in_string
        elif not in_string and line[i : i + 2] == "//":
            return line[:i].rstrip()
        i += 1
    return line


def parse_json_with_comments(content: str) -> dict:
    """Parse JSON que pode conter comentários (como VS Code settings.json)"""
    lines = content.split("\n")
    cleaned_lines = [
        _remove_line_comment(line)
        for line in lines
        if _remove_line_comment(line).strip()
    ]
    cleaned_content = "\n".join(cleaned_lines)
    try:
        return json.loads(cleaned_content)
    except json.JSONDecodeError:
        cleaned_content = re.sub(r",\s*([}\]])", r"\1", cleaned_content)
        return json.loads(cleaned_content)


def _index_json_files(user_root: str, client_keywords: list) -> list:
    import fnmatch

    json_paths = []
    for root, dirs, files in os.walk(user_root):
        if any(
            x in root.lower() for x in ["code", "vscode", "claude", "copilot", "gemini"]
        ):
            for filename in files:
                if fnmatch.fnmatch(filename, "*.json"):
                    file_path = Path(root) / filename
                    score = sum(1 for kw in client_keywords if kw in filename.lower())
                    if score > 0:
                        json_paths.append(file_path)
    return json_paths


def _score_candidate_files(
    json_paths: list,
    client_keywords: list,
    content_keywords: list,
    content_quick_check: list,
) -> list:
    import time

    candidate_files = []
    total_files = len(json_paths)
    print(f"🔎 Encontrados {total_files} arquivos JSON para análise...")
    for idx, file_path in enumerate(json_paths, 1):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().lower()
            content_score = sum(1 for kw in content_keywords if kw in content)
            score = sum(1 for kw in client_keywords if kw in file_path.name.lower())
            total_score = score + content_score
            quick_check = any(kw in content for kw in content_quick_check)
            if total_score > 0:
                candidate_files.append((total_score, file_path, quick_check))
        except Exception:
            continue
        progress = int((idx / total_files) * 40)
        bar = "[" + "#" * progress + "-" * (40 - progress) + f"] {idx}/{total_files}"
        print(f"\r{bar}", end="")
        time.sleep(0.01)
    print()
    return candidate_files


def _select_best_files(candidate_files: list) -> list:
    candidate_files.sort(reverse=True)
    quick_files = [f for s, f, q in candidate_files if q]
    if quick_files:
        return quick_files[:5]
    if candidate_files:
        return [f for s, f, q in candidate_files[:5]]
    return []


def find_vscode_settings() -> list:
    """Encontra o arquivo settings.json do VS Code"""
    CLIENT_KEYWORDS = ["cline", "copilot", "gemini", "mcp", "settings"]
    CONTENT_KEYWORDS = ["mcp", "filesystem", "server", "token", "endpoint"]
    CONTENT_QUICK_CHECK = ["filesystem", "mcp", "servers", "token", "path", "cwd"]
    user_root = str(Path.home())
    json_paths = _index_json_files(user_root, CLIENT_KEYWORDS)
    candidate_files = _score_candidate_files(
        json_paths, CLIENT_KEYWORDS, CONTENT_KEYWORDS, CONTENT_QUICK_CHECK
    )
    return _select_best_files(candidate_files)


def get_copilot_config(project_dir: str, allowed_dirs: list) -> Dict[str, Any]:
    """Gera configuração para GitHub Copilot"""
    return {
        COPILOT_KEY: {
            "filesystem": {
                "command": "poetry",
                "args": ["run", "mcp-filesystem", "start", "--allowed-dirs"]
                + allowed_dirs,
                "cwd": project_dir,
            }
        }
    }


def get_cline_config(project_dir: str, allowed_dirs: list) -> Dict[str, Any]:
    """Gera configuração para Cline"""
    return {
        "cline.mcpServers": {
            "filesystem": {
                "command": "poetry",
                "args": ["run", "mcp-filesystem", "start", "--allowed-dirs"]
                + allowed_dirs,
                "cwd": project_dir,
            }
        }
    }


def get_gemini_config(project_dir: str, allowed_dirs: list) -> Dict[str, Any]:
    """Gera configuração para Gemini Code Assist"""
    return {
        GEMINI_KEY: {
            "filesystem": {
                "command": "poetry",
                "args": ["run", "mcp-filesystem", "start", "--allowed-dirs"]
                + allowed_dirs,
                "cwd": project_dir,
                "env": {},
            }
        }
    }


def merge_config(
    existing: Dict[str, Any], new_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Mescla configuração existente com nova"""
    for key, value in new_config.items():
        if (
            key in existing
            and isinstance(existing[key], dict)
            and isinstance(value, dict)
        ):
            existing[key].update(value)
        else:
            existing[key] = value
    return existing


def get_client_type() -> str:
    if len(sys.argv) < 2:
        print("Uso: python setup-ai-clients.py [copilot|gemini|cline]")
        sys.exit(1)
    client_type = sys.argv[1].lower()
    if client_type not in ["copilot", "gemini", "cline"]:
        print("❌ Tipo inválido. Use 'copilot', 'gemini' ou 'cline'")
        sys.exit(1)
    return client_type


def _manual_settings_path() -> Path:
    path_input = input("Caminho completo do arquivo: ").strip()
    if path_input:
        return Path(path_input).expanduser()
    print("❌ Caminho não fornecido. Saindo...")
    sys.exit(1)


def _select_found_file(found_files: list) -> Path:
    print("\nArquivos de configuração encontrados:")
    for idx, f in enumerate(found_files, 1):
        print(f"{idx}. {f}")
    print(f"{len(found_files) + 1}. Inserir manualmente o caminho")
    escolha_arquivo = input(f"Escolha [1-{len(found_files) + 1}]: ").strip()
    try:
        escolha_num = int(escolha_arquivo)
        if 1 <= escolha_num <= len(found_files):
            return found_files[escolha_num - 1]
        elif escolha_num == len(found_files) + 1:
            return _manual_settings_path()
    except Exception:
        pass
    print("❌ Opção inválida. Saindo...")
    sys.exit(1)


def _auto_settings_path() -> Path:
    found_files = find_vscode_settings()
    if found_files:
        return _select_found_file(found_files)
    print("❌ Nenhum arquivo encontrado automaticamente.")
    return _manual_settings_path()


def resolve_settings_path() -> Path:
    print("\nComo deseja localizar o arquivo de configurações?")
    print("1. Inserir manualmente o caminho")
    print("2. Tentar pesquisar automaticamente")
    escolha = input("Escolha [1/2]: ").strip()
    if escolha == "1":
        return _manual_settings_path()
    elif escolha == "2":
        return _auto_settings_path()
    print("❌ Opção inválida. Saindo...")
    sys.exit(1)


def collect_allowed_dirs() -> list:
    home_dir = str(Path.home())
    print(f"\n📁 Diretório raiz do usuário detectado: {home_dir}")
    allowed_dirs = [home_dir]
    additional = input(
        "📂 Diretórios adicionais (separados por vírgula, Enter para pular): "
    ).strip()
    if additional:
        additional_dirs = [d.strip() for d in additional.split(",") if d.strip()]
        for d in additional_dirs:
            if d not in allowed_dirs:
                allowed_dirs.append(d)
    print(f"✅ Diretórios configurados: {allowed_dirs}")
    return allowed_dirs


def load_existing_config(settings_path: Path) -> dict:
    if settings_path.exists():
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                content = f.read()
            config = parse_json_with_comments(content)
            print("📖 Configuração existente carregada")
            return config
        except Exception as e:
            print(f"⚠️ Erro ao ler settings: {e}")
    return {}


def build_mcp_config(
    client_type: str,
    project_dir: str,
    allowed_dirs: list,
) -> dict:
    if client_type == "copilot":
        return get_copilot_config(project_dir, allowed_dirs)
    elif client_type == "gemini":
        return get_gemini_config(project_dir, allowed_dirs)
    else:
        return get_cline_config(project_dir, allowed_dirs)


def update_final_config(
    existing_config: dict, mcp_config: dict, client_type: str
) -> dict:
    CLINE_KEY = "mcpServers"
    MCP_BLOCKS = {
        "cline": (CLINE_KEY, "cline.mcpServers"),
        "copilot": (COPILOT_KEY, COPILOT_KEY),
        "gemini": (GEMINI_KEY, GEMINI_KEY),
    }
    config_key, mcp_key = MCP_BLOCKS[client_type]
    if config_key not in existing_config:
        existing_config[config_key] = {}
    existing_config[config_key]["filesystem"] = mcp_config[mcp_key]["filesystem"]
    return existing_config


def write_config(settings_path: Path, final_config: dict, client_type: str):
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(final_config, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Configuração salva: {settings_path}")
        if client_type == "copilot":
            print("\n🚀 Próximos passos para GitHub Copilot:")
            print("1. Recarregue o VS Code (Ctrl+Shift+P → Reload Window)")
            print("2. Verifique se o GitHub Copilot está conectado")
            print("3. O MCP deve estar disponível automaticamente")
        elif client_type == "cline":
            print("\n🚀 Próximos passos para Cline:")
            print("1. Recarregue a janela do VS Code " "(Ctrl+Shift+P → Reload Window)")
            print("2. Abra o Cline e verifique se o MCP " "aparece nas configurações")
            print("3. Teste com um comando de arquivo")
        else:
            print("\n🚀 Próximos passos para Gemini Code Assist:")
            print("1. Certifique-se de ter a extensão Gemini " "Code Assist instalada")
            print("2. Recarregue o VS Code")
            print("3. Verifique as configurações do Gemini")
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
        sys.exit(1)


def main():
    client_type = get_client_type()
    client_names = {
        "copilot": "GitHub Copilot",
        "gemini": "Gemini Code Assist",
        "cline": "Cline",
    }
    print(f"🤖 Configurador automático do {client_names[client_type]}")
    print("=" * 60)
    project_dir = os.getcwd()
    settings_path = resolve_settings_path()
    allowed_dirs = collect_allowed_dirs()
    mcp_config = build_mcp_config(client_type, project_dir, allowed_dirs)
    existing_config = load_existing_config(settings_path)
    final_config = update_final_config(
        existing_config,
        mcp_config,
        client_type,
    )
    write_config(settings_path, final_config, client_type)


if __name__ == "__main__":
    main()

import os
import sys
from pathlib import Path

CAMINHO_COMPLETO_DO_ARQUIVO_PROMPT = "Caminho completo do arquivo: "
CAMINHO_NAO_FORNECIDO_MSG = "❌ Caminho não fornecido. Saindo..."
OPCAO_INVALIDA_MSG = "❌ Opção inválida. Saindo..."


def get_default_path(client_type: str) -> None | str:
    home = str(Path.home())
    default_paths = {
        "copilot": os.path.join(home, ".config", "Code", "User", "mcp.json"),
        "cline": os.path.join(
            home,
            ".config",
            "Code",
            "User",
            "globalStorage",
            "saoudrizwan.claude-dev",
            "settings",
            "cline_mcp_settings.json",
        ),
        "gemini": os.path.join(home, ".gemini", "settings.json"),
    }
    return default_paths.get(client_type)


def prompt_config_path(client_type: str, auto_search_func) -> Path:
    default_path = get_default_path(client_type)
    print(f"\nComo deseja localizar o arquivo de configurações do {client_type}?")
    print(f"1. Usar caminho padrão: {default_path}")
    print("2. Tentar identificar automaticamente")
    print("3. Digitar manualmente o caminho")
    escolha = input("Escolha [1/2/3]: ").strip()
    if escolha == "1":
        if default_path is None:
            print(CAMINHO_NAO_FORNECIDO_MSG)
            sys.exit(1)
        return Path(default_path).expanduser()
    elif escolha == "2":
        return _prompt_auto_search(auto_search_func)
    elif escolha == "3":
        return _prompt_manual_path()
    else:
        print(OPCAO_INVALIDA_MSG)
        sys.exit(1)


def _prompt_manual_path() -> Path:
    path_input = input(CAMINHO_COMPLETO_DO_ARQUIVO_PROMPT).strip()
    if path_input:
        return Path(path_input).expanduser()
    print(CAMINHO_NAO_FORNECIDO_MSG)
    sys.exit(1)


def _prompt_auto_search(auto_search_func) -> Path:
    found_files = auto_search_func()
    if found_files:
        print("\nArquivos de configuração encontrados:")
        for idx, f in enumerate(found_files, 1):
            print(f"{idx}. {f}")
        print(f"{len(found_files) + 1}. Digitar manualmente o caminho")
        escolha_arquivo = input(f"Escolha [1-{len(found_files) + 1}]: ").strip()
        try:
            escolha_num = int(escolha_arquivo)
            if 1 <= escolha_num <= len(found_files):
                return found_files[escolha_num - 1]
            elif escolha_num == len(found_files) + 1:
                return _prompt_manual_path()
        except Exception:
            print(OPCAO_INVALIDA_MSG)
            sys.exit(1)
    else:
        print("❌ Nenhum arquivo encontrado automaticamente.")
    return _prompt_manual_path()


def get_client_type() -> str:
    print("\nQual client deseja configurar?")
    print("1. GitHub Copilot")
    print("2. Gemini Code Assist")
    print("3. Cline")
    escolha = input("Escolha [1/2/3]: ").strip()
    if escolha == "1":
        return "copilot"
    elif escolha == "2":
        return "gemini"
    elif escolha == "3":
        return "cline"
    else:
        print(OPCAO_INVALIDA_MSG)
        sys.exit(1)

import json
import os
import sys
from pathlib import Path

from .config_paths import get_client_type, prompt_config_path
from .file_search import find_vscode_settings
from .mcp_config import build_mcp_config, update_final_config


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


def parse_json_with_comments(content: str) -> dict:
    import re

    lines = content.split("\n")
    cleaned_lines = [
        line for line in lines if line.strip() and not line.strip().startswith("//")
    ]
    cleaned_content = "\n".join(cleaned_lines)
    try:
        return json.loads(cleaned_content)
    except json.JSONDecodeError:
        cleaned_content = re.sub(r",\s*([}\]])", r"\1", cleaned_content)
        return json.loads(cleaned_content)


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
            print("1. Recarregue a janela do VS Code (Ctrl+Shift+P → Reload Window)")
            print("2. Abra o Cline e verifique se o MCP aparece nas configurações")
            print("3. Teste com um comando de arquivo")
        else:
            print("\n🚀 Próximos passos para Gemini Code Assist:")
            print("1. Certifique-se de ter a extensão Gemini Code Assist instalada")
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
    settings_path = prompt_config_path(client_type, find_vscode_settings)
    allowed_dirs = collect_allowed_dirs()
    mcp_config = build_mcp_config(client_type, project_dir, allowed_dirs)
    existing_config = load_existing_config(settings_path)
    final_config = update_final_config(existing_config, mcp_config, client_type)
    write_config(settings_path, final_config, client_type)


if __name__ == "__main__":
    main()

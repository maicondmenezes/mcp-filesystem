from typing import Any, Dict

COPILOT_KEY = "github.copilot.mcp.servers"
GEMINI_KEY = "gemini.mcp.servers"
CLINE_KEY = "mcpServers"


def get_copilot_config(allowed_dirs: list) -> Dict[str, Any]:
    return {
        "servers": {
            "mcp-filesystem": {
                "type": "stdio",
                "command": "poetry",
                "args": [
                    "run",
                    "mcp-filesystem",
                    "start",
                    "--allowed-dirs",
                    ",".join(allowed_dirs),
                ],
            }
        }
    }


def get_gemini_config(project_dir: str, allowed_dirs: list) -> Dict[str, Any]:
    return {
        "mcpServers": {
            "filesystem": {
                "command": "poetry",
                "args": [
                    "run",
                    "mcp-filesystem",
                    "start",
                    "--allowed-dirs",
                    ",".join(allowed_dirs),
                ],
                "cwd": project_dir,
            }
        }
    }


def get_cline_config(project_dir: str, allowed_dirs: list) -> Dict[str, Any]:
    return {
        "mcpServers": {
            "filesystem": {
                "command": "poetry",
                "args": ["run", "mcp-filesystem", "start", "--allowed-dirs"]
                + allowed_dirs,
                "cwd": project_dir,
            }
        }
    }


def update_final_config(
    existing_config: dict, mcp_config: dict, client_type: str
) -> dict:
    MCP_BLOCKS = {
        "copilot": ("servers", "servers"),
        "gemini": ("mcpServers", "mcpServers"),
        "cline": ("mcpServers", "mcpServers"),
    }
    if client_type in MCP_BLOCKS:
        config_key, mcp_key = MCP_BLOCKS[client_type]
        if config_key not in existing_config:
            existing_config[config_key] = {}

        if client_type == "cline":
            existing_config[config_key]["filesystem"] = mcp_config[mcp_key][
                "filesystem"
            ]
        elif client_type == "gemini":
            existing_config[config_key]["filesystem"] = mcp_config[mcp_key][
                "filesystem"
            ]
        elif client_type == "copilot":
            existing_config[config_key]["mcp-filesystem"] = mcp_config[mcp_key][
                "mcp-filesystem"
            ]
    return existing_config


# Função central para construir o bloco de configuração do MCP conforme o client
def build_mcp_config(client_type: str, project_dir: str, allowed_dirs: list) -> dict:
    if client_type == "copilot":
        return get_copilot_config(allowed_dirs)
    elif client_type == "gemini":
        return get_gemini_config(project_dir, allowed_dirs)
    elif client_type == "cline":
        return get_cline_config(project_dir, allowed_dirs)
    else:
        raise ValueError(f"Tipo de client desconhecido: {client_type}")

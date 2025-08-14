import fnmatch
import os
import time
from pathlib import Path


def index_json_files(user_root: str, client_keywords: list) -> list:
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


def score_candidate_files(
    json_paths: list,
    client_keywords: list,
    content_keywords: list,
    content_quick_check: list,
) -> list:
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


def select_best_files(candidate_files: list) -> list:
    candidate_files.sort(reverse=True)
    quick_files = [f for s, f, q in candidate_files if q]
    if quick_files:
        return quick_files[:5]
    if candidate_files:
        return [f for s, f, q in candidate_files[:5]]
    return []


def find_vscode_settings() -> list:
    CLIENT_KEYWORDS = ["cline", "copilot", "gemini", "mcp", "settings"]
    CONTENT_KEYWORDS = ["mcp", "filesystem", "server", "token", "endpoint"]
    CONTENT_QUICK_CHECK = ["filesystem", "mcp", "servers", "token", "path", "cwd"]
    user_root = str(Path.home())
    json_paths = index_json_files(user_root, CLIENT_KEYWORDS)
    candidate_files = score_candidate_files(
        json_paths, CLIENT_KEYWORDS, CONTENT_KEYWORDS, CONTENT_QUICK_CHECK
    )
    return select_best_files(candidate_files)

import asyncio
import os
from typing import List

import typer
from typing_extensions import Annotated

app = typer.Typer(
    name="mcp-filesystem",
    help="MCP server for filesystem operations.",
    add_completion=False,
)


@app.command()
def start(
    host: Annotated[
        str, typer.Option(help="Host to bind the server to.")
    ] = "127.0.0.1",
    port: Annotated[int, typer.Option(help="Port to run the server on.")] = 8000,
    allowed_dirs: Annotated[
        List[str] | None, typer.Option(help="Allowed directories for operations.")
    ] = None,
) -> None:
    """
    Starts the MCP server.
    """
    if not allowed_dirs:
        allowed_dirs = [os.getcwd()]

    print("Validating allowed directories...")
    invalid_dirs = []
    for directory in allowed_dirs:
        abs_dir = os.path.abspath(directory)
        if os.path.exists(abs_dir) and os.path.isdir(abs_dir):
            print(f"✓ {abs_dir}")
        else:
            invalid_dirs.append(abs_dir)
            print(f"✗ {abs_dir} (does not exist or is not a directory)")

    if invalid_dirs:
        print(f"\n{len(invalid_dirs)} invalid directory(s) found.")
        raise typer.Exit(code=1)

    print("Starting mcp-filesystem server on stdio (host/port args ignored for MCP)")
    print(f"Allowed directories: {allowed_dirs}")

    try:
        from mcp_filesystem.mcp.server import start_server

        asyncio.run(start_server(allowed_dirs))
    except ImportError as e:
        print(f"Error importing MCP server: {e}")
        print("Make sure 'mcp' dependency is installed: poetry install")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error starting server: {e}")
        raise typer.Exit(code=1)
    finally:
        print("Server stopped.")


@app.command()
def validate_dirs(
    directories: Annotated[List[str], typer.Argument(help="Directories to validate.")]
) -> None:
    """
    Validates if the specified directories are accessible.
    """
    print("Validating directories...")
    invalid_dirs = []
    for directory in directories:
        abs_dir = os.path.abspath(directory)
        if os.path.exists(abs_dir) and os.path.isdir(abs_dir):
            print(f"✓ {abs_dir}")
        else:
            invalid_dirs.append(abs_dir)
            print(f"✗ {abs_dir} (does not exist or is not a directory)")

    if invalid_dirs:
        print(f"\n{len(invalid_dirs)} invalid directory(s) found.")
        raise typer.Exit(code=1)
    else:
        print("\n✓ All directories are valid.")


@app.command()
def version() -> None:
    """
    Displays the version of the MCP.
    """
    try:
        import importlib.metadata

        version = importlib.metadata.version("mcp-filesystem")
        print(f"mcp-filesystem v{version}")
    except Exception:
        print("mcp-filesystem v0.1.0")


if __name__ == "__main__":
    app()

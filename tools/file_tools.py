import os
from pathlib import Path
from langchain_core.tools import tool

WORKSPACE = Path("./workspace").resolve()
WORKSPACE.mkdir(exist_ok=True)

def _safe_path(path: str) -> Path:
    full = (WORKSPACE / path).resolve()
    if not str(full).startswith(str(WORKSPACE)):
        raise ValueError("Access denied: Path outside workspace")
    return full

@tool
def list_files(directory: str = ".") -> str:
    """List all files and folders in the given directory inside the workspace."""
    try:
        path = _safe_path(directory)
        if not path.exists():
            return f"Directory not found: {directory}"
        items = []
        for item in sorted(path.iterdir()):
            prefix = "📁 " if item.is_dir() else "📄 "
            items.append(f"{prefix}{item.name}")
        return "\n".join(items) if items else "Empty directory"
    except Exception as e:
        return f"Error listing files: {str(e)}"

@tool
def read_file(file_path: str) -> str:
    """Read the content of a file from the workspace."""
    try:
        path = _safe_path(file_path)
        if not path.exists():
            return f"File not found: {file_path}"
        if path.is_dir():
            return f"{file_path} is a directory"
        content = path.read_text(encoding="utf-8")
        if len(content) > 15000:
            return content[:15000] + "\n\n... [truncated]"
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

@tool
def write_file(file_path: str, content: str) -> str:
    """Write content to a file in the workspace. Risky operation."""
    try:
        path = _safe_path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"✅ Successfully wrote to {file_path} ({len(content)} characters)"
    except Exception as e:
        return f"❌ Error writing file: {str(e)}"

@tool
def create_directory(dir_path: str) -> str:
    """Create a new directory inside the workspace."""
    try:
        path = _safe_path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        return f"✅ Directory created: {dir_path}"
    except Exception as e:
        return f"❌ Error creating directory: {str(e)}"

@tool
def delete_file(file_path: str) -> str:
    """Delete a file from the workspace."""
    try:
        path = _safe_path(file_path)
        if not path.exists():
            return f"File not found: {file_path}"
        if path.is_dir():
            return "Use a different tool for directories"
        path.unlink()
        return f"🗑️ Deleted: {file_path}"
    except Exception as e:
        return f"❌ Error deleting file: {str(e)}"

file_tools = [list_files, read_file, write_file, create_directory, delete_file]

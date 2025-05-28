import os
from pathlib import Path
from typing import Optional

from agno.tools import tool
from ..security.security import validate_path_or_error, get_safe_path, truncate_output


@tool()
def get_project_structure(root_path: Optional[str] = None) -> str:
    """Get the current project structure in markdown format.

    This tool provides a real-time view of the project structure, automatically
    ignoring virtual environments, cache directories, and temporary files.

    Args:
        root_path: Project root path. If None, uses current working directory.

    Returns:
        Project structure in markdown format with file tree and project information
    """
    try:
        if root_path is None:
            root_path = os.getcwd()

        security_error = validate_path_or_error(root_path)
        if security_error:
            return security_error

        safe_path = get_safe_path(root_path)

        ignore_dirs = {
            ".venv",
            "venv",
            "env",
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            ".coverage",
            "dist",
            "build",
            ".tox",
            ".nox",
            "htmlcov",
        }

        ignore_files = {
            ".DS_Store",
            "Thumbs.db",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".Python",
            "*.so",
            "*.egg-info",
            ".coverage",
            "*.log",
        }

        def should_ignore_file(file_path):
            """Check if a file should be ignored"""
            file_name = file_path.name
            return (
                file_name in ignore_files
                or file_name.startswith(".")
                and file_name
                not in {
                    ".env",
                    ".env.example",
                    ".gitignore",
                    ".python-version",
                    ".pre-commit-config.yaml",
                }
                or file_name.endswith((".pyc", ".pyo", ".pyd", ".so", ".log"))
            )

        def generate_tree(path, prefix="", is_last=True):
            """Recursively generate directory tree"""
            path = Path(path)

            if not path.exists():
                return ""

            connector = "└── " if is_last else "├── "
            result = (
                f"{prefix}{connector}{path.name}/\n"
                if path.is_dir()
                else f"{prefix}{connector}{path.name}\n"
            )

            if path.is_dir() and path.name not in ignore_dirs:
                try:
                    items = sorted(
                        [
                            item
                            for item in path.iterdir()
                            if not (item.is_dir() and item.name in ignore_dirs)
                            and not (item.is_file() and should_ignore_file(item))
                        ]
                    )

                    dirs = [item for item in items if item.is_dir()]
                    files = [item for item in items if item.is_file()]

                    all_items = dirs + files

                    for i, item in enumerate(all_items):
                        is_last_item = i == len(all_items) - 1
                        new_prefix = prefix + ("    " if is_last else "│   ")
                        result += generate_tree(item, new_prefix, is_last_item)

                except PermissionError:
                    pass

            return result

        root = Path(safe_path)
        project_name = root.name

        markdown_output = f"""🏗️ **CURRENT PROJECT STRUCTURE**

# Project Structure: {project_name}

```
{project_name}/
"""

        try:
            items = sorted(
                [
                    item
                    for item in root.iterdir()
                    if not (item.is_dir() and item.name in ignore_dirs)
                    and not (item.is_file() and should_ignore_file(item))
                ]
            )

            dirs = [item for item in items if item.is_dir()]
            files = [item for item in items if item.is_file()]
            all_items = dirs + files

            for i, item in enumerate(all_items):
                is_last_item = i == len(all_items) - 1
                markdown_output += generate_tree(item, "", is_last_item)

        except PermissionError:
            markdown_output += "Error: No permissions to read directory.\n"

        markdown_output += "```\n"

        markdown_output += f"""

- **Root directory:** `{safe_path}`
"""

        return truncate_output(markdown_output)

    except ValueError as e:
        return f"🚫 Security Error: {str(e)}"
    except Exception as e:
        return f"❌ Error generating project structure: {str(e)}"

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
            # ".venv",
            # "venv",
            # "env",
            "__pycache__",
            # ".git",
            # "node_modules",
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


@tool()
def detect_dependency_manager(root_path: Optional[str] = None) -> str:
    """Detect the dependency/package manager used in the project.

    Analyzes project structure to identify the primary dependency manager
    and provides specific commands for package installation.

    Args:
        root_path: Project root path. If None, uses current working directory.

    Returns:
        Information about detected dependency manager and recommended commands
    """
    try:
        if root_path is None:
            root_path = os.getcwd()

        security_error = validate_path_or_error(root_path)
        if security_error:
            return security_error

        safe_path = get_safe_path(root_path)
        root = Path(safe_path)

        detected_managers = []
        primary_manager = None

        # Python dependency managers (priority order)
        if (root / "uv.lock").exists():
            detected_managers.append("UV (uv.lock found)")
            primary_manager = {
                "name": "UV",
                "install": "uv add <package>",
                "remove": "uv remove <package>",
                "sync": "uv sync",
                "dev": "uv add --dev <package>",
                "requires_venv": False,
            }
        elif (root / "pyproject.toml").exists():
            pyproject_content = ""
            try:
                with open(root / "pyproject.toml", "r", encoding="utf-8") as f:
                    pyproject_content = f.read()
            except (FileNotFoundError, PermissionError, UnicodeDecodeError):
                pass

            if "[tool.uv]" in pyproject_content:
                detected_managers.append("UV (pyproject.toml with [tool.uv])")
                primary_manager = {
                    "name": "UV",
                    "install": "uv add <package>",
                    "remove": "uv remove <package>",
                    "sync": "uv sync",
                    "dev": "uv add --dev <package>",
                    "requires_venv": False,
                }
            elif "[tool.poetry]" in pyproject_content:
                detected_managers.append("Poetry (pyproject.toml with [tool.poetry])")
                primary_manager = {
                    "name": "Poetry",
                    "install": "poetry add <package>",
                    "remove": "poetry remove <package>",
                    "sync": "poetry install",
                    "dev": "poetry add --group dev <package>",
                    "requires_venv": False,
                }
            elif "[tool.pdm]" in pyproject_content:
                detected_managers.append("PDM (pyproject.toml with [tool.pdm])")
                primary_manager = {
                    "name": "PDM",
                    "install": "pdm add <package>",
                    "remove": "pdm remove <package>",
                    "sync": "pdm install",
                    "dev": "pdm add --dev <package>",
                    "requires_venv": False,
                }
        elif (root / "poetry.lock").exists():
            detected_managers.append("Poetry (poetry.lock found)")
            primary_manager = {
                "name": "Poetry",
                "install": "poetry add <package>",
                "remove": "poetry remove <package>",
                "sync": "poetry install",
                "dev": "poetry add --group dev <package>",
                "requires_venv": False,
            }
        elif (root / "Pipfile").exists() or (root / "Pipfile.lock").exists():
            detected_managers.append("Pipenv (Pipfile found)")
            primary_manager = {
                "name": "Pipenv",
                "install": "pipenv install <package>",
                "remove": "pipenv uninstall <package>",
                "sync": "pipenv install",
                "dev": "pipenv install --dev <package>",
                "requires_venv": False,
            }
        elif (root / "requirements.txt").exists():
            detected_managers.append("Pip (requirements.txt found)")
            primary_manager = {
                "name": "Pip",
                "install": "pip install <package>",
                "remove": "pip uninstall <package>",
                "sync": "pip install -r requirements.txt",
                "dev": "pip install <package>  # Add to requirements-dev.txt",
                "requires_venv": True,
            }

        # JavaScript/Node.js dependency managers
        if (root / "yarn.lock").exists():
            detected_managers.append("Yarn (yarn.lock found)")
            if not primary_manager:  # Only set if no Python manager found
                primary_manager = {
                    "name": "Yarn",
                    "install": "yarn add <package>",
                    "remove": "yarn remove <package>",
                    "sync": "yarn install",
                    "dev": "yarn add --dev <package>",
                    "requires_venv": False,
                }
        elif (root / "pnpm-lock.yaml").exists():
            detected_managers.append("PNPM (pnpm-lock.yaml found)")
            if not primary_manager:
                primary_manager = {
                    "name": "PNPM",
                    "install": "pnpm add <package>",
                    "remove": "pnpm remove <package>",
                    "sync": "pnpm install",
                    "dev": "pnpm add --save-dev <package>",
                    "requires_venv": False,
                }
        elif (root / "package-lock.json").exists() or (root / "package.json").exists():
            detected_managers.append("NPM (package.json found)")
            if not primary_manager:
                primary_manager = {
                    "name": "NPM",
                    "install": "npm install <package>",
                    "remove": "npm uninstall <package>",
                    "sync": "npm install",
                    "dev": "npm install --save-dev <package>",
                    "requires_venv": False,
                }

        # Other language managers
        if (root / "Cargo.toml").exists():
            detected_managers.append("Cargo (Cargo.toml found)")
            if not primary_manager:
                primary_manager = {
                    "name": "Cargo",
                    "install": "cargo add <package>",
                    "remove": "cargo remove <package>",
                    "sync": "cargo build",
                    "dev": "cargo add --dev <package>",
                    "requires_venv": False,
                }

        if (root / "go.mod").exists():
            detected_managers.append("Go Modules (go.mod found)")

        if (root / "Gemfile").exists():
            detected_managers.append("Bundler (Gemfile found)")

        if (root / "composer.json").exists():
            detected_managers.append("Composer (composer.json found)")

        # Virtual environment detection for Python
        venv_dirs = []
        for venv_name in [".venv", "venv", "env"]:
            if (root / venv_name).exists():
                venv_dirs.append(venv_name)

        # Build response
        result = "📦 **DEPENDENCY MANAGER DETECTION**\n\n"

        if not detected_managers:
            result += "❌ **No dependency manager detected**\n"
            result += "Consider initializing a project with:\n"
            result += "- Python: `uv init` or `poetry init`\n"
            result += "- Node.js: `npm init` or `yarn init`\n"
            result += "- Rust: `cargo init`\n"
            return result

        result += f"🔍 **Detected managers**: {', '.join(detected_managers)}\n\n"

        if primary_manager:
            pm = primary_manager
            result += f"✅ **Primary Manager**: {pm['name']}\n\n"
            result += "**Recommended Commands:**\n"
            result += f"- Install package: `{pm['install']}`\n"
            result += f"- Remove package: `{pm['remove']}`\n"
            result += f"- Sync dependencies: `{pm['sync']}`\n"
            result += f"- Install dev dependency: `{pm['dev']}`\n\n"

            if pm["requires_venv"]:
                result += "⚠️ **CRITICAL**: This manager requires virtual environment activation!\n"
                if venv_dirs:
                    result += f"Virtual environments found: {', '.join(venv_dirs)}\n"
                    result += "Activate before installing: source .venv/bin/activate (Unix) or .venv\\Scripts\\activate (Windows)\n"
                else:
                    result += "❌ No virtual environment found. Create one first!\n"
            else:
                result += "✅ No virtual environment activation required\n"

        if venv_dirs and primary_manager and not primary_manager["requires_venv"]:
            result += (
                f"\n📁 **Virtual environments detected**: {', '.join(venv_dirs)}\n"
            )

        return truncate_output(result)

    except ValueError as e:
        return f"🚫 Security Error: {str(e)}"
    except Exception as e:
        return f"❌ Error detecting dependency manager: {str(e)}"

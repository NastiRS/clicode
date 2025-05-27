import shutil
from typing import Optional

from agno.tools import tool
from ..security.security import validate_path_or_error, get_safe_path, truncate_output
from ..security.file_validation import validate_file_access, format_validation_message
from ..security.advanced_patch_system import apply_search_replace_patch


@tool()
def read_file(path: str) -> str:
    """Reads the complete content of a file within the working directory with advanced validation.

    Args:
        path: Path of the file to read (must be within working directory)

    Returns:
        File content as string with validation information
    """
    try:
        # Validate path security
        security_error = validate_path_or_error(path)
        if security_error:
            return security_error

        # Get safe path
        safe_path = get_safe_path(path)

        # Advanced file validation
        validation_result = validate_file_access(str(safe_path))
        validation_msg = format_validation_message(validation_result)

        if not validation_result.is_valid:
            return validation_msg

        with open(safe_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Build response with validation info
        response = f"{validation_msg}\n\n"
        response += f"📄 File: {path}\n"
        if validation_result.file_type:
            response += f"🏷️ Type: {validation_result.file_type.category} ({validation_result.file_type.mime_type})\n"
        response += f"📏 Size: {len(content)} characters\n\n"
        response += "Content:\n"
        response += content

        # Truncate if content is too large
        return truncate_output(response)

    except FileNotFoundError:
        return f"❌ Error: The file '{path}' does not exist."
    except ValueError as e:
        return f"🚫 Security Error: {str(e)}"
    except Exception as e:
        return f"❌ Error reading file: {str(e)}"


@tool()
def write_file(path: str, content: str, overwrite: bool = True) -> str:
    """Creates or edits a file with the specified content within the working directory.

    Args:
        path: Path of the file to create/edit (must be within working directory)
        content: Content to write to the file
        overwrite: If True, overwrites existing file

    Returns:
        Confirmation message
    """
    try:
        # Validate path security
        security_error = validate_path_or_error(path)
        if security_error:
            return security_error

        # Get safe path
        safe_path = get_safe_path(path)

        # Create parent directories if they don't exist (but only within working dir)
        safe_path.parent.mkdir(parents=True, exist_ok=True)

        if not overwrite and safe_path.exists():
            return (
                f"❌ Error: The file '{path}' already exists and overwrite is disabled."
            )

        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)

        action = "created" if not safe_path.exists() else "updated"
        return f"✅ File '{path}' {action} successfully."

    except ValueError as e:
        return f"🚫 Security Error: {str(e)}"
    except Exception as e:
        return f"❌ Error writing file: {str(e)}"


@tool()
def delete_file(path: str) -> str:
    """Deletes a file or directory within the working directory.

    Args:
        path: Path of the file or directory to delete (must be within working directory)

    Returns:
        Confirmation message
    """
    try:
        # Validate path security
        security_error = validate_path_or_error(path)
        if security_error:
            return security_error

        # Get safe path
        safe_path = get_safe_path(path)

        if safe_path.is_file():
            safe_path.unlink()
            return f"✅ File '{path}' deleted successfully."
        elif safe_path.is_dir():
            shutil.rmtree(safe_path)
            return f"✅ Directory '{path}' deleted successfully."
        else:
            return f"❌ Error: '{path}' does not exist."

    except ValueError as e:
        return f"🚫 Security Error: {str(e)}"
    except Exception as e:
        return f"❌ Error deleting: {str(e)}"


@tool()
def list_files(
    directory: str = ".", pattern: Optional[str] = None, recursive: bool = False
) -> str:
    """Lists files in a directory with filtering options within the working directory.

    Args:
        directory: Directory to explore (current by default, must be within working directory)
        pattern: Search pattern (e.g.: "*.py", "test*")
        recursive: If True, searches recursively in subdirectories

    Returns:
        List of found files
    """
    try:
        # Validate path security
        security_error = validate_path_or_error(directory)
        if security_error:
            return security_error

        # Get safe path
        safe_path = get_safe_path(directory)

        if not safe_path.exists():
            return f"❌ Error: The directory '{directory}' does not exist."

        if recursive:
            if pattern:
                files = list(safe_path.rglob(pattern))
            else:
                files = list(safe_path.rglob("*"))
        else:
            if pattern:
                files = list(safe_path.glob(pattern))
            else:
                files = list(safe_path.iterdir())

        # Separate files and directories
        dirs = [f for f in files if f.is_dir()]
        file_list = [f for f in files if f.is_file()]

        result = f"Contents of '{directory}':\n\n"

        if dirs:
            result += "Directories:\n"
            for d in sorted(dirs):
                result += f"  📁 {d.name}/\n"
            result += "\n"

        if file_list:
            result += "Files:\n"
            for f in sorted(file_list):
                size = f.stat().st_size
                result += f"  📄 {f.name} ({size} bytes)\n"

        if not dirs and not file_list:
            result += "No files or directories found."

        # Truncate output if too long
        return truncate_output(result)

    except ValueError as e:
        return f"🚫 Security Error: {str(e)}"
    except Exception as e:
        return f"❌ Error listing files: {str(e)}"


@tool()
def search_files(name: str, directory: str = ".", recursive: bool = True) -> str:
    """Searches for files by name intelligently within the working directory.

    Args:
        name: Name or pattern of the file to search
        directory: Directory where to search (must be within working directory)
        recursive: If True, searches in subdirectories

    Returns:
        List of found files with their paths
    """
    try:
        # Validate path security
        security_error = validate_path_or_error(directory)
        if security_error:
            return security_error

        # Get safe path
        safe_path = get_safe_path(directory)

        if not safe_path.exists():
            return f"❌ Error: The directory '{directory}' does not exist."

        # Search with different patterns
        patterns = [
            f"*{name}*",  # Contains the name
            f"{name}*",  # Starts with the name
            f"*{name}",  # Ends with the name
            name,  # Exact name
        ]

        found_files = set()

        for pattern in patterns:
            if recursive:
                matches = safe_path.rglob(pattern)
            else:
                matches = safe_path.glob(pattern)

            for match in matches:
                if match.is_file():
                    found_files.add(match)

        if not found_files:
            return f"No files found matching '{name}' in '{directory}'."

        result = f"Files found for '{name}':\n\n"
        for file in sorted(found_files):
            size = file.stat().st_size
            result += f"📄 {file} ({size} bytes)\n"

        # Truncate output if too long
        return truncate_output(result)

    except ValueError as e:
        return f"🚫 Security Error: {str(e)}"
    except Exception as e:
        return f"❌ Error searching files: {str(e)}"


@tool()
def replace_in_file(path: str, diff: str) -> str:
    """Replaces specific sections of content using advanced patch system with fuzzy matching and validation.

    Args:
        path: Path of the file to modify (must be within working directory)
        diff: One or more SEARCH/REPLACE blocks following the exact format:
              <<<<<<< SEARCH
              [exact content to find]
              =======
              [new content to replace with]
              >>>>>>> REPLACE

    Returns:
        Detailed confirmation message with validation and patch results
    """
    try:
        # Validate path security
        security_error = validate_path_or_error(path)
        if security_error:
            return security_error

        # Get safe path
        safe_path = get_safe_path(path)

        # Advanced file validation before modification
        validation_result = validate_file_access(str(safe_path))
        if not validation_result.is_valid:
            return format_validation_message(validation_result)

        # Apply advanced patch system
        patch_result = apply_search_replace_patch(
            str(safe_path), diff, create_backup=True
        )

        # Build detailed response
        response = "🔧 Advanced Patch System Results:\n\n"

        # Add validation info
        if validation_result.warnings:
            response += "⚠️ File Validation Warnings:\n"
            for warning in validation_result.warnings:
                response += f"  • {warning}\n"
            response += "\n"

        # Add patch results
        if patch_result.success:
            response += f"✅ {patch_result.message}\n"
            response += f"📊 Changes applied: {len(patch_result.applied_changes)}\n"
        else:
            response += f"❌ {patch_result.message}\n"
            if patch_result.failed_changes:
                response += "Failed changes:\n"
                for change, error in patch_result.failed_changes:
                    response += f"  • {error}\n"

        # Add warnings from patch system
        if patch_result.warnings:
            response += "\n⚠️ Patch Warnings:\n"
            for warning in patch_result.warnings:
                response += f"  • {warning}\n"

        return response.strip()

    except ValueError as e:
        return f"🚫 Security Error: {str(e)}"
    except Exception as e:
        return f"❌ Error modifying file: {str(e)}"

import os
import shutil
from pathlib import Path
from typing import Optional

from agno.tools import tool


@tool()
def read_file(path: str) -> str:
    """Reads the complete content of a file.

    Args:
        path: Path of the file to read

    Returns:
        File content as string
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: The file '{path}' does not exist."
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool()
def write_file(path: str, content: str, overwrite: bool = True) -> str:
    """Creates or edits a file with the specified content.

    Args:
        path: Path of the file to create/edit
        content: Content to write to the file
        overwrite: If True, overwrites existing file

    Returns:
        Confirmation message
    """
    try:
        # Create parent directories if they don't exist
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        if not overwrite and os.path.exists(path):
            return f"Error: The file '{path}' already exists and overwrite is disabled."

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File '{path}' {'created' if not os.path.exists(path) else 'updated'} successfully."
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool()
def delete_file(path: str) -> str:
    """Deletes a file or directory.

    Args:
        path: Path of the file or directory to delete

    Returns:
        Confirmation message
    """
    try:
        if os.path.isfile(path):
            os.remove(path)
            return f"File '{path}' deleted successfully."
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return f"Directory '{path}' deleted successfully."
        else:
            return f"Error: '{path}' does not exist."
    except Exception as e:
        return f"Error deleting: {str(e)}"


@tool()
def list_files(
    directory: str = ".", pattern: Optional[str] = None, recursive: bool = False
) -> str:
    """Lists files in a directory with filtering options.

    Args:
        directory: Directory to explore (current by default)
        pattern: Search pattern (e.g.: "*.py", "test*")
        recursive: If True, searches recursively in subdirectories

    Returns:
        List of found files
    """
    try:
        path = Path(directory)
        if not path.exists():
            return f"Error: The directory '{directory}' does not exist."

        if recursive:
            if pattern:
                files = list(path.rglob(pattern))
            else:
                files = list(path.rglob("*"))
        else:
            if pattern:
                files = list(path.glob(pattern))
            else:
                files = list(path.iterdir())

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

        return result
    except Exception as e:
        return f"Error listing files: {str(e)}"


@tool()
def search_files(name: str, directory: str = ".", recursive: bool = True) -> str:
    """Searches for files by name intelligently.

    Args:
        name: Name or pattern of the file to search
        directory: Directory where to search
        recursive: If True, searches in subdirectories

    Returns:
        List of found files with their paths
    """
    try:
        path = Path(directory)
        if not path.exists():
            return f"Error: The directory '{directory}' does not exist."

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
                matches = path.rglob(pattern)
            else:
                matches = path.glob(pattern)

            for match in matches:
                if match.is_file():
                    found_files.add(match)

        if not found_files:
            return f"No files found matching '{name}' in '{directory}'."

        result = f"Files found for '{name}':\n\n"
        for file in sorted(found_files):
            size = file.stat().st_size
            result += f"📄 {file} ({size} bytes)\n"

        return result
    except Exception as e:
        return f"Error searching files: {str(e)}"


@tool()
def replace_in_file(path: str, diff: str) -> str:
    """Replaces specific sections of content in an existing file using SEARCH/REPLACE blocks.

    Args:
        path: Path of the file to modify (relative to current working directory)
        diff: One or more SEARCH/REPLACE blocks following the exact format:
              <<<<<<< SEARCH
              [exact content to find]
              =======
              [new content to replace with]
              >>>>>>> REPLACE

    Returns:
        Confirmation message with details of changes made
    """
    try:
        # Check if file exists
        if not os.path.exists(path):
            return f"Error: The file '{path}' does not exist."

        # Read current file content
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        changes_made = 0

        # Parse SEARCH/REPLACE blocks
        blocks = []
        lines = diff.strip().split("\n")
        i = 0

        while i < len(lines):
            if lines[i].strip() == "<<<<<<< SEARCH":
                # Found start of SEARCH block
                search_content = []
                i += 1

                # Collect SEARCH content until separator
                while i < len(lines) and lines[i].strip() != "=======":
                    search_content.append(lines[i])
                    i += 1

                if i >= len(lines):
                    return "Error: Malformed diff - missing ======= separator"

                # Skip the ======= line
                i += 1

                # Collect REPLACE content until end marker
                replace_content = []
                while i < len(lines) and lines[i].strip() != ">>>>>>> REPLACE":
                    replace_content.append(lines[i])
                    i += 1

                if i >= len(lines):
                    return "Error: Malformed diff - missing >>>>>>> REPLACE marker"

                # Add the block
                search_text = "\n".join(search_content)
                replace_text = "\n".join(replace_content)
                blocks.append((search_text, replace_text))

            i += 1

        if not blocks:
            return "Error: No valid SEARCH/REPLACE blocks found in diff"

        # Apply replacements
        for search_text, replace_text in blocks:
            if search_text in content:
                content = content.replace(
                    search_text, replace_text, 1
                )  # Replace only first occurrence
                changes_made += 1
            else:
                return (
                    f"Error: Could not find the exact text to replace:\n{search_text}"
                )

        # Write the modified content back to file
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully applied {changes_made} change(s) to '{path}'"

    except Exception as e:
        return f"Error replacing content in file: {str(e)}"

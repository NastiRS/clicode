import os
import subprocess

from agno.tools import tool
from .security import (
    DEFAULT_TIMEOUT,
    validate_path_or_error,
    get_safe_path,
    truncate_output,
    WORKING_DIRECTORY,
)


@tool()
def execute_command(command: str) -> str:
    """Executes a system command with security restrictions.

    Args:
        command: The command to execute

    Returns:
        The command output or error message
    """
    try:
        # Execute with timeout and capture output
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
            cwd=str(WORKING_DIRECTORY),  # Ensure execution in working directory
        )

        # Build output
        output = f"Command: {command}\n"
        output += f"Exit code: {result.returncode}\n"

        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"

        # Truncate output if too long
        return truncate_output(output)

    except subprocess.TimeoutExpired:
        return f"⏰ Command '{command}' exceeded the {DEFAULT_TIMEOUT} second timeout"
    except Exception as e:
        return f"❌ Error executing '{command}': {str(e)}"


@tool()
def get_current_directory() -> str:
    """Gets the current working directory.

    Returns:
        The current directory path
    """
    try:
        directory = os.getcwd()
        return f"📁 Current directory: {directory}"
    except Exception as e:
        return f"❌ Error getting directory: {str(e)}"


@tool()
def change_directory(path: str) -> str:
    """Changes the working directory within the allowed workspace.

    Args:
        path: The path to the new directory (must be within working directory)

    Returns:
        Change confirmation or error message
    """
    try:
        # Validate path security
        security_error = validate_path_or_error(path)
        if security_error:
            return security_error

        # Get safe path
        safe_path = get_safe_path(path)

        if not safe_path.exists():
            return f"❌ Path does not exist: {path}"

        if not safe_path.is_dir():
            return f"❌ Path is not a directory: {path}"

        os.chdir(str(safe_path))
        new_directory = os.getcwd()
        return f"✅ Directory changed to: {new_directory}"

    except ValueError as e:
        return f"🚫 Security Error: {str(e)}"
    except Exception as e:
        return f"❌ Error changing directory: {str(e)}"

import os
import subprocess
from pathlib import Path

from agno.tools import tool


@tool()
def execute_command(command: str) -> str:
    """Executes a system command.

    Args:
        command: The command to execute

    Returns:
        The command output or error message
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
        )

        output = f"Command: {command}\n"
        output += f"Exit code: {result.returncode}\n"

        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"

        return output

    except subprocess.TimeoutExpired:
        return f"⏰ Command '{command}' exceeded the 1 minute timeout"
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
    """Changes the working directory.

    Args:
        path: The path to the new directory

    Returns:
        Change confirmation or error message
    """
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            return f"❌ Path does not exist: {path}"

        if not path_obj.is_dir():
            return f"❌ Path is not a directory: {path}"

        os.chdir(path)
        new_directory = os.getcwd()
        return f"✅ Directory changed to: {new_directory}"

    except Exception as e:
        return f"❌ Error changing directory: {str(e)}"

from pathlib import Path
from typing import Union


# Configuration constants
DEFAULT_TIMEOUT = 10  # seconds
MAX_OUTPUT_BYTES = 50 * 1024  # 50KB
MAX_OUTPUT_LINES = 1000  # 1000 lines
MAX_FILE_SIZE = 100 * 1024  # 100KB

# Get the working directory when the agent starts
WORKING_DIRECTORY = Path.cwd().resolve()


def is_path_safe(path: Union[str, Path]) -> tuple[bool, str]:
    """
    Validates if a path is safe to access (within working directory).

    Args:
        path: Path to validate

    Returns:
        Tuple of (is_safe, message)
    """
    try:
        # Convert to Path object and resolve
        path_obj = Path(path).resolve()

        # Check if path is within working directory
        try:
            path_obj.relative_to(WORKING_DIRECTORY)
            return True, "Path is safe"
        except ValueError:
            return (
                False,
                f"Path '{path}' is outside working directory '{WORKING_DIRECTORY}'",
            )

    except Exception as e:
        return False, f"Invalid path '{path}': {str(e)}"


def validate_path_or_error(path: Union[str, Path]) -> str:
    """
    Validates a path and returns an error message if unsafe.

    Args:
        path: Path to validate

    Returns:
        Error message if path is unsafe, empty string if safe
    """
    is_safe, message = is_path_safe(path)
    if not is_safe:
        return f"🚫 Security Error: {message}"
    return ""


def get_safe_path(path: Union[str, Path]) -> Path:
    """
    Returns a safe resolved path within the working directory.

    Args:
        path: Path to resolve

    Returns:
        Resolved path

    Raises:
        ValueError: If path is outside working directory
    """
    path_obj = Path(path).resolve()

    try:
        path_obj.relative_to(WORKING_DIRECTORY)
        return path_obj
    except ValueError:
        raise ValueError(
            f"Path '{path}' is outside working directory '{WORKING_DIRECTORY}'"
        )


def truncate_output(
    output: str, max_bytes: int = MAX_OUTPUT_BYTES, max_lines: int = MAX_OUTPUT_LINES
) -> str:
    """
    Truncates output to stay within limits.

    Args:
        output: Output to truncate
        max_bytes: Maximum bytes allowed
        max_lines: Maximum lines allowed

    Returns:
        Truncated output with warning if truncated
    """
    lines = output.split("\n")
    truncated = False

    # Check line limit
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        truncated = True

    # Rejoin and check byte limit
    result = "\n".join(lines)
    if len(result.encode("utf-8")) > max_bytes:
        # Truncate by bytes
        result_bytes = result.encode("utf-8")[:max_bytes]
        # Decode safely (might cut in middle of character)
        result = result_bytes.decode("utf-8", errors="ignore")
        truncated = True

    if truncated:
        result += f"\n\n⚠️ Output truncated (max {max_lines} lines, {max_bytes} bytes)"

    return result

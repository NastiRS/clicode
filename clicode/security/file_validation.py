import os
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Set
import chardet


class FileType:
    """Represents file type information."""

    def __init__(
        self, extension: str, mime_type: str, category: str, is_safe: bool = True
    ):
        self.extension = extension
        self.mime_type = mime_type
        self.category = category
        self.is_safe = is_safe


# Comprehensive file type definitions
KNOWN_FILE_TYPES: Dict[str, FileType] = {
    # Text files (safe)
    ".txt": FileType(".txt", "text/plain", "text", True),
    ".md": FileType(".md", "text/markdown", "text", True),
    ".rst": FileType(".rst", "text/x-rst", "text", True),
    # Code files (safe)
    ".py": FileType(".py", "text/x-python", "code", True),
    ".js": FileType(".js", "text/javascript", "code", True),
    ".ts": FileType(".ts", "text/typescript", "code", True),
    ".html": FileType(".html", "text/html", "code", True),
    ".css": FileType(".css", "text/css", "code", True),
    ".json": FileType(".json", "application/json", "data", True),
    ".xml": FileType(".xml", "text/xml", "data", True),
    ".yaml": FileType(".yaml", "text/yaml", "data", True),
    ".yml": FileType(".yml", "text/yaml", "data", True),
    ".toml": FileType(".toml", "text/toml", "data", True),
    ".ini": FileType(".ini", "text/plain", "config", True),
    ".cfg": FileType(".cfg", "text/plain", "config", True),
    ".conf": FileType(".conf", "text/plain", "config", True),
    # Shell scripts (potentially unsafe)
    ".sh": FileType(".sh", "text/x-shellscript", "script", False),
    ".bat": FileType(".bat", "text/x-msdos-batch", "script", False),
    ".ps1": FileType(".ps1", "text/x-powershell", "script", False),
    # Binary files (unsafe)
    ".exe": FileType(".exe", "application/x-executable", "binary", False),
    ".dll": FileType(".dll", "application/x-msdownload", "binary", False),
    ".so": FileType(".so", "application/x-sharedlib", "binary", False),
    ".dylib": FileType(".dylib", "application/x-sharedlib", "binary", False),
    # Archives (potentially unsafe)
    ".zip": FileType(".zip", "application/zip", "archive", False),
    ".tar": FileType(".tar", "application/x-tar", "archive", False),
    ".gz": FileType(".gz", "application/gzip", "archive", False),
    ".rar": FileType(".rar", "application/x-rar", "archive", False),
    # Images (safe for reading)
    ".png": FileType(".png", "image/png", "image", True),
    ".jpg": FileType(".jpg", "image/jpeg", "image", True),
    ".jpeg": FileType(".jpeg", "image/jpeg", "image", True),
    ".gif": FileType(".gif", "image/gif", "image", True),
    ".svg": FileType(".svg", "image/svg+xml", "image", True),
    # Documents (safe for reading)
    ".pdf": FileType(".pdf", "application/pdf", "document", True),
    ".doc": FileType(".doc", "application/msword", "document", True),
    ".docx": FileType(
        ".docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "document",
        True,
    ),
}

# Dangerous file patterns
DANGEROUS_PATTERNS: Set[str] = {
    "*.key",
    "*.pem",
    "*.p12",
    "*.pfx",  # Private keys
    ".env",
    "*.env",
    ".env.*",  # Environment files
    "/etc/passwd",
    "/etc/shadow",  # System files
    "id_rsa",
    "id_dsa",
    "id_ecdsa",  # SSH keys
    "*.crt",
    "*.cer",  # Certificates
    "config.json",
    "secrets.json",  # Config files
}

# Maximum file sizes for different categories (bytes)
MAX_FILE_SIZES: Dict[str, int] = {
    "text": 1024 * 1024,  # 1MB for text files
    "code": 1024 * 1024,  # 1MB for code files
    "data": 512 * 1024,  # 512KB for data files
    "config": 256 * 1024,  # 256KB for config files
    "image": 5 * 1024 * 1024,  # 5MB for images
    "document": 10 * 1024 * 1024,  # 10MB for documents
    "default": 1024 * 1024,  # 1MB default
}


class FileValidationResult:
    """Result of file validation."""

    def __init__(
        self,
        is_valid: bool,
        file_type: Optional[FileType] = None,
        warnings: List[str] = None,
        errors: List[str] = None,
    ):
        self.is_valid = is_valid
        self.file_type = file_type
        self.warnings = warnings or []
        self.errors = errors or []

    def add_warning(self, message: str):
        self.warnings.append(message)

    def add_error(self, message: str):
        self.errors.append(message)
        self.is_valid = False


def detect_file_type(file_path: str) -> Optional[FileType]:
    """
    Detect file type using multiple methods.

    Args:
        file_path: Path to the file

    Returns:
        FileType object or None if unknown
    """
    path = Path(file_path)
    extension = path.suffix.lower()

    # Check known extensions first
    if extension in KNOWN_FILE_TYPES:
        return KNOWN_FILE_TYPES[extension]

    # Try to detect using mimetypes
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        # Map common mime types to categories
        if mime_type.startswith("text/"):
            return FileType(extension, mime_type, "text", True)
        elif mime_type.startswith("image/"):
            return FileType(extension, mime_type, "image", True)
        elif mime_type.startswith("application/"):
            # Most application types are potentially unsafe
            return FileType(extension, mime_type, "binary", False)

    return None


def is_text_file(file_path: str) -> bool:
    """
    Determine if a file is a text file by examining its content.

    Args:
        file_path: Path to the file

    Returns:
        True if file appears to be text
    """
    try:
        with open(file_path, "rb") as f:
            # Read first 8KB to determine if it's text
            chunk = f.read(8192)

        if not chunk:
            return True  # Empty file is considered text

        # Try to detect encoding
        result = chardet.detect(chunk)
        if result["confidence"] > 0.7:
            return True

        # Check for null bytes (common in binary files)
        if b"\x00" in chunk:
            return False

        # Check if most characters are printable
        printable_chars = sum(
            1 for byte in chunk if 32 <= byte <= 126 or byte in [9, 10, 13]
        )
        return printable_chars / len(chunk) > 0.7

    except Exception:
        return False


def check_dangerous_patterns(file_path: str) -> List[str]:
    """
    Check if file matches dangerous patterns.

    Args:
        file_path: Path to check

    Returns:
        List of warnings for dangerous patterns
    """
    warnings = []
    path = Path(file_path)

    for pattern in DANGEROUS_PATTERNS:
        if path.match(pattern) or str(path).endswith(pattern.replace("*", "")):
            warnings.append(f"File matches dangerous pattern: {pattern}")

    return warnings


def validate_file_size(file_path: str, file_type: Optional[FileType]) -> List[str]:
    """
    Validate file size against category limits.

    Args:
        file_path: Path to the file
        file_type: Detected file type

    Returns:
        List of warnings if file is too large
    """
    warnings = []

    try:
        size = os.path.getsize(file_path)
        category = file_type.category if file_type else "default"
        max_size = MAX_FILE_SIZES.get(category, MAX_FILE_SIZES["default"])

        if size > max_size:
            size_mb = size / (1024 * 1024)
            max_mb = max_size / (1024 * 1024)
            warnings.append(
                f"File size ({size_mb:.1f}MB) exceeds limit for {category} files ({max_mb:.1f}MB)"
            )

    except OSError as e:
        warnings.append(f"Could not check file size: {e}")

    return warnings


def validate_file_access(file_path: str) -> FileValidationResult:
    """
    Comprehensive file validation inspired by Codex.

    Args:
        file_path: Path to validate

    Returns:
        FileValidationResult with validation details
    """
    result = FileValidationResult(True)
    path = Path(file_path)

    # Check if file exists
    if not path.exists():
        result.add_error(f"File does not exist: {file_path}")
        return result

    # Check if it's actually a file
    if not path.is_file():
        result.add_error(f"Path is not a file: {file_path}")
        return result

    # Detect file type
    file_type = detect_file_type(file_path)
    result.file_type = file_type

    if not file_type:
        result.add_warning("Unknown file type - proceeding with caution")
        # Try to determine if it's text
        if is_text_file(file_path):
            file_type = FileType("", "text/plain", "text", True)
            result.file_type = file_type
        else:
            result.add_warning("File appears to be binary - may not be safe to edit")

    # Check for dangerous patterns
    dangerous_warnings = check_dangerous_patterns(file_path)
    for warning in dangerous_warnings:
        result.add_warning(warning)

    # Validate file size
    size_warnings = validate_file_size(file_path, file_type)
    for warning in size_warnings:
        result.add_warning(warning)

    # Check if file type is safe for editing
    if file_type and not file_type.is_safe:
        result.add_warning(
            f"File type '{file_type.category}' may not be safe for automated editing"
        )

    # Check file permissions
    if not os.access(file_path, os.R_OK):
        result.add_error("File is not readable")

    if not os.access(file_path, os.W_OK):
        result.add_warning("File is not writable")

    return result


def get_safe_file_extensions() -> List[str]:
    """Get list of file extensions considered safe for editing."""
    return [ext for ext, file_type in KNOWN_FILE_TYPES.items() if file_type.is_safe]


def format_validation_message(result: FileValidationResult) -> str:
    """
    Format validation result into a user-friendly message.

    Args:
        result: FileValidationResult to format

    Returns:
        Formatted message string
    """
    if not result.is_valid:
        message = "❌ File validation failed:\n"
        for error in result.errors:
            message += f"  • {error}\n"
    else:
        message = "✅ File validation passed"
        if result.file_type:
            message += f" ({result.file_type.category} file)"
        message += "\n"

    if result.warnings:
        message += "⚠️ Warnings:\n"
        for warning in result.warnings:
            message += f"  • {warning}\n"

    return message.strip()

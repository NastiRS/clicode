"""
Advanced patch system inspired by Codex CLI.
Provides precise file editing with context validation and fuzzy matching.
"""

import os
import difflib
from typing import List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


class PatchAction(Enum):
    """Types of patch actions."""

    ADD = "add"
    UPDATE = "update"
    DELETE = "delete"
    MOVE = "move"


@dataclass
class Chunk:
    """Represents a chunk of changes in a file."""

    orig_index: int  # Line index in original file
    del_lines: List[str]  # Lines to delete
    ins_lines: List[str]  # Lines to insert
    context_before: List[str] = None  # Context lines before
    context_after: List[str] = None  # Context lines after

    def __post_init__(self):
        if self.context_before is None:
            self.context_before = []
        if self.context_after is None:
            self.context_after = []


@dataclass
class FileChange:
    """Represents a change to a file."""

    action: PatchAction
    path: str
    chunks: List[Chunk] = None
    new_content: Optional[str] = None
    move_to: Optional[str] = None

    def __post_init__(self):
        if self.chunks is None:
            self.chunks = []


class PatchResult:
    """Result of applying a patch."""

    def __init__(self, success: bool, message: str = ""):
        self.success = success
        self.message = message
        self.applied_changes: List[FileChange] = []
        self.failed_changes: List[Tuple[FileChange, str]] = []
        self.warnings: List[str] = []

    def add_success(self, change: FileChange):
        self.applied_changes.append(change)

    def add_failure(self, change: FileChange, error: str):
        self.failed_changes.append((change, error))
        self.success = False

    def add_warning(self, warning: str):
        self.warnings.append(warning)


class AdvancedPatchSystem:
    """Advanced patch system with context validation and fuzzy matching."""

    def __init__(self, fuzz_factor: int = 2):
        """
        Initialize patch system.

        Args:
            fuzz_factor: Number of lines of context to allow for fuzzy matching
        """
        self.fuzz_factor = fuzz_factor

    def parse_search_replace_block(self, diff_text: str) -> List[FileChange]:
        """
        Parse SEARCH/REPLACE blocks into FileChange objects.

        Args:
            diff_text: Text containing SEARCH/REPLACE blocks

        Returns:
            List of FileChange objects
        """
        changes = []
        lines = diff_text.strip().split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Look for file path indicators
            if line.startswith("<<<<<<< SEARCH"):
                # Parse search/replace block
                search_lines = []
                replace_lines = []
                i += 1

                # Collect search content
                while i < len(lines) and lines[i].strip() != "=======":
                    search_lines.append(lines[i])
                    i += 1

                if i >= len(lines):
                    raise ValueError(
                        "Invalid SEARCH/REPLACE block: missing '=======' separator"
                    )

                i += 1  # Skip =======

                # Collect replace content
                while i < len(lines) and lines[i].strip() != ">>>>>>> REPLACE":
                    replace_lines.append(lines[i])
                    i += 1

                if i >= len(lines):
                    raise ValueError(
                        "Invalid SEARCH/REPLACE block: missing '>>>>>>> REPLACE' end"
                    )

                # Create chunk
                chunk = Chunk(
                    orig_index=0,  # Will be determined during application
                    del_lines=search_lines,
                    ins_lines=replace_lines,
                )

                # For now, assume we're working with a single file
                # In a real implementation, you'd need to specify the file path
                change = FileChange(
                    action=PatchAction.UPDATE,
                    path="",  # Will be set by caller
                    chunks=[chunk],
                )
                changes.append(change)

            i += 1

        return changes

    def find_best_match(
        self, file_lines: List[str], search_lines: List[str], start_hint: int = 0
    ) -> Tuple[int, float]:
        """
        Find the best match for search lines in the file using fuzzy matching.

        Args:
            file_lines: Lines of the file to search in
            search_lines: Lines to search for
            start_hint: Hint for where to start searching

        Returns:
            Tuple of (best_match_index, confidence_score)
        """
        if not search_lines:
            return -1, 0.0

        best_match = -1
        best_score = 0.0

        # Try exact match first
        search_text = "\n".join(search_lines)
        for i in range(len(file_lines) - len(search_lines) + 1):
            file_segment = "\n".join(file_lines[i : i + len(search_lines)])
            if file_segment == search_text:
                return i, 1.0

        # Try fuzzy matching
        for i in range(len(file_lines) - len(search_lines) + 1):
            file_segment = file_lines[i : i + len(search_lines)]

            # Calculate similarity using difflib
            matcher = difflib.SequenceMatcher(None, search_lines, file_segment)
            score = matcher.ratio()

            if score > best_score:
                best_score = score
                best_match = i

        return best_match, best_score

    def apply_chunk(
        self, file_lines: List[str], chunk: Chunk
    ) -> Tuple[List[str], bool, str]:
        """
        Apply a single chunk to file lines.

        Args:
            file_lines: Current file lines
            chunk: Chunk to apply

        Returns:
            Tuple of (modified_lines, success, error_message)
        """
        if not chunk.del_lines:
            # Pure insertion
            insert_point = chunk.orig_index
            if insert_point > len(file_lines):
                return (
                    file_lines,
                    False,
                    f"Insert point {insert_point} beyond file length",
                )

            new_lines = (
                file_lines[:insert_point] + chunk.ins_lines + file_lines[insert_point:]
            )
            return new_lines, True, ""

        # Find the best match for deletion lines
        match_index, confidence = self.find_best_match(file_lines, chunk.del_lines)

        if match_index == -1:
            return file_lines, False, "Could not find matching lines to replace"

        if confidence < 0.8:  # Require high confidence for automatic application
            return (
                file_lines,
                False,
                f"Low confidence match ({confidence:.2f}) - manual review required",
            )

        # Apply the replacement
        end_index = match_index + len(chunk.del_lines)
        new_lines = file_lines[:match_index] + chunk.ins_lines + file_lines[end_index:]

        return new_lines, True, ""

    def apply_file_change(self, change: FileChange) -> PatchResult:
        """
        Apply a file change.

        Args:
            change: FileChange to apply

        Returns:
            PatchResult indicating success/failure
        """
        result = PatchResult(True)

        try:
            if change.action == PatchAction.ADD:
                return self._apply_add_file(change)
            elif change.action == PatchAction.DELETE:
                return self._apply_delete_file(change)
            elif change.action == PatchAction.UPDATE:
                return self._apply_update_file(change)
            elif change.action == PatchAction.MOVE:
                return self._apply_move_file(change)
            else:
                result.success = False
                result.message = f"Unknown action: {change.action}"

        except Exception as e:
            result.success = False
            result.message = f"Error applying change: {str(e)}"

        return result

    def _apply_add_file(self, change: FileChange) -> PatchResult:
        """Apply ADD file change."""
        result = PatchResult(True)

        if os.path.exists(change.path):
            result.success = False
            result.message = f"File already exists: {change.path}"
            return result

        try:
            # Create parent directories if needed
            os.makedirs(os.path.dirname(change.path), exist_ok=True)

            with open(change.path, "w", encoding="utf-8") as f:
                if change.new_content:
                    f.write(change.new_content)
                else:
                    # Reconstruct content from chunks
                    lines = []
                    for chunk in change.chunks:
                        lines.extend(chunk.ins_lines)
                    f.write("\n".join(lines))

            result.add_success(change)
            result.message = f"Successfully created file: {change.path}"

        except Exception as e:
            result.success = False
            result.message = f"Failed to create file {change.path}: {str(e)}"

        return result

    def _apply_delete_file(self, change: FileChange) -> PatchResult:
        """Apply DELETE file change."""
        result = PatchResult(True)

        if not os.path.exists(change.path):
            result.success = False
            result.message = f"File does not exist: {change.path}"
            return result

        try:
            os.remove(change.path)
            result.add_success(change)
            result.message = f"Successfully deleted file: {change.path}"

        except Exception as e:
            result.success = False
            result.message = f"Failed to delete file {change.path}: {str(e)}"

        return result

    def _apply_update_file(self, change: FileChange) -> PatchResult:
        """Apply UPDATE file change."""
        result = PatchResult(True)

        if not os.path.exists(change.path):
            result.success = False
            result.message = f"File does not exist: {change.path}"
            return result

        try:
            # Read current file content
            with open(change.path, "r", encoding="utf-8") as f:
                file_lines = f.read().splitlines()

            # Apply each chunk
            modified_lines = file_lines[:]
            offset = 0  # Track line offset due to insertions/deletions

            for chunk in sorted(change.chunks, key=lambda c: c.orig_index):
                # Adjust chunk index for previous modifications
                adjusted_chunk = Chunk(
                    orig_index=chunk.orig_index + offset,
                    del_lines=chunk.del_lines,
                    ins_lines=chunk.ins_lines,
                    context_before=chunk.context_before,
                    context_after=chunk.context_after,
                )

                new_lines, success, error = self.apply_chunk(
                    modified_lines, adjusted_chunk
                )

                if not success:
                    result.add_failure(change, error)
                    return result

                # Update offset
                lines_deleted = len(chunk.del_lines)
                lines_inserted = len(chunk.ins_lines)
                offset += lines_inserted - lines_deleted

                modified_lines = new_lines

            # Write modified content back
            with open(change.path, "w", encoding="utf-8") as f:
                f.write("\n".join(modified_lines))

            result.add_success(change)
            result.message = f"Successfully updated file: {change.path}"

        except Exception as e:
            result.success = False
            result.message = f"Failed to update file {change.path}: {str(e)}"

        return result

    def _apply_move_file(self, change: FileChange) -> PatchResult:
        """Apply MOVE file change."""
        result = PatchResult(True)

        if not os.path.exists(change.path):
            result.success = False
            result.message = f"Source file does not exist: {change.path}"
            return result

        if not change.move_to:
            result.success = False
            result.message = "Move destination not specified"
            return result

        try:
            # Create parent directories if needed
            os.makedirs(os.path.dirname(change.move_to), exist_ok=True)

            # Move the file
            os.rename(change.path, change.move_to)

            result.add_success(change)
            result.message = (
                f"Successfully moved file from {change.path} to {change.move_to}"
            )

        except Exception as e:
            result.success = False
            result.message = f"Failed to move file: {str(e)}"

        return result

    def validate_patch_safety(self, changes: List[FileChange]) -> List[str]:
        """
        Validate that patch changes are safe to apply.

        Args:
            changes: List of changes to validate

        Returns:
            List of safety warnings
        """
        warnings = []

        for change in changes:
            # Check for dangerous file operations
            if change.action == PatchAction.DELETE:
                warnings.append(f"Deleting file: {change.path}")

            # Check for large changes
            if change.action == PatchAction.UPDATE:
                total_deletions = sum(len(chunk.del_lines) for chunk in change.chunks)
                total_insertions = sum(len(chunk.ins_lines) for chunk in change.chunks)

                if total_deletions > 100:
                    warnings.append(
                        f"Large deletion in {change.path}: {total_deletions} lines"
                    )

                if total_insertions > 100:
                    warnings.append(
                        f"Large insertion in {change.path}: {total_insertions} lines"
                    )

        return warnings


def apply_search_replace_patch(file_path: str, diff_text: str) -> PatchResult:
    """
    Apply a search/replace patch to a file.

    Args:
        file_path: Path to the file to modify
        diff_text: SEARCH/REPLACE block text

    Returns:
        PatchResult indicating success/failure
    """
    patch_system = AdvancedPatchSystem()

    try:
        # Parse the diff text
        changes = patch_system.parse_search_replace_block(diff_text)

        if not changes:
            return PatchResult(False, "No valid SEARCH/REPLACE blocks found")

        # Set the file path for all changes
        for change in changes:
            change.path = file_path

        # Validate safety
        warnings = patch_system.validate_patch_safety(changes)

        # Apply changes
        overall_result = PatchResult(True)

        for change in changes:
            result = patch_system.apply_file_change(change)

            if result.success:
                overall_result.add_success(change)
            else:
                overall_result.add_failure(change, result.message)

            overall_result.warnings.extend(result.warnings)

        # Add safety warnings
        overall_result.warnings.extend(warnings)

        if overall_result.success:
            overall_result.message = f"Successfully applied patch to {file_path}"
        else:
            overall_result.message = f"Failed to apply patch to {file_path}"

        return overall_result

    except Exception as e:
        return PatchResult(False, f"Error processing patch: {str(e)}")

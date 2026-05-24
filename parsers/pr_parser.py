"""GitHub Pull Request diff parser."""

from __future__ import annotations

import re
from typing import Any


class PRParser:
    """Parses unified diff text from GitHub Pull Requests."""

    def parse_diff(self, diff_text: str) -> list[dict[str, Any]]:
        """
        Parse a unified diff into a list of file-level changes.

        Args:
            diff_text: Raw unified diff text.

        Returns:
            List of dicts, each representing a changed file with
            keys: filename, added_lines, removed_lines, hunks.
        """
        files: list[dict[str, Any]] = []
        current_file: dict[str, Any] | None = None

        for line in diff_text.splitlines():
            if line.startswith("diff --git"):
                if current_file:
                    files.append(current_file)
                match = re.search(r"b/(.+)$", line)
                current_file = {
                    "filename": match.group(1) if match else "",
                    "added_lines": 0,
                    "removed_lines": 0,
                    "hunks": [],
                    "status": "modified",
                }
            elif line.startswith("new file"):
                if current_file:
                    current_file["status"] = "added"
            elif line.startswith("deleted file"):
                if current_file:
                    current_file["status"] = "deleted"
            elif line.startswith("rename"):
                if current_file:
                    current_file["status"] = "renamed"
            elif line.startswith("+") and not line.startswith("+++"):
                if current_file:
                    current_file["added_lines"] += 1
            elif line.startswith("-") and not line.startswith("---"):
                if current_file:
                    current_file["removed_lines"] += 1
            elif line.startswith("@@"):
                if current_file:
                    current_file["hunks"].append(line)

        if current_file:
            files.append(current_file)

        return files

    def extract_changed_functions(self, diff_text: str, language: str = "python") -> list[str]:
        """
        Identify function/method names that were changed in the diff.

        Args:
            diff_text: Raw unified diff text.
            language: Programming language for heuristic matching.

        Returns:
            List of changed function/method names.
        """
        changed: set[str] = set()
        pattern_map = {
            "python": r"^\+.*def\s+(\w+)\s*\(",
            "javascript": r"^\+.*function\s+(\w+)\s*\(|^\+.*const\s+(\w+)\s*=.*=>",
            "typescript": r"^\+.*function\s+(\w+)\s*\(|^\+.*const\s+(\w+)\s*=.*=>",
            "java": r"^\+.*(?:public|private|protected)\s+\w+\s+(\w+)\s*\(",
            "go": r"^\+.*func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(",
        }
        pattern = pattern_map.get(language, r"^\+.*def\s+(\w+)\s*\(")
        for m in re.finditer(pattern, diff_text, re.M):
            # Some patterns have multiple groups
            name = next((g for g in m.groups() if g), None)
            if name:
                changed.add(name)
        return sorted(changed)

    def summarize_changes(self, diff_text: str) -> dict[str, Any]:
        """
        Generate a high-level summary of the diff.

        Args:
            diff_text: Raw unified diff text.

        Returns:
            Summary dict with files_changed, lines_added, lines_removed, key_changes.
        """
        files = self.parse_diff(diff_text)
        total_added = sum(f["added_lines"] for f in files)
        total_removed = sum(f["removed_lines"] for f in files)

        added_files = [f["filename"] for f in files if f["status"] == "added"]
        deleted_files = [f["filename"] for f in files if f["status"] == "deleted"]
        modified_files = [f["filename"] for f in files if f["status"] == "modified"]
        renamed_files = [f["filename"] for f in files if f["status"] == "renamed"]

        return {
            "files_changed": len(files),
            "lines_added": total_added,
            "lines_removed": total_removed,
            "added_files": added_files,
            "deleted_files": deleted_files,
            "modified_files": modified_files,
            "renamed_files": renamed_files,
            "net_change": total_added - total_removed,
        }

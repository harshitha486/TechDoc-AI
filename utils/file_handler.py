"""File upload handler with language detection."""

from __future__ import annotations

from typing import Any


EXTENSION_TO_LANGUAGE: dict[str, str] = {
    ".py": "python",
    ".pyw": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".kt": "kotlin",
    ".swift": "swift",
    ".sh": "bash",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".md": "markdown",
    ".sql": "sql",
    ".r": "r",
    ".scala": "scala",
}

SUPPORTED_EXTENSIONS = set(EXTENSION_TO_LANGUAGE.keys())


class FileHandler:
    """Handles file uploads and multi-file processing."""

    def detect_language_from_extension(self, filename: str) -> str:
        """
        Detect programming language from file extension.

        Args:
            filename: Filename with extension.

        Returns:
            Language identifier string, or "unknown" if not recognised.
        """
        import os

        _, ext = os.path.splitext(filename.lower())
        return EXTENSION_TO_LANGUAGE.get(ext, "unknown")

    def process_upload(self, uploaded_file: Any) -> dict[str, str]:
        """
        Process a Streamlit UploadedFile object.

        Args:
            uploaded_file: Streamlit UploadedFile instance.

        Returns:
            Dict with keys: code (str), language (str), filename (str).
        """
        filename = uploaded_file.name
        try:
            code = uploaded_file.read().decode("utf-8", errors="replace")
        except Exception:
            code = ""

        language = self.detect_language_from_extension(filename)
        return {"code": code, "language": language, "filename": filename}

    def read_multiple_files(self, uploaded_files: list[Any]) -> list[dict[str, str]]:
        """
        Process multiple uploaded files.

        Args:
            uploaded_files: List of Streamlit UploadedFile instances.

        Returns:
            List of dicts with code, language, and filename for each file.
        """
        return [self.process_upload(f) for f in uploaded_files]

    def combine_files(self, file_results: list[dict[str, str]]) -> str:
        """
        Combine multiple file contents into a single string for processing.

        Args:
            file_results: List of dicts from read_multiple_files.

        Returns:
            Combined code string with file headers.
        """
        parts: list[str] = []
        for fr in file_results:
            parts.append(f"# === FILE: {fr['filename']} ===\n{fr['code']}\n")
        return "\n".join(parts)

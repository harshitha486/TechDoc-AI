"""
Multi-language code parser.
Uses Python AST for Python code; regex-based parsing for other languages.
"""

from __future__ import annotations

import ast
import re
from typing import Any


class CodeParser:
    """Parses source code across multiple languages to extract structure."""

    EXTENSION_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".c": "c",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".cs": "csharp",
        ".kt": "kotlin",
        ".swift": "swift",
    }

    # ------------------------------------------------------------------
    # Language detection
    # ------------------------------------------------------------------

    def detect_language(self, code: str, filename: str = "") -> str:
        """
        Detect the programming language of the code.

        Args:
            code: Source code text.
            filename: Optional filename with extension.

        Returns:
            Language identifier string (e.g., "python", "javascript").
        """
        if filename:
            for ext, lang in self.EXTENSION_MAP.items():
                if filename.lower().endswith(ext):
                    return lang

        # Heuristic detection
        if re.search(r"^\s*def\s+\w+\s*\(|^\s*class\s+\w+\s*[:(]|import\s+\w+|from\s+\w+\s+import", code, re.M):
            return "python"
        if re.search(r"function\s+\w+\s*\(|const\s+\w+\s*=|=>\s*{|require\(|import\s+.*from", code, re.M):
            if re.search(r":\s*(string|number|boolean|any|void|interface\s+\w+)", code):
                return "typescript"
            return "javascript"
        if re.search(r"public\s+class\s+\w+|System\.out\.println|@Override", code):
            return "java"
        if re.search(r"#include\s*<|std::|cout\s*<<|int\s+main\s*\(", code):
            return "cpp"
        if re.search(r"^package\s+\w+|^import\s+\"|\bfunc\s+\w+\s*\(", code, re.M):
            return "go"
        if re.search(r"^fn\s+\w+|let\s+mut\s+\w+|impl\s+\w+|use\s+std::", code, re.M):
            return "rust"

        return "unknown"

    # ------------------------------------------------------------------
    # Python parsing (AST-based)
    # ------------------------------------------------------------------

    def parse_python(self, code: str) -> dict[str, Any]:
        """
        Parse Python source code using the AST module.

        Args:
            code: Python source code.

        Returns:
            Dictionary with keys: functions, classes, imports, module_doc.
        """
        result: dict[str, Any] = {
            "language": "python",
            "functions": [],
            "classes": [],
            "imports": [],
            "module_doc": "",
        }

        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            result["parse_error"] = str(exc)
            return result

        result["module_doc"] = ast.get_docstring(tree) or ""

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    result["imports"].append(f"{module}.{alias.name}")

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                result["functions"].append(self._parse_python_function(node))
            elif isinstance(node, ast.ClassDef):
                result["classes"].append(self._parse_python_class(node))

        return result

    def _parse_python_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, Any]:
        args = []
        for arg in node.args.args:
            arg_info: dict[str, Any] = {"name": arg.arg}
            if arg.annotation:
                try:
                    arg_info["type"] = ast.unparse(arg.annotation)
                except Exception:
                    arg_info["type"] = "Any"
            args.append(arg_info)

        return_type = ""
        if node.returns:
            try:
                return_type = ast.unparse(node.returns)
            except Exception:
                return_type = "Any"

        return {
            "name": node.name,
            "args": args,
            "return_type": return_type,
            "docstring": ast.get_docstring(node) or "",
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "decorators": [ast.unparse(d) for d in node.decorator_list],
            "line": node.lineno,
        }

    def _parse_python_class(self, node: ast.ClassDef) -> dict[str, Any]:
        methods = []
        for item in ast.iter_child_nodes(node):
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._parse_python_function(item))

        return {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "methods": methods,
            "bases": [ast.unparse(b) for b in node.bases],
            "decorators": [ast.unparse(d) for d in node.decorator_list],
            "line": node.lineno,
        }

    # ------------------------------------------------------------------
    # JavaScript / TypeScript parsing (regex)
    # ------------------------------------------------------------------

    def parse_javascript(self, code: str) -> dict[str, Any]:
        """
        Parse JavaScript/TypeScript source code using regex.

        Args:
            code: JavaScript or TypeScript source code.

        Returns:
            Dictionary with keys: functions, classes, exports, imports.
        """
        result: dict[str, Any] = {"language": "javascript", "functions": [], "classes": [], "exports": [], "imports": []}

        # Named functions
        for m in re.finditer(r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)", code):
            result["functions"].append({"name": m.group(1), "args": m.group(2), "line": code[: m.start()].count("\n") + 1})

        # Arrow functions assigned to const/let
        for m in re.finditer(r"(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>", code):
            result["functions"].append({"name": m.group(1), "args": m.group(2), "line": code[: m.start()].count("\n") + 1})

        # Classes
        for m in re.finditer(r"class\s+(\w+)(?:\s+extends\s+(\w+))?\s*{", code):
            result["classes"].append(
                {"name": m.group(1), "extends": m.group(2) or "", "line": code[: m.start()].count("\n") + 1}
            )

        # Exports
        for m in re.finditer(r"export\s+(?:default\s+)?(\w+)", code):
            result["exports"].append(m.group(1))

        # Imports
        for m in re.finditer(r"import\s+.*?from\s+['\"]([^'\"]+)['\"]", code):
            result["imports"].append(m.group(1))

        return result

    # ------------------------------------------------------------------
    # Generic regex parser (Java, Go, Rust, etc.)
    # ------------------------------------------------------------------

    def parse_generic(self, code: str, language: str) -> dict[str, Any]:
        """
        Generic regex-based parser for languages without dedicated parsers.

        Args:
            code: Source code.
            language: Programming language identifier.

        Returns:
            Dictionary with extracted code structure.
        """
        result: dict[str, Any] = {"language": language, "functions": [], "classes": []}

        if language == "java":
            for m in re.finditer(r"(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)", code):
                result["functions"].append({"name": m.group(1), "args": m.group(2)})
            for m in re.finditer(r"(?:public|abstract|final|\s)*class\s+(\w+)", code):
                result["classes"].append({"name": m.group(1)})

        elif language == "go":
            for m in re.finditer(r"func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(([^)]*)\)", code):
                result["functions"].append({"name": m.group(1), "args": m.group(2)})
            for m in re.finditer(r"type\s+(\w+)\s+struct", code):
                result["classes"].append({"name": m.group(1)})

        elif language in ("cpp", "c"):
            for m in re.finditer(r"(?:[\w:*&<>]+\s+)+(\w+)\s*\(([^)]*)\)\s*(?:const\s*)?{", code):
                if m.group(1) not in ("if", "while", "for", "switch"):
                    result["functions"].append({"name": m.group(1), "args": m.group(2)})
            for m in re.finditer(r"class\s+(\w+)", code):
                result["classes"].append({"name": m.group(1)})

        elif language == "rust":
            for m in re.finditer(r"(?:pub\s+)?fn\s+(\w+)\s*(?:<[^>]*>)?\s*\(([^)]*)\)", code):
                result["functions"].append({"name": m.group(1), "args": m.group(2)})
            for m in re.finditer(r"(?:pub\s+)?struct\s+(\w+)", code):
                result["classes"].append({"name": m.group(1)})

        return result

    # ------------------------------------------------------------------
    # API route extraction
    # ------------------------------------------------------------------

    def extract_api_routes(self, code: str, language: str = "python") -> list[dict[str, Any]]:
        """
        Extract REST API route definitions from framework-specific code.

        Args:
            code: Source code containing route definitions.
            language: Programming language of the code.

        Returns:
            List of route dicts with keys: method, path, function, line.
        """
        routes: list[dict[str, Any]] = []

        # Flask / Python
        for m in re.finditer(
            r"@(?:app|router|blueprint|bp)\.(get|post|put|delete|patch|options)\s*\(\s*['\"]([^'\"]+)['\"]",
            code,
            re.I,
        ):
            routes.append({"method": m.group(1).upper(), "path": m.group(2), "framework": "flask"})

        # FastAPI
        for m in re.finditer(
            r"@(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]",
            code,
            re.I,
        ):
            routes.append({"method": m.group(1).upper(), "path": m.group(2), "framework": "fastapi"})

        # Flask @app.route
        for m in re.finditer(
            r"@(?:app|blueprint|bp)\.route\s*\(\s*['\"]([^'\"]+)['\"].*?methods\s*=\s*\[([^\]]+)\]",
            code,
            re.I | re.S,
        ):
            methods_str = m.group(2)
            methods = [x.strip().strip("'\"") for x in methods_str.split(",")]
            for method in methods:
                routes.append({"method": method.upper(), "path": m.group(1), "framework": "flask"})

        # Express.js
        for m in re.finditer(
            r"(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*['\"`]([^'\"` ]+)['\"`]",
            code,
            re.I,
        ):
            routes.append({"method": m.group(1).upper(), "path": m.group(2), "framework": "express"})

        # Django urls
        for m in re.finditer(r"path\s*\(\s*['\"]([^'\"]+)['\"]", code):
            routes.append({"method": "GET/POST", "path": m.group(1), "framework": "django"})

        return routes

    # ------------------------------------------------------------------
    # Main entry
    # ------------------------------------------------------------------

    def parse(self, code: str, filename: str = "") -> dict[str, Any]:
        """
        Parse source code and return its structure.

        Args:
            code: Source code to parse.
            filename: Optional filename for language detection.

        Returns:
            Parsed structure dictionary.
        """
        language = self.detect_language(code, filename)
        if language == "python":
            return self.parse_python(code)
        elif language in ("javascript", "typescript"):
            result = self.parse_javascript(code)
            result["language"] = language
            return result
        else:
            return self.parse_generic(code, language)

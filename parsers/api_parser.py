"""API spec and endpoint extractor."""

from __future__ import annotations

import re
from typing import Any


class APIParser:
    """Extracts API endpoint information from code and OpenAPI specs."""

    def parse_openapi(self, spec: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Parse an OpenAPI/Swagger specification dict into a list of endpoints.

        Args:
            spec: Parsed OpenAPI JSON/YAML as a Python dict.

        Returns:
            List of endpoint dicts with method, path, summary, params, etc.
        """
        endpoints: list[dict[str, Any]] = []
        paths = spec.get("paths", {})
        for path, path_item in paths.items():
            for method in ("get", "post", "put", "delete", "patch", "options", "head"):
                op = path_item.get(method)
                if not op:
                    continue
                endpoints.append(
                    {
                        "method": method.upper(),
                        "path": path,
                        "summary": op.get("summary", ""),
                        "description": op.get("description", ""),
                        "tags": op.get("tags", []),
                        "parameters": op.get("parameters", []),
                        "request_body": op.get("requestBody"),
                        "responses": op.get("responses", {}),
                        "security": op.get("security", []),
                        "operation_id": op.get("operationId", ""),
                    }
                )
        return endpoints

    def extract_flask_routes(self, code: str) -> list[dict[str, Any]]:
        """
        Extract Flask route definitions from Python source code.

        Args:
            code: Python source code with Flask route decorators.

        Returns:
            List of route dicts.
        """
        routes: list[dict[str, Any]] = []

        # @app.route('/path', methods=['GET', 'POST'])
        for m in re.finditer(
            r"@(?:\w+)\.route\s*\(\s*['\"]([^'\"]+)['\"](?:.*?methods\s*=\s*\[([^\]]+)\])?",
            code,
            re.S,
        ):
            methods_str = m.group(2) or "'GET'"
            methods = [x.strip().strip("'\"") for x in methods_str.split(",")]
            # Find the function immediately after
            func_match = re.search(r"def\s+(\w+)\s*\(", code[m.end() :])
            func_name = func_match.group(1) if func_match else ""
            for method in methods:
                routes.append({"method": method.upper(), "path": m.group(1), "handler": func_name, "framework": "flask"})

        # @app.get('/path')  style
        for m in re.finditer(
            r"@(?:\w+)\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]",
            code,
            re.I,
        ):
            func_match = re.search(r"def\s+(\w+)\s*\(", code[m.end() :])
            func_name = func_match.group(1) if func_match else ""
            routes.append(
                {"method": m.group(1).upper(), "path": m.group(2), "handler": func_name, "framework": "flask"}
            )

        return routes

    def extract_fastapi_routes(self, code: str) -> list[dict[str, Any]]:
        """
        Extract FastAPI route definitions from Python source code.

        Args:
            code: Python source code with FastAPI route decorators.

        Returns:
            List of route dicts.
        """
        routes: list[dict[str, Any]] = []
        for m in re.finditer(
            r"@(?:app|router|APIRouter\(\))\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]",
            code,
            re.I,
        ):
            func_match = re.search(r"(?:async\s+)?def\s+(\w+)\s*\(", code[m.end() :])
            func_name = func_match.group(1) if func_match else ""
            routes.append(
                {"method": m.group(1).upper(), "path": m.group(2), "handler": func_name, "framework": "fastapi"}
            )
        return routes

    def extract_express_routes(self, code: str) -> list[dict[str, Any]]:
        """
        Extract Express.js route definitions from JavaScript/TypeScript code.

        Args:
            code: JavaScript or TypeScript source code with Express routes.

        Returns:
            List of route dicts.
        """
        routes: list[dict[str, Any]] = []
        for m in re.finditer(
            r"(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*['\"`]([^'\"` ]+)['\"`]",
            code,
            re.I,
        ):
            routes.append({"method": m.group(1).upper(), "path": m.group(2), "framework": "express"})
        return routes

    def extract_all_routes(self, code: str, language: str = "python") -> list[dict[str, Any]]:
        """
        Extract all API routes from code regardless of framework.

        Args:
            code: Source code.
            language: Programming language.

        Returns:
            Combined list of route dicts from all detected frameworks.
        """
        routes: list[dict[str, Any]] = []
        if language == "python":
            routes.extend(self.extract_flask_routes(code))
            routes.extend(self.extract_fastapi_routes(code))
        elif language in ("javascript", "typescript"):
            routes.extend(self.extract_express_routes(code))

        # Deduplicate
        seen: set[tuple[str, str]] = set()
        unique: list[dict[str, Any]] = []
        for r in routes:
            key = (r["method"], r["path"])
            if key not in seen:
                seen.add(key)
                unique.append(r)
        return unique

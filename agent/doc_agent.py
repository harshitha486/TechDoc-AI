"""
Core AI Agent for Technical Documentation Generation.
Supports multiple providers: Google Gemini (free), Groq (free), Anthropic (paid).
"""

from __future__ import annotations

import os
from typing import Any

from .prompts import (
    API_DOC_PROMPT,
    ARCHITECTURE_PROMPT,
    CHANGELOG_PROMPT,
    DOCSTRING_PROMPT,
    README_PROMPT,
    SYSTEM_PROMPT,
    UPDATE_DOCS_PROMPT,
)


class DocAgent:
    """
    AI-powered documentation generation agent.

    Supports:
    - Google Gemini (free) — gemini-1.5-flash
    - Groq (free)          — llama-3.3-70b-versatile
    - Anthropic (paid)     — claude-sonnet-4-6
    """

    MODELS = {
        "gemini": "gemini-2.0-flash",
        "groq":   "llama-3.3-70b-versatile",
        "anthropic": "claude-sonnet-4-6",
    }

    def __init__(self, api_key: str, provider: str = "gemini") -> None:
        """
        Initialize the agent.

        Args:
            api_key: API key for the chosen provider.
            provider: One of "gemini", "groq", "anthropic".
        """
        if not api_key or not api_key.strip():
            raise ValueError("API key is required.")
        self.api_key = api_key.strip()
        self.provider = provider.lower()
        self._last_usage: dict[str, int] = {}
        self._client: Any = None
        self._init_client()

    # ------------------------------------------------------------------
    # Client initialisation
    # ------------------------------------------------------------------

    def _init_client(self) -> None:
        if self.provider == "gemini":
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except ImportError:
                raise ImportError("Run: pip install google-genai")

        elif self.provider == "groq":
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
            except ImportError:
                raise ImportError("Run: pip install groq")

        elif self.provider == "anthropic":
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("Run: pip install anthropic")
        else:
            raise ValueError(f"Unknown provider: {self.provider!r}. Choose gemini, groq, or anthropic.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_docs(
        self,
        code: str,
        doc_type: str = "docstrings",
        language: str = "auto",
        style: str = "google",
        context: str = "",
        filename: str = "",
    ) -> str:
        prompt_map = {
            "docstrings":   DOCSTRING_PROMPT,
            "readme":       README_PROMPT,
            "api_docs":     API_DOC_PROMPT,
            "architecture": ARCHITECTURE_PROMPT,
        }
        task_prompt = prompt_map.get(doc_type, DOCSTRING_PROMPT)
        user_content = self._build_user_message(task_prompt, code, language, style, context, filename)
        return self._call(user_content)

    def update_docs(self, old_code: str, new_code: str, existing_docs: str, doc_type: str = "docstrings") -> str:
        user_content = f"""{UPDATE_DOCS_PROMPT}

## OLD CODE
```
{old_code}
```

## NEW CODE
```
{new_code}
```

## EXISTING DOCUMENTATION
{existing_docs}

Doc type: {doc_type}
Please update the documentation now.
"""
        return self._call(user_content)

    def analyze_pr(self, pr_diff: str, pr_title: str = "", pr_description: str = "", version: str = "Unreleased") -> str:
        user_content = f"""{CHANGELOG_PROMPT}

## Pull Request Information
**Title:** {pr_title or 'N/A'}
**Version:** {version}

**Description:**
{pr_description or 'No description provided.'}

**Diff:**
```diff
{pr_diff[:6000]}
```

Generate the changelog entry now.
"""
        return self._call(user_content)

    def generate_from_deployment(self, diff: str, service_name: str, old_version: str, new_version: str, extra_notes: str = "") -> str:
        user_content = f"""{CHANGELOG_PROMPT}

## Deployment Information
**Service:** {service_name}
**Version:** {old_version} → {new_version}

**Changes / Diff:**
```
{diff[:6000]}
```

**Additional Notes:** {extra_notes or 'None'}

Generate professional release notes now.
"""
        return self._call(user_content)

    def generate_api_docs(self, code: str, service_name: str = "API", base_url: str = "https://api.example.com") -> str:
        user_content = f"""{API_DOC_PROMPT}

**Service Name:** {service_name}
**Base URL:** {base_url}

**Source Code:**
```
{code}
```

Generate the complete API reference documentation now.
"""
        return self._call(user_content)

    @property
    def last_usage(self) -> dict[str, int]:
        return self._last_usage

    # ------------------------------------------------------------------
    # Private: build prompt
    # ------------------------------------------------------------------

    def _build_user_message(self, task_prompt: str, code: str, language: str, style: str, context: str, filename: str) -> str:
        parts = [task_prompt, "\n---\n"]
        if language and language != "auto":
            parts.append(f"**Language:** {language}\n")
        if filename:
            parts.append(f"**Filename:** {filename}\n")
        if style:
            parts.append(f"**Documentation Style:** {style}\n")
        if context:
            parts.append(f"**Context:** {context}\n")
        parts.append(f"\n**Source Code:**\n```\n{code}\n```\n\nGenerate the documentation now.")
        return "".join(parts)

    # ------------------------------------------------------------------
    # Private: unified call dispatcher
    # ------------------------------------------------------------------

    def _call(self, user_content: str) -> str:
        if self.provider == "gemini":
            return self._call_gemini(user_content)
        elif self.provider == "groq":
            return self._call_groq(user_content)
        elif self.provider == "anthropic":
            return self._call_anthropic(user_content)
        raise ValueError(f"Unknown provider: {self.provider}")

    def _call_gemini(self, user_content: str) -> str:
        import time
        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_content}"
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self._client.models.generate_content(
                    model=self.MODELS["gemini"],
                    contents=full_prompt,
                )
                self._last_usage = {}
                return response.text
            except Exception as exc:
                err = str(exc)
                if "API_KEY_INVALID" in err or "api_key_invalid" in err.lower():
                    raise ValueError("Invalid Gemini API key. Get a free one at aistudio.google.com")
                if "quota" in err.lower() or "429" in err or "rate" in err.lower():
                    if attempt < max_retries - 1:
                        wait = 25 * (attempt + 1)   # 25s, 50s
                        time.sleep(wait)
                        continue
                    raise RuntimeError(
                        "Gemini rate limit hit. You've made too many requests recently. "
                        "Wait 1–2 minutes and try again — or switch to **Groq** (free, no limit issues) in the sidebar."
                    )
                raise RuntimeError(f"Gemini error: {exc}") from exc
        raise RuntimeError("Gemini: max retries exceeded.")

    def _call_groq(self, user_content: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.MODELS["groq"],
                max_tokens=8192,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_content},
                ],
            )
            usage = response.usage
            if usage:
                self._last_usage = {
                    "input_tokens":  usage.prompt_tokens,
                    "output_tokens": usage.completion_tokens,
                }
            return response.choices[0].message.content
        except Exception as exc:
            err = str(exc)
            if "401" in err or "invalid" in err.lower():
                raise ValueError("Invalid Groq API key. Get one free at console.groq.com")
            if "429" in err or "rate" in err.lower():
                raise RuntimeError("Groq rate limit hit. Wait a moment and retry (free tier: 30 req/min).")
            raise RuntimeError(f"Groq error: {exc}") from exc

    def _call_anthropic(self, user_content: str) -> str:
        try:
            import anthropic
            response = self._client.messages.create(
                model=self.MODELS["anthropic"],
                max_tokens=8192,
                system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": user_content}],
            )
            self._last_usage = {
                "input_tokens":  response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "cache_read":    getattr(response.usage, "cache_read_input_tokens", 0),
            }
            return response.content[0].text
        except anthropic.AuthenticationError:
            raise ValueError("Invalid Anthropic API key.")
        except anthropic.RateLimitError:
            raise RuntimeError("Anthropic rate limit. Please wait and retry.")
        except Exception as exc:
            raise RuntimeError(f"Anthropic error: {exc}") from exc

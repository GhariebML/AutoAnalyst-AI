"""Helpers for dealing with JSON strings, especially LLM outputs.

Phase 1 placeholder – only safe parsing utilities, no real LLM logic.
"""

import json
import re
from typing import Any


def strip_markdown_fences(text: str) -> str:
    """Remove triple‑backtick fences that many LLMs wrap JSON inside.

    Example
    -------
    >>> strip_markdown_fences("```json\\n{}\\n```")
    '{}'
    """
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return text.strip()


def safe_json_loads(text: str) -> Any:
    """Parse *text* as JSON, repairing common LLM formatting issues first."""
    cleaned = text.strip()
    
    # Remove markdown code block fences if present
    if cleaned.startswith("```"):
        first_newline = cleaned.find("\n")
        if first_newline != -1:
            cleaned = cleaned[first_newline:].strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
            
    # Escape raw control characters inside string literals
    result_chars = []
    in_string = False
    escape = False
    for char in cleaned:
        if char == '"' and not escape:
            in_string = not in_string
            result_chars.append(char)
        elif char == '\\' and in_string:
            escape = not escape
            result_chars.append(char)
        else:
            if escape:
                escape = False
            if in_string:
                if char == '\n':
                    result_chars.append('\\n')
                elif char == '\r':
                    result_chars.append('\\r')
                elif char == '\t':
                    result_chars.append('\\t')
                else:
                    result_chars.append(char)
            else:
                result_chars.append(char)
                
    cleaned = "".join(result_chars)
    
    # Remove trailing commas before closing braces/brackets
    cleaned = re.sub(r',(\s*[\]\}])', r'\1', cleaned)
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}\nCleaned JSON snippet: {cleaned[:400]}") from exc


def pretty_json(data: Any, **kwargs: Any) -> str:
    """Return a pretty‑printed JSON string for *data*."""
    return json.dumps(data, indent=2, ensure_ascii=False, **kwargs)

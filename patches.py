"""
Patch layer for automatic correction of parsing from LLM analysis.

Provides getters for unit_mapping, cleanup_rules, and system_prompt_append
from the patches/ directory, and apply_patches_from_analysis to merge
analysis-reported patches into patches/.
"""
import json
from pathlib import Path
from typing import Dict, List, Optional

from config_section import PATCHES_DIR

_UNIT_MAPPING_FILE = "unit_mapping.json"
_CLEANUP_RULES_FILE = "cleanup_rules.json"
_SYSTEM_PROMPT_APPEND_FILE = "system_prompt_append.txt"
_SEPARATOR = "\n\n---\n\n"


def get_patch_unit_mapping() -> dict:
    """
    Load unit mapping overlay from patches/unit_mapping.json.

    Returns:
        Dict mapping variant strings to standard units. Empty dict if file missing.
    """
    path = PATCHES_DIR / _UNIT_MAPPING_FILE
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def get_cleanup_rules() -> list:
    """
    Load cleanup rules from patches/cleanup_rules.json.

    Returns:
        List of dicts with 'pattern', 'replacement', and optional 'regex'.
        Empty list if file missing.
    """
    path = PATCHES_DIR / _CLEANUP_RULES_FILE
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return []
        return [r for r in data if isinstance(r, dict) and "pattern" in r and "replacement" in r]
    except (json.JSONDecodeError, OSError):
        return []


def get_system_prompt_append() -> str:
    """
    Load system prompt append text from patches/system_prompt_append.txt.

    Returns:
        Plain text to append to the parsing system prompt. Empty string if file missing.
    """
    path = PATCHES_DIR / _SYSTEM_PROMPT_APPEND_FILE
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def apply_patches_to_disk(
    unit_mapping: Optional[Dict[str, str]] = None,
    cleanup_rules: Optional[List[dict]] = None,
    system_prompt_append: Optional[str] = None,
) -> None:
    """
    Merge patch content into the patches/ directory.

    - unit_mapping: dict-merge into patches/unit_mapping.json
    - cleanup_rules: extend patches/cleanup_rules.json
    - system_prompt_append: append to patches/system_prompt_append.txt with separator

    Args:
        unit_mapping: Optional overlay {variant: standard}
        cleanup_rules: Optional list of {pattern, replacement, regex?}
        system_prompt_append: Optional text to append to system prompt
    """
    PATCHES_DIR.mkdir(parents=True, exist_ok=True)

    if unit_mapping is not None and isinstance(unit_mapping, dict):
        path = PATCHES_DIR / _UNIT_MAPPING_FILE
        existing = {}
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                existing = data if isinstance(data, dict) else {}
            except (json.JSONDecodeError, OSError):
                pass
        merged = {**existing, **unit_mapping}
        path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

    if cleanup_rules is not None and isinstance(cleanup_rules, list):
        path = PATCHES_DIR / _CLEANUP_RULES_FILE
        existing: list = []
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                existing = data if isinstance(data, list) else []
            except (json.JSONDecodeError, OSError):
                pass
        valid = [r for r in cleanup_rules if isinstance(r, dict) and "pattern" in r and "replacement" in r]
        extended = existing + valid
        path.write_text(json.dumps(extended, ensure_ascii=False, indent=2), encoding="utf-8")

    if system_prompt_append is not None and isinstance(system_prompt_append, str) and system_prompt_append.strip():
        path = PATCHES_DIR / _SYSTEM_PROMPT_APPEND_FILE
        existing = ""
        if path.exists():
            try:
                existing = path.read_text(encoding="utf-8").strip()
            except OSError:
                pass
        new_content = (existing + _SEPARATOR + system_prompt_append.strip()) if existing else system_prompt_append.strip()
        path.write_text(new_content, encoding="utf-8")


def apply_patches_from_analysis(analysis_report: dict) -> None:
    """
    Extract 'patches' from an analysis report and merge into patches/ via apply_patches_to_disk.

    Ignores missing or malformed 'patches'. Supported keys:
    - unit_mapping: dict
    - cleanup_rules: list
    - system_prompt_append: str

    Args:
        analysis_report: Dict from analysis LLM (may contain 'patches').
    """
    p = analysis_report.get("patches") or {}
    if not isinstance(p, dict):
        return

    um = p.get("unit_mapping")
    if isinstance(um, dict):
        apply_patches_to_disk(unit_mapping=um)

    cr = p.get("cleanup_rules")
    if isinstance(cr, list):
        apply_patches_to_disk(cleanup_rules=cr)

    spa = p.get("system_prompt_append")
    if isinstance(spa, str) and spa.strip():
        apply_patches_to_disk(system_prompt_append=spa)

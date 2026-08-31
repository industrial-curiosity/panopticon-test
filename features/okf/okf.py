"""Deterministic constrained OKF v0.1 Markdown validation."""

import re
from pathlib import Path


FRONTMATTER_KEYS = ("type", "name", "status", "owner", "updated")
FRONTMATTER_START = "---"
FRONTMATTER_END = "---"
DATE_HEADING = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
KEY_VALUE = re.compile(r"^([a-z][a-z0-9_-]*):(?:[ \t]+(.*))?$")


def _frontmatter_problems(path, text):
    lines = text.splitlines()
    if not lines or lines[0] != FRONTMATTER_START:
        return [f"{path}: frontmatter must start with ---"]
    try:
        end = lines.index(FRONTMATTER_END, 1)
    except ValueError:
        return [f"{path}: frontmatter closing --- is missing"]
    if end == 1:
        return [f"{path}: frontmatter must contain type: <non-empty value>"]
    values = {}
    problems = []
    for line in lines[1:end]:
        match = KEY_VALUE.fullmatch(line)
        if not match:
            problems.append(f"{path}: frontmatter line is not constrained key: value syntax: {line!r}")
            continue
        key, value = match.groups()
        if key not in FRONTMATTER_KEYS:
            problems.append(f"{path}: frontmatter key {key!r} is not allowed")
        if key in values:
            problems.append(f"{path}: frontmatter key {key!r} is duplicated")
        values[key] = (value or "").strip()
    if not values.get("type"):
        problems.append(f"{path}: frontmatter type must be non-empty")
    return problems


def validate_document(path):
    """Validate one non-reserved concept document and return diagnostics."""
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"{path}: cannot read Markdown: {exc}"]
    return _frontmatter_problems(path, text)


def _validate_reserved(path, text):
    if path.name == "index.md":
        if not re.search(r"^\s*- \[[^]]+\]\([^)]*\.md(?:#[^)]*)?\)", text, re.MULTILINE):
            return [f"{path}: reserved index.md must contain progressive-disclosure Markdown links"]
        return []
    if path.name == "log.md":
        if not DATE_HEADING.search(text):
            return [f"{path}: reserved log.md must contain a date-grouped ## YYYY-MM-DD heading"]
    return []


def validate_bundle(root="docs"):
    """Validate all Markdown in an OKF bundle, excluding test-only fixtures."""
    root = Path(root)
    if not root.is_dir():
        return [f"{root}: OKF documentation root is missing"]
    problems = []
    for path in sorted(root.rglob("*.md")):
        if "test-fixtures" in path.parts or "fixtures" in path.parts:
            continue
        relative = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        if path.name in {"index.md", "log.md"}:
            problems.extend(_validate_reserved(relative, text))
        else:
            problems.extend(_frontmatter_problems(relative, text))
    return problems

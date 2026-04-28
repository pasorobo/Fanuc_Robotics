#!/usr/bin/env python3
"""Documentation handbook quality gate.

Verifies fenced-block balance, internal link resolution, SVG references,
and ADR section headings. Run before every docs commit.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
ADR_DIR = DOCS_ROOT / "decisions"

LINK_RE = re.compile(r"(?<!\!)\[[^\]]+\]\(([^)]+)\)")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^(`{3,})(.*)$")
ADR_REQUIRED_SECTIONS = ("## Status", "## Context", "## Decision", "## Consequences")


EXCLUDED_DIRS = (DOCS_ROOT / "superpowers",)


def iter_markdown_files() -> List[Path]:
    paths = sorted(DOCS_ROOT.rglob("*.md"))
    paths.append(REPO_ROOT / "README.md")
    return [
        p for p in paths
        if p.exists() and not any(excluded in p.parents for excluded in EXCLUDED_DIRS)
    ]


def check_fences(path: Path) -> List[str]:
    errors: List[str] = []
    stack: List[Tuple[int, int]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = FENCE_RE.match(line.rstrip("\n"))
        if not match:
            continue
        flen = len(match.group(1))
        info = match.group(2).strip()
        if stack:
            top_line, top_len = stack[-1]
            if info == "" and flen >= top_len:
                stack.pop()
        else:
            stack.append((lineno, flen))
    for opened_line, length in stack:
        errors.append(f"{path}:{opened_line}: unclosed fence (length {length})")
    return errors


def check_internal_link(path: Path, target: str) -> List[str]:
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return []
    bare = target.split("#", 1)[0].split("?", 1)[0]
    if not bare:
        return []
    resolved = (path.parent / bare).resolve()
    if not resolved.exists():
        return [f"{path}: link target does not exist: {target}"]
    return []


def strip_fenced_blocks(text: str) -> str:
    """Remove content inside fenced code blocks so embedded snippets do not
    contribute false positives to link/image checks. Fence opening/closing
    follows the same rule used in check_fences (CommonMark)."""
    lines = text.splitlines()
    out: List[str] = []
    stack: List[int] = []
    for line in lines:
        match = FENCE_RE.match(line)
        if match:
            flen = len(match.group(1))
            info = match.group(2).strip()
            if stack:
                if info == "" and flen >= stack[-1]:
                    stack.pop()
                    out.append("")
                    continue
            else:
                stack.append(flen)
                out.append("")
                continue
        if stack:
            out.append("")
        else:
            out.append(line)
    return "\n".join(out)


def check_links_and_images(path: Path) -> List[str]:
    errors: List[str] = []
    text = strip_fenced_blocks(path.read_text(encoding="utf-8"))
    for match in LINK_RE.finditer(text):
        errors.extend(check_internal_link(path, match.group(1)))
    for match in IMAGE_RE.finditer(text):
        errors.extend(check_internal_link(path, match.group(1)))
    return errors


def check_adr_sections(path: Path) -> List[str]:
    if path.parent != ADR_DIR or not path.name[0].isdigit():
        return []
    text = path.read_text(encoding="utf-8")
    missing = [section for section in ADR_REQUIRED_SECTIONS if section not in text]
    return [f"{path}: ADR missing section: {section}" for section in missing]


def main() -> int:
    failures: List[str] = []
    files = iter_markdown_files()
    for path in files:
        failures.extend(check_fences(path))
        failures.extend(check_links_and_images(path))
        failures.extend(check_adr_sections(path))

    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        print(f"\n{len(failures)} documentation issue(s) found", file=sys.stderr)
        return 1

    print(f"check_docs ok ({len(files)} markdown files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

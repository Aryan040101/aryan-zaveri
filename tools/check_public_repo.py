#!/usr/bin/env python3
"""Public repository safety and Markdown link checks."""

from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {
    ".md",
    ".py",
    ".cpp",
    ".hpp",
    ".json",
    ".yml",
    ".yaml",
    ".txt",
    ".gitignore",
}

FORBIDDEN_CONTENT = [
    re.compile(r"career[-_ ]?os", re.IGNORECASE),
    re.compile("/home/" + "aryan", re.IGNORECASE),
    re.compile("/home/" + "greyoak", re.IGNORECASE),
    re.compile(r"\b100\.(?:\d{1,3}\.){2}\d{1,3}\b"),
    re.compile("BEGIN " + r"[A-Z ]*" + "PRIVATE " + "KEY"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"(?:password|api[_-]?key|secret|token)\s*[:=]\s*['\"]?[^'\"\s]+", re.IGNORECASE),
]

FORBIDDEN_FILENAMES = {
    ".env",
    ".env.local",
    ".env.production",
}


def tracked_text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_dir():
            continue
        if path.name in FORBIDDEN_FILENAMES:
            raise AssertionError(f"forbidden file present: {path.relative_to(ROOT)}")
        if path.suffix in TEXT_EXTENSIONS or path.name == ".gitignore":
            files.append(path)
    return files


def check_sensitive_content() -> None:
    failures: list[str] = []
    for path in tracked_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in FORBIDDEN_CONTENT:
            if pattern.search(text):
                failures.append(f"{path.relative_to(ROOT)} matched {pattern.pattern}")
    if failures:
        raise AssertionError("sensitive-content scan failed:\n" + "\n".join(failures))


def check_markdown_links() -> None:
    failures: list[str] = []
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for target in link_re.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean_target = target.split("#", 1)[0]
            if clean_target and not (path.parent / clean_target).exists():
                failures.append(f"{path.relative_to(ROOT)} -> {target}")
    if failures:
        raise AssertionError("markdown link check failed:\n" + "\n".join(failures))


def main() -> int:
    check_sensitive_content()
    check_markdown_links()
    print("public repo checks ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1)

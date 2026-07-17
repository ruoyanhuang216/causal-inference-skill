#!/usr/bin/env python3
"""Catch currency `$` that GitHub will silently render as math.

GitHub renders `$...$` as inline math. A line containing two unescaped
currency amounts — `$250k–$1.25M` — therefore parses as math and eats the
text between them. The fix is always `\\$`, which renders as a literal `$`.

This flags inline `$...$` spans that contain no LaTeX and so are almost
certainly currency. Run from lectures/:  python3 check-math.py
"""
import glob
import re
import sys

# Match currency positively rather than math negatively: bare variables
# like `$i$` carry no LaTeX markup, so "has no backslash" flags everything.
CURRENCY_START = re.compile(r"^\d[\d,]*(\.\d+)?\s*[kKMB]?\b")
LATEX_MARKER = re.compile(r"[\\^_{}]")
PURE_NUMBER = re.compile(r"^\d+$")  # `$2$` is legitimate math


def strip_blocks(src: str) -> str:
    """Blank out anything GitHub won't parse as inline math, preserving
    line numbers and columns: fenced code, $$display$$ math, and inline
    `code` spans (math is not parsed inside code)."""
    blank = lambda m: "\n" * m.group().count("\n")
    src = re.sub(r"```.*?```", blank, src, flags=re.S)
    src = re.sub(r"\$\$.*?\$\$", blank, src, flags=re.S)
    # Inline code: replace with same-width filler so columns stay honest.
    return re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group()), src)


def spans(line: str):
    """Yield (start, content) for each inline $...$ span on the line."""
    positions = [m.start() for m in re.finditer(r"(?<!\\)\$", line)]
    for open_at, close_at in zip(positions[::2], positions[1::2]):
        yield open_at, line[open_at + 1 : close_at]


def check(path):
    problems = []
    for lineno, line in enumerate(strip_blocks(open(path).read()).split("\n"), 1):
        for col, content in spans(line):
            if not CURRENCY_START.match(content.strip()):
                continue  # `$i$`, `$Z=0$`, `$(0, 1]$` — math, not money
            if LATEX_MARKER.search(content):
                continue  # `$2^n$`, `$1/\pi = 5\times$` — math that opens on a digit
            if PURE_NUMBER.match(content.strip()):
                continue  # `$2$`
            problems.append(
                f"{path}:{lineno}:{col}  ${content}$  <- currency? use \\$"
            )
    return problems


if __name__ == "__main__":
    found = [p for f in sorted(glob.glob("**/*.md", recursive=True)) for p in check(f)]
    for p in found:
        print(p)
    print(f"{len(found)} suspected unescaped currency span(s)")
    sys.exit(1 if found else 0)

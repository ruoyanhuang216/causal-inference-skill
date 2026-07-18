#!/usr/bin/env python3
"""Catch the two ways GitHub silently mangles math in these lectures.

1. CURRENCY. GitHub renders `$...$` as inline math, so two bare amounts on
   one line — `$250k–$1.25M` — make it treat `250k–` as math and swallow the
   text between them. Always write `\\$`.

2. MULTI-LINE `$$` BLOCKS. GitHub does not reliably parse these as math. When
   it fails, markdown processes the body instead: `_` pairs become <em> (eating
   the subscripts) and a leading `+ ` becomes a bullet list. The formula is not
   merely unrendered, it is corrupted. Use a ```math fenced block, which is
   immune because fenced code is never markdown-parsed.

Run from lectures/:  python3 check-math.py
"""
import glob
import re
import sys

# Match currency positively rather than math negatively: bare variables
# like `$i$` carry no LaTeX markup, so "has no backslash" flags everything.
CURRENCY_START = re.compile(r"^\d[\d,]*(\.\d+)?\s*[kKMB]?\b")
LATEX_MARKER = re.compile(r"[\\^_{}/=<>()]")  # these mean math: `$1/J$`, `$Z=0$`, `$0 < e(X) < 1$`
PURE_NUMBER = re.compile(r"^\d+$")  # `$2$` is legitimate math


def strip_blocks(src):
    """Blank out anything GitHub won't parse as inline math, preserving
    line numbers and columns: fenced code, $$display$$ math, and inline
    `code` spans (math is not parsed inside code)."""
    blank = lambda m: "\n" * m.group().count("\n")
    src = re.sub(r"```.*?```", blank, src, flags=re.S)
    src = re.sub(r"\$\$.*?\$\$", blank, src, flags=re.S)
    # Inline code: replace with same-width filler so columns stay honest.
    return re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group()), src)


def spans(line):
    """Yield (start, content) for each inline $...$ span on the line."""
    positions = [m.start() for m in re.finditer(r"(?<!\\)\$", line)]
    for open_at, close_at in zip(positions[::2], positions[1::2]):
        yield open_at, line[open_at + 1 : close_at]


def check_currency(path):
    problems = []
    for lineno, line in enumerate(strip_blocks(open(path).read()).split("\n"), 1):
        for col, content in spans(line):
            if not CURRENCY_START.match(content.strip()):
                continue  # `$i$`, `$Z=0$`, `$(0, 1]$` — math, not money
            if LATEX_MARKER.search(content):
                continue  # `$2^n$`, `$1/\pi = 5\times$` — math opening on a digit
            if PURE_NUMBER.match(content.strip()):
                continue  # `$2$`
            problems.append(f"{path}:{lineno}:{col}  ${content}$  <- currency? use \\$")
    return problems


def check_multiline_math(path):
    """Multi-line $$...$$ blocks. GitHub corrupts these; use ```math."""
    src = open(path).read()
    # Ignore fenced code (that's the fix, not the bug).
    src = re.sub(r"```.*?```", lambda m: "\n" * m.group().count("\n"), src, flags=re.S)
    problems = []
    for m in re.finditer(r"\$\$(.*?)\$\$", src, flags=re.S):
        body = m.group(1)
        if "\n" not in body.strip():
            continue  # single-line $$ is fine
        lineno = src[: m.start()].count("\n") + 1
        why = []
        if any(l.lstrip().startswith(("+ ", "- ", "* ")) for l in body.split("\n")):
            why.append("leading +/-/* becomes a bullet list")
        if body.count("_") >= 2:
            why.append("_ pairs become <em>, eating subscripts")
        detail = "; ".join(why) or "not reliably parsed as math"
        problems.append(f"{path}:{lineno}  multi-line $$ block  <- {detail}; use ```math")
    return problems


if __name__ == "__main__":
    files = sorted(glob.glob("**/*.md", recursive=True))
    found = [p for f in files for p in check_currency(f) + check_multiline_math(f)]
    for p in found:
        print(p)
    print(f"{len(found)} problem(s) across {len(files)} file(s)")
    sys.exit(1 if found else 0)

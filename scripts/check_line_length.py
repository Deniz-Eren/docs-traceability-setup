##
# @file     check_line_length.py
# @brief    Validate and fix line lengths and greedy prose packing
#
# @copyright
# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>
# MIT License
#

"""Line-length and greedy prose-packing checker and fixer."""

from __future__ import annotations

import argparse
import ast
import importlib.util
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from editorconfig import EditorConfig, EditorConfigError, load_editorconfig
from file_kinds import (
    KIND_C_CPP,
    KIND_CMAKE,
    KIND_HASH_DATA,
    KIND_MARKDOWN,
    KIND_PYTHON,
    KIND_RST,
    KIND_SHELL,
    FileKind,
    discover_files,
)
from project_config import ConfigError, load_project_config

FALLBACK_NEED_DIRECTIVES = frozenset(
    {
        "sys",
        "swr",
        "arc",
        "icd",
        "comp",
        "ver",
        "adr",
        "bdr",
        "wdr",
        "con",
        "task",
        "roadmap",
    }
)

MD_FENCE_RE = re.compile(r"^([ ]{0,3})(`{3,}|~{3,})(.*)$")
MD_NEED_DIR_RE = re.compile(r"^\{([a-zA-Z0-9_-]+)\}(?:\s|$)")
MD_LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])(\s+)(\S.*)$")
MD_LINK_DEF_RE = re.compile(r"^[ ]*\[[^\]]+\]:\s+\S")
MD_FIELD_RE = re.compile(r"^[ ]*:[a-zA-Z0-9_ -]+:(?:\s|$)")
MD_HR_RE = re.compile(r"^[ ]{0,3}(?:(?:\*\s*){3,}|(?:-\s*){3,}|(?:_\s*){3,})$")
MD_SETEXT_RE = re.compile(r"^[ ]{0,3}(?:={2,}|-{2,})\s*$")
RST_DIRECTIVE_RE = re.compile(r"^([ ]*)\.\.\s+([a-zA-Z0-9_-]+)::(.*)$")
RST_UNDERLINE_RE = re.compile(r"^([=~^\"'`#*\-+_:])\1{2,}$")
RST_LINK_DEF_RE = re.compile(r"^[ ]*\.\.\s+_[^:]+:")
TAG_LINE_RE = re.compile(r"^\w+::(?:\s|$)")
DOXYGEN_CMD_RE = re.compile(r"^[@\\][A-Za-z]")
TOOL_DIRECTIVE_RE = re.compile(
    r"^(?:noqa|type:|pragma:|pylint:|shellcheck|fmt:|isort:)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Finding:
    """A single `<file>:<line>: <message>` checker finding."""

    path: Path
    line: int
    message: str

    def format(self) -> str:
        return f"{self.path.as_posix()}:{self.line}: {self.message}"


@dataclass(frozen=True)
class ProseLine:
    """One packable text line with its prefix, content, suffix, and indent."""

    no: int  # 1-based line number
    prefix: str
    text: str
    suffix: str = ""
    indent: int = 0


@dataclass(frozen=True)
class ProseRun:
    """A maximal run of consecutive lines belonging to one packed unit."""

    lines: tuple[ProseLine, ...]
    cont_prefix: str

    @property
    def suffix(self) -> str:
        return self.lines[-1].suffix


class _RunCollector:
    """Accumulates ProseLine entries into contiguous ProseRun groups."""

    def __init__(self) -> None:
        self.runs: list[ProseRun] = []
        self._buf: list[ProseLine] = []
        self._single_cont = ""

    def add(self, pline: ProseLine, single_cont: str) -> None:
        if self._buf and self._buf[-1].indent != pline.indent:
            self.break_run()
        if not self._buf:
            self._single_cont = single_cont
        self._buf.append(pline)

    def break_run(self) -> None:
        if self._buf:
            cont = (
                self._buf[1].prefix if len(self._buf) > 1 else self._single_cont
            )
            self.runs.append(ProseRun(tuple(self._buf), cont))
            self._buf = []


def _split_prefix_text(raw: str, text: str) -> tuple[str, str]:
    stripped = raw.rstrip()
    return stripped[: len(stripped) - len(text)], stripped[-len(text) :]


def _is_verbatim_notice(
    raw: str, notice_values: tuple[str, ...], markers: tuple[str, ...]
) -> bool:
    if not notice_values:
        return False
    line = raw.rstrip()
    return any(
        line == marker + val
        for marker in markers
        for val in notice_values
        if val.strip()
    )


def load_prose_directives(root: Path) -> frozenset[str]:
    """Load need directive names from target `config/sphinx/needs_model.py`."""
    model_path = root / "config" / "sphinx" / "needs_model.py"
    if not model_path.is_file():
        return FALLBACK_NEED_DIRECTIVES
    try:
        spec = importlib.util.spec_from_file_location(
            "_target_needs_model", model_path
        )
        if spec is None or spec.loader is None:
            return FALLBACK_NEED_DIRECTIVES
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "get_prose_directives"):
            names = module.get_prose_directives()
            return frozenset(str(n) for n in names)
        if hasattr(module, "NEEDS_TYPES"):
            return frozenset(
                str(entry["directive"])
                for entry in module.NEEDS_TYPES
                if isinstance(entry, dict) and "directive" in entry
            )
    except Exception:
        return FALLBACK_NEED_DIRECTIVES
    return FALLBACK_NEED_DIRECTIVES


def _collect_markdown(
    lines: list[str],
    prose_directives: frozenset[str],
    notice_values: tuple[str, ...],
) -> list[ProseRun]:
    collector = _RunCollector()
    # Stack entries: (fence_char, fence_len, is_prose_need)
    fence_stack: list[tuple[str, int, bool]] = []
    after_open = False
    in_yaml_options = False

    for no, raw in enumerate(lines, start=1):
        if no == 1 and raw.strip() == "---":
            in_yaml_options = True
            continue
        if in_yaml_options:
            if raw.strip() == "---":
                in_yaml_options = False
            continue

        m_fence = MD_FENCE_RE.match(raw)
        if fence_stack:
            if m_fence:
                f_char = m_fence.group(2)[0]
                f_len = len(m_fence.group(2))
                info = m_fence.group(3).strip()
                top = fence_stack[-1]
                if f_char == top[0] and f_len >= top[1] and not info:
                    fence_stack.pop()
                    collector.break_run()
                    after_open = False
                    continue
                if f_len < top[1] and top[2]:
                    m_dir = MD_NEED_DIR_RE.match(info)
                    is_prose = bool(
                        m_dir and m_dir.group(1) in prose_directives
                    )
                    fence_stack.append((f_char, f_len, is_prose))
                    collector.break_run()
                    after_open = is_prose
                    continue
            if not fence_stack[-1][2]:
                continue
            if after_open and raw.strip() == "---":
                in_yaml_options = True
                after_open = False
                collector.break_run()
                continue
            after_open = False
        elif m_fence:
            f_char = m_fence.group(2)[0]
            f_len = len(m_fence.group(2))
            info = m_fence.group(3).strip()
            m_dir = MD_NEED_DIR_RE.match(info)
            is_prose = bool(m_dir and m_dir.group(1) in prose_directives)
            fence_stack.append((f_char, f_len, is_prose))
            collector.break_run()
            after_open = is_prose
            continue

        stripped = raw.strip()
        if not stripped:
            collector.break_run()
            continue

        if (
            stripped.startswith("#")
            or stripped.startswith("|")
            or stripped.startswith(">")
            or stripped.startswith("<!--")
            or MD_HR_RE.match(raw)
            or MD_SETEXT_RE.match(raw)
            or MD_LINK_DEF_RE.match(raw)
            or MD_FIELD_RE.match(raw)
            or (no < len(lines) and MD_SETEXT_RE.match(lines[no]))
            or _is_verbatim_notice(raw, notice_values, ("",))
        ):
            collector.break_run()
            continue

        m_list = MD_LIST_RE.match(stripped)
        if m_list:
            collector.break_run()
            item_text = m_list.group(4)
            prefix, _ = _split_prefix_text(raw, item_text)
            collector.add(
                ProseLine(no, prefix, item_text, indent=len(prefix)),
                " " * len(prefix),
            )
            continue

        prefix, text = _split_prefix_text(raw, stripped)
        # Skip deeply indented code blocks not continuing a list item
        if len(prefix) >= 4 and (
            not collector._buf or collector._buf[-1].indent != len(prefix)
        ):
            collector.break_run()
            continue
        collector.add(
            ProseLine(no, prefix, text, indent=len(prefix)),
            " " * len(prefix),
        )

    collector.break_run()
    return collector.runs


def _collect_rst(
    lines: list[str],
    prose_directives: frozenset[str],
    notice_values: tuple[str, ...],
) -> list[ProseRun]:
    collector = _RunCollector()
    skip_indent: int | None = None

    for no, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        indent_len = len(raw) - len(raw.lstrip(" "))

        if skip_indent is not None:
            if not stripped or indent_len > skip_indent:
                continue
            skip_indent = None

        if not stripped:
            collector.break_run()
            continue

        m_dir = RST_DIRECTIVE_RE.match(raw)
        if m_dir:
            collector.break_run()
            dir_indent = len(m_dir.group(1))
            if m_dir.group(2) not in prose_directives:
                skip_indent = dir_indent
            continue

        if (
            RST_UNDERLINE_RE.match(stripped)
            or (no < len(lines) and RST_UNDERLINE_RE.match(lines[no].strip()))
            or RST_LINK_DEF_RE.match(raw)
            or MD_FIELD_RE.match(raw)
            or stripped.startswith(("|", "+---", "+===", ".. "))
            or _is_verbatim_notice(raw, notice_values, ("",))
        ):
            collector.break_run()
            if stripped.endswith("::"):
                skip_indent = indent_len
            continue

        if stripped.endswith("::"):
            prefix, text = _split_prefix_text(raw, stripped)
            collector.add(
                ProseLine(no, prefix, text, indent=len(prefix)),
                " " * len(prefix),
            )
            collector.break_run()
            skip_indent = indent_len
            continue

        m_list = MD_LIST_RE.match(stripped)
        if m_list:
            collector.break_run()
            item_text = m_list.group(4)
            prefix, _ = _split_prefix_text(raw, item_text)
            collector.add(
                ProseLine(no, prefix, item_text, indent=len(prefix)),
                " " * len(prefix),
            )
            continue

        prefix, text = _split_prefix_text(raw, stripped)
        collector.add(
            ProseLine(no, prefix, text, indent=len(prefix)),
            " " * len(prefix),
        )

    collector.break_run()
    return collector.runs


def _is_non_packed_comment(body: str) -> bool:
    stripped = body.strip()
    if not stripped:
        return True
    probe = stripped.lstrip("#").strip()
    return bool(
        TAG_LINE_RE.match(probe)
        or DOXYGEN_CMD_RE.match(stripped)
        or TOOL_DIRECTIVE_RE.match(stripped)
        or stripped.startswith(("|", "```"))
    )


def _header_end_index(lines: list[str], style: str | None) -> int:
    idx = 1 if (lines and lines[0].startswith("#!")) else 0
    if idx >= len(lines):
        return idx
    if style == "hash" and lines[idx].strip() == "##":
        end = idx + 1
        while end < len(lines) and lines[end].startswith("#"):
            end += 1
        return end
    if style == "c_block" and lines[idx].strip() == "/**":
        end = idx + 1
        while end < len(lines):
            if lines[end].strip() == "*/":
                return end + 1
            end += 1
    return idx


def _collect_hash_line(
    raw: str,
    no: int,
    collector: _RunCollector,
    notice_values: tuple[str, ...],
) -> None:
    stripped = raw.strip()
    if not stripped.startswith("#") or stripped.startswith("#!"):
        collector.break_run()
        return
    body = stripped.lstrip("#").strip()
    if not body or _is_non_packed_comment(body):
        collector.break_run()
        return
    if _is_verbatim_notice(raw, notice_values, ("# ",)):
        collector.break_run()
        return
    m_list = MD_LIST_RE.match(body)
    if m_list:
        collector.break_run()
        item_text = m_list.group(4)
        prefix, _ = _split_prefix_text(raw, item_text)
        hash_prefix = raw[: raw.index("#") + 1]
        cont = hash_prefix + " " * (len(prefix) - len(hash_prefix))
        collector.add(
            ProseLine(no, prefix, item_text, indent=len(prefix)),
            cont,
        )
        return
    prefix, text = _split_prefix_text(raw, body)
    collector.add(ProseLine(no, prefix, text, indent=len(prefix)), prefix)


def _docstring_spans(lines: list[str]) -> list[tuple[int, int, int]]:
    """Return `(first_line, last_line, base_indent)` for true docstrings."""
    try:
        tree = ast.parse("\n".join(lines))
    except SyntaxError:
        return []
    spans: list[tuple[int, int, int]] = []
    for node in ast.walk(tree):
        if not isinstance(
            node,
            (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            continue
        if not (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            continue
        const = node.body[0].value
        assert const.end_lineno is not None
        closer = lines[const.end_lineno - 1]
        base_indent = len(closer) - len(closer.lstrip(" "))
        spans.append((const.lineno, const.end_lineno, base_indent))
    return spans


def _collect_docstring_span(
    span: tuple[int, int, int],
    lines: list[str],
    collector: _RunCollector,
    notice_values: tuple[str, ...],
) -> None:
    first, last, base_indent = span
    if first == last:
        return
    span_lines = lines[first - 1 : last]
    opener = span_lines[0].rstrip()
    delim = '"""' if '"""' in opener else "'''"
    if delim not in opener:
        return
    open_text = opener[opener.index(delim) + 3 :].strip()
    if open_text:
        prefix, _ = _split_prefix_text(opener, open_text)
        collector.add(
            ProseLine(first, prefix, open_text, indent=base_indent),
            " " * base_indent,
        )
    for no, raw in enumerate(span_lines[1:-1], start=first + 1):
        stripped = raw.strip()
        if not stripped:
            collector.break_run()
            continue
        if _is_non_packed_comment(stripped) or _is_verbatim_notice(
            raw, notice_values, ("", "# ")
        ):
            collector.break_run()
            continue
        m_list = MD_LIST_RE.match(stripped)
        if m_list:
            collector.break_run()
            item_text = m_list.group(4)
            prefix, _ = _split_prefix_text(raw, item_text)
            collector.add(
                ProseLine(no, prefix, item_text, indent=len(prefix)),
                " " * len(prefix),
            )
            continue
        prefix, text = _split_prefix_text(raw, stripped)
        collector.add(
            ProseLine(no, prefix, text, indent=len(prefix)),
            " " * len(prefix),
        )
    closer = span_lines[-1].rstrip()
    if delim in closer:
        before = closer[: closer.index(delim)]
        close_text = before.strip()
        if close_text:
            prefix, _ = _split_prefix_text(before, close_text)
            collector.add(
                ProseLine(
                    last, prefix, close_text, suffix=delim, indent=len(prefix)
                ),
                " " * base_indent,
            )
    collector.break_run()


def _collect_python(
    lines: list[str],
    notice_values: tuple[str, ...],
) -> list[ProseRun]:
    collector = _RunCollector()
    hdr_end = _header_end_index(lines, "hash")
    spans = _docstring_spans(lines)
    span_at = {s[0]: s for s in spans}
    covered = {n for first, last, _ in spans for n in range(first, last + 1)}

    for no, raw in enumerate(lines, start=1):
        if no <= hdr_end:
            continue
        if no in span_at:
            collector.break_run()
            _collect_docstring_span(
                span_at[no], lines, collector, notice_values
            )
        elif no in covered:
            collector.break_run()
        else:
            _collect_hash_line(raw, no, collector, notice_values)
    collector.break_run()
    return collector.runs


def _collect_hash_only(
    lines: list[str],
    header_style: str | None,
    notice_values: tuple[str, ...],
) -> list[ProseRun]:
    collector = _RunCollector()
    hdr_end = _header_end_index(lines, header_style)
    for no, raw in enumerate(lines, start=1):
        if no <= hdr_end:
            continue
        _collect_hash_line(raw, no, collector, notice_values)
    collector.break_run()
    return collector.runs


def _collect_c_cpp(
    lines: list[str], notice_values: tuple[str, ...]
) -> list[ProseRun]:
    collector = _RunCollector()
    hdr_end = _header_end_index(lines, "c_block")
    in_block = False

    for no, raw in enumerate(lines, start=1):
        if no <= hdr_end:
            continue
        stripped = raw.strip()
        if in_block:
            end = stripped.endswith("*/") and "/*" not in stripped
            body = stripped[:-2] if end else stripped
            text = body.strip().lstrip("*").strip() if body.strip(" *") else ""
            if (
                not text
                or _is_non_packed_comment(text)
                or _is_verbatim_notice(raw, notice_values, (" * ",))
            ):
                collector.break_run()
            else:
                prefix, _ = _split_prefix_text(raw, text)
                collector.add(
                    ProseLine(no, prefix, text, indent=len(prefix)), prefix
                )
            in_block = not end
            continue

        if stripped.startswith("/*"):
            body = stripped[2:]
            end = body.rstrip().endswith("*/")
            text = (
                (body.rstrip()[:-2] if end else body)
                .strip()
                .lstrip("*")
                .strip()
            )
            collector.break_run()
            if (
                text
                and not _is_non_packed_comment(text)
                and not _is_verbatim_notice(raw, notice_values, (" * ", "/* "))
            ):
                prefix, _ = _split_prefix_text(raw, text)
                collector.add(
                    ProseLine(no, prefix, text, indent=len(prefix)), prefix
                )
            in_block = not end
            continue

        if not stripped.startswith("//"):
            collector.break_run()
            continue
        text = stripped[2:].strip()
        if (
            not text
            or _is_non_packed_comment(text)
            or _is_verbatim_notice(raw, notice_values, ("// ",))
        ):
            collector.break_run()
            continue
        m_list = MD_LIST_RE.match(text)
        if m_list:
            collector.break_run()
            item_text = m_list.group(4)
            prefix, _ = _split_prefix_text(raw, item_text)
            slash_prefix = raw[: raw.index("//") + 2]
            cont = slash_prefix + " " * (len(prefix) - len(slash_prefix))
            collector.add(
                ProseLine(no, prefix, item_text, indent=len(prefix)),
                cont,
            )
            continue
        prefix, _ = _split_prefix_text(raw, text)
        collector.add(ProseLine(no, prefix, text, indent=len(prefix)), prefix)

    collector.break_run()
    return collector.runs


def _collect_runs(
    lines: list[str],
    kind: FileKind,
    prose_directives: frozenset[str],
    notice_values: tuple[str, ...],
) -> list[ProseRun]:
    if kind == KIND_MARKDOWN:
        return _collect_markdown(lines, prose_directives, notice_values)
    if kind == KIND_RST:
        return _collect_rst(lines, prose_directives, notice_values)
    if kind == KIND_PYTHON:
        return _collect_python(lines, notice_values)
    if kind in (KIND_CMAKE, KIND_SHELL, KIND_HASH_DATA):
        return _collect_hash_only(lines, kind.header_style, notice_values)
    if kind == KIND_C_CPP:
        return _collect_c_cpp(lines, notice_values)
    return []


def _rewrap_runs(
    lines: list[str], runs: list[ProseRun], limit: int
) -> list[str]:
    spans: list[tuple[int, int, list[str]]] = []
    for run in runs:
        words = [w for ln in run.lines for w in ln.text.split()]
        if not words:
            continue
        effective = limit - len(run.suffix)
        rendered: list[str] = []
        first_prefix = run.lines[0].prefix
        cur = first_prefix
        for idx, word in enumerate(words):
            cap = effective if idx == len(words) - 1 else limit
            if cur == first_prefix:
                cur = first_prefix + word
            elif len(cur) + 1 + len(word) <= cap:
                cur = f"{cur} {word}"
            else:
                rendered.append(cur)
                cur = run.cont_prefix + word
        rendered.append(cur + run.suffix)
        spans.append(
            (run.lines[0].no, run.lines[-1].no - run.lines[0].no + 1, rendered)
        )

    out: list[str] = []
    cursor = 0
    for first, count, rendered in sorted(spans):
        start = first - 1
        out.extend(lines[cursor:start])
        out.extend(rendered)
        cursor = start + count
    out.extend(lines[cursor:])
    return out


def check_file_lines(
    root: Path,
    rel_path: Path,
    kind: FileKind,
    limit: int,
    *,
    prose_packing: bool = True,
    prose_directives: frozenset[str] = FALLBACK_NEED_DIRECTIVES,
    notice_values: tuple[str, ...] = (),
    fix: bool = False,
) -> list[Finding]:
    """Check (and optionally fix) line lengths and prose packing for a file."""
    full_path = root / rel_path
    text = full_path.read_text(encoding="utf-8")
    had_trailing_nl = text.endswith("\n") or text == ""
    lines = text.splitlines()

    if fix and prose_packing:
        runs = _collect_runs(lines, kind, prose_directives, notice_values)
        new_lines = _rewrap_runs(lines, runs, limit)
        new_text = "\n".join(new_lines) + ("\n" if had_trailing_nl else "")
        if new_text != text:
            full_path.write_text(new_text, encoding="utf-8")
            lines = new_lines

    findings: list[Finding] = []
    for idx, line in enumerate(lines, start=1):
        if len(line) > limit:
            findings.append(
                Finding(
                    rel_path,
                    idx,
                    f"line length {len(line)} exceeds maximum {limit}",
                )
            )

    if prose_packing:
        runs = _collect_runs(lines, kind, prose_directives, notice_values)
        for run in runs:
            last = run.lines[-1]
            for a, b in zip(run.lines, run.lines[1:]):
                words = b.text.split()
                if not words:
                    continue
                word = words[0]
                extra = len(b.suffix) if (b is last and len(words) == 1) else 0
                cur_len = len(a.prefix) + len(a.text)
                if cur_len + 1 + len(word) + extra <= limit:
                    findings.append(
                        Finding(
                            rel_path,
                            a.no,
                            "prose line is not greedily packed "
                            f"('{word}' fits within {limit} columns)",
                        )
                    )

    return findings


def check_line_lengths(
    root: Path,
    files: list[tuple[Path, FileKind]],
    editorconfig: EditorConfig,
    *,
    prose_packing: bool = True,
    fix: bool = False,
) -> list[Finding]:
    """Check line lengths and prose packing across `files`."""
    directives = load_prose_directives(root)
    notice_values = tuple(editorconfig.file_header or ())
    findings: list[Finding] = []
    for rel_path, kind in files:
        limit = editorconfig.max_line_length_for(rel_path)
        if limit is None:
            continue
        findings.extend(
            check_file_lines(
                root,
                rel_path,
                kind,
                limit,
                prose_packing=prose_packing,
                prose_directives=directives,
                notice_values=notice_values,
                fix=fix,
            )
        )
    return findings


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for standalone line-length and packing checks."""
    parser = argparse.ArgumentParser(
        description="Check line length and greedy prose packing."
    )
    parser.add_argument(
        "--root", required=True, help="Path to the target repository root."
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Re-pack prose paragraphs in place.",
    )
    parser.add_argument(
        "paths", nargs="*", help="Optional paths to check (relative to --root)."
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"error: root directory not found: {root}", file=sys.stderr)
        return 2

    try:
        proj_cfg, cfg_notices = load_project_config(root, allow_missing=True)
        ec, ec_notices = load_editorconfig(root)
        files = discover_files(
            root,
            ec,
            extra_excludes=proj_cfg["model"]["code_tag_exclude"],
            explicit_paths=args.paths or None,
        )
    except (ConfigError, EditorConfigError, FileNotFoundError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    for notice in [*cfg_notices, *ec_notices]:
        print(notice, file=sys.stderr)

    findings = check_line_lengths(
        root,
        files,
        ec,
        prose_packing=proj_cfg["checks"]["prose_packing"],
        fix=args.fix,
    )
    for finding in sorted(findings, key=lambda f: (f.path.as_posix(), f.line)):
        print(finding.format())
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

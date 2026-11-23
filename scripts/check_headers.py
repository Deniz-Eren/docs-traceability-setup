##
# @file     check_headers.py
# @brief    Validate and repair Doxygen file header blocks
#
# @copyright
# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>
# MIT License
#

"""Doxygen file header validator and fixer."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from editorconfig import EditorConfig, EditorConfigError, load_editorconfig
from file_kinds import FileKind, discover_files
from project_config import ConfigError, load_project_config


@dataclass(frozen=True)
class Finding:
    """A single `<file>:<line>: <message>` checker finding."""

    path: Path
    line: int
    message: str

    def format(self) -> str:
        return f"{self.path.as_posix()}:{self.line}: {self.message}"


def _format_header(
    style: str,
    filename: str,
    brief: str,
    notice_lines: list[str],
    details_lines: list[str] | None = None,
) -> list[str]:
    """Render one canonical Doxygen file header block."""
    opener = "##" if style == "hash" else "/**"
    marker = "#" if style == "hash" else " *"

    out = [
        opener,
        f"{marker} @file     {filename}",
        f"{marker} @brief    {brief}",
        marker,
    ]
    if details_lines:
        out.append(
            f"{marker} @details  {details_lines[0]}"
            if details_lines[0]
            else f"{marker} @details"
        )
        for extra in details_lines[1:]:
            out.append(f"{marker} {extra}" if extra else marker)
        out.append(marker)

    out.append(f"{marker} @copyright")
    for line in notice_lines:
        out.append(f"{marker} {line}" if line else marker)
    out.append(marker)
    if style == "c_block":
        out.append(" */")
    return out


def _is_comment_line(line: str, marker: str) -> bool:
    return line == marker or line.startswith(f"{marker} ")


def _find_block_end(lines: list[str], start_idx: int, style: str) -> int | None:
    """Return exclusive end index of an existing leading header block."""
    if start_idx >= len(lines):
        return None
    if style == "hash":
        if lines[start_idx] != "##":
            return None
        end = start_idx + 1
        while end < len(lines) and _is_comment_line(lines[end], "#"):
            end += 1
        return end
    if style == "c_block":
        if lines[start_idx] != "/**":
            return None
        end = start_idx + 1
        while end < len(lines):
            if lines[end] == " */":
                return end + 1
            if not _is_comment_line(lines[end], " *"):
                return None
            end += 1
        return None
    return None


def _extract_existing_brief_and_details(
    lines: list[str], start_idx: int, end_idx: int, style: str
) -> tuple[str, list[str] | None]:
    """Preserve `@brief` and `@details` when repairing a header block."""
    marker = "#" if style == "hash" else " *"
    brief = "TODO"
    details: list[str] | None = None
    in_details = False
    body_end = end_idx - 1 if style == "c_block" else end_idx

    for raw in lines[start_idx + 1 : body_end]:
        if raw == marker:
            if in_details and details is not None:
                details.append("")
            continue
        content = raw[len(marker) + 1 :]
        if content.startswith("@copyright"):
            break
        if content.startswith("@brief"):
            val = content[len("@brief") :].strip()
            if val:
                brief = val
            in_details = False
        elif content.startswith("@details"):
            val = content[len("@details") :].strip()
            details = [val]
            in_details = True
        elif in_details and details is not None:
            details.append(content)

    if details is not None:
        while details and details[-1] == "":
            details.pop()
        if not details:
            details = None
    return brief, details


def _validate_header_lines(
    rel_path: Path,
    lines: list[str],
    start_idx: int,
    style: str,
    notice_lines: list[str],
) -> list[Finding]:
    """Validate one Doxygen header block line by line."""
    opener = "##" if style == "hash" else "/**"
    marker = "#" if style == "hash" else " *"
    findings: list[Finding] = []

    def expect(idx: int, expected: str, what: str) -> bool:
        if idx < len(lines) and lines[idx] == expected:
            return True
        found = lines[idx] if idx < len(lines) else "<end of file>"
        findings.append(
            Finding(
                rel_path,
                idx + 1,
                f"expected {what}: {expected!r}, found {found!r}",
            )
        )
        return False

    if not expect(start_idx, opener, "header block opener"):
        return findings

    idx = start_idx + 1
    if not expect(idx, f"{marker} @file     {rel_path.name}", "@file line"):
        return findings

    idx += 1
    brief_prefix = f"{marker} @brief    "
    if idx >= len(lines) or not lines[idx].startswith(brief_prefix):
        found = lines[idx] if idx < len(lines) else "<end of file>"
        findings.append(
            Finding(
                rel_path,
                idx + 1,
                f"missing or malformed '@brief' line, found {found!r}",
            )
        )
        return findings

    brief_text = lines[idx][len(brief_prefix) :].strip()
    if not brief_text or brief_text == "TODO":
        findings.append(
            Finding(rel_path, idx + 1, "@brief must describe the file function")
        )
    elif brief_text.endswith("."):
        findings.append(
            Finding(rel_path, idx + 1, "@brief must not end with a period")
        )

    # Scan optional @details region up to '@copyright', requiring a closing bare
    # marker line immediately before '@copyright'.
    idx += 1
    details_prefix = f"{marker} @details  "
    copyright_line = f"{marker} @copyright"
    doc_start = idx
    has_details = False
    while idx < len(lines):
        line = lines[idx]
        if (
            line == copyright_line
            or line.startswith(f"{copyright_line} ")
            or not _is_comment_line(line, marker)
        ):
            break
        if line != marker:
            if not has_details and not line.startswith(details_prefix):
                findings.append(
                    Finding(
                        rel_path,
                        idx + 1,
                        f"expected '@details' region to open with "
                        f"{details_prefix!r}, found {line!r}",
                    )
                )
                return findings
            has_details = True
        idx += 1

    if idx == doc_start or lines[idx - 1] != marker:
        findings.append(
            Finding(
                rel_path,
                idx + 1,
                f"expected bare {marker!r} line before '@copyright'",
            )
        )
        return findings

    if not expect(idx, copyright_line, "'@copyright' line"):
        return findings

    idx += 1
    for notice_line in notice_lines:
        expected = f"{marker} {notice_line}" if notice_line else marker
        if not expect(idx, expected, "[file-header] copyright line"):
            return findings
        idx += 1

    if not expect(idx, marker, "closing bare comment line of header block"):
        return findings
    idx += 1

    if style == "c_block":
        if not expect(idx, " */", "closing ' */' line of header block"):
            return findings
        idx += 1

    if idx < len(lines) and lines[idx] != "":
        findings.append(
            Finding(
                rel_path,
                idx + 1,
                "expected empty line after Doxygen header block",
            )
        )

    return findings


def check_file_header(
    root: Path,
    rel_path: Path,
    kind: FileKind,
    notice_lines: list[str],
    *,
    fix: bool = False,
) -> list[Finding]:
    """Check (and optionally fix) the Doxygen header of a single file."""
    if kind.header_style is None:
        return []

    full_path = root / rel_path
    text = full_path.read_text(encoding="utf-8")
    had_trailing_nl = text.endswith("\n") or text == ""
    lines = text.splitlines()
    start_idx = 1 if (lines and lines[0].startswith("#!")) else 0

    if fix:
        block_end = _find_block_end(lines, start_idx, kind.header_style)
        if block_end is None:
            brief = "TODO"
            details = None
            rest = lines[start_idx:]
        else:
            brief, details = _extract_existing_brief_and_details(
                lines, start_idx, block_end, kind.header_style
            )
            rest = lines[block_end:]

        if rest and rest[0] == "":
            rest = rest[1:]

        header_lines = _format_header(
            kind.header_style, rel_path.name, brief, notice_lines, details
        )
        new_lines = lines[:start_idx] + header_lines
        if rest:
            new_lines.append("")
            new_lines.extend(rest)
        new_text = "\n".join(new_lines) + ("\n" if had_trailing_nl else "")
        if new_text != text:
            full_path.write_text(new_text, encoding="utf-8")
            lines = new_lines

    return _validate_header_lines(
        rel_path, lines, start_idx, kind.header_style, notice_lines
    )


def check_headers(
    root: Path,
    files: list[tuple[Path, FileKind]],
    editorconfig: EditorConfig,
    *,
    enabled: bool = True,
    fix: bool = False,
) -> tuple[list[Finding], list[str]]:
    """Run header checks across `files`, returning `(findings, notices)`."""
    if not enabled:
        return [], []
    if editorconfig.file_header is None:
        return [], [
            "notice: [file-header] not defined in .editorconfig; "
            "skipping file header check"
        ]
    findings: list[Finding] = []
    for rel_path, kind in files:
        findings.extend(
            check_file_header(
                root, rel_path, kind, editorconfig.file_header, fix=fix
            )
        )
    return findings, []


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for standalone header checking."""
    parser = argparse.ArgumentParser(
        description="Check Doxygen file headers against .editorconfig."
    )
    parser.add_argument(
        "--root", required=True, help="Path to the target repository root."
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Insert or repair header blocks in place.",
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

    findings, hdr_notices = check_headers(
        root,
        files,
        ec,
        enabled=proj_cfg["checks"]["file_headers"],
        fix=args.fix,
    )
    for notice in [*cfg_notices, *ec_notices, *hdr_notices]:
        print(notice, file=sys.stderr)
    for finding in sorted(findings, key=lambda f: (f.path.as_posix(), f.line)):
        print(finding.format())
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

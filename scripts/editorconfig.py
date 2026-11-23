##
# @file     editorconfig.py
# @brief    Parse .editorconfig glob sections and [file-header] notices
#
# @copyright
# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>
# MIT License
#

"""EditorConfig reader with glob section matching and `[file-header]` rules."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

DEFAULTS_PATH = Path(__file__).resolve().parent / "defaults.editorconfig"

VALID_CHARSETS = frozenset(
    {"utf-8", "utf-8-bom", "latin1", "utf-16be", "utf-16le"}
)
VALID_EOL = frozenset({"lf", "crlf", "cr"})
VALID_INDENT_STYLES = frozenset({"space", "tab"})
VALID_BOOLS = frozenset({"true", "false"})
HEADER_KEY_RE = re.compile(r"^[0-9]{2}$")


class EditorConfigError(ValueError):
    """Raised when an `.editorconfig` file contains invalid syntax or values."""


def _expand_braces(pattern: str) -> list[str]:
    """Expand `{a,b}` and `{1..3}` brace expressions in an EditorConfig glob."""
    depth = 0
    start = -1
    for idx, ch in enumerate(pattern):
        if ch == "\\" and idx + 1 < len(pattern):
            continue
        if ch == "{":
            if depth == 0:
                start = idx
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start != -1:
                    inner = pattern[start + 1 : idx]
                    prefix = pattern[:start]
                    suffix = pattern[idx + 1 :]
                    range_match = re.fullmatch(
                        r"(-?[0-9]+)\.\.(-?[0-9]+)", inner
                    )
                    if range_match:
                        lo = int(range_match.group(1))
                        hi = int(range_match.group(2))
                        step = 1 if lo <= hi else -1
                        alts = [str(n) for n in range(lo, hi + step, step)]
                    elif "," in inner:
                        alts = _split_brace_items(inner)
                    else:
                        return [pattern]
                    out: list[str] = []
                    for alt in alts:
                        out.extend(_expand_braces(prefix + alt + suffix))
                    return out
    return [pattern]


def _split_brace_items(inner: str) -> list[str]:
    items: list[str] = []
    buf: list[str] = []
    depth = 0
    for ch in inner:
        if ch == "{":
            depth += 1
            buf.append(ch)
        elif ch == "}":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            items.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    items.append("".join(buf))
    return items


def _glob_to_regex(glob: str) -> re.Pattern[str]:
    """Compile a single brace-expanded EditorConfig glob to a regex."""
    has_slash = "/" in glob
    pat = glob.lstrip("/")
    i = 0
    n = len(pat)
    parts: list[str] = []
    while i < n:
        ch = pat[i]
        if ch == "\\" and i + 1 < n:
            parts.append(re.escape(pat[i + 1]))
            i += 2
        elif ch == "*":
            if i + 1 < n and pat[i + 1] == "*":
                if i + 2 < n and pat[i + 2] == "/":
                    parts.append("(?:.*/)?")
                    i += 3
                else:
                    parts.append(".*")
                    i += 2
            else:
                parts.append("[^/]*")
                i += 1
        elif ch == "?":
            parts.append("[^/]")
            i += 1
        elif ch == "[":
            j = i + 1
            if j < n and pat[j] in ("!", "^"):
                j += 1
            if j < n and pat[j] == "]":
                j += 1
            while j < n and pat[j] != "]":
                j += 1
            if j >= n:
                parts.append(re.escape(ch))
                i += 1
            else:
                body = pat[i + 1 : j]
                if body.startswith("!"):
                    body = "^" + body[1:]
                parts.append(f"[{body}]")
                i = j + 1
        else:
            parts.append(re.escape(ch))
            i += 1
    body_re = "".join(parts)
    if has_slash:
        return re.compile(f"^{body_re}$")
    return re.compile(f"^(?:.*/)?{body_re}$")


def match_section_glob(section_pattern: str, rel_posix: str) -> bool:
    """Return True when `rel_posix` matches an EditorConfig section header."""
    for expanded in _expand_braces(section_pattern):
        if _glob_to_regex(expanded).match(rel_posix):
            return True
    return False


def _validate_property(key: str, val: str, line_no: int) -> str:
    low_key = key.lower()
    low_val = val.lower()
    if low_key == "max_line_length":
        if low_val == "off":
            return "off"
        if re.fullmatch(r"[0-9]+", low_val) and int(low_val) > 0:
            return low_val
        raise EditorConfigError(
            f"line {line_no}: invalid max_line_length '{val}'"
        )
    if low_key == "indent_style":
        if low_val not in VALID_INDENT_STYLES:
            raise EditorConfigError(
                f"line {line_no}: invalid indent_style '{val}'"
            )
        return low_val
    if low_key == "indent_size":
        if low_val == "tab" or (
            re.fullmatch(r"[0-9]+", low_val) and int(low_val) > 0
        ):
            return low_val
        raise EditorConfigError(f"line {line_no}: invalid indent_size '{val}'")
    if low_key == "tab_width":
        if re.fullmatch(r"[0-9]+", low_val) and int(low_val) > 0:
            return low_val
        raise EditorConfigError(f"line {line_no}: invalid tab_width '{val}'")
    if low_key == "end_of_line":
        if low_val not in VALID_EOL:
            raise EditorConfigError(
                f"line {line_no}: invalid end_of_line '{val}'"
            )
        return low_val
    if low_key == "charset":
        if low_val not in VALID_CHARSETS:
            raise EditorConfigError(f"line {line_no}: invalid charset '{val}'")
        return low_val
    if low_key in ("trim_trailing_whitespace", "insert_final_newline"):
        if low_val not in VALID_BOOLS:
            raise EditorConfigError(
                f"line {line_no}: invalid {low_key} '{val}'"
            )
        return low_val
    return val


@dataclass
class EditorConfig:
    """Parsed representation of an `.editorconfig` file."""

    sections: list[tuple[str, dict[str, str]]] = field(default_factory=list)
    file_header: list[str] | None = None

    def properties_for(self, rel_path: str | Path) -> dict[str, str]:
        """Resolve merged properties for a repo-relative file path."""
        rel_posix = Path(rel_path).as_posix().lstrip("./")
        props: dict[str, str] = {}
        for pattern, section_props in self.sections:
            if match_section_glob(pattern, rel_posix):
                props.update(section_props)
        return props

    def max_line_length_for(self, rel_path: str | Path) -> int | None:
        """Return max line length as int, or None when set to `off`."""
        props = self.properties_for(rel_path)
        raw = props.get("max_line_length", "80")
        if raw == "off":
            return None
        return int(raw)


def parse_editorconfig(text: str) -> EditorConfig:
    """Parse EditorConfig text, validating properties and `[file-header]`."""
    cfg = EditorConfig()
    current_section: str | None = None
    current_props: dict[str, str] = {}
    header_entries: dict[int, str] = {}
    saw_file_header = False

    def flush_section() -> None:
        if current_section is not None and current_section != "file-header":
            cfg.sections.append((current_section, dict(current_props)))

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith(";"):
            continue

        if stripped.startswith("["):
            if not stripped.endswith("]"):
                raise EditorConfigError(
                    f"line {line_no}: unterminated section header"
                )
            flush_section()
            current_section = stripped[1:-1].strip()
            if not current_section:
                raise EditorConfigError(f"line {line_no}: empty section header")
            current_props = {}
            if current_section == "file-header":
                saw_file_header = True
            continue

        if "=" not in raw_line:
            raise EditorConfigError(f"line {line_no}: expected 'key = value'")
        key_raw, _, val_raw = raw_line.partition("=")
        key = key_raw.strip()
        if not key:
            raise EditorConfigError(f"line {line_no}: empty property key")

        if current_section is None:
            if key.lower() != "root":
                raise EditorConfigError(
                    f"line {line_no}: unexpected preamble key '{key}'"
                )
            if val_raw.strip().lower() not in VALID_BOOLS:
                raise EditorConfigError(
                    f"line {line_no}: invalid root value '{val_raw.strip()}'"
                )
            continue

        if current_section == "file-header":
            if not HEADER_KEY_RE.fullmatch(key):
                raise EditorConfigError(
                    f"line {line_no}: [file-header] key '{key}' must be two "
                    "digits (01, 02, ...)"
                )
            idx = int(key)
            if idx in header_entries:
                raise EditorConfigError(
                    f"line {line_no}: duplicate [file-header] key '{key}'"
                )
            # Remove at most one separating space after '=' so indented notice
            # lines keep their leading spaces verbatim.
            notice_line = val_raw.rstrip()
            if notice_line.startswith(" "):
                notice_line = notice_line[1:]
            header_entries[idx] = notice_line
            continue

        val = val_raw.strip()
        validated = _validate_property(key, val, line_no)
        current_props[key.lower()] = validated

    flush_section()
    if saw_file_header:
        sorted_keys = sorted(header_entries)
        expected_keys = list(range(1, len(sorted_keys) + 1))
        if not sorted_keys or sorted_keys != expected_keys:
            raise EditorConfigError(
                "[file-header] keys must form a contiguous 2-digit run "
                "starting at 01"
            )
        cfg.file_header = [header_entries[k] for k in sorted_keys]
    return cfg


def load_editorconfig(root: Path) -> tuple[EditorConfig, list[str]]:
    """Load `.editorconfig` from `root`, falling back to built-in defaults."""
    target = root / ".editorconfig"
    if not target.is_file():
        notice = (
            f"notice: .editorconfig not found in {root}; "
            f"using {DEFAULTS_PATH.name}"
        )
        text = DEFAULTS_PATH.read_text(encoding="utf-8")
        return parse_editorconfig(text), [notice]

    text = target.read_text(encoding="utf-8")
    return parse_editorconfig(text), []

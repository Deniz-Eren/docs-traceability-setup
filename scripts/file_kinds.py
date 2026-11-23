##
# @file     file_kinds.py
# @brief    Classify file kinds, comment syntax, and repository check scope
#
# @copyright
# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>
# MIT License
#

"""File kind definitions and repository file discovery for text checks."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from editorconfig import EditorConfig

EXCLUDED_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "build",
        "__pycache__",
        ".ruff_cache",
        ".pytest_cache",
        ".mypy_cache",
        "node_modules",
    }
)


@dataclass(frozen=True)
class FileKind:
    """Describes comment syntax and header requirement for a file kind."""

    name: str
    header_style: str | None  # "hash", "c_block", or None
    line_comment: str | None


KIND_MARKDOWN = FileKind("markdown", None, None)
KIND_RST = FileKind("rst", None, "..")
KIND_PYTHON = FileKind("python", "hash", "#")
KIND_CMAKE = FileKind("cmake", "hash", "#")
KIND_SHELL = FileKind("shell", "hash", "#")
KIND_HASH_DATA = FileKind("hash_data", None, "#")
KIND_C_CPP = FileKind("c_cpp", "c_block", "//")

EXT_MAP: dict[str, FileKind] = {
    ".md": KIND_MARKDOWN,
    ".rst": KIND_RST,
    ".py": KIND_PYTHON,
    ".cmake": KIND_CMAKE,
    ".sh": KIND_SHELL,
    ".yaml": KIND_HASH_DATA,
    ".yml": KIND_HASH_DATA,
    ".toml": KIND_HASH_DATA,
    ".cfg": KIND_HASH_DATA,
    ".c": KIND_C_CPP,
    ".h": KIND_C_CPP,
    ".cc": KIND_C_CPP,
    ".cpp": KIND_C_CPP,
    ".cxx": KIND_C_CPP,
    ".hpp": KIND_C_CPP,
    ".hh": KIND_C_CPP,
    ".hxx": KIND_C_CPP,
}


def detect_file_kind(path: Path) -> FileKind | None:
    """Return the FileKind for `path`, or None if outside checker scope."""
    if path.name == "CMakeLists.txt":
        return KIND_CMAKE
    return EXT_MAP.get(path.suffix.lower())


def _is_excluded(rel_posix: str, extra_excludes: Iterable[str]) -> bool:
    parts = Path(rel_posix).parts
    if any(part in EXCLUDED_DIRS for part in parts):
        return True
    for exc in extra_excludes:
        norm = exc.strip().strip("/")
        if not norm:
            continue
        if rel_posix == norm or rel_posix.startswith(f"{norm}/"):
            return True
    return False


def _git_ls_files(root: Path) -> list[str] | None:
    if not (root / ".git").exists():
        return None
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            check=False,
            capture_output=True,
        )
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    raw = proc.stdout.decode("utf-8", errors="surrogateescape")
    return [entry for entry in raw.split("\0") if entry]


def _walk_files(root: Path, extra_excludes: Iterable[str]) -> list[str]:
    found: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root).as_posix()
        rel_prefix = "" if rel_dir == "." else f"{rel_dir}/"
        kept_dirs: list[str] = []
        for d in sorted(dirnames):
            cand = f"{rel_prefix}{d}"
            if not _is_excluded(cand, extra_excludes):
                kept_dirs.append(d)
        dirnames[:] = kept_dirs
        for fname in sorted(filenames):
            rel = f"{rel_prefix}{fname}"
            if not _is_excluded(rel, extra_excludes):
                found.append(rel)
    return found


def discover_files(
    root: Path,
    editorconfig: EditorConfig,
    *,
    extra_excludes: Iterable[str] = (),
    explicit_paths: list[str] | None = None,
) -> list[tuple[Path, FileKind]]:
    """Discover in-scope files as `(relative_path, FileKind)` pairs."""
    excludes = tuple(extra_excludes)
    candidates: list[str] = []

    if explicit_paths:
        for raw_p in explicit_paths:
            p = Path(raw_p)
            full = p if p.is_absolute() else (root / p)
            if not full.exists():
                raise FileNotFoundError(f"path not found: {raw_p}")
            if full.is_dir():
                for sub in _walk_files(full, excludes):
                    rel = (full / sub).resolve().relative_to(root.resolve())
                    candidates.append(rel.as_posix())
            else:
                rel = full.resolve().relative_to(root.resolve())
                candidates.append(rel.as_posix())
    else:
        tracked = _git_ls_files(root)
        if tracked is not None:
            candidates = [
                c
                for c in tracked
                if not _is_excluded(c, excludes) and (root / c).is_file()
            ]
        else:
            candidates = _walk_files(root, excludes)

    results: list[tuple[Path, FileKind]] = []
    seen: set[str] = set()
    for rel_str in sorted(candidates):
        if rel_str in seen:
            continue
        seen.add(rel_str)
        rel_path = Path(rel_str)
        kind = detect_file_kind(rel_path)
        if kind is None:
            continue
        if editorconfig.max_line_length_for(rel_path) is None:
            continue
        results.append((rel_path, kind))
    return results

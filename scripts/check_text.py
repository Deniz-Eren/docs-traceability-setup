##
# @file     check_text.py
# @brief    Run file-header, line-length, and prose-packing checks on a repo
#
# @copyright
# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>
# MIT License
#

"""Entry point combining header, line-length, and prose-packing checks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from check_headers import check_headers
from check_line_length import check_line_lengths
from editorconfig import EditorConfigError, load_editorconfig
from file_kinds import discover_files
from project_config import ConfigError, load_project_config


def main(argv: list[str] | None = None) -> int:
    """Run all source-text checks and return exit code 0, 1, or 2."""
    parser = argparse.ArgumentParser(
        description=(
            "Check file headers, line lengths, and greedy prose packing."
        )
    )
    parser.add_argument(
        "--root", required=True, help="Path to the target repository root."
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Repair headers and re-pack prose in place before checking.",
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

    hdr_findings, hdr_notices = check_headers(
        root,
        files,
        ec,
        enabled=proj_cfg["checks"]["file_headers"],
        fix=args.fix,
    )
    line_findings = check_line_lengths(
        root,
        files,
        ec,
        prose_packing=proj_cfg["checks"]["prose_packing"],
        fix=args.fix,
    )

    for notice in [*cfg_notices, *ec_notices, *hdr_notices]:
        print(notice, file=sys.stderr)

    all_findings = [*hdr_findings, *line_findings]
    for finding in sorted(
        all_findings, key=lambda f: (f.path.as_posix(), f.line, f.message)
    ):
        print(finding.format())
    return 1 if all_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

##
# @file     test_editorconfig.py
# @brief    Unit tests for editorconfig.py glob matching and [file-header]
#
# @copyright
# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>
# MIT License
#

"""Unit tests for `editorconfig.py`."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from editorconfig import (  # noqa: E402
    EditorConfigError,
    load_editorconfig,
    match_section_glob,
    parse_editorconfig,
)

SAMPLE_EC = """\
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
max_line_length = 80

[*.py]
indent_size = 4

[*.{yaml,yml}]
max_line_length = off

[vendor/**]
max_line_length = off

[docs/*.md]
max_line_length = 72

[file-header]
01 = Copyright (c) 2026 Example Corp
02 =
03 =    /LICENSE.md
"""


class EditorConfigTests(unittest.TestCase):
    """Tests for EditorConfig glob matching, validation, and notices."""

    def test_glob_matching(self) -> None:
        self.assertTrue(match_section_glob("*", "a/b/c.py"))
        self.assertTrue(match_section_glob("*.py", "src/mod.py"))
        self.assertTrue(match_section_glob("*.{yaml,yml}", "ci/build.yml"))
        self.assertFalse(match_section_glob("*.{yaml,yml}", "ci/build.py"))
        self.assertTrue(match_section_glob("vendor/**", "vendor/lib/foo.c"))
        self.assertFalse(match_section_glob("vendor/**", "src/vendor/foo.c"))
        self.assertTrue(match_section_glob("docs/*.md", "docs/index.md"))
        self.assertFalse(match_section_glob("docs/*.md", "docs/sub/index.md"))

    def test_property_precedence_and_indented_file_header(self) -> None:
        ec = parse_editorconfig(SAMPLE_EC)
        self.assertEqual(ec.max_line_length_for("scripts/app.py"), 80)
        self.assertEqual(
            ec.properties_for("scripts/app.py")["indent_size"], "4"
        )
        self.assertIsNone(ec.max_line_length_for("config/ci.yaml"))
        self.assertIsNone(ec.max_line_length_for("vendor/third/a.c"))
        self.assertEqual(ec.max_line_length_for("docs/readme.md"), 72)
        self.assertEqual(
            ec.file_header,
            [
                "Copyright (c) 2026 Example Corp",
                "",
                "   /LICENSE.md",
            ],
        )

    def test_invalid_max_line_length_raises(self) -> None:
        with self.assertRaises(EditorConfigError):
            parse_editorconfig("[*]\nmax_line_length = zero\n")

    def test_invalid_file_header_key_raises(self) -> None:
        with self.assertRaises(EditorConfigError):
            parse_editorconfig("[file-header]\n1 = Bad key\n")

    def test_non_contiguous_file_header_keys_raise(self) -> None:
        with self.assertRaises(EditorConfigError):
            parse_editorconfig("[file-header]\n01 = A\n03 = B\n")

    def test_load_missing_uses_defaults_with_notice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ec, notices = load_editorconfig(Path(tmp))
            self.assertEqual(ec.max_line_length_for("foo.py"), 80)
            self.assertIsNone(ec.max_line_length_for("cfg.yml"))
            self.assertIsNone(ec.file_header)
            self.assertEqual(len(notices), 1)
            self.assertIn("defaults.editorconfig", notices[0])


if __name__ == "__main__":
    unittest.main()

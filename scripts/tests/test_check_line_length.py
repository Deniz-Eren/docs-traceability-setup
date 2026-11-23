##
# @file     test_check_line_length.py
# @brief    Unit tests for check_line_length.py and check_text.py CLI
#
# @copyright
# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>
# MIT License
#

"""Unit tests for `check_line_length.py` and `check_text.py`."""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from check_line_length import check_file_lines  # noqa: E402
from check_text import main as check_text_main  # noqa: E402
from file_kinds import (  # noqa: E402
    KIND_MARKDOWN,
    KIND_PYTHON,
    KIND_RST,
)


class CheckLineLengthTests(unittest.TestCase):
    """Tests for line length limits, greedy packing, and exclusions."""

    def test_81_char_line_fails_80_char_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "doc.md"
            p.write_text("a" * 80 + "\n", encoding="utf-8")
            self.assertEqual(
                check_file_lines(root, Path("doc.md"), KIND_MARKDOWN, 80), []
            )
            p.write_text("a" * 81 + "\n", encoding="utf-8")
            findings = check_file_lines(root, Path("doc.md"), KIND_MARKDOWN, 80)
            self.assertEqual(len(findings), 1)
            self.assertIn("81", findings[0].message)

    def test_unpacked_markdown_fixed_without_touching_protected_blocks(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "spec.md"
            p.write_text(
                "# Title\n"
                "\n"
                "This line is short\n"
                "and should pack onto the previous line cleanly.\n"
                "\n"
                "| Col A | Col B |\n"
                "| --- | --- |\n"
                "| short | val |\n"
                "\n"
                "```python\n"
                "x = 1\n"
                "y = 2\n"
                "```\n"
                "\n"
                "````{swr} Monitor supply\n"
                "---\n"
                "id: SWR_POWER_MONITOR\n"
                "status: active\n"
                "---\n"
                "\n"
                "Short line\n"
                "that packs inside a need directive body.\n"
                "\n"
                "```{swr} Child check\n"
                ":id: SWR_POWER_MONITOR_LOW\n"
                ":status: active\n"
                "\n"
                "Child\n"
                "body.\n"
                "```\n"
                "````\n",
                encoding="utf-8",
            )
            before = check_file_lines(root, Path("spec.md"), KIND_MARKDOWN, 80)
            self.assertEqual(len(before), 3)

            after = check_file_lines(
                root, Path("spec.md"), KIND_MARKDOWN, 80, fix=True
            )
            self.assertEqual(after, [])
            content = p.read_text(encoding="utf-8")
            self.assertIn(
                "This line is short and should pack onto the previous line "
                "cleanly.",
                content,
            )
            self.assertIn(
                "---\nid: SWR_POWER_MONITOR\nstatus: active\n---", content
            )
            self.assertIn("| short | val |", content)
            self.assertIn("```python\nx = 1\ny = 2\n```", content)
            self.assertIn("Child body.", content)

    def test_python_docstrings_preserve_need_tags_and_string_literals(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "mod.py"
            p.write_text(
                "##\n"
                "# @file     mod.py\n"
                "# @brief    Sample module\n"
                "#\n"
                "# @copyright\n"
                "# Copyright (c) 2026 Example\n"
                "#\n"
                "\n"
                '"""Opening line\n'
                "wraps cleanly.\n"
                "\n"
                "# need:: COMP_POWER_MONITOR\n"
                "# need:: ARC_POWER_MONITOR\n"
                '"""\n'
                "\n"
                "# First short comment\n"
                "# line that should pack.\n"
                "def run() -> str:\n"
                '    """\n'
                "    Short docstring\n"
                "    line to pack.\n"
                '    """\n'
                '    raw = """\n'
                "    not a docstring\n"
                "    keep untouched\n"
                '    """\n'
                "    return raw\n",
                encoding="utf-8",
            )
            before = check_file_lines(root, Path("mod.py"), KIND_PYTHON, 80)
            self.assertEqual(len(before), 3)

            after = check_file_lines(
                root, Path("mod.py"), KIND_PYTHON, 80, fix=True
            )
            self.assertEqual(after, [])
            text = p.read_text(encoding="utf-8")
            self.assertIn('"""Opening line wraps cleanly.\n', text)
            self.assertIn(
                "# need:: COMP_POWER_MONITOR\n# need:: ARC_POWER_MONITOR\n",
                text,
            )
            self.assertIn("# First short comment line that should pack.", text)
            self.assertIn("    Short docstring line to pack.", text)
            self.assertIn(
                "    not a docstring\n    keep untouched\n",
                text,
            )

    def test_verbatim_file_header_notice_exempt_in_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "LICENSE.md"
            p.write_text(
                "# License\n\n"
                "Copyright (c) 2026 Example Corp\n"
                "All Rights Reserved.\n",
                encoding="utf-8",
            )
            findings = check_file_lines(
                root,
                Path("LICENSE.md"),
                KIND_MARKDOWN,
                80,
                notice_values=(
                    "Copyright (c) 2026 Example Corp",
                    "All Rights Reserved.",
                ),
            )
            self.assertEqual(findings, [])

    def test_top_of_file_yaml_frontmatter_not_packed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "SKILL.md"
            p.write_text(
                "---\n"
                "name: demo-skill\n"
                "license: MIT\n"
                "---\n\n"
                "# Demo\n\n"
                "Packed paragraph line.\n",
                encoding="utf-8",
            )
            self.assertEqual(
                check_file_lines(root, Path("SKILL.md"), KIND_MARKDOWN, 80), []
            )

    def test_rst_literal_block_not_packed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "doc.rst"
            p.write_text(
                "Heading\n=======\n\nExample::\n\n    short\n    lines\n",
                encoding="utf-8",
            )
            self.assertEqual(
                check_file_lines(root, Path("doc.rst"), KIND_RST, 80), []
            )

    def test_check_text_cli_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".editorconfig").write_text(
                "root = true\n\n"
                "[*]\nmax_line_length = 80\n\n"
                "[file-header]\n01 = Copyright (c) 2026 Test\n",
                encoding="utf-8",
            )
            (root / "ok.py").write_text(
                "##\n"
                "# @file     ok.py\n"
                "# @brief    Valid module\n"
                "#\n"
                "# @copyright\n"
                "# Copyright (c) 2026 Test\n"
                "#\n"
                "\n"
                "x = 1\n",
                encoding="utf-8",
            )
            out = io.StringIO()
            err = io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                rc = check_text_main(["--root", str(root)])
            self.assertEqual(rc, 0, out.getvalue() + err.getvalue())

            # Bad .editorconfig yields exit code 2
            (root / ".editorconfig").write_text(
                "[*]\nmax_line_length = bogus\n", encoding="utf-8"
            )
            with (
                redirect_stdout(io.StringIO()),
                redirect_stderr(io.StringIO()),
            ):
                rc_bad = check_text_main(["--root", str(root)])
            self.assertEqual(rc_bad, 2)


if __name__ == "__main__":
    unittest.main()

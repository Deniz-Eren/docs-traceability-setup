##
# @file     test_check_headers.py
# @brief    Unit tests for check_headers.py Doxygen header checks and fixes
#
# @copyright
# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>
# MIT License
#

"""Unit tests for `check_headers.py`."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from check_headers import check_file_header, check_headers  # noqa: E402
from editorconfig import parse_editorconfig  # noqa: E402
from file_kinds import (  # noqa: E402
    KIND_C_CPP,
    KIND_MARKDOWN,
    KIND_PYTHON,
    KIND_SHELL,
)

NOTICE = [
    "Copyright (c) 2026 Example Corp",
    "",
    "   /LICENSE.md",
]


class CheckHeadersTests(unittest.TestCase):
    """Tests for Doxygen file header verification and `--fix` behavior."""

    def test_valid_python_header_with_details_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "mod.py"
            p.write_text(
                "##\n"
                "# @file     mod.py\n"
                "# @brief    Implement sample logic\n"
                "#\n"
                "# @details  Verbose file-level comment.\n"
                "#\n"
                "# @copyright\n"
                "# Copyright (c) 2026 Example Corp\n"
                "#\n"
                "#    /LICENSE.md\n"
                "#\n"
                "\n"
                "x = 1\n",
                encoding="utf-8",
            )
            findings = check_file_header(
                root, Path("mod.py"), KIND_PYTHON, NOTICE
            )
            self.assertEqual(findings, [])

    def test_valid_shebang_and_c_header_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sh = root / "run.sh"
            sh.write_text(
                "#!/usr/bin/env bash\n"
                "##\n"
                "# @file     run.sh\n"
                "# @brief    Run sample build\n"
                "#\n"
                "# @copyright\n"
                "# Copyright (c) 2026 Example Corp\n"
                "#\n"
                "#    /LICENSE.md\n"
                "#\n"
                "\n"
                "echo ok\n",
                encoding="utf-8",
            )
            cfile = root / "main.c"
            cfile.write_text(
                "/**\n"
                " * @file     main.c\n"
                " * @brief    Entry point for sample program\n"
                " *\n"
                " * @copyright\n"
                " * Copyright (c) 2026 Example Corp\n"
                " *\n"
                " *    /LICENSE.md\n"
                " *\n"
                " */\n"
                "\n"
                "int main(void) { return 0; }\n",
                encoding="utf-8",
            )
            self.assertEqual(
                check_file_header(root, Path("run.sh"), KIND_SHELL, NOTICE), []
            )
            self.assertEqual(
                check_file_header(root, Path("main.c"), KIND_C_CPP, NOTICE), []
            )

    def test_missing_header_fix_adds_todo_and_still_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "tool.py"
            p.write_text(
                "#!/usr/bin/env python3\nprint('hi')\n", encoding="utf-8"
            )
            findings = check_file_header(
                root, Path("tool.py"), KIND_PYTHON, NOTICE, fix=True
            )
            self.assertEqual(len(findings), 1)
            self.assertIn("@brief", findings[0].message)
            updated = p.read_text(encoding="utf-8")
            self.assertTrue(updated.startswith("#!/usr/bin/env python3\n##\n"))
            self.assertIn("# @file     tool.py", updated)
            self.assertIn("# @brief    TODO", updated)
            self.assertIn("# @copyright\n# Copyright (c) 2026", updated)
            self.assertIn("#    /LICENSE.md\n#\n\nprint", updated)

    def test_wrong_copyright_is_repaired_keeping_brief_and_details(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "app.py"
            p.write_text(
                "##\n"
                "# @file     app.py\n"
                "# @brief    Run application loop\n"
                "#\n"
                "# @details  Extra file note.\n"
                "#\n"
                "# @copyright\n"
                "# Old Notice\n"
                "#\n"
                "\n"
                "pass\n",
                encoding="utf-8",
            )
            findings = check_file_header(
                root, Path("app.py"), KIND_PYTHON, NOTICE, fix=True
            )
            self.assertEqual(findings, [])
            content = p.read_text(encoding="utf-8")
            self.assertIn("# @brief    Run application loop", content)
            self.assertIn("# @details  Extra file note.", content)
            self.assertIn("#    /LICENSE.md", content)

    def test_brief_period_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "bad.py"
            p.write_text(
                "##\n"
                "# @file     bad.py\n"
                "# @brief    Has a trailing period.\n"
                "#\n"
                "# @copyright\n"
                "# Copyright (c) 2026 Example Corp\n"
                "#\n"
                "#    /LICENSE.md\n"
                "#\n"
                "\n"
                "pass\n",
                encoding="utf-8",
            )
            findings = check_file_header(
                root, Path("bad.py"), KIND_PYTHON, NOTICE
            )
            self.assertTrue(
                any("period" in f.message for f in findings), findings
            )

    def test_markdown_and_missing_section_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "doc.md").write_text("# Title\n", encoding="utf-8")
            ec = parse_editorconfig("[*]\nmax_line_length = 80\n")
            findings, notices = check_headers(
                root, [(Path("doc.md"), KIND_MARKDOWN)], ec, enabled=True
            )
            self.assertEqual(findings, [])
            self.assertEqual(len(notices), 1)


if __name__ == "__main__":
    unittest.main()

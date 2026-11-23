##
# @file     test_project_config.py
# @brief    Unit tests for project_config.py YAML parsing and validation
#
# @copyright
# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>
# MIT License
#

"""Unit tests for `project_config.py`."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from project_config import (  # noqa: E402
    CONFIG_FILENAME,
    ConfigError,
    load_project_config,
    parse_simple_yaml,
    validate_config,
)

VALID_SLUG_YAML = """\
project:
  name: "demo"
  repo_url: "https://example.com/demo"
  domains:
    - POWER
    - COMM

id:
  style: slug

authoring:
  primary_markup: myst
  modal_verb: shall

model:
  decision_types:
    - adr
    - bdr
    - wdr
  ver_method_tags:
    - unit
    - integration
  test_file_patterns:
    - "test_*"
    - "*_test.*"
  code_tag_exclude: []

build:
  cmake_mode: subdirectory
  python_manifest: requirements.txt
  docs_auto_install: false
  graphviz: auto

checks:
  file_headers: true
  prose_packing: true
"""


class ProjectConfigTests(unittest.TestCase):
    """Tests for `.docs-traceability-setup.yml` loading and validation."""

    def test_valid_slug_config(self) -> None:
        parsed = parse_simple_yaml(VALID_SLUG_YAML)
        cfg = validate_config(parsed)
        self.assertEqual(cfg["project"]["name"], "demo")
        self.assertEqual(cfg["project"]["domains"], ["POWER", "COMM"])
        self.assertEqual(cfg["id"]["style"], "slug")
        self.assertNotIn("digits", cfg["id"])
        self.assertEqual(cfg["model"]["code_tag_exclude"], [])
        self.assertFalse(cfg["build"]["docs_auto_install"])

    def test_valid_number_config(self) -> None:
        text = VALID_SLUG_YAML.replace(
            "style: slug", "style: number\n  digits: 4"
        )
        cfg = validate_config(parse_simple_yaml(text))
        self.assertEqual(cfg["id"]["style"], "number")
        self.assertEqual(cfg["id"]["digits"], 4)

    def test_number_style_requires_digits(self) -> None:
        text = VALID_SLUG_YAML.replace("style: slug", "style: number")
        with self.assertRaises(ConfigError):
            validate_config(parse_simple_yaml(text))

    def test_unknown_key_raises(self) -> None:
        text = VALID_SLUG_YAML + "  extra_flag: true\n"
        with self.assertRaises(ConfigError):
            validate_config(parse_simple_yaml(text))

    def test_unknown_section_raises(self) -> None:
        text = VALID_SLUG_YAML + "\nextra:\n  foo: bar\n"
        with self.assertRaises(ConfigError):
            validate_config(parse_simple_yaml(text))

    def test_invalid_domain_raises(self) -> None:
        text = VALID_SLUG_YAML.replace("- POWER", "- bad_domain")
        with self.assertRaises(ConfigError):
            validate_config(parse_simple_yaml(text))

    def test_invalid_enum_values_raise(self) -> None:
        for old, new in [
            ("style: slug", "style: uuid"),
            ("primary_markup: myst", "primary_markup: asciidoc"),
            ("cmake_mode: subdirectory", "cmake_mode: ninja"),
            ("graphviz: auto", "graphviz: always"),
            ("- adr", "- dec"),
        ]:
            with self.subTest(replacement=new):
                with self.assertRaises(ConfigError):
                    validate_config(
                        parse_simple_yaml(VALID_SLUG_YAML.replace(old, new))
                    )

    def test_load_missing_allow_missing_returns_notice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg, notices = load_project_config(Path(tmp), allow_missing=True)
            self.assertEqual(cfg["id"]["style"], "slug")
            self.assertEqual(len(notices), 1)
            self.assertIn(CONFIG_FILENAME, notices[0])

    def test_load_invalid_file_does_not_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / CONFIG_FILENAME).write_text("bad_section:\n  a: 1\n")
            with self.assertRaises(ConfigError):
                load_project_config(root, allow_missing=True)


if __name__ == "__main__":
    unittest.main()

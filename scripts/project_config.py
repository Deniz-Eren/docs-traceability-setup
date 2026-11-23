##
# @file     project_config.py
# @brief    Read and validate .docs-traceability-setup.yml with stdlib only
#
# @copyright
# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>
# MIT License
#

"""Reader and validator for `.docs-traceability-setup.yml`."""

from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any

CONFIG_FILENAME = ".docs-traceability-setup.yml"
DOMAIN_RE = re.compile(r"^[A-Z0-9]+$")
VALID_DECISION_TYPES = frozenset({"adr", "bdr", "wdr"})
VALID_ID_STYLES = frozenset({"slug", "number"})
VALID_MARKUPS = frozenset({"myst", "rst"})
VALID_CMAKE_MODES = frozenset({"subdirectory", "standalone"})
VALID_GRAPHVIZ_MODES = frozenset({"auto", "on", "off"})

DEFAULT_CONFIG: dict[str, Any] = {
    "project": {
        "name": "example",
        "repo_url": "",
        "domains": ["POWER"],
    },
    "id": {
        "style": "slug",
        "digits": 4,
    },
    "authoring": {
        "primary_markup": "myst",
        "modal_verb": "shall",
    },
    "model": {
        "decision_types": ["adr", "bdr", "wdr"],
        "ver_method_tags": ["unit", "integration", "network", "analysis"],
        "test_file_patterns": ["test_*", "*_test.*", "check_*"],
        "code_tag_exclude": [],
    },
    "build": {
        "cmake_mode": "subdirectory",
        "python_manifest": "requirements.txt",
        "docs_auto_install": False,
        "graphviz": "auto",
    },
    "checks": {
        "file_headers": True,
        "prose_packing": True,
    },
}

SCHEMA_KEYS: dict[str, frozenset[str]] = {
    "project": frozenset({"name", "repo_url", "domains"}),
    "id": frozenset({"style", "digits"}),
    "authoring": frozenset({"primary_markup", "modal_verb"}),
    "model": frozenset(
        {
            "decision_types",
            "ver_method_tags",
            "test_file_patterns",
            "code_tag_exclude",
        }
    ),
    "build": frozenset(
        {
            "cmake_mode",
            "python_manifest",
            "docs_auto_install",
            "graphviz",
        }
    ),
    "checks": frozenset({"file_headers", "prose_packing"}),
}


class ConfigError(ValueError):
    """Raised when `.docs-traceability-setup.yml` is invalid."""


def _strip_comment(raw: str) -> str:
    in_single = False
    in_double = False
    escaped = False
    for idx, ch in enumerate(raw):
        if escaped:
            escaped = False
            continue
        if ch == "\\" and in_double:
            escaped = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            if idx == 0 or raw[idx - 1].isspace():
                return raw[:idx].rstrip()
    return raw.rstrip()


def _parse_scalar(text: str, line_no: int) -> Any:
    val = text.strip()
    if val == "":
        return ""
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner:
            return []
        items: list[Any] = []
        buf: list[str] = []
        in_single = False
        in_double = False
        for ch in inner:
            if ch == "'" and not in_double:
                in_single = not in_single
                buf.append(ch)
            elif ch == '"' and not in_single:
                in_double = not in_double
                buf.append(ch)
            elif ch == "," and not in_single and not in_double:
                items.append(_parse_scalar("".join(buf), line_no))
                buf = []
            else:
                buf.append(ch)
        if in_single or in_double:
            raise ConfigError(f"line {line_no}: unterminated quote in list")
        items.append(_parse_scalar("".join(buf), line_no))
        return items
    if (val.startswith('"') and val.endswith('"')) or (
        val.startswith("'") and val.endswith("'")
    ):
        if len(val) < 2:
            raise ConfigError(f"line {line_no}: unterminated string")
        quote = val[0]
        body = val[1:-1]
        if quote == '"':
            return body.replace('\\"', '"').replace("\\\\", "\\")
        return body.replace("''", "'")
    if val.startswith('"') or val.startswith("'"):
        raise ConfigError(f"line {line_no}: unterminated string")
    if val == "true":
        return True
    if val == "false":
        return False
    if re.fullmatch(r"-?[0-9]+", val):
        return int(val)
    return val


def parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse the two-level YAML subset used by configuration files."""
    data: dict[str, Any] = {}
    current_section: str | None = None
    current_list_key: tuple[str, str] | None = None
    list_indent: int | None = None

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        cleaned = _strip_comment(raw_line)
        if not cleaned.strip():
            continue
        if "\t" in cleaned[: len(cleaned) - len(cleaned.lstrip(" \t"))]:
            raise ConfigError(
                f"line {line_no}: tabs are not allowed for indentation"
            )
        indent = len(cleaned) - len(cleaned.lstrip(" "))
        stripped = cleaned.lstrip(" ")

        if indent == 0:
            current_list_key = None
            list_indent = None
            if ":" not in stripped:
                raise ConfigError(f"line {line_no}: expected 'section:'")
            key, _, rest = stripped.partition(":")
            key = key.strip()
            rest = rest.strip()
            if not key:
                raise ConfigError(f"line {line_no}: empty top-level key")
            if rest:
                raise ConfigError(
                    f"line {line_no}: top-level key '{key}' must be a mapping"
                )
            if key in data:
                raise ConfigError(f"line {line_no}: duplicate section '{key}'")
            data[key] = {}
            current_section = key
            continue

        if current_section is None:
            raise ConfigError(f"line {line_no}: indented content before key")

        if stripped.startswith("- "):
            if current_list_key is None:
                raise ConfigError(
                    f"line {line_no}: list item without preceding key"
                )
            if list_indent is None:
                list_indent = indent
            elif indent != list_indent:
                raise ConfigError(
                    f"line {line_no}: inconsistent list indentation"
                )
            sec, k = current_list_key
            item_val = _parse_scalar(stripped[2:], line_no)
            data[sec][k].append(item_val)
            continue

        if stripped == "-":
            raise ConfigError(f"line {line_no}: empty list item is not allowed")

        if indent != 2:
            raise ConfigError(
                f"line {line_no}: expected 2-space indentation for section keys"
            )

        current_list_key = None
        list_indent = None
        if ":" not in stripped:
            raise ConfigError(f"line {line_no}: expected 'key: value'")
        key, _, rest = stripped.partition(":")
        key = key.strip()
        rest = rest.strip()
        if not key:
            raise ConfigError(f"line {line_no}: empty key")
        if key in data[current_section]:
            raise ConfigError(
                f"line {line_no}: duplicate key '{current_section}.{key}'"
            )
        if rest == "":
            data[current_section][key] = []
            current_list_key = (current_section, key)
        else:
            data[current_section][key] = _parse_scalar(rest, line_no)

    return data


def _require_str(
    mapping: dict[str, Any], key: str, section: str, *, allow_empty: bool
) -> str:
    if key not in mapping:
        raise ConfigError(f"missing required key '{section}.{key}'")
    val = mapping[key]
    if not isinstance(val, str):
        raise ConfigError(f"'{section}.{key}' must be a string")
    if not allow_empty and not val.strip():
        raise ConfigError(f"'{section}.{key}' must not be empty")
    return val


def _require_bool(mapping: dict[str, Any], key: str, section: str) -> bool:
    if key not in mapping:
        raise ConfigError(f"missing required key '{section}.{key}'")
    val = mapping[key]
    if not isinstance(val, bool):
        raise ConfigError(f"'{section}.{key}' must be a boolean")
    return val


def _require_str_list(
    mapping: dict[str, Any], key: str, section: str, *, allow_empty: bool
) -> list[str]:
    if key not in mapping:
        raise ConfigError(f"missing required key '{section}.{key}'")
    val = mapping[key]
    if not isinstance(val, list) or not all(isinstance(x, str) for x in val):
        raise ConfigError(f"'{section}.{key}' must be a list of strings")
    if not allow_empty and not val:
        raise ConfigError(f"'{section}.{key}' must not be empty")
    if any(not x.strip() for x in val):
        raise ConfigError(
            f"'{section}.{key}' must not contain empty string items"
        )
    return list(val)


def validate_config(raw: dict[str, Any]) -> dict[str, Any]:
    """Validate parsed configuration dictionary against the strict schema."""
    if not isinstance(raw, dict):
        raise ConfigError("configuration root must be a mapping")

    unknown_sections = set(raw.keys()) - set(SCHEMA_KEYS.keys())
    if unknown_sections:
        names = ", ".join(sorted(unknown_sections))
        raise ConfigError(f"unknown configuration section(s): {names}")

    missing_sections = set(SCHEMA_KEYS.keys()) - set(raw.keys())
    if missing_sections:
        names = ", ".join(sorted(missing_sections))
        raise ConfigError(f"missing required section(s): {names}")

    for section, allowed_keys in SCHEMA_KEYS.items():
        if not isinstance(raw[section], dict):
            raise ConfigError(f"section '{section}' must be a mapping")
        unknown_keys = set(raw[section].keys()) - allowed_keys
        if unknown_keys:
            names = ", ".join(sorted(f"{section}.{k}" for k in unknown_keys))
            raise ConfigError(f"unknown configuration key(s): {names}")

    project = raw["project"]
    proj_name = _require_str(project, "name", "project", allow_empty=False)
    repo_url = _require_str(project, "repo_url", "project", allow_empty=True)
    domains = _require_str_list(
        project, "domains", "project", allow_empty=False
    )
    for dom in domains:
        if not DOMAIN_RE.fullmatch(dom):
            raise ConfigError(
                f"invalid domain '{dom}' in 'project.domains': "
                "must match [A-Z0-9]+"
            )

    id_cfg = raw["id"]
    id_style = _require_str(id_cfg, "style", "id", allow_empty=False)
    if id_style not in VALID_ID_STYLES:
        raise ConfigError(
            f"invalid 'id.style': '{id_style}' (expected 'slug' or 'number')"
        )
    id_digits = id_cfg.get("digits")
    if id_style == "number":
        if (
            id_digits is None
            or isinstance(id_digits, bool)
            or not isinstance(id_digits, int)
            or id_digits < 1
        ):
            raise ConfigError(
                "'id.digits' must be a positive integer when id.style is "
                "'number'"
            )
    elif id_digits is not None:
        if (
            isinstance(id_digits, bool)
            or not isinstance(id_digits, int)
            or id_digits < 1
        ):
            raise ConfigError("'id.digits' must be a positive integer")

    authoring = raw["authoring"]
    primary_markup = _require_str(
        authoring, "primary_markup", "authoring", allow_empty=False
    )
    if primary_markup not in VALID_MARKUPS:
        raise ConfigError(
            f"invalid 'authoring.primary_markup': '{primary_markup}'"
        )
    modal_verb = _require_str(
        authoring, "modal_verb", "authoring", allow_empty=False
    )

    model = raw["model"]
    decision_types = _require_str_list(
        model, "decision_types", "model", allow_empty=True
    )
    bad_dec = [d for d in decision_types if d not in VALID_DECISION_TYPES]
    if bad_dec:
        raise ConfigError(
            f"invalid 'model.decision_types' value(s): {', '.join(bad_dec)}"
        )
    ver_method_tags = _require_str_list(
        model, "ver_method_tags", "model", allow_empty=False
    )
    test_file_patterns = _require_str_list(
        model, "test_file_patterns", "model", allow_empty=False
    )
    code_tag_exclude = _require_str_list(
        model, "code_tag_exclude", "model", allow_empty=True
    )

    build = raw["build"]
    cmake_mode = _require_str(build, "cmake_mode", "build", allow_empty=False)
    if cmake_mode not in VALID_CMAKE_MODES:
        raise ConfigError(f"invalid 'build.cmake_mode': '{cmake_mode}'")
    python_manifest = _require_str(
        build, "python_manifest", "build", allow_empty=False
    )
    docs_auto_install = _require_bool(build, "docs_auto_install", "build")
    graphviz = _require_str(build, "graphviz", "build", allow_empty=False)
    if graphviz not in VALID_GRAPHVIZ_MODES:
        raise ConfigError(f"invalid 'build.graphviz': '{graphviz}'")

    checks = raw["checks"]
    file_headers = _require_bool(checks, "file_headers", "checks")
    prose_packing = _require_bool(checks, "prose_packing", "checks")

    result: dict[str, Any] = {
        "project": {
            "name": proj_name,
            "repo_url": repo_url,
            "domains": domains,
        },
        "id": {
            "style": id_style,
        },
        "authoring": {
            "primary_markup": primary_markup,
            "modal_verb": modal_verb,
        },
        "model": {
            "decision_types": decision_types,
            "ver_method_tags": ver_method_tags,
            "test_file_patterns": test_file_patterns,
            "code_tag_exclude": code_tag_exclude,
        },
        "build": {
            "cmake_mode": cmake_mode,
            "python_manifest": python_manifest,
            "docs_auto_install": docs_auto_install,
            "graphviz": graphviz,
        },
        "checks": {
            "file_headers": file_headers,
            "prose_packing": prose_packing,
        },
    }
    if id_digits is not None:
        result["id"]["digits"] = id_digits
    return result


def load_project_config(
    root: Path, *, allow_missing: bool = False
) -> tuple[dict[str, Any], list[str]]:
    """Load and validate `.docs-traceability-setup.yml` from `root`."""
    config_path = root / CONFIG_FILENAME
    if not config_path.is_file():
        if allow_missing:
            notice = (
                f"notice: {CONFIG_FILENAME} not found in {root}; "
                "using default check settings"
            )
            return copy.deepcopy(DEFAULT_CONFIG), [notice]
        raise ConfigError(f"configuration file not found: {config_path}")

    text = config_path.read_text(encoding="utf-8")
    parsed = parse_simple_yaml(text)
    validated = validate_config(parsed)
    return validated, []

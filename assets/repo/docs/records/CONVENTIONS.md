# Conventions

## Purpose

Record the active engineering conventions (`con`) of `{{PROJECT_NAME}}`.

## Structure

Each convention appears under a `### CNV_<SUFFIX> — Title` heading followed by
one `{con}` directive tracing the decision that established it.

## Formatting Rules

- Update each convention in place so it always reflects current practice.
- Mark retired conventions with `:status: obsolete`.
- Never reuse or rename an assigned ID.

```{needtable} All conventions
:types: con
:columns: id; title; status; traces as "Traces to"; traces_back as "Traced by"
```

### {{CNV_CODE_TAGS_ID}} — In-Code Traceability Tags

```{con} In-code traceability tags
:id: {{CNV_CODE_TAGS_ID}}
:status: active
:traces: {{ADR_SPHINX_NEEDS_ID}}

Use comment lines starting with `need:: <ID>` near related code or inside the
module docstring. Implementation code links only `ARC_`, `ICD_`, or `COMP_` IDs;
test files link `VER_` IDs.
```

### {{CNV_SOURCE_TEXT_ID}} — Source Text Conventions

```{con} Source text conventions
:id: {{CNV_SOURCE_TEXT_ID}}
:status: active
:traces: {{ADR_SPHINX_NEEDS_ID}}

Wrap source and documentation files to the column limit configured in
`.editorconfig` and pack prose paragraphs greedily as validated by the
`docs-traceability-setup` skill.
```

### {{CNV_FILE_HEADER_ID}} — File Header Blocks

```{con} File header blocks
:id: {{CNV_FILE_HEADER_ID}}
:status: active
:traces: {{ADR_SPHINX_NEEDS_ID}}

Start every human-authored Python, CMake, shell, and C/C++ file with a Doxygen
header block carrying `@file`, `@brief`, and `@copyright` matching the
`[file-header]` section of `.editorconfig`.
```

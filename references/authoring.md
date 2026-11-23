# Authoring Rules

## Markup and Directive Fences

- `authoring.primary_markup` (`myst` default, or `rst`) in
  `.docs-traceability-setup.yml` sets the primary markup.
- In MyST, write need directives with backtick fences. Use three backticks for
  atomic items and four backticks on a parent item that encloses nested child
  items. For long option values (such as multi-line `:traces:` lists), MyST YAML
  frontmatter option blocks (`---` ... `---`) directly inside the opening fence
  are also supported.
- In `needtable` directives:
  - Keep the uniform default **DataTables style** (`NEEDS_DATATABLES`, with
    search, paging, column visibility, copy, and CSV controls) by omitting
    `:style: table`.
  - Provide a descriptive table caption on the opening directive line (for
    example ```` ```{needtable} All conventions ````).
  - Separate columns with `;` and alias column headers with `as "Label"` (for
    example `:columns: id; title; status; traces as "Traces to"; traces_back as
    "Traced by"`).
- In RST, write standard `.. <type>:: Title` directives with indented fields and
  nested child directives.

## Item Document Template

Every domain specification document (`20-system/<domain>.md`,
`30-architecture/<domain>.md`, `40-interfaces/<domain>.md`,
`50-components/<domain>.md`, `60-verification/<domain>.md`) follows this
structure:

```markdown
# <Kind> — <Topic>

Domain `<DOMAIN>`: <scope in one sentence>.

```{swr} Short imperative title
:id: SWR_<DOMAIN>_<SUFFIX>
:status: active
:derives: SYS_<DOMAIN>_<SUFFIX>

The system shall <single testable obligation>.
```
```

## Writing Requirements and Cross-References

- **Modal verb:** Use the single modal verb configured in
  `authoring.modal_verb` (default `shall`) for all normative obligations. When
  you migrate a current project, keep its established modal verb.
- **Atomicity:** State one clear obligation per requirement item. Split
  multi-obligation requirements into a compound parent with atomic child items.
- **Prose links to needs:** Refer to items in natural prose followed by their
  linked ID in parentheses, for example:
  ``the supply monitor ({need}`SWR_POWER_MONITOR`)`` (or
  ``{need}`SWR_POWER_0001` `` in 4-digit `number` mode).
- **Role template:** Configure `needs_role_need_template = "{{ id }}"` in
  `conf.py` (Jinja syntax, not the deprecated `{id}` format).
- **Page references:** Always link documentation pages with hyperlinks instead
  of plain-text paths.
- **Verification bodies:** Each `ver` item body names the automated test file
  and test function/class or the analysis procedure that verifies the
  requirement.

## In-Code Traceability Tags

- **Syntax:** Place `need:: <ID> [<ID> ...]` immediately after the file's
  comment marker:
  - C/C++, Rust, Go, JS/TS, Java: `// need:: COMP_POWER_MONITOR`,
    `/* need:: COMP_POWER_MONITOR */`, or `/** \req{COMP_POWER_MONITOR} */`
  - Python, shell, CMake, YAML, `.editorconfig`: `# need:: COMP_POWER_MONITOR`
  - SQL, Lua, VHDL, Ada: `-- need:: COMP_POWER_MONITOR`
  - reStructuredText: `.. need:: COMP_POWER_MONITOR`
- **Placement:** Use one tag line per association near the implementing symbol
  or in the module docstring. Do not put `need::` tags in the Doxygen file
  header block.
- **Allowed IDs in implementation code:** Reference only the lowest-level
  design specification (`ARC_`, `ICD_`, or `COMP_`).
- **Forbidden IDs in code:** Do not put `SYS_`, `SWR_`, `ADR_`, `BDR_`, `WDR_`,
  `CNV_`, `TSK_`, or `RDM_` IDs in source or test code.
- **Test files (`model.test_file_patterns`):**
  - Use `VER_` IDs **only** in test files (for example `test_*`, `*_test.*`,
    `check_*`).
  - Each test file must contain at least one `VER_` ID.
  - Record requirement links one time in `:verifies:` on the `ver` item, not in
    test code comments.

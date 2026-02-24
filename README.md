# AgentChanti Global KB Registry

The **AgentChanti Global Knowledge Base Registry** is a structured content repository containing curated knowledge files consumed by the AgentChanti coding assistant. This is a **content repository** — not a code repository. All files here are knowledge artifacts: error dictionaries, coding patterns, architectural decision records, reference documentation, and behavioral instructions that shape how AgentChanti reasons about code.

---

## Directory Structure

```
agentchanti-kb-registry/
├── .github/
│   └── workflows/
│       ├── validate.yml        # PR validation (frontmatter, IDs, schema)
│       ├── release.yml         # Auto-versioning and release packaging
│       └── index-check.yml     # Content quality checks
├── scripts/
│   ├── validate.py             # Validation logic for CI
│   ├── bump_version.py         # Semver bumping from PR labels
│   ├── build_release.py        # Zip packaging for releases
│   └── index_check.py          # Content quality analysis
├── errors/                     # Error dictionaries per language/framework
│   ├── python/
│   │   ├── builtin.yml
│   │   ├── async.yml
│   │   └── frameworks/
│   │       ├── django.yml
│   │       └── fastapi.yml
│   ├── javascript/
│   │   ├── builtin.yml
│   │   └── frameworks/
│   │       ├── react.yml
│   │       └── node.yml
│   ├── typescript/
│   │   └── builtin.yml
│   ├── java/
│   │   ├── builtin.yml
│   │   └── frameworks/
│   │       └── spring.yml
│   ├── go/
│   │   └── builtin.yml
│   ├── rust/
│   │   └── builtin.yml
│   └── csharp/
│       ├── builtin.yml
│       └── frameworks/
│           └── dotnet.yml
├── patterns/                   # Coding patterns and best practices
│   ├── general/
│   ├── python/
│   ├── javascript/
│   ├── typescript/
│   ├── frameworks/
│   └── domains/
├── adrs/                       # Architectural Decision Records
├── docs/                       # Reference documentation
│   ├── tools/
│   ├── languages/
│   └── frameworks/
├── behavioral/                 # LLM behavioral instructions (injected per call)
│   ├── general/
│   ├── domains/
│   └── languages/
├── manifest.json               # Registry version and category counts
├── PULL_REQUEST_TEMPLATE.md
└── README.md
```

---

## How to Add New Content

### 1. Choose the Right Category

| Category | Purpose | Format |
|---|---|---|
| `errors/` | Error message dictionaries with patterns and fixes | `.yml` |
| `patterns/` | Reusable coding patterns and best practices | `.md` |
| `adrs/` | Architectural decisions for AgentChanti's own design | `.md` |
| `docs/` | Reference guides for tools, languages, frameworks | `.md` |
| `behavioral/` | Behavioral instructions injected into LLM calls | `.md` |

### 2. Follow the Frontmatter Schema (for .md files)

Every `.md` file must begin with valid YAML frontmatter:

```yaml
---
id: "unique-id-here"          # Required. Unique across entire registry. Format: {prefix}-{number}
title: "Human Readable Title"  # Required.
category: "pattern"            # Required. One of: pattern | adr | doc | behavioral | error
language: "python"             # Required. One of: all | python | javascript | typescript | java | go | rust | csharp
version: "1.0.0"               # Required. Semver format X.Y.Z
created_at: "2026-02-24"       # Required. ISO date YYYY-MM-DD
tags:                          # Optional but recommended.
  - tag1
  - tag2
---
```

### 3. Follow the Error Entry Schema (for .yml files)

Each entry in an error `.yml` file must conform to:

```yaml
- id: "py-attr-001"                    # Required. Unique across all error entries.
  error_type: "AttributeError"          # Required. The exception/error class name.
  severity: "warning"                   # Required. One of: critical | warning | info
  pattern: "'(.+)' object has no attribute '(.+)'"  # Required. Regex matching the error message.
  cause: "Explanation of what causes this error."   # Required.
  fix_template: |                        # Required. Non-empty. Include code examples.
    # How to fix:
    # Check that the attribute exists before accessing it
    if hasattr(obj, 'attribute_name'):
        obj.attribute_name
  tags:                                  # Required. At least one tag.
    - attribute
    - runtime
  related_errors:                        # Optional. Must reference existing IDs.
    - py-type-001
```

### 4. ID Naming Conventions

- **Error IDs**: `{lang-abbrev}-{error-abbrev}-{number}` → e.g., `py-attr-001`, `js-ref-002`
- **Pattern IDs**: `{scope}-pattern-{number}` → e.g., `py-pattern-001`, `gen-pattern-002`
- **ADR IDs**: `adr-{number}` → e.g., `adr-001`
- **Doc IDs**: `doc-{number}` → e.g., `doc-001`
- **Behavioral IDs**: `beh-{number}` → e.g., `beh-001`

### 5. Open a Pull Request

Use the PR template (`.github/PULL_REQUEST_TEMPLATE.md`). CI will run:
- **validate.yml** — checks frontmatter, IDs, schema validity
- **index-check.yml** — checks content quality (word count, YAML validity, coverage)

---

## How Versioning Works

Versioning follows **semantic versioning** (semver: `MAJOR.MINOR.PATCH`).

- Versions are stored in `manifest.json` at the root.
- CI **auto-bumps** the version on every merge to `main` via `scripts/bump_version.py`.
- The bump type is determined by PR labels:
  - Label `bump:major` → increments `MAJOR` (breaking schema changes)
  - Label `bump:minor` → increments `MINOR` (new files/categories added)
  - Label `bump:patch` → increments `PATCH` (content corrections, new error entries)
  - No label → defaults to `patch`
- A GitHub Release is automatically created with a zip artifact.

---

## How AgentChanti Pulls Updates

AgentChanti pulls the latest KB release using:

```bash
agentchanti kb update
```

This command:
1. Fetches `manifest.json` from the latest GitHub Release tag.
2. Compares versions with the locally cached version.
3. If newer, downloads `kb-registry-v{version}.zip` from the release assets.
4. Extracts to the local KB cache directory (`~/.agentchanti/kb/`).
5. Reloads error dictionaries, pattern indexes, behavioral instructions into memory.

You can force a specific version:

```bash
agentchanti kb update --version 1.2.0
```

Or check the current version:

```bash
agentchanti kb version
```

---

## Contributing Guide

1. Fork the repository.
2. Create a branch: `git checkout -b add/py-error-sqlalchemy`
3. Add your content following the schemas above.
4. Run validation locally: `python scripts/validate.py`
5. Run index check: `python scripts/index_check.py`
6. Open a PR with the provided template.
7. Address any CI failures — the bot will comment with specific issues.
8. Once approved and merged, the version auto-bumps and a release is created.

**Quality bar:** All content must be production-ready. No placeholder text. Error patterns must match real error messages. Fix templates must contain working code examples. Behavioral instructions must be specific and actionable.

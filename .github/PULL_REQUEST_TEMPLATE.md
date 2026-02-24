# Pull Request

## Content Description

Brief description of what this PR adds or changes:

---

## Checklist

### Content Type
- [ ] `error` — New or updated error entries in `errors/`
- [ ] `pattern` — New or updated coding pattern in `patterns/`
- [ ] `adr` — New or updated architectural decision record in `adrs/`
- [ ] `doc` — New or updated reference documentation in `docs/`
- [ ] `behavioral` — New or updated behavioral instruction in `behavioral/`

### Scope
- [ ] Language/framework scope identified: _(specify: e.g., Python, React, Go)_
- [ ] Content applies to the scope listed in frontmatter `language` field

### ID Validation
- [ ] All new IDs are unique — checked against existing IDs in the registry
- [ ] ID follows naming convention: `{prefix}-{category}-{number}` for .md, `{lang}-{type}-{number}` for error entries
- [ ] No ID reuses an existing ID (run `python scripts/validate.py` to confirm)

### Schema Compliance
- [ ] All `.md` files have complete frontmatter: `id`, `title`, `category`, `language`, `version`, `created_at`
- [ ] All `.yml` error files have required fields per entry: `id`, `error_type`, `severity`, `pattern`, `fix_template`, `tags`
- [ ] `severity` values are only `critical`, `warning`, or `info`
- [ ] `category` values are only `pattern`, `adr`, `doc`, `behavioral`, or `error`
- [ ] `language` values are only `all`, `python`, `javascript`, `typescript`, `java`, `go`, `rust`, or `csharp`
- [ ] `version` follows semver format `X.Y.Z`
- [ ] All `related_errors` references in `.yml` files point to existing IDs

### Content Quality
- [ ] Fix templates include actual working code examples (for error entries)
- [ ] No placeholder or lorem ipsum text — all content is production-ready
- [ ] `.md` files have at least one `##` heading section
- [ ] Error `pattern` fields are valid regex that match real error messages
- [ ] `cause` fields explain the root cause, not just restating the error

### Local Testing
- [ ] Ran `python scripts/validate.py` locally — exits with code 0
- [ ] Ran `python scripts/index_check.py` locally — reviewed all warnings
- [ ] Tested that `agentchanti kb update` picks up this content locally (if applicable)

### Manifest
- [ ] Updated `manifest.json` category counts if adding new files
  - Errors: `categories.errors.total_entries`
  - Patterns: `categories.patterns.total_files`
  - ADRs: `categories.adrs.total_files`
  - Docs: `categories.docs.total_files`
  - Behavioral: `categories.behavioral.total_files`

---

## Version Bump Label

Apply **one** of the following labels to this PR to control versioning:

| Label | When to Use |
|---|---|
| `bump:patch` | Content corrections, new error entries, minor wording fixes |
| `bump:minor` | New files added, new categories, new language coverage |
| `bump:major` | Breaking schema changes, ID renames, structural reorganization |

_(Default is `bump:patch` if no label is applied.)_

---

## Related Issues

Closes #_(issue number, if applicable)_

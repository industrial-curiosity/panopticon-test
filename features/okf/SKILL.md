---
name: panopticon-feature-okf
description: Generate and validate constrained OKF Markdown documentation when the instance enables the OKF feature.
---

# Panopticon OKF documentation

Use this feature only when the effective instance mode is `advisory` or `blocking`.

Every non-reserved concept document starts with the constrained frontmatter below:

```yaml
---
type: component
---
```

Use the installed templates for component and interface documents. Keep
`interfaces.md` deterministic: render it from `panopticon/index.json` and
preserve the generated body beneath its frontmatter. Root and nested
`index.md` files list the next documentation level, and `log.md` groups updates
under ISO date headings.

Run the deterministic validator before finalization:

```bash
python3 -m panopticon.features check --docs-root docs
```

Advisory findings are reported for migration. Blocking findings prevent
initialization or the shared PR gate. CI validates but never rewrites docs.

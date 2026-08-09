---
name: quality-lessons-python
description: Language-specific code quality lessons for Python. Load this skill when writing or reviewing Python code to apply accumulated fixes and avoid patterns that have caused errors, warnings, or static analysis issues in this codebase. Activate whenever writing new Python code or reviewing existing Python code for quality.
---

# Code Quality Lessons — Python

## Known Issues and Fixes

### Synthetic package module-ordering — module-level imports need registration first

**Trigger**: Executing fetched Python modules into an in-memory package with an empty `__path__` while registering a module after another module imports it.

**Fix**: Register modules in dependency order and test the path with the real source of the module that owns the import.

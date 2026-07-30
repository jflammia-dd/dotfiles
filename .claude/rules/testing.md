---
paths:
  - "**/*.go"
  - "**/*.java"
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.py"
---

# Testing

Scoped to source globs rather than test-file globs on purpose. The test-first rule has to
load when you open the implementation file, not after the implementation is already written.

- Use TDD where applicable. Write or update tests before writing implementation code.
- Before writing any tests, read existing tests in the area to understand naming conventions,
  structure, assertion style and test organization. Match those patterns exactly.
- Cover both happy and sad paths. Every meaningful code path, error condition and edge case
  needs a test.
- Update existing tests as you introduce changes. Never leave tests in a state where they pass
  by accident or are no longer testing the right thing.
- The goal is increased coverage without duplication. Do not write redundant tests that cover
  ground already handled elsewhere.
- Use the `superpowers:test-driven-development` skill when implementing any feature or bugfix.

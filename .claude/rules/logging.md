---
paths:
  - "**/*.go"
  - "**/*.java"
  - "**/*.ts"
  - "**/*.tsx"
---

# Logging Conventions

When writing Go, Java or TypeScript, follow `docs/Logging Standards - Go, Java, TypeScript.md`
in the Datadog vault for log statement conventions: structured JSON, static messages with
values in fields, snake_case field keys, level semantics, correlation, error handling and
per-language exceptions like EVP workers.

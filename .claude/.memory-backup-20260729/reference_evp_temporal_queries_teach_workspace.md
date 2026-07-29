---
name: reference-evp-temporal-queries-teach-workspace
description: "Second /teach workspace at ~/teach/evp-temporal-queries/ covering Temporal Husky AS-OF semantics, born from the SEC-34246 investigation"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 68ffa770-ab5b-4696-b7ee-84bdd8a596cd
  modified: 2026-07-28T17:45:15.641Z
---

`/teach` workspace at `~/teach/evp-temporal-queries/`, separate from
[[reference-tables-teach-workspace]] because one mission per workspace. Mission is EVP
temporal query and Temporal Husky AS-OF fluency, grounded in ERS reads.

Lesson 1 (`0001-as-of-resolves-one-active-revision.html`) done, covering the SEC-34246
two-query lookup, the `optional_expression` engine gap and why one AS-OF search suffices.
Glossary exists at `reference/glossary.html`. Assets (`style.css`, `quiz.js`) copied from
the reference-tables workspace so both courses look consistent.

Candidates for lesson 2, recorded in learning record 0001: tie-breaking between revisions
sharing a `start_timestamp`, deletion versus edit semantics and write-freshness immediately
after a write.

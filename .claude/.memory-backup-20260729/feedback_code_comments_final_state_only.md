---
name: code-comments-final-state-only
description: "Code comments must describe final, general-purpose behavior only, never development history or the narrow lens of the current ticket"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 1166dd41-c837-44c4-9acb-dcb6a70b794a
  modified: 2026-07-21T19:51:24.803Z
---

Code comments (and any other artifact: PR descriptions, commit messages, docs) must describe the system's final state and intent for every future reader, not the back-and-forth that produced it and not just what mattered for the ticket at hand.

Two distinct failure modes, both caught in the same review session on the same lines:

1. **Development history leaking in.** "A struct rather than a package-level var" or "X instead of Y" references removed code, not current behavior. Iteration happens in conversation; comments capture only the result.
2. **Ticket-scoped framing on a general-purpose type.** A comment on `Dispatcher` (a routing table over any `Strategy`) that explained itself in terms of `EmailStrategy`'s dependency was too narrow. The codebase supports multiple providers, so the comment must describe the general contract (a `Strategy` can depend on runtime state), not the one caller that happened to need it this ticket.

**Why:** The user flagged both as recurring corrections (SEC-34239 code review session, `strategy.go`'s `Dispatcher` comment, corrected twice on the same two lines). A comment that explains what changed, or that only makes sense in light of the current ticket, rots the moment the history or the ticket's context is gone, and reads as if it wasn't written for the whole team.

**How to apply:** Before finalizing any code comment, check it against two questions: (1) does it reference a prior runtime state of the running system (valid) or the old version of the code (invalid, rewrite)? (2) would this comment still make sense to someone reading this type/function with no idea which ticket touched it last, and does it describe the general contract rather than today's one caller? This extends the global CLAUDE.md "Anti-pattern: Iterative Thinking in Output" section explicitly to inline code comments during implementation, not just published artifacts. See [[feedback_documents_define_own_terminology]] for the related discipline of not importing outside framing into a document's own voice.

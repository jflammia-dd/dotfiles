---
name: transcript-ingest-skill-gap
description: No skill exists in the vault for ingesting raw Zoom transcripts (timestamped speaker turns); ingest-zoom-meeting explicitly excludes them
metadata: 
  node_type: memory
  type: project
  originSessionId: a3c9da90-4db1-4c48-84a9-73ebf5cf7ec1
---

`ingest-zoom-meeting` (agents/skills/ingest-zoom-meeting/SKILL.md) only handles structured Zoom AI summaries (Key Outcomes/Decisions/Action Items sections). Its Step 0.5 explicitly stops on raw transcripts (timestamped speaker turns, no summary structure) and says to redirect to a "transcript ingestion skill". No such skill exists in this vault though. The generic `ingest` skill also doesn't cover this case; it only routes URLs or pasted content through the general obsidian ingest workflow.

Why: surfaced 2026-07-15 when given a raw .txt transcript (Justin/Romain GCP onboarding) instead of a Zoom Hub summary export.

How to apply: when handed a raw transcript, don't force it through `ingest-zoom-meeting`. Flag the gap, ask the user whether to (a) manually summarize it into the same 1:1/group-meeting note format, (b) file verbatim, or (c) skip. If this keeps recurring, consider building a real `ingest-transcript` skill (or extending `ingest-zoom-meeting` with a transcript-summarization branch) rather than repeating the same manual workaround each time. Related: [[ingest-zoom-meeting]] known-corrections table lives in the same skill file.

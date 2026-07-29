---
name: feedback-voice-full-scrub-on-revision
description: when revising a draft after a justins-voice violation is flagged, re-run the full skill checklist, not just a patch for the one flagged violation
metadata:
  type: feedback
---

When the user flags one justins-voice violation in a draft, do not just fix that single instance and resubmit. Re-scan the entire draft against the full rule set (Oxford commas, em dashes, comma-before-conjunction, colons in narrative prose, passive voice, semicolons joining clauses) before showing the revision again.

Why: on one PR reply draft, three separate corrections were needed in sequence ("good flag" opener, then a missed comma-before-conjunction, then another missed comma-before-conjunction, then a mid-sentence colon) because each revision only patched the specific thing just flagged instead of a full pass. User asked directly whether justins-voice was being used at all after the pattern repeated.

How to apply: on any revision triggered by a voice-rule correction, treat it as a fresh full application of the skill, not a targeted patch. Read the whole draft back against every rule category before presenting it again.

---
name: feedback-comma-before-conjunction
description: comma before any FANBOYS coordinating conjunction (and/but/or/so/nor/for/yet) joining two clauses is forbidden, not a style suggestion
metadata:
  type: feedback
---

Never write a comma immediately before a coordinating conjunction ("and", "but", "or", "so", "nor", "for", "yet") joining two clauses. The `justins-voice` skill's Punctuation section names "and"/"but"/"or" explicitly but the user's corrections extended this to "so" as well, meaning the intended scope is the full FANBOYS set, not just the three literally listed. Treat it as a hard constraint to actively check for in every draft, not background guidance that can slip.

Exception: an introductory adverbial phrase followed by a comma before the subject (e.g. "Before commit 4, it compared...") is not this violation. That comma separates an intro phrase from the main clause; it has nothing to do with a coordinating conjunction joining two clauses. Don't over-apply the no-comma rule to intro-phrase commas.

Why: user calls this a specific LLM tell they hate. Multiple rounds of correction on one draft (missed on "and", missed again on "and", then missed on "so") show the rule needs a full recheck against all seven FANBOYS words, not just the three named in the skill text.

How to apply: before presenting any drafted reply, scan for ", and", ", but", ", or", ", so", ", nor", ", for", ", yet" joining two clauses and either drop the comma or split into two sentences. See [[feedback_always_voice_drafts]] and [[feedback_voice_full_scrub_on_revision]].

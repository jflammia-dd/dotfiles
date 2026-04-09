---
name: justins-voice
description: "Canonical source of Justin's style and voice rules. Apply when drafting or editing any document, comment or message meant for others: engineering docs, landscape summaries, proposals, meeting summaries, Slack explanations, Confluence comments or any text shared with colleagues or leadership. Also triggers on \"write like me\", \"match my voice\", \"make this sound like me\". Other skills that enforce these rules (edit-doc, confluence-comment-review, etc.) should reference this file rather than duplicating the rules."
---

# Justin's Writing Voice

This skill defines how Justin writes. The goal is writing that builds the reader's mental model with precision and clarity, at every scale from a design doc to a two-sentence Slack reply. It should sound like a technically capable peer, not a language model filling a page.

**Scope**: Apply this skill only to human-facing prose. That includes documents, announcements, Confluence pages, Slack messages, emails, meeting notes, RFCs, proposals and any other content a person will read. Do NOT apply to machine-consumed content: skill files, hook scripts, memory files, CLAUDE.md, settings, code and any output written for Claude to read rather than a human.

## Punctuation

- No Oxford commas. In a list of three or more items, omit the comma before the final "and" or "or." This applies everywhere: lists of nouns, lists of predicates, lists of clauses. "X, Y and Z" not "X, Y, and Z."
  - **High-risk pattern: compound predicates.** "It reads entities, runs strategies and writes results." No comma before "and writes." This is a list of predicates sharing the same subject and the Oxford comma rule applies.
- No em dashes (U+2014) and no double hyphens (`--`) used as em dash substitutes. These are the same mistake in different encodings. Use commas, periods, semicolons or parentheses instead. Restructure the sentence if none of those work naturally. If you catch yourself reaching for an em dash or a `--`, that is a signal the sentence needs to be restructured, not patched.
  - **High-risk pattern: the inline list.** Inserting a parenthetical list mid-sentence produces em dashes almost automatically. "Future implementations (item one, item two and item three) will read from the same track" is correct. Never write "future implementations -- item one, item two, item three -- will read from the same track" or the em dash equivalent. If the list feels too long for parentheses, move it to a numbered list before or after the sentence.
- No colons in narrative prose, or use them extremely sparingly. Find another way to introduce what follows. Colons are fine in headings, labels and non-narrative contexts.
  - **High-risk pattern: the consequence clause.** Explaining or elaborating on a prior statement naturally produces a colon. Split into two sentences instead. "This scope is intentional. The entities most relevant are those analysts investigate." Alternatively, restructure with "because", "since" or a relative clause to avoid the colon entirely.
  - **High-risk pattern: the em dash workaround.** When the em dash rule blocks a construction, the instinct is to reach for a colon as a substitute. "This is not accidental deferral: it is a deliberate strategy" is the same mistake as "This is not accidental deferral -- it is a deliberate strategy." Both violate the rules. The fix is the same in both cases: split into two sentences or restructure with a conjunction. "This is not accidental deferral but a deliberate strategy" or "This is deliberate, not accidental."
- No comma before a coordinating conjunction ("and," "but," "or") joining two independent clauses. Drop the comma and let the conjunction do the work. "The math is straightforward and the team agrees" not "The math is straightforward, and the team agrees." If the sentence feels too long without the pause, split it into two sentences instead.
- Minimize commas. If a comma can be dropped without creating ambiguity, drop it. Introductory phrases under five words often don't need a comma after them. Read the sentence without the comma first and only add it if the meaning changes or the rhythm breaks.
- Straight quotes, not curly.

## Sentence structure

- Sentences should connect and build on each other. Avoid sequences of short declarative sentences that feel like prose trying to be a bullet list.
- Long sentences are fine when well-structured. A single sentence can carry a complex thought.
- No semicolons for joining thoughts. Use separate sentences or natural conjunctions.

## Voice

- **Always use active voice.** Rewrite every passive construction so the subject performs the action. "The proposal was reviewed by the team" becomes "The team reviewed the proposal." If the actor is unclear, name one from context. The only acceptable passive is when the actor is genuinely unknown or irrelevant. Scan every sentence. This is a correction step, not a suggestion.
- **Active voice does not mean first person.** Do NOT rewrite sentences into first person ("I") when the existing subject is already performing the action. "This document builds on" is active voice with "this document" as the subject. "We adopt this framing" is active voice with "we" as the subject. "Justin Flammia is the RFC owner" is active voice with "Justin Flammia" as the subject. All of these are correct and should be left alone. The goal is eliminating passive constructions, not changing who the subject is.
- First person ("I") is fine when it already appears in the text or when Justin is genuinely the one speaking in his own voice. Don't force it where third person or "we" is the natural framing.
- Use "we" for team decisions, shared direction and collective work.
- Be careful about attribution. Credit others for their contributions. Don't attribute decisions or ideas to "the team" or "the workshop" when Justin is the one synthesizing and proposing.
- Confident but not aggressive. Direct but not terse. The writing should feel like someone who has thought carefully about what they're saying and believes it, without posturing.
- Contractions are fine. "I've", "we're", "don't" all read naturally.

## Building mental models

The purpose of every piece of writing is to transfer an accurate model of something into the reader's head. This applies at all scales: a ten-page design proposal, a two-paragraph Confluence reply, a single Slack message. If the reader's model hasn't sharpened by the end, the writing didn't do its job.

**Lead with the insight, not the setup.** The claim or conclusion belongs at the front. Supporting details follow. Don't make the reader accumulate context before they know what the context is for. "The race condition exists because the lock scope doesn't cover the update path" is the right structure. Walking through lock semantics before naming the failure is not.

**Name the constraint, not just the behavior.** Explaining what a system does is less useful than explaining why it must work that way. "The entity model uses composite versioning because two concurrent writes at the same timestamp would be indistinguishable otherwise" builds a model. "The entity model uses composite versioning" is a fact without a frame.

**Connect explicitly to what the reader already knows.** When a concept has an analogue the audience understands, name it and explain the difference. Engineers reason from analogy. The bridge matters. Don't assume the connection is obvious.

**Precision is not optional.** Vague explanations feel approachable but leave the reader with a blurry model. Say exactly what you mean: name the specific field, the specific condition, the specific invariant. Round numbers and hand-waving generate follow-up questions that a precise first sentence would have prevented.

**Don't humor. Correct the model.** When a reviewer has a misunderstanding, correct it directly. "That's a great question" wastes a sentence. The answer can be generous and thorough without being performative. Treating someone like a peer means giving them an accurate response, not a validating one.

**Short writing can still teach.** A Confluence comment can advance the reader's model in two sentences. A Slack reply can resolve a conceptual confusion without becoming a document. Length is not the variable. Precision is.

Write for peers who are already technically capable. Don't over-explain what they know but don't assume they've worked through the same edge cases or constraints you have. The gap to close is specific and technical, not general.

## Simplicity as mastery

True mastery over an idea shows in the ability to explain it simply. Fluency with a system isn't enough. The test is whether you can explain it to someone who lacks your context.

When an explanation grows complex, that usually signals unclear thinking, not a complex subject. Stop and find the simpler sentence before reaching for qualifications and structure to compensate.

When two phrasings are both accurate, always choose the simpler one. "The event triggers a lookup" is clearer than "upon event receipt, a lookup operation is initiated" and equally precise.

Use technical terms when they genuinely compress meaning because the reader knows them and no simpler substitute exists. Don't use them to signal domain familiarity or make reasoning feel more rigorous.

Genuinely complex systems require carrying their complexity. When that's unavoidable, simple structure still matters. One idea per sentence. One argument per paragraph. The reader's cognitive load comes from the subject. Don't add to it.

## Length discipline and cutting

Every paragraph must earn its place by advancing the reader's model. If a paragraph does not leave the reader knowing something they didn't know before, or reframing something they already knew, cut it.

**The earn-your-place test.** Read each paragraph and ask: what does the reader understand after this that they didn't understand before? If the answer is "the same thing they understood from the previous paragraph, stated again," cut the paragraph.

**When to cut vs. trim.** Trimming makes a paragraph shorter. Cutting removes it entirely. If a paragraph's core claim is already made elsewhere, the right action is usually to cut, not trim. Trimmed padding is still padding.

**Signs a section has gone on too long:**
- The last paragraph restates the conclusion of the first paragraph
- You find yourself writing "in other words" or "to put it differently"
- A paragraph explains what the previous paragraph implied but didn't state
- The section covers the same ground at a higher and lower level of abstraction without the shift adding anything

**Defensive writing.** Adding caveats and qualifications the reader didn't ask for pads length and signals uncertainty. "It's worth noting that this may not apply in all cases" is almost never worth writing. State the claim. If it has real exceptions that matter to the reader, state them directly. If the exceptions are edge cases the reader won't encounter, omit them.

**Throat-clearing.** Introductory material that orients without informing belongs in documents where readers need to be brought along gradually. In technical writing for peers, throat-clearing wastes sentences. Don't spend a paragraph explaining what you're about to explain. Say the thing.

**Redundant context.** Documents that grow through iterative editing often contain the same background information in two places: once near the beginning (where it was originally introduced) and once in a later section (where it was re-explained for a reviewer who asked). When this happens, keep one and remove the other. The reader only needs the context once.

## Formatting preferences

- Prefer numbered lists over bullet lists. Numbered lists give readers a handle for referencing specific points in comments and discussions ("I agree with point 3 but have a question about 5") and they impose a natural ordering that helps the reader digest information sequentially. Use numbered lists whenever presenting distinct items, steps, options, tracks of work or categories. Bullet lists are acceptable only for truly unordered sets where numbering would imply a false ranking or sequence.
- Prefer numbered lists over inline prose enumeration. When three or more substantive items appear in a sentence, break them out into a numbered list rather than running them inline. A short inline pair ("X and Y") is fine when it flows naturally in prose. The threshold is substance: if each item could stand as its own thought or action, it belongs in a list. "The approach covers authentication, session management and audit logging" is borderline but acceptable. "The approach covers five distinct concerns..." followed by inline descriptions is not acceptable. That belongs as a numbered list.
- When breaking complex topics into parts, use numbered lists with bold standalone headers. Put the narrative text on the line below the header, indented.
- Don't use em dashes, colons or other inline separators between a header and its description.
- Light on bold in narrative prose. Bold is for headers in structured lists, not for emphasis within sentences.
- Parenthetical asides are fine for definitions or brief context but shouldn't be overused.

## What to avoid

- Formulaic transitions like "Additionally," "Furthermore," "Moreover"
- Defining something by what it isn't ("This is not a project plan. It is not a set of solutions.")
- Hedging language ("it could potentially be argued," "this document attempts to")
- Overly punchy openings that state the obvious
- Sentences that feel assembled rather than written
- Passive voice ("was completed," "were identified," "has been proposed"). Rewrite every instance into active voice with a clear subject performing the action.
- Counting preambles that preview a list's length without adding context. "There are three key considerations:" followed by the three considerations adds nothing. If the intro sentence explains what the list represents or why it matters, it earns its place. If it just announces the count, cut it.
- AI writing patterns from the humanizer skill (significance inflation, copula avoidance, rule of three, etc.)
- Repeating back the request before responding to it. "You asked me to add a link to this section. I'll go ahead and add that now." Both sentences are wasted. Just add the link. In conversational contexts, the acknowledgment should be one word at most ("sure", "yes") and the action follows immediately.

## Tone by context

- **Documents for distribution** (engineering landscapes, proposals, summaries shared with leadership): formal-but-human. First person where appropriate. Confident framing. The tone of this skill.
- **Technical design specs and data model proposals**: impersonal third-person. No second-person ("you", "your") and no first-person ("I", "we"). Systems, components, services and tracks are the subjects. The document speaks for itself as a specification rather than as a letter to a reader. Use this mode when Justin explicitly asks for it or when the document will circulate as a standalone spec detached from its author. See "Impersonal third-person technical voice" below.
- **Slack messages and Confluence comments**: casual and direct in tone, but precision still matters. Formality drops; the goal of building the reader's mental model does not. A two-sentence Slack reply can correct a misunderstanding or add a constraint the reader was missing. Don't pad, but don't sacrifice accuracy for brevity. Apply all punctuation and voice rules from this skill. When someone makes a simple request ("can you add a link?", "mind clarifying this?"), acknowledge minimally ("sure", "yes", "done") and act. Don't restate what was asked, don't explain what you're about to do. The action is the response.

## Impersonal third-person technical voice

When applying this mode, eliminate every second-person and first-person reference and replace them with precise technical subjects.

**Second-person → component/system subjects:**
- "your view" → "the Risk Insights Caniche view" or "the User Entity view"
- "your RFC" → "the RFC" or name it specifically
- "you need to approve or reject" → "this proposal requires approval or rejection"
- "you can verify" → "reviewers can verify"
- "before you finalize" → "before the Data Stores section is finalized"

**First-person → document/proposal subjects:**
- "I'm proposing" → "this proposal introduces" or "the proposal covers"
- "What I'm proposing" → "The proposed changes" or "This proposal"
- "What I need from you" → "Open dependencies" or "Prerequisites"
- "I'd like us to start it together" → "This conversation should start jointly"
- "Happy to walk through this" → "Questions and comments are welcome in Slack or on [document]"

**What stays the same:** All other voice rules apply. Active voice, no Oxford commas, no em dashes, no double hyphens, numbered lists, no hedging, no counting preambles.

## Example of Justin's voice (first-person mode)

> Based on the discussions and decisions from the workshop, I've separated UEBA into distinct tracks of work that can be reasoned about independently while still remaining connected to each other. Not all of these tracks are the same kind of work. Some are foundational components that need to exist before other tracks can move forward and some are net-new functionality that builds on top of those foundations.

Notice: no Oxford commas, no em dashes, no hedging, first person ownership ("I've separated"), sentences that flow into each other, assumes the reader knows what UEBA is.

## Example of impersonal third-person technical voice

> The `siem_entity_resolution` track stores one record per resolved inferred entity, keyed by `inferred_entity_id`. That key matches `signal_scores_v3."entity_metadata.id"` exactly, so no changes to upstream views are needed to use it. The Caniche view joins this track against `redaplinfra` to produce one consolidated row per anchored identity.

Notice: no "you" or "I", systems and tracks are the subjects, confident and direct, reads like a specification.

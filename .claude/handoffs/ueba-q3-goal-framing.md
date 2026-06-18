---
name: ueba-q3-goal-framing
created: 2026-06-18T02:33:00Z
summary: Published the UEBA Q3 Goal Framing doc to Confluence; Deliverables doc and GitHub deep-dive edits still pending
project: /Users/justin.flammia/Documents/Datadog
---

# UEBA Q3 Goal Framing session handoff

## What this session did

Reviewed, scrubbed and published the UEBA Q3 planning doc (the one previously titled "UEBA Q3 Integration Briefs", renamed this session to **UEBA Q3 Goal Framing**).

Two vault docs:
- `docs/UEBA Q3 Goal Framing.md` (published).
- `docs/UEBA Q3 Deliverables and Ownership.md` (NOT yet published, planned for tomorrow).

Published Confluence page: [UEBA Q3 Goal Framing](https://datadoghq.atlassian.net/wiki/spaces/CSiem/pages/6876006301) (id `6876006301`, version 9), child of the UEBA page (id `6459031643`) under a new "Planning" H2 section.

Model the doc now tells (all agreed/edited with Justin this session):
1. One canonical entity foundation; customer value lands in three views. User Entity view and Risk Insights entity-rollup view already exist (Q3 decorates them); the Asset Entity view is net-new.
2. Operating frame: resolve / enrich / relate, best-effort ([ADR-0003]).
3. Cloud actor resolution (Section 1): defined a resolution curve (Classified → Resolved-human → Attributed-non-human → Fully-resolved). Email is the universal baseline (cross-trust `EmailExactStrategy`, works today, all four providers). Per-provider gap-closers by who controls the data: GCP nothing, AWS within-trust walk (in-flight Q3, NOT shipped), Azure principal-ID via Entra objectId (P0, needs Entra ingestion), GitHub login via SAML SSO data (P1, SSO-gated, in-flight with GitHub integration team / Mark Azer). Non-human Q3 = classification only; attribution is post-Q3. Resolved actors surface in the Risk Insights entity-rollup view + User Entity view.
4. Workday, SpyCloud decorate the User Entity view on email. CrowdStrike = standalone browsable Asset Entity view, explicitly NOT linked to users/signals in Q3 (no clear path yet).

Scrubs applied (durable-source discipline): removed undocumented SpyCloud legal-approval gate, weighted scoring, match-rate/coverage caveat (out of scope), the specific "side panel" surface; standardized the three view names; dropped "briefs" phrasing.

## Verified facts worth keeping

- ERS strategy code read this session (`dd-source/domains/cloud-security-platform/apps/apis/siem-entity-resolution-api/internal/strategy/`): `EmailExactStrategy` is the only cross-trust path, runs all orgs; within-trust strategies are AWS-only (`CloudTrailAssumeRoleStrategy`); no GCP/Azure within-trust; `EntityTypeResolutionPaths` = {Email Address, IAM User} only (no principal-ID strategy yet). This corrected the Deliverables doc (item 3 was wrongly "within-trust resolvers for GCP and Azure").
- GCP `principalEmail`, Azure `caller` (UPN/GUID/service identity), GitHub `externalIdentities` GraphQL + SAML-in-audit-log (GA March 2024) all substantiated from public provider docs (cited in the doc).

## Not done yet

1. **Publish `docs/UEBA Q3 Deliverables and Ownership.md`** (tomorrow). Add it as the second entry under the Planning section on the UEBA page. Source is already scrubbed/consistent (legal refs removed, kept documented SpyCloud OEM procurement; CrowdStrike device attribution moved to post-Q3; asset inventory reframed standalone).
2. **GitHub deep-dive Confluence edits (DRAFTED, NOT APPLIED).** Page [GitHub Actor Resolution in UEBA](https://datadoghq.atlassian.net/wiki/spaces/CSiem/pages/6876661455) (id `6876661455`). Drafted edits add the `externalIdentities` GraphQL path + the 2024 SAML-in-audit-log feature (which may explain the 0-resolved logins in staging) and rework the "missing dataset" section + conclusion. Awaiting Justin's go to apply. Verified sources: [GitHub changelog](https://github.blog/changelog/2024-03-19-logging-saml-sso-and-scim-identity-data-in-audit-log-events-is-generally-available/), [GraphQL objects](https://docs.github.com/en/graphql/reference/objects).

## Mechanics / gotchas for resuming

- Publish flow: `uv run python3 /tmp/update_briefs.py` (converts `docs/UEBA Q3 Goal Framing.md` → ADF, PUTs to page 6876006301). Script strips the H1, the Obsidian banner blockquote and the companion-Deliverables sentence, and asserts no "legal"/"Deliverables" leak. Run with `uv run python3` (plain `python3` is blocked).
- Converter fix made this session in `~/.claude/skills/obsidian-to-confluence/scripts/md_to_adf.py` (real file in `dotfiles`): list-item AND paragraph continuation lines now emit a `hardBreak` so standalone bold headers render on their own line. Benefits all future publishes.
- The Goal Framing page is now "edit in Confluence" (banner). Prefer surgical Confluence edits over republish-from-Obsidian for further changes; republish is set up correctly but the banner reflects Confluence as canonical.
- `docs/log.md` is append-only and protected. Left its historical "Integration Briefs" references untouched.
- Confluence ops use the keychain token (`security find-generic-password -s confluence-api-token`) + git email; no secrets in repo.

## Suggested skills next session

- `obsidian-to-confluence` (publishing the Deliverables doc, applying the deep-dive edits)
- `justins-voice` (any prose)
- `grill-me` (if reviewing the Deliverables doc end to end like we did for Goal Framing)

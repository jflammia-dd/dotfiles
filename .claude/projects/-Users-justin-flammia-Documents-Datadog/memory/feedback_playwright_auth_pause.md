---
name: feedback-playwright-auth-pause
description: "Pause and explicitly wait after navigating Playwright to an authenticated page (Slack, etc.) instead of immediately assuming failure from a sign-in redirect"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: dffa5859-a983-4140-b244-af57b84f0480
  modified: 2026-08-10T13:28:56.279Z
---

When a Playwright `browser_navigate` to an authenticated surface (e.g. Slack's Rimeto profile pages) lands on a sign-in/workspace-picker page, that is not necessarily a dead end. Justin may need to manually authenticate in that browser window. This happens every time this workflow runs, not just once.

Why: on 2026-08-10 I hit a "Find your workspace" sign-in page twice, concluded the session had no saved login, told the user the path was blocked, and moved on to asking for a workaround. Justin had actually already logged in twice in that window without me noticing, because I never paused to give him the chance or re-checked the page state afterward.

How to apply: after a Playwright navigation to a page that could require login, if the snapshot shows a sign-in/workspace picker, say so and explicitly pause for the user to authenticate rather than declaring the path blocked. Before concluding failure, re-run `browser_snapshot` to check current state (don't rely on the state captured at navigation time). This applies to every Slack Rimeto profile lookup and any other authenticated-browser workflow in this vault (see the obsidian skill's person-enrichment start_date/manager lookup steps).

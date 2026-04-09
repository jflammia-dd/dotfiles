---
name: Obsidian Templater Plugin Dependency
description: The vault's Person template depends on the Templater community plugin for first-name alias auto-population; the obsidian CLI does NOT execute Templater — always fix aliases manually after create
type: project
---

The Person template (`templates/Person.md`) uses Templater syntax to auto-populate the first-name alias on new person notes.

**Why:** Obsidian's built-in Templates plugin only supports `{{title}}`, `{{date}}`, and `{{time}}` — it cannot extract the first word from the title. Templater enables `<% tp.file.title.split(' ')[0] %>` to do this automatically.

**Critical CLI limitation:** The `obsidian create ... template=Person` CLI command copies the template verbatim without executing Templater JavaScript. The `aliases` field will contain the raw expression `<% tp.file.title.split(' ')[0] %>` instead of the person's first name. This must be fixed manually immediately after creation:

```bash
obsidian property:set name=aliases value='["FirstName"]' type=list path="people/First Last.md"
```

Always do this as step 1b whenever creating a person profile via the CLI.

**How to apply:** If the Person template ever stops auto-populating aliases in Obsidian's UI, check that the Templater community plugin is installed and enabled in Obsidian settings. When editing the template, use Templater syntax (`<% ... %>`) not built-in template syntax (`{{ }}`).

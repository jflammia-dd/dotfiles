# Obsidian Formatting Reference

Sourced from official Obsidian documentation at help.obsidian.md. Consult this reference when creating or editing files in the vault.

## Properties (YAML Frontmatter)

Properties are stored in YAML format at the top of the file, delimited by `---`.

### Property Types

| Type | Format | Example |
|---|---|---|
| Text | Single line of text | `title: A New Hope` |
| List | Hyphen-prefixed items | `cast:\n  - Mark Hamill\n  - Harrison Ford` |
| Number | Literal number | `year: 1977` |
| Checkbox | `true` or `false` | `favorite: true` |
| Date | ISO format | `date: 2020-08-21` |
| Date & time | ISO with time | `time: 2020-08-21T10:30:00` |
| Tags | List of tag values | `tags:\n  - journal\n  - personal` |

### Important Rules

- Each property name must be unique within a note.
- Property names are separated from values by a colon followed by a space.
- Internal links in text properties must be surrounded with quotes: `link: "[[Episode IV]]"`.
- Internal links in list properties must be surrounded with quotes: `- "[[Link]]"`.
- Markdown is not rendered in text properties. Properties are meant for small, atomic bits of information.
- Nested properties are not supported. Use source mode to view them.
- The `tag` (singular) property is deprecated since Obsidian 1.4; use `tags` (plural).
- The `alias` property is deprecated; use `aliases`.
- The `cssclass` property is deprecated; use `cssclasses`.

### Default Properties

| Property | Type | Purpose |
|---|---|---|
| `tags` | Tags | Categorize notes |
| `aliases` | List | Alternative names for the note |
| `cssclasses` | List | Apply CSS snippets to individual notes |

## Internal Links (Wiki-links)

### Supported Formats

- Wikilink: `[[Three laws of motion]]`
- Markdown: `[Three laws of motion](Three%20laws%20of%20motion.md)`

Obsidian defaults to Wikilink format due to its compact syntax.

### Link Types

| Link Type | Syntax | Example |
|---|---|---|
| Basic link | `[[Note]]` | `[[Three laws of motion]]` |
| With display text | `[[Note\|Display]]` | `[[Three laws of motion\|Newton's laws]]` |
| To heading | `[[Note#Heading]]` | `[[Note#Details]]` |
| To heading with display | `[[Note#Heading\|Display]]` | `[[Note#Details\|Section name]]` |
| To block | `[[Note#^blockid]]` | `[[2023-01-01#^37066d]]` |
| Same-note heading | `[[#Heading]]` | `[[#Preview a linked file]]` |
| Subheading | `[[Note#H1#H2]]` | `[[Help#Questions#Report bugs]]` |

Note: The `\|` in the table above is required by markdown table escaping. In normal text outside tables, use `|` without the backslash: `[[Full Name|Display Name]]`.

### Invalid Characters in Link Targets

Do not use these in note names intended as link targets: `# | ^ : %% [[ ]]`

### Display Text (Aliases)

- Use `|` for one-off display text: `[[Full Name|Short Name]]`
- Use the `aliases` frontmatter property for reusable alternate names across the vault
- Display text is for specific contexts; aliases are for vault-wide alternate names

## External Links

Standard markdown link syntax: `[Display Text](URL)`

- Blank spaces in URLs must be URL-encoded: `%20`
- Or wrap URL in angle brackets: `[Note](<path with spaces>)`

### Images

- External: `![Alt|widthxheight](URL)`
- Width only (preserves aspect ratio): `![Alt|100](URL)`
- Embedded from vault: `![[image.png]]`

### Embedding Notes (Transclusion)

Embed an entire note or a specific section into another note:

- Embed full note: `![[Note Name]]`
- Embed specific heading: `![[Note Name#Heading]]`
- Embed specific block: `![[Note Name#^block-id]]`

Embeds render the content inline in Reading view and Live Preview.

## Tags

### Inline Tags

Use `#` followed by the tag name: `#todo`, `#meeting`, `#follow-up`

Nested tags use `/` as separator: `#project/ueba`, `#status/in-progress`

Tags can appear anywhere in the note body. They are distinct from the `tags` frontmatter property, though both are searchable.

Valid tag characters: alphanumeric, hyphens, underscores, and forward slashes. Tags must contain at least one non-numeric character.

## Basic Formatting

| Style | Syntax | Notes |
|---|---|---|
| Bold | `**text**` or `__text__` | |
| Italic | `*text*` or `_text_` | |
| Strikethrough | `~~text~~` | |
| Highlight | `==text==` | Obsidian-specific |
| Bold + italic | `***text***` | |
| Inline code | `` `text` `` | |

### Escape Characters

Place `\` before special characters to display them literally: `\*`, `\_`, `\#`, `` \` ``, `\|`, `\~`

For numbered lists, escape the period: `1\.` prevents list formatting.

## Paragraphs and Line Breaks

- Blank line between text creates separate paragraphs.
- Single Enter is a continuation of the same paragraph in rendered output.
- Two spaces at end of line + Enter creates a line break within a paragraph.
- `Shift+Enter` inserts a line break directly.
- Multiple blank spaces collapse to single space in Reading view.
- Use `&nbsp;` or `<br>` for explicit spacing.

## Headings

```md
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6
```

## Lists

### Unordered
Use `-`, `*`, or `+` before text.

### Ordered
Use `number.` or `number)` before text.

### Task Lists
```md
- [x] Completed task
- [ ] Incomplete task
```

Obsidian core supports any character inside brackets (`[x]`, `[?]`, `[-]`), but the Tasks plugin specifically uses `[x]` for completion. Other bracket characters may have special meanings in Obsidian core but are not recognized as "done" by the Tasks plugin.

### Nesting
Indent with tab or spaces. Can mix ordered, unordered, and task lists.

## Tables

### Basic Syntax

```md
| First name | Last name |
| ---------- | --------- |
| Max        | Planck    |
| Marie      | Curie     |
```

### Requirements

- Header row separator must contain at least two hyphens per column.
- Outer pipes are optional but recommended for readability.
- Cells do not need perfect alignment.

### Column Alignment

```md
| Left | Center | Right |
| :-- | :--: | --: |
| Content | Content | Content |
```

### Pipes in Table Cells

Escape with backslash: `\|`

This is required when using wiki-link aliases or image sizing inside tables:
```md
| Column |
| --- |
| [[Note\|Display Text]] |
| ![[image.jpg\|200]] |
```

## Blockquotes

```md
> Quoted text
```

### Callouts

Callouts are specially formatted blockquotes:
```md
> [!info] Optional title
> Callout content
```

Common types include: `info`, `tip`, `warning`, `note`, `example`, `question`, `abstract`, `todo`, `success`, `failure`, `danger`, `bug`, `quote`. Custom types are also supported.

Foldable callouts use `+` (expanded) or `-` (collapsed):
```md
> [!tip]- Collapsed by default
> Hidden content
```

## Code

### Inline
Single backticks: `` `code` ``

### Code Blocks
Triple backticks or triple tildes with optional language identifier:
````md
```js
console.log("hello")
```
````

### Nesting Code Blocks
Use more fence characters for the outer block than the inner block:
`````md
````md
```js
console.log("hello")
```
````
`````

## Comments

- Inline: `%%comment%%`
- Block:
```md
%%
Multi-line comment.
Only visible in Editing view.
%%
```

## Footnotes

```md
Simple footnote[^1].

[^1]: Referenced text.
[^2]: Multi-line footnote.
  Add 2 spaces for continuation lines.
```

Inline footnotes: `^[This is inline.]` (Reading view only, not Live Preview)

## Math (MathJax/LaTeX)

- Block: `$$..$$` on separate lines
- Inline: `$expression$`

## Diagrams (Mermaid)

Use `mermaid` code blocks:
````md
```mermaid
graph TD
    A --> B
```
````

To create internal links in diagrams, add the `internal-link` class:
```
class Biology,Chemistry internal-link;
```

## Horizontal Rules

Three or more of: `***`, `---`, `___` (with or without spaces between characters)

## Template Variables

| Variable | Output |
|---|---|
| `{{date}}` | Current date in default format |
| `{{date:YYYY-MM-DD}}` | Date with explicit format |
| `{{date:dddd, MMMM DD, YYYY}}` | Readable date (e.g., Thursday, January 30, 2026) |
| `{{time}}` | Current time in default format |
| `{{time:HH:mm}}` | Time with explicit format |
| `{{title}}` | Current note title |

Always use explicit date formatting to ensure consistency: `{{date:YYYY-MM-DD}}` rather than `{{date}}`.

## Tasks Plugin Syntax

For compatibility with the Tasks community plugin:

```md
- [ ] Task description #todo
- [ ] Task with priority ⏫ #todo
- [ ] Task with due date 📅 2026-02-10 #todo
- [ ] Combined ⏫ 📅 2026-02-10 #todo
- [x] Completed task #todo ✅ 2026-02-04
```

Priority emojis: ⏫ (highest), 🔼 (high), 🔽 (low), ⏬ (lowest)

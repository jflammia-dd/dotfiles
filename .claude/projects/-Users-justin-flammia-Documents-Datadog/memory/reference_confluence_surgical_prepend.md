---
name: reference-confluence-surgical-prepend
description: How to prepend a panel to a Confluence page without disturbing existing content or annotation marks.
metadata:
  type: reference
---

The `confluence-write` skill has no prepend mode. Its script only does replace, delete-block, add-annotation and strip-annotation. To insert a banner at the top of a page, drive the v2 ADF API directly.

```
GET  /wiki/api/v2/pages/{id}?body-format=atlas_doc_format
PUT  /wiki/api/v2/pages/{id}
     {id, status:"current", title, body:{representation:"atlas_doc_format", value:"<json string>"}, version:{number:N+1, message:"..."}}
```

Build the new tree as `[panel] + existing_content`, then assert `json.dumps(new[1:]) == json.dumps(old)` before the PUT. That assertion is what makes the edit surgical. Annotation marks survive because they are still in the tree being sent.

Auth is the same as the `confluence-api` skill, so `security find-generic-password -s confluence-api-token -w` with `justin.flammia@datadoghq.com`.

A warning panel is `{"type":"panel","attrs":{"panelType":"warning"},"content":[...]}` and accepts paragraphs and `codeBlock` children. Markdown needs converting by hand, so `**bold**` becomes a `strong` mark, backticked spans become a `code` mark and `[text](url)` becomes a `link` mark with `attrs.href`.

Worked example: page 7013762888 gained an obsolescence banner at v18, 42 nodes to 43, with all 7 annotation marks intact. See [[feedback-confluence-annotations-stay-intact]].

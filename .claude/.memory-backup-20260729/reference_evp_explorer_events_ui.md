---
name: reference_evp_explorer_events_ui
description: EVP Explorer = Events UI internal tool for browsing EVP track data without SQL
metadata: 
  node_type: memory
  type: reference
  originSessionId: 1e46641a-15ad-494d-9b86-8dff46e51cac
---

When the user asks for an "EVP Explorer" or a GUI way to browse data in an EVP track, they mean the **Events UI** internal tool.

URL: `dd.datad0g.com/internal/events-ui/`

For `siementity` specifically: `https://dd.datad0g.com/internal/events-ui/queries?track=siementity`

Append `&query_type=list` and a `&timerange=` parameter to scope the view. Change `track=` for other tracks.

Works like Logs Explorer: pick a track, set a time range, filter by field values, browse raw events. No SQL required.

Does NOT support Temporal Husky point-in-time queries (`AS_OF`, `IS_LIVE`). Use PUP for those.

Full reference doc in vault: [[Events UI]]

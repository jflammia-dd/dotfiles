---
name: feedback_balto_cindy_trigger
description: balto migrate CLI creates proposals without a reviewer so CINDY never fires; must call UpdateConfiguration with ReviewConfig to trigger the Slack approval bot
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 55a57b35-5822-482b-893c-64362ef7e96b
---

`balto migrate` creates Balto proposals but never sets `ReviewConfig`, so CINDY (the Mosaic change-approval Slack bot) does not fire automatically after a CLI-based migration.

**Why:** The `ini_converter.go` constructs `CreateConfigurationRequest` without a `ReviewConfig` field. The portal UI populates this at creation time, which is why CINDY fires for portal-created proposals but not CLI ones.

**How to apply:** After running `balto migrate`, trigger CINDY by calling `UpdateConfiguration` with `ReviewConfig.Teams` and `ReviewConfig.SlackChannels` set. The tool approach (use `C04MCBZ3ZCJ` for `#k9-siem-ops`, the correct CINDY channel):

```go
c.UpdateConfiguration(ctx, &baltoapi.UpdateConfigurationRequest{
    DomainName:   "domain-name",
    ConfigKey:    "key-name",
    ReviewConfig: &baltoapi.ReviewConfiguration{
        Teams:         []string{"cloud-siem"},
        SlackChannels: []string{"C04MCBZ3ZCJ"},
    },
})
```

Run via a small `bzl run` tool using `ddgrpc.WithTLS()` + `ddgrpc.WithIdentity("balto-control-plane-api.balto")` + a Vault token from `authn.GetToken(ctx, "us1.release.mgmt.dog", "balto")`. The datacenter must be `"us1.release.mgmt.dog"` (not `"us1.ddbuild.io"`).

See [[Balto Runtime Configuration]] for the full workflow including the synthetic INI file trick for `balto migrate`.

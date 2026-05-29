---
name: feedback_proto_regen_bazel
description: "Proto regeneration in dd-source must use Bazel snapshot update targets, never local protoc"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a4af6c84-be83-436f-a2f9-72b997621bd9
---

Never use local `protoc` or `protoc-gen-go` to regenerate `.pb.go` files in dd-source. The Bazel-pinned toolchain produces different output than the system-installed tools. DDCI runs snapshot tests that verify the committed files match Bazel's output exactly.

**Why:** In a session, local `protoc-gen-go-grpc 1.6.1` generated different method invocation patterns than Bazel's pinned version, causing `resolution.pb.go_snapshot_test` and `resolution_grpc.pb.go_snapshot_test` to fail in DDCI.

**How to apply:** After editing a `.proto` file, regenerate using the Bazel snapshot update targets:

```bash
bzl run //path/to/resolutionpb:resolution.pb.go_snapshot_test_update
bzl run //path/to/resolutionpb:resolution_grpc.pb.go_snapshot_test_update
```

The `_snapshot_test_update` targets run Bazel's pinned `protoc`, compare the output against the committed file and overwrite it with the correct version. Commit the resulting diff. These targets work in-session unlike `bzl build`/`bzl run` for app targets (which hit the python3 shim issue).

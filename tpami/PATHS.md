# Local paths in this release

Absolute paths from the research host are not published. Where a generator or a
provenance record referred to one, the released copy carries a placeholder:

| placeholder | what it stood for |
|---|---|
| `<AUDIT_ROOT>` | the audit working tree holding the frozen records |
| `<MOT_AUDIT_ROOT>` | the frozen MOT17/MOT20 state and ground-truth tree |
| `<DATASETS_ROOT>` | the local dataset root (DanceTrack, MOT17 images) |
| `<LOCAL_PATH>` | any other host-local path |
| `<EMAIL>`, `<HOST>`, `<CONDA>` | contact, host and environment identifiers |

Only path strings were replaced. Every recorded SHA-256 is unchanged, so each
artifact is still identified by content rather than by location. To re-run a
generator, set the placeholder to your own copy of the corresponding tree; the
layout each one expects is in `UPSTREAM.md`.

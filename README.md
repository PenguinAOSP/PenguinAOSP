# PenguinAOSP

Developer-friendly custom ROM layer on **[UwUAOSP](https://github.com/uwuAOSP)** (Android 17).

Unlike full-tree forks (AlphaDroid-style `platform_*` mirrors), PenguinAOSP keeps upstream UwUAOSP clean and ships all changes as a **replayable patch layer**.

First device: **Nubia Z60 Ultra (`cerro`, SM8650)**.

## Built with vibe coding

This repository was built with **[Cursor](https://cursor.com)** / **Codex** vibe coding (AI-assisted agent workflow).  
Git history / GitHub **Contributors** only list the human owner ([@ycrrongos](https://github.com/ycrrongos)); AI tools are not co-authors on commits.

## Quick start

```bash
# 1) Sync UwUAOSP (release manifest)
bash scripts/init-uwu-source.sh

# 2) Replay Penguin layer
bash scripts/apply-all.sh

# 3) Build cerro OTA
bash scripts/build-cerro.sh va
```

## Repository layout (truth source)

| Path | Role |
|------|------|
| `vendor/penguin/` | Features, Python context patches, file copies, overlays |
| `devices/nubia/` | Device product trees (`cerro`, `sm8650-common`) |
| `patches/` | Small unified diffs |
| `scripts/` | `apply-all.sh`, build helpers |
| `docs/` | Feature docs, troubleshooting, worklog |
| `source/` | **Not in git** — local UwUAOSP checkout only |

See [`docs/SKELETON.md`](docs/SKELETON.md) and [`AGENTS.md`](AGENTS.md).

## Relation to UwUAOSP

| | UwUAOSP | PenguinAOSP |
|--|---------|-------------|
| Model | Full Android tree (`platform_*`, versions manifest) | Patch layer only |
| Sync | Official release / `uwu-17.0` | `repo sync` upstream, then `apply-all.sh` |
| Branding | uwu | PenguinAOSP lunch / product name |

penguinOS ([Project-penguinOS](https://github.com/Project-penguinOS)) is **reference only** — we do not use its tree as a base.

## License

Individual files keep their upstream SPDX / Apache-2.0 notices unless stated otherwise.

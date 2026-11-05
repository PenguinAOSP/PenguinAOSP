# platform_vendor_penguin-versions

PenguinAOSP **release manifest** — based on [UwUAOSP `platform_vendor_uwu-versions`](https://github.com/uwuAOSP/platform_vendor_uwu-versions) pin **17.0.181**.

## What this is

Normal AOSP-style entrypoint:

```bash
repo init -u https://github.com/PenguinAOSP/platform_vendor_penguin-versions.git -b main --git-lfs
repo sync -c -j$(nproc)
```

| Layer | Where it comes from |
|-------|---------------------|
| AOSP (~867) | `android.googlesource.com` (unchanged) |
| LineageOS (~159) | `github.com/LineageOS/...` (unchanged) |
| UwU ROM layer (~46) | **Forked into** [`PenguinAOSP`](https://github.com/PenguinAOSP) |
| Penguin device / vendor / patches | PenguinAOSP org repos + `apply-all.sh` |

## Patches are kept

Forked trees start as UwU mirrors. Penguin features stay maintainable via the patch layer in [`PenguinAOSP/PenguinAOSP`](https://github.com/PenguinAOSP/PenguinAOSP):

```bash
# after sync (from tree root)
bash penguin/scripts/apply-all.sh   # if meta cloned at penguin/
# or
bash /path/to/PenguinAOSP/scripts/apply-all.sh
```

Upstream UwU bump → refresh forks / pin → re-run `apply-all.sh` → fix anchors.

## Built with vibe coding

Built with **Cursor / Codex** vibe coding. GitHub Contributors list the human owner only.

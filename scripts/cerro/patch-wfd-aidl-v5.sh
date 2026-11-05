#!/usr/bin/env bash
# RisingOS seventeen / Android 17: WFD prebuilts were extracted against
# android.media.audio.common.types V4, while libmedia/libaudiobase now pull V5.
# Soong forbids one module depending on two versions of the same aidl_interface.
# Keep WFD shipped; point soong at V5 (platform) and skip ELF DT_NEEDED vs V4.
#
# PenguinOS: hooked into apply-all as PENGUIN_WFD_AIDL_V5 (M1 soong blocker).
# Target is vendor/nubia blobs (local_manifest), not devices/ truth source.
# Idempotent: V4→V5 replace no-ops when already V5; ELF flags skip if present.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE="${SOURCE_DIR:-$ROOT/source}"
BP="$SOURCE/vendor/nubia/sm8650-common/Android.bp"
[[ -f "$BP" ]] || { echo "[wfd-aidl-v5] skip missing $BP"; exit 0; }
if grep -q 'android.media.audio.common.types-V5-cpp' "$BP" \
    && ! grep -q 'android.media.audio.common.types-V4-cpp' "$BP" \
    && grep -q 'name: "libwfdservice"' "$BP" \
    && grep -A5 'name: "libwfdservice"' "$BP" | grep -q 'check_elf_files: false'; then
    echo "[wfd-aidl-v5] skip (already applied): $BP"
    exit 0
fi
python3 - "$BP" <<'PY'
from pathlib import Path
import re
import sys

p = Path(sys.argv[1])
text = p.read_text(encoding="utf-8")
pattern = re.compile(r'cc_prebuilt_library_shared \{\n    name: "(libwfd[^"]*)",')
count = 0
out = []
i = 0
while True:
    m = pattern.search(text, i)
    if not m:
        out.append(text[i:])
        break
    out.append(text[i : m.start()])
    name = m.group(1)
    start = m.start()
    brace = 0
    j = start
    while j < len(text):
        if text[j] == "{":
            brace += 1
        elif text[j] == "}":
            brace -= 1
            if brace == 0:
                j += 1
                break
        j += 1
    block = text[start:j]
    if "check_elf_files: false" not in block:
        block = block.replace(
            f'name: "{name}",',
            f'name: "{name}",\n    check_elf_files: false,\n    allow_undefined_symbols: true,',
            1,
        )
        count += 1
    elif "allow_undefined_symbols: true" not in block:
        block = block.replace(
            "check_elf_files: false,",
            "check_elf_files: false,\n    allow_undefined_symbols: true,",
            1,
        )
        count += 1
    out.append(block)
    i = j
text2 = "".join(out).replace(
    "android.media.audio.common.types-V4-cpp",
    "android.media.audio.common.types-V5-cpp",
)
p.write_text(text2, encoding="utf-8")
print(f"[wfd-aidl-v5] patched {count} libwfd* modules in {p}")
PY

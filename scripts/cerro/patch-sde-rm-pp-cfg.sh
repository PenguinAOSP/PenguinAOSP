#!/usr/bin/env bash
# _sde_rm_reserve_pp took pp_cfg as an argument then overwrote it.
# Caller never assigned it → clang -Werror -Wuninitialized.
# Make pp_cfg local to the callee (it was never an input).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="${SOURCE_DIR:-$ROOT/source}"
f="$SOURCE/kernel/nubia/sm8650-modules/qcom/opensource/display-drivers/msm/sde/sde_rm.c"
[[ -f "$f" ]] || { echo "[sde-rm-pp] skip missing $f"; exit 0; }
python3 - "$f" <<'PY'
from pathlib import Path
import sys

p = Path(sys.argv[1])
text = p.read_text(encoding="utf-8")
marker = "/* RisingOS cerro: pp_cfg is local"
if marker in text:
    print("[sde-rm-pp] already patched")
    sys.exit(0)

old_fn = """static bool _sde_rm_reserve_pp(
		struct sde_rm *rm,
		struct sde_rm_rsvp *rsvp,
		struct sde_rm_requirements *reqs,
		const struct sde_lm_cfg *lm_cfg,
		const struct sde_pingpong_cfg *pp_cfg,
		struct sde_rm_hw_blk *lm,
		struct sde_rm_hw_blk **dspp,
		struct sde_rm_hw_blk **ds,
		struct sde_rm_hw_blk **pp)
{
	struct sde_rm_hw_iter iter;
"""
new_fn = """static bool _sde_rm_reserve_pp(
		struct sde_rm *rm,
		struct sde_rm_rsvp *rsvp,
		struct sde_rm_requirements *reqs,
		const struct sde_lm_cfg *lm_cfg,
		struct sde_rm_hw_blk *lm,
		struct sde_rm_hw_blk **dspp,
		struct sde_rm_hw_blk **ds,
		struct sde_rm_hw_blk **pp)
{
	const struct sde_pingpong_cfg *pp_cfg; /* RisingOS cerro: pp_cfg is local */
	struct sde_rm_hw_iter iter;
"""
if old_fn not in text:
    sys.exit(f"[sde-rm-pp] function block not found in {p}")
text = text.replace(old_fn, new_fn, 1)

old_call = """	ret = _sde_rm_reserve_pp(rm, rsvp, reqs, lm_cfg, pp_cfg, lm,
			dspp, ds, pp);
"""
new_call = """	ret = _sde_rm_reserve_pp(rm, rsvp, reqs, lm_cfg, lm,
			dspp, ds, pp);
"""
if old_call not in text:
    sys.exit(f"[sde-rm-pp] call site not found in {p}")
text = text.replace(old_call, new_call, 1)

old_decl = """	const struct sde_lm_cfg *lm_cfg = to_sde_hw_mixer(lm->hw)->cap;
	const struct sde_pingpong_cfg *pp_cfg;
	bool ret, is_conn_primary, is_conn_secondary;
"""
new_decl = """	const struct sde_lm_cfg *lm_cfg = to_sde_hw_mixer(lm->hw)->cap;
	bool ret, is_conn_primary, is_conn_secondary;
"""
if old_decl not in text:
    sys.exit(f"[sde-rm-pp] caller pp_cfg decl not found in {p}")
text = text.replace(old_decl, new_decl, 1)

p.write_text(text, encoding="utf-8")
print("[sde-rm-pp] patched", p)
PY

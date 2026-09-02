# -*- coding: utf-8 -*-
"""handedness_v3_stratified.py -- POST-HOC, referee-prompted, NOT preregistered.

A statistical referee (2026-09-02) objected that the header/line gap in
handedness_v3_result.json is a token-kind composition effect: the header cell is mostly decimals
and decimals are almost always claims, so the two cells are not comparable. This script
re-derives that stratification from the committed rows and writes it as a receipt so the
objection can be sworn to beside the result it attacks. It moves no gate. The v3 verdict was
scored on the raw delta, as frozen; this is the reading's correction, not the verdict's.

  python handedness_v3_stratified.py
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "handedness_v3_result.json"
OUT = HERE / "handedness_v3_stratified.json"


def kind(tok: str) -> str:
    t = str(tok)
    return "comma" if "," in t else ("decimal" if "." in t else "integer")


def main() -> int:
    rows = json.loads(SRC.read_text(encoding="utf-8"))["rows"]
    cells = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for x in rows:
        c = x["cell"]
        if c not in ("header", "line"):
            continue
        k = kind(x["token"])
        cells[c][k][1] += 1
        cells[c][k][0] += int(x["panel"] == "CLAIM")
    out = {"what": __doc__.strip().splitlines()[0], "source": SRC.name, "post_hoc": True, "preregistered": False,
           "by_kind": {c: {k: {"genuine": v[0], "n": v[1], "share": round(v[0] / v[1], 4)}
                          for k, v in sorted(cells[c].items())} for c in ("header", "line")}}
    for c in ("header", "line"):
        g = sum(v[0] for v in cells[c].values()); n = sum(v[1] for v in cells[c].values())
        out["by_kind"][c]["all"] = {"genuine": g, "n": n, "share": round(g / n, 4)}
    num = den = 0.0
    for k in set(cells["header"]) | set(cells["line"]):
        a, n1 = cells["header"][k]; b, n2 = cells["line"][k]
        if n1 and n2:
            w = n1 * n2 / (n1 + n2); num += w * (a / n1 - b / n2); den += w
    nh = out["by_kind"]["header"]["all"]["n"]; gh = out["by_kind"]["header"]["all"]["genuine"]
    std = sum((cells["header"][k][1] / nh) * (cells["line"][k][0] / cells["line"][k][1])
              for k in cells["line"] if cells["header"][k][1])
    out["raw_delta_header_minus_line"] = round(gh / nh - out["by_kind"]["line"]["all"]["share"], 4)
    out["kind_adjusted_delta_mh_weights"] = round(num / den, 4)
    out["line_standardized_to_header_kind_mix"] = round(std, 4)
    out["standardized_delta"] = round(gh / nh - std, 4)
    out["decimal_share_of_header_cell"] = round(cells["header"]["decimal"][1] / nh, 4)
    out["frozen_bar_for_the_raw_delta"] = 0.15
    out["kind_adjusted_delta_clears_the_frozen_bar"] = bool(num / den >= 0.15)
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "by_kind"}, indent=1))
    print(json.dumps(out["by_kind"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# -*- coding: utf-8 -*-
"""handedness_accusations_v4.py -- frozen by PREREG_handedness_v4_own_label_2026_09_02.

Re-splits v3's joined rows by the author's OWN label: the token's own column header or its own
row label carries a trigger (STRUCTURAL) or not (INCIDENTAL). Reads the corpus from the
hash-verified cache; re-judges nothing.
"""
from __future__ import annotations

import collections
import hashlib
import importlib
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
from styxx.protocol import Experiment                    # noqa: E402

C = importlib.import_module("styxx.certify")            # the name-shadow trap: never `import styxx.certify as C`
PREREG = HERE / "PREREG_handedness_v4_own_label_2026_09_02.md"
V3 = HERE / "handedness_v3_result.json"
LEDGER = HERE / "oath_external_epistemics_ledger.jsonl"
CORPUS = HERE / "oath_external_corpus.json"
CACHE = Path(os.environ.get("OATH_EXT_CACHE", Path(os.environ.get("TEMP", "/tmp")) / "oath_ext_corpus_cache"))
EIGHT = ["T0224", "T0229", "T0234", "T0239", "T0244", "T0249", "T0141", "T0181"]


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None]
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 4), round(c + h, 4)]


def kind(tok):
    t = str(tok)
    return "comma" if "," in t else ("decimal" if "." in t else "integer")


def docs():
    m = json.loads(CORPUS.read_text(encoding="utf-8"))
    out = {}
    for rec in m["per_repo"]:
        if rec.get("status") != "CERTIFIED":
            continue
        for f in rec["files"]:
            if f["role"] != "document":
                continue
            key = hashlib.sha256(f"{rec['repo']}@{rec['sha']}/{f['path']}".encode()).hexdigest()[:32]
            b = CACHE / key
            if b.exists() and hashlib.sha256(b.read_bytes()).hexdigest() == f["sha256"]:
                out[rec["repo"]] = b.read_bytes().decode("utf-8", errors="replace")
    return out


def cells_of(line: str):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def classify(text: str, ln: int, col: int):
    lines = text.splitlines()
    table = C._table_rows(lines)
    if ln not in table or not (0 < ln <= len(lines)):
        return {"is_table": False, "own_label": "", "row_label": "", "structural": False}
    line = lines[ln - 1].replace("−", "-")
    header = lines[table[ln] - 1]
    k = line[:col].count("|")
    idx = k - 1 if line.lstrip().startswith("|") else k
    hc = cells_of(header)
    own = hc[idx] if 0 <= idx < len(hc) else ""
    row_label = cells_of(line)[0] if cells_of(line) else ""
    structural = bool(C._TRIGGERS.search(own)) or bool(C._TRIGGERS.search(row_label))
    return {"is_table": True, "own_label": own[:60], "row_label": row_label[:60], "structural": structural}


def share(rows):
    n = len(rows); g = sum(r["genuine"] for r in rows)
    return {"n": n, "genuine": g, "share": round(g / n, 4) if n else None, "wilson": wilson(g, n)}


def mh_delta(a_rows, b_rows):
    num = den = 0.0
    ks = {r["kind"] for r in a_rows} | {r["kind"] for r in b_rows}
    for k in ks:
        a = [r for r in a_rows if r["kind"] == k]; b = [r for r in b_rows if r["kind"] == k]
        if a and b:
            w = len(a) * len(b) / (len(a) + len(b))
            num += w * (sum(r["genuine"] for r in a) / len(a) - sum(r["genuine"] for r in b) / len(b)); den += w
    return round(num / den, 4) if den else None


def main() -> int:
    v3 = json.loads(V3.read_text(encoding="utf-8"))
    led = {}
    for l in LEDGER.read_text(encoding="utf-8").splitlines():
        d = json.loads(l)
        if d["status"] == "UNGROUNDED":
            led[(d["repo"], int(d["line"]), d["token"])] = d
    texts = docs()
    rows, missing = [], 0
    for x in v3["rows"]:
        if x["cell"] not in ("header", "line"):
            continue
        t = texts.get(x["repo"])
        if t is None:
            missing += 1
            continue
        col = int(led[(x["repo"], x["line"], x["token"])]["col"])
        cl = classify(t, x["line"], col)
        rows.append({**x, "col": col, "kind": kind(x["token"]), "genuine": x["panel"] == "CLAIM",
                     "v4_cell": "structural" if cl["structural"] else "incidental", **cl})
    S = [r for r in rows if r["v4_cell"] == "structural"]; I = [r for r in rows if r["v4_cell"] == "incidental"]
    top = collections.Counter(r["repo"] for r in rows).most_common(1)[0][0]
    S_ex = [r for r in S if r["repo"] != top]; I_ex = [r for r in I if r["repo"] != top]
    eight = {r["id"]: r["v4_cell"] for r in rows if r["id"] in EIGHT}
    line_table_to_S = sum(1 for r in rows if r["cell"] == "line" and r["is_table"] and r["v4_cell"] == "structural")
    metrics = {"docs_missing": missing,
               "eight_named_rows_not_incidental": sum(1 for i in EIGHT if eight.get(i) != "incidental"),
               "line_table_rows_reclassified_structural": line_table_to_S,
               "min_cell_n_ex_top_repo": min(len(S_ex), len(I_ex)),
               "delta_ex_top_repo": round(share(S_ex)["share"] - share(I_ex)["share"], 4) if S_ex and I_ex else -1.0,
               "kind_adjusted_delta_all": mh_delta(S, I) if S and I else -1.0}
    res = {"prereg": PREREG.name, "source": V3.name, "rows_joined": len(rows), "largest_repo": top,
           "cells": {"structural": share(S), "incidental": share(I)},
           "cells_ex_top_repo": {"structural": share(S_ex), "incidental": share(I_ex)},
           "raw_delta_all": round(share(S)["share"] - share(I)["share"], 4) if S and I else None,
           "by_kind": {c: {k: share([r for r in rs if r["kind"] == k]) for k in ("decimal", "integer", "comma")}
                       for c, rs in (("structural", S), ("incidental", I))},
           "table_vs_prose": {"table": share([r for r in rows if r["is_table"]]),
                              "prose": share([r for r in rows if not r["is_table"]])},
           "v3_cell_by_v4_cell": {f"{a}_to_{b}": sum(1 for r in rows if r["cell"] == a and r["v4_cell"] == b)
                                  for a in ("header", "line") for b in ("structural", "incidental")},
           "eight_named_rows": eight, "metrics": metrics, "rows": rows}
    v = Experiment(PREREG, repo_root=ROOT).score(metrics, smoke=False)
    res["verdict"], res["gates"] = v.verdict, v.gates
    (HERE / "handedness_v4_result.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("cells", "cells_ex_top_repo", "raw_delta_all", "table_vs_prose", "v3_cell_by_v4_cell", "eight_named_rows", "metrics")}, indent=1))
    print(json.dumps(res["by_kind"]))
    print(f"\n===== VERDICT: {res['verdict']} =====")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

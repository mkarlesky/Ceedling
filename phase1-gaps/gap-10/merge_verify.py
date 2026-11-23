#!/usr/bin/env python3
"""Merges verifier verdicts and adjudicator rulings into phase1-gaps/gap-10.json.

Inputs under phase1-gaps/gap-10/verify/: batch_N.json (findings), verdicts.json (list of
{id, verdict, evidence, note}), rulings.json (list of {id, final, revised_claim, reason}).
A finding is `confirmed` when its verdict is confirmed. Otherwise the ruling's `final` decides:
confirmed, revised (claim replaced, old text kept as original_claim) or refuted.
"""
import json, os, glob

here = os.path.dirname(os.path.abspath(__file__))
findings = json.load(open(os.path.join(here, "findings_src.json")))
verdicts = {v["id"]: v for v in json.load(open(os.path.join(here, "verify", "verdicts.json")))}
rpath = os.path.join(here, "verify", "rulings.json")
rulings = {r["id"]: r for r in json.load(open(rpath))} if os.path.exists(rpath) else {}

out = []
for f in findings:
    v = verdicts[f["id"]]
    f = dict(f)
    f["verdict"] = {"verdict": v["verdict"], "note": v.get("note", "")}
    if v["verdict"] == "confirmed":
        f["status"] = "confirmed"
        f["ruling"] = None
    else:
        r = rulings[f["id"]]
        f["ruling"] = {"final": r["final"], "reason": r["reason"]}
        if r["final"] == "confirmed":
            f["status"] = "confirmed"
        elif r["final"] == "revised":
            f["status"] = "revised"
            f["original_claim"] = f["claim"]
            f["claim"] = r["revised_claim"]
        else:
            f["status"] = "refuted"
    out.append(f)

json.dump(out, open(os.path.join(here, "..", "gap-10.json"), "w"), indent=1, ensure_ascii=False)
from collections import Counter
print(Counter(f["status"] for f in out))

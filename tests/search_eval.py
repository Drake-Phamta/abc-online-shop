# -*- coding: utf-8 -*-
"""Offline evaluation of the AI search (docs/SPEC.md 6.2) against a running server with the demo data.

Text: the 30 labelled queries of tests/search/queries.json through the keyword search of UC04 (GET /api/products?q=)
and through the AI search (GET /api/search?q=). Measures per method:
  hit@1        share of queries whose first result is relevant
  recall@5     share of the relevant products found in the first five results (averaged over queries)
  MRR          mean of 1 / rank of the first relevant result (0 when none)
  zero result  share of queries with no result at all
  latency      median and maximum server time (AI search) or round-trip time (keyword search)
Photo: the 84 photos of tests/search/photos (python tests/search/make_photos.py) through POST /api/search/photo;
top-1 and top-3 accuracy of the product the photo shows, per kind of photo.
Usage: python tests/search_eval.py [base-url]   writes docs/evidence/search_eval.txt; exit code 1 when the AI search
does not beat the keyword search on MRR or when photo top-1 accuracy is under 0.8.
"""
import json
import statistics
import sys
import time
import urllib.parse
import urllib.request
import uuid
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
QUERIES = json.loads((ROOT / "tests" / "search" / "queries.json").read_text(encoding="utf-8"))["queries"]
PHOTOS = ROOT / "tests" / "search" / "photos"
OUT = ROOT / "docs" / "evidence" / "search_eval.txt"


def get(path):
    t0 = time.perf_counter()
    with urllib.request.urlopen(BASE + path) as r:
        data = json.load(r)
    return data, (time.perf_counter() - t0) * 1000


def post_photo(path):
    boundary = uuid.uuid4().hex
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"photo\"; filename=\"{path.name}\"\r\n"
            f"Content-Type: image/jpeg\r\n\r\n").encode() + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(BASE + "/api/search/photo", data=body, method="POST",
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def score(ranked, relevant):
    rel = set(relevant)
    first = next((i + 1 for i, s in enumerate(ranked) if s in rel), None)
    return {
        "hit1": 1.0 if ranked[:1] and ranked[0] in rel else 0.0,
        "recall5": len(rel & set(ranked[:5])) / len(rel),
        "rr": 1.0 / first if first else 0.0,
        "zero": 1.0 if not ranked else 0.0,
    }


def main():
    lines, rows = [], []
    totals = {"keyword": defaultdict(float), "ai": defaultdict(float)}
    times = {"keyword": [], "ai": []}
    for item in QUERIES:
        q = urllib.parse.quote(item["q"])
        kw, t_kw = get(f"/api/products?q={q}")
        ai, _ = get(f"/api/search?q={q}")
        kw_ranked = [p["sku"] for p in kw]
        ai_ranked = [r["product"]["sku"] for r in ai["results"]] if not ai["fallback"] else [r["product"]["sku"] for r in ai["results"]]
        times["keyword"].append(t_kw)
        times["ai"].append(ai["tookMs"])
        s_kw, s_ai = score(kw_ranked, item["relevant"]), score(ai_ranked, item["relevant"])
        for k, v in s_kw.items():
            totals["keyword"][k] += v
        for k, v in s_ai.items():
            totals["ai"][k] += v
        rows.append((item["q"], item["type"], s_kw, s_ai, ai_ranked[:3], ai["mode"]))
    n = len(QUERIES)
    lines.append(f"AI search evaluation, {time.strftime('%Y-%m-%d %H:%M')}, server {BASE}")
    lines.append(f"Text: {n} labelled queries (tests/search/queries.json)")
    lines.append("")
    lines.append(f"{'method':10} {'hit@1':>7} {'recall@5':>9} {'MRR':>6} {'zero result':>12} {'median ms':>10} {'max ms':>7}")
    for m, label in (("keyword", "keyword"), ("ai", "AI search")):
        t = totals[m]
        lines.append(f"{label:10} {t['hit1'] / n:7.2f} {t['recall5'] / n:9.2f} {t['rr'] / n:6.2f} {t['zero'] / n:12.2f} "
                     f"{statistics.median(times[m]):10.0f} {max(times[m]):7.0f}")
    lines.append("")
    lines.append("Per query (RR = 1 / rank of the first relevant result; AI top 3 by SKU):")
    for q, typ, s_kw, s_ai, top, mode in rows:
        lines.append(f"  {q[:34]:34} {typ:11} keyword RR {s_kw['rr']:.2f} | AI RR {s_ai['rr']:.2f} {'(fallback)' if mode == 'KEYWORD' else '':10} {', '.join(top)}")

    by_kind = defaultdict(lambda: [0, 0, 0])
    photo_ms = []
    misses = []
    photos = sorted(PHOTOS.glob("*.jpg"))
    for f in photos:
        sku, kind = f.stem.rsplit("_", 1)
        r = post_photo(f)
        photo_ms.append(r["tookMs"])
        ranked = [x["product"]["sku"] for x in r["results"]]
        by_kind[kind][0] += 1
        by_kind[kind][1] += 1 if ranked[:1] == [sku] else 0
        by_kind[kind][2] += 1 if sku in ranked[:3] else 0
        if ranked[:1] != [sku]:
            misses.append(f"{f.name}: first {ranked[0] if ranked else 'none'}, true product at {ranked.index(sku) + 1 if sku in ranked else '-'}")
    lines.append("")
    lines.append(f"Photo: {len(photos)} photos made from the catalogue images (tests/search/make_photos.py)")
    lines.append(f"{'kind':12} {'photos':>6} {'top-1':>6} {'top-3':>6}")
    all_n = all_1 = all_3 = 0
    for kind, (cnt, t1, t3) in sorted(by_kind.items()):
        lines.append(f"{kind:12} {cnt:6} {t1 / cnt:6.2f} {t3 / cnt:6.2f}")
        all_n, all_1, all_3 = all_n + cnt, all_1 + t1, all_3 + t3
    lines.append(f"{'all':12} {all_n:6} {all_1 / all_n:6.2f} {all_3 / all_n:6.2f}   median {statistics.median(photo_ms):.0f} ms, max {max(photo_ms)} ms")
    if misses:
        lines.append("Photos whose product was not first:")
        lines.extend("  " + m for m in misses)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    ok = totals["ai"]["rr"] > totals["keyword"]["rr"] and all_1 / all_n >= 0.8
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

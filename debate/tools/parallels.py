#!/usr/bin/env python3
"""Find shared character strings (parallel passages) between two Kanripo texts.

Usage:
    python3 debate/tools/parallels.py <dirA> <dirB> [--n 10] [--out report.md]

Each dir is a Kanripo text folder (debate/bibliography/local/kanripo/KR1e0001 etc.).
The tool strips Kanripo markup (org headers, <pb:…> leaf markers, ¶, punctuation, and
double-column commentary in parentheses) and reports every maximal run of >= n identical
characters that occurs in both corpora, with the juan and leaf marker of each occurrence.

Interpretation caveats (write them into any argument that uses the numbers):
- Shared strings include formulaic phrases (「君子曰」「對曰」…) and quotations from a common
  source (《詩》《書》); only long runs (>= 15) are interesting as text-level parallels.
- Commentary (韋昭注, 顏師古注) is removed by dropping parenthesised runs, which is only
  approximately right for the Siku layout.
"""
import argparse, glob, os, re, sys
from collections import defaultdict

PUNCT = "，。、；：？！「」『』（）()《》〈〉—…·,.;:?!\"' \n\t　"

def load(d):
    """Return list of (juan, leaf, cleaned_text) chunks, one per leaf."""
    chunks = []
    for f in sorted(glob.glob(os.path.join(d, "*_[0-9]*.txt"))):
        juan = os.path.basename(f).rsplit("_", 1)[1].split(".")[0]
        leaf = "?"
        buf = []
        for line in open(f, encoding="utf-8", errors="ignore"):
            if line.startswith("#"):
                continue
            m = re.search(r"<pb:([^>]+)>", line)
            if m:
                if buf:
                    chunks.append((juan, leaf, "".join(buf)))
                    buf = []
                leaf = m.group(1).split("_")[-1]
                line = line[m.end():]
            line = re.sub(r"\([^)]*\)", "", line)      # drop inline commentary
            line = re.sub(r"<[^>]*>", "", line)
            line = "".join(ch for ch in line if ch not in PUNCT and ch != "¶")
            buf.append(line)
        if buf:
            chunks.append((juan, leaf, "".join(buf)))
    return chunks

def index(chunks, n):
    idx = defaultdict(list)
    for ci, (_, _, t) in enumerate(chunks):
        for i in range(len(t) - n + 1):
            idx[t[i:i + n]].append((ci, i))
    return idx

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a"); ap.add_argument("b")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--out")
    ap.add_argument("--min-report", type=int, default=0, help="only report runs of at least this length (default n)")
    a = ap.parse_args()
    A, B = load(a.a), load(a.b)
    ia = index(A, a.n)
    hits = {}
    for cj, (_, _, tb) in enumerate(B):
        i = 0
        while i <= len(tb) - a.n:
            g = tb[i:i + a.n]
            if g in ia:
                # extend to maximal run against the first A occurrence
                ci, ai = ia[g][0]
                ta = A[ci][2]
                L = a.n
                while ai + L < len(ta) and i + L < len(tb) and ta[ai + L] == tb[i + L]:
                    L += 1
                s = tb[i:i + L]
                key = (ci, ai, cj, i)
                hits[key] = (L, s)
                i += L
            else:
                i += 1
    mr = a.min_report or a.n
    rows = sorted(((L, s, k) for k, (L, s) in hits.items() if L >= mr), reverse=True)
    lines = [f"# Parallel passages: {a.a} vs {a.b} (n>={mr})", "",
             f"chunks A={len(A)} B={len(B)}; shared runs>={mr}: {len(rows)}; "
             f"runs>=15: {sum(1 for L,_,_ in rows if L>=15)}; runs>=30: {sum(1 for L,_,_ in rows if L>=30)}", "",
             "| len | A (juan/leaf) | B (juan/leaf) | text |", "| --- | --- | --- | --- |"]
    for L, s, (ci, ai, cj, bi) in rows:
        lines.append(f"| {L} | {A[ci][0]}/{A[ci][1]} | {B[cj][0]}/{B[cj][1]} | {s[:60]}{'…' if L>60 else ''} |")
    out = "\n".join(lines)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(out)
        print(lines[2], file=sys.stderr); print(f"wrote {a.out}", file=sys.stderr)
    else:
        print(out)

if __name__ == "__main__":
    main()

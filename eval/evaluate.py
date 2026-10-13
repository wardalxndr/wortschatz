"""Evaluasi retrieval v1: hit@1/3/5 + MRR lawan gold set. Gratis, tanpa LLM.

Jalankan dari root:  python eval/evaluate.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ingest"))

from build_index import build_index
from words import WORDS


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, "gold_set.json")) as f:
        gold = json.load(f)

    index = build_index(WORDS)
    k = 5
    hits = {1: 0, 3: 0, 5: 0}
    mrr = 0.0
    misses = []
    weak = []

    for item in gold:
        ids = [r["id"] for r in index.search(item["question"], num_results=k)]
        if item["expected_id"] in ids:
            rank = ids.index(item["expected_id"]) + 1
            mrr += 1.0 / rank
            for kk in hits:
                if rank <= kk:
                    hits[kk] += 1
            if rank > 1:
                weak.append((item["question"], item["expected_id"], rank, ids[0]))
        else:
            misses.append(item["question"])

    n = len(gold)
    print(f"n={n}")
    print(f"hit@1: {hits[1]/n:.2f}  hit@3: {hits[3]/n:.2f}  hit@5: {hits[5]/n:.2f}  mrr: {mrr/n:.3f}")
    if weak:
        print("weak (rank 2-5, expected kalah sama siapa):")
        for q, exp, rank, winner in weak:
            print(f" - {q!r} -> {exp} di rank {rank}, rank 1 direbut {winner}")
    if misses:
        print("misses:")
        for q in misses:
            print(" -", q)


if __name__ == "__main__":
    main()

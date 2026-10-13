"""Contoh pemakaian Tatoeba (CC-BY): ambil contoh kalimat per kata (opsional).

Jalankan dari root:  python scripts/fetch_tatoeba.py
Hasil: data/tatoeba_examples.json  {word: [{de, en}, ...]}
Butuh internet. Kalau gagal, UI tetap jalan tanpa contoh kalimat.
"""

import json
import os
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ingest"))

from words import WORDS

SAMPLE_WORDS = ["Haus", "Handschuh", "Bahnhof", "lieben", "Wasser", "Hund", "Buch", "Essen"]


def fetch_examples(word, n=2):
    q = urllib.parse.quote(word)
    url = f"https://tatoeba.org/en/api_v0/search?from=deu&to=eng&query={q}&limit={n}"
    req = urllib.request.Request(url, headers={"User-Agent": "WortSchatz/0.1 (learning project)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    out = []
    for r in data.get("results", []):
        de_text = r.get("text", "")
        en_text = ""
        for t in r.get("translations", [[]])[0]:
            if isinstance(t, dict) and t.get("text"):
                en_text = t["text"]
                break
        if de_text and en_text:
            out.append({"de": de_text, "en": en_text})
    return out


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_path = os.path.join(base, "data", "tatoeba_examples.json")
    all_examples = {}
    for w in SAMPLE_WORDS:
        try:
            all_examples[w] = fetch_examples(w)
            print(f"{w}: {len(all_examples[w])} examples")
        except Exception as e:  # noqa: BLE001 - offline tetap lanjut
            print(f"{w}: skipped ({e})")
            all_examples[w] = []
        time.sleep(1)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_examples, f, ensure_ascii=False, indent=1)
    print("saved", out_path)


if __name__ == "__main__":
    main()

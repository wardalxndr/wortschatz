"""Ingestion v1: index keyword (minsearch) dari seed dictionary.

Jalankan dari root repo:  python ingest/build_index.py
"""

from minsearch import Index

from words import WORDS


def build_index(documents=None):
    docs = documents if documents is not None else WORDS
    index = Index(
        text_fields=["de", "en", "note"],
        keyword_fields=["pos", "cefr"],
    )
    index.fit(docs)
    return index


def vocab():
    return {w["de"].lower() for w in WORDS}


def main():
    index = build_index()
    print(f"indexed {len(WORDS)} words")
    for q in ["apple", "to arrive", "glove"]:
        top = index.search(q, num_results=1)[0]
        print(f"- {q!r:12} -> {top['de']} ({top['en']})")


if __name__ == "__main__":
    main()

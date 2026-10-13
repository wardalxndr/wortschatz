"""Compound splitter — senjata utama WortSchatz (padanan Sudachi-nya Reikun).

Jerman nempel kata seenaknya: Handschuh = Hand + Schuh (sepatu tangan = sarung
tangan). Splitter mecah kata majemuk jadi potongan kamus pakai longest-match
rekursif + Fugen-linker (s/es/n/en di sambungan, misal Woche+n+Ende).
"""

FUGEN = ("en", "es", "er", "n", "s")


def split_compound(word, vocab, max_parts=4):
    """Balikin list potongan, misal ['donau', 'dampf', 'schiff', 'fahrt'].

    vocab: set lowercase headword kamus. Satu kata utuh -> [word].
    """
    w = word.lower()
    memo = {}

    def rec(start):
        if start == len(w):
            return []
        if start in memo:
            return memo[start]
        best_multi = None
        fallback = None
        # coba prefix terpanjang dulu; kata utuh cuma fallback,
        # pecahan multi-part selalu menang biar demo jalan
        for end in range(len(w), start, -1):
            piece = w[start:end]
            linker = ""
            base = piece
            if piece not in vocab:
                for f in FUGEN:
                    if len(piece) > len(f) and piece.endswith(f) and piece[: -len(f)] in vocab:
                        base = piece[: -len(f)]
                        linker = f
                        break
            if base not in vocab:
                continue
            if end == len(w):
                fallback = [(base, linker)]
            else:
                tail = rec(end)
                if tail is None:
                    continue
                cand = [(base, linker)] + tail
                if len(cand) <= max_parts and (best_multi is None or len(cand) < len(best_multi)):
                    best_multi = cand
        memo[start] = best_multi or fallback
        return memo[start]

    found = rec(0)
    if not found or len(found) < 2:
        return [w]
    # gabung linker ke potongan biar enak dibaca: wochen+ende
    return [base + linker for base, linker in found]


def is_compound(word, vocab):
    return len(split_compound(word, vocab)) > 1

# 📖 WortSchatz — German dictionary

Search English or German, inspect gender and plurals, split compound words
(Donaudampfschifffahrt!), get grammar explanations tuned to your CEFR level.
Terinspirasi arsitektur [Reikun](https://github.com/AnkS4/Reikun) (kamus Jepang,
LLM Zoomcamp score 26), dibangun ulang buat bahasa Jerman.

## Quick start

```bash
cp .env.example .env   # isi GROQ_API_KEY dari https://console.groq.com/keys
pip install -r requirements.txt
python ingest/build_index.py   # cek 150+ kata masuk
python eval/evaluate.py        # hit@k + MRR
streamlit run app/app.py       # :8501
```

## Struktur

```
app/            UI Streamlit ala landing Reikun + feedback
ingest/         seed dictionary (words.py) + build index minsearch
rag/            splitter.py (compound!), dictionary.py (search + explain)
eval/           gold_set.json + hit@k/MRR
scripts/        fetch_tatoeba.py (contoh kalimat CC-BY, opsional)
docs/           DATA_SOURCES.md (aturan lisensi kamus)
```

## Status evaluasi (v1, keyword only)

Jalankan `python eval/evaluate.py` buat angka terbaru.
Target v2: dump Wiktionary Jerman + hybrid + rerank + LLM judge.

## Roadmap

- [ ] Spot-check gender/plural/level seed lawan referensi
- [ ] Contoh kalimat Tatoeba tampil di kartu entri
- [ ] Wiktionary DE dump (skala Reikun ~200k entri)
- [ ] Hybrid + rerank, pilih pemenang pakai angka
- [ ] Deploy live + demo video + tabel rubrik

"""Smoke test: index, splitter, dan search gold inti."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ingest"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rag"))

from build_index import build_index, vocab
from splitter import split_compound
from words import WORDS


def test_vocab_size():
    assert len(WORDS) >= 100


def test_famous_compound():
    v = vocab()
    assert split_compound("Donaudampfschifffahrt", v) == ["donau", "dampf", "schiff", "fahrt"]


def test_glove_compound():
    v = vocab()
    assert split_compound("Handschuh", v) == ["hand", "schuh"]


def test_plain_word_not_split():
    v = vocab()
    assert split_compound("Apfel", v) == ["apfel"]


def test_search_apple():
    index = build_index()
    ids = [r["id"] for r in index.search("apple", num_results=3)]
    assert "apfel" in ids

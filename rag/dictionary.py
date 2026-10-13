"""Search + CEFR grammar explain. Search keyword dulu (v1),
grammar explanation lewat LLM (pola Reikun: on-demand, level-aware).
"""

EXPLAIN_INSTRUCTIONS = """
You explain German for a learner at CEFR level {level}.
Rules: short sentences, no jargon above their level, one example with
English gloss, end with one common mistake to avoid. Max 120 words.
""".strip()

EXPLAIN_PROMPT = """
Word or sentence: {query}
Dictionary context:
{context}

Explain it for a {level} learner.
""".strip()


class WortSearch:
    def __init__(self, index):
        self.index = index

    def search(self, query, cefr=None, num_results=5):
        filters = {"cefr": cefr} if cefr and cefr != "all" else {}
        return self.index.search(
            query,
            num_results=num_results,
            boost_dict={"de": 3.0, "en": 1.5},
            filter_dict=filters,
        )


def build_explain_prompt(query, entries, level):
    lines = []
    for e in entries:
        head = e["de"]
        if e.get("pos") == "noun":
            head = f"{e['de']} ({e.get('gender', '?')}, pl. {e.get('plural', '-')})"
        lines.append(f"- {head} [{e.get('pos', '')}/{e.get('cefr', '')}]: {e.get('en', '')}. {e.get('note', '')}")
    context = "\n".join(lines).strip()
    return EXPLAIN_PROMPT.format(query=query, context=context, level=level)


def explain(llm_client, model, query, entries, level):
    prompt = build_explain_prompt(query, entries, level)
    response = llm_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": EXPLAIN_INSTRUCTIONS.format(level=level)},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()

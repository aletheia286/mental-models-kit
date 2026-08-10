#!/usr/bin/env python3
"""mental-models-kit — a portable, generic decision-support engine, extracted 2026-08-10
from a larger personal knowledge-base project ("the Vault") where it was originally built
and battle-tested. Standalone: no dependency on that project's paths or content.

What it does: a curated table of decision-making / problem-solving mental models
(mm_hub.md + mm_*.md), plus a zero-dependency keyword-overlap matcher that scores a
free-text situation against the table and returns the best-matching category (if any) —
deliberately silent on low-confidence matches (see _mm_score_situation's docstring for why).

CLI:
  python3 mental_models_engine.py mentalmodel "<situation>"
  python3 mental_models_engine.py mm-enrich "<category>" "<word1,word2,...>"
  python3 mental_models_engine.py mm-suggest-words "<category>"
"""
import os
import re
import sys
import json
from datetime import datetime

KIT_DIR = os.path.dirname(os.path.abspath(__file__))
MM_HUB_PATH = os.path.join(KIT_DIR, "_mm_hub.md")
MM_DIR = KIT_DIR
MM_LOG_PATH = os.path.join(KIT_DIR, "_mentalmodel_log.jsonl")
MM_BACKTEST_CASES_PATH = os.path.join(KIT_DIR, "mm_backtest_cases.py")
CHANGELOG_PATH = os.path.join(KIT_DIR, "CHANGELOG.md")

_MM_STOPWORDS = {
    "il", "lo", "la", "i", "gli", "le", "un", "una", "di", "a", "da", "in", "con",
    "su", "per", "tra", "fra", "e", "o", "che", "non", "no", "si", "mi", "ti", "ci",
    "se", "ma", "come", "cosa", "quando", "dove", "perché", "perche", "sono", "è",
    "ho", "hai", "ha", "abbiamo", "avete", "hanno", "questo", "questa", "sto",
    "devo", "puoi", "vuoi", "voglio", "quale", "quali", "aprire", "file",
    # Found live via agentic backtest (39 messages / 12 categories) in the source project:
    # "solo" is generic enough (also means "only", not just "alone") to coincidentally
    # co-occur with almost any topic — confirmed reproducibly causing a WRONG-category
    # match (worse than a miss). "sotto" was a second, lower-severity instance of the same
    # class. Removed here as defense-in-depth alongside the min_score=3 threshold.
    "solo", "sotto",
}

_MM_STEM_MIN_LEN = 6  # chars kept before truncating — see _mm_stem() for why this length


def _mm_stem(word):
    """Light, dependency-free prefix stemming for Italian — the dominant failure mode found
    during backtesting was NOT bad trigger wording but exact-token matching missing regular
    verb/noun/plural variants the trigger text can't spell out for every case: 'rischiare'
    vs 'rischio', 'comunicare' vs 'comunicazione'. A real stemmer/lemmatizer would handle
    this better but pulls in a library dependency this function is deliberately built
    without. Truncating to a 6-char prefix recovers most REGULAR Italian derivational pairs
    at low collision risk. It does NOT fix irregular participle-derived nouns ('decidere'/
    'decisione', 'scegliere'/'scelta') — those are patched directly in mm_hub.md's trigger
    wording instead, since no cheap stemming trick unifies genuine root suppletion."""
    return word[:_MM_STEM_MIN_LEN] if len(word) > _MM_STEM_MIN_LEN else word


def _mm_tokenize(text):
    words = re.findall(r"[a-zàèéìòù]+", text.lower())
    return {_mm_stem(w) for w in words if len(w) > 2 and w not in _MM_STOPWORDS}


def _mm_parse_hub_table(hub_path=None):
    """Parse the trigger table out of _mm_hub.md: category name, trigger text, filename.
    Reads the file live (never hardcodes the table) so this stays in sync automatically
    if the hub's categories change. `hub_path` override exists only for `mm-enrich`'s
    gate, which needs to score against a hypothetical table without ever writing to the
    real file before the gate passes."""
    with open(hub_path or MM_HUB_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    rows = []
    for line in content.splitlines():
        m = re.match(r"^\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|\s*`(mm_[a-z_]+\.md)`\s*\|\s*$", line)
        if m:
            category, trigger_text, filename = m.groups()
            # Drop NON-trigger example clauses (e.g. "Aggiungere un tag → NON trigger.")
            # before scoring — they're explicit negative examples, but plain keyword
            # overlap can't tell a positive mention from a negative one, so left in they
            # cause false positives.
            clean_trigger = ". ".join(
                s for s in re.split(r"(?<=[.!?])\s+", trigger_text.strip())
                if "non trigger" not in s.lower()
            )
            rows.append({"category": category.strip(), "trigger": clean_trigger.strip(), "file": filename.strip()})
    return rows


_MM_MIN_SCORE = 3  # see _mm_score_situation docstring for the full history of this value


def _mm_score_situation(situation, min_score=_MM_MIN_SCORE, rows=None):
    """Shared scoring core for both `mentalmodel` (CLI) and preloader.py (UserPromptSubmit
    hook) — kept in ONE place so a fix here fixes both callers instead of two independent
    copies drifting apart.

    min_score history (found live via two rounds of agentic backtesting on a 39-message /
    12-category set in the source project): started at 1 (any overlap wins), which let a
    single coincidental common word ("solo") outrank the genuinely relevant category.
    Raised to 2 + added a light Italian prefix-stemmer (_mm_stem) + stopworded "solo"/
    "sotto" — accuracy went 25.6%→38.5%, but a SECOND backtest pass found min_score=2 still
    produces wrong-category matches via other generic words — chasing individual stopwords
    case-by-case has diminishing returns. Raised to 3: correct matches drop but wrong-
    category matches go to 0 across the full test set. Kept at 3 deliberately — silence
    (say nothing) is the safe failure mode here, injecting the WRONG mental model's framing
    into the agent's context is the dangerous one; a rarer-but-never-wrong signal beats a
    more-frequent-but-sometimes-misleading one for this specific use case.

    `rows` override (added for `mm-enrich`'s gate): lets a caller score against a
    hypothetical, in-memory hub table instead of re-parsing the real file — the gate builds
    a modified copy of one row's trigger text and scores the SAME backtest against it before
    ever touching mm_hub.md, so a claimed improvement is checked by the tool itself, not by
    trusting whoever proposed it."""
    rows = rows if rows is not None else _mm_parse_hub_table()
    if not rows:
        return [], []
    situation_tokens = _mm_tokenize(situation)
    scored = []
    for row in rows:
        overlap = situation_tokens & _mm_tokenize(row["trigger"])
        scored.append((len(overlap), overlap, row))
    scored.sort(key=lambda x: x[0], reverse=True)
    top_score = scored[0][0]
    if top_score < min_score:
        return [], scored
    matched = [row for score, _, row in scored if score == top_score][:2]
    return matched, scored


def execute_mentalmodel_check(situation):
    """The real (non-promised) technical step behind ambient "consult a mental model"
    instructions: an ambient text instruction with no technical action behind it almost
    never actually fires in practice (confirmed via a blind multi-agent test in the source
    project — 3/4 scenarios never named or opened a model despite textbook trigger
    conditions). This turns the step into an actual tool call: parse the real trigger
    table, score it against the situation with a plain keyword-overlap heuristic (no ML
    dependency — must work anywhere Python runs), print the real content of the matched
    category file (so the model names come from the file, not from memory/hallucination),
    and log the invocation with what was actually returned."""
    if not situation or not situation.strip():
        print('Usage: python3 mental_models_engine.py mentalmodel "<situation>"')
        return
    matched, scored = _mm_score_situation(situation)
    if not scored:
        print("⚠️ No categories found in _mm_hub.md (table format changed?).")
        return

    top_score = scored[0][0] if scored else 0
    near_miss_rows = []
    if not matched:
        print(f"🧭 No category in _mm_hub.md has sufficient lexical overlap with: \"{situation}\"")
        print("   (likely a NON-trigger — routine operation, not a real decision/problem/communication)")
        # Confidence-gated, CLI-only suggestion: only one step below threshold, never in
        # the passive hook (preloader.py stays silent by design) — a single extra line of
        # text, only shown when this command is already being invoked explicitly.
        if top_score == _MM_MIN_SCORE - 1:
            near_miss_rows = [row for score, _, row in scored if score == top_score][:2]
            names = ", ".join(f"{r['category']} (score {top_score})" for r in near_miss_rows)
            print(f"   Closest below threshold — consider if relevant: {names}")
    else:
        print(f"🧭 Situation: \"{situation}\"")
        for row in matched:
            print(f"\n=== Category: {row['category']} → opening ONLY {row['file']} ===")
            mm_file_path = os.path.join(MM_DIR, row["file"])
            try:
                with open(mm_file_path, "r", encoding="utf-8") as f:
                    print(f.read())
            except Exception as e:
                print(f"⚠️ Could not open {row['file']}: {e}")

    log_entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "situation": situation[:300],
        "matched_categories": [row["category"] for row in matched],
        "matched_files": [row["file"] for row in matched],
        "top_score": top_score,
        "near_miss_categories": [row["category"] for row in near_miss_rows],
    }
    try:
        with open(MM_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"⚠️ Invocation log not written: {e}")


def _mm_load_backtest_cases():
    import importlib.util
    spec = importlib.util.spec_from_file_location("mm_backtest_cases", MM_BACKTEST_CASES_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.CASES


def _mm_run_backtest(rows=None):
    """Runs the canonical backtest (mm_backtest_cases.py) against the given hub rows (or
    the real _mm_hub.md if rows=None). This is the ONLY metric `mm-enrich` trusts — a
    proposed change is always re-checked against actual scoring behavior here, never
    against a self-reported claim."""
    cases = _mm_load_backtest_cases()
    correct = 0
    wrong_category = 0
    false_positives = 0
    for expected, msg in cases:
        matched, _ = _mm_score_situation(msg, rows=rows)
        matched_cats = [m["category"] for m in matched]
        if expected is None:
            if matched_cats:
                false_positives += 1
            else:
                correct += 1
        else:
            if expected in matched_cats:
                correct += 1
            elif matched_cats:
                wrong_category += 1
    return {"correct": correct, "total": len(cases), "wrong_category": wrong_category, "false_positives": false_positives}


def _mm_fmt_metrics(m):
    return f"{m['correct']}/{m['total']} correct, {m['wrong_category']} wrong-category, {m['false_positives']} false positives"


def execute_mm_enrich(category_name, words_csv):
    """Gated, reproducible vocabulary enrichment for _mm_hub.md. The gate is IN the tool:
    a proposed addition is scored against the real backtest both before and after, in-
    memory, and only lands in the real file if no metric got worse — never a self-reported
    claim trusted on faith."""
    if not category_name or not words_csv:
        print('Usage: python3 mental_models_engine.py mm-enrich "<Category>" "word1,word2,..."')
        return

    rows = _mm_parse_hub_table()
    target = next((r for r in rows if r["category"] == category_name), None)
    if target is None:
        print(f"❌ Category '{category_name}' not found. Available: {[r['category'] for r in rows]}")
        return

    new_words = [w.strip() for w in words_csv.split(",") if w.strip()]
    if not new_words:
        print("❌ No valid words provided.")
        return

    baseline = _mm_run_backtest(rows=None)
    print(f"Baseline (current _mm_hub.md): {_mm_fmt_metrics(baseline)}")

    modified_rows = [
        {**r, "trigger": r["trigger"] + ". Also includes: " + ", ".join(new_words) + "."}
        if r["category"] == category_name else r
        for r in rows
    ]
    proposed = _mm_run_backtest(rows=modified_rows)
    print(f"Proposed (+{new_words} on '{category_name}'): {_mm_fmt_metrics(proposed)}")

    regressed = (
        proposed["wrong_category"] > baseline["wrong_category"]
        or proposed["false_positives"] > baseline["false_positives"]
        or proposed["correct"] < baseline["correct"]
    )
    if regressed:
        print("❌ REJECTED — at least one metric got worse (wrong-category, false positives, or accuracy). _mm_hub.md untouched.")
        return

    _mm_apply_enrichment_to_file(category_name, new_words)
    print(f"✅ Applied to _mm_hub.md. {baseline['correct']}/{baseline['total']} → {proposed['correct']}/{proposed['total']} correct (net-neutral-or-better on every metric).")
    _mm_log_enrichment_to_history(category_name, new_words, baseline, proposed)


def _mm_apply_enrichment_to_file(category_name, new_words):
    pattern = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|\s*`(mm_[a-z_]+\.md)`\s*\|\s*$")
    with open(MM_HUB_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    out_lines = []
    applied = False
    for line in lines:
        m = pattern.match(line.rstrip("\n"))
        if m and m.group(1).strip() == category_name:
            category, trigger_text, filename = m.groups()
            new_trigger = trigger_text.rstrip() + " Also includes: " + ", ".join(new_words) + "."
            out_lines.append(f"| {category} | {new_trigger} | `{filename}` |\n")
            applied = True
        else:
            out_lines.append(line)
    if not applied:
        raise RuntimeError(f"Category '{category_name}' not found while applying (already validated earlier — should not happen).")
    with open(MM_HUB_PATH, "w", encoding="utf-8") as f:
        f.writelines(out_lines)


def _mm_log_enrichment_to_history(category_name, new_words, baseline, proposed):
    """CHANGELOG.md is newest-first — this PREPENDS right after the header comment block,
    not appends at the end, or the entry would land at the bottom instead of at the top."""
    today = datetime.today().strftime("%Y-%m-%d")
    line = (
        f"- {today} `mm-enrich`: category '{category_name}' + [{', '.join(new_words)}]. "
        f"Backtest (mm_backtest_cases.py): {_mm_fmt_metrics(baseline)} → {_mm_fmt_metrics(proposed)}. "
        f"Applied automatically by the gate (no metric got worse).\n"
    )
    try:
        if os.path.exists(CHANGELOG_PATH):
            with open(CHANGELOG_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()
        else:
            lines = ["# CHANGELOG\n", "\n"]
        insert_at = 0
        for i, l in enumerate(lines):
            if not l.startswith("#") and l.strip() != "":
                insert_at = i
                break
            insert_at = i + 1
        lines.insert(insert_at, line)
        with open(CHANGELOG_PATH, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print("✅ Line added to the top of CHANGELOG.md.")
    except Exception as e:
        print(f"⚠️ CHANGELOG.md not updated: {e}")


def execute_mm_suggest_words(category_name):
    """Proposes candidate words for `mm-enrich` — NEVER applies anything itself. Mines the
    backtest's own FAIL cases for that category: words present in a missed message but not
    already used by ANY category's trigger text (to avoid introducing new collisions)."""
    if not category_name:
        print('Usage: python3 mental_models_engine.py mm-suggest-words "<Category>"')
        return

    rows = _mm_parse_hub_table()
    if category_name not in [r["category"] for r in rows]:
        print(f"❌ Category '{category_name}' not found. Available: {[r['category'] for r in rows]}")
        return

    used_words = set()
    for r in rows:
        used_words |= _mm_tokenize(r["trigger"])

    candidates = {}
    for expected, msg in _mm_load_backtest_cases():
        if expected != category_name:
            continue
        matched, _ = _mm_score_situation(msg)
        if category_name in [m["category"] for m in matched]:
            continue  # already correctly matched, nothing to fix
        for token in _mm_tokenize(msg) - used_words:
            candidates.setdefault(token, []).append(msg)

    if not candidates:
        print(f"No candidates for '{category_name}': either no FAIL cases in the backtest, or every word in the missed messages already collides with another category.")
        return

    print(f"Candidates for '{category_name}' (words from missed messages, not used by any other category):")
    for word, msgs in sorted(candidates.items(), key=lambda kv: -len(kv[1])):
        print(f"  {word!r} — appears in {len(msgs)} missed message(s)")
    print(f'\nTry: python3 mental_models_engine.py mm-enrich "{category_name}" "word1,word2"')


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "mentalmodel":
            execute_mentalmodel_check(" ".join(sys.argv[2:]))
        elif command == "mm-enrich":
            if len(sys.argv) < 4:
                print('Usage: python3 mental_models_engine.py mm-enrich "<Category>" "word1,word2,..."')
            else:
                execute_mm_enrich(sys.argv[2], sys.argv[3])
        elif command == "mm-suggest-words":
            if len(sys.argv) < 3:
                print('Usage: python3 mental_models_engine.py mm-suggest-words "<Category>"')
            else:
                execute_mm_suggest_words(sys.argv[2])
        else:
            print(f"Unknown command: {command}")
    else:
        print('Usage: python3 mental_models_engine.py [mentalmodel "<situation>"|mm-enrich "<category>" "<words,csv>"|mm-suggest-words "<category>"]')

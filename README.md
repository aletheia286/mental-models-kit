# mental-models-kit

A small, portable decision-support engine for Claude Code: a curated table of mental
models (decision-making, problem-solving, communication, bias-checking, etc.) plus a hook
that automatically surfaces the relevant model(s) to the agent right before it responds to
a message that looks like a real decision, trade-off, recurring problem, or delicate
communication — no manual lookup required.

Zero-cost by default: pure keyword-overlap matching, no ML dependency, works anywhere
Python runs (local or cloud). An optional local-only semantic-embedding fallback can catch
more cases at the cost of a one-time setup (see below) — it's skipped automatically in
cloud sessions, by design.

## Add it to a project

From the root of the repo you want to add it to:

```bash
git submodule add https://github.com/aletheia286/mental-models-kit.git .mental-models-kit
```

Add this to the repo's `.claude/settings.json` (merge with any existing `hooks` block —
see `settings.snippet.json` for the exact JSON to merge):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [{"type": "command", "command": "git -C \"$CLAUDE_PROJECT_DIR\" submodule update --init --recursive"}]
      }
    ],
    "UserPromptSubmit": [
      {"hooks": [{"type": "command", "command": "python3 ${CLAUDE_PROJECT_DIR}/.mental-models-kit/preloader.py", "timeout": 10}]}
    ]
  }
}
```

Commit both. The `SessionStart` hook guarantees the submodule is populated at the start of
every session (local or cloud) — it's idempotent, so running it every time is harmless even
when nothing needs updating. The `UserPromptSubmit` hook is the actual mechanism: it runs
on every message and injects the matching mental model's content into the agent's context
when (and only when) a real trigger is detected.

## Updating to a newer version of the kit

```bash
cd .mental-models-kit && git pull origin main && cd ..
git add .mental-models-kit
git commit -m "Update mental-models-kit"
```

This is always an explicit, visible action — never a silent background sync.

## CLI usage (also works standalone, without the hook)

```bash
python3 mental_models_engine.py mentalmodel "I need to choose between two vendors, there are real trade-offs"
python3 mental_models_engine.py mm-suggest-words "Decisions & trade-offs"
python3 mental_models_engine.py mm-enrich "Decisions & trade-offs" "word1,word2"
```

`mm-enrich` only ever modifies `_mm_hub.md` if a full re-run of the backtest
(`mm_backtest_cases.py`) shows the change doesn't make anything worse (no new
wrong-category matches, no new false positives, no drop in accuracy) — a proposed
improvement is always re-checked by the tool itself, never taken on faith.

## Optional: local semantic-embedding fallback

Only useful locally (skipped automatically in cloud sessions, which don't have a
persistent Python environment for this). Requires a dedicated venv:

```bash
python3 -m venv ~/.venvs/mental-models-kit
~/.venvs/mental-models-kit/bin/pip install fastembed numpy
```

Once installed, `preloader.py` detects the venv automatically and uses the embedding
fallback (`embedding_server.py`, a warm-within-session local process) whenever the
keyword matcher stays silent, subject to a similarity threshold and a margin-over-runner-
up check tuned to avoid ambiguous matches.

## Design notes

- **Silence is the safe failure mode.** The keyword matcher requires a fairly high overlap
  score before it commits to a category — on an independent 39-message backtest, this
  means it only fires ~15% of the time, but with zero wrong-category matches. Injecting
  the WRONG mental model's framing into the agent's context is worse than saying nothing.
- **`mm-enrich`/`mm-suggest-words` exist because the keyword table needs to grow over time**
  as real usage surfaces missed phrasings — but every addition goes through the same
  backtest gate, so the table can only get more accurate over time, never silently regress.

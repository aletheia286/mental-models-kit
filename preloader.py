#!/usr/bin/env python3
"""UserPromptSubmit hook — fires BEFORE the agent drafts a response. Reads the user's
incoming message, scores it against the trigger table in _mm_hub.md, and if it matches,
injects the matched mm_*.md content directly into the agent's context via additionalContext
— so the model is already in front of the agent when it starts reasoning, not something it
has to remember to fetch.

Hybrid design: keyword matching alone (`_mm_score_situation`) is the primary, always-on,
zero-cost path. When it's silent, an OPTIONAL semantic-embedding fallback via
embedding_server.py (a warm-within-session local process, LOCAL ONLY — see CLOUD
DEGRADATION below) is tried, accepting a match only above both a similarity threshold AND
a wide margin over the runner-up category.

CLOUD DEGRADATION: a cloud session has no persistent Python venv with fastembed installed
— cold-starting it there is much slower than the local cost. Not worth it — cloud sessions
skip the embedding fallback entirely and run keyword-only, by design, not by bug.
"""
import sys
import os
import json
import socket
import subprocess

# Self-locating, deliberately NOT using CLAUDE_PROJECT_DIR (lesson learned the hard way in
# the source project: that env var is NOT reliably present for a plain subprocess in a real
# cloud session — confirmed live, not assumed. It would also be the WRONG value here even
# if present: this kit is meant to be used as a git submodule nested inside another repo,
# so CLAUDE_PROJECT_DIR would point at the consuming repo's root, not at this kit's folder).
# This script always lives at the kit's own root, so locate it from its own path instead.
KIT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KIT_DIR)

from mental_models_engine import _mm_score_situation, MM_DIR  # noqa: E402

SOCKET_PATH = "/tmp/mental_models_kit_embed.sock"
SIM_THRESHOLD = 0.40
MARGIN_THRESHOLD = 0.14
SOCKET_CONNECT_TIMEOUT = 0.3
SOCKET_QUERY_TIMEOUT = 2.0


def _is_cloud_session():
    return os.environ.get("CLAUDE_CODE_REMOTE", "").lower() == "true"


def _embedding_venv_available():
    py = os.path.expanduser("~/.venvs/mental-models-kit/bin/python")
    return os.path.exists(py)


def _query_embedding_server(situation):
    """Returns sorted [{category, file, similarity}, ...] or None if unreachable/any error —
    always fails open, never raises out to main()."""
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(SOCKET_CONNECT_TIMEOUT)
        s.connect(SOCKET_PATH)
        s.settimeout(SOCKET_QUERY_TIMEOUT)
        s.sendall(json.dumps({"situation": situation}).encode("utf-8"))
        data = b""
        while True:
            chunk = s.recv(8192)
            if not chunk:
                break
            data += chunk
            if data.endswith(b"\n"):
                break
        s.close()
        resp = json.loads(data.decode("utf-8"))
        return resp.get("scores")
    except Exception:
        return None


def _spawn_embedding_server_if_needed():
    """Non-blocking: if the warm server isn't reachable, start it detached and return
    immediately WITHOUT waiting — this message gets keyword-only, next message finds it
    warm."""
    if os.path.exists(SOCKET_PATH):
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(SOCKET_CONNECT_TIMEOUT)
            s.connect(SOCKET_PATH)
            s.close()
            return  # already warm
        except Exception:
            try:
                os.remove(SOCKET_PATH)  # stale socket file, clear it
            except Exception:
                pass
    try:
        server_script = os.path.join(KIT_DIR, "embedding_server.py")
        venv_python = os.path.expanduser("~/.venvs/mental-models-kit/bin/python")
        subprocess.Popen(
            [venv_python, server_script],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass  # fail open — no embedding fallback this session, keyword-only still works


def score_situation_hybrid(situation):
    matched, _ = _mm_score_situation(situation)
    if matched:
        return matched, "keyword"

    if _is_cloud_session() or not _embedding_venv_available():
        return [], "keyword-only (cloud or no venv)"

    scores = _query_embedding_server(situation)
    if scores is None:
        _spawn_embedding_server_if_needed()
        return [], "keyword-only (embedding server cold, spawning for next message)"

    if len(scores) < 2 or scores[0]["similarity"] < SIM_THRESHOLD:
        return [], "keyword+embedding, no confident match"
    margin = scores[0]["similarity"] - scores[1]["similarity"]
    if margin < MARGIN_THRESHOLD:
        return [], f"keyword+embedding, margin too narrow ({margin:.3f})"

    top = scores[0]
    return [{"category": top["category"], "file": top["file"]}], "embedding-fallback"


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return  # malformed input — fail open, inject nothing, never block the user

    user_input = payload.get("user_input", "") or ""
    if not user_input.strip():
        return

    try:
        matched, method = score_situation_hybrid(user_input)
    except Exception:
        return  # fail open — a broken hook must never break the user's session

    if not matched:
        return

    parts = []
    for row in matched:
        mm_path = os.path.join(MM_DIR, row["file"])
        try:
            with open(mm_path, "r", encoding="utf-8") as f:
                parts.append(f"### {row['category']} ({row['file']})\n{f.read()}")
        except Exception:
            continue

    if not parts:
        return

    context = (
        f"Mental Models Kit — trigger detected on the user's message via {method} "
        f"(category: {', '.join(r['category'] for r in matched)}). "
        "Real content of the relevant mm_*.md file(s), already fetched — "
        "use it to inform the response instead of having to invoke a lookup separately:\n\n"
        + "\n\n".join(parts)
    )

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }))


if __name__ == "__main__":
    main()

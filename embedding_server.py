#!/usr/bin/env python3
"""Warm-within-session semantic scorer for the mental-models-kit hybrid matcher — OPTIONAL,
local-only extra (requires `pip install fastembed` in a dedicated venv, see README.md).

Root cause this replaces: fastembed's model load takes ~4-6s — unacceptable if paid on
every single UserPromptSubmit hook invocation (a fresh subprocess per message). A
persistent systemd daemon was considered and rejected as unnecessarily heavy; this is
simpler — start once per session (first cold call pays the 4-6s), stay warm for the rest
of the session, self-clean on exit.

NOT used in cloud sessions (see preloader.py's CLAUDE_CODE_REMOTE check) — a fresh cloud
sandbox has no persistent venv, so cold start there means pip-installing fastembed +
downloading ~260MB of model weights. Local only, entirely optional — the kit works fine
keyword-only without this file ever running.

Socket path is intentionally short and fixed (/tmp, not under a long scratch dir) — AF_UNIX
has a 108-byte sun_path limit that silently fails with no exception if exceeded.
"""
import os
import sys
import json
import socket
import signal

# Self-locating, deliberately NOT using CLAUDE_PROJECT_DIR — see preloader.py's comment for
# why (unreliable in cloud, and the wrong value anyway when this kit is used as a submodule).
KIT_DIR = os.path.dirname(os.path.abspath(__file__))
SOCKET_PATH = "/tmp/mental_models_kit_embed.sock"

sys.path.insert(0, KIT_DIR)
from mental_models_engine import _mm_parse_hub_table  # noqa: E402


def build_category_vectors(model):
    rows = _mm_parse_hub_table()
    texts = [r["trigger"] for r in rows]
    vectors = list(model.embed(texts))
    return [
        {"category": r["category"], "file": r["file"], "vector": vec}
        for r, vec in zip(rows, vectors)
    ]


def cosine(a, b):
    import numpy as np
    a, b = np.array(a), np.array(b)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    return float(a.dot(b) / denom) if denom else 0.0


def main():
    from fastembed import TextEmbedding
    model = TextEmbedding("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    categories = build_category_vectors(model)

    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(5)

    def shutdown(signum, frame):
        try:
            server.close()
        finally:
            if os.path.exists(SOCKET_PATH):
                os.remove(SOCKET_PATH)
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    while True:
        try:
            conn, _ = server.accept()
        except OSError:
            break
        try:
            data = conn.recv(8192).decode("utf-8")
            req = json.loads(data)
            situation = req.get("situation", "")
            vec = list(model.embed([situation]))[0]
            scores = sorted(
                (
                    {"category": c["category"], "file": c["file"], "similarity": cosine(vec, c["vector"])}
                    for c in categories
                ),
                key=lambda x: x["similarity"], reverse=True,
            )
            conn.sendall((json.dumps({"scores": scores}) + "\n").encode("utf-8"))
        except Exception as e:
            try:
                conn.sendall((json.dumps({"error": str(e)}) + "\n").encode("utf-8"))
            except Exception:
                pass
        finally:
            conn.close()


if __name__ == "__main__":
    main()

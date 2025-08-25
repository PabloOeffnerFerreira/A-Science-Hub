# core/ai/ash_assistant/ash_retrieve.py
from __future__ import annotations
import json, sqlite3
from pathlib import Path

# Paths per your layout
KB_ROOT = (Path(__file__).resolve().parent / "kb")
DB_PATH = (Path(__file__).resolve().parent / "storage" / "ash_kb.sqlite")

def ensure_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS docs(
        id TEXT PRIMARY KEY, ns TEXT, title TEXT, body TEXT, view TEXT, updated INTEGER
    )""")
    # Full-text search table for BM25 (no embeddings needed)
    c.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts
                 USING fts5(id, ns, title, view, body, content='')""")

    # If empty, build from KB files now
    count = c.execute("SELECT COUNT(*) FROM docs").fetchone()[0]
    if count == 0:
        for p in KB_ROOT.rglob("*"):
            if p.suffix not in (".json", ".md"):
                continue
            if p.suffix == ".json":
                j = json.loads(p.read_text(encoding="utf-8"))
                did   = j.get("id") or p.relative_to(KB_ROOT).as_posix()
                ns    = j.get("ns") or p.parent.name
                title = j.get("title") or p.stem
                view  = " ".join([j.get("title",""), j.get("summary",""), j.get("route","")])[:1200]
                body  = json.dumps(j, ensure_ascii=False)
            else:
                txt   = p.read_text(encoding="utf-8")
                did   = p.relative_to(KB_ROOT).as_posix()
                ns    = did.split("/")[0]
                title = p.stem
                view  = txt.split("\n\n", 1)[0][:1200]
                body  = txt

            c.execute("REPLACE INTO docs(id,ns,title,body,view,updated) VALUES(?,?,?,?,?,strftime('%s','now'))",
                      (did, ns, title, body, view))
            c.execute("REPLACE INTO docs_fts(id,ns,title,view,body) VALUES(?,?,?,?,?)",
                      (did, ns, title, view, body))
        db.commit()
    db.close()

def _fts_query(db, query: str, namespaces: tuple[str,...], k: int):
    import re
    # 1) Sanitize: keep only letters/numbers/underscores/spaces
    cleaned = re.sub(r"[^0-9A-Za-z_ \t]", " ", query)
    # 2) Tokenize to words (min length 1) and build a MATCH string
    terms = [t for t in re.split(r"\s+", cleaned) if t]
    # If nothing survives, fallback to a harmless term
    if not terms:
        terms = ["ash"]

    # FTS5: space = AND between terms. Quote each to avoid operator parsing.
    match = " ".join(f'"{t}"' for t in terms)

    # IMPORTANT: filter namespaces via normal WHERE, not inside MATCH
    qmarks = ",".join("?" * len(namespaces))
    sql = (
        f"SELECT id, ns, title, view, body, bm25(docs_fts) AS s "
        f"FROM docs_fts "
        f"WHERE docs_fts MATCH ? AND ns IN ({qmarks}) "
        f"ORDER BY s LIMIT ?"
    )
    args = (match, *namespaces, k)
    cur = db.execute(sql, args)
    rows = cur.fetchall()
    return [
        {"id": id_, "ns": ns, "title": title, "snippet": (view or body)[:800], "score": -s}
        for id_, ns, title, view, body, s in rows
    ]


def retrieve(query: str, k: int = 4,
             namespaces: tuple[str,...] = ("tools","app","faq","dev_public"),
             db_path: str = str(DB_PATH)) -> list[dict]:
    ensure_db()
    db = sqlite3.connect(db_path)
    try:
        return _fts_query(db, query, namespaces, k)
    finally:
        db.close()

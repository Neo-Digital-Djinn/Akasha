"""
driver.py — Akasha port
The Great Discovery / akasha-discovery

Original written in Termux on Android (ver+4).
Ported for canonical Akasha ecosystem membership.

PORTING CHANGES vs original driver.py:
  - Schema column names corrected: source/target -> src/dst
    (core_engine.py uses 'src' and 'dst'; original driver.py used
    'source' and 'target' -- this was a dormant bug on Android where
    the db was always freshly created each run)
  - holes table: removed node_id (Phase 2 schema uses epoch_found/shape_sig/demands)
  - semantic_pressure table: value -> structural_compress/semantic_compress/mismatch
  - main() entrypoint added for pyproject.toml script registration
  - Epoch output written as NDJSON for Akasha pipeline compatibility
"""

import sys
import json
import random
from great_discovery.core_engine import init_db


# ---------- Graph Operations ----------

def seed_nodes(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM nodes")
    count = cur.fetchone()[0]

    if count == 0:
        seeds = [
            ("number",    "mathematics"),
            ("force",     "physics"),
            ("cell",      "biology"),
            ("symbol",    "information"),
            ("energy",    "physics"),
            ("pattern",   "cognition"),
            ("pressure",  "systems"),
        ]
        for concept, domain in seeds:
            cur.execute(
                "INSERT INTO nodes(concept, domain, introduced) VALUES (?, ?, 0)",
                (concept, domain)
            )
        conn.commit()


def grow_graph(conn, epoch):
    cur = conn.cursor()
    cur.execute("SELECT id FROM nodes")
    nodes = [r[0] for r in cur.fetchall()]
    if len(nodes) < 2:
        return

    a, b = random.sample(nodes, 2)
    relation_types = [
        "causes", "requires", "constrains", "amplifies",
        "stabilizes", "emerges_from", "destabilizes",
        "analogous_to", "is_dual_of", "related",
    ]
    rel = random.choice(relation_types)
    weight = round(random.random(), 3)
    cur.execute(
        "INSERT INTO edges(src, dst, relation_type, weight) VALUES (?, ?, ?, ?)",
        (a, b, rel, weight)
    )
    conn.commit()


def detect_holes(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, concept, domain FROM nodes
        WHERE id NOT IN (
            SELECT src FROM edges
            UNION
            SELECT dst FROM edges
        )
    """)
    isolated = cur.fetchall()

    for node_id, concept, domain in isolated:
        shape_sig = f"isolated:{node_id}"
        cur.execute("SELECT id FROM holes WHERE shape_sig=? AND filled=0", (shape_sig,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO holes(epoch_found, shape_sig, demands, filled) VALUES (?, ?, ?, 0)",
                (0, shape_sig, f"{concept}:{domain} has no edges")
            )
    conn.commit()
    return len(isolated)


def apply_semantic_pressure(conn, holes):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM nodes")
    n_nodes = cur.fetchone()[0] or 1
    cur.execute("SELECT COUNT(DISTINCT concept) FROM nodes")
    n_unique = cur.fetchone()[0] or 1

    structural_compress = round(n_unique / n_nodes, 4)
    semantic_compress   = round(max(0.0, structural_compress - holes * 0.01), 4)
    mismatch            = round(abs(structural_compress - semantic_compress), 4)

    cur.execute(
        """INSERT OR REPLACE INTO semantic_pressure
           (epoch, structural_compress, semantic_compress, mismatch)
           VALUES (
               (SELECT COALESCE(MAX(epoch), -1) + 1 FROM semantic_pressure),
               ?, ?, ?
           )""",
        (structural_compress, semantic_compress, mismatch)
    )
    conn.commit()
    return mismatch


# ---------- Epoch Execution ----------

def run_epoch(epoch_number, db_path="discovery.db"):
    conn = init_db(db_path)
    try:
        seed_nodes(conn)
        grow_graph(conn, epoch_number)
        holes   = detect_holes(conn)
        mismatch = apply_semantic_pressure(conn, holes)

        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM nodes")
        n_nodes = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM edges")
        n_edges = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM holes WHERE filled=0")
        open_holes = cur.fetchone()[0]

        record = {
            "epoch": epoch_number,
            "nodes": n_nodes,
            "edges": n_edges,
            "isolated_this_epoch": holes,
            "open_holes": open_holes,
            "semantic_mismatch": mismatch,
        }
        print(json.dumps(record), flush=True)
        return record

    except Exception as e:
        print(json.dumps({"epoch": epoch_number, "error": str(e)}), flush=True)
        return None
    finally:
        conn.close()


def main():
    import argparse
    p = argparse.ArgumentParser(description="akasha-discovery epoch runner")
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--db",     type=str, default="discovery.db")
    args = p.parse_args()
    for i in range(args.epochs):
        run_epoch(i, db_path=args.db)


if __name__ == "__main__":
    main()

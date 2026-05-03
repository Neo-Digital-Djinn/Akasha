import csv, sys, pathlib, importlib.util, os

# Load common from same directory
_dir = pathlib.Path(__file__).parent
_spec = importlib.util.spec_from_file_location("common", _dir / "common.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
normalize_url = _mod.normalize_url

files = sys.argv[1:]

if not files:
    print("Usage: merge_csvs.py <file1.csv> [file2.csv ...]")
    sys.exit(1)

rows = []
seen = set()

for f in files:
    try:
        for r in csv.DictReader(open(f)):
            key = (r["name"].lower(), normalize_url(r["url"]))
            if key not in seen:
                seen.add(key)
                rows.append(r)
    except Exception as e:
        print(f"Warning: skipped {f} ({e})")

if not rows:
    print("No rows found to merge.")
    sys.exit(0)

out = pathlib.Path("reports/merged.csv")
out.parent.mkdir(exist_ok=True)

with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

print("merged ->", out)

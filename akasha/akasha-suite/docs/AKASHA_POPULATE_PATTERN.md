# Akasha Repo Populate Pattern

Whenever a new repo skeleton is born via the request pipeline, the fastest way to populate it is with a **single heredoc wrapper command**.

Pattern:

1. Ask AI:
   "Populate <repo-name> using the Akasha populate wrapper."

2. AI returns a single command like:

cat <<'EOF' > ~/populate_repo.sh
...
EOF

3. Run the script.

Result:
- README.md
- repo-manifest.yaml
- src/
- docs/
- tests/

All written in one shot.

Why this exists:
Editing files manually on mobile or Termux is slow.
The heredoc wrapper seeds an entire repo instantly.

Rule:
Every new Akasha repo should support **one-shot population**.

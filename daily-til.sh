#!/usr/bin/env bash
# Tambah 1 catatan TIL hari ini + commit + push.
# Cron: 30 22 * * * /path/ke/til/daily-til.sh
set -euo pipefail

cd "$(dirname "$0")"

DAY=$(date '+%Y-%m-%d')
ENTRY=$(ls "notes/$DAY"-*.md 2>/dev/null | head -1 || true)

if [ -n "$ENTRY" ]; then
  echo "catatan $DAY sudah ada"
  exit 0
fi

TITLE="${1:-Hal kecil hari ini}"
SLUG=$(printf '%s' "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]\+/-/g; s/^-//; s/-$//')
FILE="notes/$DAY-$SLUG.md"

printf '# %s\n\n**Tanggal:** %s  \n**Tag:** `#til`\n\nCatatan singkat: apa masalahnya, apa solusinya, kenapa jalan.\n' \
  "$TITLE" "$DAY" > "$FILE"

python3 - "$FILE" <<'PY'
import json
p = "tags.json"
try:
    d = json.load(open(p))
except FileNotFoundError:
    d = {}
d["til"] = d.get("til", 0) + 1
json.dump(dict(sorted(d.items())), open(p, "w"), indent=2)
open(p, "a").write("\n")
PY

git add notes tags.json
git commit -m "til: $TITLE ($DAY)" >/dev/null
git push origin "$(git rev-parse --abbrev-ref HEAD)" >/dev/null 2>&1 || echo "push gagal (cek kredensial)"
echo "ok: $FILE"

#!/bin/bash
# Haalt Google Scholar-data op en pusht het resultaat naar GitHub.
# Wordt dagelijks automatisch uitgevoerd via cron.

set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo ""
echo "========================================"
echo " Scholar data ophalen — $(date '+%Y-%m-%d %H:%M')"
echo "========================================"

# Python-script uitvoeren
python3 scholar_fetch.py

# Alleen committen en pushen als het JSON-bestand veranderd is
git add scholar_data.json
if git diff --staged --quiet; then
  echo "Geen wijzigingen — niets te pushen."
else
  git commit -m "Scholar data: $(date '+%Y-%m-%d %H:%M')"
  git push
  echo "✓ Naar GitHub gepusht."
fi

echo "========================================"
echo " Klaar — $(date '+%H:%M')"
echo "========================================"

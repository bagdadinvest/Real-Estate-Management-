#!/usr/bin/env bash
set -euo pipefail

# Import listings one-by-one from a CSV by feeding the management command
# a temporary single-URL CSV each run. This helps when sites block rapid
# sequential navigation within a single browser session.

# Defaults (override via env/flags)
CSV_PATH=${CSV_PATH:-"listings/links.csv"}
PY=${PY:-"python"}
MANAGE=${MANAGE:-"manage.py"}
REALTOR_ID=${REALTOR_ID:-"1"}
COOKIE_FILE=${COOKIE_FILE:-"listings/5dba612c-7239-43f0-9a4c-285062377c6f.txt"}
HEADLESS_FLAG=${HEADLESS_FLAG:-"--headed"}   # set to --headless for CI
DELAY=${DELAY:-"2"}
DEBUG_FLAG=${DEBUG_FLAG:-"--debug"}
SKIP_GEOCODE_FLAG=${SKIP_GEOCODE_FLAG:-"--skip-geocode"}
TIMEOUT_MS=${TIMEOUT_MS:-"20000"}
RETRIES=${RETRIES:-"2"}
COOLDOWN=${COOLDOWN:-"5.0"}

# Limits
LIMIT=${LIMIT:-"0"}          # 0 = all
OFFSET=${OFFSET:-"0"}

usage() {
  cat <<EOF
Usage: $0 [-c csv] [-n limit] [-o offset] [--] [extra manage.py flags]

Env overrides:
  REALTOR_ID, COOKIE_FILE, HEADLESS_FLAG, DELAY, DEBUG_FLAG, SKIP_GEOCODE_FLAG,
  TIMEOUT_MS, RETRIES, COOLDOWN

Examples:
  $0 -n 10                           # import first 10 URLs
  LIMIT=5 OFFSET=10 $0               # import 5 URLs starting from 11th
  HEADLESS_FLAG=--headless $0 --dry-run  # pass through extra flags
EOF
}

# Parse minimal flags
EXTRA_FLAGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -c|--csv) CSV_PATH="$2"; shift 2;;
    -n|--limit) LIMIT="$2"; shift 2;;
    -o|--offset) OFFSET="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    --) shift; EXTRA_FLAGS+=("$@"); break;;
    *) EXTRA_FLAGS+=("$1"); shift;;
  esac
done

if [[ ! -f "$CSV_PATH" ]]; then
  echo "CSV not found: $CSV_PATH" >&2
  exit 1
fi

TMP_DIR="listings"
mkdir -p "$TMP_DIR"
TMP_SINGLE="$TMP_DIR/tmp_single.csv"

# Build list of URLs (skip comments/blank, take first field before comma)
mapfile -t URLS < <(awk -F',' 'BEGIN{IGNORECASE=1}
  NR==1{if($0 ~ /(^|,)url(,|$)/){next}} # skip header with url
  {gsub(/^\s+|\s+$/,"",$0); if($0 ~ /^#/ || $0=="") next; split($0,a,","); u=a[1]; gsub(/^\s+|\s+$/,"",u); if(u!="") print u}
' "$CSV_PATH")

TOTAL=${#URLS[@]}
START=$OFFSET
END=$TOTAL
if [[ "$LIMIT" != "0" ]]; then
  END=$(( OFFSET + LIMIT ))
  if (( END > TOTAL )); then END=$TOTAL; fi
fi

echo "Processing URLs $((START+1))..$END of $TOTAL from $CSV_PATH"

count=0
for (( i=START; i<END; i++ )); do
  url="${URLS[$i]}"
  ((count++)) || true
  echo "[$count/$((END-START))] Importing: $url"

  # Write a single-URL CSV the importer understands
  printf "url\n%s\n" "$url" > "$TMP_SINGLE"

  set +e
  $PY "$MANAGE" import_listings_with_playwright \
    "$TMP_SINGLE" \
    --realtor-id "$REALTOR_ID" \
    --cookie-file "$COOKIE_FILE" \
    $HEADLESS_FLAG $DEBUG_FLAG $SKIP_GEOCODE_FLAG \
    --delay "$DELAY" --timeout "$TIMEOUT_MS" \
    --retries "$RETRIES" --cooldown "$COOLDOWN" \
    "${EXTRA_FLAGS[@]}"
  rc=$?
  set -e
  if [[ $rc -ne 0 ]]; then
    echo "  -> Import command failed (exit $rc); continuing to next URL" >&2
  fi
done

echo "Done. Processed $count URL(s)."


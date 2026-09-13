#!/bin/sh
# VPS / local entry: one slot, then exit (pair with cron at 4,7,10,13,15).
set -e
cd "$(dirname "$0")/../.."
export TZ="${TZ:-America/Chicago}"
exec python3 scripts/kagg_loop/orchestrate.py "$@"

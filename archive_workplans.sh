#!/usr/bin/env bash
set -euo pipefail

WORKPLAN_PATH="${1:-}"
OUTPUT_NAME="${2:-}"
ARCHIVE_DIR=".claude/workplans/archives"

if [[ -z "$WORKPLAN_PATH" ]]; then
  echo "Usage: $0 <workplan-path> [output.tar.gz]" >&2
  exit 1
fi

if [[ ! -e "$WORKPLAN_PATH" ]]; then
  echo "Workplan path not found: $WORKPLAN_PATH" >&2
  exit 1
fi

mkdir -p "$ARCHIVE_DIR"

base_name="$(basename "$WORKPLAN_PATH")"
timestamp="$(date +%Y%m%d-%H%M%S)"
if [[ -z "$OUTPUT_NAME" ]]; then
  OUTPUT_NAME="${base_name}-${timestamp}.tar.gz"
fi
OUTPUT_TAR="${ARCHIVE_DIR}/$(basename "$OUTPUT_NAME")"

tar -czf "$OUTPUT_TAR" "$WORKPLAN_PATH"
rm -rf "$WORKPLAN_PATH"

echo "✔ Archived $WORKPLAN_PATH to $OUTPUT_TAR and removed source"

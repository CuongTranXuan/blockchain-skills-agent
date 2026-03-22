#!/usr/bin/env bash
# Build a silent 1080p H.264 MP4 from showcase PNGs — meant for you to dub in any editor.
# Requires: ffmpeg (brew install ffmpeg)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ASSETS="$ROOT/assets"
OUT_DIR="${OUT_DIR:-$ROOT/demo/output}"
TMP="${TMPDIR:-/tmp}/bamboo-demo-$$"
ADD_SILENT_AUDIO="${ADD_SILENT_AUDIO:-1}"

mkdir -p "$OUT_DIR" "$TMP"
trap 'rm -rf "$TMP"' EXIT

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg not found. Install with: brew install ffmpeg" >&2
  exit 1
fi

# Durations (seconds) — tweak to match your dub script (see docs/DEMO_VIDEO_SCRIPT.md)
declare -a IMGS=(
  "$ASSETS/submission-cover.png"
  "$ASSETS/submission-architecture.png"
  "$ASSETS/scenario-happy-path.png"
  "$ASSETS/scenario-blocked-path.png"
  "$ASSETS/scenario-failure-path.png"
)
declare -a SECS=(10 10 20 16 16)

if [[ ${#IMGS[@]} -ne ${#SECS[@]} ]]; then
  echo "IMGS and SECS length mismatch" >&2
  exit 1
fi

SEG_LIST=()
for i in "${!IMGS[@]}"; do
  img="${IMGS[$i]}"
  t="${SECS[$i]}"
  seg="$TMP/seg$(printf '%02d' "$i").mp4"
  if [[ ! -f "$img" ]]; then
    echo "Missing image: $img" >&2
    exit 1
  fi
  ffmpeg -y -hide_banner -loglevel warning \
    -loop 1 -t "$t" -i "$img" \
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p" \
    -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -r 30 \
    "$seg"
  SEG_LIST+=("$seg")
done

CONCAT="$TMP/list.txt"
: > "$CONCAT"
for seg in "${SEG_LIST[@]}"; do
  printf "file '%s'\n" "$seg" >> "$CONCAT"
done

VIDEO_ONLY="$TMP/concat.mp4"
ffmpeg -y -hide_banner -loglevel warning \
  -f concat -safe 0 -i "$CONCAT" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -movflags +faststart \
  "$VIDEO_ONLY"

OUT="$OUT_DIR/demo-silent-for-dub-1080p.mp4"
if [[ "$ADD_SILENT_AUDIO" == "1" ]]; then
  # Many editors expect an audio track; stereo silence @ 48kHz.
  DUR="$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO_ONLY")"
  ffmpeg -y -hide_banner -loglevel warning \
    -i "$VIDEO_ONLY" \
    -f lavfi -i "anullsrc=channel_layout=stereo:sample_rate=48000" \
    -t "$DUR" \
    -shortest \
    -c:v copy \
    -c:a aac -b:a 128k \
    -movflags +faststart \
    "$OUT"
else
  cp "$VIDEO_ONLY" "$OUT"
fi

echo "Wrote: $OUT"
ls -lh "$OUT"

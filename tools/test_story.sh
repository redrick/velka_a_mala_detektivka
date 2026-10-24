#!/usr/bin/env bash
# Plays a story headless with tests/runner.gd (see there). Backs up and restores the real saves,
# and adds the runner autoload only for this run.
#   tools/test_story.sh 4        -> game/tests/story_4.gd
#   SHOTS=/some/dir tools/test_story.sh 4   -> with a window, screenshots of every step into /some/dir
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GODOT="${GODOT:-$HOME/apps/godot-4.6/Godot_v4.6.3-stable_linux.x86_64}"
DATA="$HOME/.local/share/godot/app_userdata/Velká a malá detektivka"
BACKUP="$(mktemp -d)"
if [ -d "$DATA" ]; then cp -a "$DATA/." "$BACKUP/" || { echo "backup of saves failed, not testing"; exit 2; }; fi
PROJ="$ROOT/game/project.godot"
cp "$PROJ" "$BACKUP/project.godot.orig"
sed -i 's|^Music=.*|&\nTestRun="*res://tests/runner.gd"|' "$PROJ"
MODE=(--headless); EXTRA=()
if [ -n "${SHOTS:-}" ]; then MODE=(); EXTRA=(--shots=user://tour); fi
timeout "${TIMEOUT:-900}" "$GODOT" "${MODE[@]}" --path "$ROOT/game" -- --test="res://tests/story_$1.gd" "${EXTRA[@]}" 2>&1 \
  | grep -v "invalid UID\|RID allocations\|^$" 
code=${PIPESTATUS[0]}
cp "$BACKUP/project.godot.orig" "$PROJ"
if [ -n "${SHOTS:-}" ] && [ -d "$DATA/tour" ]; then mkdir -p "$SHOTS"; cp "$DATA/tour/"*.png "$SHOTS/"; fi
rm -rf "$DATA"; mkdir -p "$DATA"; cp -a "$BACKUP/." "$DATA/"; rm -f "$DATA/project.godot.orig"
rm -rf "$BACKUP"
exit $code

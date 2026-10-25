#!/usr/bin/env bash
# Plays stories with tests/blind.gd (an explorer that doesn't know the solution) or a scripted
# tests/story_<x>.gd, headless. Every job runs in its own copy of game/ (rsynced, with the .godot
# cache) and its own XDG_DATA_HOME, so jobs run in parallel and never touch the project or the
# real saves.
#   tools/blind_play.sh 4 5 6                   blind, seed 1
#   SEEDS="1 2 3" JOBS=12 tools/blind_play.sh 1 2 3 4 5 6 7 8 9 10 11 12
#   tools/blind_play.sh test:4 test:mg2         the scripted tests
#   CRASHES="1 2 3 4 5" tools/blind_play.sh crash:4
#       saves and quits in the middle of the 1st, 2nd, … running chain that changed the story (like
#       closing the window mid-dialogue), then continues the save and has to finish the story;
#       CRASH_SEED=1 keeps one path, so CRASHES="$(seq 1 20)" walks through its first 20 chains
#   ARGS="--right --tries=3" tools/blind_play.sh 7
# Logs go to $BLIND_DIR/logs/<job>.log; the summary prints the BLIND / TEST / FAIL / error lines.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GODOT="${GODOT:-$HOME/apps/godot-4.6/Godot_v4.6.3-stable_linux.x86_64}"
BLIND_DIR="${BLIND_DIR:-${TMPDIR:-/tmp}/vamd_blind}"
JOBS="${JOBS:-8}"
SEEDS="${SEEDS:-1}"
CRASHES="${CRASHES:-1 2 3 4 5 6 7 8}"
mkdir -p "$BLIND_DIR/logs"

jobs_list=()
for s in "$@"; do
  if [[ $s == test:* ]]; then jobs_list+=("$s")
  elif [[ $s == crash:* ]]; then for c in $CRASHES; do jobs_list+=("$s:$c"); done
  else for seed in $SEEDS; do jobs_list+=("$s:$seed"); done; fi
done

log_of() { echo "$BLIND_DIR/logs/$(echo "$1" | tr ':' '_').log"; }

godot() {
  XDG_DATA_HOME="$1/data" timeout "${TIMEOUT:-1800}" "$GODOT" --headless --path "$1/game" -- "${@:2}"
}

run_job() {
  local slot="$1" job="$2" dir="$BLIND_DIR/slot$1" log
  log="$(log_of "$job")"
  mkdir -p "$dir"
  rsync -a --delete "$ROOT/game/" "$dir/game/"
  sed -i 's|^Music=.*|&\nTestRun="*res://tests/runner.gd"|' "$dir/game/project.godot"
  rm -rf "$dir/data"; mkdir -p "$dir/data"
  case $job in
    test:*) godot "$dir" --test="res://tests/story_${job#test:}.gd" > "$log" 2>&1; echo "exit=$?" >> "$log" ;;
    crash:*)
      local n c
      n=$(echo "$job" | cut -d: -f2); c=$(echo "$job" | cut -d: -f3)
      godot "$dir" --test=res://tests/blind.gd --story="$n" --seed="${CRASH_SEED:-$c}" --crash="$c" ${ARGS:-} > "$log" 2>&1
      local code=$?
      echo "exit=$code" >> "$log"
      if [ $code -eq 3 ]; then
        godot "$dir" --test=res://tests/blind.gd --story="$n" --seed="${CRASH_SEED:-$c}" --resume ${ARGS:-} >> "$log" 2>&1
        echo "exit=$?" >> "$log"
      fi ;;
    *) godot "$dir" --test=res://tests/blind.gd --story="${job%%:*}" --seed="${job##*:}" ${ARGS:-} > "$log" 2>&1
       echo "exit=$?" >> "$log" ;;
  esac
}

for ((k = 0; k < JOBS; k++)); do
  (
    for ((i = k; i < ${#jobs_list[@]}; i += JOBS)); do run_job "$k" "${jobs_list[$i]}"; done
  ) &
done
wait

for job in "${jobs_list[@]}"; do
  echo "== $job"
  grep -E "^BLIND|^TEST|FAIL|SCRIPT ERROR|^ERROR|Parse Error|exit=" "$(log_of "$job")" \
    | grep -v "invalid UID\|RID allocations\|resources still in use\|from \"String\" to \"PackedVector2Array\"" | head -40
done
[ -n "${KEEP:-}" ] || rm -rf "$BLIND_DIR"/slot*

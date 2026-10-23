#!/bin/bash
# Daily unattended discovery scan: runs `claude --print` with scan-prompt.md.
#
# Schedule it with launchd (launchd.plist.template) or cron (crontab.example).
# Each attempt gets its own log pair under $JOB_PIPELINE_LOGS (default
# ~/.job-pipeline/logs). One retry on failure: API connection drops are common
# enough that a run with no retry leaves crashed days that look like empty days.
#
# Environment:
#   JOB_PIPELINE_LOGS     log folder (default ~/.job-pipeline/logs)
#   JOB_SCAN_TIMEOUT      seconds per attempt (default 3000)
#   JOB_SCAN_MODEL        optional --model for claude
#   JOB_PIPELINE_NOTIFY   optional command: called as  <cmd> "<message>" "<title>"
#                         (profile.yaml notify.command is used when this is unset)

set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="${JOB_PIPELINE_LOGS:-$HOME/.job-pipeline/logs}"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TIMEOUT_SEC="${JOB_SCAN_TIMEOUT:-3000}"
MAX_ATTEMPTS=2
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"   # launchd and cron start with a bare PATH

notify() {
    local cmd="${JOB_PIPELINE_NOTIFY:-}"
    [ -z "$cmd" ] && cmd=$(cd "$REPO" && python3 -c 'import sys; sys.path.insert(0, "pipeline"); import jobprofile as P; print(P.get("notify.command", "") or "")' 2>/dev/null)
    if [ -n "$cmd" ]; then $cmd "$1" "$2" || true; else echo "[notify] $2: $1"; fi
}

if ! command -v claude >/dev/null; then
    notify "Claude CLI not found, job scan did not run" "Job scan ERROR"
    exit 1
fi

# A catch-up run fired the moment a laptop wakes often starts before DNS
# answers. Wait up to 5 minutes for the API host, which is the hard dependency.
for _ in $(seq 1 60); do
    curl -s -o /dev/null -m 5 https://api.anthropic.com && break
    sleep 5
done

cd "$REPO" || exit 1
PROMPT="$(cat "$REPO/scheduler/scan-prompt.md")"
MODEL_ARGS=()
[ -n "${JOB_SCAN_MODEL:-}" ] && MODEL_ARGS=(--model "$JOB_SCAN_MODEL")

run_attempt() {
    OUT_FILE="$LOG_DIR/job-scan-$TIMESTAMP-a$1.out"
    ERR_FILE="$LOG_DIR/job-scan-$TIMESTAMP-a$1.err"
    # --dangerously-skip-permissions: an unattended run cannot answer prompts.
    # Run it as a user account that holds nothing you would not risk; postings
    # and emails are third-party text (see the skill's unattended rules).
    claude --print --dangerously-skip-permissions "${MODEL_ARGS[@]}" -p "$PROMPT" \
        >"$OUT_FILE" 2>"$ERR_FILE" &
    local pid=$!
    ( sleep "$TIMEOUT_SEC"; kill -0 $pid 2>/dev/null && { kill -TERM $pid; sleep 5; kill -KILL $pid 2>/dev/null;
      echo "[$TIMESTAMP] TIMEOUT after ${TIMEOUT_SEC}s (attempt $1)" >> "$LOG_DIR/job-scan-failures.log"; } ) &
    local killer=$!
    wait $pid; local rc=$?
    kill $killer 2>/dev/null; wait $killer 2>/dev/null
    return $rc
}

EXIT_CODE=1
for ATTEMPT in $(seq 1 $MAX_ATTEMPTS); do
    run_attempt "$ATTEMPT"; EXIT_CODE=$?
    [ $EXIT_CODE -eq 0 ] && break
    # claude --print writes API errors to stdout, so fall back to its tail.
    MSG=$(tail -1 "$ERR_FILE" 2>/dev/null | head -c 100)
    [ -z "$MSG" ] && MSG=$(tail -3 "$OUT_FILE" 2>/dev/null | tr '\n' ' ' | head -c 200)
    echo "[$TIMESTAMP] attempt $ATTEMPT FAILED (exit $EXIT_CODE): $MSG" >> "$LOG_DIR/job-scan-failures.log"
    [ "$ATTEMPT" -lt $MAX_ATTEMPTS ] && sleep 30
done
[ $EXIT_CODE -ne 0 ] && notify "Job scan failed after $MAX_ATTEMPTS attempts. Log: $OUT_FILE" "Job scan ERROR"

# Lane flags: a lane whose tool needs an interactive login (mail, LinkedIn)
# can be absent in an unattended run. The prompt ends with two marker lines;
# SKIPPED raises a flag file that the next interactive session must clear by
# running that lane. A missing marker (crash, timeout) leaves the flag as is.
for LANE in GMAIL LINKEDIN; do
    FLAG="$REPO/state/.$(echo $LANE | tr 'A-Z' 'a-z')-scan-pending"
    case "$(grep -oE "${LANE}_LANE: (RAN|SKIPPED)" "$OUT_FILE" 2>/dev/null | tail -1)" in
        *RAN) rm -f "$FLAG" ;;
        *SKIPPED) date +%Y-%m-%d > "$FLAG" ;;
    esac
done

for f in "$LOG_DIR"/job-scan-"$TIMESTAMP"-a*; do [ -s "$f" ] || rm -f "$f"; done
exit 0

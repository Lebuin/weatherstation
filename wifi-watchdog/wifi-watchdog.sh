#!/usr/bin/env bash

set -Eeuo pipefail

INTERFACE="${INTERFACE:-wlan0}"
PING_TIMEOUT="${PING_TIMEOUT:-3}"
SETTLE_SECONDS="${SETTLE_SECONDS:-30}"
FAILURE_THRESHOLD="${FAILURE_THRESHOLD:-3}"
STATE_DIR="${STATE_DIR:-/var/lib/wifi-watchdog}"
FAILURE_FILE="$STATE_DIR/consecutive-failures"
# By default, check the WiFi gateway. Set PING_TARGETS to check internet reachability instead.
PING_TARGETS="${PING_TARGETS:-}"

log() {
    logger -t wifi-watchdog "$*"
}

default_gateway() {
    ip -4 route show default dev "$INTERFACE" 2>/dev/null | awk 'NR == 1 {print $3}'
}

build_targets() {
    local gateway
    local target
    local -a targets

    if [[ -n "$PING_TARGETS" ]]; then
        read -r -a targets <<<"$PING_TARGETS"
        for target in "${targets[@]}"; do
            printf '%s\n' "$target"
        done
        return
    fi

    gateway="$(default_gateway)"
    if [[ -n "$gateway" ]]; then
        printf '%s\n' "$gateway"
    fi
}

network_ok() {
    local target

    while IFS= read -r target; do
        [[ -z "$target" ]] && continue

        if ping -c1 -W "$PING_TIMEOUT" "$target" >/dev/null 2>&1; then
            return 0
        fi
    done < <(build_targets)

    return 1
}

reset_failures() {
    rm -f "$FAILURE_FILE"
}

record_failure() {
    local failures=0

    mkdir -p "$STATE_DIR"
    if [[ -r "$FAILURE_FILE" ]]; then
        failures="$(<"$FAILURE_FILE")"
    fi

    if [[ ! "$failures" =~ ^[0-9]+$ ]]; then
        failures=0
    fi

    failures=$((failures + 1))
    printf '%s\n' "$failures" >"$FAILURE_FILE"
    printf '%s\n' "$failures"
}

if network_ok; then
    reset_failures
    exit 0
fi

log "connectivity lost, reconnecting $INTERFACE"

if command -v nmcli >/dev/null 2>&1; then
    nmcli radio wifi on || true
    nmcli device reconnect "$INTERFACE" || nmcli device connect "$INTERFACE" || true
else
    log "nmcli not found, skipping interface reconnect"
fi

sleep "$SETTLE_SECONDS"

if network_ok; then
    log "connectivity restored after reconnecting $INTERFACE"
    reset_failures
    exit 0
fi

log "reconnect failed, restarting NetworkManager"

if ! systemctl restart NetworkManager; then
    log "failed to restart NetworkManager"
fi

sleep "$SETTLE_SECONDS"

if network_ok; then
    log "connectivity restored after restarting NetworkManager"
    reset_failures
    exit 0
fi

failures="$(record_failure)"
log "network recovery failed ($failures/$FAILURE_THRESHOLD)"

if (( failures >= FAILURE_THRESHOLD )); then
    log "failure threshold reached, rebooting"
    systemctl reboot --no-block
fi

exit 1

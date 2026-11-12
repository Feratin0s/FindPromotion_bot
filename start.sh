#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
GO_PROJECT_DIR="$PROJECT_DIR/wppconnect-server-go"
SCRIPT="$PROJECT_DIR/start.sh"
BUILD_DIR="$PROJECT_DIR/.dev-build"
CORE_BINARY="$BUILD_DIR/findpromo-core"
TERMINAL="${TERMINAL:-x-terminal-emulator}"

run_service() {
    case "$1" in
        go)
            cd "$GO_PROJECT_DIR"
            if [ -f "$PROJECT_DIR/.env" ]; then
                set -a
                . "$PROJECT_DIR/.env"
                set +a
            fi
            export PORT="${PORT:-21465}"
            if [ -z "${DATA_DIR:-}" ] || [ "$DATA_DIR" = /data ]; then
                DATA_DIR="$GO_PROJECT_DIR/wpp_go_data"
            fi
            export DATA_DIR
            WEBHOOK_URL="${WEBHOOK_URL:-http://127.0.0.1:3000/webhook}"
            case "$WEBHOOK_URL" in
                http://findpromo-core:3000*)
                    WEBHOOK_URL="http://127.0.0.1:3000${WEBHOOK_URL#http://findpromo-core:3000}"
                    ;;
            esac
            export WEBHOOK_URL
            go run ./cmd/server
            ;;
        core)
            "$CORE_BINARY"
            ;;
        python)
            if [ ! -x "$PROJECT_DIR/venv/bin/python" ] || [ ! -f "$PROJECT_DIR/venv/bin/activate" ]; then
                printf 'The project virtual environment is missing. Create it with: python3 -m venv "%s/venv"\n' "$PROJECT_DIR" >&2
                return 1
            fi
            . "$PROJECT_DIR/venv/bin/activate"
            export CORE_URL="${CORE_URL:-http://127.0.0.1:3000}"
            cd "$PROJECT_DIR"
            python main.py
            ;;
        *)
            printf 'Unknown development service: %s\n' "$1" >&2
            return 2
            ;;
    esac
}

if [ -n "${FINDPROMO_DEV_SERVICE:-}" ]; then
    set +e
    run_service "$FINDPROMO_DEV_SERVICE"
    status=$?
    printf '\n[%s] process exited with status %s.\n' "$FINDPROMO_DEV_SERVICE" "$status"
    printf 'Press Enter to close this terminal...'
    IFS= read -r _ || :
    exit "$status"
fi

if ! command -v "$TERMINAL" >/dev/null 2>&1; then
    printf 'Terminal emulator "%s" not found. Set TERMINAL to an installed terminal command.\n' "$TERMINAL" >&2
    exit 1
fi

if ! command -v cc >/dev/null 2>&1; then
    printf 'A C compiler (cc) is required. Install build tools and try again.\n' >&2
    exit 1
fi

mkdir -p "$BUILD_DIR"
cc -O2 -Wall -o "$CORE_BINARY" "$PROJECT_DIR/core/main.c" "$PROJECT_DIR/core/mongoose.c"

FINDPROMO_DEV_SERVICE=core "$TERMINAL" -e "$SCRIPT" &
sleep 0.3
FINDPROMO_DEV_SERVICE=go "$TERMINAL" -e "$SCRIPT" &
sleep 0.3
FINDPROMO_DEV_SERVICE=python "$TERMINAL" -e "$SCRIPT" &

printf 'Started separate terminals for the C service, WPPConnect Go, and Python bot.\n'

#!/bin/bash
# OpenClaw Memory Backup - Start Script
# Usage: gtools backup_openclaw_memory start [command] [options]

set -e

echo "🐱 OpenClaw Memory Backup & Restore"
echo "===================================="
echo ""

# Default values
COMMAND="${1:-backup}"
WORKSPACE=""
NAME=""
FULL=""

# Parse arguments
shift || true
while [[ $# -gt 0 ]]; do
    case $1 in
        -w|--workspace)
            WORKSPACE="$2"
            shift 2
            ;;
        -n|--name)
            NAME="$2"
            shift 2
            ;;
        -f|--full)
            FULL="--full"
            shift
            ;;
        -d|--dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        *)
            if [[ -z "$COMMAND" ]]; then
                COMMAND="$1"
            fi
            shift
            ;;
    esac
done

# Build command
CMD_ARGS="$COMMAND"

if [[ -n "$WORKSPACE" ]]; then
    CMD_ARGS="$CMD_ARGS --workspace $WORKSPACE"
fi

if [[ -n "$NAME" ]]; then
    CMD_ARGS="$CMD_ARGS --name $NAME"
fi

if [[ -n "$FULL" ]]; then
    CMD_ARGS="$CMD_ARGS $FULL"
fi

if [[ -n "$DRY_RUN" ]]; then
    CMD_ARGS="$CMD_ARGS $DRY_RUN"
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the Python module
echo "Running: gtools backup_openclaw_memory $CMD_ARGS"
echo ""

# Execute using gtools if available, otherwise use Python directly
if command -v gtools &> /dev/null; then
    gtools backup_openclaw_memory $CMD_ARGS
else
    # Fallback to direct Python execution
    cd "$SCRIPT_DIR"
    python3 main.py $CMD_ARGS
fi

echo ""
echo "✅ Done!"

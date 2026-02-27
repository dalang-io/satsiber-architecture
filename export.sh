#!/usr/bin/env bash
set -euo pipefail

# Export all .drawio diagrams to PNG and PDF
# Requires: drawio CLI (xvfb-run drawio) or Docker image rlespinasse/drawio-export
#
# Usage:
#   ./export.sh          # Export all diagrams
#   ./export.sh --docker # Use Docker instead of local drawio CLI

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIAGRAMS_DIR="$SCRIPT_DIR/diagrams"
OUTPUT_DIR="$SCRIPT_DIR/build"
USE_DOCKER=false

if [[ "${1:-}" == "--docker" ]]; then
    USE_DOCKER=true
fi

# Create output directories mirroring diagrams structure
find "$DIAGRAMS_DIR" -type d | while read -r dir; do
    rel="${dir#$DIAGRAMS_DIR}"
    mkdir -p "$OUTPUT_DIR/png${rel}"
    mkdir -p "$OUTPUT_DIR/pdf${rel}"
done

export_drawio() {
    local input="$1"
    local rel_path="${input#$DIAGRAMS_DIR/}"
    local dir_part="$(dirname "$rel_path")"
    local base="$(basename "$input" .drawio)"

    local png_out="$OUTPUT_DIR/png/$dir_part/${base}.png"
    local pdf_out="$OUTPUT_DIR/pdf/$dir_part/${base}.pdf"

    echo "Exporting: $rel_path"

    if $USE_DOCKER; then
        docker run --rm -v "$SCRIPT_DIR:/data" rlespinasse/drawio-export \
            --fileext drawio \
            --format png \
            --output "/data/build/png/$dir_part/" \
            "/data/diagrams/$rel_path"

        docker run --rm -v "$SCRIPT_DIR:/data" rlespinasse/drawio-export \
            --fileext drawio \
            --format pdf \
            --output "/data/build/pdf/$dir_part/" \
            "/data/diagrams/$rel_path"
    else
        xvfb-run -a drawio --export --format png --output "$png_out" "$input"
        xvfb-run -a drawio --export --format pdf --output "$pdf_out" "$input"
    fi

    echo "  -> PNG: build/png/$dir_part/${base}.png"
    echo "  -> PDF: build/pdf/$dir_part/${base}.pdf"
}

echo "=== Satsiber DC - Draw.io Export ==="
echo ""

# Find and export all .drawio files
count=0
find "$DIAGRAMS_DIR" -name "*.drawio" -type f | sort | while read -r file; do
    export_drawio "$file"
    count=$((count + 1))
done

echo ""
echo "Done! Exports saved to: $OUTPUT_DIR/"

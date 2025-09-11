#!/bin/bash
set -e

if [ -x "$CLOUDFLARED_BIN" ]; then
    echo "✅ Using cached cloudflared"
    "$CLOUDFLARED_BIN" --version
else
    curl -fsSL "$CLOUDFLARED_URL" -o "$CLOUDFLARED_BIN"
    chmod +x "$CLOUDFLARED_BIN"
    "$CLOUDFLARED_BIN" --version
fi

if [ -x "$UV_BIN" ]; then
    echo "✅ Using cached uv"
    "$UV_BIN" --version
else
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

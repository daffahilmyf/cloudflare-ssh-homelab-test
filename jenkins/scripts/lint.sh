#!/bin/bash
set -e

echo "🔍 Running linter..."
uv pip install ruff
uv run ruff check .

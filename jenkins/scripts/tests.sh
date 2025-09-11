#!/bin/bash
set -e

echo "🐍 Setting up virtual environment with uv..."
uv venv
echo "🐍 Installing Python dependencies..."
uv pip install '.[dev]'
echo "🧪 Running tests with coverage..."
uv run coverage run -m pytest
uv run coverage report -m

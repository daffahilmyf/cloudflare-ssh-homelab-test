#!/bin/bash
set -euo pipefail

mkdir -p "$DEPLOY_DIR"
cd "$DEPLOY_DIR"

if [ ! -d .git ]; then
    echo "📥 Cloning $REPO_URL"
    git clone "$REPO_URL" .
else
    echo "🔄 Pulling latest changes"
    git pull origin $(git rev-parse --abbrev-ref HEAD)
fi

echo "🛑 Stopping Docker Compose"
docker compose down || true

echo "🔍 Checking for changes in src/, tests/, or configs..."
CHANGED=$(git diff --name-only HEAD@{1} HEAD | grep -E '^(src/|tests/|pyproject\.toml|Dockerfile)' || true)

if [ -n "$CHANGED" ]; then
    echo "🧱 Changes detected → Rebuilding image with no cache"
    docker compose build --no-cache
else
    echo "⚡ No relevant changes → Using cache"
    docker compose build
fi

echo "🚀 Starting Docker Compose"
docker compose up -d

echo "✅ Deploy finished"

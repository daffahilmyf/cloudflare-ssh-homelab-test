#!/bin/bash
set -euo pipefail

TEMP_TUNNEL_LOG=$(cat .tunnel_log_path)

echo "🔐 Starting tunnel to $SSH_HOSTNAME on port $SSH_PORT"
"$CLOUDFLARED_BIN" access tcp \
    --hostname "$SSH_HOSTNAME" \
    --id "$CLIENT_ID" \
    --secret "$CLIENT_SECRET" \
    --url "$TUNNEL_LOCAL_BIND" \
    --destination "$TUNNEL_LOCAL_BIND" \
    > "$TEMP_TUNNEL_LOG" 2>&1 &

TUNNEL_PID=$!
echo "$TUNNEL_PID" > tunnel.pid

# Wait for tunnel to be ready
for i in {1..30}; do
    nc -z localhost "$SSH_PORT" && break
    echo "⏳ Waiting for tunnel ($i)..."
    sleep 2
done

if ! nc -z localhost "$SSH_PORT"; then
    echo "❌ Tunnel did not open"
    tail -n 20 "$TEMP_TUNNEL_LOG" || true
    kill "$TUNNEL_PID" || true
    exit 1
fi

echo "📡 Connecting and deploying..."

ssh -i "$SSH_KEY" $SSH_KNOWN_HOSTS_OPTION -p "$SSH_PORT" "$SSH_USER"@localhost bash -s <<'EOF'
set -euo pipefail

# Required variables passed through environment:
# DEPLOY_DIR, REPO_URL, REPO_NAME

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
CHANGED=$(git diff --name-only HEAD@{1} HEAD | grep -E '^(src/|tests/|pyproject\\.toml|Dockerfile)' || true)

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
EOF

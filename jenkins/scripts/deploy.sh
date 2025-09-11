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

ssh -i "$SSH_KEY" $SSH_KNOWN_HOSTS_OPTION -p "$SSH_PORT" "$SSH_USER"@localhost env \
    DEPLOY_DIR="$DEPLOY_DIR" \
    REPO_URL="$REPO_URL" \
    REPO_NAME="$REPO_NAME" \
    bash -s < jenkins/scripts/remote_deploy.sh

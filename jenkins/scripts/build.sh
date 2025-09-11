#!/bin/bash
set -e

echo "🏗️ Building Docker image..."
docker build . -t homelab-api:latest

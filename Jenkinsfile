pipeline {
    agent any

    environment {
        CLOUDFLARED_BIN = "${HOME}/.local/bin/cloudflared"
        UV_BIN = "${HOME}/.local/bin/uv"
        SSH_KNOWN_HOSTS_OPTION = '-o StrictHostKeyChecking=no'
        PYTHON_VERSION = '3.12'
        PATH = "${HOME}/.local/bin:${PATH}"
        VERSION = "v${env.BUILD_NUMBER}"
    }

    options {
        timestamps()
        timeout(time: 15, unit: 'MINUTES')
    }

    parameters {
        string(name: 'CLOUDFLARED_VERSION', defaultValue: '2024.8.0')
        string(name: 'CLOUDFLARED_ARCH', defaultValue: 'linux-amd64')
        string(name: 'SSH_HOSTNAME', defaultValue: 'ssh.tesutotech.my.id')
        string(name: 'DEPLOY_DIR', defaultValue: '~/homelab-apps')
        booleanParam(name: 'USE_RANDOM_PORT', defaultValue: false)
        booleanParam(name: 'STRICT_HOST_CHECKING', defaultValue: false)
    }

    stages {
        stage('Setup') {
            steps {
                script {
                    env.SSH_PORT = params.USE_RANDOM_PORT
                        ? sh(script: "shuf -i 2000-65000 -n 1", returnStdout: true).trim()
                        : '2222'

                    env.TUNNEL_LOCAL_BIND = "localhost:${env.SSH_PORT}"
                    env.CLOUDFLARED_URL = "https://github.com/cloudflare/cloudflared/releases/download/${params.CLOUDFLARED_VERSION}/cloudflared-${params.CLOUDFLARED_ARCH}"
                    env.REPO_URL = sh(script: 'git config --get remote.origin.url', returnStdout: true).trim()
                    env.REPO_NAME = env.REPO_URL.tokenize('/').last().replace('.git', '')
                    env.DEPLOY_DIR = "${params.DEPLOY_DIR}/${env.REPO_NAME}"
                    if (params.STRICT_HOST_CHECKING) {
                        env.SSH_KNOWN_HOSTS_OPTION = ''
                    }
                    sh 'mkdir -p "$(dirname $CLOUDFLARED_BIN)"'
                    sh 'mkdir -p "$(dirname $UV_BIN)"'
                    writeFile file: '.tunnel_log_path', text: sh(script: 'mktemp', returnStdout: true).trim()
                }
            }
        }

        stage('Install Tools') {
            steps {
                sh '''
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
                '''
            }
        }

        stage('Test & Lint') {
            steps {
                sh '''
                    echo "🐍 Setting up virtual environment and installing dependencies..."
                    uv venv
                    uv pip install '.[dev]'

                    echo "🧪 Running tests with coverage..."
                    uv run coverage run -m pytest
                    uv run coverage report -m

                    echo "🔍 Running linter..."
                    uv run ruff check .
                '''
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                    echo "🛡️ Scanning for vulnerable Python packages..."
                    uv pip install '.[dev]'
                    uv run pip-audit
                '''
            }
        }

        stage('Tag Release') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'f856e05c-4757-4368-a28b-0a6804256f56', keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')]) {
                    sh '''
                        echo "🔖 Tagging release ${VERSION}..."
                        git config --global user.email "jenkins@example.com"
                        git config --global user.name "Jenkins"
                        git tag -a "${VERSION}" -m "Release ${VERSION}"
                        git push origin "${VERSION}"
                    '''
                }
            }
        }

        stage('Deploy to Homelab') {
            steps {
                withCredentials([
                    string(credentialsId: '3e686402-a4a8-4278-8116-0a726c671824', variable: 'CLIENT_ID'),
                    string(credentialsId: 'af1d8abd-ada2-45c6-8d8c-b518135c759b', variable: 'CLIENT_SECRET'),
                    sshUserPrivateKey(credentialsId: 'f856e05c-4757-4368-a28b-0a6804256f56', keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')
                ]) {
                    sh '''
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
                            echo "⏳ Waiting ($i)..."
                            sleep 2
                        done

                        if ! nc -z localhost "$SSH_PORT"; then
                            echo "❌ Tunnel did not open"
                            tail -n 20 "$TEMP_TUNNEL_LOG" || true
                            kill "$TUNNEL_PID" || true
                            exit 1
                        fi

                        echo "📡 Connecting and deploying..."

                        ssh -i "$SSH_KEY" $SSH_KNOWN_HOSTS_OPTION -p "$SSH_PORT" "$SSH_USER"@localhost DEPLOY_DIR="$DEPLOY_DIR" REPO_URL="$REPO_URL" REPO_NAME="$REPO_NAME" bash <<-'EOF'
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

# Best-effort rollback: Tag the current image so we can manually revert if needed.
# The image name is determined by docker-compose, typically <project_name>_web
IMAGE_NAME="${REPO_NAME}_web"
echo "PREVIOUS_IMAGE_TAG=${IMAGE_NAME}:previous-good" > .env.previous
docker image inspect "${IMAGE_NAME}:latest" &> /dev/null && \
    docker tag "${IMAGE_NAME}:latest" "${IMAGE_NAME}:previous-good" || \
    echo "No previous image to tag as good."


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

# You can add a Trivy scan here for the newly built image if Trivy is installed on the remote host.
# trivy image --exit-code 1 --severity CRITICAL,HIGH "${IMAGE_NAME}:latest"

echo "🚀 Starting Docker Compose"
docker compose up -d

echo "✅ Deploy finished"
EOF
                    '''
                }
            }
        }
    }

    post {
        always {
            sh '''
                if [ -f tunnel.pid ]; then
                    kill "$(cat tunnel.pid)" || true
                    rm -f tunnel.pid
                fi

                if [ -f .tunnel_log_path ]; then
                    cp "$(cat .tunnel_log_path)" tunnel.log || true
                fi
            '''
            archiveArtifacts artifacts: 'tunnel.log', onlyIfSuccessful: false
            echo "🧹 Cleanup complete."
        }
        success {
            // Placeholder for success notifications
            echo "✅ Pipeline completed successfully!"
            // Example for Slack:
            // slackSend channel: '#ci', message: "✅ Success: ${env.JOB_NAME} build #${env.BUILD_NUMBER}. See: ${env.BUILD_URL}"
        }
        failure {
            // Placeholder for failure notifications
            echo "❌ Pipeline failed. See tunnel.log for more info."
            // Example for Slack:
            // slackSend channel: '#ci', message: "❌ Failed: ${env.JOB_NAME} build #${env.BUILD_NUMBER}. See: ${env.BUILD_URL}"
        }
    }
}
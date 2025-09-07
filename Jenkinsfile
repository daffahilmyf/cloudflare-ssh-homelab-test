pipeline {
    agent any

    environment {
        CLOUDFLARED_BIN = "${HOME}/.local/bin/cloudflared"
        UV_BIN = "${HOME}/.local/bin/uv"
        SSH_KNOWN_HOSTS_OPTION = '-o StrictHostKeyChecking=no'
        PYTHON_VERSION = '3.12'
        PATH = "${HOME}/.local/bin:${PATH}"
    }

    options {
        timestamps()
        timeout(time: 15, unit: 'MINUTES')
    }

    parameters {
        string(name: 'CLOUDFLARED_VERSION', defaultValue: '2024.8.0', description: 'Version of cloudflared to use')
        string(name: 'CLOUDFLARED_ARCH', defaultValue: 'linux-amd64', description: 'cloudflared architecture (e.g., linux-amd64)')
        string(name: 'SSH_HOSTNAME', defaultValue: 'ssh.tesutotech.my.id', description: 'Cloudflare tunnel hostname')
        string(name: 'DEPLOY_DIR', defaultValue: '~/homelab-apps/my-repo', description: 'Target directory on the remote machine')
        booleanParam(name: 'USE_RANDOM_PORT', defaultValue: false, description: 'Use a random port for the local tunnel')
        booleanParam(name: 'STRICT_HOST_CHECKING', defaultValue: false, description: 'Enable strict SSH host key checking')
    }

    stages {
        stage('Setup') {
            steps {
                script {
                    env.SSH_HOSTNAME = params.SSH_HOSTNAME?.trim()
                    env.CLOUDFLARED_VERSION = params.CLOUDFLARED_VERSION?.trim()
                    env.CLOUDFLARED_ARCH = params.CLOUDFLARED_ARCH?.trim()
                    env.DEPLOY_DIR = params.DEPLOY_DIR?.trim()
                    env.DEFAULT_SSH_PORT = '2222'
                    env.SSH_PORT = params.USE_RANDOM_PORT ? sh(script: "shuf -i 2000-65000 -n 1", returnStdout: true).trim() : env.DEFAULT_SSH_PORT
                    env.TUNNEL_LOCAL_BIND = "localhost:${env.SSH_PORT}"
                    env.CLOUDFLARED_URL = "https://github.com/cloudflare/cloudflared/releases/download/${env.CLOUDFLARED_VERSION}/cloudflared-${env.CLOUDFLARED_ARCH}"
                    env.REPO_URL = env.GIT_URL ?: sh(script: 'git config --get remote.origin.url', returnStdout: true).trim()

                    if (params.STRICT_HOST_CHECKING) {
                        env.SSH_KNOWN_HOSTS_OPTION = ''
                    }

                    sh 'mkdir -p "$(dirname $CLOUDFLARED_BIN)"'
                    sh 'mkdir -p "$(dirname $UV_BIN)"'
                    def logPath = sh(script: 'mktemp', returnStdout: true).trim()
                    writeFile file: '.tunnel_log_path', text: logPath
                }
            }
        }

        stage('Install Tools') {
            steps {
                sh '''
                    # Install cloudflared
                    if [ -x "$CLOUDFLARED_BIN" ]; then
                        echo "✅ Using cached cloudflared"
                        "$CLOUDFLARED_BIN" --version
                    else
                        echo "⬇️ Downloading cloudflared..."
                        curl -fsSL "$CLOUDFLARED_URL" -o "$CLOUDFLARED_BIN"
                        chmod +x "$CLOUDFLARED_BIN"
                        "$CLOUDFLARED_BIN" --version
                    fi

                    # Install uv
                    if [ -x "$UV_BIN" ]; then
                        echo "✅ Using cached uv"
                        "$UV_BIN" --version
                    else
                        echo "⬇️ Downloading uv..."
                        curl -LsSf https://astral.sh/uv/install.sh | sh
                    fi
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    echo "🐍 Setting up virtual environment with uv..."
                    uv venv

                    echo "🐍 Installing Python dependencies..."
                    uv pip install '.[dev]'

                    echo "🧪 Running tests with coverage..."
                    uv run coverage run -m pytest
                    uv run coverage report -m
                '''
            }
        }


        stage('Lint') {
            steps {
                sh '''
                    echo "🔍 Running linter..."
                    uv pip install ruff
                    ruff check .
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "🏗️ Building Docker image..."
                    docker build . -t homelab-api:latest
                '''
            }
        }

        stage('Deploy to Homelab') {
            steps {
                withCredentials([
                    string(credentialsId: '3e686402-a4a8-4278-8116-0a726c671824', variable: 'CLIENT_ID'),
                    string(credentialsId: 'af1d8abd-ada2-45c6-8d8c-b518135c759b', variable: 'CLIENT_SECRET'),
                    sshUserPrivateKey(credentialsId: 'f856e05c-4757-4368-a28b-0a6804256f56', keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')
                ]) {
                    script {
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

                            echo "⏳ Waiting for tunnel..."
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

                            ssh -i "$SSH_KEY" $SSH_KNOWN_HOSTS_OPTION -p "$SSH_PORT" "$SSH_USER"@localhost \
                              DEPLOY_DIR="$DEPLOY_DIR" REPO_URL="$REPO_URL" bash <<'EOF'
set -euo pipefail
mkdir -p "$DEPLOY_DIR"
cd "$DEPLOY_DIR"

if [ ! -d .git ]; then
    echo "📥 Cloning repo $REPO_URL"
    git clone "$REPO_URL" .
else
    echo "🔁 Pulling latest changes"
    git pull
fi

echo "🛑 Stopping Docker Compose"
docker compose down || true

echo "🚀 Starting Docker Compose"
docker compose up -d

echo "✅ Deploy finished"
EOF
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                sh '''
                    if [ -f tunnel.pid ]; then
                        kill "$(cat tunnel.pid)" || true
                        rm -f tunnel.pid
                    fi

                    if [ -f .tunnel_log_path ]; then
                        cp "$(cat .tunnel_log_path)" tunnel.log || true
                    fi
                '''
            }

            archiveArtifacts artifacts: 'tunnel.log', onlyIfSuccessful: false
            echo "🧹 Cleanup complete."
        }

        success {
            echo "✅ Pipeline completed successfully!"
        }

        failure {
            echo "❌ Pipeline failed. See tunnel.log for more info."
        }
    }
}
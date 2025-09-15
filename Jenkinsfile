pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo "Building PR #${env.CHANGE_ID} from ${env.CHANGE_BRANCH}"
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
            }
        }

        stage('Deploy Preview') {
            when {
                branch 'PR-*'
            }
            steps {
                echo 'Deploying preview...'
            }
        }
    }

    post {
        success {
            echo "Success ✅"
        }
        failure {
            echo "Failed ❌"
        }
    }
}

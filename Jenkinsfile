pipeline {
    agent any

    environment {
        PYTHON = 'python3'
        VENV_DIR = 'TestAutomation/.venv'
        REPORT_DIR = 'TestAutomation/HTML_Reports'
        SCREENSHOT_DIR = 'TestAutomation/Screenshots'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python venv') {
            steps {
                sh "${PYTHON} --version || true"
                sh "${PYTHON} -m venv ${VENV_DIR}"
                sh "${VENV_DIR}/bin/pip install --upgrade pip"
                // Install required packages explicitly in case requirements.txt is absent
                //sh "${VENV_DIR}/bin/pip install selenium openpyxl"
                // If you later add a requirements file, uncomment the next line
                sh "[ -f TestAutomation/requirements.txt ] && ${VENV_DIR}/bin/pip install -r TestAutomation/requirements.txt || true"
            }
        }

        stage('Run Selenium Tests') {
            steps {
                sh 'chmod +x TestAutomation/RunTest.sh'
                sh 'TestAutomation/RunTest.sh'
            }
        }

        stage('Archive Artifacts') {
            steps {
                archiveArtifacts artifacts: 'TestAutomation/HTML_Reports/*.html, TestAutomation/Screenshots/*.png', allowEmptyArchive: true
            }
        }

        stage('Publish HTML Reports') {
            when {
                expression { fileExists(env.REPORT_DIR) }
            }
            steps {
                script {
                    // Publish all HTML files in the report directory if the HTML Publisher plugin is available
                    try {
                        publishHTML(target: [
                            reportDir: env.REPORT_DIR,
                            reportFiles: '*.html',
                            reportName: 'Selenium Test Reports',
                            alwaysLinkToLastBuild: true,
                            keepAll: true,
                            allowMissing: true
                        ])
                    } catch (ignored) {
                        echo 'HTML Publisher plugin not available; skipping publishHTML.'
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
        }
        failure {
            echo 'Pipeline failed.'
        }
        success {
            echo 'Pipeline succeeded.'
        }
    }
}

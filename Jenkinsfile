pipeline {
    agent any

    environment {
        PYTHON = 'python3'
        // Absolute path to use local files on the Jenkins node
        LOCAL_ROOT = '/home/adarsh/projects/Final_Dissertation'
        VENV_DIR = "${LOCAL_ROOT}/TestAutomation/.venv"
        REPORT_DIR = 'TestAutomation/HTML_Reports'
        SCREENSHOT_DIR = 'TestAutomation/Screenshots'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Skipping git checkout; using local files from LOCAL_ROOT.'
            }
        }

        stage('Run Selenium Tests') {
            steps {
                // sh "chmod +x ${LOCAL_ROOT}/TestAutomation/RunTest.sh"
                sh "cd ${LOCAL_ROOT}/TestAutomation && ./RunTest.sh"

                // Copy artifacts back into the Jenkins workspace for archiving/publishing
                // sh "mkdir -p ${REPORT_DIR} ${SCREENSHOT_DIR}"
                // sh "cp -f ${LOCAL_ROOT}/TestAutomation/HTML_Reports/*.html ${REPORT_DIR}/ 2>/dev/null || true"
                // sh "cp -f ${LOCAL_ROOT}/TestAutomation/Screenshots/*.png ${SCREENSHOT_DIR}/ 2>/dev/null || true"
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

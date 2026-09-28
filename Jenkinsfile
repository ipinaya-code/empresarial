// Alternativa a Actions. Agente Linux dedicado, Python 3.12 y Podman rootless.
// Crear credencial secret-text boa-test-database-url hacia BD descartable boa_test.
// No conectar esta credencial a la base del laboratorio compartido o producción.
pipeline {
    agent { label 'podman' }
    options {
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '15'))
    }
    environment {
        APP_DEBUG = 'false'
        TEST_DATABASE_URL = credentials('boa-test-database-url')
    }
    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Dependencies') { steps { sh 'make setup PYTHON=python3.12' } }
        stage('Quality') { steps { sh 'make check' } }
        stage('PostgreSQL') { steps { sh 'make test-postgres' } }
        stage('OCI image') { steps { sh 'make build API_IMAGE=localhost/boa-reservas:ci-$BUILD_NUMBER' } }
    }
    post {
        always {
            junit allowEmptyResults: true, testResults: 'artifacts/pytest-*.xml'
            archiveArtifacts allowEmptyArchive: true, artifacts: 'artifacts/**'
        }
    }
}

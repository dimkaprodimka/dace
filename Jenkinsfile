pipeline {
    agent { dockerfile true }
    stages {
        stage('Test') {
            steps {
		sh 'curl http://127.0.0.1:6878'
                sh 'node --version'
                sh 'svn --version'
            }
        }
    }
}

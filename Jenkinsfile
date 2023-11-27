pipeline {
    agent { dockerfile true }
    stages {
        stage('Test') {
            steps {
		sh 'curl "http://127.0.0.1:6878/webui/api/service?method=get_version" | grep linux'
               
              
            }
        }
    }
}

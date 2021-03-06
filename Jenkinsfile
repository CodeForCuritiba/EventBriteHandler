#!groovy

pipeline {
    agent {
        docker { image 'joepreludian/python-poetry:latest' }
    }
    triggers {
        cron('*/15 * * * *')
    }
    stages {
        stage('Run') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'codecwb-eventbrite-token', variable: 'TOKEN_ID'),
                                     string(credentialsId: 'codecwb-eventbrite-event-id', variable: 'EVENT_ID'),
                                     string(credentialsId: 'codecwb-telegram-token', variable: 'TELEGRAM_TOKEN_ID'),
                                     string(credentialsId: 'codecwb-telegram-chat-id', variable: 'TELEGRAM_CHAT_ID')]) {

                        sh 'poetry export -o requirements.txt'
                        sh 'pip3 install -r requirements.txt'
                        sh 'python fetch.py'
                    }
                }
            }
        }
    }
}

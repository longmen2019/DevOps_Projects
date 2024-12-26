

# Netflix Server Setup Guide

## Create EC2 Instance
1. **Create an EC2 instance** with the following specifications:
   - **Instance Type**: t2.large
   - **Name**: `netflix-server`

## SSH into EC2
1. **SSH into the EC2 instance** using the SSH key pair you created:
    ```sh
    ssh -i /path/to/ssh-key.pem ubuntu@your-ec2-instance-ip
    ```

## Install Docker
1. **Update the package list and install Docker**:
    ```sh
    sudo apt-get update
    sudo apt-get install -y docker.io
    ```

## Install Java Runtime Environment (JRE)
1. **Update the package list and install JRE**:
    ```sh
    sudo apt update
    sudo apt install -y fontconfig openjdk-17-jre
    java -version
    ```

## Clone the Repository
1. **Clone your repository**:
    ```sh
    git clone https://github.com/your-repo/your-project.git
    cd your-project
    ```

## Build and Run Docker Container
1. **Build the Docker image**:
    ```sh
    sudo docker build -t netflix .
    ```
2. **List Docker images to verify**:
    ```sh
    sudo docker images
    ```
3. **Run the Docker container**:
    ```sh
    sudo docker run -d -p 8081:80 <image-id>
    ```

## Additional Setup Steps

### Enable Port 8081
1. **Ensure port 8081 is enabled for inbound traffic** in your security groups.
2. **Access the application** at: `http://your-ec2-instance-ip:8081/browse`.

### Generate TMDB API Key
1. **Go to [The Movie Database (TMDB)](https://www.themoviedb.org/)** to generate your API key.
2. **Update the Docker build with your API key**:
    ```sh
    sudo docker build --build-arg TMDB_V3_API_KEY=<your-api-key> -t netflix .
    ```

### Running SonarQube
1. **Run the SonarQube container**:
    ```sh
    sudo docker run -d --name sonar -p 9000:9000 sonarqube:lts-community
    ```
2. **If you stop the container and need to start SonarQube again**:
    ```sh
    sudo docker start sonar
    sudo docker restart sonar
    ```

### Install Jenkins
1. **Add Jenkins key and source list, then install Jenkins**:
    ```sh
    sudo wget -O /usr/share/keyrings/jenkins-keyring.asc https://pkg.jenkins.io/debian/jenkins.io-2023.key
    echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian binary/" | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y jenkins
    ```
2. **Check Jenkins status**:
    ```sh
    sudo service jenkins status
    ```
3. **Go to Jenkins server and install the following plugins**:
    - NodeJS
    - SonarQube Scanner
    - Eclipse Temurin Installer
    - Docker Plugin
    - Docker Commons Plugin
    - Docker Pipeline
    - Docker API
    - Docker Build Step
4. **Add JDK from [Adoptium](https://adoptium.net/) and name it `jdk17`**.

### Install OWASP Dependency-Check on Jenkins
1. **Install the OWASP Dependency-Check plugin** from the Jenkins plugin manager.

### Creating Another EC2 for Monitoring
1. **Create a new EC2 instance** with the following specifications:
    - **Instance Type**: t2.medium
2. **Add a Prometheus user**:
    ```sh
    sudo useradd --system --no-create-home --shell /bin/false prometheus
    ```
3. **Follow the instructions to install Prometheus and Node Exporter** from [this guide](https://antonputra.com/monitoring/install-prometheus-and-grafana-on-ubuntu/#install-node-exporter-on-ubuntu-2004).

### Troubleshooting Docker Daemon Permission Issues
If your Jenkins job encounters permission issues connecting to the Docker daemon, follow these steps:

#### Grant Jenkins User Access to Docker
1. **Add Jenkins User to Docker Group**:
    ```sh
    sudo usermod -aG docker jenkins
    ```
2. **Restart Jenkins Service**:
    ```sh
    sudo systemctl restart jenkins
    ```
3. **Restart Docker Service**:
    ```sh
    sudo systemctl restart docker
    ```

#### Verify Docker Group Membership
1. **Check if Jenkins User is in Docker Group**:
    ```sh
    groups jenkins
    ```
    Ensure `docker` is listed. If not, the user wasn't added properly.

#### Re-run Your Jenkins Job
After performing these steps, try re-running your Jenkins pipeline to see if the issue is resolved. If you still encounter permission errors, consider running the Docker commands with `sudo` in your Jenkins pipeline, noting that this may require additional configuration.

### Connect SonarQube to Jenkins
1. **Navigate to SonarQube**:
    - Administration > User > Find Jenkins > Copy Password
2. **Go to Jenkins**:
    - Credentials > Paste the Password > Manage Jenkins > Configure > SonarQube Server

### Additional Instructions
- **Edit Prometheus configuration**:
    ```sh
    sudo nano /path/to/prometheus.yaml
    ```
- **Install Grafana**:
    Follow [these instructions](https://grafana.com/docs/grafana/latest/setup-grafana/installation/debian/) to install Grafana. Grafana runs on port 3000.

### Grafana Dashboard
- Use [this dashboard](https://grafana.com/grafana/dashboards/1860-node-exporter-full/) for monitoring node exporter metrics.

### Docker Commands
- **Logout**:
    ```sh
    docker logout
    ```
- **Login**:
    ```sh
    docker login -u longmen2022 -p ********
    ```

### Jenkins Pipeline: Stage View Plugin
To see stage builds in Jenkins, you can use the Pipeline: Stage View plugin. Here's a quick guide to get you started:
- **Install the Plugin**: Go to Jenkins' main page, click on "Manage Jenkins," then "Manage Plugins." Search for "Pipeline: Stage View" and install it.

### Jenkins Pipeline Example
```groovy
pipeline {
    agent any
    tools {
        jdk 'jdk17'
        nodejs 'node16'
    }
    environment {
        SCANNER_HOME = tool 'sonar-scanner'
    }
    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }
        stage('Checkout from Git') {
            steps {
                git branch: 'main', url: 'https://github.com/N4si/DevSecOps-Project.git'
            }
        }
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sonar-server') {
                    sh '''
                    $SCANNER_HOME/bin/sonar-scanner \
                    -Dsonar.projectName=Netflix \
                    -Dsonar.projectKey=Netflix
                    '''
                }
            }
        }
        stage('Install Dependencies') {
            steps {
                sh 'npm install'
            }
        }
        stage('Docker Build & Push') {
            steps {
                script {
                    withDockerRegistry(credentialsId: 'docker', toolName: 'docker') {
                        sh '''
                        docker build --build-arg TMDB_V3_API_KEY=<your-api-key> -t netflix .
                        docker tag netflix longmen2022/netflix:latest
                        docker push longmen2022/netflix:latest
                        '''
                    }
                }
            }
        }
        stage('Deploy to Container') {
            steps {
                sh 'docker run -d -p 8081:80 longmen2022/netflix:latest'
            }
        }
    }
    post {
        always {
            emailext(
                attachLog: true,
                subject: "'${currentBuild.result}'",
                body: "Project: ${env.JOB_NAME}<br/>" +
                      "Build Number: ${env.BUILD_NUMBER}<br/>" +
                      "URL: ${env.BUILD_URL}<br/>",
                to: 'lmen776@gmail.com'
            )
        }
    }
}
```


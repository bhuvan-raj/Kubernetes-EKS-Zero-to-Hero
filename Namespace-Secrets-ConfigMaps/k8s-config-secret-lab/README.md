# Kubernetes ConfigMaps & Secrets Lab


## Project Overview

This project provides a hands-on laboratory exercise to demonstrate the fundamental concepts of Kubernetes `ConfigMaps` and `Secrets`. It involves a simple Python Flask web application that retrieves its non-sensitive configuration data from a `ConfigMap` and sensitive credentials from a `Secret`.

The lab will guide you through creating these Kubernetes objects, deploying an application that consumes them, and observing how changes to ConfigMaps and Secrets are reflected in a running application.

## Features

* **ConfigMap Usage:** Demonstrates how to inject non-sensitive configuration (application title, welcome message, log level) into Pods as environment variables.
* **Secret Usage:** Illustrates how to securely provide sensitive data (database username, password, API key) to Pods by mounting Secrets as files.
* **Dynamic Updates:** Shows the different behaviors of ConfigMap/Secret updates when consumed as environment variables vs. mounted files, and how to trigger application reloads.
* **Minimal Flask App:** A simple web application built with Flask to serve as the consumer of Kubernetes configuration.

## Prerequisites

Before you begin, ensure you have the following installed and configured:

* **Kubernetes Cluster:** A running Kubernetes cluster (e.g., Minikube, Kind, Docker Desktop Kubernetes, GKE, EKS, AKS).
* **`kubectl`:** The Kubernetes command-line tool, configured to connect to your cluster.
* **Docker:** (Optional, but recommended for building the image) A Docker installation to build and push container images.
* **Git:** To clone this repository (if applicable).

## Project Structure
k8s-config-secret-lab/
├── app.py                     # Python Flask web application
├── requirements.txt           # Python dependencies for the Flask app
├── Dockerfile                 # Dockerfile to build the application image
├── configmap.yaml             # Kubernetes ConfigMap definition
├── secret.yaml                # Kubernetes Secret definition
└── deployment-service.yaml    # Kubernetes Deployment and Service definitions
└── README.md                  # This README file

## Getting Started

Follow these steps to deploy the application and explore ConfigMaps and Secrets.

### 1. Clone the Repository

First, create a directory for your lab and place all the files listed above inside it:

```bash
mkdir k8s-config-secret-lab
```
```
cd k8s-config-secret-lab
```
Now, create each file manually as provided in the instructions above Or copy paste the contents from the files provided inside this folder

## 2. Build & Push Docker Image

You need to build the Docker image for the Flask application and push it to a container registry that your Kubernetes cluster can access (e.g., Docker Hub, Google Container Registry, GitHub Container Registry).

- Build the Docker image:
```
docker build -t your_docker_repo/my-k8s-app:1.0 .
```
IMPORTANT: Replace your_docker_repo with your Docker Hub username or the address of your private registry (e.g., ghcr.io/your_github_username).

- Push the Docker image:
```
docker push your_docker_repo/my-k8s-app:1.0
```
Create Kubernetes ConfigMap
```
kubectl apply -f configmap.yaml
```
Verify:
```
kubectl get configmap app-config -o yaml
```


Create Kubernetes Secret

```
kubectl apply -f secret.yaml
```

Verify and Observe Encoding:

```
kubectl get secret app-secrets -o yaml
```

Deploy Application

Now, deploy the Flask application using the deployment-service.yaml file. Remember to update the image field in deployment-service.yaml to point to your pushed Docker image.

```
# Inside deployment-service.yaml, locate this line and update:
        image: your_docker_repo/my-k8s-app:1.0 # <<-- UPDATE THIS LINE
```

Then apply the deployment:

```
kubectl apply -f deployment-service.yaml
```

Monitor Deployment:

```
kubectl get deployment my-k8s-app-deployment
kubectl get pods -l app=my-k8s-app
```
Wait until the Pod is Running.

Get the Node's Private IP and the Service's NodePort:

Get the Node's Private IP:
First, identify your Kubernetes node(s).

```
kubectl get nodes -o wide
```
Look for the INTERNAL-IP column. If you have multiple nodes, pick one.


Get the Service's NodePort:

Now, get the NodePort assigned to your service.
```
kubectl get service my-k8s-app-service
```
In the output, under the PORT(S) column, you'll see something like 80:3xxxx/TCP. The 3xxxx part is the NodePort that Kubernetes has randomly assigned (it will be in the range 30000-32767).

For example, if the output is 80:30345/TCP, your NodePort is 30345.

Access the Application:
Combine the Node's Private IP and the Service's NodePort:

Open your web browser and go to:
```
http://<NODE_PRIVATE_IP>:<NODE_PORT>
```
You will see the results containing data which we gave in configmaps

### If you are using killercoda or anyother Distributions which doesnt facilitate public IP
Use the Curl within the cluster and identify the change in the index.html

```
curl http://<NODE_PRIVATE_IP>:<NODE_PORT>
```


Cleanup

To remove all the resources created during this lab:
```
kubectl delete -f deployment-service.yaml
kubectl delete -f configmap.yaml
kubectl delete -f secret.yaml
```



















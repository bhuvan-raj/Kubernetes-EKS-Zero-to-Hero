# EKS HPA, Taints, and Tolerations Lab 🚀

This lab guides you through setting up an Amazon EKS (Elastic Kubernetes Service) cluster and demonstrating key Kubernetes features: **Horizontal Pod Autoscaling (HPA)**, **Taints**, and **Tolerations**. You'll deploy an application, configure HPA to automatically scale it based on CPU utilization, and then use taints and tolerations to control where your application's pods can be scheduled.

-----

## 🎯 Objectives

  * Create an **EKS Cluster** using `eksctl`.
  * Deploy a sample Nginx application.
  * Configure and observe **Horizontal Pod Autoscaling (HPA)** for the Nginx application.
  * Apply a **taint** to an EKS worker node.
  * Modify the Nginx deployment to include **tolerations**, allowing pods to schedule on the tainted node.

-----

## 📋 Prerequisites

Before you begin, ensure you have the following tools installed and configured:

  * **AWS CLI:** Configured with appropriate IAM permissions to create and manage EKS clusters.
      * [AWS CLI Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
  * **`kubectl`:** The Kubernetes command-line tool.
      * [Install kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
  * **`eksctl`:** A simple CLI tool for creating and managing EKS clusters.
      * [Install eksctl](https://www.google.com/search?q=https://eksctl.io/introduction/%23installation)
  * **Helm (Optional):** While not strictly required for this basic lab, Helm is a package manager for Kubernetes and is often used in real-world scenarios.

-----

## 🚀 Lab Steps

### 1\. Create an EKS Cluster

We'll use `eksctl` to provision a new EKS cluster quickly.

```bash
eksctl create cluster \
  --name eks-hpa-taint-lab \
  --region ap-south-1 \
  --version 1.29 \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 3 \
  --with-oidc \
  --managed
```

  * **`--name eks-hpa-taint-lab`**: Your cluster's name.
  * **`--region ap-south-1`**: **Important for users in Bengaluru, India.**
  * **`--nodes 2`**: Starts with two worker nodes.
  * The command will take several minutes to complete. Once done, verify your `kubectl` context:
    ```bash
    kubectl get nodes
    ```

-----

### 2\. Deploy an Application for HPA

Deploy a simple Nginx application that can be targeted by HPA. The deployment includes CPU resource requests and limits, which are essential for HPA to function.

**`nginx-deployment.yaml`**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-hpa-demo
  labels:
    app: nginx-hpa-demo
spec:
  replicas: 2 # Start with 2 replicas
  selector:
    matchLabels:
      app: nginx-hpa-demo
  template:
    metadata:
      labels:
        app: nginx-hpa-demo
    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: "200m" # Request 200m CPU
            memory: "256Mi"
          limits:
            cpu: "500m" # Limit to 500m CPU
            memory: "512Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-hpa-demo-service
spec:
  selector:
    app: nginx-hpa-demo
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: ClusterIP
```

Apply the deployment:

```bash
kubectl apply -f nginx-deployment.yaml
```

Verify the deployment:

```bash
kubectl get deployments nginx-hpa-demo
kubectl get pods -l app=nginx-hpa-demo
```

-----

### 3\. Configure Horizontal Pod Autoscaler (HPA)

Create an HPA resource to automatically scale your Nginx pods based on **CPU utilization**. We'll set a target of 50% CPU utilization.

**`hpa.yaml`**:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nginx-cpu-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-hpa-demo
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50 # Target 50% CPU utilization
```

Apply the HPA:

```bash
kubectl apply -f hpa.yaml
```

Check HPA status:

```bash
kubectl get hpa
```

#### Testing HPA (Simulating Load)

To see HPA in action, simulate CPU load on your Nginx pods.

1.  Get a pod name:
    ```bash
    NGINX_POD=$(kubectl get pods -l app=nginx-hpa-demo -o jsonpath='{.items[0].metadata.name}')
    echo $NGINX_POD
    ```
2.  Exec into the pod and run a CPU-intensive command:
    ```bash
    kubectl exec -it $NGINX_POD -- /bin/sh -c "while true; do true; done" &
    ```
    *(Remember to press `Ctrl+C` in the terminal where you ran `kubectl exec` to stop the load.)*
3.  Monitor HPA scaling:
    ```bash
    kubectl get hpa -w
    ```
    Observe the `CURRENT` CPU utilization increase and the `REPLICAS` scale up. After stopping the load, pods will scale back down.

-----

### 4\. Apply Taints to a Node

Taints prevent pods from being scheduled on a node unless they have a matching toleration. We'll taint one of your EKS worker nodes.

1.  Get your node names:
    ```bash
    kubectl get nodes
    ```
2.  Choose one node (e.g., `ip-192-168-XX-XXX.ap-south-1.compute.internal`) and apply a taint:
    ```bash
    kubectl taint nodes <YOUR_NODE_NAME> dedicated=special:NoSchedule
    ```
      * **`dedicated=special`**: The key-value pair for the taint.
      * **`NoSchedule`**: Effect means new pods won't be scheduled unless they tolerate it.
3.  Verify the taint:
    ```bash
    kubectl describe node <YOUR_NODE_NAME> | grep Taints
    ```

-----

### 5\. Configure Tolerations for the Application

Modify your Nginx deployment to include `tolerations`. This allows Nginx pods to be scheduled on the node you just tainted.

**Update `nginx-deployment.yaml`**: Add the `tolerations` section under `spec.template.spec`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-hpa-demo
  labels:
    app: nginx-hpa-demo
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx-hpa-demo
  template:
    metadata:
      labels:
        app: nginx-hpa-demo
    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: "200m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
      tolerations: # Add this section
      - key: "dedicated"
        operator: "Equal"
        value: "special"
        effect: "NoSchedule"
```

Apply the updated deployment:

```bash
kubectl apply -f nginx-deployment.yaml
```

Observe where pods are scheduled after the update (and potential re-scheduling due to scaling):

```bash
kubectl get pods -o wide -l app=nginx-hpa-demo
```

You should now see Nginx pods being scheduled on the tainted node.

-----

## 🧹 Cleanup

To avoid ongoing AWS charges, **always delete your EKS cluster** when you've finished the lab.

```bash
eksctl delete cluster --name eks-hpa-taint-lab --region ap-south-1
```

This command will remove all associated AWS resources, including EC2 instances, security groups, and IAM roles. This process may also take several minutes.

-----

This lab provides a foundational understanding of key Kubernetes operational aspects. Feel free to experiment further with different HPA metrics, taint effects (`NoExecute`, `PreferNoSchedule`), and node selectors\!

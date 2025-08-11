# **EKS LoadBalancer Service**

This lab demonstrates how to deploy an application in Amazon EKS and expose it using AWS Classic load balancer

* **Classic Load Balancer (CLB)** — default without AWS Load Balancer Controller

---

## **Prerequisites**

* An **Amazon EKS cluster** with at least one EC2 worker node group (Fargate-only clusters will not work for this example).
* `kubectl` configured for your cluster:

  ```bash
  aws eks update-kubeconfig --region <your-region> --name <your-cluster-name>
  ```
* AWS CLI installed with sufficient IAM permissions.
* EKSCTL installed

## **1. Create the Namespace**

```bash
kubectl create namespace my-app
```

---

## **2. Create the Deployment**

**`todoapp-deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: glasmorphism-todo
spec:
  replicas: 2
  selector:
    matchLabels:
      app: glasmorphism-todo
  template:
    metadata:
      labels:
        app: glasmorphism-todo
    spec:
      containers:
      - name: glasmorphism-todo
        image: bhuvanraj123/glasmorphism-todo:latest
        ports:
        - containerPort: 80

```

```bash
kubectl apply -f todoapp-deployment.yaml
```

---

## **3. Classic Load Balancer (Default)**

Without annotations, a `LoadBalancer` Service in EKS creates a **Classic Load Balancer**.

**`todoapp-service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: glasmorphism-todo-service
spec:
  type: LoadBalancer
  selector:
    app: glasmorphism-todo
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80

```

```bash
kubectl apply -f todo-service.yaml
```
###Test the loadbalancer

- Go to the aws console - EC2 - LoadBalancer
- Here you can see a classical loadbalancer created,check the target instances for verification

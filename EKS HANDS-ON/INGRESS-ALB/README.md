
# EKS Ingress Lab: Path-Based Routing with AWS Application Load Balancer (ALB) 🌐

This lab demonstrates how to deploy two custom web applications (`bhuvanraj123/myapp1:latest` and `bhuvanraj123/myapp2:latest`) on an **Amazon EKS cluster** and expose them via **path-based routing** using a single Kubernetes Ingress resource backed by an **AWS Application Load Balancer (ALB)**.

## Table of Contents

1.  [Prerequisites](https://www.google.com/search?q=%231-prerequisites-%E2%9A%99%EF%B8%8F)
2.  [Create IAM OIDC Provider for EKS](https://www.google.com/search?q=%232-create-iam-oidc-provider-for-eks-%F0%9F%94%90)
3.  [Deploy the AWS Load Balancer Controller](https://www.google.com/search?q=%233-deploy-the-aws-load-balancer-controller-%F0%9F%8F%97%EF%B8%8F)
4.  [Deploy Backend Applications to EKS](https://www.google.com/search?q=%234-deploy-backend-applications-to-eks-%F0%9F%9A%80)
5.  [Configure Ingress for Path-Based Routing](https://www.google.com/search?q=%235-configure-ingress-for-path-based-routing-%F0%9F%9A%A6)
6.  [Verify the Ingress Setup](https://www.google.com/search?q=%236-verify-the-ingress-setup-%E2%9C%85)
7.  [Cleanup (Optional)](https://www.google.com/search?q=%237-cleanup-optional-%F0%9F%A7%B9)

-----

## 1\. Prerequisites ⚙️

Ensure you have the following tools and configurations ready:

  * An **active Amazon EKS cluster**.
  * **`kubectl`** configured to communicate with your EKS cluster.
  * **`helm`** installed (version 3+ recommended).
  * **`aws cli`** configured and authenticated with the AWS account where your EKS cluster resides, with sufficient permissions to create IAM roles, policies, and Load Balancers.
  * Your custom Docker images `bhuvanraj123/myapp1:latest` and `bhuvanraj123/myapp2:latest` are already available on Docker Hub (or your chosen container registry).

-----

## 2\. Create IAM OIDC Provider for EKS 🔐

The AWS Load Balancer Controller relies on **IAM Roles for Service Accounts (IRSA)**, which requires an OpenID Connect (OIDC) identity provider to be associated with your EKS cluster. If you don't have one, create it using `eksctl`.

```bash
eksctl utils associate-iam-oidc-provider --cluster=<your-cluster-name> --approve
```

Replace `<your-cluster-name>` with the actual name of your EKS cluster. This command establishes trust between your EKS cluster and IAM, allowing Kubernetes Service Accounts to assume IAM roles.

-----

## 3\. Deploy the AWS Load Balancer Controller 🏗️

The **AWS Load Balancer Controller** is crucial for managing ALBs from within your EKS cluster. It watches for Ingress resources and provisions the corresponding AWS ALBs.

### a. Create IAM Policy and Role for the Controller

The ALB Controller needs specific IAM permissions to interact with AWS services. You'll create an IAM policy and an IAM role, then associate this role with the Kubernetes Service Account used by the controller.

1.  **Download the IAM Policy Document:**

    ```bash
    curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.5.4/docs/install/iam_policy.json
    ```

2.  **Create the IAM Policy in AWS:**

    ```bash
    aws iam create-policy \
        --policy-name AWSLoadBalancerControllerIAMPolicy \
        --policy-document file://iam_policy.json
    ```

    Make sure to note down the **`Arn`** of the created policy from the output.

3.  **Create an IAM Service Account for the Controller:**
    This command creates the necessary IAM role and associates it with a Kubernetes Service Account named `aws-load-balancer-controller` in the `kube-system` namespace.
    Replace `<cluster-name>` with your EKS cluster name and `<AWS_ACCOUNT_ID>` with your AWS account ID.

    ```bash
    eksctl create iamserviceaccount \
        --cluster <cluster-name> \
        --namespace kube-system \
        --name aws-load-balancer-controller \
        --attach-policy-arn arn:aws:iam::<AWS_ACCOUNT_ID>:policy/AWSLoadBalancerControllerIAMPolicy \
        --override-existing-serviceaccounts \
        --approve
    ```

### b. Add Helm Repository for the Controller

```bash
helm repo add eks https://aws.github.io/eks-charts
helm repo update
```

### c. Install the AWS Load Balancer Controller

Install the controller using Helm. Replace `<cluster-name>` with your EKS cluster name.

```bash
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
    -n kube-system \
    --set clusterName=<cluster-name> \
    --set serviceAccount.create=false \
    --set serviceAccount.name=aws-load-balancer-controller
```

### d. Verify AWS Load Balancer Controller Deployment

Wait a few minutes for the controller pods to become ready.

```bash
kubectl get deployment -n kube-system aws-load-balancer-controller
kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller
```

You should see pods in a `Running` state.

-----

## 4\. Deploy Backend Applications to EKS 🚀

Now, deploy your two custom UI applications (`myapp1` and `myapp2`) to EKS using the images you've already pushed to Docker Hub. These applications will run as Deployments and be exposed by internal ClusterIP Services.

### Application 1 Deployment and Service

**a. Create `app1-k8s.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app1-deployment
  labels:
    app: app1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app1
  template:
    metadata:
      labels:
        app: app1
    spec:
      containers:
      - name: app1-container
        image: bhuvanraj123/myapp1:latest # Your custom image for App 1
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: app1-service
  labels:
    app: app1
spec:
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP
  selector:
    app: app1
  type: ClusterIP # ALB Ingress will route to this internal ClusterIP Service
```

**b. Apply App 1 Manifests**

```bash
kubectl apply -f app1-k8s.yaml
```

-----

### Application 2 Deployment and Service

**a. Create `app2-k8s.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app2-deployment
  labels:
    app: app2
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app2
  template:
    metadata:
      labels:
        app: app2
    spec:
      containers:
      - name: app2-container
        image: bhuvanraj123/myapp2:latest # Your custom image for App 2
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: app2-service
  labels:
    app: app2
spec:
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP
  selector:
    app: app2
  type: ClusterIP # ALB Ingress will route to this internal ClusterIP Service
```

**b. Apply App 2 Manifests**

```bash
kubectl apply -f app2-k8s.yaml
```

### c. Verify Deployments and Services

```bash
kubectl get deployments
kubectl get services
kubectl get pods -l app=app1
kubectl get pods -l app=app2
```

Ensure all pods are `Running` and services are of `ClusterIP` type.

-----

## 5\. Configure Ingress for Path-Based Routing 🚦

Now, create an `Ingress` resource for path-based routing. The AWS Load Balancer Controller will detect this Ingress and automatically provision an ALB in your AWS account, configuring its listener rules based on your Ingress definition.

**a. Create `alb-ingress-path-based.yaml`**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-alb-path-ingress
  annotations:
    # Optional: You can keep this annotation for older Kubernetes versions or for clarity,
    # but the 'ingressClassName' field is the preferred method for K8s 1.19+
    # kubernetes.io/ingress.class: alb

    alb.ingress.kubernetes.io/scheme: internet-facing # Creates an internet-facing ALB
    alb.ingress.kubernetes.io/target-type: ip # Directs traffic to pod IPs
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}]' # Configure listener for HTTP on port 80
spec:
  ingressClassName: alb # <--- ADD THIS LINE! This tells Kubernetes which controller should manage this Ingress.
  rules:
  - http:
      paths:
      - path: /app1
        pathType: Prefix
        backend:
          service:
            name: app1-service
            port:
              number: 80
      - path: /app2
        pathType: Prefix
        backend:
          service:
            name: app2-service
            port:
              number: 80
```

**b. Apply the Path-Based Ingress**

```bash
kubectl apply -f alb-ingress-path-based.yaml
```

-----

## 6\. Verify the Ingress Setup ✅

After applying the Ingress manifest, give it a few minutes for the AWS Load Balancer Controller to provision the ALB and configure its rules.

### a. Check Ingress Status

```bash
kubectl get ingress
```

You should see your Ingress resource with an `ADDRESS` field. This will be the **DNS name of the AWS ALB** that was provisioned. Note this down.

### b. Verify AWS ALB in Console

You can also navigate to the **EC2 -\> Load Balancers** section in your AWS Console to see the newly created Application Load Balancer. It will have a name similar to `k8s-default-app-alb-path-ingress-xxxxxxxx`.

### c. Test Access

Use the `ADDRESS` (DNS name) of your Ingress.

```bash
curl http://<ALB_DNS_NAME>/app1
curl http://<ALB_DNS_NAME>/app2
```

You should see the content from your respective applications. Open these URLs in a web browser to see the custom UIs.

-----

## 7\. Cleanup (Optional) 🧹

To remove all resources created during this lab:

```bash
# Delete Ingress
kubectl delete -f alb-ingress-path-based.yaml

# The ALB will be automatically deleted by the controller when the Ingress resource is removed.

# Delete backend applications
kubectl delete -f app1-k8s.yaml
kubectl delete -f app2-k8s.yaml

# Delete AWS Load Balancer Controller and its IAM resources
helm uninstall aws-load-balancer-controller -n kube-system
kubectl delete serviceaccount aws-load-balancer-controller -n kube-system
aws iam delete-policy --policy-arn arn:aws:iam::<AWS_ACCOUNT_ID>:policy/AWSLoadBalancerControllerIAMPolicy # Replace <AWS_ACCOUNT_ID>

# Optionally, disassociate OIDC provider if this was the last thing using it
# eksctl utils disassociate-iam-oidc-provider --cluster=<your-cluster-name> --approve
```

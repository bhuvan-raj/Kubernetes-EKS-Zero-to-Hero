# **AWS EKS + ALB Ingress Lab **

---

## **Step 0 — Prerequisites**

* AWS CLI configured
* kubectl installed
* eksctl installed
* Helm installed
* Docker Hub images already exist:

  * `bhuvanraj123/myapp1:v3`
  * `bhuvanraj123/myapp2:v3`

---

## **Step 1 — Create EKS Cluster**

```bash
eksctl create cluster \
  --name ingress-lab \
  --region us-east-1 \
  --nodegroup-name worker-nodes \
  --node-type t3.medium \
  --nodes 2 \
  --managed
```

Verify nodes:

```bash
kubectl get nodes
```

---

## **Step 2 — Configure kubectl**

```bash
aws eks update-kubeconfig \
  --region us-east-1 \
  --name ingress-lab
```

---

## **Step 3 — Associate OIDC & create IAM policy for ALB**

```bash
eksctl utils associate-iam-oidc-provider \
  --region us-east-1 \
  --cluster ingress-lab \
  --approve
```

```bash
curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json
aws iam create-policy \
  --policy-name AWSLoadBalancerControllerIAMPolicy \
  --policy-document file://iam_policy.json
```

---

## **Step 4 — Create IAM Service Account for ALB Controller**

```bash
eksctl create iamserviceaccount \
  --cluster ingress-lab \
  --namespace kube-system \
  --name aws-load-balancer-controller \
  --attach-policy-arn arn:aws:iam::<ACCOUNT_ID>:policy/AWSLoadBalancerControllerIAMPolicy \
  --approve
```

---

## **Step 5 — Install AWS Load Balancer Controller using Helm**

```bash
helm repo add eks https://aws.github.io/eks-charts
helm repo update
```

```bash
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=ingress-lab \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set region=us-east-1
```

Verify pods:

```bash
kubectl get pods -n kube-system | grep load
```

---

## **Step 6 — Create namespace for apps**

```bash
kubectl create namespace ingress-demo
```

---

## **Step 7 — Deploy Applications Using Docker Hub Images**

### **app1-deployment.yaml**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app1
  namespace: ingress-demo
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
      - name: app1
        image: bhuvanraj123/myapp1:v3
        ports:
        - containerPort: 80
```

### **app2-deployment.yaml**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app2
  namespace: ingress-demo
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
      - name: app2
        image: bhuvanraj123/myapp2:v3
        ports:
        - containerPort: 80
```

Apply deployments:

```bash
kubectl apply -f app1-deployment.yaml
kubectl apply -f app2-deployment.yaml
```

---

## **Step 8 — Create Services**

### **app1-service.yaml**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: app1-service
  namespace: ingress-demo
spec:
  selector:
    app: app1
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```

### **app2-service.yaml**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: app2-service
  namespace: ingress-demo
spec:
  selector:
    app: app2
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```

Apply services:

```bash
kubectl apply -f app1-service.yaml
kubectl apply -f app2-service.yaml
```

---

## **Step 9 — Create Ingress**

### **ingress.yaml**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: alb-ingress
  namespace: ingress-demo
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP":80}]'
spec:
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

Apply ingress:

```bash
kubectl apply -f ingress.yaml
```

---

## **Step 10 — Wait for ALB**

```bash
kubectl get ingress -n ingress-demo
```

* Wait until `ADDRESS` shows something like:

```
k8s-ingressd-albingre-xxxxxxxx.us-east-1.elb.amazonaws.com
```

---

## **Step 11 — Test Applications**

### Path-based routing:

```
http://<ALB-DNS>/app1
http://<ALB-DNS>/app2
```

✅ Both apps should load UI correctly with no 404 errors.

---

## **Step 12 — Verification Commands**

```bash
kubectl get pods -n ingress-demo
kubectl get svc -n ingress-demo
kubectl describe ingress alb-ingress -n ingress-demo
kubectl exec -it <app1-pod> -n ingress-demo -- curl http://localhost/app1
kubectl exec -it <app2-pod> -n ingress-demo -- curl http://localhost/app2
```

---

# ✅ Lab Complete

* Two apps deployed using **prebuilt Docker Hub images**
* Path-based routing using **ALB ingress**
* Custom NGINX images handle `/app1` and `/app2` paths
* Browser accessible via ALB DNS


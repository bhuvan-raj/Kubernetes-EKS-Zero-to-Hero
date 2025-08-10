# **EKS LoadBalancer Service**

This lab demonstrates how to deploy an application in Amazon EKS and expose it using different AWS load balancer types:

* **Classic Load Balancer (CLB)** — default without AWS Load Balancer Controller
* **Network Load Balancer (NLB)** — requires AWS Load Balancer Controller
* **Application Load Balancer (ALB)** — requires AWS Load Balancer Controller

---

## **Prerequisites**

* An **Amazon EKS cluster** with at least one EC2 worker node group (Fargate-only clusters will not work for this example).
* `kubectl` configured for your cluster:

  ```bash
  aws eks update-kubeconfig --region <your-region> --name <your-cluster-name>
  ```
* AWS CLI installed with sufficient IAM permissions.
* **IAM OIDC provider** associated with your EKS cluster:

  ```bash
  eksctl utils associate-iam-oidc-provider \
    --region <your-region> \
    --cluster <your-cluster-name> \
    --approve
  ```
* **AWS Load Balancer Controller** installed (needed for NLB and ALB).

---

## **1. Create the Namespace**

```bash
kubectl create namespace my-app
```

---

## **2. Create the Deployment**

**`nginx-deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  namespace: my-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
```

```bash
kubectl apply -f nginx-deployment.yaml
```

---

## **3. Classic Load Balancer (Default)**

Without annotations, a `LoadBalancer` Service in EKS creates a **Classic Load Balancer**.

**`nginx-service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-clb-service
  namespace: my-app
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```

```bash
kubectl apply -f nginx-service.yaml
```

---

## **4. AWS Load Balancer Controller Setup**

To create an **NLB** or **ALB**, you must install the AWS Load Balancer Controller:

1. **Create IAM policy**

   ```bash
   curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json

   aws iam create-policy \
     --policy-name AWSLoadBalancerControllerIAMPolicy \
     --policy-document file://iam_policy.json
   ```

2. **Create service account with IAM role**

   ```bash
   eksctl create iamserviceaccount \
     --cluster=<your-cluster-name> \
     --namespace=kube-system \
     --name=aws-load-balancer-controller \
     --role-name AmazonEKSLoadBalancerControllerRole \
     --attach-policy-arn=arn:aws:iam::<your-account-id>:policy/AWSLoadBalancerControllerIAMPolicy \
     --approve
   ```

3. **Install the controller with Helm**

   ```bash
   helm repo add eks https://aws.github.io/eks-charts
   helm repo update

   helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
     -n kube-system \
     --set clusterName=<your-cluster-name> \
     --set serviceAccount.create=false \
     --set serviceAccount.name=aws-load-balancer-controller
   ```

---

## **5. Network Load Balancer (NLB)**

Once the AWS Load Balancer Controller is installed, create your NLB Service:

**`nginx-nlb-service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-nlb-service
  namespace: my-app
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "external"
    service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: "instance"
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```

```bash
kubectl apply -f nginx-nlb-service.yaml
```

---

## **6. Application Load Balancer (ALB)**

For ALB, you need an Ingress:

**`nginx-alb-ingress.yaml`**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-alb-ingress
  namespace: my-app
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
spec:
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: nginx-clb-service
                port:
                  number: 80
```

```bash
kubectl apply -f nginx-alb-ingress.yaml
```

---

## **7. Clean Up**

```bash
kubectl delete namespace my-app
```

---

## **Key Learning Points**

* **CLB** = Default `LoadBalancer` type without AWS Load Balancer Controller.
* **NLB** & **ALB** = Require AWS Load Balancer Controller.
* Public subnets must be tagged with `kubernetes.io/role/elb=1`, private subnets with `kubernetes.io/role/internal-elb=1`.
* Always clean up AWS resources to avoid charges.

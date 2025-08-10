
# **EKS LoadBalancer Service**

This lab demonstrates how to deploy an application in an Amazon EKS cluster and expose it to the outside world using a **LoadBalancer Service**.
We’ll also cover how to switch between **Classic Load Balancer (default)**, **Network Load Balancer (NLB)**, and **Application Load Balancer (ALB)**.

---

## **Prerequisites**

* Amazon EKS cluster up and running
* At least one **EC2 worker node group** attached to the cluster (Fargate-only clusters will not work for this basic LoadBalancer example)
* `kubectl` configured to point to your EKS cluster:

  ```bash
  aws eks update-kubeconfig --region <your-region> --name <your-cluster-name>
  ```
* AWS CLI installed and configured with sufficient IAM permissions

---

## **1. Create the Namespace**

We will use a dedicated namespace `my-app` for this lab.

```bash
kubectl create namespace my-app
```

---

## **2. Create the Deployment**

We will deploy a simple **Nginx** web server with 2 replicas.

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

Apply the deployment:

```bash
kubectl apply -f nginx-deployment.yaml
```

---

## **3. Verify the Deployment**

Check the status of the pods:

```bash
kubectl get pods -n my-app
```

Expected:

```
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-xxxxxxx-xxxxx      1/1     Running   0          20s
nginx-deployment-xxxxxxx-xxxxx      1/1     Running   0          20s
```

---

## **4. Create the LoadBalancer Service (Default CLB)**

**`nginx-service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-lb-service
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

Apply the service:

```bash
kubectl apply -f nginx-service.yaml
```

---

## **5. Verify the LoadBalancer**

Check the service:

```bash
kubectl get svc -n my-app
```

Expected:

```
NAME               TYPE           CLUSTER-IP      EXTERNAL-IP                           PORT(S)        AGE
nginx-lb-service   LoadBalancer   10.100.22.177   a1b2c3d4e5f6.elb.amazonaws.com         80:32598/TCP   1m
```

* **EXTERNAL-IP** is the DNS name of the AWS Elastic Load Balancer.
* May take 1–2 minutes to become active.

---

## **6. Test the Application**

Get the EXTERNAL-IP:

```bash
kubectl get svc nginx-lb-service -n my-app -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

Test in browser or via curl:

```bash
curl http://<EXTERNAL-IP>
```

You should see **Welcome to nginx!**.

---

## **7. View the Load Balancer in AWS Console**

1. Go to **EC2 → Load Balancers** in AWS Console.
2. Look for one starting with `k8s-myapp-nginxlb...`.
3. Check listeners, target groups, and registered nodes.

---

## **8. Using a Network Load Balancer (NLB)**

By default, `LoadBalancer` in EKS provisions a **Classic Load Balancer**.
To create an **NLB**, add an annotation:

**`nginx-nlb-service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-nlb-service
  namespace: my-app
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```

Apply:

```bash
kubectl apply -f nginx-nlb-service.yaml
```

---

## **9. Using an Application Load Balancer (ALB)**

An ALB is **not** created directly from a `Service`.
Instead, you need the **AWS Load Balancer Controller** and an **Ingress** resource.

**High-level steps:**

1. **Install AWS Load Balancer Controller** in your EKS cluster.
2. Create an **Ingress** with `alb` annotations.

Example Ingress:

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
                name: nginx-lb-service
                port:
                  number: 80
```

The AWS Load Balancer Controller will then provision an ALB and configure rules to route traffic to your service.

---

## **10. Clean Up**

```bash
kubectl delete namespace my-app
```

---

## **Key Learning Points**

* **CLB** = default for `LoadBalancer` in EKS.
* **NLB** = use annotation `service.beta.kubernetes.io/aws-load-balancer-type: "nlb"`.
* **ALB** = requires AWS Load Balancer Controller + Ingress.
* Always clean up to avoid AWS charges.


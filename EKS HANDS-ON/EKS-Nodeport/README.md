
# EKS NodePort Service

This lab demonstrates how to deploy an application in an Amazon EKS cluster and expose it using a **NodePort Service**.


## **Prerequisites**

- Amazon EKS cluster with **EC2 worker nodes** (NodePort cannot be accessed directly on Fargate-only clusters)
- `kubectl` configured for your cluster:
  ```bash
  aws eks update-kubeconfig --region <your-region> --name <your-cluster-name>

* AWS CLI installed and configured
* Ports `30000–32767` allowed in your **EC2 security group** for inbound access (needed to reach the NodePort service from the internet)

## **1. Create the Namespace**

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

```bash
kubectl get pods -n my-app
```

Expected output:

```
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-xxxxxxx-xxxxx      1/1     Running   0          20s
nginx-deployment-xxxxxxx-xxxxx      1/1     Running   0          20s
```

---

## **4. Create the NodePort Service**

**`nginx-nodeport.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-nodeport-service
  namespace: my-app
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
      nodePort: 30080
```

Apply the service:

```bash
kubectl apply -f nginx-nodeport.yaml
```

---

## **5. Verify the Service**

```bash
kubectl get svc -n my-app
```

Expected output:

```
NAME                      TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
nginx-nodeport-service    NodePort   10.100.22.200    <none>        80:30080/TCP   1m
```

---

## **6. Access the Application**

1. Get the public IP address of any EC2 worker node:

   ```bash
   kubectl get nodes -o wide
   ```

   or using AWS CLI:

   ```bash
   aws ec2 describe-instances \
     --filters "Name=tag:eks:cluster-name,Values=<your-cluster-name>" "Name=instance-state-name,Values=running" \
     --query "Reservations[].Instances[].PublicIpAddress" \
     --output text
   ```

2. Open the app in your browser:

   ```
   http://<NODE_PUBLIC_IP>:30080
   ```

You should see the **Welcome to nginx!** page.

---

## **7. Cleanup Resources**

```bash
kubectl delete namespace my-app
```

---

## **Key Learning Points**

* `NodePort` exposes a service on each node’s IP at a static port between **30000–32767**.
* The service is reachable from outside the cluster only if:

  * The worker nodes have public IPs (or accessible via a bastion host/VPN)
  * The node security group allows inbound traffic to the chosen `nodePort`
* Commonly used for **internal testing** or **accessing services without a load balancer**.

---

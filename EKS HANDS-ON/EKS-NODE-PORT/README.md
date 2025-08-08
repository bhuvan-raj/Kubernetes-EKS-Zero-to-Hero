
# On-Hand Lab: NodePort Service on Amazon EKS

## 1\. Introduction to NodePort Service

In Kubernetes, a **Service** is an abstract way to expose an application running on a set of Pods as a network service. It defines a logical set of Pods and a policy by which to access them.

A **NodePort** service is one of the simplest ways to get external traffic directly to your service. When you define a service of `type: NodePort`, Kubernetes allocates a port from a pre-configured range (default: 30000-32767) on **every Node** in the cluster. Any traffic sent to this port on any Node is then forwarded to the corresponding Pods of the service.

**Key Characteristics of NodePort:**

  * **Node-level Exposure:** The service is exposed on a specific port on **each worker node**.
  * **Direct Access:** Clients can directly access the service using `<NodeIP>:<NodePort>`.
  * **Port Range:** The assigned NodePort is typically in the range of 30000-32767.
  * **Simplicity:** Easiest to set up for basic external access.
  * **Limitations:**
      * Requires knowing the Node's IP address, which can change.
      * Ports are in a high, non-standard range, making them less user-friendly for direct consumption.
      * Not suitable for production environments requiring high availability, load balancing, or custom domain names. For production, **LoadBalancer** or **Ingress** services are generally preferred.

This lab will guide you through setting up a basic NodePort service to understand its mechanics on an EKS cluster.

-----

## 2\. Prerequisites

Before starting this lab, ensure you have the following installed and configured on your local machine:

  * **AWS Account:** An active AWS account with administrative access.
  * **AWS CLI:** Installed and configured with your AWS credentials and a default region.
      * Verify: `aws configure`
  * **eksctl:** The official CLI for Amazon EKS.
      * Verify: `eksctl version`
  * **kubectl:** The Kubernetes command-line tool.
      * Verify: `kubectl version --client`

-----

## 3\. Lab Setup: Deploying an EKS Cluster

We'll use `eksctl` to quickly set up a minimal EKS cluster for this lab.

### 3.1. Install AWS CLI & eksctl

If you don't have them installed, follow these steps:

**Install AWS CLI:**

For Linux/macOS:

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

For Windows: Download from the [official AWS CLI documentation](https://docs.aws.amazon.com/cli/latest/userguide/install-windows.html).

Configure AWS CLI:

```bash
aws configure
# Enter your AWS Access Key ID, AWS Secret Access Key, default region (e.g., us-east-1), and default output format (e.g., json).
```

**Install eksctl:**

For Linux/macOS (AMD64/x86\_64):

```bash
curl --silent --location "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
```

For Linux/macOS (ARM64):

```bash
curl --silent --location "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$(uname -s)_arm64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
```

For Windows:

1.  Download the appropriate `.zip` file (e.g., `eksctl_Windows_amd64.zip`) from the [eksctl GitHub releases page](https://www.google.com/search?q=https://github.com/eksctl-io/eksctl/releases/latest).
2.  Unzip and move `eksctl.exe` to a directory in your system's `PATH`.

### 3.2. Create an EKS Cluster with eksctl

Create a file named `eks-nodeport-cluster.yaml`:

```yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: nodeport-lab-cluster
  region: us-east-1 # Choose your desired AWS region
  version: "1.29" # Specify a supported Kubernetes version

managedNodeGroups:
  - name: nodeport-workers
    instanceType: t3.medium # Or t2.medium for lower cost
    desiredCapacity: 2 # Two worker nodes
    minSize: 1
    maxSize: 3
    # Optional: Enable SSH access to worker nodes for debugging (requires an SSH public key)
    # ssh:
    #   allow: true
    #   publicKeyPath: ~/.ssh/id_rsa.pub # Path to your public SSH key
```

Now, deploy the EKS cluster using this configuration:

```bash
eksctl create cluster -f eks-nodeport-cluster.yaml
```

This command will take approximately **15-25 minutes** to complete. `eksctl` will provision the EKS control plane, worker nodes, VPC, subnets, security groups, and IAM roles.

### 3.3. Verify Cluster Connectivity

Once the cluster creation is complete, `eksctl` automatically updates your `~/.kube/config` file.

Verify that `kubectl` can connect to your new cluster and that nodes are in `Ready` state:

```bash
kubectl get nodes
```

You should see output similar to this, indicating two ready worker nodes:

```
NAME                                           STATUS   ROLES    AGE   VERSION
ip-192-168-XX-XXX.ec2.internal   Ready    <none>   5m    v1.29.0
ip-192-168-XX-XXX.ec2.internal   Ready    <none>   5m    v1.29.0
```

-----

## 4\. Deploying a NodePort Service

Now, let's deploy a simple Nginx application and expose it using a NodePort service.

### 4.1. Understanding NodePort

A **NodePort** service works by opening a specific port on all nodes in your cluster. When traffic hits that port on any node, it's forwarded to a Pod selected by the service. This is useful for development or when you need direct access to a service without setting up a load balancer.

### 4.2. Create a Sample Application Deployment

We'll deploy a simple Nginx web server. Create a file named `nginx-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 2 # Deploy two Nginx Pods
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
        image: nginx:latest # Use the latest Nginx image
        ports:
        - containerPort: 80 # Nginx listens on port 80
```

Apply the deployment:

```bash
kubectl apply -f nginx-deployment.yaml
```

Verify that the Pods are running:

```bash
kubectl get pods -l app=nginx
```

You should see output similar to:

```
NAME                               READY   STATUS    RESTARTS   AGE
nginx-deployment-abcdefghi-jklmn   1/1     Running   0          30s
nginx-deployment-opqrstu-vwxyz01   1/1     Running   0          30s
```

### 4.3. Expose the Application as a NodePort Service

Now, create a service of type `NodePort` to expose the Nginx deployment. Create a file named `nginx-nodeport-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-nodeport-service
spec:
  type: NodePort # This is the crucial part for NodePort
  selector:
    app: nginx # Selects Pods with label app: nginx
  ports:
    - protocol: TCP
      port: 80 # The port on the service
      targetPort: 80 # The port on the Pod (Nginx's port)
      # nodePort: 30080 # Optional: You can specify a desired port within the 30000-32767 range.
                       # If omitted, Kubernetes will auto-assign one.
```

Apply the service:

```bash
kubectl apply -f nginx-nodeport-service.yaml
```

### 4.4. Verify the NodePort Service

Check the service details to find the assigned NodePort:

```bash
kubectl get service nginx-nodeport-service
```

You should see output similar to this:

```
NAME                     TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
nginx-nodeport-service   NodePort    10.100.XXX.XXX   <none>        80:3XXXX/TCP   10s
```

Note the `PORT(S)` column: `80:3XXXX/TCP`. Here, `3XXXX` is the dynamically assigned **NodePort**. Make a note of this port.

Now, get the IP addresses of your worker nodes:

```bash
kubectl get nodes -o wide
```

Look for the `EXTERNAL-IP` column. If no external IP is listed (e.g., in a private subnet), you might need to use the `INTERNAL-IP` and ensure you have SSH access or a jump box configured to reach the nodes. For this lab, assume the nodes have public IPs or are reachable.

Let's assume one of your Node IPs is `X.X.X.X` and the NodePort is `30080`.

### 4.5. Access the Application

You can now access your Nginx application from your local machine using any of your worker node's IP addresses and the assigned NodePort.

Open your web browser and navigate to:

`http://<NODE_IP>:<NODE_PORT>`

**Example:** If your node IP is `54.234.123.45` and your NodePort is `30080`, you would go to:

`http://54.234.123.45:30080`

You should see the default Nginx welcome page, confirming that your NodePort service is working correctly\!

Alternatively, you can use `curl` from your terminal:

```bash
curl http://<NODE_IP>:<NODE_PORT>
```

-----

## 5\. Cleanup

It's crucial to clean up all resources to avoid incurring unnecessary AWS costs.

### 5.1. Delete Kubernetes Resources

First, delete the Kubernetes Deployment and Service:

```bash
kubectl delete -f nginx-nodeport-service.yaml
kubectl delete -f nginx-deployment.yaml
```

Verify they are gone:

```bash
kubectl get all
```

You should not see `nginx-deployment` or `nginx-nodeport-service` listed.

### 5.2. Delete the EKS Cluster

Finally, delete the EKS cluster created by `eksctl`. This will remove all associated AWS resources (EKS control plane, EC2 instances, VPC, IAM roles, etc.).

```bash
eksctl delete cluster --name nodeport-lab-cluster --region us-east-1 # Use the region you specified
```

This process will also take several minutes to complete. Wait until you see a confirmation message that the cluster has been deleted.

-----

## 6\. Troubleshooting Tips

  * **`kubectl` connection issues:** If `kubectl` can't connect, try `aws eks update-kubeconfig --name nodeport-lab-cluster --region us-east-1` to refresh your kubeconfig.
  * **Pods not running:** Check `kubectl get pods -o wide` for status. Use `kubectl describe pod <pod-name>` and `kubectl logs <pod-name>` for more details.
  * **Service not accessible:**
      * Ensure the `NodePort` is correct (`kubectl get svc`).
      * Verify the **security group** attached to your EKS worker nodes allows inbound traffic on the NodePort. `eksctl` usually configures this, but manual intervention might be needed if you used a custom VPC or security groups. The Node security group must permit ingress on the NodePort.
      * Check if the **Network ACLs** (NACLs) of your VPC subnets allow the traffic.
      * Confirm that your Node has a **public IP** if accessing from outside the VPC. If not, you might need a bastion host or VPC peering to access private IPs.
  * **Nginx Welcome Page not showing:** Ensure the Nginx container is healthy and serving on port 80 inside the Pod.
  * **Permissions:** Ensure your AWS CLI credentials have sufficient permissions to create and manage EKS clusters and related resources.

-----

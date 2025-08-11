

# Deploying `glasmorphism-todo` on EKS with a Network Load Balancer (NLB) 🚀

This `README.md` provides a comprehensive guide to deploying your `glasmorphism-todo` application on an Amazon EKS cluster and exposing it using an AWS Network Load Balancer (NLB). We'll leverage the **AWS Load Balancer Controller** for seamless integration and advanced features.

-----

## Table of Contents

1.  [Prerequisites](https://www.google.com/search?q=%231-prerequisites-%E2%9A%99%EF%B8%8F)
2.  [Deploy the AWS Load Balancer Controller](https://www.google.com/search?q=%232-deploy-the-aws-load-balancer-controller-%F0%9F%8F%97%EF%B8%8F)
3.  [Deploy Your Application](https://www.google.com/search?q=%233-deploy-your-application-%F0%9F%9A%80)
4.  [Create Kubernetes Service for NLB](https://www.google.com/search?q=%234-create-kubernetes-service-for-nlb-%F0%9F%8C%90)
5.  [Verify the NLB and Access Your Application](https://www.google.com/search?q=%235-verify-the-nlb-and-access-your-application-%E2%9C%85)

-----

## 1\. Prerequisites ⚙️

Before you begin, ensure you have the following tools and configurations:

  * **Amazon EKS Cluster**: An active EKS cluster.

  * **`kubectl`**: Configured to communicate with your EKS cluster.

  * **`helm`**: Installed on your local machine (version 3+ recommended).

  * **`aws cli`**: Configured and authenticated with your AWS account.

  * **`eksctl`**: (Optional but recommended) A command-line tool for EKS.

  * **IAM OIDC Provider for EKS**: Your EKS cluster must have an IAM OIDC provider associated with it. If not, create one using `eksctl`:

    ```bash
    eksctl utils associate-iam-oidc-provider --cluster=<your-cluster-name> --approve
    ```

    Replace `<your-cluster-name>` with the actual name of your EKS cluster.

-----

## 2\. Deploy the AWS Load Balancer Controller 🏗️

The AWS Load Balancer Controller is essential for provisioning and managing AWS Load Balancers (ALBs and NLBs) in EKS. It integrates Kubernetes Services and Ingress resources with AWS's load balancing capabilities.

### a. Download IAM Policy

The controller needs specific **IAM permissions** to interact with AWS Load Balancer APIs. Download the predefined IAM policy from the official GitHub repository:

```bash
curl -O https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json
```

### b. Create IAM Policy in AWS

Now, create an **IAM policy** in your AWS account using the downloaded JSON file:

```bash
aws iam create-policy \
    --policy-name AWSLoadBalancerControllerIAMPolicy \
    --policy-document file://iam_policy.json
```

**Note**: Make sure to copy the **ARN** (Amazon Resource Name) of the created policy; you'll need it in the next step. It will look something like `arn:aws:iam::<your-aws-account-id>:policy/AWSLoadBalancerControllerIAMPolicy`.

### c. Create IAM Service Account for the Controller

Associate the IAM policy with a **Kubernetes Service Account** that the Load Balancer Controller pods will use. This allows the pods to assume the necessary AWS permissions securely via **IAM Roles for Service Accounts (IRSA)**.

Replace `<your-cluster-name>` and `<your-aws-account-id>` with your actual values.

```bash
eksctl create iamserviceaccount \
    --cluster=<your-cluster-name> \
    --namespace=kube-system \
    --name=aws-load-balancer-controller \
    --attach-policy-arn=arn:aws:iam::<your-aws-account-id>:policy/AWSLoadBalancerControllerIAMPolicy \
    --override-existing-serviceaccounts \
    --approve
```

### d. Install the AWS Load Balancer Controller with Helm

Add the EKS Helm chart repository and then install the controller using Helm. Replace `<your-cluster-name>` with your actual cluster name.

```bash
helm repo add eks https://aws.github.io/eks-charts
helm repo update

helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
    -n kube-system \
    --set clusterName=<your-cluster-name> \
    --set serviceAccount.create=false \
    --set serviceAccount.name=aws-load-balancer-controller
```

This Helm command also installs the necessary Custom Resource Definitions (CRDs).

### e. Verify Controller Deployment

Check if the controller pods are running successfully:

```bash
kubectl get deployment -n kube-system aws-load-balancer-controller
kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller
```

You should see the controller deployment and its pods in a `Running` state.

-----

## 3\. Deploy Your Application 🚀

Now, let's deploy your `glasmorphism-todo` application to your EKS cluster.

### a. Create `deployment.yml`

Create a file named `deployment.yml` with the following content:

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

### b. Apply the Deployment

Apply this deployment manifest to your EKS cluster:

```bash
kubectl apply -f deployment.yml
```

### c. Verify Deployment and Pods

Ensure your pods are running as expected:

```bash
kubectl get deployment glasmorphism-todo
kubectl get pods -l app=glasmorphism-todo
```

You should see two pods in a `Running` state, corresponding to the `replicas: 2` defined in your deployment.

-----

## 4\. Create Kubernetes Service for NLB 🌐

Finally, you'll create a Kubernetes Service of type `LoadBalancer`. This service will leverage the AWS Load Balancer Controller to provision and configure an NLB for your `glasmorphism-todo` application.

### a. Create `service.yaml`

Create a file named `service.yaml` with the following content. The `annotations` are critical here, as they instruct the AWS Load Balancer Controller on how to create the NLB.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: glasmorphism-todo-nlb-service
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "external" # Specifies that we want an AWS Load Balancer
    service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: "ip" # CRITICAL: Configures the NLB to target pod IPs directly
    service.beta.kubernetes.io/aws-load-balancer-scheme: "internet-facing" # "internet-facing" for public access, "internal" for private
    # Optional: To enable Proxy Protocol v2 for source IP preservation
    # service.beta.kubernetes.io/aws-load-balancer-target-group-attributes: preserve_client_ip.enabled=true
spec:
  type: LoadBalancer
  selector:
    app: glasmorphism-todo # This MUST match the 'app' label in your deployment's pod template
  ports:
    - protocol: TCP
      port: 80 # The port the NLB will listen on (external port)
      targetPort: 80 # The port your application container is listening on (internal pod port)
```

#### Key Annotations Explained:

  * `service.beta.kubernetes.io/aws-load-balancer-type: "external"`: This annotation tells the AWS Load Balancer Controller that you want an AWS-managed load balancer.
  * `service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: "ip"`: **This is the most crucial annotation for creating an NLB.** It configures the NLB to directly target the **IP addresses of your Kubernetes pods**. This method offers better performance and latency compared to targeting instance IPs.
  * `service.kubernetes.io/aws-load-balancer-scheme: "internet-facing"`: Defines whether the NLB will be publicly accessible from the internet (`internet-facing`) or restricted to your VPC (`internal`). Choose based on your application's requirements.
  * `service.beta.kubernetes.io/aws-load-balancer-target-group-attributes: preserve_client_ip.enabled=true` (Optional): If your `glasmorphism-todo` application needs to know the actual client's IP address (rather than the NLB's IP), uncomment this line. This enables Proxy Protocol v2 on the NLB's target group. **Note**: Your application must be configured to parse and understand Proxy Protocol headers for this to work correctly.

### b. Apply the Service

Apply the service manifest to your EKS cluster:

```bash
kubectl apply -f service.yaml
```

-----

## 5\. Verify the NLB and Access Your Application ✅

After applying the service, the AWS Load Balancer Controller will provision the NLB. This process usually takes a few minutes.

### a. Get Service Details

Check the status of your Kubernetes Service. You'll observe that the `EXTERNAL-IP` column initially shows `pending` and then populates with the NLB's DNS name once it's ready.

```bash
kubectl get svc glasmorphism-todo-nlb-service
```

Once the NLB is provisioned, the `EXTERNAL-IP` column will display a DNS name (e.g., `k8s-yourname-yoursvc-xxxxxxxxxx.elb.your-region.amazonaws.com`). This is your NLB's endpoint.

### b. Verify in AWS Console

You can also confirm the creation and status of your NLB directly in the AWS Management Console:

1.  Log in to your AWS Management Console.
2.  Navigate to **EC2** -\> **Load Balancers** (under "Load Balancing" in the left navigation pane).
3.  You should see a new **Network Load Balancer** created. Its name will typically follow a pattern like `k8s-<your-cluster-name>-<your-service-name>-<random-id>`.
4.  Click on the NLB, then navigate to the **Target Groups** tab.
5.  You should see a target group associated with your service, and your EKS pods (identified by their IP addresses if you used `ip` target type) should be registered and healthy.

### c. Access Your Application

Use the `EXTERNAL-IP` (the DNS name) obtained from `kubectl get svc` in your web browser or with `curl` to access your `glasmorphism-todo` application:

```bash
curl http://<your-nlb-dns-name>
```

You should receive a successful response from your `glasmorphism-todo` application\!

-----

Congratulations\! You have successfully deployed your application and exposed it via an AWS Network Load Balancer in your EKS cluster.

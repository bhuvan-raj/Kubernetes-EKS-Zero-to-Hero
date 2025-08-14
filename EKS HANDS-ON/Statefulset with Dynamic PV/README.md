# StatefulSet Lab: Persistent Applications on Amazon EKS with EBS Dynamic Provisioning 💾

This lab demonstrates how to deploy and manage stateful applications using Kubernetes **StatefulSets** on an **Amazon EKS** cluster, leveraging **Amazon EBS** for dynamic Persistent Volume (PV) provisioning.

---

## Overview

StatefulSets are essential for applications that require **stable, unique network identifiers**, **stable persistent storage**, and **ordered, graceful deployment and scaling**. In a cloud environment like AWS, integrating StatefulSets with **dynamic Persistent Volume provisioning** using **EBS volumes** via the **EBS CSI driver** provides a robust solution for persistent workloads. This lab will walk you through the entire process.

---

## Prerequisites 🛠️

Before you begin, ensure you have the following:

* **AWS Account and Credentials:** Configured with sufficient permissions for EKS, IAM, and EC2 (EBS).
* **`eksctl` CLI:** Installed and configured to manage your EKS clusters.
* **`kubectl` CLI:** Installed and configured to connect to your EKS cluster.
* **AWS CLI:** Installed and configured for your AWS account.
* **Existing Amazon EKS Cluster:** This lab assumes you have an EKS cluster running. If not, create one:
    ```bash
    eksctl create cluster --name my-statefulset-cluster --region us-east-1 --version 1.28 --node-type t3.medium --nodes 2
    ```
    *(Adjust cluster name, region, Kubernetes version, node type, and node count as needed.)*

---

## Lab Steps 🧪

### 1. Install the Amazon EBS CSI Driver

The Amazon EBS CSI driver enables your EKS cluster to dynamically provision EBS volumes. This step ensures the necessary IAM role and the CSI driver components are correctly deployed and configured.

1.  **Associate IAM OIDC Provider with your EKS cluster:**
    This command registers your EKS cluster's OpenID Connect (OIDC) issuer with IAM, allowing Kubernetes service accounts to assume IAM roles.
    ```bash
    eksctl utils associate-iam-oidc-provider --cluster your-cluster-name --approve
    ```
    *(Replace `your-cluster-name` with your EKS cluster's name.)*

2.  **Manually Create the IAM Role for the EBS CSI Driver:**
    The `AmazonEKS_EBS_CSI_DriverRole` is essential for the CSI driver to make AWS API calls (e.g., to create EBS volumes). In some cases, `eksctl` might not create this role automatically, or its trust policy might be incorrect. We will create it explicitly here.

    a.  **Get your Cluster's OIDC Issuer Details:**
        You need your AWS Account ID, your cluster's region, and the unique OIDC ID from your cluster's issuer URL.
   ```bash
        # Replace 'your-cluster-name' with your actual EKS cluster name
        EKS_CLUSTER_NAME="your-cluster-name"

        # Get OIDC Issuer URL for your cluster
        OIDC_ISSUER_URL=$(aws eks describe-cluster --name "$EKS_CLUSTER_NAME" --query "cluster.identity.oidc.issuer" --output text)
        echo "OIDC Issuer URL: $OIDC_ISSUER_URL"

        # Extract OIDC ID (the last segment of the URL)
        OIDC_ID=$(basename "$OIDC_ISSUER_URL")
        echo "OIDC ID: $OIDC_ID"

        # Get your AWS Account ID
        AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
        echo "AWS Account ID: $AWS_ACCOUNT_ID"

        # Your AWS Region (e.g., us-east-1) - CONFIRM THIS IS YOUR CLUSTER'S REGION
        AWS_REGION="us-east-1"
        echo "AWS Region: $AWS_REGION"
```

 b.  **Create the IAM Trust Policy Document (`ebs-csi-trust-policy.json`):**
This JSON policy defines who (your EKS cluster's OIDC provider and the `ebs-csi-controller-sa` service account) is allowed to **assume** this IAM role. **Ensure you replace the placeholders** with the actual values obtained in the previous step.

        ```json
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Principal": {
                "Federated": "arn:aws:iam::YOUR_AWS_ACCOUNT_ID:oidc-provider/oidc.eks.YOUR_AWS_[REGION.amazonaws.com/id/YOUR_OIDC_ID](https://REGION.amazonaws.com/id/YOUR_OIDC_ID)"
              },
              "Action": "sts:AssumeRoleWithWebIdentity",
              "Condition": {
                "StringEquals": {
                  "oidc.eks.YOUR_AWS_[REGION.amazonaws.com/id/YOUR_OIDC_ID:aud](https://REGION.amazonaws.com/id/YOUR_OIDC_ID:aud)": "sts.amazonaws.com",
                  "oidc.eks.YOUR_AWS_[REGION.amazonaws.com/id/YOUR_OIDC_ID:sub](https://REGION.amazonaws.com/id/YOUR_OIDC_ID:sub)": "system:serviceaccount:kube-system:ebs-csi-controller-sa"
                }
              }
            }
          ]
        }
        ```
        
 Save this content to a file named `ebs-csi-trust-policy.json`.

 c.  **Create or Update the IAM Role:**
 
If the role `AmazonEKS_EBS_CSI_DriverRole` doesn't exist, create it. If it exists, you'll need to update its trust policy using the AWS Console (as described in troubleshooting if `aws iam create-role` fails due to existence).
```bash
        aws iam create-role --role-name AmazonEKS_EBS_CSI_DriverRole --assume-role-policy-document file://ebs-csi-trust-policy.json
```
This command will output the ARN of the role.

 d.  **Attach the Required Managed Policy:**
 This step attaches the `AmazonEBSCSIDriverPolicy` (an **AWS-managed policy**) to your new role. This policy grants the necessary permissions for the CSI driver to interact with EBS (e.g., `ec2:CreateVolume`, `ec2:AttachVolume`).
```
        aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy --role-name AmazonEKS_EBS_CSI_DriverRole
```

3.  **Install/Update the EBS CSI Driver EKS Add-on:**
    This step ensures the EKS add-on for the EBS CSI driver is deployed or reconciled with the correct IAM role. We'll use `aws eks update-addon` with `resolve-conflicts OVERWRITE` to ensure the add-on's desired state is enforced, especially if it was previously in a `DEGRADED` state.
    ```bash
    # Replace 'your-cluster-name' with your actual EKS cluster name
    # Replace 'v1.47.0-eksbuild.1' with the exact version shown by `eksctl get addon --name aws-ebs-csi-driver --cluster your-cluster-name`
    aws eks update-addon --cluster-name your-cluster-name --addon-name aws-ebs-csi-driver --addon-version v1.47.0-eksbuild.1 --service-account-role-arn arn:aws:iam::YOUR_AWS_ACCOUNT_ID:role/AmazonEKS_EBS_CSI_DriverRole --resolve-conflicts OVERWRITE
    ```
    *(Remember to replace `YOUR_AWS_ACCOUNT_ID` and `your-cluster-name`.)*

4.  **Verify the driver components are running:**
    After the `aws eks update-addon` command completes, it may take a few minutes for Kubernetes to deploy the CSI controller and node pods. Monitor their status:
    ```bash
    kubectl get deploy -n kube-system  -l app.kubernetes.io/name=aws-ebs-csi-driver
    # Or, if that doesn't show:
    kubectl get deploy -n kube-system
    # And check pods:
    kubectl get pods -n kube-system  -l app.kubernetes.io/name=aws-ebs-csi-driver
    ```
    You should see the `ebs-csi-controller` deployment and its pods (e.g., `ebs-csi-controller-xxxx`, `ebs-csi-node-xxxx`) in `Running` status.

---

### 2. Create a StorageClass for EBS (GP3)

Define a Kubernetes `StorageClass` that uses the EBS CSI driver to provision `gp3` type EBS volumes. GP3 offers a balance of price and performance. 

Create `ebs-storageclass.yaml`:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-gp3-sc
  annotations:
    storageclass.kubernetes.io/is-default-class: "true" # Optional: sets this as the default storage class
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  fsType: ext4 # Or xfs
  encrypted: "true" # Optional: encrypt EBS volumes
reclaimPolicy: Delete # EBS volume is deleted when PVC is deleted
volumeBindingMode: WaitForFirstConsumer # Ensures volume is provisioned in the same AZ as the Pod
````

Apply the StorageClass:

```bash
kubectl apply -f ebs-storageclass.yaml
```

Verify it:

```bash
kubectl get sc
```

-----

### 3\. Create a Headless Service

A Headless Service provides stable network identities (DNS entries) for the Pods within our StatefulSet.

Create `nginx-headless-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-headless
  labels:
    app: nginx-stateful
spec:
  ports:
  - port: 80
    name: web
  clusterIP: None # This makes it a Headless Service
  selector:
    app: nginx-stateful
```

Apply the service:

```bash
kubectl apply -f nginx-headless-service.yaml
```

-----

### 4\. Create a StatefulSet with Dynamic PV Provisioning

Now, define the StatefulSet. The `volumeClaimTemplates` section is crucial here, as it tells Kubernetes to dynamically provision a new PersistentVolumeClaim (PVC) and subsequently an EBS volume for each Pod replica, using our `ebs-gp3-sc` StorageClass.

Create `nginx-statefulset.yaml`:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web-nginx
spec:
  serviceName: "nginx-headless" # Must match the headless service name
  replicas: 3
  selector:
    matchLabels:
      app: nginx-stateful
  template:
    metadata:
      labels:
        app: nginx-stateful
    spec:
      containers:
      - name: nginx
        image: registry.k8s.io/nginx-slim:0.8
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "ebs-gp3-sc" # Reference your EBS StorageClass
      resources:
        requests:
          storage: 1Gi # Request a 1GiB EBS volume for each Pod
```

Apply the StatefulSet:

```bash
kubectl apply -f nginx-statefulset.yaml
```

-----

### 5\. Verify Deployment and Dynamic Provisioning

Observe the ordered creation of Pods and the dynamic provisioning of PVCs and EBS volumes.

1.  **Watch Pods come up:**

    ```bash
    kubectl get pods -l app=nginx-stateful -w
    ```

    You'll see pods named `web-nginx-0`, `web-nginx-1`, `web-nginx-2` come up sequentially.

2.  **Check PVCs:**

    ```bash
    kubectl get pvc -l app=nginx-stateful
    ```

    You'll see PVCs like `www-web-nginx-0`, `www-web-nginx-1`, `www-web-nginx-2` in the `Bound` state.

3.  **Check PVs:**

    ```bash
    kubectl get pv
    ```

    You'll see PersistentVolumes dynamically created and bound to the PVCs.

4.  **Verify EBS Volumes in AWS Console/CLI:**
    Navigate to the **EC2 console** -\> **Volumes** in your AWS region. You should see three new 1GiB EBS volumes, each tagged with its associated PVC name.

-----

### 6\. Test Persistence

Demonstrate data persistence across Pod recreation.

1.  **Write data to `web-nginx-0`'s volume:**

    ```bash
    kubectl exec web-nginx-0 -- sh -c 'echo "This is data from web-nginx-0" > /usr/share/nginx/html/index.html'
    ```

2.  **Access data from `web-nginx-0`:**

    ```bash
    kubectl exec -it web-nginx-0 -- curl localhost:80
    ```

    You should see "This is data from web-nginx-0".

3.  **Delete and recreate `web-nginx-0` Pod:**

    ```bash
    kubectl delete pod web-nginx-0
    ```

    Wait for Kubernetes to reschedule and recreate the `web-nginx-0` Pod.

4.  **Access data from the *new* `web-nginx-0` Pod:**

    ```bash
    kubectl exec -it web-nginx-0 -- curl localhost:80
    ```

    The data should still be present, confirming persistence via the attached EBS volume.

-----

### 7\. Scaling a StatefulSet

Observe ordered scaling behavior.

1.  **Scale up to 5 replicas:**

    ```bash
    kubectl scale statefulset web-nginx --replicas=5
    ```

    New pods (`web-nginx-3`, `web-nginx-4`) and their respective EBS volumes will be created.

2.  **Scale down to 1 replica:**

    ```bash
    kubectl scale statefulset web-nginx --replicas=1
    ```

    Pods will terminate in reverse ordinal order (`web-nginx-4` first, then `web-nginx-3`, etc.).

-----

## Cleanup 🧹

To avoid incurring AWS costs, ensure you clean up all resources.

1.  **Delete the StatefulSet:** This will terminate the pods.

    ```bash
    kubectl delete statefulset web-nginx
    ```

2.  **Delete the PersistentVolumeClaims (PVCs):** Since `reclaimPolicy` was `Delete`, this will also delete the underlying EBS volumes.

    ```bash
    kubectl delete pvc -l app=nginx-stateful
    ```

    *(Verify in the AWS EC2 console that the EBS volumes are being deleted.)*

3.  **Delete the Headless Service:**

    ```bash
    kubectl delete service nginx-headless
    ```

4.  **Delete the StorageClass:**

    ```bash
    kubectl delete sc ebs-gp3-sc
    ```

5.  **Optional: Uninstall the EBS CSI Driver (if no longer needed for other workloads):**
    This will also delete the `ebs-csi-controller-sa` service account, but not the IAM role itself.

    ```bash
    eksctl delete addon --name aws-ebs-csi-driver --cluster your-cluster-name
    ```

6.  **Optional: Delete the IAM Role `AmazonEKS_EBS_CSI_DriverRole`:**
    You'll need to detach the policy first, then delete the role.

    ```bash
    aws iam detach-role-policy --role-name AmazonEKS_EBS_CSI_DriverRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy
    aws iam delete-role --role-name AmazonEKS_EBS_CSI_DriverRole
    ```

7.  **Optional: Delete your EKS Cluster (if you created it just for this lab):**

    ```bash
    eksctl delete cluster --name my-statefulset-cluster --region us-east-1
    ```

-----

## Troubleshooting 🐛

  * **Pods stuck in `Pending`:**

      * Check `kubectl describe pod <pod-name>` for events. Look for `FailedScheduling` or `VolumeBinding` errors.
      * Ensure your EKS worker nodes have sufficient resources (CPU, Memory) and are in the same Availability Zone as where the EBS volume needs to be created (`WaitForFirstConsumer`).
      * Verify the `ebs-gp3-sc` StorageClass exists and is correctly configured.

  * **PVC stuck in `Pending`:**

      * Check `kubectl describe pvc <pvc-name>`. **This is crucial and usually provides the exact AWS API error.**
      * Ensure the `ebs.csi.aws.com` provisioner is correct in your `StorageClass`.
      * Verify the `aws-ebs-csi-driver` pods are running successfully in the `kube-system` namespace and check their logs for errors.
        ```bash
        kubectl logs -n kube-system -l app.kubernetes.io/component=controller -c csi-provisioner
        ```
      * **Common issue: `AccessDenied: Not authorized to perform sts:AssumeRoleWithWebIdentity`**: This explicitly indicates a problem with the **IAM role's Trust Relationship**. Ensure the `AmazonEKS_EBS_CSI_DriverRole`'s trust policy correctly references your cluster's OIDC issuer URL and the `ebs-csi-controller-sa` service account. Follow **Step 1.2** carefully to rectify this.
      * **Add-on in `DEGRADED` status (`deployments.apps "ebs-csi-controller" not found`):** If the `ebs-csi-controller` deployment is missing, the add-on is degraded. Use the `aws eks update-addon` command from **Step 1.3** to force reconciliation and recreation of the deployment.

  * **Data not persisting:**

      * Verify the `volumeMounts` in your StatefulSet template are correct and point to the `www` volume.
      * Check the `reclaimPolicy` of your StorageClass (`Delete` vs. `Retain`).

-----

```
```

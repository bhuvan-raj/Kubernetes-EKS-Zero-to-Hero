

# StatefulSet Lab: Persistent Applications on Amazon EKS with EBS Dynamic Provisioning 💾

This lab demonstrates how to deploy and manage stateful applications using Kubernetes **StatefulSets** on an **Amazon EKS** cluster, leveraging **Amazon EBS** for dynamic Persistent Volume (PV) provisioning.
-

## Overview

StatefulSets are essential for applications that require **stable, unique network identifiers**, **stable persistent storage**, and **ordered, graceful deployment and scaling**. In a cloud environment like AWS, integrating StatefulSets with **dynamic Persistent Volume provisioning** using **EBS volumes** via the **EBS CSI driver** provides a robust solution for persistent workloads. This lab will walk you through the entire process.

-----

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

-----

## Lab Steps 🧪

### 1\. Install the Amazon EBS CSI Driver

The Amazon EBS CSI driver enables your EKS cluster to dynamically provision EBS volumes.

1.  **Associate IAM OIDC Provider with your EKS cluster:**

    ```bash
    eksctl utils associate-iam-oidc-provider --cluster your-cluster-name --approve
    ```

    *(Replace `your-cluster-name` with your EKS cluster's name.)*

2.  **Install the EBS CSI Driver as an EKS Add-on:** This is the simplest method. `eksctl` will handle IAM role creation.

    ```bash
    eksctl create addon --name aws-ebs-csi-driver --cluster your-cluster-name --service-account-role-arn arn:aws:iam::YOUR_AWS_ACCOUNT_ID:role/AmazonEKS_EBS_CSI_DriverRole --force
    ```

    If the `AmazonEKS_EBS_CSI_DriverRole` doesn't exist, `eksctl` will likely prompt you or attempt to create it. Ensure your user has permissions to create IAM roles. If manual creation is preferred, ensure the role exists with `AmazonEBSCSIDriverPolicy` and the correct trust policy.

3.  **Verify the driver pods are running:**

    ```bash
    kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-ebs-csi-driver
    ```

### 2\. Create a StorageClass for EBS (GP3)

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
```

Apply the StorageClass:

```bash
kubectl apply -f ebs-storageclass.yaml
```

Verify it:

```bash
kubectl get sc
```

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

    ```bash
    eksctl delete addon --name aws-ebs-csi-driver --cluster your-cluster-name
    ```

6.  **Optional: Delete your EKS Cluster (if you created it just for this lab):**

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

      * Check `kubectl describe pvc <pvc-name>`.
      * Ensure the `ebs.csi.aws.com` provisioner is correct in your `StorageClass`.
      * Verify the `aws-ebs-csi-driver` pods are running successfully in the `kube-system` namespace and check their logs for errors.
      * Ensure the IAM role associated with the EBS CSI driver has the necessary permissions to create EBS volumes.

  * **Data not persisting:**

      * Verify the `volumeMounts` in your StatefulSet template are correct and point to the `www` volume.
      * Check the `reclaimPolicy` of your StorageClass (`Delete` vs. `Retain`).

-----

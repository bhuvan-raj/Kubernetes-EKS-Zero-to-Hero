# 🚀 Kubernetes Deployments: A Comprehensive Guide 📧
<img src="https://github.com/bhuvan-raj/Kubernetes-Openshift-Zero-to-Hero/blob/main/Deployment/assets/deploy.png" alt="Banner" />


## 1\. What is a Kubernetes Deployment? 📦

A **Kubernetes Deployment** is a high-level resource object that declaratively manages the lifecycle of your stateless applications. Instead of directly handling individual Pods, a Deployment automates and orchestrates common tasks, ensuring your application runs reliably and can be updated smoothly.

Key responsibilities of a Deployment include:

  * **Creating and maintaining Pods**: Ensures a specified number of identical Pods are always running.
  * **Rollbacks**: Allows you to revert to a previous, stable version of your application if an update introduces issues.
  * **Scaling**: Easily adjusts the number of application instances (Pods) up or down.
  * **Self-healing**: Automatically replaces failed Pods or Pods on unhealthy nodes to maintain the desired state.

Deployments achieve these capabilities by managing **ReplicaSets**, which in turn manage individual **Pods**.

-----

## 2\. Key Kubernetes Objects Involved 🧩

Understanding Deployments requires familiarity with these interconnected Kubernetes components:

### 2.1. Pods 🏃‍♂️

  * The **smallest deployable unit** in Kubernetes.
  * Encapsulates one or more containers (sharing network, storage, and lifecycle), storage resources, and a unique IP.
  * **Ephemeral**: Pods are designed to be short-lived. If they crash or are terminated, they don't self-heal; a higher-level controller is needed to replace them.

### 2.2. ReplicaSets 🛡️

  * A ReplicaSet's primary role is to **maintain a stable set of replica Pods running at any given time**.
  * It ensures the desired number of Pods are available, creating new ones if any fail and terminating excess ones.
  * **Managed by Deployments**: In most scenarios, you interact with Deployments, and they implicitly create and manage the necessary ReplicaSets for you.

### 2.3. Labels and Selectors 🏷️

  * **Labels**: Key/value pairs attached to Kubernetes objects (Pods, Deployments, Services). Used for identification and organization.
  * **Selectors**: Used by controllers (like Deployments and Services) to identify which Pods they should manage or route traffic to, based on their labels. A Deployment's `selector` must match the `labels` defined in its `template`'s `metadata`.

-----

### 3\. How Deployments Work 🛠️

When you create a Deployment, here's what happens:

  * **Creation of ReplicaSet:** The Deployment first creates a new ReplicaSet. This ReplicaSet is configured to manage the desired number of Pods for the application version specified in the Deployment.
  * **Pod Creation:** The newly created ReplicaSet then starts creating Pods based on the Pod template defined in the Deployment.
  * **Update Strategy:** If you update the Deployment (e.g., change the Docker image version), the Deployment controller implements the specified update strategy (e.g., RollingUpdate) to gradually replace the old Pods with new ones, ensuring minimal downtime.

**Managing Multiple ReplicaSets:** During an update, a Deployment will typically manage two (or more) ReplicaSets:

  * One for the old version of your application.
  * One for the new version of your application.

The Deployment gradually scales down the old ReplicaSet and scales up the new one.
**Rollback Capability:** Since Deployments keep track of previous ReplicaSets, they enable easy rollbacks to earlier versions of your application if an update introduces issues.

-----

### 4\. Functions of the Deployment Controller

  * **Reconciling Desired and Actual State:** This is the fundamental function of all Kubernetes controllers. The Deployment controller constantly observes the Deployment objects you create (the desired state) and compares them to the current state of the Pods and ReplicaSets running in the cluster (the actual state). If there's a discrepancy, it takes action to bring the actual state in line with the desired state.
  * **Creating and Managing ReplicaSets:** When you create a Deployment, the controller creates an underlying ReplicaSet based on the Pod template defined in the Deployment. When you update a Deployment, it creates new ReplicaSets for the new version and intelligently scales down the old ReplicaSets while scaling up the new ones (typically using a rolling update strategy).
  * **Orchestrating Rollouts:** The Deployment controller is responsible for executing the specified update strategy (e.g., RollingUpdate, Recreate). For a RollingUpdate, it carefully manages the creation of new Pods and the termination of old ones, ensuring that your application remains available throughout the update process by respecting `maxUnavailable` and `maxSurge` parameters.
  * **Enabling Rollbacks:** Because the Deployment controller preserves a history of previous ReplicaSets, it facilitates easy rollbacks to an earlier, stable version of your application if a new deployment introduces issues. It simply scales up the desired historical ReplicaSet and scales down the problematic one.
  * **Self-Healing:** In conjunction with the ReplicaSet controller, the Deployment controller contributes to the self-healing capabilities of Kubernetes. If Pods managed by a Deployment crash, become unhealthy (as detected by probes), or are evicted from a node, the Deployment controller ensures that the underlying ReplicaSet creates new Pods to maintain the desired replica count.
  * **Scaling:** When you change the `replicas` field in a Deployment, the controller detects this change and adjusts the number of Pods managed by its current ReplicaSet accordingly, either scaling up or scaling down your application instances.

-----

## 5\. Deployment Revisions: Tracking Changes for Rollbacks 🔄

One of the most powerful features of Deployments is their ability to **track revisions**. Every time you make a significant change to the Pod template within your Deployment, Kubernetes creates a new **revision**. These revisions are snapshots of your Deployment's configuration, primarily managed through the creation of new **ReplicaSets**.

### 5.1. How Revisions are Created and Managed

When you perform an update to a Deployment (e.g., changing the container image, environment variables, or resource limits), the Deployment controller does the following:

1.  **Creates a New ReplicaSet:** A brand new ReplicaSet is created with a unique name and a hash reflecting the updated Pod template. This new ReplicaSet is assigned the next sequential **revision number**.
2.  **Scales Up New ReplicaSet:** The Deployment controller starts scaling up the new ReplicaSet, bringing up new Pods with the updated configuration.
3.  **Scales Down Old ReplicaSet:** Concurrently, it starts scaling down the *previous* ReplicaSet (associated with the old revision), terminating the old Pods. This happens according to the Deployment's `updateStrategy` (e.g., `RollingUpdate`).
4.  **Maintains History:** The old ReplicaSets (and their associated Pods, while they exist) are retained. This history is crucial for rollbacks.

### 5.2. Understanding Revision Numbers

  * Each meaningful change to a Deployment's `spec.template` (the Pod template) increments the revision number.
  * The revision number is stored in an annotation on the ReplicaSet, typically `deployment.kubernetes.io/revision`.
  * You **don't explicitly set revision numbers**. Kubernetes assigns and manages them automatically.
  * Changes that **do not** affect the Pod template (e.g., scaling the `replicas` count, changing `metadata` like labels or annotations on the Deployment itself but *not* on the `template`) typically **do not create a new revision**.

### 5.3. Inspecting Deployment History (Revisions)

You can inspect the revision history of a Deployment using the `kubectl rollout history` command:

```bash
kubectl rollout history deployment/<your-deployment-name>
```

**Example Output:**

```
deployment.apps/my-app
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
3         kubectl set image deployment/my-app my-app=my-image:v2.0
4         kubectl set env deployment/my-app MY_ENV=new_value
```

  * **`REVISION`**: The unique number assigned to each revision.

  * **`CHANGE-CAUSE`**: This annotation (`kubernetes.io/change-cause`) is often automatically populated by `kubectl` commands (like `kubectl set image`, `kubectl apply -f`) when they initiate a rollout. If you use a `kubectl apply -f` with a file, you might need to add this annotation manually to the Deployment's `metadata` for better traceability:

    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: my-app
      annotations:
        kubernetes.io/change-cause: "Updated image to v2.0" # Manually added for clarity
    spec:
      # ...
    ```

### 5.4. The Power of Rollbacks ↩️

Since Deployments meticulously track revisions, you can easily revert to any previous stable version if an update goes wrong.

  * **Rollback to the immediately previous revision:**

    ```bash
    kubectl rollout undo deployment/<your-deployment-name>
    ```

    This command effectively undoes the last change, scaling down the current ReplicaSet and scaling up the one associated with the previous revision.

  * **Rollback to a specific revision:**

    ```bash
    kubectl rollout undo deployment/<your-deployment-name> --to-revision=<revision-number>
    ```

    This allows you to jump back several versions if needed. Kubernetes will scale up the ReplicaSet corresponding to the specified revision and scale down others.

### 5.5. Limiting Revision History (`revisionHistoryLimit`)

By default, Kubernetes keeps a history of 10 old ReplicaSets and their corresponding revisions. This is configurable using the `revisionHistoryLimit` field in your Deployment spec.

  * **Purpose:** To prevent an excessive number of old ReplicaSets from accumulating in your cluster, which can consume resources (even if scaled to 0 pods) and clutter `kubectl get rs` output.
  * **Syntax:**
    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: my-app
    spec:
      replicas: 3
      selector:
        matchLabels:
          app: my-app
      revisionHistoryLimit: 5 # Keep only the last 5 revisions + the current one
      template:
        metadata:
          labels:
            app: my-app
        spec:
          containers:
          - name: my-container
            image: nginx:latest
    ```
  * **Impact:** If `revisionHistoryLimit` is set to `5`, Kubernetes will only retain the last 5 old ReplicaSets (plus the currently active one). When a new revision is created, the oldest ReplicaSet beyond this limit will be garbage-collected.

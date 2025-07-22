# Kubernetes Horizontal Pod Autoscaler (HPA) Study Notes 🚀

This repository contains in-depth study notes on the **Horizontal Pod Autoscaler (HPA)** in Kubernetes. HPA is a crucial component that allows your applications to dynamically adjust to varying workloads by automatically changing the number of running pods.

-----

## Table of Contents

  * [Understanding HPA: How It Works](https://www.google.com/search?q=%23understanding-hpa-how-it-works)
      * [Metric Collection](https://www.google.com/search?q=%23metric-collection)
      * [Evaluation and Desired Replicas Calculation](https://www.google.com/search?q=%23evaluation-and-desired-replicas-calculation)
      * [Scaling Decision](https://www.google.com/search?q=%23scaling-decision)
      * [Action](https://www.google.com/search?q=%23action)
  * [How to Set Up HPA](https://www.google.com/search?q=%23how-to-set-up-hpa)
      * [Prerequisites](https://www.google.com/search?q=%23prerequisites)
      * [Steps to Configure HPA](https://www.google.com/search?q=%23steps-to-configure-hpa)
  * [HPA Metrics Types](https://www.google.com/search?q=%23hpa-metrics-types)
  * [HPA Configuration Parameters (v2 API)](https://www.google.com/search?q=%23hpa-configuration-parameters-v2-api)
  * [Advanced HPA: The `behavior` Field](https://www.google.com/search?q=%23advanced-hpa-the-behavior-field)
  * [Conclusion](https://www.google.com/search?q=%23conclusion)

-----

## Understanding HPA: How It Works

The HPA operates as a **control loop**, continuously monitoring specified metrics and adjusting the replica count of your target workload (e.g., Deployment, ReplicaSet, StatefulSet).

### Metric Collection

The HPA gathers metrics from:

  * **Kubernetes Metrics Server**: For core metrics like **CPU** and **memory** utilization.
  * **Custom Metrics API**: For application-specific metrics (e.g., requests per second, queue length).
  * **External Metrics API**: For metrics originating from outside the cluster (e.g., messages in an external queue).

### Evaluation and Desired Replicas Calculation

The HPA controller periodically (default **15 seconds**) queries the metrics APIs for current values. It calculates the average metric value across all pods and determines the `desiredReplicas` using the formula:

$$\text{desiredReplicas} = \text{ceil}(\text{currentReplicas} \times (\text{currentMetricValue} / \text{targetMetricValue}))$$

For example, if you have 3 pods, the target CPU is 50%, and the current average CPU is 75%, the desired replicas would be:

$$\text{desiredReplicas} = \text{ceil}(3 \times (75 / 50)) = \text{ceil}(3 \times 1.5) = \text{ceil}(4.5) = 5$$

HPA also includes a **stabilization window** (default **5 minutes for scale down**, **3 minutes for scale up**) to prevent rapid fluctuations or "thrashing" in the number of replicas.

### Scaling Decision

  * **Scale Up**: Initiated if `desiredReplicas` \> `currentReplicas` and $\\le$ `maxReplicas`.
  * **Scale Down**: Initiated if `desiredReplicas` \< `currentReplicas` and $\\ge$ `minReplicas` (after the stabilization period).
  * **No Action**: If `desiredReplicas` equals `currentReplicas`.

HPA always respects the **`minReplicas`** and **`maxReplicas`** bounds defined in its specification.

### Action

The HPA updates the `replicas` field of the target workload, and the corresponding Kubernetes controller (e.g., Deployment Controller) then creates or terminates pods to match the new desired count.

-----

## How to Set Up HPA

Setting up HPA involves a few critical steps:

### Prerequisites

1.  **Kubernetes Cluster**: A running Kubernetes cluster.
2.  **Metrics Server**: The **Kubernetes Metrics Server** must be installed. Install it using:
    ```bash
    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
    ```
    Verify with: `kubectl get apiservices | grep metrics`
3.  **Resource Requests and Limits**: Your application's pods **must have CPU resource requests defined** for CPU-based HPA to function correctly.

### Steps to Configure HPA

Let's use an `nginx-deployment` as an example.

1.  **Define Resource Requests for Your Pods**:
    Modify your Deployment manifest (`nginx-deployment.yaml`) to include `resources.requests` for CPU:

    ```yaml
    # nginx-deployment.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: nginx-deployment
    spec:
      replicas: 1
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
            resources:
              requests:
                cpu: "100m" # Request 100 millicores (0.1 CPU core)
                memory: "128Mi"
              limits:
                cpu: "200m" # Limit 200 millicores
                memory: "256Mi"
    ```

    Apply this change: `kubectl apply -f nginx-deployment.yaml`

2.  **Create the Horizontal Pod Autoscaler**:

      * **Option A: Using `kubectl autoscale` (Quick Way)**:

        ```bash
        kubectl autoscale deployment nginx-deployment --cpu-percent=50 --min=1 --max=5
        ```

        This sets a target **50% CPU utilization**, with a **minimum of 1 pod** and a **maximum of 5 pods**.

      * **Option B: Using a YAML Manifest (Recommended for Flexibility)**:
        Create `nginx-hpa.yaml`:

        ```yaml
        # nginx-hpa.yaml
        apiVersion: autoscaling/v2
        kind: HorizontalPodAutoscaler
        metadata:
          name: nginx-hpa
        spec:
          scaleTargetRef:
            apiVersion: apps/v1
            kind: Deployment
            name: nginx-deployment
          minReplicas: 1
          maxReplicas: 5
          metrics:
          - type: Resource
            resource:
              name: cpu
              target:
                type: Utilization
                averageUtilization: 50 # Target average CPU utilization at 50%
        ```

        Apply the manifest: `kubectl apply -f nginx-hpa.yaml`

3.  **Verify HPA Status**:
    Check the HPA status with: `kubectl get hpa`

    Example output:

    ```
    NAME        REFERENCE                  TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
    nginx-hpa   Deployment/nginx-deployment   0%/50%    1         5         1          1m
    ```

      * `TARGETS`: Current vs. target CPU utilization.
      * `REPLICAS`: Current number of running pods.

4.  **Test HPA (Simulate Load)**:

      * **Method 1: Using `kubectl run` (CPU Intensive Pod)**:
        ```bash
        kubectl run -it --rm load-generator --image=busybox -- /bin/sh -c "while true; do wget -q -O- http://nginx-deployment.default.svc.cluster.local; done"
        ```
      * **Method 2: Using a Dedicated Load Testing Tool**: (e.g., ApacheBench, Hey, Locust)
        Example with `hey`:
        ```bash
        hey -z 30s -c 100 http://<your-nginx-service-ip>
        ```

5.  **Observe HPA Scaling**:
    Monitor the HPA status in watch mode: `kubectl get hpa -w`
    You'll observe `TARGETS` increasing, followed by `REPLICAS` scaling up. After the load stops and the scale-down stabilization period passes, `REPLICAS` will decrease.

-----

## HPA Metrics Types

HPA supports diverse metrics for scaling decisions:

  * **`Resource` Metrics**:
      * **CPU**: Scales based on average CPU utilization or raw usage.
      * **Memory**: Scales based on average memory utilization or raw usage.
        (Both require resource requests to be set on pods.)
  * **`Pods` Metrics**: Custom metrics averaged or summed per pod (e.g., HTTP requests per second per pod). Requires a custom metrics adapter (e.g., Prometheus Adapter).
  * **`Object` Metrics**: Custom metrics associated with a single Kubernetes object (e.g., total requests per second on an Ingress). Requires a custom metrics adapter.
  * **`External` Metrics**: Metrics from outside the Kubernetes cluster (e.g., message queue depth). Requires an external metrics adapter.

-----

## HPA Configuration Parameters (v2 API)

When defining HPA via YAML using `autoscaling/v2`, key fields include:

  * `scaleTargetRef`: Specifies the Deployment, ReplicaSet, or StatefulSet to scale.
      * `apiVersion`: API version of the target.
      * `kind`: Kind of the target.
      * `name`: Name of the target.
  * `minReplicas`: Minimum number of replicas.
  * `maxReplicas`: Maximum number of replicas.
  * `metrics`: An array of metric specifications. HPA scales if *any* metric suggests it.
  * `behavior` (Optional): Allows fine-tuning scaling actions.

-----

## Advanced HPA: The `behavior` Field

The `behavior` field (available in `autoscaling/v2`) provides granular control to prevent aggressive or overly conservative scaling:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-hpa-with-behavior
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300 # Wait 5 minutes before scaling down
      policies:
      - type: Percent
        value: 100 # Allow scaling down by 100% of current pods
        periodSeconds: 15
      - type: Pods
        value: 2 # Allow removing max 2 pods
        periodSeconds: 15
    scaleUp:
      stabilizationWindowSeconds: 0 # Scale up immediately
      policies:
      - type: Percent
        value: 100 # Allow scaling up by 100% of current pods
        periodSeconds: 15
      - type: Pods
        value: 4 # Allow adding max 4 pods
        periodSeconds: 15
```

This example shows policies for both `scaleDown` and `scaleUp` to control the rate and amount of pod changes.

-----

## Conclusion

The Horizontal Pod Autoscaler is an **indispensable feature** in Kubernetes for managing application elasticity. By effectively using CPU, memory, or custom metrics, HPA ensures your applications can dynamically adapt to changing demands, leading to better performance, improved resource utilization, and ultimately, **cost savings**. Always start by defining appropriate resource requests and limits, install the Metrics Server, and then carefully configure and monitor your HPA behavior to achieve optimal results.

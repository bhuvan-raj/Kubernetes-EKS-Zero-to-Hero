# Kubernetes Pod Placement: Node Selector vs. Node Affinity 🚀

Welcome\! This `README.md` will guide you through two crucial concepts in Kubernetes: **Node Selector** and **Node Affinity**. These mechanisms empower you to control *where* your Pods run within your cluster, ensuring they land on nodes that meet specific requirements.

-----

## 🎯 Why is Pod Placement Important?

Imagine you have different types of servers (nodes) in your Kubernetes cluster:

  * Some with **GPUs** for machine learning workloads.
  * Others with **SSDs** for high-performance databases.
  * Nodes in specific **geographical zones** for disaster recovery.
  * Nodes dedicated to **production** environments, separate from development.

Without proper placement controls, Kubernetes might schedule your high-performance database on a slow HDD node, or a GPU-intensive task on a CPU-only node. This is where Node Selector and Node Affinity come in\!

-----

## 🔑 Node Selector: The Simple Matchmaker

<img src="https://github.com/bhuvan-raj/Kubernetes-Openshift-Zero-to-Hero/blob/main/Node%20Selector%20and%20Node%20Affinity/assets/node.png" alt="Banner" />


`Node Selector` is the **most basic and direct** way to constrain Pods to nodes. It works like a simple, strict filter.

### How it Works:

You specify a set of `key: value` pairs (these are **labels**) that a target node *must* have for your Pod to be scheduled on it. If no node has *all* the specified labels, the Pod will remain unscheduled.

### Syntax:

You define `nodeSelector` directly in your Pod's `spec`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-web-app
spec:
  # The nodeSelector field
  nodeSelector:
    disktype: ssd        # Node must have label 'disktype: ssd'
    environment: prod    # Node must have label 'environment: prod'
  containers:
    - name: nginx
      image: nginx:latest
      ports:
        - containerPort: 80
```

### Explanation:

This Pod `my-web-app` will **only** be scheduled on a node that has *both* the label `disktype: ssd` AND `environment: prod`.

### Use Cases:

  * **Dedicated Nodes:** Running specific applications (e.g., databases) on nodes specifically configured for them.
  * **Simple Hardware Requirements:** Ensuring a Pod runs on a node with a particular hardware component (e.g., `gpu: true`).

### Limitations:

  * **Strict Equality Only:** No "OR" logic, no "NOT IN" logic. It's an exact match for *all* specified labels.
  * **No Preferences:** You can't say "prefer this node, but if not available, try that."


## How to Label a Node

The basic syntax for labeling a node is:
```
kubectl label nodes <node-name> <label-key>=<label-value>
```

## Verifying Node Labels

```
kubectl get nodes --show-labels
```

-----

## ✨ Node Affinity: The Advanced Matchmaker
<img src="https://github.com/bhuvan-raj/Kubernetes-Openshift-Zero-to-Hero/blob/main/Node%20Selector%20and%20Node%20Affinity/assets/affinity.png" alt="Banner" />

`Node Affinity` is a **more powerful and flexible** way to constrain Pods. It offers richer matching logic, including "soft" preferences and various operators. It's defined under the `affinity` field in your Pod's `spec`.

Node Affinity has two main types:

### 1\. `requiredDuringSchedulingIgnoredDuringExecution` (Hard Affinity) 🚦

This is like an **enhanced `nodeSelector`**. It's a **hard requirement**: if a node doesn't meet these rules, the Pod will *not* be scheduled.

  * `requiredDuringScheduling`: The rule *must* be met for the Pod to be scheduled.
  * `IgnoredDuringExecution`: If a node's labels change *after* the Pod is scheduled, the Pod will **not** be evicted or moved. It stays put.

### Syntax:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-ml-pod
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms: # This is an OR condition
        - matchExpressions: # This is an AND condition
          - key: kubernetes.io/arch
            operator: In
            values:
            - amd64
            - arm64
          - key: gpu
            operator: Exists
        - matchExpressions: # This is another AND condition (OR with the first)
          - key: cloud-provider
            operator: NotIn
            values:
            - aws # Don't schedule on AWS nodes (just an example)
  containers:
    - name: ml-model
      image: ml-image:latest
```

### Explanation of Operators:

  * `In`: Node's label value must be one of the specified values.
  * `NotIn`: Node's label value must *not* be one of the specified values.
  * `Exists`: Node must have a label with the specified key (value doesn't matter).
  * `DoesNotExist`: Node must *not* have a label with the specified key.
  * `Gt` (Greater than), `Lt` (Less than): For numeric label values.

### Logic:

  * `nodeSelectorTerms`: Acts as a **logical OR**. If *any* `nodeSelectorTerm` is satisfied, the Pod can be scheduled.
  * `matchExpressions` within a `nodeSelectorTerm`: Acts as a **logical AND**. All `matchExpressions` within a term must be true for that term to be satisfied.

### 2\. `preferredDuringSchedulingIgnoredDuringExecution` (Soft Affinity) 🙏

This specifies a **preference**, not a strict requirement. The scheduler will *try* to place the Pod on a node that meets these rules. If it can't find such a node, it will still schedule the Pod elsewhere. This is great for optimization\!

You can assign a `weight` (1-100) to each preference. Nodes that satisfy higher-weighted preferences will be prioritized.

### Syntax:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-batch-job
spec:
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 80 # High preference
        preference:
          matchExpressions:
          - key: cost-effective
            operator: In
            values:
            - "true"
      - weight: 20 # Lower preference
        preference:
          matchExpressions:
          - key: zone
            operator: In
            values:
            - us-east-1a
  containers:
    - name: batch-processor
      image: batch-image:latest
```

### Explanation:

The scheduler will strongly prefer nodes labeled `cost-effective: "true"` (weight 80). It will also prefer nodes in `us-east-1a` (weight 20). If a node has both, it gets a combined weight of 100, making it highly desirable. If no such nodes exist, the Pod will still be scheduled on any available node.

### Use Cases:

  * **Cost Optimization:** Preferring cheaper or spot instances.
  * **Performance Optimization:** Preferring nodes with specific hardware for better performance, but allowing fallback.
  * **Spreading Workloads:** Gently guiding Pods to be distributed across different zones or racks.

-----

## 🆚 Node Selector vs. Node Affinity: A Quick Summary

| Feature          | `Node Selector`                               | `Node Affinity` (`requiredDuringScheduling...`)         | `Node Affinity` (`preferredDuringScheduling...`)      |
| :--------------- | :-------------------------------------------- | :------------------------------------------------------ | :---------------------------------------------------- |
| **Requirement** | Hard (must match)                             | Hard (must match)                                       | Soft (preference, tries to match)                     |
| **Operators** | Only equality (`key: value`)                  | `In`, `NotIn`, `Exists`, `DoesNotExist`, `Gt`, `Lt`     | `In`, `NotIn`, `Exists`, `DoesNotExist`, `Gt`, `Lt`   |
| **Logic** | AND (all labels must match)                   | OR (between `nodeSelectorTerms`), AND (within `matchExpressions`) | OR (between `preferences`), AND (within `matchExpressions`) |
| **Flexibility** | Low                                           | High                                                    | High (with weighting)                                 |
| **Best For** | Simple, strict, exact-match requirements      | Complex, strict requirements with advanced logic        | Guiding placement, optimization, graceful degradation |

-----

## 👩‍💻 Hands-On Exercise Ideas:

1.  **Label Your Nodes:**

      * Pick a few nodes in your cluster.
      * Use `kubectl label nodes <node-name> disktype=ssd environment=dev`
      * Use `kubectl label nodes <node-name> gpu=true`

2.  **Deploy with Node Selector:**

      * Create a Pod YAML that uses `nodeSelector` to target a node with `disktype: ssd`.
      * Observe if it gets scheduled.
      * Try changing the label to something that doesn't exist – what happens?

3.  **Deploy with Required Node Affinity:**

      * Create a Pod YAML using `requiredDuringSchedulingIgnoredDuringExecution` to schedule on nodes that are `amd64` OR `arm64`, AND have a `gpu` label.
      * Experiment with different `operator` types (`NotIn`, `Exists`).

4.  **Deploy with Preferred Node Affinity:**

      * Create a Pod YAML using `preferredDuringSchedulingIgnoredDuringExecution`.
      * Give a higher weight to nodes with `cost-effective: "true"` and a lower weight to nodes in a specific zone.
      * Observe how the scheduler places your Pods.

-----

By mastering Node Selector and Node Affinity, you gain fine-grained control over your Kubernetes workloads, leading to more efficient resource utilization, better performance, and improved reliability\! Happy scheduling\! 🚀

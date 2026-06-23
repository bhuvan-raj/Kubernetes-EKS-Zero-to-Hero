# Kubernetes Pod Affinity & Pod Anti-Affinity

Pod Affinity and Pod Anti-Affinity are Kubernetes scheduling features that control how pods are placed relative to other pods.

* **Pod Affinity** attracts pods toward other pods.
* **Pod Anti-Affinity** repels pods away from other pods.

These rules help achieve:

* High Availability
* Fault Tolerance
* Workload Colocation
* Performance Optimization
* Resource Distribution

---

## 📚 Core Concept

Unlike **Node Affinity**, which makes scheduling decisions based on **node labels**, **Pod Affinity** and **Pod Anti-Affinity** make scheduling decisions based on the labels of existing pods.

The Kubernetes scheduler evaluates:

1. Labels on existing pods
2. The topology domain (node, zone, region, etc.)
3. Affinity or anti-affinity rules defined in the new pod

---

# 🤝 Pod Affinity

Pod Affinity tells Kubernetes:

> "Schedule this pod close to other pods matching specific labels."

### Example Use Cases

* Frontend pods should run close to backend pods.
* Application pods should run in the same availability zone as their database.

### Benefits

* Reduced network latency
* Better communication performance
* Improved data locality

---

## Types of Pod Affinity Rules

### 1. requiredDuringSchedulingIgnoredDuringExecution (Hard Affinity) 🔒

This rule is **mandatory**.

If Kubernetes cannot find a location satisfying the affinity rule, the pod remains in the **Pending** state.

### Example

```yaml
affinity:
  podAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchExpressions:
        - key: app
          operator: In
          values:
          - backend
      topologyKey: kubernetes.io/hostname
```

### Meaning

Schedule this pod **only** on a node that already contains a pod with label:

```text
app=backend
```

---

### 2. preferredDuringSchedulingIgnoredDuringExecution (Soft Affinity) 🧘

This rule is a **preference**.

The scheduler tries to satisfy the rule but may ignore it if necessary.

### Example

```yaml
affinity:
  podAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - backend
        topologyKey: kubernetes.io/hostname
```

### Meaning

Prefer placing this pod on a node containing backend pods.

---

# 🚫 Pod Anti-Affinity

Pod Anti-Affinity tells Kubernetes:

> "Do not schedule this pod near other pods matching specific labels."

This is commonly used to spread replicas across nodes and improve availability.

### Benefits

* High Availability
* Fault Tolerance
* Better Workload Distribution
* Reduced Single Points of Failure

---

## Types of Pod Anti-Affinity Rules

### 1. requiredDuringSchedulingIgnoredDuringExecution (Hard Anti-Affinity) 🚫

This rule is **mandatory**.

If Kubernetes cannot find a node satisfying the rule, the pod remains in the **Pending** state.

### Example

```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchExpressions:
        - key: app
          operator: In
          values:
          - nginx
      topologyKey: kubernetes.io/hostname
```

### Meaning

Do not place this pod on a node that already contains:

```text
app=nginx
```

---

### 2. preferredDuringSchedulingIgnoredDuringExecution (Soft Anti-Affinity) 🧘

This is a **best-effort** rule.

The scheduler prefers to avoid placing pods together but will do so if required.

### Example

```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - nginx
        topologyKey: kubernetes.io/hostname
```

### Meaning

Prefer not to place this pod on a node already running nginx pods.

---

# 📝 Complete Example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: frontend
  labels:
    app: frontend

spec:
  containers:
  - name: nginx
    image: nginx

  affinity:
    podAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: app
              operator: In
              values:
              - backend
          topologyKey: topology.kubernetes.io/zone

    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - frontend
        topologyKey: kubernetes.io/hostname
```

### Explanation

* Frontend pods prefer running in the same zone as backend pods.
* Frontend replicas cannot run on the same node.

---

# 🔑 Understanding topologyKey

The `topologyKey` defines the boundary within which affinity or anti-affinity is evaluated.

| topologyKey                   | Meaning                 |
| ----------------------------- | ----------------------- |
| kubernetes.io/hostname        | Node Level              |
| topology.kubernetes.io/zone   | Availability Zone Level |
| topology.kubernetes.io/region | Region Level            |

### Examples

#### Same Node

```yaml
topologyKey: kubernetes.io/hostname
```

#### Same Availability Zone

```yaml
topologyKey: topology.kubernetes.io/zone
```

#### Same Region

```yaml
topologyKey: topology.kubernetes.io/region
```

---

# ✨ Real-World Use Cases

## Pod Affinity

### Frontend Near Backend

Keep frontend and backend pods in the same zone to reduce latency.

### Application Near Cache

Place application pods close to Redis pods for faster communication.

### Microservice Colocation

Run heavily communicating services together.

---

## Pod Anti-Affinity

### High Availability

Distribute replicas across multiple worker nodes.

### Stateful Applications

Prevent database replicas from running on the same node.

### Fault Isolation

Ensure critical services are separated.

### Kubernetes Deployments

Spread deployment replicas across different worker nodes.

---

# ⚠️ Important Considerations

## Hard Rules Can Block Scheduling

Pods using:

```yaml
requiredDuringSchedulingIgnoredDuringExecution
```

may remain in the **Pending** state if no suitable location exists.

---

## Soft Rules Are Recommendations

Pods using:

```yaml
preferredDuringSchedulingIgnoredDuringExecution
```

can still be scheduled even when the preference cannot be met.

---

## Topology Matters

Choosing an incorrect topology key can unintentionally restrict scheduling.

---

## Debugging Affinity Issues

To troubleshoot scheduling problems:

```bash
kubectl describe pod <pod-name>
```

Check the **Events** section for scheduler messages explaining why the pod could not be scheduled.

---

# 📌 Summary

| Feature           | Purpose                     |
| ----------------- | --------------------------- |
| Pod Affinity      | Place pods together         |
| Pod Anti-Affinity | Keep pods apart             |
| Hard Rules        | Must be satisfied           |
| Soft Rules        | Preferred but optional      |
| topologyKey       | Defines scheduling boundary |

---

## Conclusion

Pod Affinity improves communication and locality by placing related workloads together.

Pod Anti-Affinity improves availability and fault tolerance by spreading workloads apart.

Together, they provide powerful control over workload placement and help build highly available, efficient Kubernetes clusters.

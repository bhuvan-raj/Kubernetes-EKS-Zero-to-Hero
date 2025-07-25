# Kubernetes `PriorityClass` - Study Notes

## 📌 1. Introduction to PriorityClass

`PriorityClass` is a Kubernetes object that allows you to define the importance of Pods using an integer-based priority. Higher values mean higher priority, influencing scheduling and **preemption** (eviction of lower-priority Pods).

## ❓ 2. Why is PriorityClass Needed?

Without `PriorityClass`, the scheduler treats all Pods equally. This can cause:

* Critical apps getting stuck in `Pending` state
* Unstable system components
* Inefficient use of resources

Use cases:

* Critical system Pods
* Business-critical apps
* Low-priority batch jobs

## ⚙️ 3. How It Works

### a) Scheduling Phase

* Scheduler attempts to place Pods based on resource requests and constraints.

### b) Preemption Phase

* When a high-priority Pod is `Pending`:

  1. Scheduler identifies nodes where it *could* run.
  2. Evicts lower-priority Pods to free up space.
  3. Pod is scheduled once resources are available.

**Note:** Preemption is graceful and not instantaneous.

## 🧾 4. PriorityClass YAML Fields

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: <name>
value: <integer> # Required
globalDefault: <true|false>
description: <string> # Optional
```

* `value`: Priority level
* `globalDefault`: Used for Pods without a `priorityClassName`

## 🔧 5. Built-in PriorityClasses

| Name                      | Priority Value | Use Case                         |
| ------------------------- | -------------- | -------------------------------- |
| `system-node-critical`    | 2000000000     | Essential node-level components  |
| `system-cluster-critical` | 1000000000     | Cluster-wide critical components |

## 🛠️ 6. Creating PriorityClasses

### Example: High Priority

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 1000000
globalDefault: false
description: "Critical application components."
```

### Example: Low Priority (Default)

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: low-priority
value: 100
globalDefault: true
description: "Default for non-critical workloads."
```

## 🚀 7. Using PriorityClass in Pods

### Example: Pod with High Priority

```yaml
spec:
  priorityClassName: high-priority
```

### Example: Deployment with Low Priority

```yaml
spec:
  template:
    spec:
      priorityClassName: low-priority
```

## 🔄 8. Preemption: Choosing Victims

* **Lowest priority** Pods are evicted first
* Evict **largest consumers** next
* Follow QoS class: BestEffort < Burstable < Guaranteed
* PodDisruptionBudget (PDB) is respected

## ✅ 9. Best Practices

* Use `globalDefault: true` on low-priority classes
* Leave gaps in `value` to add intermediate classes later
* Don’t assign high priority to all Pods
* Simulate preemption in test environments

## ⚠️ 10. Limitations

* **No extra resources:** Priority doesn't create capacity
* **Eviction delay:** Grace period may slow scheduling
* **Complexity:** Adds overhead to scheduling logic
* **Non-preemptable Pods:** Some daemon-level Pods can't be evicted

---

By understanding and applying `PriorityClass`, you can build more stable, fair, and intelligent Kubernetes scheduling policies for critical workloads.

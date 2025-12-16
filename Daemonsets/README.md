# 🖥️ Kubernetes DaemonSets - Ensuring Pod Presence on Every Node

<img src="https://github.com/bhuvan-raj/Kubernetes-Openshift-Zero-to-Hero/blob/main/Daemonsets/assets/ds.png" alt="Banner" />


This README provides a comprehensive overview of **DaemonSets** in Kubernetes, explaining their purpose, how they operate, configuration details, and their crucial role in managing cluster-wide services.

-----

## 🤔 Why DaemonSets?

In a Kubernetes cluster, certain services or agents need to run on **every (or selected) node** rather than being randomly scheduled. Think of them as essential background processes for each machine. Manually deploying and managing these across all nodes would be tedious and error-prone.

DaemonSets solve this by:

  * **Guaranteed Presence:** Ensuring a single copy of a specific Pod is always running on every eligible node.
  * **Automated Deployment:** Automatically spinning up the Pod on new nodes as they join the cluster.
  * **Self-Healing:** Replacing a Pod if it fails or is deleted from a node.

-----

## ⚙️ How DaemonSets Work

The DaemonSet controller works behind the scenes to maintain the desired state:

1.  **Node Affinity:** Unlike other controllers (like Deployments), DaemonSets **don't use the standard Kubernetes scheduler**. Instead, the DaemonSet controller directly creates Pods on nodes that match its specified `nodeSelector` or `nodeAffinity` criteria. If no selector is defined, it targets *all* eligible nodes.
2.  **One Pod Per Node:** This is the core principle. If a node is added, a new Pod is created. If a node is removed, its associated Pod is garbage collected.
3.  **Self-Healing:** Should a DaemonSet Pod crash or be accidentally deleted from a node, the controller swiftly creates a replacement to restore the desired state.
4.  **No Scheduling Conflicts:** Since they bypass the scheduler, DaemonSet Pods don't compete for resources with other Pods during the initial placement.
5.  **Rolling Updates:** DaemonSets support graceful rolling updates, allowing you to update the Pod template (e.g., a new image version) one node at a time (or in batches) with minimal disruption.

-----

## 🛠️ DaemonSet Configuration


** Basic DaemonSet manifest **
```
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: nginx-test-daemonset
  labels:
    name: irfan-daemonset
spec:
  selector:
    matchLabels:
      app: nginx-test
  template:
    metadata:
      labels:
        app: nginx-test
    spec:
      containers:
      - name: nginx-test-container
        image: nginx:latest # Latest Nginx image
        ports:
        - containerPort: 80
          name: http-web
```



**Example DaemonSet Manifest (for a log collector):**

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd-logger # Name of your DaemonSet
  labels:
    app: fluentd-logging
spec:
  selector:
    matchLabels:
      app: fluentd-logging # Must match labels in template.metadata.labels
  template: # This defines the Pod that will run on each node
    metadata:
      labels:
        app: fluentd-logging
    spec:
      tolerations: # Allows Pod to be scheduled on nodes with specific taints
      - key: node-role.kubernetes.io/control-plane # Or "master" for older versions
        operator: Exists
        effect: NoSchedule
      containers:
      - name: fluentd-container
        image: fluentd/fluentd:v1.16-debian-1 # Example image for log collection
        resources:
          limits:
            memory: 200Mi
          requests:
            cpu: 100m
            memory: 128Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log # Mount host's log directory
        - name: docker-logs # Mount Docker container logs
          mountPath: /var/lib/docker/containers
          readOnly: true
      terminationGracePeriodSeconds: 30 # Time for graceful shutdown
      volumes: # Define hostPath volumes to access node resources
      - name: varlog
        hostPath:
          path: /var/log
      - name: docker-logs
        hostPath:
          path: /var/lib/docker/containers
```

**Key Configuration Details:**

  * `spec.selector`: **Required.** Must match `spec.template.metadata.labels` to identify and manage its Pods.
  * `spec.template`: The actual **Pod specification** that will be deployed on each eligible node.
  * `spec.updateStrategy`: Controls how Pod updates are rolled out.
      * `RollingUpdate` (default): Updates Pods one by one. Recommended for most cases.
      * `OnDelete`: Requires manual deletion of old Pods to trigger recreation. (Rarely used).
  * `spec.template.spec.nodeSelector` / `nodeAffinity`: Use these to **target a subset of nodes**. For example, run a GPU monitoring agent only on nodes with GPUs.
  * `spec.template.spec.tolerations`: Essential for DaemonSets that need to run on all nodes, including those with taints (e.g., control plane nodes often have `NoSchedule` taints).

-----

## ✨ Benefits of DaemonSets

  * **Guaranteed Service Availability:** Ensures critical infrastructure agents are always present on their respective nodes.
  * **Automated Management:** Simplifies the deployment, scaling, and self-healing of node-level services.
  * **Efficient Resource Usage:** Prevents redundant Pods on a single node, optimizing resource consumption.
  * **Smooth Updates:** `RollingUpdate` strategy allows for seamless upgrades with minimal disruption.
  * **Targeted Deployment:** Granular control to deploy services only to specific node types using selectors/affinity.

-----

## 🚧 Limitations of DaemonSets

  * **One Pod Per Node (Generally):** While ideal for many agents, DaemonSets are not suitable if you need *multiple* instances of the same Pod on a single node.
  * **No Workload-Based Auto-Scaling:** DaemonSets scale based on node count, not on the workload demand of the agent itself. If an agent becomes overloaded, it won't automatically scale up on the same node.
  * **Resource Management:** Careful management of CPU/memory requests and limits is crucial, as DaemonSet Pods run across your entire cluster and can impact overall node performance if poorly configured.

-----

## 🎯 Common Use Cases for DaemonSets

DaemonSets are perfectly suited for:

  * **Log Collection Agents:** `fluentd`, `Filebeat`, `Logstash` forwarders.
  * **Monitoring Agents:** `Prometheus Node Exporter`, `Datadog Agent`, `New Relic Infrastructure Agent`.
  * **Network Proxies / CNI Plugins:** `kube-proxy` (a core Kubernetes component), `Calico`, `Flannel`, `Weave Net` agents.
  * **Storage Daemons:** Components for distributed storage systems like `Ceph` or `GlusterFS`.
  * **Security Agents:** Host-based intrusion detection systems (HIDS) or vulnerability scanners.
  * **Any Node-Level Utility:** Any process that needs direct access to a node's operating system or hardware.

-----

DaemonSets are a fundamental building block for a robust and observable Kubernetes cluster, ensuring that your essential background services are always running where they're needed.

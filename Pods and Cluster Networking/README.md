## 📘 Table of Contents

1. [What is a Kubernetes Pod?](#1-what-is-a-kubernetes-pod)

   * [Key Characteristics](#key-characteristics)
2. [Why Does Kubernetes Manage Pods (Not Just Containers)?](#2-why-does-kubernetes-manage-pods-not-just-containers)
3. [How is a Pod Created in Kubernetes? (In-depth Lifecycle)](#3-how-is-a-pod-created-in-kubernetes-in-depth-lifecycle)
4. [Example: A Simple Nginx Pod](#example-a-simple-nginx-pod)
5. [Understanding Kubernetes Networking: The Invisible Connective Tissue](#understanding-kubernetes-networking-the-invisible-connective-tissue)

   * [The Core Principle: Every Pod Gets Its Own IP](#1-the-core-principle-every-pod-gets-its-own-ip)
   * [Key Networking Components in Kubernetes](#2-key-networking-components-in-kubernetes)

     * [Container Network Interface (CNI) Plugin](#21-container-network-interface-cni-plugin-the-pod-network-creator)
     * [Kube-Proxy](#22-kube-proxy-the-service-enabler)
     * [DNS Service](#23-dns-service-service-discovery)
   * [How Pods Communicate: The Scenarios](#3-how-pods-communicate-the-scenarios)

     * [Container-to-Container (Same Pod)](#31-container-to-container-communication-within-the-same-pod)
     * [Pod-to-Pod (Same Node)](#32-pod-to-pod-communication-same-node)
     * [Pod-to-Pod (Different Nodes)](#33-pod-to-pod-communication-across-different-nodes)
     * [Pod-to-Service Communication](#34-pod-to-service-communication-within-the-cluster)
     * [Pod-to-Pod Across Namespaces](#35-pod-to-pod-communication-across-namespaces)
     * [External-to-Service Communication](#36-external-to-service-communication-exposing-to-the-outside-world)
6. [Network Policy (Controlling Traffic Flow)](#4-network-policy-controlling-traffic-flow)
7. [Conclusion](#conclusion)

#  Pods: The Smallest Deployable Unit

<img src="https://github.com/bhuvan-raj/Kubernetes-Openshift-Zero-to-Hero/blob/main/Pods%20and%20Cluster%20Networking/assets/pod.webp" alt="Banner"/>

## 1\. What is a Kubernetes Pod?

In Kubernetes, a **Pod** is the smallest and most fundamental deployable unit. It represents a **single instance of a running process** in your cluster.

Imagine a Pod as a self-contained, isolated environment designed to run one or more tightly-coupled containers. While Docker (or other container runtimes) provides the containerization technology, Kubernetes uses the Pod as its atomic unit of scheduling and management.

### Key Characteristics:

  * **One or More Containers:** A Pod can contain one or more containers that are designed to work closely together. The most common scenario is a single application container, but "sidecar" containers (e.g., for logging, monitoring, data synchronization, or a proxy) are also frequently used within the same Pod.
  * **Shared Resources:** All containers within a single Pod share the same network namespace, IP address, port space, and can share storage volumes. This allows them to communicate with each other using `localhost` and share data efficiently.
  * **Ephemeral Nature:** Pods are designed to be relatively short-lived. If a Pod dies (e.g., due to an application crash, node failure, or explicit deletion), Kubernetes will automatically create a *new* Pod to replace it, rather than attempting to restart the old one.
  * **Atomic Unit of Management:** Kubernetes schedules, scales, and manages Pods as a single, indivisible unit. You never deploy individual containers directly; you always deploy them wrapped inside a Pod.

-----

## 2\. Why Does Kubernetes Manage Pods (Not Just Containers)?

This is a critical distinction that often confuses beginners. While containers are the packaging format for applications, Pods provide the necessary environment and abstraction layer for Kubernetes to manage them effectively.

Here's why Kubernetes focuses on Pods rather than individual containers:

  * **Co-location and Co-scheduling:**
      * **Problem:** Some applications consist of multiple, tightly coupled processes that *must* run on the same machine and communicate with each other very frequently (e.g., a web server and a specialized data synchronizer, or an application with a dedicated log collector).
      * **Pod Solution:** By placing these related containers within the same Pod, Kubernetes guarantees that they will always be **co-located on the same node** and **co-scheduled together**. This ensures low-latency communication via `localhost` and efficient resource sharing.
  * **Shared Network Namespace:**
      * **Problem:** If multiple containers need to share the same IP address and port space to interact, managing them individually would be complex.
      * **Pod Solution:** All containers in a Pod share the same network namespace. They get a single Pod IP address, and they can communicate using `localhost` and distinct port numbers, just like processes on a single physical host. This greatly simplifies inter-container communication.
  * **Shared Storage (Volumes):**
      * **Problem:** Containers often need to share data or access persistent storage.
      * **Pod Solution:** Pods can define and share volumes among their constituent containers. This allows containers within the same Pod to access the same data effortlessly, simplifying tasks like log file sharing or common configuration mounts.
  * **Resource Management and Lifecycle:**
      * **Problem:** Managing CPU, memory, and lifecycle (start, stop, restart) for individual, inter-dependent containers would be difficult and error-prone.
      * **Pod Solution:** Kubernetes applies resource requests/limits and lifecycle management (e.g., probes for health checks) at the Pod level. If any container within a Pod fails, Kubernetes can decide to restart only that container, or restart the entire Pod, ensuring the desired state is maintained.
  * **Abstraction and Flexibility:**
      * **Problem:** Kubernetes needs to be container-runtime agnostic (e.g., work with Docker, containerd, CRI-O).
      * **Pod Solution:** The Pod provides a stable abstraction layer above the container runtime. Kubernetes interacts with the Pod abstraction, and the Kubelet translates Pod specifications into commands for the underlying container runtime.

In essence, the Pod provides the necessary **"container wrapper" and shared execution environment** that allows Kubernetes to manage complex, multi-container applications as a single, atomic unit, while keeping the core container concept simple and focused on packaging.

-----

## 3\. How is a Pod Created in Kubernetes? (In-depth Lifecycle)

When you define a Pod in a YAML file and apply it to your cluster (e.g., `kubectl apply -f my-pod.yml`), a series of orchestrated steps occur to bring your Pod to life. This process involves several key components of the Kubernetes control plane:

### Step 1: User Submits Pod Definition (`kubectl apply`)

1.  **`kubectl` Parses YAML:** Your `kubectl` client reads the `my-pod.yml` file.
2.  **YAML to JSON Conversion:** `kubectl` converts the YAML definition into its JSON equivalent.
3.  **API Request to API Server:** `kubectl` sends an HTTP `POST` request (to create) or `PATCH` request (to update) this JSON payload to the Kubernetes API Server.

### Step 2: API Server Processing

1.  **Request Reception:** The API Server (the central management component) receives the HTTP request.
2.  **Authentication & Authorization:** It authenticates your user and checks your RBAC permissions to ensure you are authorized to create/modify Pods in the specified namespace.
3.  **Admission Controllers:** Various Admission Controllers intercept the request. These can validate the Pod definition (e.g., checking resource quotas, security policies) or even mutate it (e.g., injecting default values). If any controller rejects the Pod, the process stops here.
4.  **Object Persistence:** If all checks pass, the API Server saves the Pod object's desired state into **etcd**, the cluster's highly available key-value store. The Pod's `status.phase` is initially set to `Pending`.
5.  **API Server Response:** The API Server sends a `201 Created` or `200 OK` response back to `kubectl`, confirming the Pod object has been accepted.

### Step 3: Scheduler's Role (Pod Assignment)

1.  **Watching for Pending Pods:** The Kubernetes **Scheduler** continuously watches the API Server for new Pods that are in the `Pending` state and have not yet been assigned to a node (`spec.nodeName` is empty).
2.  **Node Selection Algorithm:** The Scheduler runs a sophisticated algorithm to find the "best fit" node for the Pod. This involves:
      * **Filtering (Predicates):** Eliminating nodes that don't meet the Pod's basic requirements (e.g., insufficient CPU/memory, incompatible node selectors, taints).
      * **Scoring (Priorities):** Ranking the remaining eligible nodes based on various factors (e.g., resource utilization, affinity/anti-affinity rules, even distribution).
3.  **Binding Pod to Node:** Once a node is chosen, the Scheduler makes a `PATCH` request to the API Server to update the Pod object, setting its `spec.nodeName` to the name of the selected node. This binding is also persisted in `etcd`.

### Step 4: Kubelet's Role (Node-Level Execution)

1.  **Watching for Assigned Pods:** The **Kubelet** agent running on the selected worker node continuously watches the API Server for Pods that have been assigned to *its* node.
2.  **Pod Setup:** When it detects the newly assigned Pod:
      * **Creates Network Namespace:** The Kubelet instructs the container runtime (e.g., containerd) to create a new, isolated network namespace for the Pod.
      * **Invokes CNI Plugin:** The Kubelet then calls the **Container Network Interface (CNI)** plugin configured on the node (e.g., Calico, Flannel). The CNI plugin is responsible for:
          * Assigning a unique IP address to the Pod within the cluster's network.
          * Creating virtual network interfaces to connect the Pod's namespace to the node's network.
          * Configuring routing rules to enable Pod-to-Pod communication.
      * **Volume Setup:** If the Pod defines any volumes (like Persistent Volumes or `emptyDir`), the Kubelet prepares and mounts them.
3.  **Container Image Pull & Start:**
      * The Kubelet instructs the container runtime to pull the specified container images (e.g., `nginx:latest`) if they aren't already cached locally.
      * It then creates and starts the container(s) within the Pod's configured environment (network, volumes, resource limits).
4.  **Health Checks & Status Reporting:** The Kubelet continuously monitors the health of the containers (via Liveness and Readiness probes) and reports the Pod's real-time status (e.g., `ContainerCreating`, `Running`, `Ready`, `Failed`) and its assigned IP address back to the API Server. This `status` is updated in `etcd`.

### Step 5: Pod is Running and Accessible

  * Once all containers in the Pod are running and pass their readiness probes, the Pod's `status.phase` eventually becomes `Running`, and it is considered `Ready`.
  * At this point, the Pod is fully operational on its assigned node, consuming resources, and available for network communication within the cluster.

This detailed orchestration ensures that Pods are resilient, scalable, and correctly placed within your Kubernetes cluster.

-----

## Example: A Simple Nginx Pod

To see a Pod definition in action, check out the `nginx-pod.yml` file in this directory.

```yaml
# nginx-pod.yml (Example content - full file likely in the folder)
apiVersion: v1
kind: Pod
metadata:
  name: my-nginx-pod
spec:
  containers:
  - name: nginx-container
    image: nginx:latest
    ports:
    - containerPort: 80
```

You can create this Pod using:

```bash
kubectl apply -f nginx-pod.yml
```

And check its status:

```bash
kubectl get pod my-nginx-pod
kubectl describe pod my-nginx-pod
```
---

# Understanding Kubernetes Networking: The Invisible Connective Tissue

<img src="https://github.com/bhuvan-raj/Kubernetes-Openshift-Zero-to-Hero/blob/main/Pods%20and%20Cluster%20Networking/assets/k8s.jpeg" alt="Banner"/>


While Pods run your applications, and Services expose them, it's the underlying **Kubernetes Networking Model** that enables all these components to communicate seamlessly and effectively. Understanding this model is fundamental to deploying and managing applications in a distributed environment.

## 1\. The Core Principle: Every Pod Gets Its Own IP

The foundational principle of Kubernetes networking is surprisingly simple:

**Every Pod gets its own unique IP address.**

This means:

  * A Pod's IP address is distinct from the IP addresses of the Nodes it runs on.
  * Containers within the *same* Pod share that Pod's single IP address and port space.
  * No NAT (Network Address Translation) is required when communicating between Pods.

This "flat network space" simplifies application design and makes it feel like all Pods are on the same logical network, regardless of which node they are actually running on.

-----

## 2\. Key Networking Components in Kubernetes

Several components work together to implement this network model:

### 2.1. Container Network Interface (CNI) Plugin (The Pod Network Creator)

  * **What it is:** CNI is a specification, and CNI plugins (like Calico, Flannel, Cilium, Weave Net, Canal) are the actual implementations that provide network connectivity for Pods. You install one of these in your cluster.
  * **Role:** The CNI plugin is responsible for:
      * **Assigning IP addresses to Pods.** This is where your excellent question comes in\! The CNI plugin assigns Pod IPs from a **dedicated IP range (CIDR block)** that is specifically reserved for Pods within your Kubernetes cluster. This **"Pod CIDR"** is usually separate from the subnet range used by the Nodes themselves. For example, your Nodes might be in `10.0.0.0/16`, while your Pods might be in `10.42.0.0/16`.
      * **Creating network interfaces** (e.g., `veth` pairs) for each Pod, connecting them to the node's network stack.
      * **Configuring routing rules** on the nodes to ensure that all Pods in the cluster can communicate with each other directly, even across different nodes.
  * **How it works:** When the Kubelet on a node needs to bring up a Pod, it calls the CNI plugin. The CNI plugin then performs the necessary low-level network setup for that specific Pod, drawing an IP from the cluster's Pod CIDR.

### 2.2. Kube-Proxy (The Service Enabler)

  * **What it is:** A network proxy that runs on each Node in the cluster.
  * **Role:** Kube-Proxy's primary job is to ensure that network traffic directed to a Kubernetes **Service** is correctly routed to the healthy Pods backing that Service. It handles **Service abstraction and load balancing**.
  * **How it works:** Kube-Proxy watches the Kubernetes API Server for changes to Service and Endpoint objects. Based on these, it configures `iptables` rules (most common) or `IPVS` rules in the node's kernel. These rules intercept traffic destined for a Service's ClusterIP and redirect it to one of the Service's healthy backend Pods.

### 2.3. DNS Service (Service Discovery)

  * **What it is:** A standard DNS server (like CoreDNS or Kube-DNS) running as a Service within your Kubernetes cluster.
  * **Role:** Provides service discovery. Instead of hardcoding IP addresses, applications within the cluster can use DNS names to find and communicate with Services.
  * **How it works:** When you create a Service, Kubernetes automatically creates a DNS record for it. Pods are configured to use the cluster's DNS service. When a Pod tries to reach `my-service.my-namespace.svc.cluster.local`, the DNS service resolves it to the Service's ClusterIP, which Kube-Proxy then uses to route traffic to the backend Pods.

-----

## 3\. How Pods Communicate: The Scenarios

The core networking model enables seamless communication in various scenarios:

### 3.1. Container-to-Container Communication (Within the Same Pod)

  * **Mechanism:** Shared network namespace.
  * **How it works:** All containers within a single Pod share the same Pod IP address and network interfaces. They can communicate directly using `localhost` and the respective port numbers.
  * **Example:** A main application container on `localhost:8080` and a sidecar logging agent on `localhost:8081`.

### 3.2. Pod-to-Pod Communication (Same Node)

  * **Mechanism:** Direct routing via CNI plugin.
  * **How it works:** Since every Pod has a unique IP (from the Pod CIDR) and the CNI plugin has configured the node's network interfaces and routing tables, a Pod can directly reach another Pod on the same node using its IP address. This communication happens without any NAT.
  * **Example:** `Pod A` (IP: `10.42.0.5`) communicates directly with `Pod B` (IP: `10.42.0.6`) on `Node 1`.

### 3.3. Pod-to-Pod Communication (Across Different Nodes)

  * **Mechanism:** Direct routing via CNI plugin (often using an overlay network or underlying network configuration).
  * **How it works:** This is the magic of the CNI plugin. It ensures that traffic from a Pod on `Node A` destined for a Pod on `Node B` is correctly routed across the physical network between the nodes.
      * **Overlay Networks (e.g., Flannel, Weave Net):** The CNI plugin encapsulates the Pod's network packets into another packet (e.g., VXLAN) that can be routed across the underlying physical network. When the packet arrives at the destination node, it's decapsulated and delivered to the target Pod.
      * **Underlay Networks (e.g., Calico with BGP):** The CNI plugin configures the host's routing tables (often using BGP) so that the underlying network infrastructure (routers, switches) knows how to directly route traffic to the Pod IPs on different nodes, without encapsulation.
  * **Key Takeaway:** Regardless of the underlying CNI implementation, the **Kubernetes network model guarantees that a Pod on one node can communicate directly with a Pod on any other node using the Pod's IP address, without explicit NAT.** The Pod IP is always drawn from the **Pod CIDR**, which is routable across the cluster.
  * **Example:** `Pod A` (IP: `10.42.0.5` on `Node 1`) communicates directly with `Pod C` (IP: `10.42.1.7` on `Node 2`).

### 3.4. Pod-to-Service Communication (Within the Cluster)

  * **Mechanism:** Kube-Proxy and DNS.
  * **How it works:**
    1.  A Pod (e.g., a frontend app) wants to talk to a backend `my-api-service`.
    2.  It resolves `my-api-service` (or `my-api-service.my-namespace.svc.cluster.local`) via the cluster's DNS service. This returns the `ClusterIP` of `my-api-service`.
    3.  The Pod sends traffic to `my-api-service`'s `ClusterIP`.
    4.  Kube-Proxy, running on the Pod's node, intercepts this traffic via `iptables` or `IPVS` rules.
    5.  Kube-Proxy then randomly selects a healthy backend Pod associated with `my-api-service` and redirects the traffic to that Pod's IP and `containerPort`.
  * **Benefit:** Applications don't need to know individual Pod IPs, which are dynamic. They just connect to the stable Service IP, and Kubernetes handles the load balancing and routing.

### 3.5. Pod-to-Pod Communication (Across Namespaces)

  * **Mechanism:** Same as Pod-to-Pod communication (same or different node), but with DNS for service discovery.
  * **How it works:** Communication between Pods in different namespaces follows the same principles as within a single namespace: every Pod has a unique IP address and can communicate directly. However, for a Pod in `namespace-A` to easily find a Pod or Service in `namespace-B`, it typically uses a fully qualified domain name (FQDN).
      * **For Services:** `my-service.other-namespace.svc.cluster.local` (or shorthand `my-service.other-namespace`). The DNS service handles the resolution.
      * **For direct Pod-to-Pod:** While possible by IP, it's generally discouraged due to Pod ephemerality. Services are the robust way to communicate.
  * **Network Policy Note:** While the underlying network allows this communication, **Network Policies** (discussed below) are crucial for restricting communication across namespaces for security and isolation.

### 3.6. External-to-Service Communication (Exposing to the Outside World)

This involves different Service types or Ingress:

  * **`NodePort` Service:**

      * **How it works:** Kube-Proxy opens a specific port (e.g., 30000) on *all* Nodes in the cluster. External traffic hitting `<any_Node_IP>:<NodePort>` is forwarded to the Service's ClusterIP, and then onward to a backend Pod.
      * **Use Case:** Simple exposure, useful for development/testing, or when an external load balancer is manually configured to point to NodePorts.

  * **`LoadBalancer` Service:**

      * **How it works:** Only available in cloud environments (AWS, GCP, Azure, etc.). When you create a `LoadBalancer` Service, the cloud provider's Kubernetes integration automatically provisions an external cloud load balancer (e.g., AWS ELB/ALB, GCP Load Balancer). This external load balancer has a publicly accessible IP and forwards traffic to the Nodes, which then use Kube-Proxy to route to the Pods.
      * **Use Case:** Exposing a single Service directly to the internet with a dedicated external IP.

  * **Ingress Resource:**

      * **How it works:** This is the most flexible way for HTTP/HTTPS traffic. An **Ingress Controller** (e.g., Nginx Ingress Controller, AWS ALB Ingress Controller) runs inside your cluster. You define `Ingress` rules (YAML) that specify how incoming HTTP/HTTPS requests (based on hostname or path) should be routed to internal Kubernetes Services. The Ingress Controller configures itself (or an external cloud load balancer) to implement these rules.
      * **Use Case:** Centralized routing for multiple services under a single external IP, hostname-based routing, path-based routing, SSL/TLS termination.

-----

## 4\. Network Policy (Controlling Traffic Flow)

While the Kubernetes network model allows all Pods to communicate by default, in production environments, you often need to restrict traffic for security.

  * **What it is:** A Kubernetes API object (`kind: NetworkPolicy`) that allows you to define rules about how Pods are allowed to communicate with each other and with external endpoints.
  * **Role:** Acts as a firewall for Pods. It enables you to specify which Pods can talk to which other Pods, based on labels, namespaces, IP blocks, and ports.
  * **Mechanism:** Network Policies are enforced by the CNI plugin (e.g., Calico, Cilium, Weave Net). If your CNI plugin doesn't support Network Policies, the resource will exist but won't be enforced.
  * **Default Behavior:** By default, if no `NetworkPolicy` selects a Pod, all traffic to/from that Pod is allowed. Once a `NetworkPolicy` selects a Pod, only traffic explicitly allowed by that policy will pass.
  * **Use Case:** Implementing a "least privilege" network model, isolating sensitive applications, creating multi-tier application segmentation.

**Example: Allowing traffic only from frontend Pods to backend Pods:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: default
spec:
  podSelector: # This policy applies to pods with label app: backend
    matchLabels:
      app: backend
  policyTypes:
    - Ingress # This policy only applies to incoming traffic
  ingress:
    - from:
        - podSelector: # Allow incoming traffic from pods with label app: frontend
            matchLabels:
              app: frontend
      ports: # Allow traffic on specific ports
        - protocol: TCP
          port: 8080
```


## 💥 Lab Objective

* Create 3 pods: `pod1`, `pod2`, and `pod3`
* Apply a **NetworkPolicy** so that:

  * ✅ pod1 can talk to pod3
  * ✅ pod2 can talk to pod3
  * 🚫 pod1 and pod2 **cannot** talk to each other

---

## ⚙️ Prerequisites

* A working Kubernetes cluster (like `kind`, `minikube`, or cloud-based)
* `kubectl` installed and configured
* CNI plugin that supports NetworkPolicies (e.g., **Calico**, **Cilium**, **Weave Net**)

---

## 🧱 Step 1: Create the Pods

Let’s deploy three simple pods that run **busybox**, which can ping or curl others.

**File:** `pods.yaml`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod1
  labels:
    app: pod1
spec:
  containers:
  - name: pod1
    image: busybox
    command: ["sleep", "3600"]
---
apiVersion: v1
kind: Pod
metadata:
  name: pod2
  labels:
    app: pod2
spec:
  containers:
  - name: pod2
    image: busybox
    command: ["sleep", "3600"]
---
apiVersion: v1
kind: Pod
metadata:
  name: pod3
  labels:
    app: pod3
spec:
  containers:
  - name: pod3
    image: busybox
    command: ["sleep", "3600"]
```

Apply it:

```bash
kubectl apply -f pods.yaml
```

Verify:

```bash
kubectl get pods -o wide
```

---

## 🧠 Step 2: Test Communication (Before Policy)

Let’s test pod-to-pod connectivity before applying the NetworkPolicy.
All should be able to talk freely right now.

Get pod IPs:

```bash
kubectl get pods -o wide
```

Test from `pod1`:

```bash
kubectl exec -it pod1 -- ping <pod2-IP> -c 2
kubectl exec -it pod1 -- ping <pod3-IP> -c 2
```

Test from `pod2`:

```bash
kubectl exec -it pod2 -- ping <pod3-IP> -c 2
```

✅ You’ll see successful replies — all communication is open by default.

---

## 🚧 Step 3: Apply the NetworkPolicy

**File:** `networkpolicy.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-pod1-pod2-to-communicate-with-pod3
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: pod3
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: pod1
    - podSelector:
        matchLabels:
          app: pod2
```

Apply it:

```bash
kubectl apply -f networkpolicy.yaml
```

Check it’s active:

```bash
kubectl get networkpolicy
```

---

## 🧪 Step 4: Test Communication (After Policy)

Now that the policy is applied — time for the truth test 😏

### 1️⃣ pod1 → pod3 ✅ should work

```bash
kubectl exec -it pod1 -- ping <pod3-IP> -c 2
```

### 2️⃣ pod2 → pod3 ✅ should work

```bash
kubectl exec -it pod2 -- ping <pod3-IP> -c 2
```

### 3️⃣ pod1 → pod2 ❌ should fail

```bash
kubectl exec -it pod1 -- ping <pod2-IP> -c 2
```

You should see **no replies / 100% packet loss** — success!
That’s your NetworkPolicy doing its job.

---

## 🧹 Step 5: Cleanup (optional)

```bash
kubectl delete -f networkpolicy.yaml
kubectl delete -f pods.yaml
```

---

## 🧭 Summary

| Communication | Allowed | Reason                   |
| ------------- | ------- | ------------------------ |
| pod1 → pod3   | ✅       | Explicitly allowed       |
| pod2 → pod3   | ✅       | Explicitly allowed       |
| pod1 → pod2   | 🚫      | No policy rule allows it |




## Conclusion

Kubernetes networking is a powerful abstraction that allows your applications to behave as if they are running on a single, flat network, while transparently handling the complexities of underlying infrastructure, load balancing, and service discovery. By understanding the roles of the CNI plugin, Kube-Proxy, DNS, Services, Ingress, and Network Policies, along with the fundamental "Pod has its own IP" principle and where those IPs come from, you gain the ability to deploy robust, scalable, and secure applications in your cluster.

# KUBERNETES

<img src="https://github.com/bhuvan-raj/Kubernetes-Openshift-Zero-to-Hero/blob/main/Introduction%20to%20K8s/assets/k8s.gif" alt="Banner" />


## What Does "Kubernetes" Mean?

The word "Kubernetes" (pronounced koo-bur-NET-eez) is derived from Greek. It means **"helmsman"** or **"pilot"** – someone who steers a ship. This name perfectly reflects its role: Kubernetes steers and manages your containerized applications.

## How Did It Get the Name "K8s"?

You'll often see Kubernetes abbreviated as **K8s**. This is a numeronym (a number-based word abbreviation) where '8' stands for the eight letters between 'K' and 's' in "Kubernetes". It's a common practice in tech for long names (e.g., i18n for internationalization).

## Limitations of Standalone Containerization Tools

Before Kubernetes, deploying containerized applications typically involved managing them directly on individual servers using tools like the Docker CLI. While powerful for single instances, this approach quickly hits severe limitations:

  * **Scaling:** How do you run multiple copies of your application to handle increased load? Manually starting new containers on different machines is cumbersome.
  * **Load Balancing:** How do you distribute incoming traffic across multiple instances of your application?
  * **Self-Healing/High Availability:** What happens if a container crashes or the server it's on fails? Who restarts it? Who moves it to a healthy server?
  * **Service Discovery:** How do applications find and communicate with each other if their IPs change or new instances are added?
  * **Rolling Updates & Rollbacks:** How do you update your application to a new version without downtime? What if the new version breaks and you need to revert?
  * **Resource Management:** How do you ensure your applications get enough CPU and memory, and don't monopolize resources on a server?
  * **Configuration Management:** How do you manage configuration files, secrets (like database passwords), and environment variables consistently across many containers?
  * **Deployment Automation:** How do you automate the entire deployment process from code to running containers?

These challenges make managing complex, scalable, and resilient applications almost impossible without an orchestration layer.

## How Kubernetes Solves These Limitations

Kubernetes was designed by Google (based on their internal system called Borg) to tackle exactly these problems. It provides an automated platform that:

  * **Automates Scaling:** Easily scale your applications up or down by simply changing a number.
  * **Built-in Load Balancing:** Distributes network traffic efficiently across all healthy instances of your application.
  * **Self-Healing:** Automatically restarts failed containers, replaces unhealthy ones, and moves containers from failing nodes.
  * **Service Discovery:** Provides stable DNS names for your applications, allowing them to find each other regardless of where their individual instances are running.
  * **Automated Rollouts & Rollbacks:** Manages the rollout of new versions, allowing for zero-downtime updates and easy reversion if issues arise.
  * **Resource Management:** Allows you to define resource requests and limits for your containers, ensuring fair resource allocation.
  * **Centralized Configuration & Secret Management:** Provides secure ways to inject configuration data and sensitive information into your containers.
  * **Declarative Management:** You describe the desired state of your applications (e.g., "I want 3 instances of my web app running"), and Kubernetes works to maintain that state, continuously monitoring and correcting deviations.

## What is Kubernetes?

Kubernetes is an **open-source container orchestration platform** that automates the deployment, scaling, and management of containerized applications. It groups containers that make up an application into logical units for easy management and discovery.

It acts as an "operating system for your data center," abstracting away the underlying infrastructure and providing a consistent environment for your applications, no matter where they run (on-premises, public cloud, hybrid cloud).

## Why Kubernetes is Known as a Cluster Architecture

Kubernetes is fundamentally a **cluster architecture** because it operates across a collection of machines (physical or virtual) that work together as a single, unified computing resource. Instead of managing containers on individual servers, you manage them on the *cluster*.

This distributed nature is key to its power:

  * **High Availability:** If one machine in the cluster fails, Kubernetes can reschedule the affected containers onto healthy machines.
  * **Scalability:** You can easily add more machines (nodes) to the cluster to increase its overall computing capacity.
  * **Resource Pooling:** All the resources (CPU, RAM, storage) of the individual machines are pooled together and managed by Kubernetes, allowing for efficient allocation to applications.

## The Architecture of Kubernetes


<img src="https://github.com/bhuvan-raj/Kubernetes-Openshift-Zero-to-Hero/blob/main/Introduction%20to%20K8s/assets/k8s1.svg" alt="Banner" />


A Kubernetes cluster typically consists of two main types of nodes:

1.  **Control Plane (Master Node):** The "brain" of the cluster. It manages the worker nodes and the Pods running on them. There's usually at least one, but often multiple for high availability.
2.  **Worker Nodes:** The "workhorses" that run your containerized applications (Pods). Each cluster has at least one worker node.

<!-- end list -->

```
+-------------------------------------------------------+
|                 Kubernetes Cluster                    |
|                                                       |
|   +---------------------+       +-------------------+ |
|   |   Control Plane     |       |    Worker Node 1  | |
|   | (Master Node)       |       |                   | |
|   |---------------------|       |-------------------| |
|   | - API Server        |       | - Kubelet         | |
|   | - etcd              |       | - Kube-proxy      | |
|   | - Scheduler         |       | - Container       | |
|   | - Controller Manager|       |   Runtime (Docker)| |
|   +---------------------+       +-------------------+ |
|                                                       |
|   +---------------------+       +-------------------+ |
|   |   Worker Node N     |       |       ...         | |
|   |                     |       |                   | |
|   |---------------------|       |-------------------| |
|   | - Kubelet           |       |                   | |
|   | - Kube-proxy        |       |                   | |
|   | - Container         |       |                   | |
|   |   Runtime (Docker)  |       |                   | |
|   +---------------------+       +-------------------+ |
+-------------------------------------------------------+
```

## What are the Components in Kubernetes and Their Uses?

Let's break down the key components within the Control Plane and Worker Nodes:

### Control Plane Components (Master Node)

These components manage the cluster state and make global decisions.

  * **kube-apiserver (API Server):**
      * The **front-end** for the Kubernetes control plane.
      * Exposes the Kubernetes API, which is the central communication hub. All interactions (from `kubectl` to other components) go through the API Server.
      * Validates and configures data for API objects (Pods, Services, etc.).
  * **etcd:**
      * A highly available, distributed, consistent **key-value store**.
      * Kubernetes uses `etcd` to store all cluster data, including the desired state of your applications, configuration, and actual state.
      * It's the single source of truth for the cluster.
  * **kube-scheduler (Scheduler):**
      * Watches for newly created Pods with no assigned node.
      * Selects the **best node** for a Pod to run on, considering factors like resource requirements, hardware constraints, policy constraints, affinity, and anti-affinity specifications.
  * **kube-controller-manager (Controller Manager):**
      * Runs controller processes that regulate the state of the cluster.
      * Each controller (e.g., Node Controller, Replication Controller, Endpoints Controller, Service Account & Token Controllers) manages a specific resource type.
      * Its job is to bring the current state of the cluster closer to the desired state. For example, the Replication Controller ensures the correct number of Pods for a ReplicaSet are always running.

### Worker Node Components

These components run on each worker node and are responsible for maintaining running Pods and providing the Kubernetes runtime environment.

  * **kubelet:**
      * An agent that runs on each node in the cluster.
      * Ensures that containers are running in a Pod.
      * Receives Pod specifications from the API Server and ensures the containers described in those Pods are healthy and running.
      * Reports the status of the Pods and the node back to the API Server.
  * **kube-proxy:**
      * A network proxy that runs on each node.
      * Maintains network rules on nodes, allowing network communication to your Pods from inside or outside of the cluster.
      * Handles network proxying for Kubernetes Services, providing load balancing and service discovery.
  * **Container Runtime (e.g., Docker, containerd, CRI-O):**
      * The software responsible for running containers.
      * Kubernetes supports various container runtimes that implement the Kubernetes Container Runtime Interface (CRI).
      * It pulls container images from a registry, unpackages them, and runs them.


-----

## What is a Kubernetes Pod?

In Kubernetes, a **Pod** is the smallest and most fundamental deployable unit in the Kubernetes object model. It acts as a wrap around your container.

### Key characteristics of a Pod:

  * **One or More Containers:** A Pod can contain one or more tightly coupled containers that need to share resources and be co-located. The most common scenario is a single application container, but "sidecar" containers (e.g., for logging, monitoring, or data synchronization) are also common.
  * **Shared Resources:** All containers within a single Pod share the same network namespace, IP address, port space, and storage volumes. This allows them to communicate with each other using `localhost` and share data efficiently.
  * **Ephemeral:** Pods are designed to be relatively ephemeral. If a Pod dies (e.g., due to a node failure or application crash), Kubernetes will automatically create a *new* Pod to replace it, rather than trying to restart the old one.
  * **Atomic Unit:** Kubernetes schedules and manages Pods as a single, atomic unit. You don't deploy individual containers directly to Kubernetes; you deploy Pods.

-----

## Example: `nginx-pod.yml`


```yaml
# nginx-pod.yml
apiVersion: v1
kind: Pod
metadata:
  name: my-nginx-pod
  labels:
    app: nginx
    environment: development
spec:
  containers:
  - name: nginx-container
    image: nginx:latest
    ports:
    - containerPort: 80
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

-----

## Explanation of `nginx-pod.yml` Content

  * **`apiVersion: v1`**

      * Specifies the Kubernetes API version being used to create this object. For core Kubernetes objects like Pods, `v1` is the standard.

  * **`kind: Pod`**

      * Declares the type of Kubernetes object we are creating. In this case, it's a `Pod`.

  * **`metadata:`**

      * This section holds metadata about the Pod.
      * **`name: my-nginx-pod`**: A unique name for this Pod within its namespace. Kubernetes uses this name to identify and manage the Pod.
      * **`labels:`**:
          * Key-value pairs that are used to organize and select Kubernetes objects. They are crucial for grouping related resources (e.g., all Pods belonging to a specific application or environment).
          * `app: nginx`: Indicates that this Pod is part of the `nginx` application.
          * `environment: development`: Specifies the environment this Pod is intended for.

  * **`spec:`**

      * This section defines the desired state of the Pod, describing what should run inside it.
      * **`containers:`**:
          * A list of container definitions that will run within this Pod. Even for a single-container Pod, this is an array.
          * **`- name: nginx-container`**: A unique name for this specific container within the Pod.
          * **`image: nginx:latest`**: The Docker image to use for this container. `nginx:latest` tells Kubernetes to pull the latest version of the official Nginx image from Docker Hub.
          * **`ports:`**:
              * A list of ports that the container exposes. This is informational; it doesn't actually open the port on the node but declares which ports the application inside the container listens on.
              * **`- containerPort: 80`**: Declares that the Nginx container listens on port 80 (the default HTTP port).
          * **`resources:`**:
              * Defines the resource requests and limits for the container. This is crucial for Kubernetes to schedule the Pod effectively and for cluster stability.
              * **`requests:`**: The minimum amount of resources the container needs. Kubernetes guarantees these resources will be available when scheduling the Pod.
                  * `memory: "64Mi"`: Requests 64 mebibytes of memory.
                  * `cpu: "250m"`: Requests 250 millicores of CPU (i.e., 25% of a single CPU core).
              * **`limits:`**: The maximum amount of resources the container can consume. If a container tries to use more than its limit, it might be throttled or even terminated (e.g., an OOMKilled event for memory).
                  * `memory: "128Mi"`: Limits memory usage to 128 mebibytes.
                  * `cpu: "500m"`: Limits CPU usage to 500 millicores (i.e., 50% of a single CPU core).

-----

## What Happens When You Execute `kubectl apply -f nginx-pod.yml`?

When you run the command `kubectl apply -f nginx-pod.yml` (where `-f` specifies the file), the following sequence of events typically occurs:


## 1\. `kubectl`'s Initial Processing (Client-Side)

When you type `kubectl apply -f pod.yml`, your `kubectl` client begins the orchestration:

### 1.1 Reading the YAML File

  * `kubectl` first reads the `pod.yml` file from your local filesystem.
  * It parses the YAML content, understanding its hierarchical structure (`apiVersion`, `kind`, `metadata`, `spec`, etc.).

### 1.2 YAML to JSON Conversion

  * **Crucially, yes\!** While YAML is used for human readability, the Kubernetes API Server primarily communicates using **JSON (JavaScript Object Notation)**.
  * `kubectl` performs an **in-memory conversion** of the parsed YAML data into its equivalent JSON representation. This JSON payload is precisely what will be sent over the network to the API Server. This conversion is lossless.

### 1.3 Determining the API Endpoint and Request Type

  * `kubectl` uses the `kind` (`Pod`) and `apiVersion` (`v1`) specified in your YAML to identify the correct API endpoint. For a `Pod` of `apiVersion: v1`, the base endpoint is typically `/api/v1/namespaces/{namespace}/pods`.
  * Since `kubectl apply` is designed for **declarative management** (meaning "make the cluster state match this definition"):
      * `kubectl` first attempts to **read** the existing state of the resource. It sends a `GET` request to check if a Pod with the same name (e.g., `my-nginx-pod`) already exists in the target namespace (e.g., `default`).
      * Based on the `GET` request's response:
          * **If the Pod does NOT exist (HTTP 404 Not Found):** `kubectl` prepares an **HTTP `POST` request** to create the new Pod.
          * **If the Pod DOES exist (HTTP 200 OK):** `kubectl` calculates the **diff** (the differences) between the current state of the Pod on the cluster and the desired state from your `pod.yml`. It then prepares an **HTTP `PATCH` request** (specifically, a `strategic merge patch`) to update only the changed fields. This is the core of `kubectl apply`'s declarative update capability.

### 1.4 Authentication and Authorization Setup

  * `kubectl` uses the credentials defined in your `kubeconfig` file (usually `~/.kube/config`) to authenticate with the API Server. This often involves client certificates, bearer tokens, or cloud provider-specific authentication methods.
  * (Note: The actual authorization check is performed by the API Server itself).

-----

## 2\. The API Request (HTTP/HTTPS)

Let's assume the Pod does *not* exist and `kubectl` is sending a `POST` request to create it.

  * **Method:** `POST`

  * **URL:** `https://<KUBERNETES_API_SERVER_IP_OR_HOSTNAME>:<PORT>/api/v1/namespaces/default/pods`

      * (Assuming `default` namespace and standard API Server port, typically 6443)

  * **Key HTTP Headers:**

      * `Content-Type: application/json`
      * `Accept: application/json`
      * `Authorization: Bearer <your_bearer_token_or_client_cert_details>` (or other authentication headers)

  * **HTTP Body:** The JSON representation of your `pod.yml` content.

    ```json
    {
      "apiVersion": "v1",
      "kind": "Pod",
      "metadata": {
        "name": "my-nginx-pod",
        "labels": {
          "app": "nginx",
          "environment": "development"
        }
      },
      "spec": {
        "containers": [
          {
            "name": "nginx-container",
            "image": "nginx:latest",
            "ports": [
              {
                "containerPort": 80
              }
            ],
            "resources": {
              "requests": {
                "memory": "64Mi",
                "cpu": "250m"
              },
              "limits": {
                "memory": "128Mi",
                "cpu": "500m"
              }
            }
          }
        ]
      }
    }
    ```

-----

## 3\. API Server's Processing (Control Plane Interaction)

This is the central hub where Kubernetes' intelligence processes your request.

### 3.1 Request Reception and HTTPS Termination

  * The Kubernetes API Server, running securely over HTTPS, receives the incoming request. The TLS/SSL connection is terminated here.

### 3.2 Authentication and Authorization

  * The API Server first **authenticates** the identity of the requester (your `kubectl` user).
  * Then, it performs **authorization** using Role-Based Access Control (RBAC) policies. It checks if the authenticated user has the necessary permissions (e.g., `create` or `patch` verbs) for `pods` resources in the specified namespace. If not, the request is rejected with an HTTP `403 Forbidden` error.

### 3.3 Admission Controllers

  * Before the object is saved, a chain of **Admission Controllers** intercept the request. These are powerful plugins that can mutate (modify) or validate requests. Common examples include:
      * **`LimitRanger`:** Can inject default resource requests/limits if they are missing in your Pod definition.
      * **`ResourceQuota`:** Ensures that creating this Pod will not exceed any defined resource quotas for the namespace (e.g., maximum number of Pods, total CPU/memory usage).
      * **`PodSecurityAdmission` (PSA):** Enforces defined Pod Security Standards.
      * **Custom Admission Webhooks:** If configured, external webhooks can be called for more complex, custom validations or mutations (e.g., injecting sidecar containers automatically).
  * If any admission controller rejects the request, it fails at this stage.

### 3.4 Validation and Object Persistence (etcd)

  * The API Server performs thorough structural validation of the JSON payload against the Kubernetes schema for a Pod object.
  * If the request passes all validation and admission checks, the API Server **persists the desired state of the Pod object** into `etcd`. `etcd` is the highly available, distributed key-value store that acts as Kubernetes' single source of truth for all cluster configuration and state.
  * A unique `UID` (Universal Unique Identifier) is assigned to the new Pod object, and its initial `status.phase` is set to `Pending`.

### 3.5 API Server Response to `kubectl`

  * The API Server sends an HTTP `201 Created` (for a `POST`) or `200 OK` (for a `PATCH`) response back to your `kubectl` client. This response includes the full, created/updated Pod object definition, along with additional fields like `uid`, `creationTimestamp`, and initial `status`.
  * At this point, `kubectl` completes its execution and typically prints a confirmation message like "pod/my-nginx-pod created" or "pod/my-nginx-pod configured" to your terminal. **Crucially, the Pod object now exists in the desired state within Kubernetes, but it is not yet running on a node.**

-----

## 4\. Scheduler's Role (Control Plane Interaction)

Once the Pod object is persisted in `etcd`, the **Scheduler** takes over.

### 4.1 Watching for New Pods

  * The Kubernetes **Scheduler** is a core control plane component that continuously watches the API Server for newly created Pods that are in the `Pending` state and do not yet have a `nodeName` assigned (meaning they haven't been scheduled to a specific worker node).

### 4.2 Node Selection Algorithm

  * Upon detecting `my-nginx-pod`, the Scheduler executes its sophisticated algorithm to determine the *best* worker node in the cluster to run this Pod on. This process involves two main phases:
      * **Filtering (Predicates):** It eliminates nodes that do not meet the Pod's basic requirements. Examples of filters include:
          * **`PodFitsResources`:** Does the node have enough available CPU, memory, and other resources to satisfy the Pod's `requests`?
          * **`PodToleratesTaints`:** Can the Pod tolerate any taints present on the node?
          * **`NoDiskConflict`:** Are there any volume conflicts?
          * **`MatchNodeSelector`:** Does the node match any `nodeSelector` specified in the Pod's `spec`?
      * **Scoring (Priorities):** From the remaining, filtered nodes, the Scheduler assigns a score to each based on various factors to find the most suitable one. Examples of priorities include:
          * **`LeastRequestedPriority`:** Prefers nodes with less requested resources (to balance load).
          * **`BalancedResourceAllocation`:** Favors nodes where CPU and memory utilization are balanced.
          * **`NodeAffinity` / `PodAffinity` / `PodAntiAffinity`:** Respects rules about where Pods prefer/avoid to be scheduled relative to other Pods or nodes.

### 4.3 Binding the Pod to a Node

  * Once the Scheduler identifies the optimal node, it performs a **binding** operation. It makes a `PATCH` request to the API Server to update the `my-nginx-pod` object's `spec.nodeName` field with the name of the selected node.
  * This update is also persisted in `etcd`, marking the Pod as scheduled.

-----

## 5\. Kubelet's Role (Node-Level Execution)

The **Kubelet** is the agent that runs on each worker node and is responsible for making the Pod's desired state a reality on its assigned node.

### 5.1 Watching for Assigned Pods

  * The Kubelet continuously watches the API Server for Pods that have been assigned to *its* specific node (i.e., Pods whose `spec.nodeName` matches the Kubelet's own node name).
  * When it detects that `my-nginx-pod` has been assigned to its node, it initiates the process of running the Pod's containers.

### 5.2 Pod Container Orchestration

  * **Pod CGroup/Namespace Setup:** The Kubelet ensures that the necessary Linux Control Groups (cgroups) are created for the Pod (to enforce resource limits) and, crucially, that a new **network namespace** is established for the Pod. This provides the Pod with its own isolated network stack, including its own IP address and network interfaces.
  * **Image Pull:** It interacts with the **Container Runtime Interface (CRI)** (e.g., containerd, CRI-O, or Docker shim) to pull the `nginx:latest` Docker image from the configured container registry (like Docker Hub) if the image is not already cached locally on the node.
  * **CNI Plugin Invocation (Networking - The Real Work):**
      * The Kubelet does *not* directly configure network interfaces or IP addresses. Instead, it **invokes the configured Container Network Interface (CNI) plugin** (e.g., Calico, Flannel, Weave Net, Cilium) installed on the node.
      * The CNI plugin is the one responsible for:
          * **Assigning a unique IP address** to the Pod from the cluster's Pod CIDR range.
          * **Creating the virtual network interfaces** (e.g., `veth` pairs) that connect the Pod's network namespace to the node's main network stack.
          * **Configuring routing rules** on the node (and potentially across nodes, depending on the CNI solution) to enable communication between all Pods in the cluster.
  * **Volume Mounts (if any):** If the Pod defined any persistent or ephemeral volumes, the Kubelet prepares and mounts those volumes into the container's filesystem.
  * **Container Creation and Start:** The Kubelet instructs the container runtime to create and start the `nginx-container` process, injecting it into the Pod's prepared network namespace, resource cgroups, and mounted volumes.

### 5.3 Health Checks and Status Reporting

  * The Kubelet continuously monitors the health of the containers within the Pod (e.g., via Liveness probes to restart unhealthy containers, and Readiness probes to control traffic routing).
  * It periodically reports the Pod's current status (e.g., `ContainerCreating`, `Running`, `Ready`, `Failed`, `Succeeded`) and its assigned IP address back to the Kubernetes API Server. This status is updated in the `status` field of the Pod object in `etcd`.

-----

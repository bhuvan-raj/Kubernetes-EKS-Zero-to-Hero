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


<img src="https://github.com/bhuvan-raj/Kubernetes-Openshift-Zero-to-Hero/blob/main/Introduction%20to%20K8s/assets/k8s1.png" alt="Banner" />


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

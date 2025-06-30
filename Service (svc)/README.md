# Service in Kubernetes

<img src="https://github.com/bhuvan-raj/Kubernetes-Openshift-Zero-to-Hero/blob/main/Service%20(svc)/assets/service.gif" alt="Banner" />

## 1. Introduction

In the world of Kubernetes, applications are deployed as Pods. While Pods are excellent for running containers, they are inherently ephemeral and dynamic. Their IP addresses can change frequently due to scaling, rolling updates, crashes, or rescheduling. This presents a fundamental challenge: how do other parts of your application, or even external users, consistently find and communicate with these ever-changing Pods?

## 2. The Challenge: Ephemeral Pods

Consider a microservices architecture running in Kubernetes:

- Dynamic IPs: When a Pod is created, it's assigned a unique IP address. However, if that Pod dies or is replaced (e.g., during an update or scaling event), a new Pod with a new IP address takes its place.

- Load Balancing: If you have multiple replicas of a backend service (e.g., 3 API Pods), how do you distribute incoming requests evenly among them?

- Service Discovery: How does your frontend application know the current IP address of your backend API? Hardcoding IPs is not feasible in a dynamic environment.

## 3. What is a Kubernetes Service?

A Kubernetes Service is an abstraction that defines a logical set of Pods and a policy by which to access them. It provides a single, stable entry point (a virtual IP address and DNS name) for a group of Pods, regardless of their individual lifecycles.

Think of a Service as:

- A stable internal IP address and DNS name for a set of Pods.

- A load balancer that distributes traffic across those Pods.

- A service discovery mechanism for other applications within the cluster.

## 4. Core Functions and Benefits

Kubernetes Services serve several critical functions:

- Stable Network Identity: Provides a persistent IP address and DNS name for a logical application, even as the underlying Pods come and go. This is the cornerstone of reliable communication in Kubernetes.

- Load Balancing: Automatically distributes incoming network requests across all healthy Pods that are part of the Service. This ensures high availability and efficient resource utilization.

- Service Discovery: Enables other Pods and applications within the cluster to easily find and connect to your services using simple DNS names, rather than tracking individual Pod IPs.

## 5. How Services Work: The Core Mechanism

 **Selectors**

- At the heart of every Service definition is the selector field. This field specifies a set of labels that the Service uses to identify which Pods belong to it. When new Pods are created, or existing Pods are updated, Kubernetes continuously checks their labels. If a Pod's labels match the Service's selector, that Pod automatically becomes a backend for the Service.

Example:
If a Service has selector: { app: my-backend, tier: api }, it will only route traffic to Pods that have both the app: my-backend and tier: api labels.


**Endpoints Object**

- For every Service object that you create, Kubernetes automatically creates and maintains a corresponding Endpoints object. This Endpoints object is essentially a dynamic list of the actual IP addresses and ports of the healthy Pods that currently match the Service's selector.

- When Pods are added, removed, or their health status changes, the Kubernetes control plane updates the associated Endpoints object.

- This Endpoints object is what kube-proxy (and other components) refer to when routing traffic.

**Kube-Proxy: The Network Enforcer**

- kube-proxy is a network proxy that runs on each Node in your Kubernetes cluster. Its primary role is to implement the virtual IP (VIP) for Services.

- kube-proxy constantly watches the Kubernetes API server for changes to Service and Endpoints objects.

- When traffic destined for a Service's virtual IP (ClusterIP) arrives at a Node, kube-proxy's rules intercept it.

- These rules then perform Destination Network Address Translation (DNAT), rewriting the destination IP from the Service's ClusterIP to the actual IP address of one of the backend Pods listed in the Endpoints object.


7. Types of Kubernetes Services (Overview)

Kubernetes offers different Service types to cater to various exposure requirements. While all types provide stable IP/DNS and load balancing, they differ in how they make the application accessible:

- ClusterIP: The default type. Exposes the Service on a cluster-internal IP address. Only reachable from within the cluster. Ideal for internal communication between microservices.

- NodePort: Exposes the Service on a static port on each Node's IP address. This makes the Service accessible from outside the cluster via NodeIP:NodePort. Primarily used for development or when an external load balancer isn't available.

- LoadBalancer: Exposes the Service externally using a cloud provider's load balancer. This type is typically used in cloud environments (AWS, GCP, Azure, etc.) to provision a dedicated external IP and load balancer for your application.

- ExternalName: Maps the Service to an arbitrary external DNS name. No proxying is involved; it simply returns a CNAME record. Useful for accessing external services from within your cluster.


# 1.Cluster IP

The ClusterIP Service is the default and most fundamental Kubernetes Service type. It exposes a logical set of Pods on an internal IP address that is only reachable from within the Kubernetes cluster.

**Primary Purpose**

Its main role is to enable stable and reliable communication between different services or Pods inside the cluster. It acts as a single, consistent entry point for backend Pods, abstracting away their dynamic nature.

**Why it's the Default**

When you create a Service without explicitly specifying a type, Kubernetes automatically assigns it the ClusterIP type. This reflects its foundational role in building internal application architectures within Kubernetes.

## 2. Characteristics & Key Properties

**Internal Accessibility Only:**
 
- The ClusterIP is a virtual IP address that is part of a dedicated Service CIDR block within your cluster (e.g., 10.96.0.0/12).

- It is not routable from outside the cluster. Direct external access to a ClusterIP is impossible.

- This makes ClusterIP Services inherently secure for internal communications, as they are not exposed to the public internet unless explicitly combined with another exposure mechanism (like NodePort, LoadBalancer, or Ingress).


**Stable IP Address for Service Lifetime:**

- Unlike Pods, whose IPs are ephemeral, the ClusterIP assigned to a Service remains constant for the entire lifetime of that Service object.

- If the underlying Pods crash, are scaled, or replaced, the Service's ClusterIP does not change, providing a reliable target for clients.

**DNS Resolution within the Cluster:**

- Kubernetes' internal DNS service (kube-dns or CoreDNS) automatically creates DNS records for every Service.

- Pods within the same namespace can resolve the Service by its name (e.g., my-backend-service).

- Pods in other namespaces can resolve it using the format <service-name>.<namespace-name> (e.g., my-backend-service.default).

- The Fully Qualified Domain Name (FQDN) is <service-name>.<namespace-name>.svc.cluster.local. This DNS entry resolves to the Service's ClusterIP.


**Internal Load Balancing:**

- Traffic sent to the ClusterIP:ServicePort is automatically load-balanced across all healthy Pods selected by the Service.

- By default, kube-proxy typically uses a round-robin approach for distributing connections, but more advanced algorithms can be available in IPVS mode.

**Decoupling of Client from Pods:**

- Clients communicate with the stable ClusterIP and port of the Service, rather than directly with individual Pod IPs.

- This means clients don't need to know about the number of replicas, their health status, or their constantly changing IP addresses. Kubernetes handles the complexity of finding and routing to the correct backend Pod.

## How ClusterIP Works (Deep Dive into Mechanisms)

The magic of Kubernetes Services, including ClusterIP, is primarily orchestrated by two key components in the Kubernetes control plane and node agents:

**3.1. Role of kube-controller-manager**

- The kube-controller-manager runs various controllers, one of which is the service-controller.

- This controller continuously monitors the Kubernetes API server for Service and Pod changes.

- When a Service is created, updated, or when Pods matching a Service's selector come into existence, are terminated, or change their health status, the service-controller updates the corresponding Endpoints object for that Service.

- The Endpoints object is essentially a dynamic list of PodIP:ContainerPort pairs for all healthy Pods that currently back the Service.

**3.2. Role of kube-proxy**

- kube-proxy is a network proxy that runs on every Node in the Kubernetes cluster. It is the component responsible for implementing the Service's virtual IP (VIP) and routing traffic.

- Watches API Server: kube-proxy continuously watches the Kubernetes API server for Service and Endpoints object changes.

- Programs Network Rules: Based on the Services and their associated Endpoints, kube-proxy programs network rules on the Node's host operating system to facilitate the routing. The two main modes are iptables and IPVS.

**3.2.1. iptables Mode (Default and Most Common)**

- kube-proxy adds rules to the Linux kernel's iptables NAT table.

- Traffic Interception: When a packet destined for a Service's ClusterIP:ServicePort arrives at any Node in the cluster (even if the target Pod is on a different Node), iptables rules intercept it.

- Destination Network Address Translation (DNAT): The iptables rules perform DNAT, which means they rewrite the destination IP address of the incoming packet.

          The destination ClusterIP is changed to the IP address of a randomly selected backend Pod from the Service's Endpoints list.

          The destination ServicePort is changed to the targetPort of that chosen Pod.

- Load Balancing: iptables rules distribute connections among the backend Pods. This is typically a basic round-robin or random distribution for new connections.

**Workflow:**

        KUBE-SERVICES chain: All traffic hitting a Node first goes through this chain. Rules here identify traffic targeting any ClusterIP.

        KUBE-SVC-<hash> chain: For each Service, a dedicated chain redirects traffic from the ClusterIP to a specific KUBE-SEP-<hash> chain (Service Endpoint).

        KUBE-SEP-<hash> chain: Contains rules that perform the actual DNAT, rewriting the destination to a specific PodIP:ContainerPort. iptables has a mechanism to randomly select one of these SEP chains for load balancing.

**3.2.2.** IPVS Mode (IP Virtual Server)

- IPVS is a more advanced, high-performance load-balancing solution built into the Linux kernel (part of netfilter).

- Mechanism: When kube-proxy runs in IPVS mode, it uses netlink to program IPVS rules instead of iptables for Service load balancing. iptables is still used for other rules like Kube-Proxy itself, health checks, etc.

- Load Balancing Algorithms: IPVS supports a wider range of sophisticated load balancing algorithms, such as:

        Least Connections (lc)

        Round Robin (rr)

        Weighted Least Connections (wlc)

        Source Hashing (sh)

        Destination Hashing (dh)

- Performance: IPVS is generally more performant than iptables for high-traffic Services, as it uses hash tables for faster lookups and handles connection tracking more efficiently, especially with a large number of Services and Pods.

**Graceful Updates:** IPVS handles backend changes (Pod additions/removals) more smoothly, reducing the chance of connection drops during updates.

    Prerequisites: Requires the ipvs kernel modules to be loaded on the Node.

**3.3.** Endpoints Object: The Backend List

- The Endpoints object (kubectl get ep <service-name>) is a direct, concrete representation of the Pods that a Service is currently targeting.

- It contains the actual IP addresses and ports of the healthy Pods matching the Service's selector.

- Crucially, kube-proxy relies on this Endpoints object to know where to redirect traffic for the Service's ClusterIP.

  Example Endpoints output:
```
Name:         my-backend-service
Namespace:    default
Labels:       app=my-backend
Annotations:  <none>
Subsets:
  Addresses:  10.244.1.5,10.244.2.6  # IPs of the Pods
  NotReadyAddresses:  <none>
  Ports:        8080               # Port the Pod is listening on (targetPort)
```
**3.4. Service Discovery via DNS**

- The kube-dns or CoreDNS service (which typically runs as a Deployment/Pod within your cluster) is responsible for resolving Service names to their corresponding ClusterIPs.

- When a Pod makes a request to my-backend-service, the Pod's DNS resolver sends a query to kube-dns.

- kube-dns looks up the my-backend-service record and returns its ClusterIP.

- The requesting Pod then sends traffic to this resolved ClusterIP, and kube-proxy takes over for the actual routing and load balancing.
    


























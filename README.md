# Kubernetes-EKS-Openshift
<img src="https://github.com/bhuvan-raj/Kubernetes-Openshift-Zero-to-Hero/blob/main/assets/k8s.jpg" alt="Banner" />

This repository is a comprehensive learning resource for students and professionals learning Kubernetes.

---

## Repository Structure

This repository is meticulously organized into key sections, progressing from broader Kubernetes distributions to fundamental core concepts, detailed resource types, and advanced networking. Each top-level folder contains its own dedicated `README.md` file, providing in-depth explanations, examples, and usage instructions for the content within.

### 1. Kubernetes-Distributions
* **Description:** Dive into different Kubernetes distributions, with a particular focus on Amazon EKS (Elastic Kubernetes Service) and Red Hat OpenShift. This section explores how these managed services and platforms extend or implement Kubernetes.
* **Explore:** Navigate to [Kubernetes-Distributions](./Kubernetes-Distributions/) for detailed information.

### 2. Introduction to K8s
* **Description:** This section serves as a foundational guide to Kubernetes, covering its core concepts, architecture, and fundamental components. It's an ideal starting point for anyone new to Kubernetes.
* **Explore:** Navigate to [Introduction to K8s](./Introduction%20to%20K8s/) for detailed information.

### 3. Pods and Cluster Networking
* **Description:** This crucial section delves into Kubernetes Pods, the smallest deployable units, and how they interact within the cluster's internal network. It explains the core concepts of Pod networking and how Pods communicate.
* **Explore:** Navigate to [Pods and Cluster Networking](./Pods%20and%20Cluster%20Networking/) for detailed information.

### 4. Replicasets
* **Description:** This section focuses on ReplicaSets, the Kubernetes controller responsible for ensuring a specified number of identical Pod replicas are always running. It also introduces how ReplicaSets relate to Deployments and how they help achieve high availability and scalability.
* **Explore:** Navigate to [Replicasets](./Replicasets/)  for detailed information.

### 5. Deployments
* **Description:** This section focuses on Deployment, The object which helps in managing roll-out and roll-back for stateless applications
* **Explore:** Navigate to [Deployments](./Deployment/)  for detailed information.


### 6. Service (svc)
* **Description:** Understand how applications are made discoverable and accessible within the cluster, and the different ways to expose them for internal or controlled external access.
* **Explore:** Navigate to [Service (svc)](./Service%20(svc)/) for detailed information.

### 7. Namespace-Secrets-ConfigMaps
* **Description:** This folder focuses on crucial Kubernetes objects for organizing and configuring your applications within the cluster.
* **Explore:** Navigate to [Namespace-Secrets-ConfigMaps](./Namespace-Secrets-ConfigMaps/) for detailed information.

### 8. Ingress Resource
* **Description:** This section covers Kubernetes Ingress, the advanced mechanism for exposing HTTP and HTTPS services to the outside world with sophisticated routing, SSL/TLS termination, and host/path-based rules.
* **Explore:** Navigate to [Ingress Resource](./Ingress%20Resource/) for detailed information.

### 9. PV,PVC and Storageclass
* **Description:** This section covers PV and PVC, the mechanism for persistent storage and automatic provisioning of such persistent volumes.
* **Explore:** Navigate to [**PV and PVC**](./Persistant%20Volume%20and%20PVC/) for detailed information.

### 10. Resource Management and RequestQuota
* **Description:** This section covers Resource Management and ResourceQuota, the mechanism for limiting and controlling pod resource usage and the overall namespace resource allocation
* **Explore:** Navigate to [**Resource Management and ResourceQuota**](./Resource%20Management%20and%20Resource%20Quota/) for detailed information.

### 11. Node Selector and Node Affinity
* **Description:** These mechanisms empower you to control where your Pods run within your cluster, ensuring they land on nodes that meet specific requirements.
* **Explore:** Navigate to [**Node Selector and Node Affinity**](./Node%20Selector%20and%20Node%20Affinity/) for detailed information.


These mechanisms empower you to control where your Pods run within your cluster, ensuring they land on nodes that meet specific requirements.

---

## Getting Started

To explore the examples and concepts in this repository, you will need:

* A running Kubernetes cluster (e.g., Minikube, Kind, Docker Desktop with Kubernetes enabled, or a cloud-managed cluster like Amazon EKS).
* `kubectl` command-line tool configured to connect to your cluster.
* Specific tools for EKS or OpenShift if you plan to follow examples in the `Kubernetes-Distributions` folder (e.g., `aws cli`, `oc cli`).
* An Ingress Controller installed in your cluster (e.g., Nginx Ingress Controller) if you plan to work with the `Ingress Resource` examples.

Each sub-folder's `README.md` will provide specific instructions for deploying and interacting with its respective examples.

---

## Contributing

Contributions are welcome! If you have suggestions for improvements, new examples, or find any issues, please feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License. See the [License](./LICENSE) file for details.

---

## Contact

For any questions or feedback, feel free to reach out via GitHub Issues.

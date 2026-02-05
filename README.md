# Kubernetes-Zero-to-Hero
![Learning](https://img.shields.io/badge/Level-Beginner%20to%20Advanced-purple.svg)
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


### 6. Probes
* **Description:** Probes are health checks defined for containers within a Pod. The Kubelet uses these probes to determine the health and readiness of your application's containers, ensuring reliable operation.
* **Explore:** Navigate to [Probes](./Probes/)  for detailed information.


### 7. Service (svc)
* **Description:** Understand how applications are made discoverable and accessible within the cluster, and the different ways to expose them for internal or controlled external access.
* **Explore:** Navigate to [Service (svc)](./Service%20(svc)/) for detailed information.

### 8. Namespace-Secrets-ConfigMaps
* **Description:** This folder focuses on crucial Kubernetes objects for organizing and configuring your applications within the cluster.
* **Explore:** Navigate to [Namespace-Secrets-ConfigMaps](./Namespace-Secrets-ConfigMaps/) for detailed information.

### 9. Ingress Resource
* **Description:** This section covers Kubernetes Ingress, the advanced mechanism for exposing HTTP and HTTPS services to the outside world with sophisticated routing, SSL/TLS termination, and host/path-based rules.
* **Explore:** Navigate to [Ingress Resource](./Ingress%20Resource/) for detailed information.

### 10. PV,PVC and Storageclass
* **Description:** This section covers PV and PVC, the mechanism for persistent storage and automatic provisioning of such persistent volumes.
* **Explore:** Navigate to [**PV and PVC**](./Persistant%20Volume%20and%20PVC/) for detailed information.

### 11. Resource Management and ResourceQuota
* **Description:** This section covers Resource Management and ResourceQuota, the mechanism for limiting and controlling pod resource usage and the overall namespace resource allocation
* **Explore:** Navigate to [**Resource Management and ResourceQuota**](./Resource%20Management%20and%20Resource%20Quota/) for detailed information.

### 12. Node Selector ,Node Affinity and Node AntiAffinity
* **Description:** These mechanisms empower you to control where your Pods run within your cluster, ensuring they land on nodes that meet specific requirements.
* **Explore:** Navigate to [**Node Selector and Node Affinity**](./Node%20Selector%20and%20Node%20Affinity/) for detailed information.
*  **Explore:** Navigate to [**Node Anti-Affinity**](./Node%20Anti-Affinity/) for detailed information.

### 13. Taint and Tolerations
* **Description:** used for advanced controlling the nodes - placement of pods inside the nodes, ensuring they land on nodes that meet specific tolerations.
* **Explore:** Navigate to [**Taint and Tolerations**](./Taint%20and%20Tolerations/) for detailed information.

### 14. Horizontal Pod Autoscaler
* **Description:** used for scaling the pods horizontally whenever a certain threshold breaches, such as CPU , MEMMORY , REQUESTS etc.
* **Explore:** Navigate to [**HPA**](./HPA/) for detailed information.

### 15. Vertical Pod Autoscaler
* **Description:** used for scaling the pods vertically  whenever a certain threshold breaches, such as CPU , MEMMORY , REQUESTS etc.
* **Explore:** Navigate to [**VPA**](./VPA/) for detailed information.

### 16. Daemonsets
* **Description:** DaemonSets are a fundamental building block for a robust and observable Kubernetes cluster, ensuring that your essential background services are always running where they're needed.
* **Explore:** Navigate to [**Daemonsets**](./Daemonsets/) for detailed information.

### 17. Statefulsets
* **Description:** StatefulSets are used to manage stateful applications in Kubernetes. Unlike Deployments, they provide each pod with a unique, stable identity and persistent storage, ensuring ordered deployment, scaling, and deletion.
* **Explore:** Navigate to [**Statefulsets**](./Statefulsets/) for detailed information.


### 18. RBAC
* **Description:** RBAC in Kubernetes is a method for regulating access to computer or network resources based on the roles of individual users within an enterprise. It allows administrators to define who can perform what actions on which resources in a cluster, or within specific namespaces.
* **Explore:** Navigate to [**RBAC**](./RBAC/) for detailed information.

### 19. Admission Controller
* **Description:** Admission Controllers in Kubernetes are powerful components that intercept requests to the Kubernetes API server *after* authentication and authorization, but *before* the object is persisted in `etcd`. They act as "gatekeepers" to enforce policies and ensure that requests conform to specific rules, enhancing security, ensuring resource consistency, and automating configurations. 
* **Explore:** Navigate to [**Admission Controllers**](./Admission%20Controller/) for detailed information.


### 20. Jobs and Cronjobs
* **Description:** Kubernetes Jobs manage finite tasks that run to completion, ensuring a specified number of Pods successfully execute a task. CronJobs automate the creation of these Jobs on a recurring schedule, ideal for routine operations like backups or data cleanup within your cluster.
* **Explore:** Navigate to [**Jobs and CronJobs**](./Jobs%20and%20Cronjobs/) for detailed information.


### 21. HELM
* **Description:** Helm serves as the package manager for Kubernetes, simplifying the deployment and management of applications.
* **Explore:** Navigate to [**HELM**](./HELM/) for detailed information.




## EKS HANDS ON LABS INCLUDED 
- **This repository includes hands-on labs on previously completed topics using AWS EKS**
- **Explore:** Navigate to [**EKS HANDS ON**](./EKS%20HANDS-ON/) for detailed information.

    **LAB INDEX**


1. [**EKS-CLUSTER-SETUP**](./EKS%20HANDS-ON/EKS-CLUSTER-SETUP/)
2. [**EKS-NODEPORT**](./EKS%20HANDS-ON/EKS-Nodeport/)
3. [**EKS-CLASSICAL-LOADBALANCER-SERVICE**](./EKS%20HANDS-ON/Classical-LoadBalancer/)
4. [**EKS-NETWORK-LOADBALANCER-SERVICE**](./EKS%20HANDS-ON/Network-LoadBalancer/)
5. [**EKS-INGRESS-WITH-ALB**](./EKS%20HANDS-ON/INGRESS-ALB/)
6. [**EKS-STATEFULSET-WITH-DYNAMIC-PV&PVC**](./EKS%20HANDS-ON/Statefulset%20with%20Dynamic%20PV/)
7. [**EKS-HPA-WITH-TAINT&TOLERANCE**](./EKS%20HANDS-ON/HPA%20with%20Taint%20and%20Tolerance/)



---
## ARGOCD Integration with Kubernetes Cluster

<img src="https://github.com/bhuvan-raj/Kubernetes-EKS-FROM-SCRATCH/blob/main/assets/argo.png" width="200" height="150" alt="Banner" />

Argo CD integration with a Kubernetes cluster enables GitOps-based deployment, where applications are automatically synchronized from Git to the cluster, ensuring consistency and reliable continuous delivery.

**Checkout the Repo**
[**ArgoCD Zero to Hero**](https://github.com/bhuvan-raj/ArgoCD-Zero-to-Hero.git)



## MONITORING INTEGRATION WITH PROMETHEUS AND GRAFANA
<img src="https://github.com/bhuvan-raj/Kubernetes-EKS-FROM-SCRATCH/blob/main/assets/pg.png" width="400" height="150" alt="Banner" />

Implementing the advanced concept of monitoring through tools such as Prometheus and Building a custom dashboard using Grafana template for advanced visualisation

**Checkout the Repo**
[**Prometheus and Grafana**](https://github.com/bhuvan-raj/Prometheus-and-Grafana.git)

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

<img src="https://github.com/bhuvan-raj/Kubernetes-Openshift-Zero-to-Hero/blob/main/assets/k8s.jpg" alt="Banner" />

<div align="center">

![Learning](https://img.shields.io/badge/Level-Beginner%20to%20Advanced-purple?style=for-the-badge)
![Focus](https://img.shields.io/badge/Focus-DevOps-informational?style=for-the-badge)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![AWS EKS](https://img.shields.io/badge/AWS-EKS-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Helm](https://img.shields.io/badge/Helm-0F1689?style=for-the-badge&logo=helm&logoColor=white)
![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen?style=for-the-badge)
[![README Grammar Check](https://github.com/bhuvan-raj/Kubernetes-EKS-Zero-to-Hero/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/bhuvan-raj/Kubernetes-EKS-Zero-to-Hero/actions/workflows/main.yml)

# Kubernetes — Zero to Hero

### 🚀 A comprehensive, hands-on Kubernetes learning resource — from core concepts to production-grade EKS deployments.

</div>

---

## 📖 About This Repository

**Kubernetes Zero to Hero** is a structured, project-based learning repository designed to take you from knowing nothing about Kubernetes to confidently deploying, managing, and scaling containerized applications in real-world cluster environments.

Every section is organized into its own folder with a dedicated `README.md` containing in-depth explanations, YAML manifests, diagrams, and hands-on examples. The content progresses logically — from foundational concepts to advanced topics like RBAC, autoscaling, and GitOps.

By the end of this course, you will be able to:

- ✅ Understand Kubernetes architecture and core resource types
- ✅ Deploy and manage stateless and stateful applications
- ✅ Configure networking, ingress, and service discovery
- ✅ Manage persistent storage with PVs, PVCs, and StorageClasses
- ✅ Implement autoscaling, resource management, and pod scheduling policies
- ✅ Secure clusters using RBAC and Admission Controllers
- ✅ Run production workloads on AWS EKS
- ✅ Package and deploy applications with Helm

---

## 📚 Table of Contents

| # | Topic | Description |
|---|-------|-------------|
| 01 | [Kubernetes Distributions](./Kubernetes-Distributions/) | Deep dive into Amazon EKS and Red Hat OpenShift — managed Kubernetes platforms |
| 02 | [Introduction to K8s](./Introduction%20to%20K8s/) | Core concepts, architecture, and fundamental components — the ideal starting point |
| 03 | [Pods and Cluster Networking](./Pods%20and%20Cluster%20Networking/) | Pods as the smallest deployable unit, internal networking, and Pod communication |
| 04 | [ReplicaSets](./Replicasets/) | Ensuring a specified number of Pod replicas are always running — high availability basics |
| 05 | [Deployments](./Deployment/) | Managing rollouts and rollbacks for stateless applications |
| 06 | [Probes](./Probes/) | Liveness, readiness, and startup probes for container health checking |
| 07 | [Service (svc)](./Service%20(svc)/) | ClusterIP, NodePort, and LoadBalancer — making applications discoverable and accessible |
| 08 | [Namespace, Secrets & ConfigMaps](./Namespace-Secrets-ConfigMaps/) | Organizing workloads and managing application configuration and sensitive data |
| 09 | [Ingress Resource](./Ingress%20Resource/) | HTTP/HTTPS routing, SSL/TLS termination, and host/path-based traffic rules |
| 10 | [PV, PVC & StorageClass](./Persistant%20Volume%20and%20PVC/) | Persistent storage, volume claims, and dynamic provisioning |
| 11 | [Resource Management & ResourceQuota](./Resource%20Management%20and%20Resource%20Quota/) | Controlling pod resource usage and namespace-level allocation limits |
| 12 | [Node Selector & Node Affinity](./Node%20Selector%20and%20Node%20Affinity/) | Controlling where Pods are scheduled based on node labels and rules |
| 13 | [Node Anti-Affinity](./Node%20Anti-Affinity/) | Spreading Pods across nodes to avoid co-location and improve resilience |
| 14 | [Taints & Tolerations](./Taint%20and%20Tolerations/) | Advanced node-level access control — restricting which Pods can run on which nodes |
| 15 | [Horizontal Pod Autoscaler (HPA)](./HPA/) | Automatically scaling Pod count based on CPU, memory, or custom metrics |
| 16 | [Vertical Pod Autoscaler (VPA)](./VPA/) | Automatically adjusting container resource requests and limits based on usage |
| 17 | [DaemonSets](./Daemonsets/) | Ensuring a Pod runs on every node — ideal for logging, monitoring, and networking agents |
| 18 | [StatefulSets](./Statefulsets/) | Managing stateful applications with stable identities and persistent storage per Pod |
| 19 | [RBAC](./RBAC/) | Role-Based Access Control — defining who can perform what actions on which resources |
| 20 | [Admission Controllers](./Admission%20Controller/) | API server gatekeepers that enforce policies before objects are persisted |
| 21 | [Jobs & CronJobs](./Jobs%20and%20Cronjobs/) | Running finite tasks to completion and scheduling recurring workloads |
| 22 | [HELM](./HELM/) | Kubernetes package manager — templating, packaging, and managing application releases |

---

## 🧪 EKS Hands-On Labs

This repository includes **hands-on labs** that apply the concepts above using **AWS EKS** — a production-grade managed Kubernetes service.

| # | Lab | Description |
|---|-----|-------------|
| 01 | [EKS Cluster Setup](./EKS%20HANDS-ON/EKS-CLUSTER-SETUP/) | Provision and configure an EKS cluster from scratch |
| 02 | [EKS NodePort](./EKS%20HANDS-ON/EKS-Nodeport/) | Expose a service using NodePort on EKS worker nodes |
| 03 | [Classical Load Balancer](./EKS%20HANDS-ON/Classical-LoadBalancer/) | Attach an AWS Classic Load Balancer to a Kubernetes service |
| 04 | [Network Load Balancer](./EKS%20HANDS-ON/Network-LoadBalancer/) | High-performance L4 load balancing using AWS NLB |
| 05 | [Ingress with ALB](./EKS%20HANDS-ON/INGRESS-ALB/) | HTTP routing using AWS Application Load Balancer and Ingress |
| 06 | [StatefulSet with Dynamic PV & PVC](./EKS%20HANDS-ON/Statefulset%20with%20Dynamic%20PV/) | Dynamic storage provisioning for stateful applications on EKS |
| 07 | [HPA with Taint & Toleration](./EKS%20HANDS-ON/HPA%20with%20Taint%20and%20Tolerance/) | Combine horizontal autoscaling with advanced pod scheduling |

---

## 🔗 Related Repositories

### ArgoCD — GitOps for Kubernetes

<img src="https://github.com/bhuvan-raj/Kubernetes-EKS-FROM-SCRATCH/blob/main/assets/argo.png" width="120" alt="ArgoCD" />

Argo CD enables **GitOps-based deployment** — applications are automatically synchronized from Git to the cluster, ensuring consistency and reliable continuous delivery without manual `kubectl apply` steps.

📦 **[ArgoCD Zero to Hero →](https://github.com/bhuvan-raj/ArgoCD-Zero-to-Hero.git)**

---

### Prometheus & Grafana — Cluster Monitoring

<img src="https://github.com/bhuvan-raj/Kubernetes-EKS-FROM-SCRATCH/blob/main/assets/pg.png" width="220" alt="Prometheus Grafana" />

Learn how to implement **production-grade monitoring** using Prometheus for metrics collection and Grafana for custom dashboard visualization across your Kubernetes workloads.

📦 **[Prometheus and Grafana →](https://github.com/bhuvan-raj/Prometheus-and-Grafana.git)**

---

## 🛠️ Prerequisites

Before getting started, make sure you have the following:

| Tool | Purpose |
|------|---------|
| A running Kubernetes cluster | Minikube, Kind, Docker Desktop, or AWS EKS |
| `kubectl` | Command-line tool configured to connect to your cluster |
| `aws cli` + `eksctl` | Required for EKS hands-on labs |
| `helm` | Required for the HELM module |
| An Ingress Controller | e.g., Nginx Ingress Controller — required for Ingress examples |
| `oc` CLI | Required only for OpenShift examples in the Distributions section |

---

## 🚦 Getting Started

```bash
# Clone this repository
git clone https://github.com/bhuvan-raj/Kubernetes-Zero-to-Hero.git

# Navigate into the project
cd Kubernetes-Zero-to-Hero

# Start with the Introduction
cd "Introduction to K8s"
```

Each folder contains its own `README.md` with step-by-step instructions, YAML manifests, and explanations. Work through the topics in order for the best learning experience.

---

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements, new examples, or find any issues, feel free to open an issue or submit a pull request.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

<div align="center">

**Happy Orchestrating! ☸️**

*If this repo helped you, please consider giving it a ⭐*

</div>

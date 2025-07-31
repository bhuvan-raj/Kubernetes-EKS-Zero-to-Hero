# Kubernetes Admission Controllers: The Cluster Gatekeepers

<img src="https://github.com/bhuvan-raj/Kubernetes-Openshift-Zero-to-Hero/blob/main/Admission%20Controller/assets/ac.jpg" alt="Banner" />

## 🚀 Introduction

Welcome to the deep dive into **Kubernetes Admission Controllers**! In the realm of cloud-native security and policy enforcement, these controllers are arguably one of the most powerful, yet often misunderstood, components of the Kubernetes control plane.

You've already mastered **Role-Based Access Control (RBAC)**, which dictates *who* can do *what* in your cluster. Now, we're taking it a step further to understand *what actions are allowed*, regardless of user permissions, and *how objects behave* even before they are persisted. Admission Controllers act as the "gatekeepers" that ensure every operation aligns with your cluster's policies and security standards.

This module will equip you with a fundamental understanding of what Admission Controllers are, why they are essential, how they function, and how you can leverage them to build more secure and compliant Kubernetes environments.

---

## 🎯 Learning Objectives

By the end of this module, you should be able to:

* **Define** Kubernetes Admission Controllers and explain their core purpose.
* **Differentiate** Admission Controllers from Authentication and Authorization (RBAC).
* **Describe** the Admission Chain and where controllers fit in the API server's request lifecycle.
* **Identify** and explain the role of common built-in Admission Controllers.
* **Understand** the concept of Dynamic/Webhook Admission Controllers (Mutating and Validating).
* **Explain** the workflow of a Webhook Admission Controller, including `AdmissionReview` requests and responses.
* **List** common use cases for implementing Admission Controllers for security, policy enforcement, and automation.
* **Discuss** best practices for configuring and operating Admission Controllers, particularly webhooks.
* **Recognize** popular tools and frameworks that leverage Admission Controllers (e.g., OPA/Gatekeeper, Kyverno).

---

## 📅 Prerequisites

Before diving into this topic, ensure you have a solid understanding of:

* **Kubernetes Basics:** Pods, Deployments, Services, Namespaces, API Server.
* **Kubernetes API Objects:** How objects are defined in YAML and interacted with via `kubectl`.
* **Role-Based Access Control (RBAC):** Users, Service Accounts, Roles, ClusterRoles, RoleBindings, ClusterRoleBindings.
* **Basic Networking Concepts:** HTTP/HTTPS, TLS.

---

## 📖 Module Content

### 1. What are Admission Controllers?

Admission Controllers are pieces of code that **intercept requests to the Kubernetes API server** after authentication and authorization, but *before* the object is persisted in `etcd`. They act as policy enforcement points, allowing you to:

* **Validate** a request: Ensure the request adheres to predefined rules or policies. If not, the request is rejected.
* **Mutate** a request: Modify the request object before it is processed, such as injecting sidecar containers, adding labels, or setting default values.

They are a critical part of a robust Kubernetes security and policy enforcement strategy, complementing RBAC by providing a layer of control over *what* is created or modified.

### 2. Why are Admission Controllers Necessary?

While RBAC governs *who* can perform *what actions*, Admission Controllers enforce rules about *what resources look like* or *what policies apply to them*, regardless of the user's permissions. They address limitations of RBAC by:

* **Enforcing cluster-wide policies:** E.g., requiring all Pods to have resource limits, disallowing specific image registries.
* **Enhancing security:** Preventing the deployment of privileged containers or ensuring `securityContext` is applied.
* **Automating configuration:** Injecting sidecar containers for logging/service mesh, or adding default environment variables.
* **Ensuring resource consistency:** Validating custom resources (CRDs) against specific schemas or business logic.
* **Preventing misconfigurations:** Catching non-compliant or erroneous configurations early.

### 3. How Do They Work? (The Admission Chain)

When a request is sent to the Kubernetes API server, it undergoes a specific sequence:

1.  **Authentication:** Identifies the user or service account.
2.  **Authorization (RBAC):** Checks if the authenticated identity has permission to perform the requested action.
3.  **Admission Controllers:**
    * The request object is passed through a configured list of Admission Controllers.
    * **Mutating Controllers** run first: They can modify the request. Their order can be significant.
    * **Validating Controllers** run second: After all mutations, they perform final checks on the object.
    * **Crucial Point:** If *any* validating controller rejects the request, the entire operation is aborted, and the object is **not** persisted.
4.  **Object Persistence:** If all controllers approve, the object is stored in `etcd`.
5.  **Response:** The API server sends a response to the client.

### 4. Types of Admission Controllers

Kubernetes offers two main categories:

#### a) Built-in Admission Controllers

These are compiled directly into the `kube-apiserver` binary and are enabled/disabled via flags during API server startup. They handle fundamental cluster operations and security enforcements.

**Common Examples:**

* `NamespaceLifecycle`: Prevents operations in terminating namespaces; cleans up resources on namespace deletion.
* `LimitRanger`: Enforces resource quotas (CPU, memory) on Pods/containers based on `LimitRange` objects.
* `ServiceAccount`: Ensures Pods have a `ServiceAccount` and injects its credentials.
* `AlwaysPullImages`: Forces `imagePullPolicy: Always` for all Pods.
* `DenyEscalatingExec`: Prevents `exec`/`attach` to Pods if privilege escalation is possible.
* `NodeRestriction`: Limits `kubelet`'s ability to modify resources to its own node/Pods.
* `DefaultStorageClass`: Injects a default `StorageClass` into `PersistentVolumeClaim`s if none is specified.
* `PodSecurityPolicy` (⭐ **DEPRECATED in 1.25+**): Previously enforced security policies for Pods. Replaced by `PodSecurityAdmission`.
* `MutatingAdmissionWebhook` & `ValidatingAdmissionWebhook`: These are *meta-controllers* that enable the use of custom webhook controllers (explained next).

**Enabling:** Configured via the `--enable-admission-plugins` flag on the `kube-apiserver`.

#### b) Dynamic/Webhook Admission Controllers

These are the most powerful and flexible type, allowing you to implement **custom logic outside** the `kube-apiserver`. The API server sends an `AdmissionReview` request (a JSON representation of the object) to an HTTP webhook endpoint. The webhook processes it and returns an `AdmissionReview` response.

**Key Components:**

* **`MutatingWebhookConfiguration`**: Kubernetes API object that registers a custom mutating webhook. Defines rules (which resources/operations), endpoint, and failure policy.
* **`ValidatingWebhookConfiguration`**: Registers a custom validating webhook, similar to mutating.
* **Webhook Server**: An external service (typically a Pod in your cluster) that runs your custom logic and exposes an HTTPS endpoint.

**Workflow of a Webhook:**

1.  User sends request (`kubectl apply -f mypod.yaml`).
2.  API server performs AuthN/AuthZ.
3.  API server checks for matching `MutatingWebhookConfiguration`s.
4.  API server sends `AdmissionReview` request (via HTTPS) to the webhook server.
5.  Webhook server processes, potentially modifies, and sends `AdmissionReview` response (with an optional JSON patch).
6.  API server applies mutations, then checks for `ValidatingWebhookConfiguration`s.
7.  API server sends `AdmissionReview` request to validating webhook server.
8.  Validating webhook server processes and sends `AdmissionReview` response (`allowed: true/false`).
9.  If all pass, object is persisted in `etcd`. If any validation fails, the request is rejected.

**Advantages of Webhooks:**

* **Custom Logic:** Implement highly specific and complex policies.
* **Decoupled:** Develop, deploy, and scale webhook logic independently of the API server.
* **Language Agnostic:** Write webhooks in any language.
* **Dynamic Configuration:** Easily add/update policies without API server restarts.

**Challenges/Considerations for Webhooks:**

* **Performance:** Adds latency to API requests. Efficient webhook design is crucial.
* **Availability:** Webhook server uptime is critical (consider `failurePolicy`).
* **Security:** Webhooks have significant power; secure them with TLS.
* **Complexity:** Requires managing additional services.

### 5. Common Use Cases for Admission Controllers

* **Security Enforcement:**
    * Preventing privileged containers or host path mounts.
    * Restricting container image registries.
    * Enforcing `securityContext` settings (e.g., `runAsNonRoot`).
* **Policy Enforcement:**
    * Requiring CPU/memory limits and requests for all Pods.
    * Ensuring specific labels or annotations are present on resources (e.g., cost centers).
    * Enforcing naming conventions.
* **Automation & Injection:**
    * Injecting sidecar containers (e.g., Istio, Linkerd, logging agents like Fluent Bit).
    * Adding default environment variables or tolerations.
* **Resource Governance:**
    * Validating custom resources (CRDs) against specific business rules.

### 6. Configuration & Best Practices

#### a) Order of Controllers

* **Mutating before Validating:** All mutating webhooks run before any validating webhooks.
* **Built-in Order:** Built-in controller order is hardcoded. For webhooks, `reinvocationPolicy` and `sideEffects` can influence behavior.

#### b) Webhook Configuration Details

* **`clientConfig`**: How the API server connects to your webhook (e.g., `service` or `url`).
* **`rules`**: Defines which API operations (`CREATE`, `UPDATE`, `DELETE`, `CONNECT`) on which resources (`Pods`, `Deployments`, `Services`) trigger the webhook.
* **`namespaceSelector`**: Filters requests based on labels on the namespace containing the resource.
* **`objectSelector`**: Filters requests based on labels on the object itself (Kubernetes 1.15+).
* **`failurePolicy`**: What happens if the webhook fails or is unreachable.
    * `Fail` (Default, most secure): The API request is rejected.
    * `Ignore`: The API request proceeds. Use with caution for non-critical policies.
* **`sideEffects`**: Indicates if the webhook has external side effects. Important for `dry-run` requests.
    * `None`, `NoneOnDryRun`, `Some`.
* **`timeoutSeconds`**: Maximum time for the webhook to respond.

#### c) Security and Operations

* **TLS is Mandatory:** Webhook communication *must* use TLS. Provide CA bundles.
* **Resource Limits:** Set CPU/memory limits for webhook Pods.
* **High Availability (HA):** Deploy multiple replicas of your webhook server across nodes.
* **Health Checks:** Implement liveness and readiness probes.
* **Logging & Monitoring:** Crucial for debugging and performance analysis.
* **Thorough Testing:** Use `kubectl apply --dry-run=server` to test policies.
* **Namespace/Object Isolation:** Use selectors (`namespaceSelector`, `objectSelector`) to limit scope.
* **Minimize Logic:** Keep webhook logic efficient to reduce latency.
* **Idempotency:** Ensure mutations are idempotent.
* **Don't Block Critical Operations:** Be cautious with `failurePolicy: Fail` on controllers affecting core cluster functions.

### 7. Popular Tools Leveraging Admission Controllers

These tools often abstract away the direct webhook implementation, allowing you to define policies in a higher-level language:

* **Open Policy Agent (OPA) / Gatekeeper:**
    * OPA is a general-purpose policy engine.
    * Gatekeeper is a Kubernetes-native integration of OPA, allowing policies to be defined using **Rego language** and enforced as validating admission webhooks. Highly flexible for custom policies.
* **Kyverno:**
    * A policy engine designed specifically for Kubernetes.
    * Policies are defined as Kubernetes resources (YAML), making them intuitive for Kubernetes users.
    * Supports validation, mutation, and even generation of resources.
* **Pod Security Admission (PSA):**
    * A built-in admission controller (GA in Kubernetes 1.25) that supersedes `PodSecurityPolicy`.
    * Enforces Pod Security Standards (PSS) at the namespace level, providing a simplified approach to Pod security profiles.

---

## 👨‍🏫 How to Learn & Practice

1.  **Review the Concepts:** Go through each section of this README thoroughly.
2.  **Explore Built-in Controllers:**
    * Research specific built-in controllers (e.g., `LimitRanger`, `AlwaysPullImages`).
    * Experiment with creating `LimitRange` objects in a namespace to see `LimitRanger` in action.
3.  **Basic Webhook Setup (Hands-on):**
    * Follow a tutorial to deploy a simple "hello world" validating webhook. This will involve:
        * Creating a `Deployment` for your webhook server.
        * Creating a `Service` for the webhook server.
        * Generating TLS certificates (usually via `cert-manager` or `openssl`).
        * Creating a `ValidatingWebhookConfiguration` pointing to your service.
    * Test by creating a resource that triggers the webhook's validation logic.
4.  **Experiment with `kubectl --dry-run=server`:** Understand how dry-run works with admission controllers.
5.  **Explore Policy Engines:** Look into introductory tutorials for OPA/Gatekeeper or Kyverno. Understanding how these tools simplify policy management is crucial.

---

## 🔗 Further Reading

* **Kubernetes Official Documentation - Admission Controllers:** [https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/)
* **Kubernetes Official Documentation - Dynamic Admission Control:** [https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/](https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/)
* **Open Policy Agent (OPA) / Gatekeeper Documentation:** [https://openpolicyagent.org/docs/latest/](https://openpolicyagent.org/docs/latest/)
* **Kyverno Documentation:** [https://kyverno.io/docs/](https://kyverno.io/docs/)
* **Pod Security Standards:** [https://kubernetes.io/docs/concepts/security/pod-security-standards/](https://kubernetes.io/docs/concepts/security/pod-security-standards/)


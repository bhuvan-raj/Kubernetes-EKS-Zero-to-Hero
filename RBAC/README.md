# Kubernetes RBAC (Role-Based Access Control) - A Comprehensive Study Note

<img src="https://github.com/bhuvan-raj/Kubernetes-Openshift-Zero-to-Hero/blob/main/RBAC/assets/rbac.png" alt="Banner" />

## 1. Introduction to RBAC: Securing Your Kubernetes Cluster

**What is RBAC?**
**Role-Based Access Control (RBAC)** is the primary authorization mechanism in Kubernetes. It's a system for regulating access to computer or network resources based on the roles of individual users within an organization. In Kubernetes, RBAC ensures that human users, tools, and, critically, applications (running in pods) can only perform actions they are explicitly allowed to do.

**Why is RBAC Crucial for Kubernetes Security?**
Kubernetes clusters often host critical applications and sensitive data. Without robust access control, unauthorized or accidental actions can lead to:
* **Security Breaches:** Unauthorized access to sensitive information or control over infrastructure.
* **Accidental Misconfigurations:** Unintended deletion or modification of resources, leading to service outages.
* **Compliance Violations:** Failure to meet industry or regulatory standards for data access.

RBAC helps enforce the **Principle of Least Privilege**: grant only the minimum permissions necessary for a user or process to perform its required tasks.

**How RBAC Works at a High Level:**
When a request is made to the Kubernetes API Server (e.g., a user running `kubectl get pods` or an application making an API call), it goes through an authorization process:

1.  **Authentication:** The API Server first verifies the identity of the requester. "Who is making this request?"
2.  **Authorization (RBAC's Role):** Once authenticated, RBAC determines: "Is this identity allowed to perform *this specific action* on *this specific resource*?"
3.  **Admission Control:** Further policies or validations may be applied.

Our focus here is on the authorization phase, where RBAC acts as the gatekeeper.

---

## 2. Core RBAC API Objects: Defining Permissions ("What" & "Where")

RBAC in Kubernetes is implemented using a set of custom API objects that define permissions and bind them to identities.

### 2.1. `Role` (Namespaced Permissions)

A `Role` defines a set of permissions that are **scoped to a specific namespace**. It dictates what actions (`verbs`) can be performed on which resources *only within that particular namespace*.

* **Key Fields:**
    * `apiVersion: rbac.authorization.k8s.io/v1`
    * `kind: Role`
    * `metadata.name`: A unique name for the role (e.g., `pod-reader`).
    * `metadata.namespace`: **The namespace to which this Role applies.** (e.g., `development`).
    * `rules`: A list of permission sets. Each rule specifies:
        * `apiGroups`: The API group(s) the resources belong to.
            * `""` (empty string) for core resources (e.g., `Pods`, `Services`, `configmaps`, `secrets`,`namespaces`).
            * `apps` for `Deployments`, `StatefulSets`, `Replicaset`, `daemonset`.
            * `batch` for `Jobs`, `CronJobs`.
            * `*` for all API groups.
        * `resources`: The resource type(s) (e.g., `pods`, `deployments`, `secrets`, `*` for all resources in `apiGroups`).
        * `verbs`: The allowed actions (e.g., `get`, `list`, `watch`, `create`, `update`, `delete`, `patch`,`deletecollection`,`*` for all verbs).
        * `resourceNames`: (Optional) Restrict permission to specific named instances of a resource (e.g., `resourceNames: ["my-critical-secret"]`).

* **Example: `dev-pod-reader-role.yaml`**
    ```yaml
    apiVersion: rbac.authorization.k8s.io/v1
    kind: Role
    metadata:
      namespace: development # This Role is defined for the 'development' namespace
      name: pod-reader
    rules:
    - apiGroups: [""] # "" indicates the core API group
      resources: ["pods", "pods/log"] # Access to pods and their logs
      verbs: ["get", "watch", "list"]
    ```
    This `pod-reader` role, when bound to an identity within the `development` namespace, will only grant `get`, `watch`, and `list` permissions for pods and their logs *inside the `development` namespace*.

### 2.3. `ClusterRole` (Cluster-Scoped Permissions)

A `ClusterRole` is similar to a `Role` but defines permissions that are **cluster-scoped** (apply across all namespaces) or for cluster-scoped resources (like `Nodes`). It does **not** belong to a specific namespace.

* **Key Fields:**
    * `apiVersion: rbac.authorization.k8s.io/v1`
    * `kind: ClusterRole`
    * `metadata.name`: A unique name for the cluster role.
    * `rules`: Same structure as `Role` rules.

* **Use Cases for `ClusterRole`:**
    * Granting permissions to resources that are not namespaced (e.g., `nodes`, `persistentvolumes`, `storageclasses`).
    * Granting permissions to namespaced resources *across all namespaces* (e.g., allowing a user to `list` all `pods` in *any* namespace).
    * Defining common roles that can be used in multiple namespaces via `RoleBinding` (acting as a template).

* **Example: `node-reader-clusterrole.yaml`**
    ```yaml
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRole
    metadata:
      name: node-reader # No namespace defined, it's cluster-scoped
    rules:
    - apiGroups: [""]
      resources: ["nodes"]
      verbs: ["get", "watch", "list"]
    ```
    This `node-reader` `ClusterRole` allows reading `Node` objects, which are cluster-scoped resources.

* **Example: `global-pod-reader-clusterrole.yaml` (Template Role)**
    ```yaml
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRole
    metadata:
      name: global-pod-reader
    rules:
    - apiGroups: [""]
      resources: ["pods"]
      verbs: ["get", "watch", "list"]
    ```
    This `ClusterRole`, when bound using a `RoleBinding` within a specific namespace, would grant read access to pods *only in that namespace*. If bound using a `ClusterRoleBinding`, it would grant read access to pods *across all namespaces*.

---

## 3. Subjects in RBAC: The Identities ("Who")

RBAC policies apply to **subjects**, which are the identities requesting to perform actions. There are three types of subjects:

### 3.1. `User` (Human Users)

* Represents an individual human user.
* Kubernetes itself does **not** have a built-in "User" object. User identities are typically managed externally by your cluster's authentication system (e.g., an OpenID Connect (OIDC) provider like Google/Okta, X.509 client certificates, or even static password files).
* When a request is authenticated, the user's name (e.g., `alice@example.com`) is identified. This name is then used in `RoleBinding` or `ClusterRoleBinding`.

### 3.2. `Group` (Collections of Human Users)

* Represents a collection of `User`s.
* Similar to `User`s, `Group` memberships are usually managed by your external authentication system.
* Granting permissions to a `Group` simplifies management, as all members of that group inherit the assigned permissions.

### 3.3. `ServiceAccount` (The "Who" for Applications/Processes)

This is a critical concept for automated tasks and applications running within your cluster.

* **What it is:** A `ServiceAccount` is a **Kubernetes API object** that provides an **identity for processes that run in a Pod**. Think of it as an identity for your applications, not for human users.
* **How it's Managed:** `ServiceAccount`s are managed directly by Kubernetes (i.e., you define them via YAML and `kubectl`).
* **Default Behavior:** Every namespace automatically gets a `default` `ServiceAccount`. If you don't explicitly assign a `ServiceAccount` to a pod, it will use the `default` one from its namespace.
* **Authentication Mechanism:** When a pod starts using a `ServiceAccount`, Kubernetes automatically injects a **secret containing a token** into the pod's filesystem (usually at `/var/run/secrets/kubernetes.io/serviceaccount/`). Applications within the pod use this token to authenticate themselves to the Kubernetes API server.
* **Purpose:** `ServiceAccount`s enable your applications to interact securely with the Kubernetes API to perform tasks like:
    * Listing other pods (e.g., for service discovery).
    * Updating a Deployment's status.
    * Creating/deleting temporary resources (e.g., Jobs).
    * Reading ConfigMaps or Secrets that they need to operate.

* **Example: `my-app-sa.yaml`**
    ```yaml
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: my-app-deployer-sa
      namespace: production # Service Accounts are namespaced
    ```
    This creates an identity for an application that will run in the `production` namespace.

**Key Distinction: Authentication vs. Authorization (for Service Accounts)**

* **Service Account = Authentication:** The `ServiceAccount` object, along with its mounted token, provides the **identity** for an application. It answers the question: "Who am I when talking to the Kubernetes API?"
* **RBAC = Authorization:** Once the `ServiceAccount`'s identity is authenticated, RBAC determines **what that identity is allowed to do**. It answers the question: "Given my identity, what actions am I *authorized* to perform?"

---

## 4. Binding RBAC Objects to Subjects: Connecting "Who" to "What/Where"

Once you have defined permissions in `Roles` or `ClusterRoles`, and you have your subjects (`User`s, `Group`s, `ServiceAccount`s), you need to "bind" them together.

### 4.1. `RoleBinding` (Namespaced Association)

A `RoleBinding` grants the permissions defined in a `Role` (or a `ClusterRole`!) to a **subject** within a **specific namespace**.

* **Key Fields:**
    * `apiVersion: rbac.authorization.k8s.io/v1`
    * `kind: RoleBinding`
    * `metadata.name`: Unique name for the binding.
    * `metadata.namespace`: **The namespace where this binding is effective.**
    * `subjects`: List of subjects (User, Group, ServiceAccount).
        * `kind`: `User`, `Group`, or `ServiceAccount`.
        * `name`: The name of the subject.
        * `namespace`: (Required for `ServiceAccount` kind) The namespace of the Service Account.
    * `roleRef`: Reference to the Role or ClusterRole being bound.
        * `kind`: `Role` or `ClusterRole`.
        * `name`: Name of the Role or ClusterRole.
        * `apiGroup`: `rbac.authorization.k8s.io`

* **Example: Binding a `Role` to a `User` in a Namespace (`user-role-binding.yaml`)**
    ```yaml
    apiVersion: rbac.authorization.k8s.io/v1
    kind: RoleBinding
    metadata:
      name: alice-reader-in-dev
      namespace: development # This binding only applies in 'development'
    subjects:
    - kind: User
      name: alice # User 'alice' (identified by authenticator)
      apiGroup: rbac.authorization.k8s.io
    roleRef:
      kind: Role # Binding to a local Role
      name: pod-reader # From the example above
      apiGroup: rbac.authorization.k8s.io
    ```
    User `alice` can now only `get`, `watch`, `list` pods within the `development` namespace.

* **Example: Binding a `ClusterRole` to a `ServiceAccount` in a Namespace (`sa-role-binding.yaml`)**
    ```yaml
    apiVersion: rbac.authorization.k8s.io/v1
    kind: RoleBinding
    metadata:
      name: deployer-access-in-prod
      namespace: production # This binding applies only in 'production'
    subjects:
    - kind: ServiceAccount
      name: my-app-deployer-sa # The Service Account we created
      namespace: production # The Service Account's namespace
    roleRef:
      kind: ClusterRole # IMPORTANT: Binding a ClusterRole here
      name: edit # Using Kubernetes' built-in 'edit' ClusterRole
      apiGroup: rbac.authorization.k8s.io
    ```
    The `my-app-deployer-sa` Service Account (from `production` namespace) now has `edit` permissions *only within the `production` namespace*. This demonstrates using a `ClusterRole` as a template via a `RoleBinding`.

### 4.2. `ClusterRoleBinding` (Cluster-Scoped Association)

A `ClusterRoleBinding` grants the permissions defined in a `ClusterRole` to a subject (user, group, or service account) across the **entire cluster**.

* **Key Fields:**
    * `apiVersion: rbac.authorization.k8s.io/v1`
    * `kind: ClusterRoleBinding`
    * `metadata.name`: Unique name for the binding.
    * `subjects`: List of subjects.
    * `roleRef`: Reference to the `ClusterRole` being bound (`kind` must be `ClusterRole`).

* **Example: Binding a `ClusterRole` to a `Group` (`group-cluster-role-binding.yaml`)**
    ```yaml
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRoleBinding
    metadata:
      name: cluster-managers-nodes
    subjects:
    - kind: Group
      name: cluster-admins-group # Group 'cluster-admins-group'
      apiGroup: rbac.authorization.k8s.io
    roleRef:
      kind: ClusterRole # Must be ClusterRole
      name: node-reader # Our 'node-reader' ClusterRole from above
      apiGroup: rbac.authorization.k8s.io
    ```
    Any member of the `cluster-admins-group` can now read all `Nodes` in the entire cluster.

* **Example: Binding a `ClusterRole` to a `ServiceAccount` Globally (`global-sa-cluster-role-binding.yaml`)**
    ```yaml
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRoleBinding
    metadata:
      name: global-monitoring-sa
    subjects:
    - kind: ServiceAccount
      name: prometheus-sa # A Service Account for Prometheus
      namespace: monitoring # The SA's namespace
    roleRef:
      kind: ClusterRole
      name: view # Using built-in 'view' ClusterRole
      apiGroup: rbac.authorization.k8s.io
    ```
    The `prometheus-sa` from the `monitoring` namespace can now *view* (read-only) most resources across *all* namespaces in the cluster.

---

## 5. How RBAC Authorizes a Request: The Decision Process

When an API request arrives (e.g., `kubectl get pods -n myapp` or an application's API call), the Kubernetes API server's authorization module evaluates it against all relevant RBAC policies.

The core of the authorization logic relies on matching the request's components with rules defined in your `Roles`/`ClusterRoles`:

1.  **`Verb`**: The action being attempted (e.g., `get`, `list`, `watch`, `create`, `update`, `delete`).
2.  **`Resource`**: The type of Kubernetes object being acted upon (e.g., `pods`, `deployments`, `secrets`, `nodes`). Can also include sub-resources like `pods/log` or `deployments/scale`.
3.  **`apiGroup`**: The API group the resource belongs to (e.g., `""` for core, `apps`, `batch`, `rbac.authorization.k8s.io`).

**The Authorization Logic:**

* The system identifies the authenticated `subject` (User, Group, or Service Account) making the request.
* It then collects all `RoleBinding`s and `ClusterRoleBinding`s that apply to this subject.
* For each applicable binding, it retrieves the associated `Role` or `ClusterRole`.
* Finally, it iterates through the `rules` defined within those roles. **If even a single rule across all applicable roles matches the requested `(verb, resource, apiGroup)` combination, the request is AUTHORIZED.**
* If no matching rule is found after checking all relevant roles, the request is **DENIED** (Forbidden).

**Key Principle: RBAC is Additive**
If a subject is bound to multiple roles (or multiple bindings point to the same subject), their effective permissions are the **union** of all permissions granted by those roles. There are **no "deny" rules** in Kubernetes RBAC; only explicit grants.

---

## 6. Built-in ClusterRoles

Kubernetes provides a set of predefined `ClusterRole`s for common use cases. These can be very useful starting points:

* **`cluster-admin`**: Grants super-user access; perform any action on any resource. **Use with extreme caution!**
* **`admin`**: Full access within a namespace, including the ability to grant `edit` and `view` roles to others. Does not allow managing quotas or the namespace itself.
* **`edit`**: Allows read/write access to most namespaced objects (e.g., Deployments, Services, ConfigMaps). Does not allow viewing or modifying RBAC objects themselves (Roles/RoleBindings/ClusterRoles/ClusterRoleBindings) or Secrets.
* **`view`**: Allows read-only access to most namespaced objects. Cannot view Secrets, RoleBindings, or modify any resources.
* **System Groups**:
    * `system:authenticated`: A special `Group` that includes all successfully authenticated users.
    * `system:unauthenticated`: A special `Group` that includes all unauthenticated requests.
    * `system:serviceaccounts`: A special `Group` that includes all ServiceAccounts in the cluster.
* Many other `system:` prefixed roles exist for internal Kubernetes components (e.g., `system:kube-scheduler`, `system:node`). **Do not modify these system roles.**

You can inspect these built-in roles using `kubectl get clusterroles`.

---
# Lab

## 🎯 Lab Objective

Demonstrate how **RBAC restricts access** in Kubernetes using:

* Namespace
* ServiceAccount
* Role
* RoleBinding
  …and validate permissions using a Pod.

---

## 🧪 Lab Scenario

* Create a namespace: `rbac-lab`
* Create a ServiceAccount: `pod-reader-sa`
* Allow **read-only access to Pods**
* Verify access **from inside a Pod**
* Prove **denied access** for other resources

---

## 🧱 Step 1: Create Namespace

```bash
kubectl create namespace rbac-lab
```

---

## 🧱 Step 2: Create ServiceAccount

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: pod-reader-sa
  namespace: rbac-lab
```

```bash
kubectl apply -f serviceaccount.yaml
```

---

## 🧱 Step 3: Create Role (Read Pods Only)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: rbac-lab
  name: pod-reader-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
```

```bash
kubectl apply -f role.yaml
```

---

## 🧱 Step 4: Bind Role to ServiceAccount

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: pod-reader-binding
  namespace: rbac-lab
subjects:
- kind: ServiceAccount
  name: pod-reader-sa
  namespace: rbac-lab
roleRef:
  kind: Role
  name: pod-reader-role
  apiGroup: rbac.authorization.k8s.io
```

```bash
kubectl apply -f rolebinding.yaml
```

---

## 🧱 Step 5: Create Test Pod Using ServiceAccount

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
  namespace: rbac-lab
spec:
  serviceAccountName: pod-reader-sa
  containers:
  - name: kubectl
    image: bitnami/kubectl
    command: ["sleep", "3600"]
```

```bash
kubectl apply -f pod.yaml
```

---

## 🧪 Step 6: Verify Access (Inside Pod)

```bash
kubectl exec -n rbac-lab -it test-pod -- /bin/sh
```

### ✅ Allowed

```bash
kubectl get pods -n rbac-lab
```

### ❌ Denied

```bash
kubectl get secrets -n rbac-lab
```

Expected error:

```
Error from server (Forbidden): secrets is forbidden
```

---

## 🧠 Key Learning Points

* **ServiceAccount** provides identity to Pods
* **Role** defines *what* actions are allowed
* **RoleBinding** defines *who* gets those permissions
* RBAC is **namespace-scoped** here
* kind fully supports RBAC without extra configuration

---

## 💡 Interview One-Liner

> “In Kubernetes, RBAC permissions are granted to ServiceAccounts using Roles and RoleBindings. Pods inherit permissions through the ServiceAccount they run with.”






### Best Practices:

1.  **Principle of Least Privilege:** This is the golden rule. Grant only the absolute minimum permissions required.
2.  **Use Namespaced `Roles` for Applications:** Most applications only need permissions within their own namespace. Define a `Role` for these, and bind it to a dedicated `ServiceAccount` using a `RoleBinding` in the same namespace.
3.  **Dedicated `ServiceAccount` per Application/Microservice:** Avoid using the `default` `ServiceAccount` for your applications. Create a unique `ServiceAccount` for each distinct application or component. This allows for granular permission control and easier auditing.
4.  **Limit `ClusterRoleBinding` Usage:** Reserve `ClusterRoleBinding`s for truly cluster-wide administrative roles (e.g., cluster operators, security auditing tools, cluster-wide monitoring).
5.  **Leverage Built-in `ClusterRoles`:** Start with `view`, `edit`, `admin` `ClusterRole`s and bind them with `RoleBinding`s to grant standard permissions within a namespace. Extend them using aggregation if necessary.
6.  **Use `Groups` for Human Users:** Manage human users in groups (via your external authentication system). Bind these groups to RBAC policies. This simplifies management greatly compared to managing individual user bindings.
7.  **Version Control All RBAC Manifests:** Store your `Role`, `ClusterRole`, `RoleBinding`, `ClusterRoleBinding`, and `ServiceAccount` definitions in Git. This enables auditing, simplifies rollbacks, and promotes collaborative management.
8.  **Regular Auditing:** Periodically review your RBAC policies to ensure they are still appropriate and not overly permissive as your cluster evolves.
9.  **Use `kubectl auth can-i` Extensively:** This command is invaluable for debugging and verifying RBAC policies *from the perspective of a specific subject*.
      * `kubectl auth can-i get pods --as=user:alice -n dev`
      * `kubectl auth can-i create deployment --as=system:serviceaccount:prod:jenkins-deployer-sa -n prod`
      * `kubectl auth can-i list nodes --as-group=cluster-admins-group`
10. **Test in Non-Production:** Always thoroughly test your RBAC configurations in development or staging environments before deploying them to production clusters.

-----


## 📚 Table of Contents

1. [Understanding Kubernetes Namespaces: Logical Isolation and Organization](#understanding-kubernetes-namespaces-logical-isolation-and-organization)

   * [What is a Kubernetes Namespace?](#what-is-a-kubernetes-namespace)
   * [Why Use Namespaces?](#why-use-namespaces-core-problems-they-solve)
   * [Key Characteristics and Properties](#key-characteristics-and-properties)
   * [Common Use Cases for Namespaces](#common-use-cases-for-namespaces)
   * [Working with Namespaces (Basic Commands)](#working-with-namespaces-basic-commands)
   * [Best Practices for Namespaces](#best-practices-for-namespaces)

2. [ConfigMaps and Secrets](#configmaps-and-secrets)

   * [1. Introduction: Why Externalize Configuration?](#1-introduction-why-externalize-configuration)
   * [2. Kubernetes ConfigMaps](#2-kubernetes-configmaps)

     * [What is a ConfigMap?](#what-is-a-configmap)
     * [When to Use ConfigMaps](#when-to-use-configmaps)
     * [Creating a ConfigMap](#creating-a-configmap)
     * [Consuming a ConfigMap in Pods](#consuming-a-configmap-in-pods)
     * [Updating ConfigMaps](#updating-configmaps)
     * [ConfigMap Best Practices](#configmap-best-practices)
   * [3. Kubernetes Secrets](#3-kubernetes-secrets)

     * [What is a Secret?](#what-is-a-secret)
     * [When to Use Secrets](#when-to-use-secrets)
     * [Understanding Secret Security](#understanding-secret-security)
     * [Different Types of Secrets](#different-types-of-secrets)
     * [Creating a Secret](#creating-a-secret)
     * [Consuming a Secret in Pods](#consuming-a-secret-in-pods)
     * [Updating Secrets](#updating-secrets)
     * [Secret Security Best Practices](#secret-security-best-practices-critical)
   * [4. ConfigMaps vs. Secrets: Key Differences](#4-configmaps-vs-secrets-key-differences)
   * [5. Further Learning](#5-further-learning)


# Understanding Kubernetes Namespaces: Logical Isolation and Organization

<img src="https://github.com/bhuvan-raj/Kubernetes-Openshift-Zero-to-Hero/blob/main/Namespace-Secrets-ConfigMaps/assets/ns.png" alt="Banner" />


As your Kubernetes clusters grow, hosting more applications, teams, or environments, managing all those resources (Pods, Deployments, Services, etc.) can become chaotic. Imagine a giant shared folder on a computer where everyone just dumps their files – finding anything specific, avoiding name clashes, or setting permissions becomes a nightmare.

This is exactly the problem **Namespaces** solve in Kubernetes. They provide a mechanism for **logical isolation** within a single Kubernetes cluster. Think of a Namespace as a **virtual sub-cluster** or a dedicated "room" within your larger Kubernetes "building."

## What is a Kubernetes Namespace?

A **Namespace** in Kubernetes is a way to **divide cluster resources into logically isolated groups.** It provides a scope for names. Names of resources within a Namespace must be unique, but identical names can exist in different Namespaces.

  * **Analogy:**
      * A Kubernetes Cluster is like a **large apartment building**.
      * Each **Namespace** is like a **separate apartment/unit** within that building.
      * Resources (Pods, Deployments, Services) are like the **furniture and appliances** inside an apartment.
      * You can have a "bed" in Apartment A and another "bed" in Apartment B without them conflicting, but you can't have two "beds" with the exact same name *within* Apartment A.

## Why Use Namespaces? (Core Problems They Solve)

Namespaces are not about network isolation (that's handled by Network Policies). They are primarily about:

1.  **Resource Isolation / Preventing Naming Collisions:**

      * Imagine two different teams deploying a `database` service. Without namespaces, they'd clash. With namespaces, Team A can have `database` in `namespace-team-a` and Team B can have `database` in `namespace-team-b`.
      * This is crucial for shared clusters.

2.  **Access Control (RBAC - Role-Based Access Control):**

      * Namespaces are the most common scope for applying RBAC policies.
      * You can grant a user or a service account permissions (e.g., "developer," "admin") *only within a specific Namespace*. This means a developer for the "dev" namespace won't accidentally (or maliciously) modify resources in the "prod" namespace.

3.  **Resource Quotas:**

      * You can set **Resource Quotas** on a Namespace to limit the total amount of CPU, memory, storage, or even the number of objects (e.g., maximum 20 Pods) that can be consumed within that Namespace.
      * This helps prevent one team or application from monopolizing cluster resources and impacting others.

4.  **Logical Grouping & Organization:**

      * Namespaces provide a clean way to group related resources together.
      * For example, all components of a single application, all services belonging to a specific team, or all resources for a particular environment (dev, staging, production) can reside in their own Namespace. This makes management, monitoring, and troubleshooting much easier.

## Key Characteristics and Properties

  * **Namespace-Scoped vs. Cluster-Scoped Objects:**
      * Most Kubernetes objects (Pods, Deployments, Services, ConfigMaps, Secrets, ReplicaSets, StatefulSets, DaemonSets) are **namespace-scoped**. They exist *within* a specific Namespace.
      * Some objects (Nodes, PersistentVolumes, StorageClasses, ClusterRoles, ClusterRoleBindings, Namespaces themselves) are **cluster-scoped**. They are not part of any Namespace and affect the entire cluster.
  * **The `default` Namespace:**
      * Every Kubernetes cluster comes with a pre-created `default` Namespace.
      * If you don't specify a Namespace when creating a resource, it will be placed in the `default` Namespace.
      * **Best Practice:** While convenient for simple testing, avoid deploying production applications to the `default` Namespace. Always create dedicated Namespaces for your applications and environments.
  * **DNS Resolution:**
      * Services within the *same* Namespace can be reached using their short name (e.g., `my-service`).
      * Services in *other* Namespaces can be reached using their fully qualified domain name (FQDN), which includes the Namespace: `my-service.other-namespace.svc.cluster.local` (or often just `my-service.other-namespace`).
  * **Resource Sharing:** While Namespaces isolate resources logically, the underlying compute resources (CPU, Memory, Storage) are still shared from the cluster's pool unless explicitly limited by Resource Quotas.

## Common Use Cases for Namespaces

1.  **Multi-Tenant Environments:**
      * If you have a large cluster shared by multiple independent teams or departments. Each team gets its own Namespace(s) to manage their applications without interfering with others.
2.  **Environment Separation:**
      * Having separate Namespaces for different environments of the *same* application (e.g., `my-app-dev`, `my-app-staging`, `my-app-prod`). This ensures that development work doesn't impact production and allows for consistent deployments across stages.
3.  **Application Separation:**
      * Even for a single team, separating different applications into their own Namespaces (e.g., `ecommerce-frontend`, `payment-service`, `user-auth`) can improve organization and simplify management.
4.  **Team-Based Isolation:**
      * Giving each development team its own Namespace(s) and allowing them to manage resources within their scope.

## Working with Namespaces (Basic Commands)

### 1\. List Namespaces

```bash
kubectl get namespaces
```
 or
```
kubectl get ns
```

**Example Output:**

```
NAME              STATUS   AGE
default           Active   3d
kube-system       Active   3d
kube-public       Active   3d
kube-node-lease   Active   3d
my-app-dev        Active   1h
my-app-prod       Active   1h
```

### 2\. Create a Namespace

```bash
kubectl create namespace my-new-app
```

### 3\. Deploy Resources to a Specific Namespace

**Option A: Specify in the YAML manifest:**

```yaml
# my-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-web-app
  namespace: my-new-app # Explicitly define the namespace here
spec:
  replicas: 2
  selector:
    matchLabels:
      app: my-web-app
  template:
    metadata:
      labels:
        app: my-web-app
    spec:
      containers:
      - name: web
        image: nginx
        ports:
        - containerPort: 80
```

```bash
kubectl apply -f my-deployment.yaml
```

**Option B: Specify on the command line:**

```bash
kubectl apply -f my-deployment.yaml -n my-new-app
```
or using the full form
```
kubectl apply -f my-deployment.yaml --namespace=my-new-app
```

### 4\. View Resources within a Namespace

```bash
kubectl get pods --namespace=my-new-app
```
 or shorthand
```
kubectl get pods -n my-new-app
```

To see resources across *all* namespaces (for cluster-wide objects or administrative overview):

```bash
kubectl get all --all-namespaces
```
# or
```
kubectl get pods --all-namespaces
```

### 5\. Switch Your Current Context (for repeated commands)

To avoid typing `-n <namespace>` repeatedly, you can change your active namespace for your current `kubectl` context:

```bash
kubectl config set-context --current --namespace=my-new-app
```

Now, any `kubectl` command you run (e.g., `kubectl get pods`) will default to `my-new-app` unless you explicitly specify another namespace.

### 6\. Delete a Namespace (and all its contents\!)

**Warning: Deleting a Namespace will delete ALL resources (Pods, Deployments, Services, etc.) within that Namespace.** Use with extreme caution.

```bash
kubectl delete namespace my-new-app
```

## Best Practices for Namespaces

  * **Always Create Dedicated Namespaces:** Never deploy your primary applications or services into the `default` namespace.
  * **Meaningful Naming:** Give your namespaces clear, descriptive names (e.g., `my-app-prod`, `dev-team-a`, `data-services`).
  * **Leverage RBAC:** Use namespaces as the primary scope for defining who can do what in your cluster.
  * **Implement Resource Quotas:** Prevent resource hogging by setting limits on CPU, memory, and object counts per namespace.
  * **Avoid Over-Segmentation:** Don't create too many tiny namespaces that become hard to manage. Find a balance that makes sense for your organization and application architecture.

Namespaces are a fundamental concept for organizing your Kubernetes cluster effectively. Mastering them is essential for building scalable, secure, and manageable containerized applications.

---
# ConfigMaps and Secrets

<img src="https://github.com/bhuvan-raj/Kubernetes-Openshift-Zero-to-Hero/blob/main/Namespace-Secrets-ConfigMaps/assets/k8s1.png" alt="Banner" />


## 1\. Introduction: Why Externalize Configuration?

In containerized applications, especially in a microservices architecture, it's crucial to separate configuration data from application code and container images. Hardcoding configuration leads to:

  * **Lack of Portability:** Images become environment-specific.
  * **Difficult Updates:** Any config change requires a new build and deploy.
  * **Security Risks:** Sensitive data can be exposed.

Kubernetes addresses this by providing **ConfigMaps** for non-sensitive data and **Secrets** for sensitive data, allowing you to inject configuration into your Pods at runtime.

-----

## 2\. Kubernetes ConfigMaps

<img src="https://github.com/bhuvan-raj/Kubernetes-Openshift-Zero-to-Hero/blob/main/Namespace-Secrets-ConfigMaps/assets/k8s.jpg" alt="Banner" />


### What is a ConfigMap?

A ConfigMap is a Kubernetes object used to store **non-sensitive configuration data** as key-value pairs.

  * **Purpose:** Store general application settings, environment-specific values, or entire configuration files.
  * **Storage:** Data is stored in plain text in `etcd` (Kubernetes' backing store).
  * **Characteristics:** Plain text, key-value pairs, easily consumed by Pods.

### When to Use ConfigMaps

  * **Environment Variables:** `API_URL`, `LOG_LEVEL`, `DEBUG_MODE`.
  * **Application Settings:** Database connection strings (non-sensitive parts), feature flags.
  * **Configuration Files:** `nginx.conf`, `application.properties`, `log4j.xml`.

### Creating a ConfigMap

You can create ConfigMaps using `kubectl` from literals, files, or, ideally, declaratively using YAML.

**1. From Literal Values:**

```bash
kubectl create configmap my-app-config \
  --from-literal=APP_ENV=production \
  --from-literal=MAX_CONNECTIONS=100
```

**2. From a File:**
(Assumes `config/app.conf` exists)

```bash
kubectl create configmap app-conf --from-file=config/app.conf
```

**3. Using a YAML Manifest (Recommended):**

```yaml
# my-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-app-config
data:
  # Key-value pairs
  APP_MESSAGE: "Welcome to production!"
  # Multi-line data (e.g., a config file)
  server.properties: |
    server.port=8080
    database.url=jdbc:mysql://prod-db:3306/appdb
```

```bash
kubectl apply -f my-configmap.yaml
```

### Consuming a ConfigMap in Pods

ConfigMaps can be consumed in two primary ways:

**1. As Environment Variables:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: env-config-pod
spec:
  containers:
  - name: my-container
    image: busybox
    command: ["sh", "-c", "echo App message: $APP_MSG"]
    env:
    - name: APP_MSG
      valueFrom:
        configMapKeyRef:
          name: my-app-config # Name of the ConfigMap
          key: APP_MESSAGE   # Key from the ConfigMap
    envFrom: # Inject all key-value pairs as environment variables
    - configMapRef:
        name: my-app-config
```

**2. As Mounted Volumes (Files):**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: volume-config-pod
spec:
  containers:
  - name: my-container
    image: nginx:alpine
    volumeMounts:
    - name: config-volume
      mountPath: /etc/nginx/conf.d # Directory where files will be mounted
      readOnly: true
  volumes:
  - name: config-volume
    configMap:
      name: my-app-config # ConfigMap containing 'server.properties' etc.
      items: # Optional: selectively mount specific keys as files
      - key: server.properties
        path: custom-server.conf # Mount 'server.properties' as 'custom-server.conf'
```

  * Files will appear at `/etc/nginx/conf.d/custom-server.conf` inside the container.

### Updating ConfigMaps

  * **Environment Variables:** Pods **do not** automatically update environment variables when the ConfigMap changes. You must restart or redeploy the Pods.
  * **Mounted Volumes:** Files in mounted volumes **are updated automatically** by Kubelet (typically within 60 seconds). Applications can monitor these files for dynamic updates. For robust updates, a rolling update of the Deployment is often recommended.

To update, `kubectl edit configmap <name>` or `kubectl apply -f <your-configmap.yaml>`.

### ConfigMap Best Practices

  * **Version Control:** Store ConfigMap YAMLs in Git.
  * **Immutability:** For critical, unchanging configs, use `immutable: true` (Kubernetes 1.18+).
  * **Size Limits:** Be aware of the 1MB size limit per ConfigMap.
  * **Organize:** Group related data logically.

-----

## 3\. Kubernetes Secrets

<img src="https://github.com/bhuvan-raj/Kubernetes-Openshift-Zero-to-Hero/blob/main/Namespace-Secrets-ConfigMaps/assets/secrets.png" alt="Banner" />


### What is a Secret?

A Secret is a Kubernetes object specifically designed to store and manage **sensitive information**.

  * **Purpose:** Store passwords, API keys, OAuth tokens, TLS certificates, SSH keys.
  * **Encoding:** Data is **base64-encoded** for transport/storage. **This is NOT encryption.**
  * **Encryption at Rest:** For true security, the underlying `etcd` database of your Kubernetes cluster **MUST have encryption at rest enabled**.
  * **Access Control:** Access to Secrets should be strictly controlled via RBAC.

### When to Use Secrets

Any time you have data that, if exposed, could lead to a security breach.

  * Database passwords.
  * External API keys.
  * TLS/SSL certificates and private keys.
  * SSH private keys.

### Understanding Secret Security

It's critical to understand that **base64 encoding is not encryption**. Anyone with read access to a Secret can easily decode its contents. The true security of Secrets relies on:

1.  **Encryption at Rest for `etcd`:** This encrypts the data before it's written to Kubernetes' database. Your cluster administrator or cloud provider must enable this.
2.  **Strict RBAC:** Limit who can read, create, or modify Secrets.

## Different types of secrets

- Opaque (default) - eneric key-value pairs (base64 encoded)
- kubernetes.io/dockerconfigjson - Used to authenticate with private container registries (like Docker Hub, ECR, etc).
  Stores a .docker/config.json file.
```
  type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: <base64>
```
Used with imagePullSecrets in Pod specs.

- kubernetes.io/basic-auth
  Stores a username and password pair
  Useful for basic HTTP authentication.
```
  type: kubernetes.io/basic-auth
data:
  username: <base64>
  password: <base64>
```
- kubernetes.io/ssh-auth
  Stores an SSH private key
```
  type: kubernetes.io/ssh-auth
data:
  ssh-privatekey: <base64>
```
- kubernetes.io/tls
  Used for TLS certificates and keys
```
  type: kubernetes.io/tls
data:
  tls.crt: <base64>
  tls.key: <base64>
```


### Creating a Secret

`kubectl` handles base64 encoding automatically for `--from-literal` and `--from-file`. When defining in YAML, use `stringData` for plain text values; Kubernetes will encode them.

**1. From Literal Values:**

This flag is used to directly specify key-value pairs inline.

```bash
kubectl create secret generic my-db-secret \
  --from-literal=username=appuser \
  --from-literal=password='S3cur3P@ssw0rd!'
```

**2. From a File:**

This flag is used to load values from files (or multiple files). The file content becomes the value, and the filename becomes the key (unless otherwise specified).

(Assumes `credentials/api_key.txt` exists)

```bash
kubectl create secret generic api-key-secret --from-file=credentials/api_key.txt
```

**3. Using a YAML Manifest (Recommended):**

```yaml
# my-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-app-secret
type: Opaque # Default type, for general-purpose secrets
stringData: # Use this for plain text; Kubernetes will base64 encode
  DB_USERNAME: "prod_user"
  DB_PASSWORD: "Sup3rS3cr3t!"
  API_TOKEN: "sk_live_xyz_123abc"
```

```bash
kubectl apply -f my-secret.yaml
```

### Consuming a Secret in Pods

Secrets are consumed similarly to ConfigMaps:

**1. As Environment Variables:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: env-secret-pod
spec:
  containers:
  - name: my-secure-container
    image: my-app-image
    env:
    - name: DB_USER
      valueFrom:
        secretKeyRef:
          name: my-app-secret
          key: DB_USERNAME
    - name: DB_PASS
      valueFrom:
        secretKeyRef:
          name: my-app-secret
          key: DB_PASSWORD
```

**2. As Mounted Volumes (Files - Recommended for Secrets):**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: volume-secret-pod
spec:
  containers:
  - name: my-secure-container
    image: my-app-image
    volumeMounts:
    - name: secret-volume
      mountPath: "/etc/app-secrets" # Directory where secret files will appear
      readOnly: true # Always mount secrets as read-only!
  volumes:
  - name: secret-volume
    secret:
      secretName: my-app-secret
      # Optional: set defaultMode for file permissions (e.g., 0400 for read-only by owner)
      defaultMode: 0400
```

  * Files like `/etc/app-secrets/DB_USERNAME` and `/etc/app-secrets/DB_PASSWORD` will exist inside the container.

### Updating Secrets

  * **Environment Variables:** Pods **do not** automatically update environment variables. Requires a Pod restart/rolling update.
  * **Mounted Volumes:** Files in mounted volumes **are updated automatically** by Kubelet. However, for most applications, a rolling update is the safest way to ensure all instances pick up the new Secret.

To update, `kubectl edit secret <name>` or `kubectl apply -f <your-secret.yaml>`.

### Secret Security Best Practices (CRITICAL)

1.  **Enable `etcd` Encryption at Rest:** This is the most crucial step for securing your Secrets. Consult your Kubernetes distribution or cloud provider documentation.
2.  **Strict RBAC:** Limit `get`, `list`, `watch` permissions on Secrets to only the ServiceAccounts and users that absolutely need them.
3.  **Use Volume Mounts over Environment Variables:** Secrets mounted as files are generally more secure, as they are not easily discoverable via `ps` commands or process introspection, and their permissions can be controlled.
4.  **Read-Only Mounts:** Always mount Secret volumes with `readOnly: true`.
5.  **Audit Logs:** Monitor Kubernetes audit logs for Secret access.
6.  **Secret Rotation:** Implement a strategy for regularly rotating (changing) sensitive credentials.
7.  **External Secret Management:** For advanced needs (e.g., centralized management, automatic rotation, stricter access), consider integrating with solutions like HashiCorp Vault, cloud provider secret managers (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager), or the External Secrets Operator.
8.  **Avoid Hardcoding:** Never hardcode secrets in code, Dockerfiles, or unencrypted YAMLs.
9.  **Immutable Secrets:** Consider `immutable: true` for Secrets that should not be changed after creation (Kubernetes 1.18+).

-----

## 4\. ConfigMaps vs. Secrets: Key Differences

| Feature             | ConfigMap                                       | Secret                                                      |
| :------------------ | :---------------------------------------------- | :---------------------------------------------------------- |
| **Purpose** | Non-sensitive configuration data.               | Sensitive data (passwords, keys, certs).                    |
| **Data Encoding** | Plain text.                                     | Base64 encoded (obfuscation, NOT encryption).               |
| **Encryption** | No built-in encryption.                         | Requires `etcd` encryption at rest for true security.       |
| **Access Control** | Standard RBAC.                                  | Critical to apply strict RBAC for restricted access.        |
| **Visibility** | Easily readable in plain text via `kubectl get`. | Base64-encoded via `kubectl get`, requires decoding.        |
| **Use Cases** | Environment variables, URLs, feature flags, config files. | Passwords, API keys, TLS certs, SSH keys, registry credentials. |

-----

## 5\. Further Learning

  * [Kubernetes Documentation: ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)
  * [Kubernetes Documentation: Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
  * [Kubernetes Documentation: Encryption at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
  * [Kubernetes Documentation: RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

-----

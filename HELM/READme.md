# Helm in Kubernetes - In-Depth Study Note

## 🛠️ What is Helm?

**Helm** is a **package manager for Kubernetes**, similar to `apt` for Debian or `yum` for CentOS. It helps you **define, install, and manage Kubernetes applications** using charts (pre-configured Kubernetes resources).

---

## 📦 Why Use Helm?

### ✅ Key Benefits:

* **Templating**: Write reusable and configurable manifests.
* **Versioning**: Helm charts can be version-controlled.
* **Lifecycle management**: Install, upgrade, rollback, and uninstall with ease.
* **Configuration**: Override values at install time.
* **Sharing**: Use public or private chart repositories.

---

## 📁 Helm Components

### 1. **Chart**

A **chart** is a package of pre-configured Kubernetes resources.

**Structure of a Helm Chart:**

```
mychart/
├── Chart.yaml          # Chart metadata
├── values.yaml         # Default configuration values
├── charts/             # Dependencies
├── templates/          # Kubernetes manifest templates
│   └── deployment.yaml
│   └── service.yaml
├── .helmignore         # Patterns to ignore when packaging
```

### 2. **Chart.yaml**

Defines metadata:

```yaml
apiVersion: v2
name: mychart
description: A sample Helm chart
version: 0.1.0
appVersion: "1.0"
```

### 3. **values.yaml**

Contains default values that can be overridden:

```yaml
replicaCount: 2
image:
  repository: nginx
  tag: stable
```

### 4. **templates/**

Templates use Go templating syntax and generate Kubernetes manifests dynamically:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: {{ .Release.Name }}-pod
spec:
  containers:
    - name: app
      image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
```

---

## 🌀 Helm Release Lifecycle

Helm maintains state about every installation called a **release**.

### Lifecycle Steps:

1. **helm install**: Deploys the chart as a release.
2. **helm upgrade**: Modifies existing release with new values or chart version.
3. **helm rollback**: Reverts to an earlier version.
4. **helm uninstall**: Deletes a release but keeps history (optional).
5. **helm history**: Shows the deployment timeline of a release.

---

## ⚙️ Helm Commands

| Command                              | Purpose                         |
| ------------------------------------ | ------------------------------- |
| `helm create <name>`                 | Scaffold a new chart            |
| `helm install <release> <chart>`     | Install a chart                 |
| `helm upgrade <release> <chart>`     | Upgrade a release               |
| `helm rollback <release> <revision>` | Roll back to a previous version |
| `helm uninstall <release>`           | Remove a release                |
| `helm list`                          | List installed releases         |
| `helm repo add <name> <url>`         | Add a chart repository          |
| `helm repo update`                   | Update chart repositories       |
| `helm search repo <chart>`           | Search for charts               |
| `helm template`                      | Render templates locally        |
| `helm lint`                          | Check chart for issues          |

---

## 🧹 Helm Values and Overrides

### Default (`values.yaml`)

```yaml
image:
  repository: nginx
  tag: latest
```

### Override at install:

```sh
helm install myapp ./mychart --set image.tag=1.21
```

### Using custom values file:

```sh
helm install myapp ./mychart -f prod-values.yaml
```

---

## 🏗️ Helm Dependency Management

Helm allows charts to depend on other charts.

### Declare in `Chart.yaml`:

```yaml
dependencies:
  - name: redis
    version: 10.5.7
    repository: https://charts.bitnami.com/bitnami
```

Then run:

```sh
helm dependency update
```

---

## 🛡️ Helm Security Considerations

* **RBAC**: Limit Helm Tiller (if using Helm v2) or use scoped permissions in Helm v3.
* **Chart validation**: Use `helm lint` to validate charts.
* **Audit**: Review third-party charts before use.

---

## 🔁 Helm v2 vs v3

| Feature     | Helm v2            | Helm v3                 |
| ----------- | ------------------ | ----------------------- |
| Tiller      | Required           | Removed                 |
| Security    | Weaker             | More secure (no Tiller) |
| CRDs        | Managed externally | Built-in CRD management |
| OCI Support | ❌                  | ✅ Supported             |

> ✅ **Always use Helm v3** (latest as of 2025).

---

## 🛠️ Use Cases

* **Install third-party apps**: NGINX Ingress, Prometheus, MySQL, etc.
* **Deploy your own app**: Package internal apps with configurable templates.
* **Environment-based deployments**: Dev/staging/prod with separate `values.yaml`.

---

## 📚 Helm Chart Repositories

* **ArtifactHub.io** — Central hub for discovering Helm charts.
* **Bitnami** — Popular, secure charts for common software.

---

## 🧠 Best Practices

* Use `helm lint` and `helm template` before deploying.
* Keep charts DRY using helpers (`_helpers.tpl`).
* Version control all Helm charts and values files.
* Validate chart changes in CI before deployment.
* Document all configurable values in `values.yaml`.

---

## 🚀 Example: Deploy NGINX Using Helm

```sh
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install mynginx bitnami/nginx
```

To override:

```sh
helm install mynginx bitnami/nginx --set service.type=NodePort
```

To uninstall:

```sh
helm uninstall mynginx
```

---

## 📘 Summary

| Topic          | Details                                        |
| -------------- | ---------------------------------------------- |
| Helm is        | Kubernetes package manager                     |
| Primary unit   | Chart (package of Kubernetes resources)        |
| Benefits       | Reusable, versioned, configurable deployments  |
| Key commands   | install, upgrade, rollback, lint, template     |
| Version to use | Helm v3 (Tiller removed)                       |
| Use cases      | App deployment, CI/CD, staging/prod separation |

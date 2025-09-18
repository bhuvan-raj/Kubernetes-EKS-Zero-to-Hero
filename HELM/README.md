# Helm in Kubernetes

<img src="https://raw.githubusercontent.com/bhuvan-raj/Kubernetes-Openshift-Zero-to-Hero/main/HELM/helm.png" alt="Helm Banner" width="800"/>

## 1\. Introduction to Helm

- **What is Helm?**
- 
Helm is often referred to as "the package manager for Kubernetes." Just as package managers like `apt` (Debian/Ubuntu) or `yum` (Red Hat/CentOS) simplify installing and managing software on operating systems, Helm simplifies the deployment and management of applications on Kubernetes clusters.

- **Why do we need Helm?**
- 
Deploying applications on Kubernetes typically involves creating and managing numerous YAML files (for Deployments, Services, ConfigMaps, Secrets, Ingress, etc.). This can quickly become complex and error-prone, especially for multi-component applications or when deploying the same application across different environments (development, staging, production). Helm addresses these challenges by:

- **Simplifying deployment:** Packages complex applications into a single, manageable unit called a "Chart."
- **Enabling reusability:** Charts can be shared and reused, promoting consistency and reducing duplication of effort.
- **Streamlining configuration:** Allows for easy customization of application deployments using templating and values.
- **Managing application lifecycle:** Provides features for versioning, upgrading, rolling back, and uninstalling applications.
- **Dependency management:** Handles dependencies between different application components.

**Key Concepts:**

  * **Chart:** A Helm Chart is a package containing all the necessary resources and configurations to deploy an application or a set of applications to a Kubernetes cluster. It's essentially a bundle of pre-configured Kubernetes resource definitions.
  * **Config:** These are configuration values that can be applied to a Chart to customize its deployment. They are typically defined in a `values.yaml` file.
  * **Release:** A Release is a running instance of a Chart in a Kubernetes cluster, combined with a specific configuration. Each time you install a Chart, Helm creates a new Release. Helm tracks the state and history of each Release.

## 2\. Helm Architecture

Helm consists of two main components:

  * **Helm Client (CLI):** This is the command-line interface that end-users interact with. It's responsible for:

      * Local Chart development.
      * Managing Chart repositories.
      * Managing Releases (installing, upgrading, rolling back, uninstalling).
      * Interfacing with the Helm Library.

  * **Helm Library:** This is the core logic engine of Helm. In Helm 3 (the current stable version), the Helm Library is embedded within the Helm client, removing the need for a separate server-side component called Tiller (which was present in Helm 2). This change significantly improves security and simplifies the architecture. The Library is responsible for:

      * Rendering templates: Processing Chart templates with provided values to generate final Kubernetes manifests.
      * Managing Releases: Tracking the state and history of each deployment by storing release information as Kubernetes Secrets (or ConfigMaps/SQL, configurable via `HELM_DRIVER`).
      * Interfacing with Kubernetes: Sending the generated manifests to the Kubernetes API server to create or update resources in the cluster.

## 📁 Helm Components

### 1. **Chart**

A **chart** is a package of pre-configured Kubernetes resources.

**Structure of a Helm Chart:**

```
my-parent-chart/
├── Chart.yaml                  # Main metadata for the parent chart
├── values.yaml                 # Default configuration values for the parent chart and its subcharts
├── templates/                  # Kubernetes manifest templates for the parent application
│   ├── deployment.yaml         # Defines the main application Deployment
│   └── service.yaml            # Defines the main application Service
│   └── ...                     # Other parent chart specific resources (e.g., Ingress, ConfigMaps)
└── charts/                     # Directory dedicated to housing subcharts
├── my-subchart-1/          # First subchart directory
│   ├── Chart.yaml          # Metadata for my-subchart-1
│   ├── values.yaml         # Default configuration values for my-subchart-1
│   └── templates/          # Kubernetes manifest templates for my-subchart-1
│       ├── deployment.yaml
│       ├── service.yaml
│       └── ...
└── my-subchart-2/          # Second subchart directory
├── Chart.yaml          # Metadata for my-subchart-2
├── values.yaml         # Default configuration values for my-subchart-2
└── templates/          # Kubernetes manifest templates for my-subchart-2
├── deployment.yaml
├── service.yaml
├── .helmignore         # Patterns to ignore when packaging
└── ...
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
**To Override the values in values.yaml**
```
helm install my-nginx ./my-nginx-chart \
  --set replicaCount=3 \
  --set image.tag=1.2.3
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

## 🌀 Helm Release Lifecycle

Helm maintains state about every installation called a **release**.

### Lifecycle Steps:

1. **helm install**: Deploys the chart as a release.
2. **helm upgrade**: Modifies existing release with new values or chart version.
3. **helm rollback**: Reverts to an earlier version.
4. **helm uninstall**: Deletes a release but keeps history (optional).
5. **helm history**: Shows the deployment timeline of a release.


## 5\. Helm Release Management

Helm provides robust capabilities for managing the lifecycle of your application deployments.

  * **Installation:**

    ```bash
    helm install <RELEASE_NAME> <CHART_PATH_OR_NAME>
    ```

    Example: `helm install my-app ./mychart`
    You can override values using `--set` or `--values` flags:
    `helm install my-app ./mychart --set replicaCount=3`
    `helm install my-app ./mychart --values custom-values.yaml`

  * **Listing Releases:**

    ```bash
    helm list
    ```

    Shows all deployed releases in the current namespace. Use `-A` or `--all-namespaces` to see all releases.

  * **Upgrade:**

    ```bash
    helm upgrade <RELEASE_NAME> <CHART_PATH_OR_NAME>
    ```

    This command updates an existing release. It intelligently compares the new chart with the old one and applies only the necessary changes to the Kubernetes cluster. You can also provide new `values.yaml` files or `--set` overrides during an upgrade.

  * **Rollback:**

    ```bash
    helm rollback <RELEASE_NAME> [REVISION_NUMBER]
    ```

    If an upgrade introduces issues, you can easily revert to a previous working version of the release. Helm keeps a history of all release revisions.
    `helm history <RELEASE_NAME>` to see revision numbers.

  * **Uninstall:**

    ```bash
    helm uninstall <RELEASE_NAME>
    ```

    Removes all Kubernetes resources associated with a specific release. By default, it keeps the release history. Use `--purge` to also remove the history.

  * **Status:**

    ```bash
    helm status <RELEASE_NAME>
    ```

    Provides a summary of a release, including its status, deployed resources, and any notes from `NOTES.txt`.

  * **History:**

    ```bash
    helm history <RELEASE_NAME>
    ```

    Shows the revision history of a specific release, including when it was deployed, the chart version, and any status.

## 6\. Managing Dependencies

Complex applications often rely on other services or components. Helm allows charts to declare dependencies on other charts.

  * **Declaring Dependencies:**
    Dependencies are declared in the `Chart.yaml` file under the `dependencies` field:

    ```yaml
    dependencies:
      - name: mariadb
        version: "11.x.x"
        repository: "https://charts.bitnami.com/bitnami"
        condition: mariadb.enabled # Optional: Allows conditional enabling/disabling
      - name: redis
        version: "18.x.x"
        repository: "https://charts.bitnami.com/bitnami"
    ```

      * `name`: The name of the dependent chart.
      * `version`: The version or version range of the dependent chart.
      * `repository`: The URL of the chart repository where the dependent chart can be found. Helm expects `index.yaml` at this URL.
      * `condition`: (Optional) A boolean value in the parent chart's `values.yaml` that can be used to conditionally enable or disable the subchart.

  * **Managing Dependencies:**

      * `helm dependency update <CHART_PATH>`: Downloads the specified dependencies into the `charts/` directory within your chart. It also creates or updates a `Chart.lock` file, which records the exact versions of dependencies being used.
      * `helm dependency build <CHART_PATH>`: Rebuilds the `charts/` directory based on the `Chart.lock` file.
      * `helm dependency list <CHART_PATH>`: Lists the dependencies for a given chart.

## 7\. Helm Hooks

Helm hooks allow chart developers to intervene at specific points in a release's lifecycle. Hooks are Kubernetes manifests with special annotations that tell Helm when to execute them.

**Common Hook Types:**

  * `pre-install`: Runs after templates are rendered, but *before* any resources are created during an `install`.
  * `post-install`: Runs *after* all resources are loaded into Kubernetes during an `install`.
  * `pre-upgrade`: Runs after templates are rendered, but *before* any resources are updated during an `upgrade`.
  * `post-upgrade`: Runs *after* all resources have been updated during an `upgrade`.
  * `pre-delete`: Runs *before* any resources are deleted during an `uninstall`.
  * `post-delete`: Runs *after* all resources have been deleted during an `uninstall`.
  * `test`: Runs when `helm test` is executed (for running integration tests on a deployed release).

**Hook Annotations:**

To define a hook, add annotations to your Kubernetes manifest in the `templates/` directory:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ .Release.Name }}-db-migration
  annotations:
    "helm.sh/hook": pre-install,pre-upgrade
    "helm.sh/hook-weight": "-5" # Lower weight (more negative) means higher priority
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded,hook-failed
spec:
  template:
    spec:
      containers:
        - name: migrate
          image: myapp/db-migrator:latest
          command: ["/bin/sh", "-c", "echo 'Running database migrations...' && sleep 10"]
      restartPolicy: OnFailure
```

**Hook Deletion Policies (`helm.sh/hook-delete-policy`):**

  * `before-hook-creation`: Deletes the previous hook resource before a new one is launched. (Default)
  * `hook-succeeded`: Deletes the resource after the hook successfully executes.
  * `hook-failed`: Deletes the resource if the hook fails during execution.

**Use Cases for Hooks:**

  * **Database migrations:** Run a `Job` to apply schema changes before upgrading your application.
  * **Pre-flight checks:** Verify prerequisites before deploying an application.
  * **Data seeding:** Populate initial data after a fresh installation.
  * **Cleanup tasks:** Remove external resources or deregister services before deletion.

## 8\. Advanced Helm Features & Best Practices

  * **Chart Repositories:** Helm Charts can be stored and distributed via Chart repositories (HTTP servers serving `index.yaml` and `.tgz` chart archives).

      * `helm repo add <NAME> <URL>`: Adds a remote chart repository.
      * `helm repo update`: Updates local cache of chart repositories.
      * `helm search repo <KEYWORD>`: Searches for charts in configured repositories.
      * OCI-based registries are now also supported for storing charts.

  * **Linter (`helm lint`):** Essential for validating your chart's structure and syntax before deployment. It checks for common errors and adherence to best practices.

  * **Dry Run (`helm install --dry-run --debug`):** Simulates an installation or upgrade without actually deploying resources to the cluster. The `--debug` flag shows the rendered Kubernetes manifests, which is invaluable for debugging templates.

  * **Testing Charts (`helm test`):** Helm allows you to define test manifests (typically `Jobs`) within your chart that can be run after installation to verify the application's functionality. These are marked with the `helm.sh/hook: test` annotation.



  * **Secure your Helm Environment:**

      * **RBAC:** Implement Role-Based Access Control (RBAC) in your Kubernetes cluster to restrict who can install, modify, or delete Helm releases. Grant the principle of least privilege.
      * **Secrets Management:** Never store sensitive information directly in `values.yaml` or templates. Use Kubernetes Secrets, external secret management tools (e.g., HashiCorp Vault, Kubernetes External Secrets), and integrate them securely into your Helm deployments.
      * **Image Security:** Use trusted image registries and scan your container images for vulnerabilities.
      * **Chart Signing:** Sign your Helm Charts to ensure their integrity and authenticity.

  * **Post-Rendering:** Helm 3 introduced a post-renderer capability, allowing users to pipe the rendered Kubernetes manifests through an external executable (like Kustomize or a custom script) before they are applied to the cluster. This offers extreme flexibility for advanced use cases or for applying enterprise-wide policies.

## 9\. Helm vs. Kustomize (Brief Comparison)

While both Helm and Kustomize aim to simplify Kubernetes manifest management, they use different approaches:

  * **Helm (Templating Engine):**

      * Uses **templates** (Go templates) with **variables** (`values.yaml`) to generate manifests.
      * Good for **packaging and sharing** complex applications.
      * Provides **release management** capabilities (install, upgrade, rollback, history).
      * Has a **learning curve** for templating.

  * **Kustomize (Overlay Engine):**

      * Uses **overlays** and **patches** to modify existing base YAML manifests. It doesn't use a templating language in the same way Helm does.
      * Good for **customizing existing configurations** for different environments.
      * Integrated directly into `kubectl` (`kubectl apply -k`).
      * Simpler for basic customizations, but can be less flexible for highly parameterized or multi-component applications.

**Can they be used together?** Yes\! A common pattern is to use Helm to package and deploy a base application, and then use Kustomize as a post-renderer (or as a separate step) to apply environment-specific patches or add sidecars to the Helm-rendered manifests.

## 10\. Practical Use Cases for Students

  * **Deploying a multi-tier application:** Package a web application, database, and caching layer into a single Helm chart with dependencies.
  * **Managing different environments:** Show how to use separate `values.yaml` files (e.g., `dev-values.yaml`, `prod-values.yaml`) for deploying the same application with different configurations (replica counts, resource limits, external URLs) to development and production clusters.
  * **Automating CI/CD:** Integrate Helm into a CI/CD pipeline for automated testing, packaging, and deployment of applications to Kubernetes.
  * **Sharing common services:** Create a Helm chart for a common service (e.g., Nginx Ingress Controller, Prometheus) that other application charts can depend on.
  * **Customizing off-the-shelf applications:** Use Helm to deploy a popular open-source application (e.g., WordPress, Redis) from a public Helm repository and then customize its values.
  * **Implementing database migrations:** Demonstrate the use of `pre-upgrade` hooks to run database migration jobs before a new application version is rolled out.

-----

This in-depth study note provides a solid foundation for understanding and teaching Helm in Kubernetes. Encourage students to get hands-on experience by creating their own charts and experimenting with the various Helm commands and features.

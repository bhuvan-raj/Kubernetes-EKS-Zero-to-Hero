# What is eksctl?

`eksctl` is an **open-source command-line interface (CLI) tool for Amazon Elastic Kubernetes Service (EKS)** that simplifies the creation, management, and deletion of EKS clusters. Developed by Weaveworks and officially endorsed by AWS, `eksctl` streamlines the process of deploying Kubernetes on AWS, abstracting away many of the complex interactions with underlying AWS services like Amazon EC2, Amazon VPC, and AWS Identity and Access Management (IAM).

Key features and benefits of `eksctl` include:

  * **Simplicity:** Create a full-fledged EKS cluster with a single command.
  * **Declarative Configuration:** Supports YAML configuration files for defining cluster parameters, enabling Infrastructure as Code (IaC) practices.
  * **Automation:** Automates the provisioning of necessary AWS resources (VPC, subnets, security groups, IAM roles) through AWS CloudFormation.
  * **Node Group Management:** Simplifies the creation, scaling, and deletion of EKS managed and self-managed node groups.
  * **Add-on Management:** Helps in installing and managing core EKS add-ons like the VPC CNI plugin, CoreDNS, and kube-proxy.
  * **Integration:** Works seamlessly with AWS CLI and `kubectl`, automatically updating your `kubeconfig` file for cluster access.
  * **Flexibility:** Supports various advanced configurations, including private clusters, Fargate profiles, spot instances, and custom AMIs.

-----

## How to Download and Set Up eksctl

Before installing `eksctl`, ensure you have the **AWS CLI** installed and configured with appropriate credentials. `eksctl` relies on your AWS CLI configuration to authenticate with AWS.

### 1\. Install AWS CLI

If you don't have it, install and configure the AWS CLI:

  * **Download:** Follow the instructions on the official AWS CLI documentation for your operating system (Linux, macOS, Windows).
  * **Configure:** Run `aws configure` and provide your AWS Access Key ID, AWS Secret Access Key, and a default AWS region.

### 2\. Install `eksctl`

`eksctl` is a single binary, making installation straightforward. The recommended method is to download the latest release directly from its GitHub repository.

#### For Linux/macOS (AMD64/x86\_64):

```bash
# For AMD64/x86_64 systems
curl --silent --location "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
```

#### For Linux/macOS (ARM64):

```bash
# For ARM64 systems (e.g., Apple Silicon, Graviton instances)
curl --silent --location "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$(uname -s)_arm64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
```

#### For Windows:

1.  Download the appropriate `.zip` file for your architecture (e.g., `eksctl_Windows_amd64.zip`) from the [eksctl GitHub releases page](https://www.google.com/search?q=https://github.com/eksctl-io/eksctl/releases/latest).
2.  Unzip the downloaded file.
3.  Move the `eksctl.exe` executable to a directory in your system's `PATH` (e.g., `C:\Program Files\eksctl` and then add this directory to your PATH environment variable, or directly to `C:\Windows\System32`).

### 3\. Verify Installation

After installation, verify that `eksctl` is working by checking its version:

```bash
eksctl version
```

You should see output similar to `0.195.0` or later.

### 4\. Install `kubectl` (Prerequisite for interacting with the cluster)

While `eksctl` creates the cluster, `kubectl` is the command-line tool for interacting with the Kubernetes API server within the cluster.

  * **Download and Install:** Follow the instructions on the official Kubernetes documentation or AWS EKS documentation for installing `kubectl` for your OS.
    Example for Linux (AMD64):
    ```bash
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    ```
  * **Verify:** `kubectl version --client`

-----

## How to Create an EKS Cluster

You have several methods to create an EKS cluster, each suited for different preferences and use cases:

1.  **Using `eksctl` (CLI tool):** Ideal for automation, Infrastructure as Code, and complex configurations.
2.  **Using AWS Management Console:** Great for visual guidance and quick setups, especially for new users.
3.  **Using AWS CLI:** Provides granular control through direct API calls.

Let's explore the two primary methods: `eksctl` and the AWS Management Console.

-----

### How to Create an EKS Cluster using `eksctl`

`eksctl` provides two primary ways to create an EKS cluster: a quick command-line approach for basic setups and a more detailed YAML configuration file approach for customized and reproducible deployments.

### 1\. Basic Cluster Creation (Quick Start)

This command creates a cluster with default settings, which include:

  * An auto-generated cluster name.
  * Two `m5.large` worker nodes (EKS Managed Node Group) in your default region's subnets.
  * A dedicated VPC with necessary subnets, security groups, and IAM roles.
  * The default Kubernetes version supported by EKS.

<!-- end list -->

```bash
eksctl create cluster --name <YOUR_CLUSTER_NAME> --region <YOUR_AWS_REGION>
```

**Example:**

```bash
eksctl create cluster --name my-first-eks-cluster --region us-east-1
```

This command will take 15-25 minutes to complete, as it provisions all the underlying AWS resources via CloudFormation. You will see detailed output about the creation process. Once finished, `eksctl` automatically updates your `~/.kube/config` file to connect to the new cluster.

### 2\. Advanced Cluster Creation (Using a Configuration File)

For more control over your cluster's configuration (e.g., specific instance types, Kubernetes version, VPC details, multiple node groups, add-ons), `eksctl` recommends using a YAML configuration file. This approach is highly recommended for production environments or for sharing cluster definitions.

1.  **Create a Cluster Configuration File:**
    Create a file named `my-eks-cluster-config.yaml` (or any name you prefer) with your desired specifications.

    ```yaml
    apiVersion: eksctl.io/v1alpha5
    kind: ClusterConfig

    metadata:
      name: my-custom-eks-cluster
      region: ap-south-1 # Example: Mumbai region
      version: "1.29" # Specify your desired Kubernetes version

    vpc:
      # Optional: You can let eksctl create a new VPC, or
      # specify an existing VPC and subnets here.
      # Defaults to creating a new VPC if not specified.
      nat:
        gateway: Single # Use 'HighlyAvailable' for production for 2 NAT Gateways

    managedNodeGroups: # Recommended for most use cases
      - name: general-workers
        instanceType: t3.medium
        desiredCapacity: 3 # Number of nodes
        minSize: 1
        maxSize: 5
        labels: {role: general}
        tags:
          Name: "my-general-worker-node" # Custom tag for EC2 instances
        # Optional: Enable SSH access to worker nodes (requires an SSH public key)
        ssh:
          allow: true
          publicKeyPath: ~/.ssh/id_rsa.pub # Path to your public SSH key

      - name: gpu-workers # Example for a separate GPU node group
        instanceType: g4dn.xlarge # A GPU instance type
        desiredCapacity: 1
        minSize: 0
        maxSize: 2
        labels: {role: gpu}
        tags:
          Name: "my-gpu-worker-node"
        # Custom AMI for GPU instances, if needed, otherwise eksctl uses default EKS-optimized
        # ami: ami-0abcdef1234567890 # Example AMI ID

    # Optional: Enable EKS add-ons (requires the add-on to be supported by eksctl version)
    # addons:
    #   - name: vpc-cni
    #   - name: coredns
    #   - name: kube-proxy
    #     version: latest

    # Optional: Configure IAM OIDC provider for IRSA (recommended for Pod Identity)
    # This is typically done automatically when you create a cluster with eksctl,
    # but you can explicitly enable it.
    # iam:
    #   withOIDC: true
    ```

2.  **Create the Cluster using the Configuration File:**

    ```bash
    eksctl create cluster -f my-eks-cluster-config.yaml
    ```

    `eksctl` will read this YAML file, create the necessary CloudFormation stacks, and provision your EKS cluster with the specified configurations.

-----

### How to Create an EKS Cluster using the AWS Management Console

The AWS Management Console provides two main configuration options when creating an EKS cluster:

1.  **Custom configuration**: This option gives you full control over all aspects of your EKS cluster, including networking, logging, and advanced features. You'll manually specify settings for your VPC, subnets, security groups, and IAM roles. This method is suitable for users who require precise control over their cluster's infrastructure and are familiar with AWS networking and IAM concepts.

2.  **EKS Auto Mode (formerly Quick configuration)**: This simplified option streamlines the cluster creation process by automatically configuring many of the underlying AWS resources. EKS Auto Mode handles the creation of the VPC, subnets, security groups, and IAM roles with sensible defaults. It also provides built-in node pools. This method is ideal for quick setups, testing, or users who want to get started with EKS without delving into complex infrastructure details.

Here's a general step-by-step guide for creating an EKS cluster via the AWS Management Console:

1.  **Sign in to the AWS Management Console**: Navigate to the Amazon EKS service.
2.  **Choose "Add cluster" and then "Create"**: This will initiate the cluster creation wizard.
3.  **Configure Cluster**:
      * **Configuration options**: Select either **Custom configuration** or **EKS Auto Mode**, depending on your preference and expertise.
      * **Cluster name**: Provide a unique name for your EKS cluster.
      * **Kubernetes version**: Choose your desired Kubernetes version. AWS recommends using the latest stable version.
      * **Cluster service role**: Select an existing IAM role for your EKS cluster, or create a new one with the necessary permissions. This role allows the EKS control plane to manage AWS resources on your behalf.
      * **(For Custom configuration)**: Specify your **VPC**, **subnets**, and **security groups**. Ensure they meet EKS requirements.
      * **(For EKS Auto Mode)**: EKS Auto Mode will automatically provision networking resources and allows you to configure built-in **node pools** and their IAM roles.
      * **Networking**: Configure cluster endpoint access (public, private, or both).
      * **Logging**: (Optional) Enable control plane logging to CloudWatch.
      * **Tags**: (Optional) Add tags for cost allocation and organization.
4.  **Review and Create**: Review all your configurations. If everything looks correct, proceed to create the cluster.

The cluster creation process can take 15-30 minutes as AWS provisions the necessary resources. Once complete, you can configure `kubectl` to interact with your new EKS cluster.

-----

### Verify Cluster Creation

After the cluster creation process is complete (it can take 15-30 minutes, depending on the configuration and region):

1.  **Check Cluster Status:**

    ```bash
    eksctl get cluster --name <YOUR_CLUSTER_NAME> --region <YOUR_AWS_REGION>
    ```

2.  **Verify Kubernetes Nodes:**

    ```bash
    kubectl get nodes
    ```

    You should see your worker nodes listed with a `Ready` status.

3.  **Verify `kubeconfig`:**
    `eksctl` automatically updates your `~/.kube/config` file. If you created the cluster via the AWS Console, you'll need to update your `kubeconfig` manually using the AWS CLI:

    ```bash
    aws eks update-kubeconfig --name <YOUR_CLUSTER_NAME> --region <YOUR_AWS_REGION>
    ```

    Then, you can check your current context:

    ```bash
    kubectl config current-context
    ```

-----

### Cleaning Up 🧹

To delete an EKS cluster created with `eksctl`, use the delete command:

```bash
eksctl delete cluster --name <YOUR_CLUSTER_NAME> --region <YOUR_AWS_REGION>
```

To delete an EKS cluster created via the AWS Management Console:

1.  Navigate to the **Amazon EKS** service in the AWS Management Console.
2.  Select your cluster from the list.
3.  Go to the **"Configuration"** tab and then **"Delete"**.
4.  Follow the prompts to confirm the deletion.

This command/action will tear down all AWS resources associated with the cluster, including the control plane, node groups, VPC, and IAM roles. This process can also take some time.

-----

To see how to create an EKS cluster using `eksctl` in a step-by-step fashion, you can watch this video: [Create EKS Cluster using “eksctl” | Step-by-Step Guide](https://www.youtube.com/watch?v=3kaI4Thx2pU).

To see how to create an EKS Cluster using the AWS Console in a step-by-step fashion, you can watch this video: [Create EKS Cluster Using AWS Console | Create EKS Cluster on AWS | AWS EKS Tutorial](https://www.youtube.com/watch?v=oDYtISiYFwk).

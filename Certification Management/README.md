# Kubernetes Certificate Management & cert-manager

---

# 1. What is Certificate Management?

Certificate management is the process of **creating, distributing, validating, renewing, revoking, and rotating X.509 certificates** used to secure communication in a Kubernetes cluster.

Every secure connection in Kubernetes relies on **TLS (Transport Layer Security)**, and TLS depends on certificates.

Certificate management ensures:

* Authentication (Who are you?)
* Encryption (Can others read the traffic?)
* Integrity (Has the data been modified?)
* Trust (Is the certificate issued by a trusted CA?)

---

# 2. Why Kubernetes Uses Certificates

Kubernetes components continuously communicate with each other.

For example:

```
kubectl
      |
      |
API Server
  |      \
  |       \
Scheduler  Controller Manager
  |
kubelet
  |
Pods

          etcd
```

Without certificates:

* Anyone could pretend to be the API server.
* Anyone could access etcd.
* Data could be intercepted.

Certificates solve these problems through **Mutual TLS (mTLS)**.

---

# 3. What is Mutual TLS (mTLS)?

Normally HTTPS only verifies the server.

```
Client -------------> Server
        Verify Server
```

With **mTLS**, both sides verify each other.

```
Client <---------> Server

Verify Server
Verify Client
```

Kubernetes uses mTLS almost everywhere.

---

# 4. Kubernetes PKI Architecture

```
                    Cluster CA
                  (Certificate Authority)
                         |
 -------------------------------------------------------
 |         |            |            |             |
API      ETCD       Kubelet     Scheduler      Controller
Server     |            |            |             |
 |         |            |            |             |
Clients   Peers      API Server    API Server   API Server
```

Everything is signed by the Cluster CA.

---

# 5. Types of Certificates

## A. Cluster CA

The root certificate.

```
ca.crt
ca.key
```

Every certificate is signed by this CA.

---

## B. API Server Certificate

```
apiserver.crt
apiserver.key
```

Used when clients connect to Kubernetes.

```
kubectl ----TLS----> API Server
```

---

## C. ETCD Certificates

Used for secure communication with etcd.

```
server.crt
server.key

peer.crt

healthcheck-client.crt
```

---

## D. Client Certificates

Used by

* admin
* scheduler
* kube-controller-manager
* kubelet
* kube-proxy

Examples

```
admin.crt

scheduler.crt

controller-manager.crt
```

---

## E. Front Proxy Certificates

Used by aggregation layer.

```
front-proxy-ca.crt

front-proxy-client.crt
```

---

## F. Service Account Keys

Not certificates.

```
sa.pub

sa.key
```

Used for signing JWT tokens.

---

# 6. Where Certificates are Stored

For kubeadm clusters:

```
/etc/kubernetes/pki/
```

Example

```
/etc/kubernetes/pki/

ca.crt
ca.key

apiserver.crt
apiserver.key

front-proxy-ca.crt

front-proxy-client.crt

sa.key

sa.pub

etcd/
```

---

# 7. Certificate Lifecycle

```
Generate Private Key
         |
Create CSR
         |
Send to CA
         |
CA verifies
         |
Certificate issued
         |
Certificate installed
         |
Certificate expires
         |
Renew
```

---

# 8. Checking Certificates

View details

```bash
openssl x509 -in apiserver.crt -text -noout
```

Output

```
Issuer

Subject

Validity

DNS Names

SAN

Public Key

Signature
```

---

# 9. Check Expiration

```bash
kubeadm certs check-expiration
```

Example

```
CERTIFICATE                EXPIRES

apiserver                 Jan 2027

admin.conf                Jan 2027

scheduler.conf            Jan 2027
```

---

# 10. Renew Certificates

Renew everything

```bash
sudo kubeadm certs renew all
```

Only API Server

```bash
sudo kubeadm certs renew apiserver
```

Restart kubelet

```bash
sudo systemctl restart kubelet
```

---

# 11. Certificate Signing Request (CSR)

Create

```
Private Key
      |
CSR
      |
kubectl apply
      |
Pending
      |
Approve
      |
Certificate Issued
```

Commands

```bash
kubectl get csr
```

Approve

```bash
kubectl certificate approve mycsr
```

Reject

```bash
kubectl certificate deny mycsr
```

---

# 12. TLS Secrets

Applications store certificates inside Secrets.

```
kubectl create secret tls mysecret \
--cert=tls.crt \
--key=tls.key
```

---

# 13. Problems with Manual Certificate Management

Managing certificates manually becomes difficult because you need to:

* Generate keys.
* Generate CSRs.
* Send CSRs to a CA.
* Approve and sign them.
* Create Kubernetes Secrets.
* Track expiration dates.
* Renew certificates before expiry.
* Update Ingress resources to use new Secrets.

In environments with dozens or hundreds of services, this process is time-consuming and error-prone.

This is where **cert-manager** helps.

---

# 14. What is cert-manager?

**cert-manager** is a Kubernetes add-on that automates the entire certificate lifecycle.

It automatically:

* Requests certificates from a CA.
* Stores certificates as Kubernetes Secrets.
* Renews certificates before they expire.
* Updates Secrets with new certificates.
* Works with Ingress controllers automatically.

Think of it as a Kubernetes operator dedicated to certificate management.

---

# 15. cert-manager Architecture

```
                        +----------------------+
                        |    cert-manager      |
                        |      Controller      |
                        +----------+-----------+
                                   |
                    Watches Certificate CRDs
                                   |
          +------------------------+------------------------+
          |                        |                        |
      Certificate              Issuer                ClusterIssuer
          |                        |                        |
          +------------------------+------------------------+
                                   |
                         Certificate Authority
                         (Let's Encrypt, Vault,
                          Self-Signed, Venafi, etc.)
                                   |
                           Certificate + Private Key
                                   |
                           Kubernetes TLS Secret
                                   |
                                Ingress / Pod
```

---

# 16. cert-manager Components

## 1. Controller

The controller watches custom resources such as `Certificate` and creates or renews certificates as required.

## 2. Webhook

The webhook validates cert-manager resources before they are accepted by the Kubernetes API server.

## 3. CA Injector

Automatically injects CA bundles into resources like webhooks and admission controllers so that they trust the appropriate CA.

---

# 17. cert-manager Custom Resources (CRDs)

When installed, cert-manager adds new resource types.

Check them:

```bash
kubectl get crds | grep cert-manager
```

Typical output:

```
certificates.cert-manager.io
certificaterequests.cert-manager.io
issuers.cert-manager.io
clusterissuers.cert-manager.io
orders.acme.cert-manager.io
challenges.acme.cert-manager.io
```

---

# 18. Installation

## Install CRDs and cert-manager using Helm

Add the Helm repository:

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
```

Install the CRDs:

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.crds.yaml
```

Install cert-manager:

```bash
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.18.2
```

Alternatively, install CRDs with Helm:

```bash
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set crds.enabled=true
```

Verify installation:

```bash
kubectl get pods -n cert-manager
```

Expected:

```
cert-manager

cert-manager-webhook

cert-manager-cainjector
```

Verify CRDs:

```bash
kubectl get crds | grep cert-manager
```

---

# 19. Issuer vs ClusterIssuer

## Issuer

* Namespace-scoped.
* Only usable within its namespace.

```
Namespace A

Issuer
 |
Certificate
```

## ClusterIssuer

* Cluster-wide.
* Accessible from any namespace.

```
ClusterIssuer
     |
-----------------------------
|            |              |
Dev         QA           Production
```

---

# 20. Types of Issuers

## SelfSigned

Creates certificates signed by themselves.

Suitable for:

* Development
* Testing
* Internal labs

---

## CA Issuer

Uses your organization's internal CA.

---

## ACME (Let's Encrypt)

Automatically issues publicly trusted certificates after validating domain ownership.

---

## HashiCorp Vault

Uses Vault as the certificate authority.

---

## Venafi

Enterprise PKI integration.

---

## Cloud Provider Integrations

Some environments integrate cert-manager with cloud-specific certificate services through additional issuers or external controllers.

---

# 21. Self-Signed Example

Issuer:

```yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: selfsigned
spec:
  selfSigned: {}
```

Certificate:

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: nginx-cert
spec:
  secretName: nginx-tls
  commonName: nginx.local
  dnsNames:
  - nginx.local
  issuerRef:
    name: selfsigned
```

Apply:

```bash
kubectl apply -f issuer.yaml
kubectl apply -f certificate.yaml
```

---

# 22. Let's Encrypt (ACME) Example

Create a ClusterIssuer:

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    email: admin@example.com
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
    - http01:
        ingress:
          class: nginx
```

After creating a `Certificate` that references this `ClusterIssuer`, cert-manager:

1. Creates an ACME order.
2. Performs the HTTP-01 challenge.
3. Obtains the signed certificate.
4. Stores it in a Kubernetes TLS Secret.
5. Renews it automatically before expiration.

---

# 23. Using Certificates with Ingress

Example Ingress:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: demo
spec:
  tls:
  - hosts:
      - demo.example.com
    secretName: demo-tls
  rules:
  - host: demo.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: demo-service
            port:
              number: 80
```

When `demo-tls` is created by cert-manager, the Ingress controller automatically serves HTTPS.

---

# 24. Certificate Renewal

cert-manager continuously monitors certificate expiration.

```
90 Days Certificate
          |
     60 Days
          |
     30 Days Left
          |
Automatically Renew
          |
Update Secret
          |
Ingress Uses New Certificate
```

No manual intervention is typically required.

---

# 25. Useful Commands

```bash
# View issuers
kubectl get issuers

# View cluster issuers
kubectl get clusterissuers

# View certificates
kubectl get certificates

# Describe a certificate
kubectl describe certificate <name>

# View certificate requests
kubectl get certificaterequests

# View ACME orders
kubectl get orders

# View ACME challenges
kubectl get challenges

# View generated TLS secrets
kubectl get secrets

# Check cert-manager logs
kubectl logs deploy/cert-manager -n cert-manager

# Check cert-manager components
kubectl get pods -n cert-manager
```

---

# 26. Common Troubleshooting

| Issue                               | Possible Cause                          | Resolution                                                           |
| ----------------------------------- | --------------------------------------- | -------------------------------------------------------------------- |
| Certificate not issued              | Issuer not ready                        | `kubectl describe issuer`                                            |
| Secret not created                  | Certificate resource error              | `kubectl describe certificate`                                       |
| HTTP-01 challenge failed            | Ingress or DNS misconfiguration         | Verify DNS, Ingress, and challenge resources                         |
| Certificate stuck in Pending        | ACME challenge incomplete               | Inspect `orders` and `challenges` resources                          |
| Renewal failed                      | Issuer unavailable or validation failed | Check cert-manager logs and issuer status                            |
| Browser shows untrusted certificate | Using a self-signed certificate         | Use a publicly trusted CA such as Let's Encrypt for public endpoints |

---

# 27. Best Practices

* Use **ClusterIssuer** for certificates shared across multiple namespaces.
* Use **Issuer** when certificates should remain isolated to a single namespace.
* Use **Let's Encrypt** for internet-facing applications.
* Use **SelfSigned** or an internal CA for development and private clusters.
* Monitor certificate status with `kubectl get certificates`.
* Back up important TLS Secrets and CA keys securely.
* Restrict access to private keys using Kubernetes RBAC and Secret encryption at rest.
* Keep cert-manager updated to benefit from security fixes and new issuer features.

---

# Summary

* Kubernetes secures component communication using **X.509 certificates** and **mTLS**.
* `kubeadm` manages control plane certificates, while applications commonly use **TLS Secrets**.
* Manual certificate handling does not scale well in large environments.
* **cert-manager** automates certificate issuance, storage, renewal, and rotation through Kubernetes custom resources.
* It integrates with **Let's Encrypt**, **HashiCorp Vault**, self-signed CAs, enterprise PKI solutions, and many other certificate providers, making HTTPS management in Kubernetes largely hands-free.

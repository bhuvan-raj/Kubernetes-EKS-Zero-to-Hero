# Kubernetes Identity creation using Git Bash

## Windows-Compatible Steps (Using Git Bash)

### 1️⃣ Verify OpenSSL

```bash
openssl version
```

If it prints a version → you are good.

---

### 2️⃣ Generate User Key

```bash
openssl genrsa -out student-user.key 2048
```

---

### 3️⃣ Create CSR

```bash
openssl req -new -key student-user.key -out student-user.csr \
  -subj "/CN=student-user"
```

---

### 4️⃣ Create Kubernetes CSR Object

```bash
cat <<EOF | kubectl apply -f -
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: student-user
spec:
  request: $(cat student-user.csr | base64 | tr -d '\n')
  signerName: kubernetes.io/kube-apiserver-client
  usages:
  - client auth
EOF
```

✔ Works in **Git Bash**

---

### 5️⃣ Approve CSR

```bash
kubectl get csr
kubectl certificate approve student-user
```

---

### 6️⃣ Extract Certificate

```bash
kubectl get csr student-user -o jsonpath='{.status.certificate}' \
| base64 --decode > student-user.crt
```

---

### 7️⃣ Configure kubeconfig

```bash
kubectl config set-credentials student-user \
  --client-certificate=student-user.crt \
  --client-key=student-user.key
```

```bash
kubectl config set-context student-user-context \
  --cluster=kind-student-cluster \
  --user=student-user
```

---

### 8️⃣ Test

```bash
kubectl config use-context student-user-context
kubectl get pods -n student-app
```

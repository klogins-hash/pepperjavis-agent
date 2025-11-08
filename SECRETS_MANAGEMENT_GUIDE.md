# PepperJarvis Agent - Secrets Management Guide

## Overview

This guide provides a comprehensive approach to managing secrets, API keys, and passwords in the PepperJarvis Agent infrastructure. The solution uses **HashiCorp Vault** for centralized secrets storage with **External Secrets Operator** for Kubernetes integration.

---

## Architecture

### Components

1. **HashiCorp Vault** (vault namespace)
   - Centralized secrets storage
   - Encryption at rest
   - Audit logging
   - Role-based access control (RBAC)

2. **External Secrets Operator** (external-secrets namespace)
   - Syncs secrets from Vault to Kubernetes
   - Automatic secret rotation
   - Template-based secret creation

3. **Kubernetes Secrets** (pepperjavis namespace)
   - Generated automatically from Vault
   - Mounted into pods
   - Refreshed hourly

4. **RBAC Controls**
   - PepperJarvis Agent can only read specific secrets
   - Namespaces are isolated via Network Policies
   - Service accounts have minimal required permissions

---

## Deployment Steps

### Step 1: Deploy External Secrets Operator

```bash
# Apply External Secrets Operator
kubectl apply -f k8s-external-secrets-operator.yaml --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# Verify deployment
kubectl get pods -n external-secrets --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml
```

### Step 2: Deploy Vault

```bash
# Apply Vault infrastructure
kubectl apply -f k8s-secrets-vault.yaml --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# Verify Vault is running
kubectl get pods -n vault --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# Wait for Vault to be ready
kubectl wait --for=condition=ready pod -l app=vault -n vault --timeout=300s --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml
```

### Step 3: Initialize Vault

```bash
# Port-forward to Vault
kubectl port-forward -n vault svc/vault-svc 8200:8200 --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml &

# Initialize Vault (run in another terminal)
export VAULT_ADDR="https://127.0.0.1:8200"
export VAULT_SKIP_VERIFY=true

# Initialize Vault (generates root token and unseal keys)
vault operator init \
  -key-shares=5 \
  -key-threshold=3 \
  > vault-init.txt

# IMPORTANT: Save vault-init.txt in a secure location!
# This file contains root token and unseal keys
```

### Step 4: Unseal Vault

```bash
# Unseal Vault with 3 of 5 keys
export VAULT_ADDR="https://127.0.0.1:8200"
export VAULT_SKIP_VERIFY=true

# Enter 3 different unseal keys when prompted
vault operator unseal

# Repeat 3 times with different keys
vault operator unseal
vault operator unseal
```

### Step 5: Login to Vault

```bash
# Login with root token (from vault-init.txt)
vault login <ROOT_TOKEN>
```

### Step 6: Enable Kubernetes Auth

```bash
# Enable Kubernetes auth method
vault auth enable kubernetes

# Configure Kubernetes auth
vault write auth/kubernetes/config \
  token_reviewer_jwt=@/var/run/secrets/kubernetes.io/serviceaccount/token \
  kubernetes_host=https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT \
  kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
```

### Step 7: Create Vault Policies and Roles

```bash
# Create policy for pepperjavis-agent
cat > /tmp/pepperjavis-policy.hcl << 'EOF'
path "secret/data/database/*" {
  capabilities = ["read", "list"]
}

path "secret/data/storage/*" {
  capabilities = ["read", "list"]
}

path "secret/data/application/*" {
  capabilities = ["read", "list"]
}

path "secret/data/cloud/*" {
  capabilities = ["read", "list"]
}

path "secret/data/llm/*" {
  capabilities = ["read", "list"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}
EOF

vault policy write pepperjavis-agent /tmp/pepperjavis-policy.hcl

# Create role for pepperjavis-agent service account
vault write auth/kubernetes/role/pepperjavis-agent \
  bound_service_account_names=pepperjavis-agent \
  bound_service_account_namespaces=pepperjavis \
  policies=pepperjavis-agent \
  ttl=24h

# Create policy for External Secrets Operator
cat > /tmp/external-secrets-policy.hcl << 'EOF'
path "secret/data/*" {
  capabilities = ["read", "list"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}
EOF

vault policy write external-secrets-operator /tmp/external-secrets-policy.hcl

# Create role for External Secrets Operator
vault write auth/kubernetes/role/external-secrets-operator \
  bound_service_account_names=external-secrets-operator \
  bound_service_account_namespaces=external-secrets \
  policies=external-secrets-operator \
  ttl=24h
```

### Step 8: Create Secrets in Vault

```bash
# Create database secrets
vault kv put secret/database/postgres \
  password="your-secure-postgres-password" \
  username="pepperjavis" \
  host="postgres.pepperjavis.svc.cluster.local" \
  port="5432" \
  database="pepperjavis"

# Create MinIO secrets
vault kv put secret/storage/minio \
  password="your-secure-minio-password" \
  username="minioadmin" \
  endpoint="minio.pepperjavis.svc.cluster.local:9000" \
  access_key="minioadmin" \
  secret_key="your-secure-minio-secret-key"

# Create application API keys
vault kv put secret/application/pepperjavis \
  api_key="your-api-key" \
  api_secret="your-api-secret" \
  jwt_secret="your-jwt-secret-key"

# Create AWS credentials (if needed)
vault kv put secret/cloud/aws \
  access_key_id="AKIA..." \
  secret_access_key="your-aws-secret" \
  region="us-east-1"

# Create LLM API keys
vault kv put secret/llm/openai \
  api_key="sk-..."

vault kv put secret/llm/anthropic \
  api_key="sk-ant-..."

vault kv put secret/llm/azure \
  api_key="your-azure-key"
```

### Step 9: Verify Secrets Sync

```bash
# Check if secrets were created in Kubernetes
kubectl get secrets -n pepperjavis --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# View secret contents (with proper RBAC restrictions)
kubectl get secret postgres-secret -n pepperjavis -o jsonpath='{.data}' --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml
```

### Step 10: Update Deployment to Use Secrets

Update `k8s-deployment.yaml` to reference secrets:

```yaml
env:
- name: POSTGRES_PASSWORD
  valueFrom:
    secretKeyRef:
      name: postgres-secret
      key: password
- name: POSTGRES_HOST
  valueFrom:
    secretKeyRef:
      name: postgres-secret
      key: host
- name: MINIO_ROOT_PASSWORD
  valueFrom:
    secretKeyRef:
      name: minio-secret
      key: password
- name: API_KEY
  valueFrom:
    secretKeyRef:
      name: pepperjavis-api-key
      key: api_key
- name: OPENAI_API_KEY
  valueFrom:
    secretKeyRef:
      name: pepperjavis-llm-key
      key: openai_api_key
```

---

## Secret Categories & Access Control

### Database Secrets
- **Stored at**: `secret/database/*`
- **Access**: PepperJarvis Agent, Database administrators
- **Includes**: PostgreSQL user/password, host, port, database name

### Storage Secrets
- **Stored at**: `secret/storage/*`
- **Access**: PepperJarvis Agent, MinIO administrators
- **Includes**: MinIO credentials, endpoint, access/secret keys

### Application Secrets
- **Stored at**: `secret/application/*`
- **Access**: PepperJarvis Agent only
- **Includes**: API keys, JWT secrets

### Cloud Credentials
- **Stored at**: `secret/cloud/*`
- **Access**: PepperJarvis Agent, Cloud administrators
- **Includes**: AWS credentials, regions

### LLM API Keys
- **Stored at**: `secret/llm/*`
- **Access**: PepperJarvis Agent only
- **Includes**: OpenAI, Anthropic, Azure API keys

---

## RBAC & Security

### PepperJarvis Agent Access
```yaml
# Can read secrets only (not delete/modify)
- Database credentials
- Storage credentials
- Application secrets
- LLM API keys

# Cannot access:
- Vault system paths
- Other service account tokens
- Other namespaces
```

### External Secrets Operator Access
```yaml
# Can read all secrets (necessary for sync)
# Limited to specific namespaces
# Cannot modify Vault policies
```

### Network Policies

Defined in `k8s-secrets-vault.yaml`:

1. **Vault Network Policy**
   - Only allow ingress from external-secrets and pepperjavis namespaces
   - Port 8200 only

2. **External Secrets Operator Network Policy**
   - Allow egress to Vault only (port 8200)
   - Allow DNS queries for service discovery

---

## Secret Rotation Strategy

### Automatic Rotation
- ExternalSecrets refresh interval: **1 hour**
- Vault token TTL: **24 hours**

### Manual Rotation

To rotate a secret:

```bash
# Update secret in Vault
vault kv put secret/database/postgres \
  password="new-secure-password" \
  username="pepperjavis" \
  host="postgres.pepperjavis.svc.cluster.local" \
  port="5432" \
  database="pepperjavis"

# External Secrets will automatically sync within 1 hour
# Or force immediate sync:
kubectl delete secret postgres-secret -n pepperjavis --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# ExternalSecret will recreate it from Vault
```

---

## Backup & Disaster Recovery

### Vault Data Backup

```bash
# Create backup of Vault data
kubectl exec -n vault vault-0 -- sh -c 'tar czf /vault/data/vault-backup.tar.gz /vault/data' --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# Copy backup to secure location
kubectl cp vault/vault-0:/vault/data/vault-backup.tar.gz ./vault-backup.tar.gz --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml
```

### Vault Snapshots

```bash
# Create Raft snapshot (if using Raft storage)
vault write -f raft/snapshot > vault-snapshot.snap
```

### Recovery

```bash
# Restore from backup
kubectl cp ./vault-backup.tar.gz vault/vault-0:/vault/data/backup.tar.gz --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

kubectl exec -n vault vault-0 -- tar xzf /vault/data/backup.tar.gz --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml
```

---

## Audit Logging

Enable Vault audit logging:

```bash
# Enable file audit backend
vault audit enable file file_path=/vault/logs/audit.log

# Enable syslog audit backend (for central logging)
vault audit enable syslog tag="vault" facility="LOCAL7"
```

### View Audit Logs

```bash
# Port-forward to Vault
kubectl logs -n vault vault-0 --tail=100 --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# Or check audit logs on filesystem (if mounted)
kubectl exec -n vault vault-0 -- tail -f /vault/logs/audit.log --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml
```

---

## Monitoring & Alerting

### Prometheus Scraping

Vault exports metrics on `:8200/v1/sys/metrics`:

```yaml
# Add to Prometheus scrape_configs
- job_name: 'vault'
  metrics_path: '/v1/sys/metrics'
  params:
    format: ['prometheus']
  bearer_token: '<VAULT_TOKEN>'
  static_configs:
    - targets: ['vault-svc.vault.svc.cluster.local:8200']
```

### Key Metrics to Monitor

- `vault_core_unsealed` - Vault sealed status (should be 1)
- `vault_secrets_kv_count` - Number of secrets stored
- `vault_audit_log_entry` - Audit log entries
- `vault_core_login` - Login attempts

### Alert Rules

```yaml
- alert: VaultSealed
  expr: vault_core_unsealed == 0
  for: 1m
  annotations:
    summary: "Vault is sealed"

- alert: VaultTokenAboutToExpire
  expr: vault_token_lookup_remaining_ttl < 3600
  for: 5m
  annotations:
    summary: "Vault token expires in less than 1 hour"
```

---

## Troubleshooting

### Issue: "permission denied" when reading secrets

**Solution**: Check RBAC permissions:

```bash
# Verify service account has role binding
kubectl get rolebinding -n pepperjavis pepperjavis-secrets-reader-binding --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# Check Vault policies
vault policy read pepperjavis-agent
```

### Issue: ExternalSecret stays in "Pending" state

**Solution**: Check logs:

```bash
# Check External Secrets Operator logs
kubectl logs -n external-secrets -l app.kubernetes.io/name=external-secrets --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# Check ExternalSecret status
kubectl describe externalsecret postgres-secret -n pepperjavis --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml
```

### Issue: Vault pod not starting

**Solution**: Check TLS certificates:

```bash
# Verify TLS secret exists
kubectl get secret vault-tls -n vault --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# If missing, create self-signed certificates:
kubectl create secret tls vault-tls \
  --cert=server.crt \
  --key=server.key \
  -n vault --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml
```

### Issue: Unseal keys lost

**Solution**: Emergency Unseal (last resort):

```bash
# Create new root token using recovery keys (if enabled)
vault operator generate-root -init
```

---

## Best Practices

### ✅ DO

1. **Store vault-init.txt in a secure location**
   - Encrypt and backup to secure storage
   - Keep separate from code/configurations

2. **Rotate root token regularly**
   - Use periodic root policy
   - Never commit root token to git

3. **Monitor secret access**
   - Enable audit logging
   - Review logs regularly
   - Alert on suspicious access patterns

4. **Use least privilege**
   - Grant minimal required permissions
   - Separate read/write policies
   - Namespace-scoped access

5. **Backup Vault regularly**
   - Schedule daily snapshots
   - Store backups securely
   - Test recovery procedures

6. **Enable TLS**
   - Use proper certificates in production
   - Rotate certificates regularly

### ❌ DON'T

1. **Never commit secrets to git**
   - Use .gitignore for secret files
   - Never hardcode API keys

2. **Don't use root token for applications**
   - Create specific roles/policies
   - Use Kubernetes auth

3. **Don't disable audit logging**
   - Maintain complete audit trail
   - Retain logs for compliance

4. **Don't share unseal keys** with developers
   - Keep separate from code access
   - Require key custodians

5. **Don't mix production/staging secrets**
   - Use separate vaults if possible
   - Never share between environments

---

## Files Reference

| File | Purpose |
|------|---------|
| `k8s-secrets-vault.yaml` | Vault deployment, policies, ExternalSecrets |
| `k8s-external-secrets-operator.yaml` | External Secrets Operator controller |
| `k8s-databases.yaml` | Updated with secret references |
| `k8s-deployment.yaml` | Updated with secret references |
| `vault-init.txt` | Vault initialization output (KEEP SECURE!) |

---

## Production Checklist

- [ ] Vault deployed and unsealed
- [ ] External Secrets Operator running
- [ ] All secrets created in Vault
- [ ] RBAC roles and policies configured
- [ ] Network policies enabled
- [ ] Audit logging enabled
- [ ] TLS certificates configured
- [ ] Backup strategy tested
- [ ] Monitoring and alerting configured
- [ ] Disaster recovery procedure documented
- [ ] Team trained on secret management
- [ ] vault-init.txt backed up securely

---

## Support & Documentation

- Vault Docs: https://www.vaultproject.io/docs
- External Secrets Operator: https://external-secrets.io/
- Kubernetes Secrets: https://kubernetes.io/docs/concepts/configuration/secret/

---

**Last Updated**: November 8, 2025
**Status**: Ready for Production Deployment

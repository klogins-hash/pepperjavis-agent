# Secrets Management Implementation - Quick Start

## Overview

PepperJarvis Agent now uses **HashiCorp Vault** with **External Secrets Operator** for centralized, secure secrets management. All credentials, API keys, and passwords are now stored securely and synchronized automatically.

## What Changed

### ✅ New Files Added
- `k8s-secrets-vault.yaml` - Vault deployment and ExternalSecrets
- `k8s-external-secrets-operator.yaml` - External Secrets Operator controller
- `SECRETS_MANAGEMENT_GUIDE.md` - Comprehensive setup guide

### ✅ Updated Files
- `k8s-databases.yaml` - Now references secrets from Vault
- `k8s-deployment.yaml` - All containers read secrets from ExternalSecrets

### ✅ Security Improvements
- ❌ No more hardcoded passwords in manifests
- ✅ Secrets encrypted at rest in Vault
- ✅ Automatic rotation support
- ✅ Granular RBAC per service
- ✅ Audit logging of all secret access
- ✅ Network policies protecting Vault access

---

## Quick Deployment

### 1. Deploy External Secrets Operator

```bash
kubectl apply -f k8s-external-secrets-operator.yaml \
  --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# Verify
kubectl get pods -n external-secrets --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml
```

### 2. Deploy Vault

```bash
kubectl apply -f k8s-secrets-vault.yaml \
  --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# Verify
kubectl get pods -n vault --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml
```

### 3. Initialize & Configure Vault

See **SECRETS_MANAGEMENT_GUIDE.md** for detailed step-by-step instructions for:
- Initializing Vault
- Unsealing Vault
- Configuring Kubernetes authentication
- Creating secrets in Vault
- Verifying syncing

### 4. Deploy Application & Databases

Once Vault is configured with secrets:

```bash
# Deploy databases (uses secrets from ExternalSecrets)
kubectl apply -f k8s-databases.yaml \
  --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# Deploy application
kubectl apply -f k8s-deployment.yaml \
  --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml
```

---

## Secret Categories

All secrets are stored in Vault under these paths:

| Path | Content | Used By |
|------|---------|---------|
| `secret/database/postgres` | PostgreSQL credentials | Database, Application |
| `secret/storage/minio` | MinIO credentials | Storage, Application |
| `secret/application/pepperjavis` | API keys, JWT secrets | Application |
| `secret/llm/*` | LLM API keys (OpenAI, Anthropic, Azure) | Application |
| `secret/cloud/aws` | AWS credentials (optional) | Application |

---

## RBAC & Access Control

### PepperJarvis Agent (Read-Only)
```yaml
Can access:
- secret/database/* (PostgreSQL creds)
- secret/storage/* (MinIO creds)
- secret/application/* (API keys)
- secret/cloud/* (AWS creds)
- secret/llm/* (LLM API keys)
```

### External Secrets Operator (Read-Only)
```yaml
Can access:
- secret/* (all secrets for syncing)
```

### Vault Namespace Isolation
- Vault: Accessible only from external-secrets & pepperjavis namespaces
- Port 8200 only, network policies enforce access

---

## Auto-Refresh & Rotation

✅ **Automatic Refresh**: ExternalSecrets refresh interval = 1 hour
✅ **Manual Rotation**: Update in Vault, ExternalSecrets syncs automatically
✅ **Zero-Downtime**: Pods pick up new secrets on next mount

### Rotate a Secret (Example)

```bash
# Update in Vault
vault kv put secret/database/postgres \
  password="new-secure-password" \
  username="pepperjavis" \
  host="postgres.pepperjavis.svc.cluster.local" \
  port="5432" \
  database="pepperjavis"

# Delete Kubernetes secret to force immediate sync
kubectl delete secret postgres-secret -n pepperjavis \
  --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# ExternalSecret will recreate it from Vault within seconds
```

---

## Monitoring & Troubleshooting

### Check Vault Status

```bash
# Port-forward to Vault
kubectl port-forward -n vault svc/vault-svc 8200:8200 \
  --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml &

export VAULT_ADDR="https://127.0.0.1:8200"
export VAULT_SKIP_VERIFY=true

# Check status
vault status

# List secrets
vault kv list secret/
```

### Check ExternalSecrets Sync

```bash
# List all ExternalSecrets
kubectl get externalsecrets -n pepperjavis \
  --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# Check specific ExternalSecret status
kubectl describe externalsecret postgres-secret -n pepperjavis \
  --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# Check synced Kubernetes secrets
kubectl get secrets -n pepperjavis \
  --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml
```

### View Secret Contents (for testing only)

```bash
# View base64-encoded secret
kubectl get secret postgres-secret -n pepperjavis \
  -o jsonpath='{.data}' --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# Decode specific value
kubectl get secret postgres-secret -n pepperjavis \
  -o jsonpath='{.data.password}' --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml | base64 -d
```

### Logs

```bash
# External Secrets Operator logs
kubectl logs -n external-secrets -l app.kubernetes.io/name=external-secrets \
  --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml -f

# Vault logs
kubectl logs -n vault vault-0 \
  --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml -f
```

---

## Troubleshooting

### ExternalSecret Stuck in "Pending"

```bash
# Check logs for errors
kubectl logs -n external-secrets -l app.kubernetes.io/name=external-secrets -f \
  --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# Check ExternalSecret status
kubectl describe externalsecret postgres-secret -n pepperjavis \
  --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml
```

**Common Issues:**
- Vault not unsealed
- Kubernetes auth not configured
- Secret path doesn't exist in Vault
- RBAC policies too restrictive

### Vault Pod Not Starting

```bash
# Check pod logs
kubectl logs -n vault vault-0 \
  --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# Check for TLS certificate issues
kubectl describe pod vault-0 -n vault \
  --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml
```

**Common Issues:**
- TLS certificate missing
- Storage volume not mounted
- Insufficient resources

### Database Connectivity Issues

```bash
# First, verify secret was created
kubectl get secret postgres-secret -n pepperjavis \
  --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml

# Check pod environment variables are set
kubectl exec -it deployment/pepperjavis-agent -n pepperjavis \
  --kubeconfig=$HOME/.kube/pepperjavis-agent.yaml -- env | grep POSTGRES
```

---

## Best Practices

### ✅ DO

1. **Backup vault-init.txt securely**
   - Keep encrypted copy offline
   - Store separate from cluster

2. **Rotate secrets regularly**
   - Update passwords monthly
   - Rotate API keys quarterly

3. **Monitor Vault access**
   - Enable audit logging
   - Review audit logs weekly
   - Alert on failed login attempts

4. **Use descriptive secret paths**
   - `secret/database/postgres` not `secret/db1`
   - `secret/llm/openai` not `secret/api-keys`

5. **Test disaster recovery**
   - Practice Vault restore
   - Verify backup procedures
   - Document RTO/RPO

### ❌ DON'T

1. **Never commit vault-init.txt to git**
   - Store in secure vault (1Password, Vault, etc.)
   - Require key custodian approval to unseal

2. **Don't disable audit logging**
   - Maintain audit trail for compliance
   - Retain logs for 90+ days

3. **Don't share Vault tokens with developers**
   - Use Kubernetes auth only
   - Require short-lived credentials

4. **Don't hardcode secrets in application code**
   - Always use environment variables
   - Never log secret values

5. **Don't skip TLS in production**
   - Use proper certificates
   - Validate certificate chains

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    pepperjavis namespace                │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────┐          │
│  │  PepperJarvis Agent Pod                  │          │
│  │  - Mount postgres-secret                 │          │
│  │  - Mount minio-secret                    │          │
│  │  - Mount pepperjavis-api-key             │          │
│  │  - Mount pepperjavis-llm-key             │          │
│  └──────────────────────────────────────────┘          │
│           ↓ (references)                               │
│  ┌──────────────────────────────────────────┐          │
│  │  ExternalSecrets (auto-created)          │          │
│  │  - postgres-secret (1h refresh)          │          │
│  │  - minio-secret (1h refresh)             │          │
│  │  - pepperjavis-api-key (1h refresh)      │          │
│  │  - pepperjavis-llm-key (1h refresh)      │          │
│  └──────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────┘
                      ↓ (pulls from)
┌─────────────────────────────────────────────────────────┐
│          external-secrets namespace                     │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────┐          │
│  │  External Secrets Operator Pod           │          │
│  │  - Watches ExternalSecrets resources     │          │
│  │  - Syncs from Vault every 1 hour         │          │
│  │  - Creates Kubernetes Secrets            │          │
│  └──────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────┘
                      ↓ (reads from)
┌─────────────────────────────────────────────────────────┐
│              vault namespace                            │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────┐          │
│  │  HashiCorp Vault Pod                     │          │
│  │  - Stores: secret/database/*             │          │
│  │  - Stores: secret/storage/*              │          │
│  │  - Stores: secret/application/*          │          │
│  │  - Stores: secret/llm/*                  │          │
│  │  - Stores: secret/cloud/*                │          │
│  │  - Sealed with 5 keys (3 required)       │          │
│  │  - Audit logging enabled                 │          │
│  │  - TLS encryption enabled                │          │
│  └──────────────────────────────────────────┘          │
│           Storage: PVC (10Gi)                          │
└─────────────────────────────────────────────────────────┘
```

---

## Deployment Checklist

Complete this checklist to ensure production-ready Secrets Management:

- [ ] External Secrets Operator deployed
- [ ] Vault deployed and initialized
- [ ] Vault unsealed (3 of 5 keys)
- [ ] Kubernetes auth configured in Vault
- [ ] All policies created
- [ ] All secrets populated in Vault
- [ ] ExternalSecrets syncing successfully
- [ ] Database pod can connect using synced secrets
- [ ] Application pod gets all required secrets
- [ ] Vault audit logging enabled
- [ ] TLS certificates configured
- [ ] Network policies verified
- [ ] Backup procedure tested
- [ ] vault-init.txt stored securely (offline)
- [ ] Team trained on secret rotation
- [ ] Monitoring & alerting configured

---

## Related Documentation

- **SECRETS_MANAGEMENT_GUIDE.md** - Complete setup & operation guide
- **k8s-databases.yaml** - Database manifest (uses secrets)
- **k8s-deployment.yaml** - Application manifest (uses secrets)
- **k8s-secrets-vault.yaml** - Vault & ExternalSecrets manifests
- **k8s-external-secrets-operator.yaml** - Operator deployment manifest

---

## Support & Resources

- **HashiCorp Vault**: https://www.vaultproject.io/docs
- **External Secrets Operator**: https://external-secrets.io/
- **Kubernetes Secrets**: https://kubernetes.io/docs/concepts/configuration/secret/

---

**Status**: ✅ Ready for Production
**Last Updated**: November 8, 2025

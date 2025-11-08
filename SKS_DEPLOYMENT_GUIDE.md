# PepperJarvis Agent - SKS Kubernetes Deployment Guide

## Cost Optimization Strategy

This guide provides a cost-optimized deployment of the PepperJarvis Agent on Exoscale SKS (Scalable Kubernetes Service).

### Cost Breakdown

#### Control Plane (Always Running)
- **Starter Tier**: $0.10/day = ~$3/month (minimum)
- **Pro Tier**: $0.30/day = ~$9/month

#### Compute Nodes (Auto-Scaling)
- **Standard.small**: ~$0.05/hour when running
- **Auto-scales 0-3 nodes**: Scales to 0 when no load = $0/hour idle

### Total Monthly Cost Estimates

| Scenario | Starter CP | 1 Small Node | 3 Small Nodes | Total |
|----------|-----------|------------|-------------|-------|
| **Idle (0 nodes)** | $3 | $0 | N/A | $3/month |
| **Normal (1 node)** | $3 | $36 | N/A | $39/month |
| **Peak (3 nodes)** | $3 | N/A | $108 | $111/month |

## Prerequisites

```bash
# Verify CLI is installed and configured
exo version
exo config show
```

## Step 1: Create SKS Cluster

```bash
cd /Users/franksimpson/vscode_projects/pepperjavis-agent

# Run the deployment script
source ~/.env.local
./sks-deployment.sh
```

**What this creates:**
- SKS cluster named `pepperjavis-agent`
- Starter control plane (cost-optimized)
- Cilium CNI (fast networking)
- Exoscale CSI (persistent storage)
- Auto-upgrade enabled
- Initial 1x standard.small node

## Step 2: Get Kubeconfig

```bash
# Create .kube directory
mkdir -p ~/.kube

# Download kubeconfig
source ~/.env.local
exo compute sks kubeconfig pepperjavis-agent \
  --zone=ch-gva-2 \
  > ~/.kube/pepperjavis-agent.yaml

# Verify kubeconfig
kubectl cluster-info --kubeconfig=~/.kube/pepperjavis-agent.yaml
```

## Step 3: Deploy Storage

```bash
export KUBECONFIG=~/.kube/pepperjavis-agent.yaml

# Create persistent volumes for databases
kubectl apply -f k8s-storage.yaml

# Verify PVCs
kubectl get pvc -n pepperjavis
```

## Step 4: Deploy PepperJarvis Agent

```bash
# Build Docker image
docker build -t pepperjavis-agent:latest .

# Tag and push to registry (or use local with imagePullPolicy: IfNotPresent)
# docker tag pepperjavis-agent:latest your-registry/pepperjavis-agent:latest
# docker push your-registry/pepperjavis-agent:latest

# Deploy to Kubernetes
kubectl apply -f k8s-deployment.yaml

# Monitor deployment
kubectl logs -n pepperjavis -f deployment/pepperjavis-agent

# Check HPA status
kubectl get hpa -n pepperjavis -w
```

## Step 5: Verify Deployment

```bash
# Check pods status
kubectl get pods -n pepperjavis

# Get service info
kubectl get svc -n pepperjavis

# Test the API
ENDPOINT=$(kubectl get svc pepperjavis-agent -n pepperjavis \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$ENDPOINT:8000/health
```

## Scaling Management

### Auto-Scaling Configuration

The deployment includes HPA (Horizontal Pod Autoscaler) that:
- Scales 1-3 replicas based on CPU & memory
- Scales up immediately (30s stabilization)
- Scales down gradually (5min stabilization)
- Target: 70% CPU, 80% memory utilization

### Manual Scaling

```bash
# Scale up immediately
kubectl scale deployment pepperjavis-agent -n pepperjavis --replicas=3

# Check scaling status
kubectl get hpa -n pepperjavis

# View pod metrics
kubectl top pods -n pepperjavis
```

### Node Pool Scaling

```bash
# List current node pools
exo compute sks nodepool list pepperjavis-agent --zone=ch-gva-2

# Add nodes manually
exo compute sks nodepool scale pepperjavis-agent default \
  --zone=ch-gva-2 \
  --size=3

# Enable autoscaling (if available)
# exo compute sks nodepool auto-scale ...
```

## Cost Control & Optimization

### 1. Set Resource Requests/Limits

Already configured in k8s-deployment.yaml:
```yaml
requests:
  cpu: 100m      # Allows high pod density
  memory: 256Mi

limits:
  cpu: 500m      # Prevents runaway processes
  memory: 512Mi
```

### 2. Use Spot Instances (if available)

```bash
# Future: Deploy on spot instances for 50-80% cost savings
# Example when creating nodepool:
exo compute sks nodepool create pepperjavis-agent spot-pool \
  --zone=ch-gva-2 \
  --instance-type=standard.small
  # --spot-instance (if supported)
```

### 3. Enable Pod Disruption Budget

Already configured to prevent service interruption during scaling.

### 4. Monitor Costs

```bash
# Get current resource usage
kubectl top nodes
kubectl top pods -n pepperjavis

# Estimate costs
# Starter CP: $3/month
# Nodes: ($0.05/hour * 24 * 30) * number_of_nodes
```

## Troubleshooting

### Cluster Creation Fails

```bash
# Check account status
exo account status

# Verify zone availability
exo compute zone list

# Check quotas
exo account limits
```

### Pods Not Scaling

```bash
# Check HPA status
kubectl describe hpa -n pepperjavis pepperjavis-agent-hpa

# Check metrics server
kubectl get deployment metrics-server -n kube-system

# Check pod metrics
kubectl get --raw /apis/metrics.k8s.io/v1beta1/nodes
```

### Storage Issues

```bash
# Check PVC status
kubectl describe pvc -n pepperjavis

# Check storage class
kubectl get storageclass

# Check CSI driver
kubectl get daemonset -n kube-system | grep csi
```

## Advanced: Helm Deployment

For production, use Helm charts:

```bash
# Create values.yaml (cost-optimized)
cat > helm-values.yaml << 'HELM'
replicaCount: 1

resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 3
  targetCPUUtilizationPercentage: 70
HELM

# Deploy with Helm
helm install pepperjavis-agent ./chart -n pepperjavis -f helm-values.yaml
```

## Security Considerations

1. **Network Policies**: Restrict pod-to-pod communication
2. **RBAC**: Limit service account permissions
3. **Secrets**: Store credentials in Kubernetes Secrets
4. **Image Security**: Use private registries with authentication

## Monitoring & Observability

The deployment includes:
- Prometheus metrics endpoint at `/metrics`
- Jaeger tracing integration
- Health checks (liveness & readiness probes)
- Pod logs accessible via `kubectl logs`

```bash
# Port-forward to local Grafana
kubectl port-forward -n pepperjavis svc/grafana 3000:3000

# Access at http://localhost:3000
```

## Emergency Scaling Up

If you need to scale to maximum capacity quickly:

```bash
# Scale pods to max
kubectl scale deployment pepperjavis-agent -n pepperjavis --replicas=3

# Scale nodes to max
exo compute sks nodepool scale pepperjavis-agent default \
  --zone=ch-gva-2 \
  --size=3

# Monitor scaling progress
watch kubectl get pods,nodes -n pepperjavis
```

## Cost Reduction - Scaling to Idle

```bash
# Scale pods to minimum
kubectl scale deployment pepperjavis-agent -n pepperjavis --replicas=1

# Scale nodes to minimum (or 0 if cluster autoscaling is enabled)
exo compute sks nodepool scale pepperjavis-agent default \
  --zone=ch-gva-2 \
  --size=0

# Verify reduction
kubectl get pods,nodes
```

## Cleanup

```bash
# Delete deployment
kubectl delete namespace pepperjavis

# Delete SKS cluster (WARNING: This is permanent!)
exo compute sks delete pepperjavis-agent --zone=ch-gva-2 --force
```

## References

- [Exoscale SKS Documentation](https://community.exoscale.com/documentation/)
- [Kubernetes HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Exoscale CSI Documentation](https://github.com/exoscale/exoscale-csi-driver)

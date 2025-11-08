#!/bin/bash

# SKS Deployment Script for PepperJarvis Agent
# Cost-Optimized: Minimal idle costs, massive scalability on demand

set -e

source ~/.env.local

CLUSTER_NAME="pepperjavis-agent"
CLUSTER_DESCRIPTION="PepperJarvis Agent - Cost-Optimized Kubernetes Cluster"
ZONE="ch-gva-2"
KUBERNETES_VERSION="latest"

echo "🚀 Creating SKS Cluster: $CLUSTER_NAME"
echo "📍 Zone: $ZONE"
echo "📊 Service Level: starter (minimal idle cost)"
echo "⚙️  Initial Nodepool: 1 small node (will auto-scale 0-3)"
echo ""

# Create SKS cluster with cost-optimization
exo compute sks create $CLUSTER_NAME \
  --zone=$ZONE \
  --description="$CLUSTER_DESCRIPTION" \
  --service-level=starter \
  --kubernetes-version=$KUBERNETES_VERSION \
  --cni=cilium \
  --exoscale-csi \
  --auto-upgrade \
  --enable-kube-proxy \
  --nodepool-name=default \
  --nodepool-instance-type=standard.small \
  --nodepool-size=1 \
  --nodepool-disk-size=50

echo ""
echo "✅ SKS Cluster created successfully!"
echo ""
echo "📝 Next Steps:"
echo "1. Get kubeconfig: exo compute sks kubeconfig $CLUSTER_NAME --zone=$ZONE > ~/.kube/pepperjavis-agent.yaml"
echo "2. Export: export KUBECONFIG=~/.kube/pepperjavis-agent.yaml"
echo "3. Deploy PepperJarvis Agent to Kubernetes"
echo ""
echo "💡 Cost Optimization Tips:"
echo "   - Starter control plane: $0.10/day (vs PRO $0.30/day)"
echo "   - Nodes auto-scale to 0 when not in use"
echo "   - Deploy HPA for automatic scaling based on load"

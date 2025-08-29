"""
Test configuration for K8s analyzer tests.
"""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_k8s_dir():
    """Create a temporary directory with sample K8s resources for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        k8s_dir = Path(temp_dir) / "k8s-sample"
        k8s_dir.mkdir()
        
        # Create a simple test deployment
        deployment_file = k8s_dir / "test-deployment.yaml"
        deployment_file.write_text("""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-deployment
  namespace: test-ns
  labels:
    app: test
spec:
  replicas: 1
  selector:
    matchLabels:
      app: test
  template:
    metadata:
      labels:
        app: test
        tier: web
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
        env:
        - name: APP_ENV
          value: "test"
        envFrom:
        - secretRef:
            name: test-secret
        volumeMounts:
        - name: config
          mountPath: /etc/config
      volumes:
      - name: config
        configMap:
          name: test-config
      serviceAccountName: test-sa
---
apiVersion: v1
kind: Service
metadata:
  name: test-service
  namespace: test-ns
  labels:
    app: test
spec:
  type: ClusterIP
  selector:
    app: test
    tier: web
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
    name: http
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: test-config
  namespace: test-ns
  labels:
    app: test
data:
  nginx.conf: |
    server {
        listen 80;
        server_name localhost;
        location / {
            root /usr/share/nginx/html;
            index index.html;
        }
    }
  app.config: |
    {
      "environment": "test",
      "debug": true
    }
---
apiVersion: v1
kind: Secret
metadata:
  name: test-secret
  namespace: test-ns
  labels:
    app: test
type: Opaque
data:
  api-key: dGVzdC1hcGkta2V5  # test-api-key
  database-url: dGVzdC1kYi11cmw=  # test-db-url
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: test-sa
  namespace: test-ns
  labels:
    app: test
automountServiceAccountToken: true
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: test-role
  namespace: test-ns
  labels:
    app: test
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: test-role-binding
  namespace: test-ns
  labels:
    app: test
subjects:
- kind: ServiceAccount
  name: test-sa
  namespace: test-ns
roleRef:
  kind: Role
  name: test-role
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: test-hpa
  namespace: test-ns
  labels:
    app: test
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: test-deployment
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: test-pdb
  namespace: test-ns
  labels:
    app: test
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: test
      tier: web
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: test-network-policy
  namespace: test-ns
  labels:
    app: test
spec:
  podSelector:
    matchLabels:
      app: test
      tier: web
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 80
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-pvc
  namespace: test-ns
  labels:
    app: test
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  storageClassName: fast-ssd
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: test-pv
  labels:
    app: test
spec:
  capacity:
    storage: 1Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: fast-ssd
  claimRef:
    apiVersion: v1
    kind: PersistentVolumeClaim
    name: test-pvc
    namespace: test-ns
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
  labels:
    storage-type: fast
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  encrypted: "true"
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
""")
        
        yield str(k8s_dir)


@pytest.fixture
def sample_resources():
    """Sample K8s resources for testing individual components."""
    return [
        {
            'kind': 'Deployment',
            'name': 'test-deployment',
            'namespace': 'test-ns',
            'labels': {'app': 'test', 'tier': 'web'},
            'pod_template': {
                'labels': {'app': 'test', 'tier': 'web'},
                'containers': [
                    {
                        'name': 'nginx',
                        'image': 'nginx:alpine',
                        'ports': [{'containerPort': 80}],
                        'env': [
                            {
                                'name': 'APP_ENV',
                                'valueFrom': {
                                    'configMapKeyRef': {'name': 'test-config'}
                                }
                            }
                        ],
                        'envFrom': [
                            {'secretRef': {'name': 'test-secret'}}
                        ],
                        'volumeMounts': [
                            {'name': 'config', 'mountPath': '/etc/config'}
                        ]
                    }
                ],
                'volumes': [
                    {'name': 'config', 'configMap': {'name': 'test-config'}}
                ],
                'serviceAccountName': 'test-sa'
            }
        },
        {
            'kind': 'Service',
            'name': 'test-service',
            'namespace': 'test-ns',
            'labels': {'app': 'test'},
            'selectors': {'app': 'test', 'tier': 'web'},
            'ports': [
                {'port': 80, 'targetPort': 80, 'protocol': 'TCP', 'name': 'http'}
            ]
        },
        {
            'kind': 'ConfigMap',
            'name': 'test-config',
            'namespace': 'test-ns',
            'labels': {'app': 'test'},
            'raw_resource': {
                'data': {
                    'nginx.conf': 'server { listen 80; }',
                    'app.config': '{"environment": "test"}'
                }
            }
        },
        {
            'kind': 'Secret',
            'name': 'test-secret',
            'namespace': 'test-ns',
            'labels': {'app': 'test'},
            'raw_resource': {
                'type': 'Opaque',
                'data': {
                    'api-key': 'dGVzdC1hcGkta2V5',
                    'database-url': 'dGVzdC1kYi11cmw='
                }
            }
        },
        {
            'kind': 'ServiceAccount',
            'name': 'test-sa',
            'namespace': 'test-ns',
            'labels': {'app': 'test'},
            'raw_resource': {
                'automountServiceAccountToken': True
            }
        }
    ]


@pytest.fixture
def mock_llm_config():
    """Mock LLM configuration for testing."""
    return {
        'provider': 'openai',
        'model': 'gpt-4',
        'temperature': 0.3
    }

"""
Kubernetes control hints mapping for NIST SP 800-53 Rev. 5

This module provides SIMPLE TOKEN hints (whitespace-delimited) that commonly
appear in Kubernetes/Argo CD manifests. It mirrors the shape of your existing
control_hints.py by exposing one list variable per control (e.g., ac6, sc7, si7_1).
Your existing enumerator will pick these up as "generic" hints when scanning
YAML because it lowercases both the file tokens and the hint tokens.

IMPORTANT tokenization note (to maximize matches against YAML):
- For YAML keys, we include both the plain key and the key with a trailing ':'
  where helpful (e.g., 'securityContext' and 'securityContext:').
- We avoid multi-word tokens like 'privileged: true' since your enumerator
  splits on whitespace. Matching 'privileged:' is still a useful hint.
- We include common CRD kinds/annotations for Argo CD, Istio, Kyverno, Gatekeeper,
  Sigstore/Cosign, External Secrets, and Pod Security Admission.

Generated on: 2025-08-26T19:19:17
"""

# -----------------------------------------------------------------------------
# ACCESS CONTROL (AC)
# -----------------------------------------------------------------------------

# AC-2: Account Management – service accounts and related secrets/tokens
ac2 = [
    "ServiceAccount",                # Use of distinct workload identities
    "serviceAccountName", "serviceAccountName:",
    "serviceAccount", "serviceAccount:",
    "automountServiceAccountToken", "automountServiceAccountToken:",
    "kubernetes.io/service-account-token",  # Secret type (legacy tokens)
    "bound-service-account-token",          # Bound tokens feature (hint term)
    "projected", "projected:",              # Projected SA token volume
    "token",                                # Generic token reference in Secret/Env
]

# AC-3: Access Enforcement – RBAC primitives
ac3 = [
    "rbac.authorization.k8s.io",
    "Role", "ClusterRole", "RoleBinding", "ClusterRoleBinding",
    "roles.rbac.authorization.k8s.io", "clusterroles.rbac.authorization.k8s.io",
    "rolebindings.rbac.authorization.k8s.io", "clusterrolebindings.rbac.authorization.k8s.io",
    "verbs:", "resources:", "resourceNames:", "apiGroups:", "subjects:",
]

# AC-4: Information Flow Enforcement – Network segmentation & policies
ac4 = [
    "NetworkPolicy", "networking.k8s.io/v1",
    "policyTypes:", "ingress:", "egress:", "podSelector:", "namespaceSelector:", "ipBlock:",
    "from:", "to:", "ports:",
]

# AC-6: Least Privilege – container & pod hardening knobs
ac6 = [
    "securityContext", "securityContext:",
    "runAsNonRoot", "runAsNonRoot:",
    "readOnlyRootFilesystem", "readOnlyRootFilesystem:",
    "allowPrivilegeEscalation", "allowPrivilegeEscalation:",
    "capabilities", "capabilities:", "drop:", "add:",
    "seccompProfile", "seccompProfile:",
    "procMount", "procMount:",
    "privileged", "privileged:",
    "hostNetwork", "hostNetwork:",
    "hostPID", "hostPID:",
    "hostIPC", "hostIPC:",
    "hostPort", "hostPort:",
    "hostPath", "hostPath:",
    "shareProcessNamespace", "shareProcessNamespace:",
    "automountServiceAccountToken", "automountServiceAccountToken:",
    # Pod Security Admission & legacy PodSecurityPolicy indicators (policy-based least privilege)
    "pod-security.kubernetes.io/enforce", "pod-security.kubernetes.io/enforce:",
    "pod-security.kubernetes.io/warn", "pod-security.kubernetes.io/audit",
    "restricted", "baseline",  # common PSA levels
    "policy/v1beta1", "PodSecurityPolicy",  # legacy PSP (still seen in older clusters/manifests)
    # AppArmor (node-based hardening)
    "container.apparmor.security.beta.kubernetes.io/",
    # Seccomp default
    "RuntimeDefault", "runtime/default",
]

# -----------------------------------------------------------------------------
# IDENTIFICATION & AUTHENTICATION (IA)
# -----------------------------------------------------------------------------

# IA-2: Identification and Authentication (organizational users) – proxies via workload identity
ia2 = [
    "ServiceAccount", "serviceAccountName:", "serviceAccount:",
    "imagePullSecrets", "imagePullSecrets:",  # auth to private registries
    "auth-provider", "oidc", "oidc:",         # hints for cluster OIDC (rare in app manifests)
]

# IA-5: Authenticator Management – secret material and credentials
ia5 = [
    "Secret", "Secret:", "kind: Secret",
    "stringData:", "data:", "secretKeyRef:", "valueFrom:", "envFrom:",
    "kubernetes.io/tls", "tls.crt", "tls.key",
    "kubernetes.io/basic-auth", "kubernetes.io/ssh-auth",
    "external-secrets.io", "ExternalSecret", "ClusterSecretStore", "SecretStore",
    "secrets-store.csi.k8s.io", "SecretProviderClass", "SecretProviderClass:",
]

# -----------------------------------------------------------------------------
# AUDIT & ACCOUNTABILITY (AU)
# -----------------------------------------------------------------------------

# AU-12: Audit Generation – common logging/collection sidecars and monitors
au12 = [
    "fluent-bit", "fluentd", "vector", "filebeat", "logstash", "promtail",
    "sidecar", "sidecar:", "stdout", "stderr",
    "otel-collector", "OpenTelemetryCollector", "opentelemetry.io",
]

# -----------------------------------------------------------------------------
# CONFIGURATION MANAGEMENT (CM)
# -----------------------------------------------------------------------------

# CM-2: Baseline Configuration – Argo CD desired state and pinning
cm2 = [
    "argoproj.io/v1alpha1", "Application",
    "spec:", "source:", "repoURL:", "targetRevision:", "path:", "directory:",
    "helm:", "values:", "valueFiles:", "kustomize:", "images:",
    "revisionHistoryLimit:", "argocd.argoproj.io/tracking-id",
    "recurse:", "directory.recurse:", "plugin:", "configManagementPlugins",
]

# CM-3: Configuration Change Control – Argo CD sync policy & validation
cm3 = [
    "syncPolicy:", "automated:", "prune:", "selfHeal:", "retry:", "syncOptions:",
    "managedNamespaceMetadata:", "resourceAnnotations:",
    "argocd.argoproj.io/compare-options", "IgnoreDifferences",
    "Validate=", "CreateNamespace=", "PrunePropagationPolicy=", "PruneLast=", "ApplyOutOfSyncOnly=",
]

# CM-5: Access Restrictions for Change – protecting config surfaces
cm5 = [
    "argocd.argoproj.io/manifest-generate-paths",    # restrict path scope
    "argocd.argoproj.io/sync-options",               # enforce/relax server-side checks
    "SkipDryRunOnMissingResource=",                  # beware: can bypass validation
    "Replace=true",                                  # server-side apply replace
]

# CM-6: Configuration Settings – policy as code (Kyverno/Gatekeeper/PSA)
cm6 = [
    "pod-security.kubernetes.io/enforce", "pod-security.kubernetes.io/warn", "pod-security.kubernetes.io/audit",
    "restricted", "baseline",
    "templates.gatekeeper.sh", "constraints.gatekeeper.sh", "ConstraintTemplate", "K8sPSP",
    "policies.kyverno.io", "ClusterPolicy", "Policy",
    "validate:", "mutate:", "verifyImages:", "validationFailureAction:",
]

# CM-7: Least Functionality – disable/avoid high-privilege & host access
cm7 = [
    "readOnlyRootFilesystem", "readOnlyRootFilesystem:",
    "capabilities:", "capabilities", "drop:", "add:",
    "privileged", "privileged:",
    "hostNetwork", "hostNetwork:", "hostPID", "hostPID:", "hostIPC", "hostIPC:",
    "hostPath", "hostPath:", "hostPort", "hostPort:",
    "mountPropagation", "mountPropagation:",
    "allowPrivilegeEscalation", "allowPrivilegeEscalation:",
]

# -----------------------------------------------------------------------------
# CONTINGENCY PLANNING / RESILIENCY (CP, SC-5)
# -----------------------------------------------------------------------------

# CP-10: System Recovery and Reconstitution – probes, rollouts, PDB
cp10 = [
    "livenessProbe", "livenessProbe:",
    "readinessProbe", "readinessProbe:",
    "startupProbe", "startupProbe:",
    "strategy:", "rollingUpdate:", "maxUnavailable:", "maxSurge:",
    "PodDisruptionBudget", "minAvailable:", "maxUnavailable:",
    "topologySpreadConstraints", "topologySpreadConstraints:",
    "affinity:", "podAntiAffinity:", "nodeAffinity:", "tolerations:",
]

# SC-5: Denial-of-Service Protection – resource control and throttling
sc5 = [
    "resources:", "limits:", "requests:", "cpu", "memory",
    "LimitRange", "ResourceQuota",
    "nginx.ingress.kubernetes.io/limit-rps", "nginx.ingress.kubernetes.io/limit-connections",
    "priorityClassName", "PriorityClass",
]

# -----------------------------------------------------------------------------
# SYSTEM & COMMUNICATIONS PROTECTION (SC)
# -----------------------------------------------------------------------------

# SC-7: Boundary Protection – network boundaries and ingress/egress control
sc7 = [
    "NetworkPolicy", "policyTypes:", "ingress:", "egress:", "from:", "to:", "ipBlock:",
    "Ingress", "IngressClass", "ingressClassName",
    "nginx.ingress.kubernetes.io/whitelist-source-range",
]

# SC-8: Transmission Confidentiality & Integrity – TLS in mesh/ingress
sc8 = [
    "tls:", "secretName:", "kubernetes.io/tls", "https",
    "nginx.ingress.kubernetes.io/ssl-redirect", "nginx.ingress.kubernetes.io/backend-protocol",
    "alb.ingress.kubernetes.io/listen-ports", "service.beta.kubernetes.io/aws-load-balancer-ssl-cert",
    "istio", "PeerAuthentication", "DestinationRule", "ISTIO_MUTUAL", "STRICT",
    "linkerd.io/inject", "linkerd.io/inject:",
]

# SC-12: Cryptographic Key Establishment & Management – cert managers & issuers
sc12 = [
    "cert-manager.io/v1", "Certificate", "Issuer", "ClusterIssuer",
    "acme:", "privateKey:", "issuerRef:", "certificateRef:",
    "kubernetes.io/tls", "tls.key", "tls.crt",
]

# SC-13: Cryptographic Protection – mTLS and service mesh policy
sc13 = [
    "PeerAuthentication", "mtls:", "mode:", "STRICT", "PERMISSIVE",
    "DestinationRule", "trafficPolicy:", "tls:", "ISTIO_MUTUAL",
    "sidecar.istio.io/inject", "sidecar.istio.io/inject:",
    "peer-authentication.istio.io", "authentication.istio.io",
]

# SC-28: Protection of Information at Rest – secrets and encryption
sc28 = [
    "SealedSecret", "bitnami.com/v1alpha1", "encryptedData:",
    "sops", "sops:", "age", "age-encryption.org",
    "external-secrets.io", "ExternalSecret", "SecretStore", "ClusterSecretStore",
    "secrets-store.csi.k8s.io", "SecretProviderClass",
    "kms", "KMSKeyID", "encryptionKey", "keyvault", "gcp-kms", "aws-kms",
]

# -----------------------------------------------------------------------------
# SYSTEM & INFORMATION INTEGRITY (SI) / SUPPLY CHAIN (SA-12)
# -----------------------------------------------------------------------------

# SI-2: Flaw Remediation – image update hygiene and pull behavior
si2 = [
    "imagePullPolicy:", "Always",
    "strategy:", "rollingUpdate:", "maxUnavailable:", "maxSurge:",
]

# SI-3: Malicious Code Protection – scanners/agents
si3 = [
    "trivy", "grype", "anchore", "clair",
    "starboard", "kubescape",
    "falco", "falcosidekick",  # runtime threat detection
]

# SI-4: System Monitoring – metrics & traces
si4 = [
    "ServiceMonitor", "PodMonitor", "monitoring.coreos.com/v1",
    "prometheus.io/scrape", "prometheus.io/scrape:",
    "OpenTelemetryCollector", "otel-collector", "opentelemetry.io",
    "kube-state-metrics",
]

# SI-7: Software, Firmware, and Information Integrity – image pinning/signing
si7 = [
    "@sha256:", "digest:", "imageDigest",   # immutable image references
    "cosign", "cosigned", "policy.sigstore.dev", "clusterimagepolicy",
    "rekor", "fulcio", "sigstore", "in-toto", "provenance", "slsa",
    "kyverno.io/verifyImages", "verifyImages:",
]

# SA-12: Supply Chain Protection – signature/policy controls
sa12 = [
    "cosign", "cosigned", "policy.sigstore.dev", "clusterimagepolicy",
    "attestor", "attestors:", "fulcio", "rekor", "sigstore",
    "verifyImages:", "kyverno.io/verifyImages",
]

# RA-5: Vulnerability Monitoring and Scanning – image scanners & policies
ra5 = [
    "trivy", "grype", "anchore", "clair",
    "starboard", "kubescape", "polaris",
    "ImagePolicyWebhook", "imagepolicy.k8s.io",  # legacy admission
]

# -----------------------------------------------------------------------------
# Optional: helpful groupings (not used by the enumerator, but handy for testing)
# -----------------------------------------------------------------------------

K8S_PRIMARY_RESOURCES = [
    "Deployment", "StatefulSet", "DaemonSet", "ReplicaSet", "Pod",
    "Service", "Ingress", "ConfigMap", "Secret", "ServiceAccount",
    "Role", "ClusterRole", "RoleBinding", "ClusterRoleBinding",
    "NetworkPolicy", "PodDisruptionBudget",
    "PersistentVolumeClaim", "PersistentVolume", "StorageClass",
    "Application",  # Argo CD
]

CONTROL_TO_PRIMARY_RESOURCE_HINT = {
    "ac2": ["ServiceAccount", "Secret"],
    "ac3": ["Role", "RoleBinding", "ClusterRole", "ClusterRoleBinding"],
    "ac4": ["NetworkPolicy"],
    "ac6": ["Deployment", "Pod"],
    "ia2": ["ServiceAccount"],
    "ia5": ["Secret", "ExternalSecret", "SecretProviderClass"],
    "au12": ["Deployment", "DaemonSet"],
    "cm2": ["Application"],
    "cm3": ["Application"],
    "cm5": ["Application"],
    "cm6": ["ClusterPolicy", "ConstraintTemplate"],
    "cm7": ["Deployment", "Pod"],
    "cp10": ["Deployment", "PodDisruptionBudget"],
    "sc5": ["LimitRange", "ResourceQuota"],
    "sc7": ["NetworkPolicy", "Ingress"],
    "sc8": ["Ingress", "DestinationRule", "PeerAuthentication"],
    "sc12": ["Certificate", "Issuer", "ClusterIssuer"],
    "sc13": ["PeerAuthentication", "DestinationRule"],
    "sc28": ["SealedSecret", "ExternalSecret", "SecretProviderClass"],
    "si2": ["Deployment"],
    "si3": ["DaemonSet", "Deployment"],
    "si4": ["ServiceMonitor", "PodMonitor"],
    "si7": ["Deployment"],
    "sa12": ["ClusterImagePolicy", "Policy"],
    "ra5": ["Deployment", "AdmissionConfiguration"],
}

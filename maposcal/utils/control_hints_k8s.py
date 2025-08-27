"""
Kubernetes control hints mapping for NIST SP 800-53 Rev. 5

This file contains Kubernetes-specific control hints that help identify
relevant security controls in Kubernetes manifests and Argo CD configurations.
"""

# AC-2: Account Management
ac2 = [
    "ServiceAccount", "serviceAccountName", "serviceAccount",
    "imagePullSecrets", "imagePullSecrets",
    "auth-provider", "oidc", "oidc",
    "serviceAccountName", "serviceAccount",
    "imagePullSecrets", "imagePullSecrets",
    "auth-provider", "oidc", "oidc",
]

# AC-3: Access Enforcement
ac3 = [
    "rbac", "RBAC", "Role", "role", "ClusterRole", "clusterRole",
    "RoleBinding", "roleBinding", "ClusterRoleBinding", "clusterRoleBinding",
    "ServiceAccount", "serviceAccount", "permissions", "rules",
    "apiGroups", "resources", "verbs", "subjects",
]

# AC-4: Information Flow Enforcement
ac4 = [
    "NetworkPolicy", "networkPolicy", "ingress", "egress",
    "podSelector", "namespaceSelector", "ipBlock", "ports",
    "protocol", "from", "to", "allow", "deny",
]

# AC-6: Least Privilege
ac6 = [
    "securityContext", "runAsNonRoot", "runAsUser", "runAsGroup",
    "fsGroup", "supplementalGroups", "allowPrivilegeEscalation",
    "capabilities", "drop", "add", "privileged", "readOnlyRootFilesystem",
    "runAsNonRoot", "runAsUser", "runAsGroup", "fsGroup",
    "supplementalGroups", "allowPrivilegeEscalation", "capabilities",
    "drop", "add", "privileged", "readOnlyRootFilesystem",
]

# AC-7: Unsuccessful Logon Attempts
ac7 = [
    "loginAttempts", "lockoutThreshold", "accountLockout",
    "maxLoginAttempts", "lockoutDuration", "failedLoginAttempts",
]

# AC-10: Concurrent Session Control
ac10 = [
    "maxSessions", "concurrentSessions", "sessionLimit",
    "maxConcurrentSessions", "sessionTimeout", "idleTimeout",
]

# AC-12: Session Termination
ac12 = [
    "logout", "sessionTimeout", "idleTimeout", "maxSessionTime",
    "sessionTermination", "logoutTimeout", "inactivityTimeout",
]

# AC-17: Remote Access
ac17 = [
    "ssh", "vpn", "remoteDesktop", "remoteAccess",
    "externalAccess", "ingress", "loadBalancer", "NodePort",
]

# IA-2: Identification and Authentication (organizational users) – proxies via workload identity
ia2 = [
    "ServiceAccount", "serviceAccountName", "serviceAccount",
    "imagePullSecrets", "imagePullSecrets",
    "auth-provider", "oidc", "oidc",
    "authentication", "identity", "credentials", "tokens",
]

# IA-5: Authenticator Management
ia5 = [
    "passwordPolicy", "keyRotation", "tokenLifetime", "secretRotation",
    "imagePullSecrets", "secrets", "configMaps", "credentials",
    "passwordExpiration", "keyExpiration", "tokenExpiration",
]

# AU-12: Audit Log Generation
au12 = [
    "audit", "logging", "logs", "logLevel", "logFormat",
    "auditLog", "auditPolicy", "auditConfig", "logRetention",
    "logRotation", "logShipping", "syslog", "fluentd",
]

# CM-2: Baseline Configuration
cm2 = [
    "baseline", "configuration", "config", "settings", "defaults",
    "baselineConfig", "baseConfig", "defaultConfig", "standardConfig",
    "configurationBaseline", "baselineSettings",
]

# CM-3: Configuration Change Control
cm3 = [
    "changeControl", "configChange", "versionControl", "git",
    "changeManagement", "configVersion", "deploymentStrategy",
    "rollingUpdate", "recreate", "blueGreen", "canary",
]

# CM-5: Access Restrictions for Change
cm5 = [
    "pullRequest", "codeReview", "changeApproval", "mergeRequest",
    "changeControl", "accessRestrictions", "changePermissions",
    "approvalWorkflow", "changeAuthorization",
]

# CM-6: Configuration Settings
cm6 = [
    "configSettings", "systemSettings", "runtimeConfig", "sysctl",
    "configurationSettings", "systemConfiguration", "runtimeSettings",
    "kernelParams", "systemParameters",
]

# CM-7: Least Functionality
cm7 = [
    "leastFunctionality", "disableServices", "removePackages",
    "minimalInstall", "securityHardening", "unnecessaryServices",
    "disableUnused", "removeUnused", "securityBaseline",
]

# CP-10: Information System Recovery and Reconstitution
cp10 = [
    "backup", "restore", "recovery", "disasterRecovery", "DR",
    "backupStrategy", "restoreStrategy", "recoveryTime", "RTO",
    "recoveryPoint", "RPO", "backupRetention", "snapshots",
]

# SC-5: Denial of Service Protection
sc5 = [
    "rateLimit", "dosProtection", "throttle", "requestLimit",
    "connectionLimit", "bandwidthLimit", "resourceQuotas",
    "requestThrottling", "connectionThrottling",
]

# SC-7: Boundary Protection
sc7 = [
    "NetworkPolicy", "networkPolicy", "ingress", "egress",
    "firewall", "securityGroups", "networkIsolation", "podSecurity",
    "namespaceIsolation", "clusterIsolation", "networkSegmentation",
]

# SC-8: Transmission Confidentiality and Integrity
sc8 = [
    "tls", "ssl", "https", "encryption", "certificates",
    "transportSecurity", "secureCommunication", "encryptedTraffic",
    "tlsConfig", "sslConfig", "certificateManagement",
]

# SC-12: Cryptographic Key Establishment and Management
sc12 = [
    "crypto", "encryption", "keys", "certificates", "secrets",
    "keyManagement", "certificateManagement", "secretManagement",
    "encryptionKeys", "signingKeys", "keyRotation",
]

# SC-13: Cryptographic Protection
sc13 = [
    "crypto", "encryption", "cipher", "algorithm", "hash",
    "cryptographicProtection", "encryptionAlgorithm", "hashAlgorithm",
    "cipherSuite", "encryptionStrength",
]

# SC-28: Protection of Information at Rest
sc28 = [
    "encryption", "atRest", "storageEncryption", "diskEncryption",
    "dataEncryption", "persistentVolume", "storageClass",
    "encryptedStorage", "dataProtection", "restEncryption",
]

# SI-2: Flaw Remediation
si2 = [
    "vulnerability", "patch", "update", "upgrade", "securityUpdate",
    "vulnerabilityScan", "patchManagement", "updateManagement",
    "securityPatches", "vulnerabilityRemediation",
]

# SI-3: Malicious Code Protection
si3 = [
    "antivirus", "malware", "scanning", "maliciousCode",
    "malwareProtection", "virusScan", "maliciousCodeScan",
    "securityScanning", "threatDetection",
]

# SI-4: System Monitoring
si4 = [
    "monitoring", "logging", "alerting", "metrics", "observability",
    "systemMonitoring", "performanceMonitoring", "healthChecks",
    "probes", "livenessProbe", "readinessProbe", "startupProbe",
]

# SI-7: Software and Information Integrity
si7 = [
    "integrity", "checksums", "signatures", "verification",
    "codeSigning", "imageSigning", "integrityChecks",
    "signatureVerification", "checksumVerification",
]

# SA-12: Supply Chain Risk Management
sa12 = [
    "supplyChain", "dependencies", "vulnerabilities", "licenses",
    "thirdParty", "vendor", "supplier", "riskAssessment",
    "dependencyScan", "licenseCompliance", "vulnerabilityAssessment",
]

# RA-5: Risk Assessment
ra5 = [
    "riskAssessment", "vulnerabilityAssessment", "threatAssessment",
    "riskAnalysis", "securityAssessment", "complianceAssessment",
    "riskEvaluation", "securityRisk", "threatModeling",
]

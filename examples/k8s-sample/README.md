# Kubernetes Sample Resources for MapOSCAL Testing

This directory contains comprehensive Kubernetes resource manifests that demonstrate all the workload types and resource relationships that the enhanced MapOSCAL K8s analyzer can process.

## Overview

The sample resources cover:
- **All workload types**: Deployment, StatefulSet, DaemonSet, CronJob, Job, and standalone Pod
- **All resource types**: Services, Ingress, ConfigMaps, Secrets, PVCs, PVs, StorageClasses
- **All RBAC components**: ServiceAccounts, Roles, RoleBindings, ClusterRoles, ClusterRoleBindings
- **All resilience features**: HPAs, PDBs, NetworkPolicies
- **Cross-workload relationships**: Shared resources, cross-namespace bindings
- **Storage relationships**: PVC → PV → StorageClass chains

## Resource Structure

### 1. Namespaces (`01-namespace.yaml`)
- `maposcal-demo`: Main application namespace
- `monitoring`: Monitoring and observability namespace

### 2. Webapp Deployment (`02-webapp-deployment.yaml`)
**Workload Type**: Deployment
**Components**:
- Deployment with 3 replicas
- Service (ClusterIP)
- Ingress with host routing
- ConfigMap with nginx configuration
- Secret with API keys
- PVC for persistent storage
- ServiceAccount with RBAC
- HPA for autoscaling
- PDB for disruption protection
- NetworkPolicy for security

**Resource Relationships**:
- Pod template references ConfigMap and Secret
- Service selector matches pod labels
- Ingress backend points to Service
- HPA targets the Deployment
- PDB selector matches pod labels
- NetworkPolicy applies to pods

### 3. Database StatefulSet (`03-database-statefulset.yaml`)
**Workload Type**: StatefulSet
**Components**:
- StatefulSet with 3 replicas
- Service (ClusterIP)
- ConfigMap with PostgreSQL configuration
- Secret with database credentials
- PVC templates for each replica
- ServiceAccount with RBAC
- PDB for disruption protection
- NetworkPolicy for security

**Resource Relationships**:
- Pod template references ConfigMap and Secret
- PVC templates create individual storage for each pod
- Service selector matches pod labels
- PDB selector matches pod labels
- NetworkPolicy applies to pods

### 4. Monitoring DaemonSet (`04-monitoring-daemonset.yaml`)
**Workload Type**: DaemonSet
**Components**:
- DaemonSet for node monitoring
- Service (ClusterIP)
- ConfigMap with collector configuration
- ServiceAccount with cluster-wide RBAC
- NetworkPolicy for security

**Resource Relationships**:
- Pod template references ConfigMap
- Service selector matches pod labels
- ClusterRoleBinding grants cluster-wide permissions
- NetworkPolicy applies to pods

### 5. Backup CronJob (`05-backup-cronjob.yaml`)
**Workload Type**: CronJob
**Components**:
- CronJob with daily schedule
- ConfigMap with backup configuration
- Secret with database and AWS credentials
- ServiceAccount with RBAC

**Resource Relationships**:
- Job template references ConfigMap and Secret
- CronJob creates Jobs, Jobs create Pods
- ServiceAccount used by pod template

### 6. Data Migration Job (`06-data-migration-job.yaml`)
**Workload Type**: Job
**Components**:
- Job for one-time data migration
- ConfigMap with migration scripts and config
- Secret with database credentials
- ServiceAccount with RBAC

**Resource Relationships**:
- Pod template references ConfigMap and Secret
- Job creates Pods
- ServiceAccount used by pod template

### 7. Utility Pod (`07-utility-pod.yaml`)
**Workload Type**: Standalone Pod
**Components**:
- Single Pod for maintenance tasks
- ConfigMap with utility configuration
- Secret with database credentials
- ServiceAccount with RBAC

**Resource Relationships**:
- Pod directly references ConfigMap and Secret
- No workload controller (direct Pod)

### 8. Storage Resources (`08-storage-resources.yaml`)
**Components**:
- StorageClasses (fast-ssd, slow-hdd)
- PersistentVolumes for webapp and postgres
- Volume binding relationships

**Resource Relationships**:
- PVs reference PVCs via claimRef
- PVs specify StorageClass
- PVCs reference StorageClass

### 9. Shared Resources (`09-shared-resources.yaml`)
**Components**:
- Shared ConfigMaps and Secrets
- Shared Services and Ingress
- Shared NetworkPolicies
- Shared RBAC components

**Resource Relationships**:
- Multiple workloads reference same resources
- Cross-namespace RBAC bindings
- Shared selectors across workloads

### 10. Additional RBAC (`10-additional-rbac.yaml`)
**Components**:
- Cluster-wide read permissions for administrative tasks
- Security auditor role for compliance monitoring
- Enhanced RBAC for cross-namespace operations

**Security Features**:
- Least-privilege access control
- Cluster-wide monitoring capabilities
- Compliance and audit support

## Testing MapOSCAL K8s Analyzer

### Basic Analysis
```bash
# Update your config to point to this directory
maposcal k8s-process sample_control_config.yaml
```

### Expected Workloads
The analyzer should identify these workloads:

1. **`maposcal-demo/Deployment/webapp-frontend`**
   - Services: webapp-service
   - Ingress: webapp-ingress
   - ConfigMaps: webapp-config, nginx-config
   - Secrets: webapp-secrets
   - Storage: webapp-data-pvc → webapp-data-pv → fast-ssd
   - RBAC: webapp-sa → webapp-role-binding → webapp-role
   - Resilience: webapp-hpa, webapp-pdb, webapp-network-policy

2. **`maposcal-demo/StatefulSet/postgres-db`**
   - Services: postgres-service
   - ConfigMaps: postgres-config
   - Secrets: postgres-secrets
   - Storage: postgres-data-postgres-db-{0,1,2} → postgres-data-pv-{0,1,2} → fast-ssd
   - RBAC: postgres-sa → postgres-role-binding → postgres-role
   - Resilience: postgres-pdb, postgres-network-policy

3. **`monitoring/DaemonSet/node-exporter`**
   - Services: node-exporter-service
   - ConfigMaps: node-exporter-config
   - RBAC: monitoring-sa → node-exporter-cluster-role-binding → node-exporter-cluster-role
   - Resilience: monitoring-network-policy

4. **`maposcal-demo/CronJob/database-backup`**
   - ConfigMaps: backup-config
   - Secrets: backup-secrets
   - RBAC: backup-sa → backup-role-binding → backup-role

5. **`maposcal-demo/Job/data-migration-v2`**
   - ConfigMaps: migration-scripts, migration-config
   - Secrets: migration-secrets
   - RBAC: migration-sa → migration-role-binding → migration-role

6. **`maposcal-demo/Pod/utility-pod`**
   - ConfigMaps: utility-config
   - Secrets: utility-secrets
   - RBAC: utility-sa → utility-role-binding → utility-role

### Expected Shared Resources
- `shared-config` ConfigMap
- `shared-secrets` Secret
- `shared-service` Service
- `shared-ingress` Ingress
- `shared-network-policy` NetworkPolicy
- `shared-role` Role
- `shared-cluster-role` ClusterRole

### Cross-Namespace Relationships
- Monitoring namespace has cluster-wide RBAC
- Shared ClusterRoleBinding spans both namespaces
- NetworkPolicies reference namespace selectors

## Validation Points

The enhanced analyzer should demonstrate:

1. **Owner Reference Resolution**: CronJob → Job → Pod chains
2. **Storage Resolution**: PVC → PV → StorageClass relationships
3. **RBAC Resolution**: ServiceAccount → Binding → Role chains
4. **Resilience Resolution**: HPA, PDB, NetworkPolicy attachment
5. **Shared Resource Detection**: Resources used by multiple workloads
6. **Conflict Detection**: Selector overlaps, orphaned resources
7. **Cross-Namespace Handling**: Cluster-scoped resources and bindings

## RBAC Improvements for AC-3 and AC-6 Compliance

The Kubernetes sample files have been enhanced with comprehensive RBAC configurations to address NIST 800-53 controls AC-3 (Access Enforcement) and AC-6 (Least Privilege):

### AC-3 (Access Enforcement) - Satisfied Through:
- **ServiceAccount Identity**: Each workload has a dedicated ServiceAccount
- **Role-Based Access Control**: Namespace-scoped Roles with specific permissions
- **Cluster-Wide Permissions**: ClusterRoles for monitoring and administrative tasks
- **Explicit Permission Binding**: RoleBindings and ClusterRoleBindings for access enforcement

### AC-6 (Least Privilege) - Satisfied Through:
- **Minimal Required Permissions**: Each Role contains only necessary permissions
- **Resource-Specific Access**: Permissions limited to specific API groups and resources
- **Verb Restrictions**: Limited to required actions (get, list, watch, patch, update)
- **Namespace Isolation**: Most permissions restricted to workload namespace

### Enhanced RBAC Features:
1. **Workload-Specific Roles**: Customized permissions for each workload type
2. **Event Logging**: Permission to create and patch events for audit trails
3. **Status Updates**: Ability to update pod status for health monitoring
4. **Cross-Resource Access**: Permissions for related resources (PVCs, endpoints)
5. **Batch Operations**: Support for Job and CronJob management
6. **Monitoring Capabilities**: Cluster-wide read access for observability

## Notes

- All resources use realistic configurations and relationships
- Base64 encoded secrets are for demonstration only
- Storage references use AWS EBS provisioner examples
- RBAC rules follow least-privilege principles
- NetworkPolicies demonstrate ingress/egress control
- Resource limits and requests are realistic for development environments

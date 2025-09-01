"""
Kubernetes Analyzer for MapOSCAL.

This module provides specialized analysis of Kubernetes resource YAML files,
creating workload groupings and extracting security-relevant information
for OSCAL component generation.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
import yaml
import json
import hashlib
import datetime
from collections import defaultdict

from maposcal.embeddings import local_embedder, faiss_index, meta_store
from maposcal.utils.metadata import generate_metadata, inject_metadata_into_json

logger = logging.getLogger(__name__)


class OwnerReferenceResolver:
    """
    Resolves owner references and expands workload seeds to include child resources.
    """
    
    def __init__(self):
        self.by_key = {}  # (kind, name, namespace) -> object
        self.owners_of = {}  # uid -> [child objects]
    
    def build_owner_graph(self, resources: List[Dict[str, Any]]):
        """
        Build owner reference indices for efficient lookup.
        
        Args:
            resources: List of parsed K8s resources
        """
        # Build byKey index
        for resource in resources:
            key = (resource['kind'], resource['name'], resource['namespace'])
            self.by_key[key] = resource
        
        # Build ownersOf index
        for resource in resources:
            owner_refs = resource.get('raw_resource', {}).get('metadata', {}).get('ownerReferences', [])
            for owner_ref in owner_refs:
                owner_uid = owner_ref.get('uid')
                if owner_uid:
                    if owner_uid not in self.owners_of:
                        self.owners_of[owner_uid] = []
                    self.owners_of[owner_uid].append(resource)
    
    def expand_workload_children(self, seed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expand a workload seed to include all child resources.
        
        Args:
            seed: Workload seed resource
            
        Returns:
            Dictionary with expanded children information
        """
        children = {
            'pods': {'materialized': False, 'items': [], 'template_labels': seed.get('pod_template', {}).get('labels', {})},
            'replicaSets': [],
            'jobs': []
        }
        
        seed_uid = seed.get('raw_resource', {}).get('metadata', {}).get('uid')
        if not seed_uid:
            return children
        
        # Find children based on seed type
        if seed['kind'] == 'Deployment':
            children.update(self._expand_deployment_children(seed_uid))
        elif seed['kind'] == 'StatefulSet':
            children.update(self._expand_statefulset_children(seed_uid))
        elif seed['kind'] == 'DaemonSet':
            children.update(self._expand_daemonset_children(seed_uid))
        elif seed['kind'] == 'CronJob':
            children.update(self._expand_cronjob_children(seed_uid))
        elif seed['kind'] == 'Job':
            children.update(self._expand_job_children(seed_uid))
        elif seed['kind'] == 'Pod':
            children['pods']['materialized'] = True
            children['pods']['items'].append(seed['name'])
        
        return children
    
    def _expand_deployment_children(self, deployment_uid: str) -> Dict[str, Any]:
        """Expand Deployment → ReplicaSet → Pod chain."""
        children = {'replicaSets': [], 'pods': {'materialized': False, 'items': []}}
        
        # Find ReplicaSets owned by this Deployment
        replica_sets = self.owners_of.get(deployment_uid, [])
        for rs in replica_sets:
            if rs['kind'] == 'ReplicaSet':
                children['replicaSets'].append(rs['name'])
                
                # Find Pods owned by this ReplicaSet
                rs_uid = rs.get('raw_resource', {}).get('metadata', {}).get('uid')
                if rs_uid:
                    pods = self.owners_of.get(rs_uid, [])
                    for pod in pods:
                        if pod['kind'] == 'Pod':
                            children['pods']['items'].append(pod['name'])
                            children['pods']['materialized'] = True
        
        return children
    
    def _expand_statefulset_children(self, statefulset_uid: str) -> Dict[str, Any]:
        """Expand StatefulSet → Pod chain."""
        children = {'pods': {'materialized': False, 'items': []}}
        
        pods = self.owners_of.get(statefulset_uid, [])
        for pod in pods:
            if pod['kind'] == 'Pod':
                children['pods']['items'].append(pod['name'])
                children['pods']['materialized'] = True
        
        return children
    
    def _expand_daemonset_children(self, daemonset_uid: str) -> Dict[str, Any]:
        """Expand DaemonSet → Pod chain."""
        children = {'pods': {'materialized': False, 'items': []}}
        
        pods = self.owners_of.get(daemonset_uid, [])
        for pod in pods:
            if pod['kind'] == 'Pod':
                children['pods']['items'].append(pod['name'])
                children['pods']['materialized'] = True
        
        return children
    
    def _expand_cronjob_children(self, cronjob_uid: str) -> Dict[str, Any]:
        """Expand CronJob → Job → Pod chain."""
        children = {'jobs': [], 'pods': {'materialized': False, 'items': []}}
        
        # Find Jobs owned by this CronJob
        jobs = self.owners_of.get(cronjob_uid, [])
        for job in jobs:
            if job['kind'] == 'Job':
                children['jobs'].append(job['name'])
                
                # Find Pods owned by this Job
                job_uid = job.get('raw_resource', {}).get('metadata', {}).get('uid')
                if job_uid:
                    pods = self.owners_of.get(job_uid, [])
                    for pod in pods:
                        if pod['kind'] == 'Pod':
                            children['pods']['items'].append(pod['name'])
                            children['pods']['materialized'] = True
        
        return children
    
    def _expand_job_children(self, job_uid: str) -> Dict[str, Any]:
        """Expand Job → Pod chain."""
        children = {'pods': {'materialized': False, 'items': []}}
        
        pods = self.owners_of.get(job_uid, [])
        for pod in pods:
            if pod['kind'] == 'Pod':
                children['pods']['items'].append(pod['name'])
                children['pods']['materialized'] = True
        
        return children


class StorageResolver:
    """
    Resolves storage relationships: PVC → PV → StorageClass.
    """
    
    def __init__(self):
        self.pvc_by_name = {}  # (namespace, name) -> PVC
        self.pv_by_name = {}   # name -> PV
        self.sc_by_name = {}   # name -> StorageClass
    
    def build_storage_indices(self, resources: List[Dict[str, Any]]):
        """
        Build storage resource indices.
        
        Args:
            resources: List of parsed K8s resources
        """
        for resource in resources:
            if resource['kind'] == 'PersistentVolumeClaim':
                key = (resource['namespace'], resource['name'])
                self.pvc_by_name[key] = resource
            elif resource['kind'] == 'PersistentVolume':
                self.pv_by_name[resource['name']] = resource
            elif resource['kind'] == 'StorageClass':
                self.sc_by_name[resource['name']] = resource
    
    def resolve_workload_storage(self, workload: Dict[str, Any], resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolve storage resources for a workload.
        
        Args:
            workload: Workload dictionary
            resources: Available resources
            
        Returns:
            Dictionary with storage information
        """
        storage = {
            'pvcs': [],
            'pvs': [],
            'storageClasses': []
        }
        
        # Find PVCs used by the workload's pods
        referenced_pvcs = set()
        
        # Check if we have materialized pods or need to use template
        if workload.get('pods', {}).get('materialized', False):
            # Use actual pod resources
            for pod_name in workload['pods']['items']:
                pod_resource = self._find_pod_resource(pod_name, workload['namespace'], resources)
                if pod_resource:
                    referenced_pvcs.update(self._extract_pvc_references(pod_resource))
        else:
            # Use controller pod template
            controller_resource = self._find_controller_resource(workload, resources)
            if controller_resource:
                referenced_pvcs.update(self._extract_pvc_references(controller_resource))
        
        # Attach referenced PVCs
        for pvc_key in referenced_pvcs:
            if pvc_key in self.pvc_by_name:
                pvc = self.pvc_by_name[pvc_key]
                storage['pvcs'].append({
                    'name': pvc['name'],
                    'storageClassName': pvc.get('raw_resource', {}).get('spec', {}).get('storageClassName'),
                    'accessModes': pvc.get('raw_resource', {}).get('spec', {}).get('accessModes', [])
                })
        
        # Bind PVCs to PVs and StorageClasses
        for pvc in storage['pvcs']:
            pvc_key = (workload['namespace'], pvc['name'])
            if pvc_key in self.pvc_by_name:
                pvc_resource = self.pvc_by_name[pvc_key]
                
                # Find bound PV
                pv_name = pvc_resource.get('raw_resource', {}).get('spec', {}).get('volumeName')
                if pv_name and pv_name in self.pv_by_name:
                    pv = self.pv_by_name[pv_name]
                    storage['pvs'].append({
                        'name': pv['name'],
                        'storageClassName': pv.get('raw_resource', {}).get('spec', {}).get('storageClassName'),
                        'accessModes': pv.get('raw_resource', {}).get('spec', {}).get('accessModes', [])
                    })
                    
                    # Attach StorageClass
                    sc_name = pv.get('raw_resource', {}).get('spec', {}).get('storageClassName')
                    if sc_name and sc_name in self.sc_by_name:
                        sc = self.sc_by_name[sc_name]
                        storage['storageClasses'].append({
                            'name': sc['name'],
                            'provisioner': sc.get('raw_resource', {}).get('provisioner', ''),
                            'volumeBindingMode': sc.get('raw_resource', {}).get('volumeBindingMode', '')
                        })
        
        return storage
    
    def _find_pod_resource(self, pod_name: str, namespace: str, resources: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find a specific pod resource."""
        for resource in resources:
            if (resource['kind'] == 'Pod' and 
                resource['name'] == pod_name and 
                resource['namespace'] == namespace):
                return resource
        return None
    
    def _find_seed_resource(self, workload: Dict[str, Any], resources: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the seed resource for a workload (legacy method for backward compatibility)."""
        for resource in resources:
            if (resource['kind'] == workload.get('seed', {}).get('kind') and
                resource['name'] == workload.get('seed', {}).get('name') and
                resource['namespace'] == workload['namespace']):
                return resource
        return None
    
    def _find_controller_resource(self, workload: Dict[str, Any], resources: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the controller resource for a workload."""
        for resource in resources:
            if (resource['kind'] == workload['controller']['kind'] and
                resource['name'] == workload['controller']['name'] and
                resource['namespace'] == workload['namespace']):
                return resource
        return None
    
    def _extract_pvc_references(self, resource: Dict[str, Any]) -> Set[str]:
        """Extract PVC references from a resource's volumes."""
        pvc_refs = set()
        
        volumes = resource.get('pod_template', {}).get('volumes', [])
        if not volumes:
            # Direct pod resource
            volumes = resource.get('raw_resource', {}).get('spec', {}).get('volumes', [])
        
        for volume in volumes:
            if 'persistentVolumeClaim' in volume:
                claim_name = volume['persistentVolumeClaim'].get('claimName')
                if claim_name:
                    pvc_refs.add((resource['namespace'], claim_name))
        
        return pvc_refs


class ResilienceResolver:
    """
    Resolves resilience and network policies: HPA, PDB, NetworkPolicy.
    """
    
    def __init__(self):
        self.hpas = {}  # namespace -> [HPA]
        self.pdbs = {}  # namespace -> [PDB]
        self.network_policies = {}  # namespace -> [NetworkPolicy]
    
    def build_resilience_indices(self, resources: List[Dict[str, Any]]):
        """
        Build resilience resource indices.
        
        Args:
            resources: List of parsed K8s resources
        """
        for resource in resources:
            if resource['kind'] == 'HorizontalPodAutoscaler':
                namespace = resource['namespace']
                if namespace not in self.hpas:
                    self.hpas[namespace] = []
                self.hpas[namespace].append(resource)
            elif resource['kind'] == 'PodDisruptionBudget':
                namespace = resource['namespace']
                if namespace not in self.pdbs:
                    self.pdbs[namespace] = []
                self.pdbs[namespace].append(resource)
            elif resource['kind'] == 'NetworkPolicy':
                namespace = resource['namespace']
                if namespace not in self.network_policies:
                    self.network_policies[namespace] = []
                self.network_policies[namespace].append(resource)
    
    def resolve_workload_resilience(self, workload: Dict[str, Any], resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolve resilience resources for a workload.
        
        Args:
            workload: Workload dictionary
            resources: Available resources
            
        Returns:
            Dictionary with resilience information
        """
        resilience = {
            'hpas': [],
            'pdbs': [],
            'networkPolicies': []
        }
        
        namespace = workload['namespace']
        
        # Resolve HPAs
        if namespace in self.hpas:
            for hpa in self.hpas[namespace]:
                if self._hpa_matches_workload(hpa, workload):
                    resilience['hpas'].append({
                        'name': hpa['name'],
                        'targetRef': hpa.get('raw_resource', {}).get('spec', {}).get('scaleTargetRef', {}),
                        'minReplicas': hpa.get('raw_resource', {}).get('spec', {}).get('minReplicas'),
                        'maxReplicas': hpa.get('raw_resource', {}).get('spec', {}).get('maxReplicas')
                    })
        
        # Resolve PDBs
        if namespace in self.pdbs:
            for pdb in self.pdbs[namespace]:
                if self._pdb_matches_workload(pdb, workload):
                    resilience['pdbs'].append({
                        'name': pdb['name'],
                        'minAvailable': pdb.get('raw_resource', {}).get('spec', {}).get('minAvailable'),
                        'maxUnavailable': pdb.get('raw_resource', {}).get('spec', {}).get('maxUnavailable'),
                        'selector': pdb.get('raw_resource', {}).get('spec', {}).get('selector', {})
                    })
        
        # Resolve NetworkPolicies
        if namespace in self.network_policies:
            for np in self.network_policies[namespace]:
                if self._network_policy_matches_workload(np, workload):
                    resilience['networkPolicies'].append({
                        'name': np['name'],
                        'podSelector': np.get('raw_resource', {}).get('spec', {}).get('podSelector', {}),
                        'policyTypes': np.get('raw_resource', {}).get('spec', {}).get('policyTypes', [])
                    })
        
        return resilience
    
    def _hpa_matches_workload(self, hpa: Dict[str, Any], workload: Dict[str, Any]) -> bool:
        """Check if HPA targets this workload."""
        target_ref = hpa.get('raw_resource', {}).get('spec', {}).get('scaleTargetRef', {})
        return (target_ref.get('kind') == workload['controller']['kind'] and 
                target_ref.get('name') == workload['controller']['name'])
    
    def _pdb_matches_workload(self, pdb: Dict[str, Any], workload: Dict[str, Any]) -> bool:
        """Check if PDB applies to this workload."""
        pdb_selector = pdb.get('raw_resource', {}).get('spec', {}).get('selector', {})
        if not pdb_selector:
            return False
        
        # Check if PDB selector matches workload pods
        workload_labels = workload.get('pods', {}).get('template_labels', {})
        return self._selectors_overlap(pdb_selector, workload_labels)
    
    def _network_policy_matches_workload(self, np: Dict[str, Any], workload: Dict[str, Any]) -> bool:
        """Check if NetworkPolicy applies to this workload."""
        np_selector = np.get('raw_resource', {}).get('spec', {}).get('podSelector', {})
        if not np_selector:
            return False
        
        # Check if NetworkPolicy selector matches workload pods
        workload_labels = workload.get('pods', {}).get('template_labels', {})
        return self._selectors_overlap(np_selector, workload_labels)
    
    def _selectors_overlap(self, selector: Dict[str, Any], labels: Dict[str, Any]) -> bool:
        """Check if selector overlaps with labels."""
        if not selector or not labels:
            return False
        
        # Simple label matching - could be enhanced for complex selectors
        for key, value in selector.items():
            if key in labels and labels[key] == value:
                return True
        
        return False


class RBACResolver:
    """
    Resolves RBAC relationships: ServiceAccount → Role/ClusterRole via Bindings.
    """
    
    def __init__(self):
        self.sa_by_name = {}  # (namespace, name) -> ServiceAccount
        self.role_by_name = {}  # (namespace, name) -> Role
        self.cluster_role_by_name = {}  # name -> ClusterRole
        self.role_binding_by_name = {}  # (namespace, name) -> RoleBinding
        self.cluster_role_binding_by_name = {}  # name -> ClusterRoleBinding
    
    def build_rbac_indices(self, resources: List[Dict[str, Any]]):
        """
        Build RBAC resource indices.
        
        Args:
            resources: List of parsed K8s resources
        """
        logger.info("Building RBAC indices...")
        
        for resource in resources:
            if resource['kind'] == 'ServiceAccount':
                key = (resource['namespace'], resource['name'])
                self.sa_by_name[key] = resource
                logger.debug(f"Indexed ServiceAccount: {key}")
            elif resource['kind'] == 'Role':
                key = (resource['namespace'], resource['name'])
                self.role_by_name[key] = resource
                logger.debug(f"Indexed Role: {key}")
            elif resource['kind'] == 'ClusterRole':
                self.cluster_role_by_name[resource['name']] = resource
                logger.debug(f"Indexed ClusterRole: {resource['name']}")
            elif resource['kind'] == 'RoleBinding':
                key = (resource['namespace'], resource['name'])
                self.role_binding_by_name[key] = resource
                logger.debug(f"Indexed RoleBinding: {key}")
            elif resource['kind'] == 'ClusterRoleBinding':
                self.cluster_role_binding_by_name[resource['name']] = resource
                logger.debug(f"Indexed ClusterRoleBinding: {resource['name']}")
        
        logger.info(f"RBAC indices built: {len(self.sa_by_name)} ServiceAccounts, {len(self.role_by_name)} Roles, {len(self.cluster_role_by_name)} ClusterRoles, {len(self.role_binding_by_name)} RoleBindings, {len(self.cluster_role_binding_by_name)} ClusterRoleBindings")
    
    def resolve_workload_rbac(self, workload: Dict[str, Any], resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolve RBAC resources for a workload.
        
        Args:
            workload: Workload dictionary
            resources: Available resources
            
        Returns:
            Dictionary with RBAC information
        """
        rbac = {
            'serviceAccounts': [],
            'roleBindings': [],
            'roles': [],
            'clusterRoleBindings': [],
            'clusterRoles': [],
            'effectiveRules': {}
        }
        
        # Gather ServiceAccounts used by the workload
        service_accounts = set()
        
        # First check if the workload already has a serviceAccount field populated
        if workload.get('serviceAccount'):
            sa_name = workload['serviceAccount']['name']
            if sa_name != 'default':
                service_accounts.add((workload['namespace'], sa_name))
            else:
                service_accounts.add((workload['namespace'], 'default'))
        else:
            # Fallback: Check controller pod template
            if workload.get('pods', {}).get('template_labels'):
                # This is a fallback - the workload should already have serviceAccount populated
                logger.warning(f"Workload {workload['id']} missing serviceAccount field, using fallback detection")
                sa_name = workload.get('pods', {}).get('template_labels', {}).get('serviceAccountName', 'default')
                if sa_name != 'default':
                    service_accounts.add((workload['namespace'], sa_name))
                else:
                    service_accounts.add((workload['namespace'], 'default'))
            
            # Check materialized pods as additional fallback
            if workload.get('pods', {}).get('materialized', False):
                for pod_name in workload['pods']['items']:
                    pod_resource = self._find_pod_resource(pod_name, workload['namespace'], resources)
                    if pod_resource:
                        sa_name = pod_resource.get('raw_resource', {}).get('spec', {}).get('serviceAccountName', 'default')
                        if sa_name != 'default':
                            service_accounts.add((workload['namespace'], sa_name))
                        else:
                            service_accounts.add((workload['namespace'], 'default'))
        
        # Resolve RBAC for each ServiceAccount
        logger.debug(f"Resolving RBAC for workload {workload['id']} with service accounts: {service_accounts}")
        
        for sa_key in service_accounts:
            if sa_key in self.sa_by_name:
                sa = self.sa_by_name[sa_key]
                logger.debug(f"Found ServiceAccount {sa['name']} for workload {workload['id']}")
                
                rbac['serviceAccounts'].append({
                    'name': sa['name'],
                    'automountServiceAccountToken': sa.get('raw_resource', {}).get('automountServiceAccountToken', True)
                })
                
                # Find RoleBindings that grant to this SA
                self._resolve_role_bindings(sa_key, rbac)
                
                # Find ClusterRoleBindings that grant to this SA
                self._resolve_cluster_role_bindings(sa_key, rbac)
            else:
                logger.warning(f"ServiceAccount {sa_key} not found in RBAC indices for workload {workload['id']}")
        
        logger.debug(f"RBAC resolution complete for workload {workload['id']}: {len(rbac['serviceAccounts'])} SAs, {len(rbac['roles'])} roles, {len(rbac['clusterRoles'])} cluster roles")
        
        # Compute effective rules summary
        rbac['effectiveRules'] = self._compute_effective_rules(rbac)
        
        return rbac
    
    def _resolve_role_bindings(self, sa_key: Tuple[str, str], rbac: Dict[str, Any]):
        """Resolve RoleBindings for a ServiceAccount."""
        namespace, sa_name = sa_key
        logger.debug(f"Resolving RoleBindings for ServiceAccount {sa_name} in namespace {namespace}")
        
        for rb_key, rb in self.role_binding_by_name.items():
            if rb_key[0] == namespace:  # Same namespace
                if self._binding_includes_sa(rb, sa_name, namespace):
                    logger.debug(f"Found RoleBinding {rb['name']} for ServiceAccount {sa_name}")
                    rbac['roleBindings'].append({
                        'name': rb['name'],
                        'roleRef': rb.get('raw_resource', {}).get('roleRef', {})
                    })
                    
                    # Attach the referenced Role
                    role_ref = rb.get('raw_resource', {}).get('roleRef', {})
                    if role_ref.get('kind') == 'Role':
                        role_key = (namespace, role_ref['name'])
                        if role_key in self.role_by_name:
                            role = self.role_by_name[role_key]
                            logger.debug(f"Attached Role {role['name']} with {len(role.get('raw_resource', {}).get('rules', []))} rules")
                            rbac['roles'].append({
                                'name': role['name'],
                                'rules': role.get('raw_resource', {}).get('rules', [])
                            })
                        else:
                            logger.warning(f"Role {role_ref['name']} referenced by RoleBinding {rb['name']} not found in indices")
                else:
                    logger.debug(f"RoleBinding {rb['name']} does not include ServiceAccount {sa_name}")
            else:
                logger.debug(f"RoleBinding {rb['name']} is in different namespace {rb_key[0]}, skipping")
    
    def _resolve_cluster_role_bindings(self, sa_key: Tuple[str, str], rbac: Dict[str, Any]):
        """Resolve ClusterRoleBindings for a ServiceAccount."""
        namespace, sa_name = sa_key
        logger.debug(f"Resolving ClusterRoleBindings for ServiceAccount {sa_name} in namespace {namespace}")
        
        for crb_name, crb in self.cluster_role_binding_by_name.items():
            if self._binding_includes_sa(crb, sa_name, namespace):
                logger.debug(f"Found ClusterRoleBinding {crb_name} for ServiceAccount {sa_name}")
                rbac['clusterRoleBindings'].append({
                    'name': crb_name,
                    'roleRef': crb.get('raw_resource', {}).get('roleRef', {})
                })
                
                # Attach the referenced ClusterRole
                role_ref = crb.get('raw_resource', {}).get('roleRef', {})
                if role_ref.get('kind') == 'ClusterRole':
                    if role_ref['name'] in self.cluster_role_by_name:
                        cr = self.cluster_role_by_name[role_ref['name']]
                        logger.debug(f"Attached ClusterRole {cr['name']} with {len(cr.get('raw_resource', {}).get('rules', []))} rules")
                        rbac['clusterRoles'].append({
                            'name': cr['name'],
                            'rules': cr.get('raw_resource', {}).get('rules', [])
                        })
                    else:
                        logger.warning(f"ClusterRole {role_ref['name']} referenced by ClusterRoleBinding {crb_name} not found in indices")
                else:
                    logger.debug(f"ClusterRoleBinding {crb_name} references non-ClusterRole: {role_ref.get('kind')}")
            else:
                logger.debug(f"ClusterRoleBinding {crb_name} does not include ServiceAccount {sa_name}")
    
    def _binding_includes_sa(self, binding: Dict[str, Any], sa_name: str, sa_namespace: str) -> bool:
        """Check if a binding includes the specified ServiceAccount."""
        subjects = binding.get('raw_resource', {}).get('subjects', [])
        logger.debug(f"Checking binding {binding.get('name', 'unknown')} subjects: {subjects}")
        
        for subject in subjects:
            logger.debug(f"Subject: kind={subject.get('kind')}, name={subject.get('name')}, namespace={subject.get('namespace')}")
            if (subject.get('kind') == 'ServiceAccount' and 
                subject.get('name') == sa_name and 
                subject.get('namespace') == sa_namespace):
                logger.debug(f"Found matching ServiceAccount in binding {binding.get('name', 'unknown')}")
                return True
        
        logger.debug(f"ServiceAccount {sa_name} not found in binding {binding.get('name', 'unknown')}")
        return False
    
    def _find_pod_resource(self, pod_name: str, namespace: str, resources: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find a specific pod resource."""
        for resource in resources:
            if (resource['kind'] == 'Pod' and 
                resource['name'] == pod_name and 
                resource['namespace'] == namespace):
                return resource
        return None
    
    def _compute_effective_rules(self, rbac: Dict[str, Any]) -> Dict[str, Any]:
        """Compute effective rules summary from attached Roles and ClusterRoles."""
        effective_rules = {
            'verbs': set(),
            'apiGroups': set(),
            'resources': set()
        }
        
        # Aggregate rules from Roles
        for role in rbac['roles']:
            for rule in role.get('rules', []):
                effective_rules['verbs'].update(rule.get('verbs', []))
                effective_rules['apiGroups'].update(rule.get('apiGroups', []))
                effective_rules['resources'].update(rule.get('resources', []))
        
        # Aggregate rules from ClusterRoles
        for cr in rbac['clusterRoles']:
            for rule in cr.get('rules', []):
                effective_rules['verbs'].update(rule.get('verbs', []))
                effective_rules['apiGroups'].update(rule.get('apiGroups', []))
                effective_rules['resources'].update(rule.get('resources', []))
        
        # Convert sets to lists for JSON serialization
        return {
            'verbs': list(effective_rules['verbs']),
            'apiGroups': list(effective_rules['apiGroups']),
            'resources': list(effective_rules['resources'])
        }


class ConflictDetector:
    """
    Detects conflicts and anomalies in K8s resource relationships.
    """
    
    def __init__(self):
        self.conflicts = []
        self.orphans = []
        self.cross_namespace = []
    
    def detect_conflicts(self, workloads: Dict[str, Any], resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect conflicts and anomalies across all workloads.
        
        Args:
            workloads: Dictionary of workload groupings
            resources: List of all parsed resources
            
        Returns:
            Dictionary with detected issues
        """
        issues = {
            'conflicts': [],
            'orphans': [],
            'crossNamespace': [],
            'selectorOverlaps': []
        }
        
        # Detect selector overlaps between workloads
        self._detect_selector_overlaps(workloads, issues)
        
        # Detect orphaned resources
        self._detect_orphaned_resources(workloads, resources, issues)
        
        # Detect cross-namespace anomalies
        self._detect_cross_namespace_issues(workloads, issues)
        
        # Detect owner reference conflicts
        self._detect_owner_conflicts(workloads, issues)
        
        return issues
    
    def _detect_selector_overlaps(self, workloads: Dict[str, Any], issues: Dict[str, Any]):
        """Detect when multiple workloads have overlapping selectors."""
        workload_list = list(workloads.values())
        
        for i, workload1 in enumerate(workload_list):
            for j, workload2 in enumerate(workload_list[i+1:], i+1):
                if workload1['namespace'] == workload2['namespace']:
                    overlap = self._compute_selector_overlap(
                        workload1.get('pods', {}).get('template_labels', {}),
                        workload2.get('pods', {}).get('template_labels', {})
                    )
                    if overlap:
                        issues['selectorOverlaps'].append({
                            'workload1': workload1['id'],
                            'workload2': workload2['id'],
                            'overlapping_labels': overlap
                        })
    
    def _detect_orphaned_resources(self, workloads: Dict[str, Any], resources: List[Dict[str, Any]], issues: Dict[str, Any]):
        """Detect resources that aren't attached to any workload."""
        attached_resources = set()
        
        # Collect all resources attached to workloads
        for workload in workloads.values():
            # Services
            for service in workload.get('services', []):
                attached_resources.add(f"Service:{workload['namespace']}:{service['name']}")
            
            # Ingress
            for ingress in workload.get('ingress', []):
                attached_resources.add(f"Ingress:{workload['namespace']}:{ingress['name']}")
            
            # ConfigMaps
            for config_map in workload.get('configMaps', []):
                attached_resources.add(f"ConfigMap:{workload['namespace']}:{config_map['name']}")
            
            # Secrets
            for secret in workload.get('secrets', []):
                attached_resources.add(f"Secret:{workload['namespace']}:{secret['name']}")
        
        # Find orphaned resources
        for resource in resources:
            if resource['kind'] in ['Service', 'Ingress', 'ConfigMap', 'Secret']:
                resource_key = f"{resource['kind']}:{resource['namespace']}:{resource['name']}"
                if resource_key not in attached_resources:
                    issues['orphans'].append({
                        'kind': resource['kind'],
                        'name': resource['name'],
                        'namespace': resource['namespace'],
                        'source_file': resource['source_file']
                    })
    
    def _detect_cross_namespace_issues(self, workloads: Dict[str, Any], issues: Dict[str, Any]):
        """Detect potential cross-namespace issues."""
        for workload in workloads.values():
            # Check for cross-namespace storage references
            for pvc in workload.get('storage', {}).get('pvcs', []):
                # This would need enhancement to detect actual cross-namespace issues
                pass
            
            # Check for cross-namespace service references
            for service in workload.get('services', []):
                # Services are namespaced, so this is more about validation
                pass
    
    def _detect_owner_conflicts(self, workloads: Dict[str, Any], issues: Dict[str, Any]):
        """Detect conflicts in owner references."""
        for workload in workloads.values():
            # Check for multiple owners in child resources
            for pod_name in workload.get('pods', {}).get('items', []):
                # This would need enhancement to detect actual owner conflicts
                pass
    
    def _compute_selector_overlap(self, labels1: Dict[str, str], labels2: Dict[str, str]) -> Dict[str, str]:
        """Compute overlapping labels between two sets."""
        overlap = {}
        for key, value in labels1.items():
            if key in labels2 and labels2[key] == value:
                overlap[key] = value
        return overlap


class K8sResourceParser:
    """
    Parses Kubernetes YAML/JSON files and extracts key resource information.
    """
    
    def __init__(self):
        self.workload_kinds = {
            'Deployment', 'StatefulSet', 'DaemonSet', 'Job', 'CronJob', 'Pod'
        }
    
    def parse_resources(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Parse multiple K8s resource files and extract key information.
        
        Args:
            file_paths: List of paths to K8s resource files
            
        Returns:
            List of parsed resource dictionaries with key fields
        """
        resources = []
        
        for file_path in file_paths:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Split multi-document YAML files
                documents = list(yaml.safe_load_all(content))
                
                for doc in documents:
                    if doc and isinstance(doc, dict) and 'kind' in doc:
                        resource = self._extract_key_fields(doc, file_path)
                        if resource:
                            resources.append(resource)
                            
            except Exception as e:
                logger.warning(f"Failed to parse {file_path}: {e}")
                continue
        
        return resources
    
    def _extract_key_fields(self, doc: Dict[str, Any], source_file: str) -> Optional[Dict[str, Any]]:
        """
        Extract key fields from a K8s resource.
        
        Args:
            doc: Parsed YAML document
            source_file: Source file path
            
        Returns:
            Dictionary with extracted key fields or None if invalid
        """
        try:
            kind = doc.get('kind')
            metadata = doc.get('metadata', {})
            
            resource = {
                'kind': kind,
                'name': metadata.get('name', ''),
                'namespace': metadata.get('namespace', 'default'),
                'labels': metadata.get('labels', {}),
                'annotations': metadata.get('annotations', {}),
                'source_file': source_file,
                'raw_resource': doc
            }
            
            # Extract selectors for Services
            if kind == 'Service':
                spec = doc.get('spec', {})
                resource['selectors'] = spec.get('selector', {})
                resource['ports'] = spec.get('ports', [])
            
            # Extract pod template for workloads
            elif kind in self.workload_kinds:
                resource['pod_template'] = self._extract_pod_template(doc)
                resource['service_account'] = resource['pod_template'].get('serviceAccountName')
            
            # Extract backend services for Ingress
            elif kind == 'Ingress':
                spec = doc.get('spec', {})
                resource['backend_services'] = self._extract_backend_services(spec)
            
            return resource
            
        except Exception as e:
            logger.warning(f"Failed to extract fields from {kind} resource: {e}")
            return None
    
    def _extract_pod_template(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract pod template information from workload resources.
        
        Args:
            doc: Workload resource document
            
        Returns:
            Dictionary with pod template information
        """
        pod_template = {}
        
        if doc['kind'] == 'Pod':
            # Pod is already the template
            pod_template = {
                'labels': doc.get('metadata', {}).get('labels', {}),
                'containers': doc.get('spec', {}).get('containers', []),
                'initContainers': doc.get('spec', {}).get('initContainers', []),
                'volumes': doc.get('spec', {}).get('volumes', []),
                'serviceAccountName': doc.get('spec', {}).get('serviceAccountName')
            }
        else:
            # Extract from pod template
            spec = doc.get('spec', {})
            template = spec.get('template', {})
            pod_template = {
                'labels': template.get('metadata', {}).get('labels', {}),
                'containers': template.get('spec', {}).get('containers', []),
                'initContainers': template.get('spec', {}).get('initContainers', []),
                'volumes': template.get('spec', {}).get('volumes', []),
                'serviceAccountName': template.get('spec', {}).get('serviceAccountName')
            }
        
        return pod_template
    
    def _extract_backend_services(self, spec: Dict[str, Any]) -> List[str]:
        """
        Extract backend service names from Ingress spec.
        
        Args:
            spec: Ingress spec section
            
        Returns:
            List of backend service names
        """
        backend_services = []
        
        # Handle default backend
        default_backend = spec.get('defaultBackend')
        if default_backend and 'service' in default_backend:
            backend_services.append(default_backend['service']['name'])
        
        # Handle rules
        rules = spec.get('rules', [])
        for rule in rules:
            http = rule.get('http', {})
            paths = http.get('paths', [])
            for path in paths:
                backend = path.get('backend', {})
                if 'service' in backend:
                    backend_services.append(backend['service']['name'])
        
        return backend_services


class WorkloadGrouper:
    """
    Groups K8s resources into logical workloads using a controller-based approach.
    
    The new approach works by:
    1. Treating each controller (Deployment, StatefulSet, DaemonSet, Job, CronJob, Pod, ReplicationController) as the root of a workload
    2. Expanding to include all directly owned resources (ReplicaSets, Pods, Jobs)
    3. Refining by Services: if a controller exposes multiple Services, each Service becomes a sub-workload
    4. Further refining by Ingress: if a Service is fronted by multiple Ingresses/hostnames, split per external interface
    
    This creates clear, deterministic groupings that mirror how operators think about workloads.
    """
    
    def __init__(self):
        self.workloads = {}
        self.shared_resources = set()
        self.controller_workloads = {}  # controller_key -> workload_id
        self.service_workloads = {}     # service_key -> [workload_ids]
        self.ingress_workloads = {}     # ingress_key -> [workload_ids]
    
    def group_resources(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Group resources into workloads using the new controller-based approach.
        
        Args:
            resources: List of parsed K8s resources
            
        Returns:
            Dictionary of workload groupings
        """
        # Step 1: Group by namespace
        resources_by_namespace = defaultdict(list)
        for resource in resources:
            namespace = resource.get('namespace', 'default')
            resources_by_namespace[namespace].append(resource)
        
        # Step 2: Process each namespace
        for namespace, namespace_resources in resources_by_namespace.items():
            self._process_namespace(namespace, namespace_resources)
        
        # Step 3: Refine workloads by Services
        self._refine_by_services(resources)
        
        # Step 4: Refine workloads by Ingress
        self._refine_by_ingress(resources)
        
        # Step 5: Mark shared resources
        self._mark_shared_resources()
        
        return self.workloads
    
    def _process_namespace(self, namespace: str, resources: List[Dict[str, Any]]):
        """
        Process resources within a namespace to create initial controller-based workloads.
        
        Args:
            namespace: Namespace name
            resources: Resources in the namespace
        """
        # Find controller seeds (Deployment, StatefulSet, DaemonSet, Job, CronJob, Pod, ReplicationController)
        controllers = []
        other_resources = []
        
        for resource in resources:
            if resource['kind'] in {'Deployment', 'StatefulSet', 'DaemonSet', 'Job', 'CronJob', 'Pod', 'ReplicationController'}:
                controllers.append(resource)
            else:
                other_resources.append(resource)
        
        # Create initial workloads for each controller
        for controller in controllers:
            workload_id = f"{namespace}/{controller['kind']}/{controller['name']}"
            workload = self._create_controller_workload(controller, workload_id)
            
            # Attach directly owned resources (ReplicaSets, Pods, Jobs)
            self._attach_owned_resources(workload, resources)
            
            # Attach related resources
            self._attach_services(workload, other_resources)
            self._attach_ingress(workload, other_resources)
            self._attach_config_and_secrets(workload, resources)
            self._attach_service_account(workload, resources)
            
            # Store the workload
            self.workloads[workload_id] = workload
            
            # Track controller -> workload mapping
            controller_key = (namespace, controller['kind'], controller['name'])
            self.controller_workloads[controller_key] = workload_id
    
    def _create_controller_workload(self, controller: Dict[str, Any], workload_id: str) -> Dict[str, Any]:
        """
        Create a new controller-based workload.
        
        Args:
            controller: Controller resource (Deployment, StatefulSet, etc.)
            workload_id: Unique workload identifier
            
        Returns:
            New workload dictionary
        """
        workload = {
            'id': workload_id,
            'namespace': controller['namespace'],
            'controller': {
                'kind': controller['kind'],
                'name': controller['name']
            },
            'selectors': controller.get('pod_template', {}).get('labels', {}),
            'services': [],
            'ingress': [],
            'configMaps': [],
            'secrets': [],
            'serviceAccount': None,
            'sharedRefs': [],
            # Enhanced fields
            'pods': {'materialized': False, 'items': [], 'template_labels': controller.get('pod_template', {}).get('labels', {})},
            'replicaSets': [],
            'jobs': [],
            'storage': {'pvcs': [], 'pvs': [], 'storageClasses': []},
            'resilience': {'hpas': [], 'pdbs': [], 'networkPolicies': []},
            'rbac': {'serviceAccounts': [], 'roleBindings': [], 'roles': [], 'clusterRoleBindings': [], 'clusterRoles': [], 'effectiveRules': {}},
            'notes': {'conflicts': [], 'orphans': [], 'crossNamespace': []},
            # New fields for workload refinement
            'sub_workloads': [],  # Service-based sub-workloads
            'parent_workload': None,  # Parent workload if this is a sub-workload
            'workload_type': 'controller'  # controller, service, or ingress
        }
        
        return workload
    
    def _create_workload(self, seed: Dict[str, Any], workload_id: str) -> Dict[str, Any]:
        """
        Create a new workload from a seed resource (legacy method for backward compatibility).
        
        Args:
            seed: Workload seed resource
            workload_id: Unique workload identifier
            
        Returns:
            New workload dictionary
        """
        workload = {
            'id': workload_id,
            'namespace': seed['namespace'],
            'seed': {
                'kind': seed['kind'],
                'name': seed['name']
            },
            'selectors': seed.get('pod_template', {}).get('labels', {}),
            'services': [],
            'ingress': [],
            'configMaps': [],
            'secrets': [],
            'serviceAccount': None,
            'sharedRefs': [],
            # New enhanced fields
            'pods': {'materialized': False, 'items': [], 'template_labels': seed.get('pod_template', {}).get('labels', {})},
            'replicaSets': [],
            'jobs': [],
            'storage': {'pvcs': [], 'pvs': [], 'storageClasses': []},
            'resilience': {'hpas': [], 'pdbs': [], 'networkPolicies': []},
            'rbac': {'serviceAccounts': [], 'roleBindings': [], 'roles': [], 'clusterRoleBindings': [], 'clusterRoles': [], 'effectiveRules': {}},
            'notes': {'conflicts': [], 'orphans': [], 'crossNamespace': []}
        }
        
        return workload
    
    def _attach_services(self, workload: Dict[str, Any], resources: List[Dict[str, Any]]):
        """
        Attach Services to workload based on selector matching.
        
        Args:
            workload: Workload to attach services to
            resources: Available resources to check
        """
        workload_selectors = workload['selectors']
        
        for resource in resources:
            if resource['kind'] == 'Service':
                service_selectors = resource.get('selectors', {})
                
                # Check if service selectors are a subset of workload selectors
                if self._selectors_match(service_selectors, workload_selectors):
                    service_info = {
                        'name': resource['name'],
                        'selectors': service_selectors,
                        'ports': resource.get('ports', [])
                    }
                    workload['services'].append(service_info)
    
    def _attach_ingress(self, workload: Dict[str, Any], resources: List[Dict[str, Any]]):
        """
        Attach Ingress resources to workload based on service backend.
        
        Args:
            workload: Workload to attach ingress to
            resources: Available resources to check
        """
        workload_service_names = {service['name'] for service in workload['services']}
        
        for resource in resources:
            if resource['kind'] == 'Ingress':
                backend_services = resource.get('backend_services', [])
                
                # Check if any backend service is in this workload
                if any(service_name in workload_service_names for service_name in backend_services):
                    ingress_info = {
                        'name': resource['name'],
                        'backend_services': backend_services
                    }
                    workload['ingress'].append(ingress_info)
    
    def _attach_config_and_secrets(self, workload: Dict[str, Any], resources: List[Dict[str, Any]]):
        """
        Attach ConfigMaps and Secrets directly referenced by the workload.
        
        Args:
            workload: Workload to attach configs to
            resources: Available resources to check
        """
        # Find the controller resource for this workload
        controller_resource = None
        for resource in resources:
            if (resource['kind'] == workload['controller']['kind'] and
                resource['name'] == workload['controller']['name'] and
                resource['namespace'] == workload['namespace']):
                controller_resource = resource
                break
        
        if not controller_resource:
            return
        
        pod_template = controller_resource.get('pod_template', {})
        
        # Extract referenced ConfigMaps and Secrets
        referenced_configs = set()
        referenced_secrets = set()
        
        # Check volumes
        for volume in pod_template.get('volumes', []):
            if 'configMap' in volume:
                referenced_configs.add(volume['configMap']['name'])
            elif 'secret' in volume:
                referenced_secrets.add(volume['secret']['secretName'])
        
        # Check environment variables
        for container in pod_template.get('containers', []) + pod_template.get('initContainers', []):
            for env in container.get('env', []):
                if 'valueFrom' in env:
                    value_from = env['valueFrom']
                    if 'configMapKeyRef' in value_from:
                        referenced_configs.add(value_from['configMapKeyRef']['name'])
                    elif 'secretKeyRef' in value_from:
                        referenced_secrets.add(value_from['secretKeyRef']['name'])
            
            for env_from in container.get('envFrom', []):
                if 'configMapRef' in env_from:
                    referenced_configs.add(env_from['configMapRef']['name'])
                elif 'secretRef' in env_from:
                    referenced_secrets.add(env_from['secretRef']['name'])
        
        # Attach referenced resources
        for resource in resources:
            if (resource['kind'] == 'ConfigMap' and 
                resource['name'] in referenced_configs and
                resource['namespace'] == workload['namespace']):
                workload['configMaps'].append({
                    'name': resource['name'],
                    'data_keys': list(resource.get('raw_resource', {}).get('data', {}).keys())
                })
            
            elif (resource['kind'] == 'Secret' and 
                  resource['name'] in referenced_secrets and
                  resource['namespace'] == workload['namespace']):
                workload['secrets'].append({
                    'name': resource['name'],
                    'type': resource.get('raw_resource', {}).get('type', 'Opaque')
                })
    
    def _attach_owned_resources(self, workload: Dict[str, Any], resources: List[Dict[str, Any]]):
        """
        Attach resources directly owned by the controller.
        
        Args:
            workload: Workload to attach owned resources to
            resources: Available resources to check
        """
        controller = workload['controller']
        namespace = workload['namespace']
        
        # Find ReplicaSets owned by this controller
        if controller['kind'] == 'Deployment':
            for resource in resources:
                if (resource['kind'] == 'ReplicaSet' and 
                    resource['namespace'] == namespace):
                    # Check if this ReplicaSet is owned by our Deployment
                    owner_refs = resource.get('raw_resource', {}).get('metadata', {}).get('ownerReferences', [])
                    for owner_ref in owner_refs:
                        if (owner_ref.get('kind') == 'Deployment' and 
                            owner_ref.get('name') == controller['name']):
                            workload['replicaSets'].append(resource['name'])
                            
                            # Find Pods owned by this ReplicaSet
                            for pod_resource in resources:
                                if (pod_resource['kind'] == 'Pod' and 
                                    pod_resource['namespace'] == namespace):
                                    pod_owner_refs = pod_resource.get('raw_resource', {}).get('metadata', {}).get('ownerReferences', [])
                                    for pod_owner_ref in pod_owner_refs:
                                        if (pod_owner_ref.get('kind') == 'ReplicaSet' and 
                                            pod_owner_ref.get('name') == resource['name']):
                                            workload['pods']['items'].append(pod_resource['name'])
                                            workload['pods']['materialized'] = True
                            break
        
        # Find Pods owned by StatefulSet, DaemonSet, Job, ReplicationController
        elif controller['kind'] in {'StatefulSet', 'DaemonSet', 'Job', 'ReplicationController'}:
            for resource in resources:
                if (resource['kind'] == 'Pod' and 
                    resource['namespace'] == namespace):
                    owner_refs = resource.get('raw_resource', {}).get('metadata', {}).get('ownerReferences', [])
                    for owner_ref in owner_refs:
                        if (owner_ref.get('kind') == controller['kind'] and 
                            owner_ref.get('name') == controller['name']):
                            workload['pods']['items'].append(resource['name'])
                            workload['pods']['materialized'] = True
                            break
        
        # Find Jobs owned by CronJob
        elif controller['kind'] == 'CronJob':
            for resource in resources:
                if (resource['kind'] == 'Job' and 
                    resource['namespace'] == namespace):
                    owner_refs = resource.get('raw_resource', {}).get('metadata', {}).get('ownerReferences', [])
                    for owner_ref in owner_refs:
                        if (owner_ref.get('kind') == 'CronJob' and 
                            owner_ref.get('name') == controller['name']):
                            workload['jobs'].append(resource['name'])
                            
                            # Find Pods owned by this Job
                            for pod_resource in resources:
                                if (pod_resource['kind'] == 'Pod' and 
                                    pod_resource['namespace'] == namespace):
                                    pod_owner_refs = pod_resource.get('raw_resource', {}).get('metadata', {}).get('ownerReferences', [])
                                    for pod_owner_ref in pod_owner_refs:
                                        if (pod_owner_ref.get('kind') == 'Job' and 
                                            pod_owner_ref.get('name') == resource['name']):
                                            workload['pods']['items'].append(pod_resource['name'])
                                            workload['pods']['materialized'] = True
                            break
        
        # For Pod controllers, the pod is already included
        elif controller['kind'] == 'Pod':
            workload['pods']['items'].append(controller['name'])
            workload['pods']['materialized'] = True
    
    def _refine_by_services(self, resources: List[Dict[str, Any]]):
        """
        Refine workloads by Services. If a controller exposes multiple Services,
        create sub-workloads for each Service.
        """
        for resource in resources:
            if resource['kind'] == 'Service':
                namespace = resource['namespace']
                service_name = resource['name']
                service_key = (namespace, service_name)
                
                # Find which controller(s) this service targets
                service_selectors = resource.get('selectors', {})
                matching_controllers = []
                
                for controller_key, workload_id in self.controller_workloads.items():
                    if controller_key[0] == namespace:  # Same namespace
                        workload = self.workloads[workload_id]
                        workload_selectors = workload['selectors']
                        
                        # Check if service selectors match workload selectors
                        if self._selectors_match(service_selectors, workload_selectors):
                            matching_controllers.append((controller_key, workload_id))
                
                # If service targets multiple controllers, create shared service workload
                if len(matching_controllers) > 1:
                    self._create_shared_service_workload(resource, matching_controllers)
                # If service targets single controller, create sub-workload
                elif len(matching_controllers) == 1:
                    self._create_service_sub_workload(resource, matching_controllers[0])
    
    def _refine_by_ingress(self, resources: List[Dict[str, Any]]):
        """
        Refine workloads by Ingress. If a Service is fronted by multiple Ingresses
        or hostnames, create sub-workloads for each external interface.
        """
        for resource in resources:
            if resource['kind'] == 'Ingress':
                namespace = resource['namespace']
                ingress_name = resource['name']
                ingress_key = (namespace, ingress_name)
                
                # Find which services this ingress targets
                backend_services = resource.get('backend_services', [])
                matching_services = []
                
                for service_key, workload_ids in self.service_workloads.items():
                    if service_key[0] == namespace:  # Same namespace
                        for workload_id in workload_ids:
                            workload = self.workloads[workload_id]
                            if workload['workload_type'] == 'service':
                                service_name = workload['controller']['name']
                                if service_name in backend_services:
                                    matching_services.append((service_key, workload_id))
                
                # If ingress targets multiple services, create shared ingress workload
                if len(matching_services) > 1:
                    self._create_shared_ingress_workload(resource, matching_services)
                # If ingress targets single service, create sub-workload
                elif len(matching_services) == 1:
                    self._create_ingress_sub_workload(resource, matching_services[0])
    
    def _create_service_sub_workload(self, service: Dict[str, Any], controller_info: Tuple):
        """
        Create a sub-workload for a service.
        
        Args:
            service: Service resource
            controller_info: (controller_key, workload_id) tuple
        """
        controller_key, parent_workload_id = controller_info
        namespace = service['namespace']
        service_name = service['name']
        
        # Create service sub-workload
        workload_id = f"{namespace}/Service/{service_name}"
        workload = {
            'id': workload_id,
            'namespace': namespace,
            'controller': {
                'kind': 'Service',
                'name': service_name
            },
            'selectors': service.get('selectors', {}),
            'services': [service],
            'ingress': [],
            'configMaps': [],
            'secrets': [],
            'serviceAccount': None,
            'sharedRefs': [],
            'pods': {'materialized': False, 'items': [], 'template_labels': {}},
            'replicaSets': [],
            'jobs': [],
            'storage': {'pvcs': [], 'pvs': [], 'storageClasses': []},
            'resilience': {'hpas': [], 'pdbs': [], 'networkPolicies': []},
            'rbac': {'serviceAccounts': [], 'roleBindings': [], 'roles': [], 'clusterRoleBindings': [], 'clusterRoles': [], 'effectiveRules': {}},
            'notes': {'conflicts': [], 'orphans': [], 'crossNamespace': []},
            'sub_workloads': [],
            'parent_workload': parent_workload_id,
            'workload_type': 'service'
        }
        
        # Copy relevant resources from parent workload
        parent_workload = self.workloads[parent_workload_id]
        workload['pods'] = parent_workload['pods'].copy()
        workload['configMaps'] = parent_workload['configMaps'].copy()
        workload['secrets'] = parent_workload['secrets'].copy()
        workload['serviceAccount'] = parent_workload['serviceAccount']
        
        # Store the workload
        self.workloads[workload_id] = workload
        
        # Track service -> workload mapping
        service_key = (namespace, service_name)
        if service_key not in self.service_workloads:
            self.service_workloads[service_key] = []
        self.service_workloads[service_key].append(workload_id)
        
        # Add to parent workload's sub-workloads
        parent_workload['sub_workloads'].append(workload_id)
    
    def _create_shared_service_workload(self, service: Dict[str, Any], controller_infos: List[Tuple]):
        """
        Create a shared service workload when a service targets multiple controllers.
        
        Args:
            service: Service resource
            controller_infos: List of (controller_key, workload_id) tuples
        """
        namespace = service['namespace']
        service_name = service['name']
        
        # Create shared service workload
        workload_id = f"{namespace}/Service/{service_name}-shared"
        workload = {
            'id': workload_id,
            'namespace': namespace,
            'controller': {
                'kind': 'Service',
                'name': f"{service_name}-shared"
            },
            'selectors': service.get('selectors', {}),
            'services': [service],
            'ingress': [],
            'configMaps': [],
            'secrets': [],
            'serviceAccount': None,
            'sharedRefs': [],
            'pods': {'materialized': False, 'items': [], 'template_labels': {}},
            'replicaSets': [],
            'jobs': [],
            'storage': {'pvcs': [], 'pvs': [], 'storageClasses': []},
            'resilience': {'hpas': [], 'pdbs': [], 'networkPolicies': []},
            'rbac': {'serviceAccounts': [], 'roleBindings': [], 'roles': [], 'clusterRoleBindings': [], 'clusterRoles': [], 'effectiveRules': {}},
            'notes': {'conflicts': [], 'orphans': [], 'crossNamespace': []},
            'sub_workloads': [],
            'parent_workload': None,
            'workload_type': 'service',
            'shared': True
        }
        
        # Store the workload
        self.workloads[workload_id] = workload
        
        # Track service -> workload mapping
        service_key = (namespace, service_name)
        if service_key not in self.service_workloads:
            self.service_workloads[service_key] = []
        self.service_workloads[service_key].append(workload_id)
    
    def _create_ingress_sub_workload(self, ingress: Dict[str, Any], service_info: Tuple):
        """
        Create a sub-workload for an ingress.
        
        Args:
            ingress: Ingress resource
            service_info: (service_key, workload_id) tuple
        """
        service_key, parent_workload_id = service_info
        namespace = ingress['namespace']
        ingress_name = ingress['name']
        
        # Create ingress sub-workload
        workload_id = f"{namespace}/Ingress/{ingress_name}"
        workload = {
            'id': workload_id,
            'namespace': namespace,
            'controller': {
                'kind': 'Ingress',
                'name': ingress_name
            },
            'selectors': {},
            'services': [],
            'ingress': [ingress],
            'configMaps': [],
            'secrets': [],
            'serviceAccount': None,
            'sharedRefs': [],
            'pods': {'materialized': False, 'items': [], 'template_labels': {}},
            'replicaSets': [],
            'jobs': [],
            'storage': {'pvcs': [], 'pvs': [], 'storageClasses': []},
            'resilience': {'hpas': [], 'pdbs': [], 'networkPolicies': []},
            'rbac': {'serviceAccounts': [], 'roleBindings': [], 'roles': [], 'clusterRoleBindings': [], 'clusterRoles': [], 'effectiveRules': {}},
            'notes': {'conflicts': [], 'orphans': [], 'crossNamespace': []},
            'sub_workloads': [],
            'parent_workload': parent_workload_id,
            'workload_type': 'ingress'
        }
        
        # Store the workload
        self.workloads[workload_id] = workload
        
        # Track ingress -> workload mapping
        ingress_key = (namespace, ingress_name)
        if ingress_key not in self.ingress_workloads:
            self.ingress_workloads[ingress_key] = []
        self.ingress_workloads[ingress_key].append(workload_id)
        
        # Add to parent workload's sub-workloads
        parent_workload = self.workloads[parent_workload_id]
        parent_workload['sub_workloads'].append(workload_id)
    
    def _create_shared_ingress_workload(self, ingress: Dict[str, Any], service_infos: List[Tuple]):
        """
        Create a shared ingress workload when an ingress targets multiple services.
        
        Args:
            ingress: Ingress resource
            service_infos: List of (service_key, workload_id) tuples
        """
        namespace = ingress['namespace']
        ingress_name = ingress['name']
        
        # Create shared ingress workload
        workload_id = f"{namespace}/Ingress/{ingress_name}-shared"
        workload = {
            'id': workload_id,
            'namespace': namespace,
            'controller': {
                'kind': 'Ingress',
                'name': f"{ingress_name}-shared"
            },
            'selectors': {},
            'services': [],
            'ingress': [ingress],
            'configMaps': [],
            'secrets': [],
            'serviceAccount': None,
            'sharedRefs': [],
            'pods': {'materialized': False, 'items': [], 'template_labels': {}},
            'replicaSets': [],
            'jobs': [],
            'storage': {'pvcs': [], 'pvs': [], 'storageClasses': []},
            'resilience': {'hpas': [], 'pdbs': [], 'networkPolicies': []},
            'rbac': {'serviceAccounts': [], 'roleBindings': [], 'roles': [], 'clusterRoleBindings': [], 'clusterRoles': [], 'effectiveRules': {}},
            'notes': {'conflicts': [], 'orphans': [], 'crossNamespace': []},
            'sub_workloads': [],
            'parent_workload': None,
            'workload_type': 'ingress',
            'shared': True
        }
        
        # Store the workload
        self.workloads[workload_id] = workload
        
        # Track ingress -> workload mapping
        ingress_key = (namespace, ingress_name)
        if ingress_key not in self.ingress_workloads:
            self.ingress_workloads[ingress_key] = []
        self.ingress_workloads[ingress_key].append(workload_id)
    
    def _attach_service_account(self, workload: Dict[str, Any], resources: List[Dict[str, Any]]):
        """
        Attach ServiceAccount if specified in the workload.
        
        Args:
            workload: Workload to attach service account to
            resources: Available resources to check
        """
        logger.debug(f"Attaching ServiceAccount to workload {workload['id']}")
        
        # Find the controller resource for this workload
        controller_resource = None
        for resource in resources:
            if (resource['kind'] == workload['controller']['kind'] and
                resource['name'] == workload['controller']['name'] and
                resource['namespace'] == workload['namespace']):
                controller_resource = resource
                break
        
        if controller_resource:
            logger.debug(f"Found controller resource for {workload['id']}: {controller_resource['kind']} {controller_resource['name']}")
            
            # Get service account name from pod template
            service_account_name = controller_resource.get('pod_template', {}).get('serviceAccountName')
            logger.debug(f"ServiceAccount name from pod template: {service_account_name}")
            
            if service_account_name:
                logger.debug(f"Looking for ServiceAccount {service_account_name} in namespace {workload['namespace']}")
                for resource in resources:
                    if (resource['kind'] == 'ServiceAccount' and 
                        resource['name'] == service_account_name and
                        resource['namespace'] == workload['namespace']):
                        workload['serviceAccount'] = {
                            'name': resource['name'],
                            'automountServiceAccountToken': resource.get('raw_resource', {}).get('automountServiceAccountToken', True)
                        }
                        logger.debug(f"Successfully attached ServiceAccount {service_account_name} to workload {workload['id']}")
                        break
                else:
                    logger.warning(f"ServiceAccount {service_account_name} not found in resources for workload {workload['id']}")
            else:
                logger.debug(f"No ServiceAccount specified in pod template for workload {workload['id']}")
        else:
            logger.warning(f"Could not find controller resource for workload {workload['id']}")
    
    def _selectors_match(self, service_selectors: Dict[str, str], workload_selectors: Dict[str, str]) -> bool:
        """
        Check if service selectors are a subset of workload selectors.
        
        Args:
            service_selectors: Service selector labels
            workload_selectors: Workload pod template labels
            
        Returns:
            True if selectors match, False otherwise
        """
        if not service_selectors:
            return False
        
        for key, value in service_selectors.items():
            if key not in workload_selectors or workload_selectors[key] != value:
                return False
        
        return True
    
    def _mark_shared_resources(self):
        """
        Mark resources that are shared across multiple workloads.
        """
        # Track resource usage across workloads
        resource_usage = defaultdict(list)
        
        for workload_id, workload in self.workloads.items():
            # Track services
            for service in workload['services']:
                resource_usage[f"Service:{service['name']}"].append(workload_id)
            
            # Track ingress
            for ingress in workload['ingress']:
                resource_usage[f"Ingress:{ingress['name']}"].append(workload_id)
            
            # Track config maps
            for config_map in workload['configMaps']:
                resource_usage[f"ConfigMap:{config_map['name']}"].append(workload_id)
            
            # Track secrets
            for secret in workload['secrets']:
                resource_usage[f"Secret:{secret['name']}"].append(workload_id)
        
        # Mark shared resources
        for resource_key, workload_ids in resource_usage.items():
            if len(workload_ids) > 1:
                self.shared_resources.add(resource_key)
                
                # Add shared flag to all workloads that use this resource
                for workload_id in workload_ids:
                    self.workloads[workload_id]['sharedRefs'].append(resource_key)


class K8sAnalyzer:
    """
    Analyzes Kubernetes resource files and creates workload groupings.
    
    This analyzer follows the v1 workload grouping logic:
    1. Groups resources by namespace
    2. Identifies workload seeds (Deployment, StatefulSet, etc.)
    3. Attaches related resources (Services, Ingress, ConfigMaps, etc.)
    4. Marks shared resources across workloads
    """
    
    def __init__(self, k8s_paths: List[str], output_dir: str, llm_config: dict = None):
        """
        Initialize the K8s analyzer.
        
        Args:
            k8s_paths: List of directories containing K8s resource files
            output_dir: Directory to store analysis results
            llm_config: LLM configuration for analysis
        """
        self.k8s_paths = [Path(path) for path in k8s_paths]
        self.output_dir = Path(output_dir)
        self.llm_config = llm_config
        
        # Initialize components
        self.parser = K8sResourceParser()
        self.grouper = WorkloadGrouper()
        self.owner_resolver = OwnerReferenceResolver()
        self.storage_resolver = StorageResolver()
        self.resilience_resolver = ResilienceResolver()
        self.rbac_resolver = RBACResolver()
        self.conflict_detector = ConflictDetector()
        
        # Analysis results
        self.workloads = {}
        self.vectors = []
        self.metadata = []
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Control mapping components
        self.profile_control_extractor = None
        self.llm_handler = None
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive K8s resource analysis.
        
        Returns:
            Dictionary containing analysis results and metadata
        """
        logger.info("Starting K8s resource analysis")
        
        try:
            # Step 1: Find all K8s resource files
            resource_files = self._find_resource_files()
            logger.info(f"Found {len(resource_files)} K8s resource files")
            
            # Step 2: Parse resources
            resources = self.parser.parse_resources(resource_files)
            logger.info(f"Parsed {len(resources)} K8s resources")
            
            # Step 3: Group into workloads (v1 grouping)
            self.workloads = self.grouper.group_resources(resources)
            logger.info(f"Created {len(self.workloads)} workload groupings")
            
            # Step 4: Build resolver indices
            logger.info("Building resolver indices...")
            self.owner_resolver.build_owner_graph(resources)
            self.storage_resolver.build_storage_indices(resources)
            self.resilience_resolver.build_resilience_indices(resources)
            self.rbac_resolver.build_rbac_indices(resources)
            
            # Step 5: Enhance workloads with expanded resources
            logger.info("Enhancing workloads with expanded resources...")
            self._enhance_workloads(resources)
            
            # Step 6: Detect conflicts and anomalies
            logger.info("Detecting conflicts and anomalies...")
            issues = self.conflict_detector.detect_conflicts(self.workloads, resources)
            
            # Step 7: Create FAISS index and metadata
            if self.workloads:
                self._create_indices()
            
            # Step 8: Save analysis results
            self._save_analysis_results()
            
            logger.info("K8s analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Error during K8s analysis: {e}")
            raise
        
        return {
            "workloads": self.workloads,
            "vectors_created": len(self.vectors),
            "metadata_entries": len(self.metadata)
        }
    
    def _enhance_workloads(self, resources: List[Dict[str, Any]]):
        """
        Enhance workloads with expanded resources using all resolvers.
        
        Args:
            resources: List of parsed K8s resources
        """
        logger.info("Enhancing workloads with expanded resources...")
        
        for workload_id, workload in self.workloads.items():
            logger.debug(f"Enhancing workload: {workload_id}")
            
            # Find the controller resource for this workload
            controller_resource = None
            for resource in resources:
                if (resource['kind'] == workload['controller']['kind'] and 
                    resource['name'] == workload['controller']['name'] and 
                    resource['namespace'] == workload['namespace']):
                    controller_resource = resource
                    break
            
            if controller_resource:
                logger.debug(f"Found controller resource for {workload_id}: {controller_resource['kind']} {controller_resource['name']}")
                
                # Expand owner references
                children = self.owner_resolver.expand_workload_children(controller_resource)
                workload['pods'] = children['pods']
                workload['replicaSets'] = children['replicaSets']
                workload['jobs'] = children['jobs']
                
                # Ensure ServiceAccount information is available for RBAC resolution
                if not workload.get('serviceAccount') and controller_resource.get('pod_template', {}).get('serviceAccountName'):
                    service_account_name = controller_resource['pod_template']['serviceAccountName']
                    logger.debug(f"Looking for ServiceAccount {service_account_name} for workload {workload_id}")
                    for resource in resources:
                        if (resource['kind'] == 'ServiceAccount' and 
                            resource['name'] == service_account_name and
                            resource['namespace'] == workload['namespace']):
                            workload['serviceAccount'] = {
                                'name': resource['name'],
                                'automountServiceAccountToken': resource.get('raw_resource', {}).get('automountServiceAccountToken', True)
                            }
                            logger.debug(f"Found and attached ServiceAccount {service_account_name} to workload {workload_id}")
                            break
                else:
                    logger.debug(f"Workload {workload_id} already has ServiceAccount: {workload.get('serviceAccount')}")
                
                # Resolve storage
                workload['storage'] = self.storage_resolver.resolve_workload_storage(workload, resources)
                
                # Resolve resilience
                workload['resilience'] = self.resilience_resolver.resolve_workload_resilience(workload, resources)
                
                # Resolve RBAC
                logger.debug(f"Resolving RBAC for workload {workload_id} with ServiceAccount: {workload.get('serviceAccount')}")
                workload['rbac'] = self.rbac_resolver.resolve_workload_rbac(workload, resources)
                logger.debug(f"RBAC resolution complete for {workload_id}: {len(workload['rbac'].get('serviceAccounts', []))} SAs, {len(workload['rbac'].get('roles', []))} roles")
            else:
                logger.warning(f"Could not find controller resource for workload {workload_id}")
        
        logger.info("Workload enhancement completed")
    
    def _find_resource_files(self) -> List[str]:
        """
        Find all K8s resource files in the specified directories.
        
        Returns:
            List of file paths to K8s resource files
        """
        resource_files = []
        k8s_extensions = {'.yaml', '.yml', '.json'}
        
        for k8s_path in self.k8s_paths:
            if not k8s_path.exists():
                logger.warning(f"K8s path does not exist: {k8s_path}")
                continue
            
            if k8s_path.is_file():
                if k8s_path.suffix in k8s_extensions:
                    resource_files.append(str(k8s_path))
            else:
                # Recursively search directories
                for file_path in k8s_path.rglob('*'):
                    if file_path.is_file() and file_path.suffix in k8s_extensions:
                        resource_files.append(str(file_path))
        
        return resource_files
    
    def _create_indices(self):
        """
        Create FAISS indices and metadata for workload analysis.
        """
        # Convert workloads to text for embedding
        workload_texts = []
        
        for workload_id, workload in self.workloads.items():
            # Create a text representation of the workload
            workload_text = self._workload_to_text(workload_id, workload)
            workload_texts.append(workload_text)
            
            # Store metadata
            self.metadata.append({
                'source_file': f"workload_{workload_id}",
                'content': workload_text,
                'summary': f"K8s workload: {workload_id}",
                'workload_id': workload_id,
                'workload_data': workload
            })
        
        # Generate embeddings
        if workload_texts:
            embeddings = local_embedder.embed_chunks(workload_texts)
            index = faiss_index.build_faiss_index(embeddings)
            
            # Save index
            index_path = self.output_dir / "k8s_index.faiss"
            faiss_index.save_index(index, index_path)
            
            # Store vectors for metadata
            self.vectors = embeddings.tolist()
    
    def map_controls_to_workloads(self, profile_path: str) -> Dict[str, Any]:
        """
        Map NIST 800-53 controls to K8s workloads using the specified OSCAL profile.
        
        Args:
            profile_path: Path to the OSCAL profile JSON file
            
        Returns:
            Dictionary containing OSCAL component definition with workload mappings
        """
        logger.info("Starting control mapping for K8s workloads")
        
        try:
            # Initialize control mapping components
            self._initialize_control_mapping(profile_path)
            
            # Filter to only controller workloads (exclude sub-workloads)
            controller_workloads = self._get_controller_workloads()
            logger.info(f"Mapping controls for {len(controller_workloads)} controller workloads")
            
            # Generate OSCAL component definition
            component_definition = self._generate_oscal_component_definition(controller_workloads)
            
            # Save the OSCAL output
            self._save_oscal_output(component_definition)
            
            logger.info("Control mapping completed successfully")
            return component_definition
            
        except Exception as e:
            logger.error(f"Error during control mapping: {e}")
            raise
    
    def _initialize_control_mapping(self, profile_path: str):
        """Initialize control mapping components."""
        from maposcal.generator.profile_control_extractor import ProfileControlExtractor
        from maposcal.llm.llm_handler import LLMHandler
        
        # Get catalog path from configuration
        # We need to pass this from the CLI, but for now use a default
        catalog_path = "examples/NIST_SP-800-53_rev5_catalog.json"
        
        # Load profile and extract controls
        self.profile_control_extractor = ProfileControlExtractor(catalog_path, profile_path)
        controls = self._extract_all_controls()
        
        # Initialize LLM handler with K8s-specific configuration
        if self.llm_config:
            self.llm_handler = LLMHandler(
                provider=self.llm_config["provider"],
                model=self.llm_config["model"]
            )
            if "temperature" in self.llm_config:
                self.llm_handler.default_temperature = self.llm_config["temperature"]
        else:
            self.llm_handler = LLMHandler(command="k8s_process")
        
        logger.info(f"Initialized control mapping with {len(controls)} controls")
    
    def _extract_all_controls(self) -> List[Dict[str, Any]]:
        """Extract all controls from the profile."""
        controls = []
        
        # Get all control IDs from the profile
        profile_imports = self.profile_control_extractor.profile.get("profile", {}).get("imports", [])
        
        for profile_import in profile_imports:
            # Extract control IDs from include-controls
            include_controls = profile_import.get("include-controls", [])
            for include_control in include_controls:
                with_ids = include_control.get("with-ids", [])
                for control_id in with_ids:
                    # Get control details from the catalog
                    control_details = self.profile_control_extractor.extract_control_parameters(control_id)
                    if control_details:
                        controls.append(control_details)
        
        return controls
    
    def _get_controller_workloads(self) -> Dict[str, Dict[str, Any]]:
        """Filter workloads to only controller types (exclude sub-workloads)."""
        controller_workloads = {}
        
        for workload_id, workload in self.workloads.items():
            # Only include workloads with workload_type == 'controller'
            if workload.get('workload_type') == 'controller':
                controller_workloads[workload_id] = workload
        
        return controller_workloads
    
    def _generate_oscal_component_definition(self, controller_workloads: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate OSCAL component definition with one component per controller workload."""
        components = []
        
        for workload_id, workload in controller_workloads.items():
            try:
                component = self._create_workload_component(workload_id, workload)
                components.append(component)
                logger.info(f"Created component for workload: {workload_id}")
                
            except Exception as e:
                logger.error(f"Failed to create component for workload {workload_id}: {e}")
                # Continue with other workloads instead of failing completely
                continue
        
        # Create the component definition structure
        component_definition = {
            "component-definition": {
                "metadata": self._generate_oscal_metadata(),
                "components": components
            }
        }
        
        return component_definition
    
    def _create_workload_component(self, workload_id: str, workload: Dict[str, Any]) -> Dict[str, Any]:
        """Create an OSCAL component for a single workload."""
        # Map controls to this workload
        implemented_requirements = self._map_controls_to_workload(workload_id, workload)
        
        # Create the component structure
        component = {
            "id": workload_id,
            "type": "application",
            "title": f"K8s Workload: {workload['controller']['name']}",
            "description": f"Kubernetes {workload['controller']['kind']} workload in namespace {workload['namespace']}",
            "implemented-requirements": implemented_requirements,
            "props": [
                {
                    "name": "workload-type",
                    "value": workload['controller']['kind'],
                    "ns": "urn:maposcal:k8s-workload-type"
                },
                {
                    "name": "namespace",
                    "value": workload['namespace'],
                    "ns": "urn:maposcal:k8s-namespace"
                }
            ]
        }
        
        return component
    
    def _map_controls_to_workload(self, workload_id: str, workload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Map all controls to a single workload using the K8s-specific prompts."""
        from maposcal.llm.prompt_templates import k8s_system_prompt, k8s_evaluate_prompt
        
        implemented_requirements = []
        
        # Get all controls from the profile
        controls = self._extract_all_controls()
        
        for control in controls:
            try:
                # Build the K8s-specific prompt
                prompt = self._build_k8s_control_prompt(workload, control)
                
                # Send to LLM with retry logic
                response = self._send_to_llm_with_retry(prompt, max_retries=3)
                
                # Parse the response into implemented requirements
                control_mapping = self._parse_control_response(response, control)
                if control_mapping:
                    implemented_requirements.append(control_mapping)
                
            except Exception as e:
                logger.error(f"Failed to map control {control.get('id', 'unknown')} to workload {workload_id}: {e}")
                # Continue with other controls instead of failing completely
                continue
        
        return implemented_requirements
    
    def _build_k8s_control_prompt(self, workload: Dict[str, Any], control: Dict[str, Any]) -> str:
        """Build the K8s-specific control mapping prompt."""
        from maposcal.llm.prompt_templates import k8s_system_prompt, k8s_evaluate_prompt
        
        # Format the workload as JSON
        workload_json = json.dumps(workload, indent=2)
        
        # Format the control information - the prompt template expects this exact format
        # Extract control description from statement field (like control_mapper does)
        control_description = (
            control.get("statement", [""])[0]
            if isinstance(control.get("statement"), list)
            else control.get("statement", "")
        )
        control_dict = f"Control ID: {control.get('id', 'N/A')}\nControl Name: {control.get('title', 'N/A')}\nControl Description: {control_description}"
        
        # Build the complete prompt
        prompt = f"{k8s_system_prompt}\n\n{k8s_evaluate_prompt.format(workload_json=workload_json, control_dict=control_dict)}"
        
        # Debug: log prompt length and first/last few characters
        logger.info(f"Prompt length: {len(prompt)} characters")
        logger.info(f"Prompt starts with: {prompt[:200]}...")
        logger.info(f"Prompt ends with: ...{prompt[-200:]}")
        
        # Debug: count tokens if LLM handler supports it
        try:
            token_count = self.llm_handler.count_tokens(prompt)
            logger.info(f"Prompt token count: {token_count}")
        except Exception as e:
            logger.info(f"Could not count tokens: {e}")
        
        return prompt
    
    def _send_to_llm_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Send prompt to LLM with retry logic."""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Let the model use its default token limits
                logger.info(f"Attempt {attempt + 1}: Sending prompt with default token limits")
                response = self.llm_handler.query(prompt)
                logger.info(f"Response length: {len(response)} characters")
                logger.info(f"Response preview: {response[:500]}...")
                return response
                
            except Exception as e:
                last_error = e
                logger.warning(f"LLM request failed (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    # Wait before retrying (exponential backoff)
                    import time
                    time.sleep(2 ** attempt)
        
        # All retries failed
        raise Exception(f"LLM request failed after {max_retries} attempts. Last error: {last_error}")
    
    def _parse_control_response(self, response: str, control: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse the LLM response into an OSCAL implemented requirement."""
        try:
            # Debug: log the raw response for troubleshooting
            logger.info(f"Raw LLM response for control {control.get('id')}: {repr(response)}")
            
            # Extract JSON from the response - the prompt template expects a list of dicts
            import re
            
            # First try to find a list of objects: [{...}, {...}]
            list_match = re.search(r'\[.*\]', response, re.DOTALL)
            if list_match:
                try:
                    control_list = json.loads(list_match.group())
                    if isinstance(control_list, list) and len(control_list) > 0:
                        # Take the first control mapping
                        control_data = control_list[0]
                    else:
                        logger.warning(f"Empty or invalid control list in LLM response for control {control.get('id')}")
                        return None
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse control list JSON for control {control.get('id')}")
                    return None
            else:
                # Fallback: try to find a single object {...}
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if not json_match:
                    logger.warning(f"No JSON found in LLM response for control {control.get('id')}")
                    logger.debug(f"Response content: {response}")
                    return None
                
                try:
                    control_data = json.loads(json_match.group())
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse control JSON for control {control.get('id')}")
                    logger.debug(f"Extracted JSON text: {json_match.group()}")
                    return None
            
            # Validate that we have the required fields
            if not isinstance(control_data, dict):
                logger.warning(f"Control data is not a dictionary for control {control.get('id')}")
                return None
            
            required_fields = ['control-status', 'control-explanation', 'statement-description']
            if not all(field in control_data for field in required_fields):
                logger.warning(f"Missing required fields in control response for control {control.get('id')}")
                logger.debug(f"Available fields: {list(control_data.keys())}")
                return None
            
            # Create the implemented requirement structure
            implemented_requirement = {
                "uuid": self._generate_uuid(),
                "control-id": control.get('id'),
                "props": [
                    {
                        "name": "control-name",
                        "value": control.get('title', 'N/A'),
                        "ns": "urn:maposcal:control-name-reference"
                    },
                    {
                        "name": "control-description",
                        "value": (
                            control.get("statement", [""])[0]
                            if isinstance(control.get("statement"), list)
                            else control.get("statement", "")
                        ),
                        "ns": "urn:maposcal:control-description-reference"
                    },
                    {
                        "name": "control-status",
                        "value": control_data.get('control-status', 'not applicable'),
                        "ns": "urn:maposcal:control-status-reference"
                    },
                    {
                        "name": "control-explanation",
                        "value": control_data.get('control-explanation', ''),
                        "ns": "urn:maposcal:explanation-reference"
                    }
                ],
                "statements": [
                    {
                        "statement-id": f"{control.get('id')}_smt.a",
                        "uuid": self._generate_uuid(),
                        "description": control_data.get('statement-description', '')
                    }
                ]
            }
            
            return implemented_requirement
            
        except Exception as e:
            logger.error(f"Failed to parse control response: {e}")
            logger.debug(f"Response that caused error: {repr(response)}")
            return None
    
    def _generate_oscal_metadata(self) -> Dict[str, Any]:
        """Generate OSCAL metadata for the component definition."""
        from maposcal.utils.metadata import generate_metadata
        
        if self.llm_config:
            from maposcal import settings
            provider_config = settings.LLM_PROVIDERS[self.llm_config["provider"]]
            metadata = generate_metadata(
                model=self.llm_config["model"],
                provider=self.llm_config["provider"],
                base_url=provider_config["base_url"],
                command="k8s_process",
            )
        else:
            metadata = {
                "title": "K8s Workload Control Mapping",
                "last-modified": datetime.datetime.now().isoformat(),
                "version": "1.0.0",
                "oscal-version": "1.0.4"
            }
        
        return metadata
    
    def _save_oscal_output(self, component_definition: Dict[str, Any]):
        """Save the OSCAL component definition to the output directory."""
        oscal_path = self.output_dir / "k8s_oscal_component_definition.json"
        
        # Try to use compliance-trestle integration for better OSCAL compliance
        try:
            from maposcal.generator.trestle_integration import (
                create_oscal_component_from_maposcal_output,
                serialize_oscal_component,
                validate_oscal_structure
            )
            
            # Convert the K8s component definition to MapOSCAL format
            # The K8s analyzer creates a different structure, so we need to adapt it
            maposcal_format = self._convert_k8s_to_maposcal_format(component_definition)
            
            # Create compliance-trestle OSCAL component
            comp_def = create_oscal_component_from_maposcal_output(maposcal_format)
            
            # Validate the OSCAL structure
            if validate_oscal_structure(comp_def):
                logger.info("✅ OSCAL structure validation passed")
            else:
                logger.warning("⚠️  OSCAL structure validation warnings")
            
            # Serialize to JSON using compliance-trestle
            json_output = serialize_oscal_component(comp_def, pretty=True)
            
            # Write the compliance-trestle generated OSCAL component
            with open(oscal_path, 'w') as f:
                f.write(json_output)
            
            # Also write the legacy format for backward compatibility
            legacy_path = self.output_dir / "k8s_oscal_component_definition_legacy.json"
            with open(legacy_path, 'w') as f:
                json.dump(component_definition, f, indent=2)
            
            logger.info(f"✅ Generated OSCAL component (compliance-trestle) written to {oscal_path}")
            logger.info(f"📄 Legacy format written to {legacy_path}")
            
        except ImportError:
            logger.warning("⚠️  Compliance-trestle not available, using legacy generation")
            # Fallback to legacy generation
            with open(oscal_path, 'w') as f:
                json.dump(component_definition, f, indent=2)
            logger.info(f"OSCAL component definition saved to {oscal_path}")
            
        except Exception as e:
            logger.error(f"❌ Error with compliance-trestle integration: {e}")
            logger.info("Falling back to legacy generation...")
            # Fallback to legacy generation
            with open(oscal_path, 'w') as f:
                json.dump(component_definition, f, indent=2)
            logger.info(f"OSCAL component definition saved to {oscal_path}")
    
    def _convert_k8s_to_maposcal_format(self, component_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Convert K8s component definition format to MapOSCAL format for trestle integration."""
        implemented_requirements = []
        
        # Extract components from the K8s format
        components = component_definition.get("component-definition", {}).get("components", [])
        
        for component in components:
            # Extract implemented requirements from each component
            component_impl_reqs = component.get("implemented-requirements", [])
            
            # Ensure all UUIDs are valid for compliance-trestle
            for impl_req in component_impl_reqs:
                # Fix the main requirement UUID
                if 'uuid' in impl_req:
                    impl_req['uuid'] = self._ensure_valid_uuid(impl_req['uuid'])
                
                # Fix statement UUIDs
                if 'statements' in impl_req:
                    for statement in impl_req['statements']:
                        if 'uuid' in statement:
                            statement['uuid'] = self._ensure_valid_uuid(statement['uuid'])
            
            implemented_requirements.extend(component_impl_reqs)
        
        # Return in MapOSCAL format
        return {
            "implemented_requirements": implemented_requirements
        }
    
    def _generate_uuid(self) -> str:
        """Generate a UUID for OSCAL elements."""
        import uuid
        return str(uuid.uuid4())
    
    def _ensure_valid_uuid(self, uuid_str: str) -> str:
        """Ensure a UUID string is in valid UUID v4 format for compliance-trestle."""
        import uuid
        try:
            # Try to parse and validate the UUID
            parsed_uuid = uuid.UUID(uuid_str)
            return str(parsed_uuid)
        except (ValueError, AttributeError):
            # If invalid, generate a new UUID v4
            return str(uuid.uuid4())
    
    def _workload_to_text(self, workload_id: str, workload: Dict[str, Any]) -> str:
        """
        Convert workload data to text representation for embedding.
        
        Args:
            workload_id: Workload identifier
            workload: Workload data
            
        Returns:
            Text representation of the workload
        """
        lines = [
            f"Workload: {workload_id}",
            f"Namespace: {workload['namespace']}",
            f"Controller: {workload['controller']['kind']} {workload['controller']['name']}",
            f"Type: {workload.get('workload_type', 'unknown')}",
            f"Selectors: {workload['selectors']}",
            ""
        ]
        
        if workload.get('parent_workload'):
            lines.append(f"Parent: {workload['parent_workload']}")
            lines.append("")
        
        if workload.get('sub_workloads'):
            lines.append(f"Sub-workloads: {', '.join(workload['sub_workloads'])}")
            lines.append("")
        
        if workload['services']:
            lines.append("Services:")
            for service in workload['services']:
                lines.append(f"  - {service['name']}: {service['selectors']}")
            lines.append("")
        
        if workload['ingress']:
            lines.append("Ingress:")
            for ingress in workload['ingress']:
                lines.append(f"  - {ingress['name']}: {ingress['backend_services']}")
            lines.append("")
        
        if workload['configMaps']:
            lines.append("ConfigMaps:")
            for config_map in workload['configMaps']:
                lines.append(f"  - {config_map['name']}: {config_map['data_keys']}")
            lines.append("")
        
        if workload['secrets']:
            lines.append("Secrets:")
            for secret in workload['secrets']:
                lines.append(f"  - {secret['name']}: {secret['type']}")
            lines.append("")
        
        if workload['serviceAccount']:
            lines.append(f"ServiceAccount: {workload['serviceAccount']['name']}")
            lines.append("")
        
        if workload['sharedRefs']:
            lines.append("Shared Resources:")
            for shared_ref in workload['sharedRefs']:
                lines.append(f"  - {shared_ref}")
        
        # Enhanced fields
        if workload.get('pods', {}).get('items'):
            lines.append("Pods:")
            for pod in workload['pods']['items']:
                lines.append(f"  - {pod}")
            lines.append("")
        
        if workload.get('replicaSets'):
            lines.append("ReplicaSets:")
            for rs in workload['replicaSets']:
                lines.append(f"  - {rs}")
            lines.append("")
        
        if workload.get('jobs'):
            lines.append("Jobs:")
            for job in workload['jobs']:
                lines.append(f"  - {job}")
            lines.append("")
        
        if workload.get('storage', {}).get('pvcs'):
            lines.append("Storage:")
            for pvc in workload['storage']['pvcs']:
                lines.append(f"  - PVC: {pvc['name']}")
            for pv in workload['storage']['pvs']:
                lines.append(f"  - PV: {pv['name']}")
            for sc in workload['storage']['storageClasses']:
                lines.append(f"  - StorageClass: {sc['name']}")
            lines.append("")
        
        if workload.get('resilience', {}).get('hpas'):
            lines.append("Resilience:")
            for hpa in workload['resilience']['hpas']:
                lines.append(f"  - HPA: {hpa['name']}")
            for pdb in workload['resilience']['pdbs']:
                lines.append(f"  - PDB: {pdb['name']}")
            for np in workload['resilience']['networkPolicies']:
                lines.append(f"  - NetworkPolicy: {np['name']}")
            lines.append("")
        
        if workload.get('rbac', {}).get('serviceAccounts'):
            lines.append("RBAC:")
            for sa in workload['rbac']['serviceAccounts']:
                lines.append(f"  - ServiceAccount: {sa['name']}")
            for rb in workload['rbac']['roleBindings']:
                lines.append(f"  - RoleBinding: {rb['name']}")
            for role in workload['rbac']['roles']:
                lines.append(f"  - Role: {role['name']}")
            for crb in workload['rbac']['clusterRoleBindings']:
                lines.append(f"  - ClusterRoleBinding: {crb['name']}")
            for cr in workload['rbac']['clusterRoles']:
                lines.append(f"  - ClusterRole: {cr['name']}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _save_analysis_results(self):
        """
        Save analysis results to output directory.
        """
        # Save workload data
        workloads_path = self.output_dir / "k8s_workloads.json"
        
        # Generate metadata for this operation
        if self.llm_config:
            from maposcal import settings
            provider_config = settings.LLM_PROVIDERS[self.llm_config["provider"]]
            metadata = generate_metadata(
                model=self.llm_config["model"],
                provider=self.llm_config["provider"],
                base_url=provider_config["base_url"],
                command="k8s_process",
            )
            workloads_with_metadata = inject_metadata_into_json(
                {"workloads": self.workloads}, metadata
            )
        else:
            workloads_with_metadata = {"workloads": self.workloads}
        
        with open(workloads_path, 'w') as f:
            json.dump(workloads_with_metadata, f, indent=2)
        
        # Save metadata
        if self.metadata:
            meta_path = self.output_dir / "k8s_meta.json"
            meta_store.save_metadata(self.metadata, meta_path)
        
        logger.info(f"Analysis results saved to {self.output_dir}")

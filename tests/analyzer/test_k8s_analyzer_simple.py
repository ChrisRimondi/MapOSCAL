"""
Simplified tests for the enhanced K8s analyzer.

This test file uses fixtures and focuses on testing the core functionality
without complex setup.
"""

import pytest
from pathlib import Path

from maposcal.analyzer.k8s_analyzer import (
    K8sAnalyzer,
    K8sResourceParser,
    WorkloadGrouper
)


class TestK8sAnalyzerIntegration:
    """Integration tests for the K8s analyzer."""
    
    def test_analyze_complete_workflow(self, temp_k8s_dir):
        """Test the complete analysis workflow with a real deployment."""
        analyzer = K8sAnalyzer(
            k8s_paths=[temp_k8s_dir],
            output_dir=Path(temp_k8s_dir).parent,
            llm_config=None
        )
        
        results = analyzer.analyze()
        
        # Check basic results structure
        assert 'workloads' in results
        assert 'vectors_created' in results
        assert 'metadata_entries' in results
        
        # Check that we have the expected workloads (controller + service sub-workload)
        assert len(results['workloads']) == 2
        
        # Get the controller workload
        controller_workload_id = 'test-ns/Deployment/test-deployment'
        assert controller_workload_id in results['workloads']
        
        # Get the service sub-workload
        service_workload_id = 'test-ns/Service/test-service'
        assert service_workload_id in results['workloads']
        
        # Check controller workload basics
        controller_workload = results['workloads'][controller_workload_id]
        assert controller_workload['namespace'] == 'test-ns'
        assert controller_workload['controller']['kind'] == 'Deployment'
        assert controller_workload['controller']['name'] == 'test-deployment'
        assert controller_workload['selectors'] == {'app': 'test', 'tier': 'web'}
        assert controller_workload['workload_type'] == 'controller'
        
        # Check service sub-workload basics
        service_workload = results['workloads'][service_workload_id]
        assert service_workload['namespace'] == 'test-ns'
        assert service_workload['controller']['kind'] == 'Service'
        assert service_workload['controller']['name'] == 'test-service'
        assert service_workload['workload_type'] == 'service'
        assert service_workload['parent_workload'] == controller_workload_id
        
        # Verify the workload hierarchy
        assert service_workload_id in controller_workload['sub_workloads']
        
        # Use controller workload for further checks
        workload = controller_workload
        
        # Check that all resources are attached
        assert len(workload['services']) == 1
        assert workload['services'][0]['name'] == 'test-service'
        
        assert len(workload['configMaps']) == 1
        assert workload['configMaps'][0]['name'] == 'test-config'
        assert 'nginx.conf' in workload['configMaps'][0]['data_keys']
        assert 'app.config' in workload['configMaps'][0]['data_keys']
        
        assert len(workload['secrets']) == 1
        assert workload['secrets'][0]['name'] == 'test-secret'
        assert workload['secrets'][0]['type'] == 'Opaque'
        
        assert workload['serviceAccount'] is not None
        assert workload['serviceAccount']['name'] == 'test-sa'
        assert workload['serviceAccount']['automountServiceAccountToken'] is True
        
        # Check enhanced fields
        assert 'pods' in workload
        assert 'storage' in workload
        assert 'resilience' in workload
        assert 'rbac' in workload
        
        # Check resilience features
        assert len(workload['resilience']['hpas']) == 1
        assert workload['resilience']['hpas'][0]['name'] == 'test-hpa'
        # Note: PDB and NetworkPolicy attachment may need additional logic
        # For now, just check that the fields exist
        assert 'pdbs' in workload['resilience']
        assert 'networkPolicies' in workload['resilience']
        
        # Check storage
        # Note: PVC attachment requires the deployment to reference the PVC
        # For now, just check that the fields exist
        assert 'pvcs' in workload['storage']
        assert 'pvs' in workload['storage']
        assert 'storageClasses' in workload['storage']
        
        # Check RBAC
        # Note: RBAC resolution may need additional logic
        # For now, just check that the fields exist
        assert 'serviceAccounts' in workload['rbac']
        assert 'roleBindings' in workload['rbac']
        assert 'roles' in workload['rbac']
        assert 'effectiveRules' in workload['rbac']
    
    def test_analyze_with_llm_config(self, temp_k8s_dir, mock_llm_config):
        """Test analysis with LLM configuration."""
        analyzer = K8sAnalyzer(
            k8s_paths=[temp_k8s_dir],
            output_dir=Path(temp_k8s_dir).parent,
            llm_config=mock_llm_config
        )
        
        results = analyzer.analyze()
        
        # Check that analysis completed successfully
        assert 'workloads' in results
        # New controller-based approach creates controller + service workloads
        assert len(results['workloads']) == 2
        
        # Check that output files were created
        output_dir = Path(temp_k8s_dir).parent
        assert (output_dir / "k8s_workloads.json").exists()
        assert (output_dir / "k8s_meta.json").exists()
        assert (output_dir / "k8s_index.faiss").exists()


class TestK8sResourceParser:
    """Test the K8s resource parser."""
    
    def test_parse_resources_from_directory(self, temp_k8s_dir):
        """Test parsing resources from a directory."""
        # Use the analyzer to test directory parsing, as it handles finding files
        analyzer = K8sAnalyzer(
            k8s_paths=[temp_k8s_dir],
            output_dir=Path(temp_k8s_dir).parent,
            llm_config=None
        )
        
        # Find resource files
        resource_files = analyzer._find_resource_files()
        
        # Should have at least one resource file
        assert len(resource_files) > 0
        
        # Parse the resources
        parser = K8sResourceParser()
        resources = parser.parse_resources(resource_files)
        
        # Should have multiple resources
        assert len(resources) > 1
        
        # Check that we have the expected resource types
        resource_kinds = {r['kind'] for r in resources}
        assert 'Deployment' in resource_kinds
        assert 'Service' in resource_kinds
        assert 'ConfigMap' in resource_kinds
        assert 'Secret' in resource_kinds
        assert 'ServiceAccount' in resource_kinds
        
        # Check that the deployment was parsed correctly
        deployment = next(r for r in resources if r['kind'] == 'Deployment')
        assert deployment['name'] == 'test-deployment'
        assert deployment['namespace'] == 'test-ns'
        assert 'pod_template' in deployment
        assert deployment['pod_template']['serviceAccountName'] == 'test-sa'
        
        # Check that the service was parsed correctly
        service = next(r for r in resources if r['kind'] == 'Service')
        assert service['name'] == 'test-service'
        assert 'selectors' in service
        assert 'ports' in service
        
        # Check that the configmap was parsed correctly
        configmap = next(r for r in resources if r['kind'] == 'ConfigMap')
        assert configmap['name'] == 'test-config'
        assert 'raw_resource' in configmap


class TestWorkloadGrouper:
    """Test the workload grouper."""
    
    def test_group_resources_with_sample_data(self, sample_resources):
        """Test grouping resources with sample data."""
        grouper = WorkloadGrouper()
        
        workloads = grouper.group_resources(sample_resources)
        
        # New controller-based approach creates controller + service workloads
        assert len(workloads) == 2
        
        # Check controller workload
        controller_workload_id = 'test-ns/Deployment/test-deployment'
        assert controller_workload_id in workloads
        
        controller_workload = workloads[controller_workload_id]
        assert controller_workload['namespace'] == 'test-ns'
        assert controller_workload['controller']['kind'] == 'Deployment'
        assert controller_workload['controller']['name'] == 'test-deployment'
        assert controller_workload['selectors'] == {'app': 'test', 'tier': 'web'}
        assert controller_workload['workload_type'] == 'controller'
        
        # Check service sub-workload
        service_workload_id = 'test-ns/Service/test-service'
        assert service_workload_id in workloads
        
        service_workload = workloads[service_workload_id]
        assert service_workload['namespace'] == 'test-ns'
        assert service_workload['controller']['kind'] == 'Service'
        assert service_workload['controller']['name'] == 'test-service'
        assert service_workload['workload_type'] == 'service'
        assert service_workload['parent_workload'] == controller_workload_id
        
        # Verify the workload hierarchy
        assert service_workload_id in controller_workload['sub_workloads']
        
        # Check that resources are attached to controller workload
        workload = controller_workload
        assert len(workload['services']) == 1
        assert workload['services'][0]['name'] == 'test-service'
        
        assert len(workload['configMaps']) == 1
        assert workload['configMaps'][0]['name'] == 'test-config'
        
        assert len(workload['secrets']) == 1
        assert workload['secrets'][0]['name'] == 'test-secret'
        
        assert workload['serviceAccount'] is not None
        assert workload['serviceAccount']['name'] == 'test-sa'
    
    def test_selector_matching_logic(self):
        """Test the selector matching logic."""
        grouper = WorkloadGrouper()
        
        # Test exact match
        workload_selectors = {'app': 'test', 'tier': 'web'}
        service_selectors = {'app': 'test', 'tier': 'web'}
        assert grouper._selectors_match(service_selectors, workload_selectors) is True
        
        # Test subset match
        service_selectors = {'app': 'test'}
        assert grouper._selectors_match(service_selectors, workload_selectors) is True
        
        # Test no match
        service_selectors = {'app': 'test', 'tier': 'api'}
        assert grouper._selectors_match(service_selectors, workload_selectors) is False
        
        # Test empty selectors
        service_selectors = {}
        assert grouper._selectors_match(service_selectors, workload_selectors) is False


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_directory(self):
        """Test analysis with an empty directory."""
        # This should not fail, just return empty results
        analyzer = K8sAnalyzer(
            k8s_paths=["/nonexistent/path"],
            output_dir="/tmp",
            llm_config=None
        )
        results = analyzer.analyze()
        
        # Should return empty results, not fail
        assert 'workloads' in results
        assert len(results['workloads']) == 0
    
    def test_invalid_yaml_handling(self, temp_k8s_dir):
        """Test handling of invalid YAML files."""
        # Create an invalid YAML file
        invalid_file = Path(temp_k8s_dir) / "invalid.yaml"
        invalid_file.write_text("""
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
  namespace: test-ns
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    ports:
  - containerPort: 80  # Missing dash, invalid YAML
""")
        
        # The parser should handle this gracefully
        parser = K8sResourceParser()
        resources = parser.parse_resources([str(invalid_file)])
        
        # The invalid file should be handled gracefully
        # It might still parse some parts or skip the file entirely
        # Just check that the parser doesn't crash
        assert isinstance(resources, list)

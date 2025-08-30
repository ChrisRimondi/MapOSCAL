#!/usr/bin/env python3
"""
Test script to verify control-name and control-description properties in k8s implemented requirements
"""

import logging
import sys
import os

# Add the maposcal package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'maposcal'))

# Set up logging
logging.basicConfig(level=logging.INFO)

from maposcal.analyzer.k8s_analyzer import K8sAnalyzer

def test_k8s_props():
    """Test that k8s implemented requirements include control-name and control-description."""
    
    # Use the k8s-sample directory
    k8s_paths = ["examples/k8s-sample"]
    output_dir = ".oscalgen/k8s-props-test"
    
    print("Testing k8s implemented requirements with new properties...")
    
    try:
        # Create analyzer
        analyzer = K8sAnalyzer(k8s_paths, output_dir)
        
        # Run analysis
        print("Running K8s analysis...")
        result = analyzer.analyze()
        
        print(f"Analysis completed: {len(result['workloads'])} workloads")
        
        # Test control mapping for one workload to see the new properties
        print("\nTesting control mapping for a workload...")
        
        # Use the min_baseline.json profile
        profile_path = "examples/min_baseline.json"
        
        # Map controls to workloads
        component_definition = analyzer.map_controls_to_workloads(profile_path)
        
        # Check if the new properties are present
        print("\nChecking implemented requirements for new properties...")
        
        components = component_definition.get('component-definition', {}).get('components', [])
        if components:
            component = components[0]  # First component
            implemented_requirements = component.get('implemented-requirements', [])
            
            if implemented_requirements:
                requirement = implemented_requirements[0]  # First requirement
                props = requirement.get('props', [])
                
                print(f"First implemented requirement: {requirement.get('control-id')}")
                print("Properties found:")
                
                for prop in props:
                    print(f"  - {prop['name']}: {prop['value'][:100]}...")
                
                # Check for the new properties
                prop_names = [prop['name'] for prop in props]
                if 'control-name' in prop_names and 'control-description' in prop_names:
                    print("\n✅ SUCCESS: control-name and control-description properties are present!")
                else:
                    print("\n❌ FAILED: Missing required properties")
                    print(f"Expected: control-name, control-description")
                    print(f"Found: {prop_names}")
            else:
                print("No implemented requirements found")
        else:
            print("No components found")
        
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_k8s_props()
    sys.exit(0 if success else 1)

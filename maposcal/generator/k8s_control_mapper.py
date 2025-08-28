"""
Kubernetes Control Mapper for MapOSCAL

This module provides Kubernetes-specific control mapping functionality that follows
the same pattern as the existing control_mapper.py but is tailored for Kubernetes
manifests and Argo CD applications.

It integrates with the control hints system to identify relevant controls and
generates OSCAL control implementations using LLM-powered RAG flows.
"""

import logging
import uuid
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

from maposcal.utils.control_hints_enumerator import search_control_hints_in_content
from maposcal.llm.llm_handler import LLMHandler
from maposcal.llm.prompt_templates import build_k8s_rich_control_mapping_prompt

logger = logging.getLogger(__name__)


@dataclass
class K8sWorkloadContext:
    """Context information for a Kubernetes workload."""
    name: str
    namespace: str
    resource_types: List[str]
    images: List[Dict[str, Any]]
    manifest_content: str
    source_path: Optional[str] = None





class K8sControlMapper:
    """
    Maps Kubernetes workloads to security controls using control hints and LLM-powered analysis.
    
    This class follows the same pattern as the existing control_mapper.py but is
    specifically designed for Kubernetes manifests and Argo CD applications.
    """
    
    def __init__(self, llm_config: Optional[Dict[str, Any]] = None, profile_controls: Optional[Dict[str, Any]] = None):
        """
        Initialize the K8s Control Mapper.
        
        Args:
            llm_config: Optional LLM configuration parameters
            profile_controls: Dictionary of profile-relevant controls from ProfileControlExtractor
        """
        self.llm_config = llm_config or {}
        self.profile_controls = profile_controls or {}
        self.llm_handler = self._initialize_llm_handler()
        
    def _initialize_llm_handler(self) -> LLMHandler:
        """Initialize the LLM handler with configuration."""
        if self.llm_config:
            return LLMHandler(
                provider=self.llm_config["provider"], 
                model=self.llm_config["model"]
            )
            # Set custom temperature if specified
            if "temperature" in self.llm_config:
                self.llm_handler.default_temperature = self.llm_config["temperature"]
        else:
            return LLMHandler(command="generate")
    
    def map_workload_controls(
        self, 
        workload: K8sWorkloadContext,
        top_k_controls: int = None  # Remove limit to process all profile controls
    ) -> Dict[str, Any]:
        """
        Map security controls to a Kubernetes workload.
        
        Args:
            workload: The workload context to analyze
            top_k_controls: Maximum number of controls to return (None = all profile controls)
            
        Returns:
            Dictionary containing mapped controls and implementation details
        """
        logger.info(f"Mapping controls for workload: {workload.name} in namespace {workload.namespace}")
        
        # Step 1: Identify relevant controls using control hints
        relevant_controls = self._identify_relevant_controls(workload)
        
        # Step 2: Use all relevant controls (no limit unless specified)
        if top_k_controls:
            top_controls = relevant_controls[:top_k_controls]
        else:
            top_controls = relevant_controls  # Process all profile controls
        
        # Step 3: Generate control implementations using LLM (batched approach)
        control_implementations = self._generate_control_implementations_batched(workload, top_controls)
        
        return {
            "workload_name": workload.name,
            "namespace": workload.namespace,
            "resource_types": workload.resource_types,
            "total_controls_found": len(relevant_controls),
            "top_controls": top_controls,
            "control_implementations": control_implementations,
            "mapping_timestamp": str(uuid.uuid4())
        }
    
    def _identify_relevant_controls(self, workload: K8sWorkloadContext) -> List[str]:
        """
        Return ALL profile controls - let LLM decide applicability.
        
        Args:
            workload: The workload context to analyze
            
        Returns:
            List of ALL profile control IDs for LLM analysis
        """
        logger.debug(f"Providing all profile controls to LLM for workload {workload.name}")
        
        if not self.profile_controls:
            logger.warning("No profile controls available, returning empty list")
            return []
        
        # Return all profile control IDs - no filtering
        # Let the LLM decide which ones are applicable, have gaps, etc.
        profile_control_ids = list(self.profile_controls.keys())
        
        logger.info(f"Providing {len(profile_control_ids)} profile controls to LLM for analysis")
        
        return profile_control_ids
    
    def _get_control_hints_context(self, workload: K8sWorkloadContext) -> Dict[str, Any]:
        """
        Get control hints context to help LLM understand what to look for.
        
        Args:
            workload: The workload context to analyze
            
        Returns:
            Dictionary with control hints context for LLM analysis
        """
        try:
            from maposcal.utils.control_hints_enumerator import get_all_control_hints, search_control_hints_in_content
            
            # Get all control hints
            all_hints = get_all_control_hints()
            
            # Search for control hints in the manifest content
            found_controls = search_control_hints_in_content(
                workload.manifest_content, 
                "kubernetes"
            )
            
            # Build context for LLM
            hints_context = {
                "total_hints_available": len(all_hints),
                "hints_found_in_manifest": found_controls,
                "hint_examples": {}
            }
            
            # Add examples of hints for found controls
            for control_id in found_controls[:5]:  # Limit to first 5 for context
                if control_id in all_hints:
                    hints_context["hint_examples"][control_id] = all_hints[control_id].get("kubernetes", [])[:3]
            
            logger.info(f"Found {len(found_controls)} control hints in manifest for LLM context")
            return hints_context
            
        except Exception as e:
            logger.warning(f"Failed to get control hints context: {e}")
            return {}
    
    def _get_simplified_hints_context(self, workload: K8sWorkloadContext) -> str:
        """Get simplified control hints context to reduce prompt length."""
        try:
            # Get control hints for this workload
            hints = search_control_hints_in_content(workload.manifest_content, "kubernetes")
            
            if not hints:
                return "No specific security hints found"
            
            # Limit to top 5 most relevant hints
            limited_hints = hints[:5]
            
            # Format as simple list
            return " | ".join([h.split("#")[0].strip() for h in limited_hints])
            
        except Exception as e:
            logger.warning(f"Failed to get hints context: {e}")
            return "Hints analysis failed"
    
    def _get_matched_hints(self, manifest_content: str, hints: List[str]) -> List[str]:
        """Get the hints that actually matched in the manifest content."""
        manifest_words = set(manifest_content.lower().split())
        matched = []
        
        for hint in hints:
            clean_hint = hint.split("#")[0].strip().lower()
            if clean_hint and clean_hint in manifest_words:
                matched.append(hint)
        
        return matched
    
    def _summarize_workload_context(self, workload: K8sWorkloadContext) -> str:
        """Create a summary of the workload context for LLM prompts."""
        summary = f"Workload: {workload.name}\n"
        summary += f"Namespace: {workload.namespace}\n"
        summary += f"Resource Types: {', '.join(workload.resource_types)}\n"
        summary += f"Container Images: {len(workload.images)}\n"
        
        if workload.source_path:
            summary += f"Source Path: {workload.source_path}\n"
        
        return summary
    
    def _extract_relevant_sections(self, workload: K8sWorkloadContext, control_id: str) -> List[str]:
        """Extract manifest sections relevant to a specific control."""
        # This is a simplified implementation
        # In a full implementation, you might want to parse YAML and extract specific sections
        
        relevant_sections = []
        manifest_lines = workload.manifest_content.split('\n')
        
        # Look for lines that might be relevant to the control
        for line in manifest_lines:
            if any(keyword in line.lower() for keyword in ['security', 'auth', 'rbac', 'network', 'secret']):
                relevant_sections.append(line.strip())
        
        return relevant_sections[:10]  # Limit to 10 most relevant lines
    
    def _analyze_workload_security(self, workload_name: str, namespace: str) -> List[str]:
        """Analyze security-relevant configurations for a workload."""
        security_info = []
        
        try:
            # Get workload details from plan (this would need to be passed in or accessed differently)
            # For now, provide basic security analysis based on common patterns
            
            security_info.append("• Workload Security Context: Container isolation and resource limits")
            security_info.append("• Network Security: Service exposure and network policies")
            security_info.append("• Access Control: RBAC and service account configurations")
            security_info.append("• Data Protection: Secret and ConfigMap management")
            security_info.append("• Monitoring: Logging and audit capabilities")
            
        except Exception as e:
            security_info.append(f"Error analyzing security: {e}")
        
        return security_info
    
    def _generate_control_implementations_batched(
        self, 
        workload: K8sWorkloadContext, 
        control_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Generate control implementations using batched LLM approach for better performance.
        
        Args:
            workload: The workload context
            control_ids: List of control IDs to implement
            
        Returns:
            Dictionary containing control implementations
        """
        logger.info(f"Generating implementations for {len(control_ids)} controls using batched approach")
        
        implementations = {}
        
        # Process controls in smaller batches to avoid rate limits
        batch_size = 3  # Process 3 controls at a time
        for i in range(0, len(control_ids), batch_size):
            batch = control_ids[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}: {batch}")
            
            for control_id in batch:
                try:
                    implementation = self._generate_control_implementation(
                        workload, control_id
                    )
                    if implementation:
                        implementations[control_id] = implementation
                    
                except Exception as e:
                    logger.error(f"Failed to generate implementation for {control_id}: {e}")
                    implementations[control_id] = {
                        "status": "failed",
                        "error": str(e),
                        "control_id": control_id
                    }
            
            # Add small delay between batches to avoid rate limiting
            if i + batch_size < len(control_ids):
                import time
                time.sleep(1)
        
        return implementations

    def _generate_control_implementations(
        self, 
        workload: K8sWorkloadContext, 
        control_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Generate control implementations using LLM-powered analysis.
        
        Args:
            workload: The workload context
            control_ids: List of control IDs to implement
            
        Returns:
            Dictionary containing control implementations
        """
        logger.info(f"Generating implementations for {len(control_ids)} controls")
        
        implementations = {}
        
        for control_id in control_ids:
            try:
                implementation = self._generate_control_implementation(
                    workload, control_id
                )
                if implementation:
                    implementations[control_id] = implementation
                
            except Exception as e:
                logger.error(f"Failed to generate implementation for {control_id}: {e}")
                implementations[control_id] = {
                    "status": "failed",
                    "error": str(e),
                    "control_id": control_id
                }
        
        return implementations
    
    def _generate_control_implementation(self, workload: K8sWorkloadContext, control_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate rich OSCAL-compliant control implementation using LLM.
        
        Args:
            workload: Kubernetes workload context
            control_id: Control ID to implement
            
        Returns:
            OSCAL-compliant control implementation dict or None if generation failed
        """
        try:
            # Get control information from profile
            control_info = self.profile_controls.get(control_id, {})
            control_name = control_info.get("title", f"{control_id.upper()} - Security Control")
            control_description = control_info.get("description", f"Security control {control_id} for system protection and compliance.")
            
            # Get control hints context for better analysis (simplified)
            hints_context = self._get_simplified_hints_context(workload)
            
            # Build comprehensive workload context
            workload_context = self._build_comprehensive_workload_context(workload)
            
            # Generate UUIDs for OSCAL compliance
            import uuid
            main_uuid = str(uuid.uuid4())
            statement_uuid = str(uuid.uuid4())
            
            # Build rich prompt for LLM
            prompt = build_k8s_rich_control_mapping_prompt(
                control_id=control_id,
                control_name=control_name,
                control_description=control_description,
                workload_context=workload_context,
                hints_context=json.dumps(hints_context, indent=2),
                manifest_content=workload.manifest_content,
                main_uuid=main_uuid,
                statement_uuid=statement_uuid
            )
            
            # Generate implementation using LLM with default token configuration
            response = self.llm_handler.query(prompt=prompt)
            
            if response and response.strip():
                try:
                    # Parse LLM response
                    implementation = json.loads(response.strip())
                    
                    # Validate required fields
                    if self._validate_oscal_implementation(implementation):
                        logger.info(f"Successfully generated OSCAL implementation for {control_id}")
                        return implementation
                    else:
                        logger.warning(f"Generated implementation for {control_id} missing required fields, using fallback")
                        return self._generate_basic_implementation(workload, control_id)
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse LLM response for {control_id}: {e}")
                    logger.debug(f"Raw response: {response}")
                    return self._generate_basic_implementation(workload, control_id)
            else:
                logger.warning(f"No response from LLM for {control_id}, using fallback")
                return self._generate_basic_implementation(workload, control_id)
                
        except Exception as e:
            logger.error(f"Failed to generate implementation for {control_id}: {e}")
            return self._generate_basic_implementation(workload, control_id)
    
    def _build_comprehensive_workload_context(self, workload: K8sWorkloadContext) -> str:
        """Build concise workload context for LLM analysis."""
        context_parts = []
        
        # Basic workload information (concise)
        context_parts.append(f"Name: {workload.name}")
        context_parts.append(f"Namespace: {workload.namespace}")
        context_parts.append(f"Resources: {', '.join(workload.resource_types)}")
        context_parts.append(f"Images: {len(workload.images)}")
        
        # Security summary (concise)
        context_parts.append(f"Security: Container isolation, network policies, RBAC")
        
        return " | ".join(context_parts)
    
    def _validate_oscal_implementation(self, implementation: Dict[str, Any]) -> bool:
        """Validate that generated implementation has required OSCAL fields."""
        required_fields = ["uuid", "control-id", "props", "annotations", "statements"]
        
        for field in required_fields:
            if field not in implementation:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Check props structure
        if "props" in implementation:
            required_props = ["control-status", "control-name", "control-description", "control-explanation"]
            prop_names = [prop.get("name") for prop in implementation["props"]]
            
            for required_prop in required_props:
                if required_prop not in prop_names:
                    logger.warning(f"Missing required prop: {required_prop}")
                    return False
        
        return True
    
    def _generate_basic_implementation(self, workload: K8sWorkloadContext, control_id: str) -> Dict[str, Any]:
        """Generate a basic control implementation based on workload characteristics."""
        
        # Get control description from profile
        control_info = self.profile_controls.get(control_id, {})
        
        # Analyze manifest for relevant sections
        relevant_sections = self._extract_relevant_manifest_sections(workload, control_id)
        
        # Generate implementation status based on evidence
        implementation_status = self._determine_implementation_status(workload, control_id, relevant_sections)
        
        # Create basic implementation structure
        implementation = {
            "control_id": control_id.upper(),
            "control_title": control_info.get("title", f"{control_id.upper()} - Security Control"),
            "status": implementation_status,
            "evidence": relevant_sections,
            "resource_types": workload.resource_types,
            "images": workload.images,
            "implementation_details": self._generate_implementation_details(workload, control_id, relevant_sections),
            "gaps": self._identify_implementation_gaps(workload, control_id, relevant_sections),
            "recommendations": self._generate_recommendations(workload, control_id, relevant_sections),
            "compliance_level": self._assess_compliance_level(implementation_status)
        }
        
        return implementation
    
    def _extract_relevant_manifest_sections(self, workload: K8sWorkloadContext, control_id: str) -> List[str]:
        """Extract manifest sections relevant to the control."""
        relevant_sections = []
        manifest_lines = workload.manifest_content.split('\n')
        
        # Look for lines that might be relevant to the control
        control_keywords = self._get_control_keywords(control_id)
        
        for line in manifest_lines:
            line_lower = line.lower()
            if any(keyword.lower() in line_lower for keyword in control_keywords):
                relevant_sections.append(line.strip())
        
        # Limit to most relevant sections
        return relevant_sections[:5]
    
    def _get_control_keywords(self, control_id: str) -> List[str]:
        """Get relevant keywords for a control based on its family."""
        control_family = control_id.split("-")[0].lower()
        
        keyword_mapping = {
            "ac": ["serviceaccount", "rbac", "role", "rolebinding", "securitycontext", "runasuser", "runasgroup"],
            "sc": ["networkpolicy", "ingress", "service", "tls", "secret", "encryption", "securitycontext"],
            "cm": ["configmap", "secret", "environment", "volume", "mount", "config"],
            "si": ["securitycontext", "readonlyrootfilesystem", "allowprivilegeescalation", "runasnonroot"],
            "au": ["log", "audit", "monitoring", "metrics", "trace"],
            "ia": ["serviceaccount", "token", "authentication", "authorization", "identity"]
        }
        
        return keyword_mapping.get(control_family, ["security", "config", "policy"])
    
    def _determine_implementation_status(self, workload: K8sWorkloadContext, control_id: str, relevant_sections: List[str]) -> str:
        """Determine the implementation status based on evidence."""
        if not relevant_sections:
            return "not-implemented"
        
        # Check if we have strong evidence based on relevant sections
        if len(relevant_sections) >= 2:
            return "implemented"
        elif len(relevant_sections) >= 1:
            return "partially-implemented"
        else:
            return "not-implemented"
    
    def _generate_implementation_details(self, workload: K8sWorkloadContext, control_id: str, relevant_sections: List[str]) -> str:
        """Generate implementation details based on workload and control."""
        control_family = control_id.split("-")[0].lower()
        
        if control_family == "ac":
            return f"Access control mechanisms implemented through {', '.join(workload.resource_types)} with relevant security configurations."
        elif control_family == "sc":
            return f"System and communications protection implemented through network policies, services, and security configurations."
        elif control_family == "cm":
            return f"Configuration management implemented through ConfigMaps, Secrets, and configuration elements."
        elif control_family == "si":
            return f"System and information integrity implemented through security contexts and integrity controls."
        elif control_family == "au":
            return f"Audit and accountability implemented through logging and monitoring with audit configurations."
        elif control_family == "ia":
            return f"Identification and authentication implemented through service accounts and identity controls."
        else:
            return f"Security control {control_id} implemented through relevant configurations."
    
    def _identify_implementation_gaps(self, workload: K8sWorkloadContext, control_id: str, relevant_sections: List[str]) -> List[str]:
        """Identify potential implementation gaps."""
        gaps = []
        
        if not relevant_sections:
            gaps.append(f"No manifest evidence found for control {control_id}")
        
        # Check for common gaps based on control family
        control_family = control_id.split("-")[0].lower()
        
        if control_family == "ac" and "serviceaccount" not in workload.manifest_content.lower():
            gaps.append("No explicit service account configuration found")
        
        if control_family == "sc" and "networkpolicy" not in workload.manifest_content.lower():
            gaps.append("No network policy configuration found")
        
        if control_family == "si" and "securitycontext" not in workload.manifest_content.lower():
            gaps.append("No security context configuration found")
        
        return gaps
    
    def _generate_recommendations(self, workload: K8sWorkloadContext, control_id: str, relevant_sections: List[str]) -> List[str]:
        """Generate recommendations for improving control implementation."""
        recommendations = []
        
        if not relevant_sections:
            recommendations.append(f"Add manifest configurations that address control {control_id} requirements")
        
        # Control-specific recommendations
        control_family = control_id.split("-")[0].lower()
        
        if control_family == "ac":
            recommendations.append("Implement explicit RBAC policies and service account configurations")
        
        if control_family == "sc":
            recommendations.append("Configure network policies and TLS encryption for communications")
        
        if control_family == "si":
            recommendations.append("Add security contexts with least privilege principles")
        
        return recommendations
    
    def _assess_compliance_level(self, implementation_status: str) -> str:
        """Assess the overall compliance level."""
        if implementation_status == "implemented":
            return "high"
        elif implementation_status == "partially-implemented":
            return "medium"
        else:
            return "low"

def create_k8s_workload_context(
    name: str,
    namespace: str,
    resource_types: List[str],
    images: List[Dict[str, Any]],
    manifest_content: str,
    source_path: Optional[str] = None
) -> K8sWorkloadContext:
    """
    Create a K8sWorkloadContext object.
    
    Args:
        name: Workload name
        namespace: Kubernetes namespace
        resource_types: Types of Kubernetes resources
        images: List of container images
        manifest_content: Raw manifest content
        source_path: Optional source path
        
    Returns:
        K8sWorkloadContext object
    """
    return K8sWorkloadContext(
        name=name,
        namespace=namespace,
        resource_types=resource_types,
        images=images,
        manifest_content=manifest_content,
        source_path=source_path
    )



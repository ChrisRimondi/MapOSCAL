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
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

from maposcal.utils.control_hints_enumerator import search_control_hints_in_content
from maposcal.llm.llm_handler import LLMHandler
from maposcal.llm.prompt_templates import build_k8s_control_mapping_prompt

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


@dataclass
class ControlMatch:
    """Information about a matched control."""
    control_id: str
    confidence_score: float
    matched_hints: List[str]
    workload_context: str
    relevant_manifest_sections: List[str]


class K8sControlMapper:
    """
    Maps Kubernetes workloads to security controls using control hints and LLM-powered analysis.
    
    This class follows the same pattern as the existing control_mapper.py but is
    specifically designed for Kubernetes manifests and Argo CD applications.
    """
    
    def __init__(self, llm_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the K8s Control Mapper.
        
        Args:
            llm_config: Optional LLM configuration parameters
        """
        self.llm_config = llm_config or {}
        self.llm_handler = self._initialize_llm_handler()
        
    def _initialize_llm_handler(self) -> LLMHandler:
        """Initialize the LLM handler with configuration."""
        if self.llm_config:
            return LLMHandler(
                provider=self.llm_config.get("provider", "openai"),
                model=self.llm_config.get("model", "gpt-4")
            )
        else:
            return LLMHandler(command="generate")
    
    def map_workload_controls(
        self, 
        workload: K8sWorkloadContext,
        top_k_controls: int = 10
    ) -> Dict[str, Any]:
        """
        Map security controls to a Kubernetes workload.
        
        Args:
            workload: The workload context to analyze
            top_k_controls: Maximum number of controls to return
            
        Returns:
            Dictionary containing mapped controls and implementation details
        """
        logger.info(f"Mapping controls for workload: {workload.name} in namespace {workload.namespace}")
        
        # Step 1: Identify relevant controls using control hints
        relevant_controls = self._identify_relevant_controls(workload)
        
        # Step 2: Score and rank controls by relevance
        scored_controls = self._score_control_relevance(workload, relevant_controls)
        
        # Step 3: Select top-k most relevant controls
        top_controls = scored_controls[:top_k_controls]
        
        # Step 4: Generate control implementations using LLM
        control_implementations = self._generate_control_implementations(workload, top_controls)
        
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
        Identify relevant controls using control hints analysis.
        
        Args:
            workload: The workload context to analyze
            
        Returns:
            List of relevant control IDs
        """
        logger.debug(f"Identifying relevant controls for workload {workload.name}")
        
        # Get all control hints
        from maposcal.utils.control_hints_enumerator import get_all_control_hints
        all_hints = get_all_control_hints()
        
        # Search for control hints in the manifest content
        found_controls = search_control_hints_in_content(
            workload.manifest_content, 
            "kubernetes"
        )
        
        # Also search in generic hints for broader coverage
        # Generic hints are stored in the "generic" field of each control
        generic_controls = []
        manifest_words = set(workload.manifest_content.lower().split())
        
        for control_id, hints_dict in all_hints.items():
            generic_hints = hints_dict.get("generic", [])
            for hint in generic_hints:
                clean_hint = hint.split("#")[0].strip().lower()
                if clean_hint and clean_hint in manifest_words:
                    generic_controls.append(control_id)
                    break  # One match is enough for this control
        
        # Combine and deduplicate
        all_controls = list(set(found_controls + generic_controls))
        
        logger.info(f"Found {len(all_controls)} relevant controls for workload {workload.name}")
        return all_controls
    
    def _score_control_relevance(
        self, 
        workload: K8sWorkloadContext, 
        control_ids: List[str]
    ) -> List[ControlMatch]:
        """
        Score controls by relevance to the workload.
        
        Args:
            workload: The workload context
            control_ids: List of control IDs to score
            
        Returns:
            List of ControlMatch objects sorted by relevance score
        """
        logger.debug(f"Scoring {len(control_ids)} controls for relevance")
        
        control_matches = []
        
        for control_id in control_ids:
            # Get hints for this control
            from maposcal.utils.control_hints_enumerator import get_all_control_hints
            all_hints = get_all_control_hints()
            hints_dict = all_hints.get(control_id, {})
            
            k8s_hints = hints_dict.get("kubernetes", [])
            generic_hints = hints_dict.get("generic", [])
            
            all_hints = k8s_hints + generic_hints
            
            if not all_hints:
                continue
            
            # Calculate relevance score based on hint matches
            score = self._calculate_relevance_score(workload, control_id, all_hints)
            
            # Get matched hints
            matched_hints = self._get_matched_hints(workload.manifest_content, all_hints)
            
            # Create control match
            control_match = ControlMatch(
                control_id=control_id,
                confidence_score=score,
                matched_hints=matched_hints,
                workload_context=self._summarize_workload_context(workload),
                relevant_manifest_sections=self._extract_relevant_sections(workload, control_id)
            )
            
            control_matches.append(control_match)
        
        # Sort by confidence score (highest first)
        control_matches.sort(key=lambda x: x.confidence_score, reverse=True)
        
        logger.info(f"Scored {len(control_matches)} controls for workload {workload.name}")
        return control_matches
    
    def _calculate_relevance_score(
        self, 
        workload: K8sWorkloadContext, 
        control_id: str, 
        hints: List[str]
    ) -> float:
        """
        Calculate relevance score for a control based on workload characteristics.
        
        Args:
            workload: The workload context
            control_id: The control ID to score
            hints: List of hints for this control
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        score = 0.0
        
        # Base score from hint matches
        manifest_words = set(workload.manifest_content.lower().split())
        hint_matches = sum(1 for hint in hints if hint.lower() in manifest_words)
        hint_score = min(hint_matches / len(hints), 1.0) if hints else 0.0
        score += hint_score * 0.6  # 60% weight for hint matches
        
        # Resource type relevance
        resource_score = self._calculate_resource_type_relevance(control_id, workload.resource_types)
        score += resource_score * 0.3  # 30% weight for resource types
        
        # Image security relevance
        image_score = self._calculate_image_security_relevance(control_id, workload.images)
        score += image_score * 0.1  # 10% weight for image security
        
        return min(score, 1.0)
    
    def _calculate_resource_type_relevance(self, control_id: str, resource_types: List[str]) -> float:
        """Calculate relevance based on resource types."""
        # Define control-to-resource mappings
        control_resource_mapping = {
            "ac2": ["ServiceAccount", "Secret"],  # Account Management
            "ac3": ["Role", "RoleBinding", "ClusterRole", "ClusterRoleBinding"],  # Access Enforcement
            "ac4": ["NetworkPolicy"],  # Information Flow Enforcement
            "ac6": ["Deployment", "Pod", "StatefulSet", "DaemonSet"],  # Least Privilege
            "ia2": ["ServiceAccount"],  # Identification and Authentication
            "ia5": ["Secret", "ExternalSecret"],  # Authenticator Management
            "cm6": ["ClusterPolicy", "ConstraintTemplate"],  # Configuration Settings
            "sc7": ["NetworkPolicy", "Ingress"],  # Boundary Protection
            "sc8": ["Ingress", "Secret"],  # Transmission Confidentiality
            "sc12": ["Certificate", "Issuer"],  # Cryptographic Key Management
            "sc28": ["Secret", "ExternalSecret"],  # Protection of Information at Rest
        }
        
        relevant_resources = control_resource_mapping.get(control_id, [])
        if not relevant_resources:
            return 0.0
        
        matches = sum(1 for rt in resource_types if rt in relevant_resources)
        return matches / len(relevant_resources)
    
    def _calculate_image_security_relevance(self, control_id: str, images: List[Dict[str, Any]]) -> float:
        """Calculate relevance based on image security characteristics."""
        if not images:
            return 0.0
        
        # Define control-to-image-security mappings
        image_security_mapping = {
            "si7": ["@sha256:", "digest:", "cosign"],  # Software Integrity
            "sa12": ["cosign", "policy.sigstore.dev"],  # Supply Chain Protection
            "ra5": ["trivy", "grype", "anchore"],  # Vulnerability Scanning
        }
        
        relevant_patterns = image_security_mapping.get(control_id, [])
        if not relevant_patterns:
            return 0.0
        
        # Check if any images contain relevant security patterns
        image_content = " ".join(str(img) for img in images)
        matches = sum(1 for pattern in relevant_patterns if pattern.lower() in image_content.lower())
        return matches / len(relevant_patterns)
    
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
    
    def _generate_control_implementations(
        self, 
        workload: K8sWorkloadContext, 
        control_matches: List[ControlMatch]
    ) -> Dict[str, Any]:
        """
        Generate control implementations using LLM-powered analysis.
        
        Args:
            workload: The workload context
            control_matches: List of control matches to implement
            
        Returns:
            Dictionary containing control implementations
        """
        logger.info(f"Generating implementations for {len(control_matches)} controls")
        
        implementations = {}
        
        for control_match in control_matches:
            try:
                implementation = self._generate_single_control_implementation(
                    workload, control_match
                )
                implementations[control_match.control_id] = implementation
                
            except Exception as e:
                logger.error(f"Failed to generate implementation for {control_match.control_id}: {e}")
                implementations[control_match.control_id] = {
                    "status": "failed",
                    "error": str(e),
                    "control_id": control_match.control_id
                }
        
        return implementations
    
    def _generate_single_control_implementation(
        self, 
        workload: K8sWorkloadContext, 
        control_match: ControlMatch
    ) -> Dict[str, Any]:
        """
        Generate implementation for a single control.
        
        Args:
            workload: The workload context
            control_match: The control match being implemented
            
        Returns:
            Dictionary containing the control implementation
        """
        # Build prompt for this specific control
        prompt = build_k8s_control_mapping_prompt(
            control_id=control_match.control_id,
            workload_context=control_match.workload_context,
            matched_hints=control_match.matched_hints,
            relevant_sections=control_match.relevant_manifest_sections,
            confidence_score=control_match.confidence_score
        )
        
        # Query LLM
        response = self.llm_handler.query(prompt=prompt)
        
        # Parse response (this would need to be implemented based on your LLM response format)
        implementation = self._parse_llm_response(response, control_match)
        
        return implementation
    
    def _parse_llm_response(self, response: str, control_match: ControlMatch) -> Dict[str, Any]:
        """
        Parse LLM response into structured control implementation.
        
        Args:
            response: Raw LLM response
            control_match: The control match being implemented
            
        Returns:
            Structured control implementation
        """
        # This is a simplified implementation
        # In a full implementation, you'd want to parse structured output
        
        return {
            "control_id": control_match.control_id,
            "status": "implemented",
            "confidence_score": control_match.confidence_score,
            "implementation_details": response,
            "matched_hints": control_match.matched_hints,
            "generated_at": str(uuid.uuid4())
        }


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


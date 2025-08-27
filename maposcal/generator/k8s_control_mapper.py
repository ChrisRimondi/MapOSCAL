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
    
    def _create_control_dict(self, control_match: ControlMatch) -> Dict[str, Any]:
         """Create control_dict format for implementation generation."""
         # This is a simplified mapping - in a real implementation, you'd want to
         # map to actual NIST 800-53 control descriptions
         control_descriptions = {
             "ac": "Access Control - The organization limits information system access to authorized users, processes acting on behalf of authorized users, or devices (including other information systems).",
             "sc": "System and Communications Protection - The organization monitors, controls, and protects organizational communications (i.e., information transmitted or received by organizational information systems) at the external boundaries and key internal boundaries of the information systems.",
             "cm": "Configuration Management - The organization establishes and maintains baseline configurations and inventories of organizational information systems (including hardware, software, firmware, and documentation) throughout the respective system development life cycles.",
             "si": "System and Information Integrity - The organization identifies, reports, and corrects information and information system flaws in a timely manner.",
             "au": "Audit and Accountability - The organization creates, protects, and retains information system audit records to the extent needed to enable the monitoring, analysis, investigation, and reporting of unlawful, unauthorized, or inappropriate information system activity.",
             "ia": "Identification and Authentication - The organization identifies and authenticates organizational users (or processes acting on behalf of organizational users)."
         }
         
         control_family = control_match.control_id.split("-")[0].lower()
         base_description = control_descriptions.get(control_family, "Security control for system protection and compliance.")
         
         return {
             "id": control_match.control_id.upper(),
             "title": f"{control_match.control_id.upper()} - {base_description.split(' - ')[1] if ' - ' in base_description else base_description}",
             "statement": [base_description],
             "params": []  # No parameters for now
         }
     
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
                implementation = self._generate_control_implementation(
                    workload, control_match
                )
                if implementation:
                    implementations[control_match.control_id] = implementation
                
            except Exception as e:
                logger.error(f"Failed to generate implementation for {control_match.control_id}: {e}")
                implementations[control_match.control_id] = {
                    "status": "failed",
                    "error": str(e),
                    "control_id": control_match.control_id
                }
        
        return implementations
    
    def _generate_control_implementation(self, workload: K8sWorkloadContext, control_match: ControlMatch) -> Optional[Dict[str, Any]]:
        """
        Generate control implementation directly without FAISS dependency.
        
        Args:
            workload: Kubernetes workload context
            control_match: Control match with relevance scoring
            
        Returns:
            Control implementation dict or None if generation failed
        """
        try:
            # Generate a basic implementation without relying on FAISS
            implementation = self._generate_basic_implementation(workload, control_match)
            
            # Add workload-specific metadata
            implementation["workload_metadata"] = {
                "workload_name": workload.name,
                "namespace": workload.namespace,
                "resource_types": workload.resource_types,
                "confidence_score": control_match.confidence_score,
                "matched_hints": control_match.matched_hints
            }
            
            return implementation
                
        except Exception as e:
            logger.error(f"Failed to generate implementation for {control_match.control_id}: {e}")
            return None
    
    def _generate_basic_implementation(self, workload: K8sWorkloadContext, control_match: ControlMatch) -> Dict[str, Any]:
        """Generate a basic control implementation based on workload characteristics."""
        
        # Get control description
        control_dict = self._create_control_dict(control_match)
        
        # Analyze manifest for relevant sections
        relevant_sections = self._extract_relevant_manifest_sections(workload, control_match)
        
        # Generate implementation status based on evidence
        implementation_status = self._determine_implementation_status(workload, control_match, relevant_sections)
        
        # Create basic implementation structure
        implementation = {
            "control_id": control_match.control_id.upper(),
            "control_title": control_dict["title"],
            "status": implementation_status,
            "confidence_score": control_match.confidence_score,
            "evidence": relevant_sections,
            "matched_hints": control_match.matched_hints,
            "resource_types": workload.resource_types,
            "images": workload.images,
            "implementation_details": self._generate_implementation_details(workload, control_match, relevant_sections),
            "gaps": self._identify_implementation_gaps(workload, control_match, relevant_sections),
            "recommendations": self._generate_recommendations(workload, control_match, relevant_sections),
            "compliance_level": self._assess_compliance_level(implementation_status, control_match.confidence_score)
        }
        
        return implementation
    
    def _extract_relevant_manifest_sections(self, workload: K8sWorkloadContext, control_match: ControlMatch) -> List[str]:
        """Extract manifest sections relevant to the control."""
        relevant_sections = []
        manifest_lines = workload.manifest_content.split('\n')
        
        # Look for lines that might be relevant to the control
        control_keywords = self._get_control_keywords(control_match.control_id)
        
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
    
    def _determine_implementation_status(self, workload: K8sWorkloadContext, control_match: ControlMatch, relevant_sections: List[str]) -> str:
        """Determine the implementation status based on evidence."""
        if not relevant_sections:
            return "not-implemented"
        
        # Check if we have strong evidence
        strong_evidence_count = len([s for s in relevant_sections if any(hint.lower() in s.lower() for hint in control_match.matched_hints)])
        
        if strong_evidence_count >= 2:
            return "implemented"
        elif strong_evidence_count >= 1:
            return "partially-implemented"
        else:
            return "not-implemented"
    
    def _generate_implementation_details(self, workload: K8sWorkloadContext, control_match: ControlMatch, relevant_sections: List[str]) -> str:
        """Generate implementation details based on workload and control."""
        control_family = control_match.control_id.split("-")[0].lower()
        
        if control_family == "ac":
            return f"Access control mechanisms implemented through {', '.join(workload.resource_types)} with {len(control_match.matched_hints)} relevant security configurations."
        elif control_family == "sc":
            return f"System and communications protection implemented through network policies, services, and {len(control_match.matched_hints)} security configurations."
        elif control_family == "cm":
            return f"Configuration management implemented through ConfigMaps, Secrets, and {len(control_match.matched_hints)} configuration elements."
        elif control_family == "si":
            return f"System and information integrity implemented through security contexts and {len(control_match.matched_hints)} integrity controls."
        elif control_family == "au":
            return f"Audit and accountability implemented through logging and monitoring with {len(control_match.matched_hints)} audit configurations."
        elif control_family == "ia":
            return f"Identification and authentication implemented through service accounts and {len(control_match.matched_hints)} identity controls."
        else:
            return f"Security control {control_match.control_id} implemented through {len(control_match.matched_hints)} relevant configurations."
    
    def _identify_implementation_gaps(self, workload: K8sWorkloadContext, control_match: ControlMatch, relevant_sections: List[str]) -> List[str]:
        """Identify potential implementation gaps."""
        gaps = []
        
        if not relevant_sections:
            gaps.append(f"No manifest evidence found for control {control_match.control_id}")
        
        if control_match.confidence_score < 0.5:
            gaps.append(f"Low confidence score ({control_match.confidence_score:.2f}) suggests incomplete implementation")
        
        # Check for common gaps based on control family
        control_family = control_match.control_id.split("-")[0].lower()
        
        if control_family == "ac" and "serviceaccount" not in workload.manifest_content.lower():
            gaps.append("No explicit service account configuration found")
        
        if control_family == "sc" and "networkpolicy" not in workload.manifest_content.lower():
            gaps.append("No network policy configuration found")
        
        if control_family == "si" and "securitycontext" not in workload.manifest_content.lower():
            gaps.append("No security context configuration found")
        
        return gaps
    
    def _generate_recommendations(self, workload: K8sWorkloadContext, control_match: ControlMatch, relevant_sections: List[str]) -> List[str]:
        """Generate recommendations for improving control implementation."""
        recommendations = []
        
        if control_match.confidence_score < 0.7:
            recommendations.append(f"Increase implementation coverage for control {control_match.control_id}")
        
        if not relevant_sections:
            recommendations.append(f"Add manifest configurations that address control {control_match.control_id} requirements")
        
        # Control-specific recommendations
        control_family = control_match.control_id.split("-")[0].lower()
        
        if control_family == "ac":
            recommendations.append("Implement explicit RBAC policies and service account configurations")
        
        if control_family == "sc":
            recommendations.append("Configure network policies and TLS encryption for communications")
        
        if control_family == "si":
            recommendations.append("Add security contexts with least privilege principles")
        
        return recommendations
    
    def _assess_compliance_level(self, implementation_status: str, confidence_score: float) -> str:
        """Assess the overall compliance level."""
        if implementation_status == "implemented" and confidence_score >= 0.8:
            return "high"
        elif implementation_status == "partially-implemented" or confidence_score >= 0.5:
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



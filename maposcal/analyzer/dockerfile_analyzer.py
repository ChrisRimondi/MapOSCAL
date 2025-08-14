"""
Dockerfile Analyzer for MapOSCAL.

This module provides specialized analysis of Dockerfiles and related ENTRYPOINT scripts,
creating separate FAISS indices and metadata for container security analysis.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import hashlib
import json

from maposcal.embeddings import local_embedder, faiss_index, meta_store
from maposcal.inspectors.inspect_dockerfile import start_inspection
from maposcal.utils.dockerfile_control_hints import is_transport_security_configured

logger = logging.getLogger(__name__)


class DockerfileAnalyzer:
    """
    Analyzes Dockerfiles and related scripts for security controls and compliance.
    
    This analyzer creates separate FAISS indices and metadata for Dockerfile analysis,
    allowing for specialized container security assessment without interfering with
    regular code analysis.
    """
    
    def __init__(self, repo_path: str, output_dir: str, config: Dict[str, Any] = None):
        """
        Initialize the Dockerfile analyzer.
        
        Args:
            repo_path: Path to the repository root
            output_dir: Directory to store analysis results
            config: Configuration dictionary with Dockerfile settings
        """
        self.repo_path = Path(repo_path)
        self.output_dir = Path(output_dir)
        self.config = config or {}
        
        # Dockerfile configuration
        self.dockerfile_path = self.config.get("dockerfile", {}).get("path", "Dockerfile")
        self.transport_security = self.config.get("dockerfile", {}).get("transport_security", False)
        self.entrypoint_analysis = self.config.get("dockerfile", {}).get("entrypoint_analysis", True)
        
        # Analysis results
        self.dockerfile_results = {}
        self.entrypoint_results = {}
        self.vectors = []
        self.metadata = []
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive Dockerfile analysis.
        
        Returns:
            Dictionary containing analysis results and metadata
        """
        logger.info("Starting Dockerfile analysis")
        
        try:
            # Find and analyze Dockerfile
            dockerfile_path = self.repo_path / self.dockerfile_path
            if dockerfile_path.exists():
                logger.info(f"Analyzing Dockerfile: {dockerfile_path}")
                self.dockerfile_results = self._analyze_dockerfile(dockerfile_path)
            else:
                logger.warning(f"Dockerfile not found at {dockerfile_path}")
                self.dockerfile_results = {"error": "Dockerfile not found"}
            
            # Find and analyze ENTRYPOINT scripts if enabled
            if self.entrypoint_analysis and self.dockerfile_results.get("entrypoint_scripts"):
                self._analyze_entrypoint_scripts()
            
            # Create FAISS index and metadata
            if self.vectors:
                self._create_indices()
            
            # Save analysis results
            self._save_analysis_results()
            
            logger.info("Dockerfile analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Error during Dockerfile analysis: {e}")
            raise
        
        return {
            "dockerfile_results": self.dockerfile_results,
            "entrypoint_results": self.entrypoint_results,
            "vectors_created": len(self.vectors),
            "metadata_entries": len(self.metadata)
        }
    
    def _analyze_dockerfile(self, dockerfile_path: Path) -> Dict[str, Any]:
        """
        Analyze a single Dockerfile.
        
        Args:
            dockerfile_path: Path to the Dockerfile
            
        Returns:
            Dictionary containing Dockerfile analysis results
        """
        try:
            # Use the Dockerfile inspector
            inspection_results = start_inspection(str(dockerfile_path), str(self.repo_path))
            
            # Create embedding for the Dockerfile summary
            if "file_summary" in inspection_results:
                summary_vec = local_embedder.embed_one(inspection_results["file_summary"])
                self.vectors.append(summary_vec)
                
                # Add metadata
                metadata_entry = {
                    "file_path": str(dockerfile_path.relative_to(self.repo_path)),
                    "file_type": "dockerfile",
                    "vector_id": len(self.vectors) - 1,
                    "summary": inspection_results["file_summary"],
                    "inspection_results": inspection_results,
                    "transport_security": inspection_results.get("transport_security", False),
                    "control_implementations": inspection_results.get("control_implementations", {}),
                    "parsed_instructions": inspection_results.get("parsed_instructions", {}),
                    "dockerfile_analysis": inspection_results.get("dockerfile_analysis", {})
                }
                self.metadata.append(metadata_entry)
                
                logger.info(f"Dockerfile analysis completed: {len(inspection_results.get('control_implementations', {}))} controls found")
            
            return inspection_results
            
        except Exception as e:
            logger.error(f"Error analyzing Dockerfile {dockerfile_path}: {e}")
            return {"error": str(e)}
    
    def _analyze_entrypoint_scripts(self):
        """Analyze ENTRYPOINT scripts identified in the Dockerfile."""
        entrypoint_scripts = self.dockerfile_results.get("dockerfile_analysis", {}).get("entrypoint_scripts", [])
        
        for script_name in entrypoint_scripts:
            # Look for the script in the repository
            script_path = self._find_script_path(script_name)
            
            if script_path and script_path.exists():
                logger.info(f"Analyzing ENTRYPOINT script: {script_path}")
                script_results = self._analyze_script(script_path)
                self.entrypoint_results[script_name] = script_results
                
                # Create embedding for the script
                if "summary" in script_results:
                    script_vec = local_embedder.embed_one(script_results["summary"])
                    self.vectors.append(script_vec)
                    
                    # Add metadata
                    metadata_entry = {
                        "file_path": str(script_path.relative_to(self.repo_path)),
                        "file_type": "entrypoint_script",
                        "vector_id": len(self.vectors) - 1,
                        "summary": script_results["summary"],
                        "inspection_results": script_results,
                        "related_dockerfile": self.dockerfile_path,
                        "script_language": self._detect_script_language(script_path)
                    }
                    self.metadata.append(metadata_entry)
            else:
                logger.warning(f"ENTRYPOINT script not found: {script_name}")
                self.entrypoint_results[script_name] = {"error": "Script not found"}
    
    def _find_script_path(self, script_name: str) -> Optional[Path]:
        """
        Find the full path to an ENTRYPOINT script.
        
        Args:
            script_name: Name of the script to find
            
        Returns:
            Full path to the script if found, None otherwise
        """
        # Check if it's an absolute path in the repository
        if script_name.startswith('/'):
            # Remove leading slash and check relative to repo root
            relative_path = script_name[1:]
            script_path = self.repo_path / relative_path
            if script_path.exists():
                return script_path
        
        # Check if it's a relative path
        script_path = self.repo_path / script_name
        if script_path.exists():
            return script_path
        
        # Search for the script in common locations
        common_paths = [
            self.repo_path / "scripts",
            self.repo_path / "bin",
            self.repo_path / "tools",
            self.repo_path / "docker",
            self.repo_path / "scripts" / script_name,
            self.repo_path / "bin" / script_name,
            self.repo_path / "tools" / script_name,
            self.repo_path / "docker" / script_name
        ]
        
        for path in common_paths:
            if path.exists():
                return path
        
        return None
    
    def _analyze_script(self, script_path: Path) -> Dict[str, Any]:
        """
        Analyze an ENTRYPOINT script.
        
        Args:
            script_path: Path to the script
            
        Returns:
            Dictionary containing script analysis results
        """
        try:
            # Read script content
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic script analysis
            script_results = {
                "file_path": str(script_path.relative_to(self.repo_path)),
                "file_size": len(content),
                "line_count": len(content.splitlines()),
                "language": self._detect_script_language(script_path),
                "summary": self._generate_script_summary(script_path, content),
                "content_preview": content[:500] + "..." if len(content) > 500 else content
            }
            
            # Add language-specific analysis if available
            if script_results["language"] == "python":
                script_results.update(self._analyze_python_script(content))
            elif script_results["language"] == "bash" or script_results["language"] == "shell":
                script_results.update(self._analyze_shell_script(content))
            
            return script_results
            
        except Exception as e:
            logger.error(f"Error analyzing script {script_path}: {e}")
            return {"error": str(e)}
    
    def _detect_script_language(self, script_path: Path) -> str:
        """
        Detect the language of a script based on file extension and shebang.
        
        Args:
            script_path: Path to the script
            
        Returns:
            Detected language string
        """
        # Check file extension
        suffix = script_path.suffix.lower()
        if suffix == '.py':
            return 'python'
        elif suffix in ['.sh', '.bash']:
            return 'bash'
        elif suffix == '.js':
            return 'javascript'
        elif suffix == '.rb':
            return 'ruby'
        elif suffix == '.pl':
            return 'perl'
        
        # Check shebang line
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#!'):
                    shebang = first_line[2:].lower()
                    if 'python' in shebang:
                        return 'python'
                    elif 'bash' in shebang or 'sh' in shebang:
                        return 'bash'
                    elif 'node' in shebang:
                        return 'javascript'
                    elif 'ruby' in shebang:
                        return 'ruby'
                    elif 'perl' in shebang:
                        return 'perl'
        except Exception:
            pass
        
        return 'unknown'
    
    def _generate_script_summary(self, script_path: Path, content: str) -> str:
        """
        Generate a summary of the script content.
        
        Args:
            script_path: Path to the script
            content: Script content
            
        Returns:
            Summary string
        """
        language = self._detect_script_language(script_path)
        line_count = len(content.splitlines())
        size_kb = len(content) / 1024
        
        summary_parts = [
            f"{language.title()} script with {line_count} lines ({size_kb:.1f} KB)",
            f"Path: {script_path.relative_to(self.repo_path)}"
        ]
        
        # Add language-specific details
        if language == 'python':
            import_count = content.count('import ') + content.count('from ')
            summary_parts.append(f"Contains {import_count} import statements")
        elif language in ['bash', 'shell']:
            # Count common shell commands
            shell_commands = ['echo', 'if', 'for', 'while', 'case', 'function']
            command_count = sum(content.count(cmd) for cmd in shell_commands)
            summary_parts.append(f"Contains {command_count} shell control structures")
        
        return ". ".join(summary_parts)
    
    def _analyze_python_script(self, content: str) -> Dict[str, Any]:
        """Analyze Python script content for security features."""
        analysis = {
            "imports": [],
            "security_features": [],
            "file_operations": [],
            "network_operations": []
        }
        
        lines = content.splitlines()
        for line in lines:
            line = line.strip()
            
            # Extract imports
            if line.startswith(('import ', 'from ')):
                analysis["imports"].append(line)
            
            # Check for security features
            if any(keyword in line.lower() for keyword in ['ssl', 'tls', 'cert', 'key', 'auth']):
                analysis["security_features"].append(line)
            
            # Check for file operations
            if any(keyword in line.lower() for keyword in ['open(', 'read(', 'write(', 'file(']):
                analysis["file_operations"].append(line)
            
            # Check for network operations
            if any(keyword in line.lower() for keyword in ['socket', 'http', 'https', 'urlopen', 'requests']):
                analysis["network_operations"].append(line)
        
        return analysis
    
    def _analyze_shell_script(self, content: str) -> Dict[str, Any]:
        """Analyze shell script content for security features."""
        analysis = {
            "commands": [],
            "security_features": [],
            "file_operations": [],
            "network_operations": []
        }
        
        lines = content.splitlines()
        for line in lines:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Extract commands
            if line.startswith(('curl', 'wget', 'ssh', 'scp', 'rsync')):
                analysis["network_operations"].append(line)
            elif line.startswith(('chmod', 'chown', 'chgrp')):
                analysis["security_features"].append(line)
            elif line.startswith(('cat', 'echo', 'touch', 'rm', 'cp', 'mv')):
                analysis["file_operations"].append(line)
            else:
                analysis["commands"].append(line)
        
        return analysis
    
    def _create_indices(self):
        """Create FAISS indices and save metadata."""
        if not self.vectors:
            logger.warning("No vectors to index")
            return
        
        try:
            # Create FAISS index
            all_vectors = np.vstack(self.vectors)
            dockerfile_index = faiss_index.build_faiss_index(all_vectors)
            
            # Save index
            index_path = self.output_dir / "dockerfile_index.faiss"
            faiss_index.save_index(dockerfile_index, index_path)
            logger.info(f"Saved Dockerfile FAISS index to {index_path}")
            
            # Save metadata
            metadata_path = self.output_dir / "dockerfile_meta.json"
            meta_store.save_metadata(self.metadata, metadata_path)
            logger.info(f"Saved Dockerfile metadata to {metadata_path}")
            
        except Exception as e:
            logger.error(f"Error creating Dockerfile indices: {e}")
            raise
    
    def _save_analysis_results(self):
        """Save comprehensive analysis results."""
        try:
            # Save detailed analysis results
            analysis_results = {
                "dockerfile_results": self.dockerfile_results,
                "entrypoint_results": self.entrypoint_results,
                "analysis_summary": {
                    "total_files_analyzed": len(self.metadata),
                    "dockerfile_controls_found": len(self.dockerfile_results.get("control_implementations", {})),
                    "entrypoint_scripts_analyzed": len(self.entrypoint_results),
                    "transport_security_configured": self.dockerfile_results.get("transport_security", False)
                },
                "metadata": self.metadata
            }
            
            results_path = self.output_dir / "dockerfile_analysis.json"
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved Dockerfile analysis results to {results_path}")
            
        except Exception as e:
            logger.error(f"Error saving analysis results: {e}")
            raise

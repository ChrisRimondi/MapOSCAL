"""
Cache manager for MapOSCAL execution artifacts.

This module provides functionality to manage content-addressed artifact caching
with application-specific organization for Argo CD Application analysis.
"""

import os
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class CacheManager:
    """Manages application-specific artifact caching for MapOSCAL execution."""
    
    def __init__(self, application_name: str, base_cache_dir: str = ".maposcal"):
        """Initialize cache manager for a specific application.
        
        Args:
            application_name: Name of the Argo CD Application
            base_cache_dir: Base directory for all MapOSCAL caches
        """
        self.application_name = application_name
        self.base_cache_dir = Path(base_cache_dir)
        
        # Application-specific cache paths
        if application_name:
            self.app_cache_dir = self.base_cache_dir / "artifacts" / "applications" / application_name
            self.app_state_dir = self.base_cache_dir / "applications" / application_name
        else:
            self.app_cache_dir = self.base_cache_dir / "artifacts" / "default"
            self.app_state_dir = self.base_cache_dir / "applications" / "default"
        
        # Ensure cache directories exist
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure all necessary cache directories exist."""
        directories = [
            self.app_cache_dir / "image",
            self.app_cache_dir / "repo",
            self.app_cache_dir / "workload",
            self.app_state_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_image_cache_path(self, image_digest: str) -> Path:
        """Get cache path for image-specific artifacts.
        
        Args:
            image_digest: Image digest (sha256:...)
            
        Returns:
            Path to image cache directory
        """
        return self.app_cache_dir / "image" / image_digest
    
    def get_repo_cache_path(self, repo_url: str, commit_sha: str) -> Path:
        """Get cache path for repository-specific artifacts.
        
        Args:
            repo_url: Normalized repository URL
            commit_sha: Git commit SHA
            
        Returns:
            Path to repository cache directory
        """
        # Normalize repo URL for filesystem safety
        safe_repo_name = self._normalize_repo_name(repo_url)
        return self.app_cache_dir / "repo" / f"{safe_repo_name}@{commit_sha}"
    
    def get_workload_cache_path(self, workload_name: str, namespace: str) -> Path:
        """Get cache path for workload-specific artifacts.
        
        Args:
            workload_name: Name of the workload
            namespace: Kubernetes namespace
            
        Returns:
            Path to workload cache directory
        """
        safe_workload_name = self._normalize_name(workload_name)
        safe_namespace = self._normalize_name(namespace)
        return self.app_cache_dir / "workload" / f"{safe_namespace}-{safe_workload_name}"
    
    def _normalize_repo_name(self, repo_url: str) -> str:
        """Normalize repository URL for filesystem safety.
        
        Args:
            repo_url: Repository URL
            
        Returns:
            Filesystem-safe repository name
        """
        # Remove protocol and normalize separators
        repo_name = repo_url.replace("https://", "").replace("http://", "")
        repo_name = repo_name.replace("git@", "").replace(":", "/")
        repo_name = repo_name.replace("/", "_").replace(".", "_")
        return repo_name
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name for filesystem safety.
        
        Args:
            name: Name to normalize
            
        Returns:
            Filesystem-safe name
        """
        return name.replace("/", "_").replace("\\", "_").replace(":", "_")
    
    def compute_input_hash(self, inputs: Dict[str, Any]) -> str:
        """Compute hash of inputs for change detection.
        
        Args:
            inputs: Dictionary of input values
            
        Returns:
            SHA256 hash of inputs
        """
        # Sort keys for deterministic hashing
        sorted_inputs = json.dumps(inputs, sort_keys=True, default=str)
        return hashlib.sha256(sorted_inputs.encode()).hexdigest()
    
    def get_artifact_path(self, artifact_type: str, artifact_name: str, 
                          inputs: Optional[Dict[str, Any]] = None) -> Path:
        """Get path for a specific artifact.
        
        Args:
            artifact_type: Type of artifact (image, repo, workload)
            artifact_name: Name/identifier for the artifact
            inputs: Optional inputs for hash-based naming
            
        Returns:
            Path to the artifact
        """
        if inputs:
            input_hash = self.compute_input_hash(inputs)
            return self.app_cache_dir / artifact_type / f"{artifact_name}_{input_hash}"
        else:
            return self.app_cache_dir / artifact_type / artifact_name
    
    def artifact_exists(self, artifact_path: Path) -> bool:
        """Check if an artifact exists and is valid.
        
        Args:
            artifact_path: Path to the artifact
            
        Returns:
            True if artifact exists and is valid
        """
        return artifact_path.exists() and artifact_path.is_file()
    
    def save_artifact(self, artifact_path: Path, data: Any, 
                      metadata: Optional[Dict[str, Any]] = None) -> None:
        """Save an artifact to cache.
        
        Args:
            artifact_path: Path where to save the artifact
            data: Data to save
            metadata: Optional metadata about the artifact
        """
        # Ensure parent directory exists
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the main artifact
        if isinstance(data, (dict, list)):
            with open(artifact_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        else:
            with open(artifact_path, 'w') as f:
                f.write(str(data))
        
        # Save metadata if provided
        if metadata:
            metadata_path = artifact_path.with_suffix('.metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
    
    def load_artifact(self, artifact_path: Path) -> Any:
        """Load an artifact from cache.
        
        Args:
            artifact_path: Path to the artifact
            
        Returns:
            Loaded artifact data
        """
        if not self.artifact_exists(artifact_path):
            raise FileNotFoundError(f"Artifact not found: {artifact_path}")
        
        # Try to load as JSON first
        try:
            with open(artifact_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to text
            with open(artifact_path, 'r') as f:
                return f.read()
    
    def get_artifact_metadata(self, artifact_path: Path) -> Optional[Dict[str, Any]]:
        """Get metadata for an artifact.
        
        Args:
            artifact_path: Path to the artifact
            
        Returns:
            Metadata dictionary or None if not found
        """
        metadata_path = artifact_path.with_suffix('.metadata.json')
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                return json.load(f)
        return None
    
    def should_skip_step(self, step_id: str, inputs: Dict[str, Any], 
                        force: bool = False) -> bool:
        """Determine if a step should be skipped based on cache.
        
        Args:
            step_id: ID of the step to check
            inputs: Input values for the step
            force: Whether to force execution regardless of cache
            
        Returns:
            True if step should be skipped
        """
        if force:
            return False
        
        # Check if we have a cached result for these inputs
        input_hash = self.compute_input_hash(inputs)
        cache_key = f"{step_id}_{input_hash}"
        artifact_path = self.app_cache_dir / "workload" / cache_key
        
        return self.artifact_exists(artifact_path)
    
    def cleanup_old_artifacts(self, max_age_days: int = 30) -> int:
        """Clean up old artifacts to manage disk space.
        
        Args:
            max_age_days: Maximum age of artifacts in days
            
        Returns:
            Number of artifacts cleaned up
        """
        cleaned_count = 0
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        
        for root, dirs, files in os.walk(self.app_cache_dir):
            for file in files:
                file_path = Path(root) / file
                if file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        cleaned_count += 1
                    except OSError:
                        # Skip files that can't be deleted
                        continue
        
        return cleaned_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the cache.
        
        Returns:
            Dictionary with cache statistics
        """
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(self.app_cache_dir):
            for file in files:
                file_path = Path(root) / file
                try:
                    total_size += file_path.stat().st_size
                    file_count += 1
                except OSError:
                    continue
        
        return {
            "application": self.application_name,
            "cache_directory": str(self.app_cache_dir),
            "total_files": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }

"""
Tests for Dockerfile analysis functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from maposcal.inspectors.inspect_dockerfile import start_inspection
from maposcal.utils.dockerfile_control_hints import (
    is_transport_security_configured,
    get_control_mappings_for_instruction,
    TRANSPORT_SECURITY_INDICATORS
)


class TestDockerfileInspector:
    """Test the Dockerfile inspector functionality."""
    
    def test_parse_dockerfile_instructions(self):
        """Test parsing of Dockerfile instructions."""
        dockerfile_content = """
        FROM python:3.9-slim
        
        USER appuser:appgroup
        WORKDIR /home/app
        
        ENV APP_DEBUG=false
        ENV TLS_MIN_VERSION=1.2
        
        EXPOSE 8080 443
        
        COPY requirements.txt /app/
        RUN pip install -r requirements.txt
        
        COPY . /app/
        
        ENTRYPOINT ["./entrypoint.sh"]
        CMD ["python", "app.py"]
        
        HEALTHCHECK CMD curl -f http://localhost/health
        """
        
        # Create temporary Dockerfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dockerfile', delete=False) as f:
            f.write(dockerfile_content)
            temp_path = f.name
        
        try:
            results = start_inspection(temp_path)
            
            # Check basic structure
            assert "file_summary" in results
            assert "control_hints" in results
            assert "parsed_instructions" in results
            assert "control_implementations" in results
            
            # Check parsed instructions
            instructions = results["parsed_instructions"]
            assert "USER" in instructions
            assert "EXPOSE" in instructions
            assert "ENV" in instructions
            assert "COPY" in instructions
            assert "RUN" in instructions
            assert "ENTRYPOINT" in instructions
            assert "HEALTHCHECK" in instructions
            
            # Check USER instruction parsing
            user_instructions = instructions["USER"]
            assert len(user_instructions) == 1
            assert user_instructions[0]["username"] == "appuser"
            assert user_instructions[0]["group"] == "appgroup"
            
            # Check EXPOSE instruction parsing
            expose_instructions = instructions["EXPOSE"]
            assert len(expose_instructions) == 1
            assert 8080 in expose_instructions[0]["ports"]
            assert 443 in expose_instructions[0]["ports"]
            
            # Check ENV instruction parsing
            env_instructions = instructions["ENV"]
            assert len(env_instructions) == 2  # Two ENV instructions
            # Check first ENV instruction
            assert "APP_DEBUG" in env_instructions[0]["env_variables"]
            # Check second ENV instruction
            assert "TLS_MIN_VERSION" in env_instructions[1]["env_variables"]
            
        finally:
            os.unlink(temp_path)
    
    def test_transport_security_detection(self):
        """Test transport security detection in Dockerfiles."""
        # Test with TLS configuration
        tls_dockerfile = """
        FROM nginx:alpine
        EXPOSE 443 8443
        ENV TLS_MIN_VERSION=1.2
        COPY server.crt /etc/ssl/certs/
        COPY server.key /etc/ssl/private/
        RUN chmod 600 /etc/ssl/private/server.key
        """
        assert is_transport_security_configured(tls_dockerfile) is True
        
        # Test without TLS configuration
        no_tls_dockerfile = """
        FROM python:3.9-slim
        USER appuser
        WORKDIR /app
        EXPOSE 8080
        CMD ["python", "app.py"]
        """
        assert is_transport_security_configured(no_tls_dockerfile) is False
    
    def test_control_mappings(self):
        """Test control mappings for Dockerfile instructions."""
        # Test USER instruction mapping
        user_mappings = get_control_mappings_for_instruction("USER", "appuser")
        assert len(user_mappings) > 0
        assert any("AC-6" in mapping["controls"] for mapping in user_mappings)
        
        # Test EXPOSE instruction mapping
        expose_mappings = get_control_mappings_for_instruction("EXPOSE", "443 8080")
        assert len(expose_mappings) > 0
        assert any("CM-7" in mapping["controls"] for mapping in expose_mappings)
        
        # Test ENV instruction mapping
        env_mappings = get_control_mappings_for_instruction("ENV", "TLS_MIN_VERSION=1.2")
        assert len(env_mappings) > 0
        assert any("SC-13" in mapping["controls"] for mapping in env_mappings)
    
    def test_entrypoint_script_detection(self):
        """Test detection of ENTRYPOINT scripts."""
        dockerfile_content = """
        FROM python:3.9-slim
        
        COPY entrypoint.sh /app/
        RUN chmod +x /app/entrypoint.sh
        
        ENTRYPOINT ["/app/entrypoint.sh"]
        CMD ["python", "app.py"]
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dockerfile', delete=False) as f:
            f.write(dockerfile_content)
            temp_path = f.name
        
        try:
            results = start_inspection(temp_path)
            
            # Check that entrypoint scripts are detected
            dockerfile_analysis = results.get("dockerfile_analysis", {})
            entrypoint_scripts = dockerfile_analysis.get("entrypoint_scripts", [])
            
            assert "/app/entrypoint.sh" in entrypoint_scripts
            
        finally:
            os.unlink(temp_path)
    
    def test_complex_dockerfile_analysis(self):
        """Test analysis of a complex Dockerfile with multiple security features."""
        complex_dockerfile = """
        FROM python:3.9-slim
        
        # Create non-root user
        RUN groupadd -r appuser && useradd -r -g appuser appuser
        
        # Set working directory
        WORKDIR /home/app
        
        # Install security updates and CA certificates
        RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
        
        # Copy requirements and install dependencies
        COPY requirements.txt /app/
        RUN pip install --no-cache-dir -r requirements.txt
        
        # Copy application code
        COPY . /app/
        
        # Set proper permissions
        RUN chown -R appuser:appuser /app && chmod 750 /app
        
        # Switch to non-root user
        USER appuser:appuser
        
        # Expose ports
        EXPOSE 8080 443
        
        # Set environment variables
        ENV PYTHONUNBUFFERED=1
        ENV TLS_MIN_VERSION=1.2
        ENV APP_DEBUG=false
        
        # Health check
        HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
          CMD curl -f http://localhost:8080/health || exit 1
        
        # Entrypoint script
        ENTRYPOINT ["./entrypoint.sh"]
        CMD ["python", "app.py"]
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dockerfile', delete=False) as f:
            f.write(complex_dockerfile)
            temp_path = f.name
        
        try:
            results = start_inspection(temp_path)
            
            # Check control implementations
            control_implementations = results.get("control_implementations", {})
            
            # Should have multiple controls implemented
            assert len(control_implementations) > 3
            
            # Check for specific controls
            assert "AC-6" in control_implementations  # User management
            assert "CM-7" in control_implementations  # Port exposure
            assert "SC-13" in control_implementations  # TLS configuration
            
            # Check transport security
            assert results.get("transport_security") is True
            
            # Check parsed instructions
            instructions = results.get("parsed_instructions", {})
            assert len(instructions["USER"]) > 0
            assert len(instructions["EXPOSE"]) > 0
            assert len(instructions["ENV"]) > 0
            assert len(instructions["RUN"]) > 0
            assert len(instructions["HEALTHCHECK"]) > 0
            
        finally:
            os.unlink(temp_path)


class TestDockerfileControlHints:
    """Test the Dockerfile control hints functionality."""
    
    def test_transport_security_indicators(self):
        """Test transport security indicator constants."""
        # Check TLS ports
        assert 443 in TRANSPORT_SECURITY_INDICATORS["tls_ports"]
        assert 8443 in TRANSPORT_SECURITY_INDICATORS["tls_ports"]
        
        # Check TLS environment variables
        assert "TLS_MIN_VERSION" in TRANSPORT_SECURITY_INDICATORS["tls_environment_vars"]
        assert "SSL_CERT_FILE" in TRANSPORT_SECURITY_INDICATORS["tls_environment_vars"]
        
        # Check TLS config files
        assert "nginx.conf" in TRANSPORT_SECURITY_INDICATORS["tls_config_files"]
        assert "ssl.conf" in TRANSPORT_SECURITY_INDICATORS["tls_config_files"]
        
        # Check certificate extensions
        assert ".crt" in TRANSPORT_SECURITY_INDICATORS["tls_certificate_extensions"]
        assert ".pem" in TRANSPORT_SECURITY_INDICATORS["tls_certificate_extensions"]
        assert ".key" in TRANSPORT_SECURITY_INDICATORS["tls_key_extensions"]
    
    def test_pattern_matching(self):
        """Test pattern matching for different instruction types."""
        from maposcal.utils.dockerfile_control_hints import _pattern_matches
        
        # Test USER instruction patterns
        assert _pattern_matches("non_root_user", "USER", "appuser") is True
        assert _pattern_matches("non_root_user", "USER", "0") is False
        assert _pattern_matches("numeric_uid_gid", "USER", "10001:10001") is True
        
        # Test EXPOSE instruction patterns
        assert _pattern_matches("exposed_ports", "EXPOSE", "8080") is True
        assert _pattern_matches("tls_ports", "EXPOSE", "443 8080") is True
        assert _pattern_matches("tls_ports", "EXPOSE", "8080") is False
        
        # Test ENV instruction patterns
        assert _pattern_matches("security_flags", "ENV", "APP_DEBUG=false") is True
        assert _pattern_matches("tls_configuration", "ENV", "TLS_MIN_VERSION=1.2") is True


if __name__ == "__main__":
    pytest.main([__file__])

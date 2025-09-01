# Changelog

All notable changes to MapOSCAL will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-09-02

### 🚀 Major Features

#### Kubernetes Support & Analysis
- **NEW**: Comprehensive Kubernetes manifest analysis and control mapping
- **K8s Control Mapping**: Automatic NIST 800-53 control identification from Kubernetes resources
- **Resource Analysis**: Analyzes Deployments, Services, ConfigMaps, Secrets, RBAC, and more
- **Security Context**: Maps Kubernetes security features to compliance controls
- **Network Policies**: Automatic detection and analysis of network security policies
- **RBAC Analysis**: Role-based access control analysis and compliance mapping
- **Pod Security**: Pod security standards and security context analysis
- **Separate Processing**: Dedicated Kubernetes analysis workflow with `k8s-process` command

#### Compliance-Trestle Integration
- **NEW**: Full integration with compliance-trestle for standards-compliant OSCAL generation
- **Standards Compliance**: 100% OSCAL 1.1.3 compliance across all commands
- **Type Safety**: Strong typing and validation for all OSCAL elements
- **Schema Validation**: Automatic OSCAL structure validation using compliance-trestle models
- **Future-Proof**: Automatic support for OSCAL standard updates
- **Developer Experience**: IDE autocomplete and compile-time validation
- **Production Ready**: Enterprise-grade OSCAL generation with full validation

### ✨ Enhancements

#### Kubernetes Analysis Features
- **Comprehensive Coverage**: Analyzes 15+ Kubernetes resource types
- **Security Mapping**: Maps K8s security features to NIST 800-53 controls
- **Evidence Generation**: Resource-specific evidence for each security control
- **OSCAL Integration**: Generates structured component definitions for K8s workloads
- **Control Families**: Covers AC, CM, SC, CP, SI, IA families with detailed mappings

#### Compliance-Trestle Features
- **Proper OSCAL Serialization**: Correct JSON wrapping with `{"component-definition": {...}}`
- **Validation on Creation**: Pydantic models validate during object creation
- **Namespace Handling**: Automatic URN to HTTPS URL conversion for compliance
- **Value Cleaning**: Robust property value normalization and validation
- **Error Handling**: Comprehensive error recovery and validation feedback

#### Enhanced Analysis Workflow
- **Dual Commands**: `generate` for code analysis, `k8s-process` for Kubernetes analysis
- **Integrated Results**: Kubernetes and code evidence combined for comprehensive control mapping
- **Performance Optimization**: Independent processing for different resource types
- **Metadata Management**: Comprehensive tracking of Kubernetes security features

### 🐛 Bug Fixes
- Fixed compliance-trestle namespace validation errors
- Resolved property value validation issues with whitespace handling
- Fixed CLI command flow for compliance-trestle integration
- Improved error handling in Kubernetes manifest parsing

### 🔧 Technical Improvements
- **Compliance-Trestle Integration**: Complete Python API integration for OSCAL generation
- **Kubernetes Parser**: Robust parsing of all Kubernetes resource types
- **Multi-format Support**: Proper handling of YAML and JSON Kubernetes manifests
- **Pattern Matching**: Intelligent security pattern recognition in K8s configurations
- **FAISS Integration**: Seamless integration with existing vector search infrastructure

### 📚 Documentation
- **Comprehensive Integration Guide**: Complete compliance-trestle integration documentation
- **Kubernetes Analysis Guide**: Detailed K8s manifest analysis documentation
- **Configuration Examples**: Sample Kubernetes manifests and analysis examples
- **Control Mapping Reference**: Detailed NIST 800-53 control mappings for K8s
- **Usage Examples**: Practical examples of Kubernetes security analysis
- **Architecture Documentation**: Detailed system design and integration details

### 🔄 Migration Notes
- **No Breaking Changes**: All existing functionality remains intact
- **New Commands**: `k8s-process` command available for Kubernetes analysis
- **Enhanced OSCAL**: All commands now generate standards-compliant OSCAL
- **Automatic Benefits**: Compliance-trestle integration works automatically
- **Performance**: Minimal impact on existing analysis workflows
- **Backward Compatibility**: All existing CLI commands and configurations continue to work

---

## [0.4.0-alpha] - 2025-08-15

### 🚀 Major Features

#### Dockerfile Analysis & Container Security
- **NEW**: Comprehensive Dockerfile security analysis and control mapping
- **Container Controls**: Automatic NIST 800-53 control identification from Dockerfile instructions
- **Separate FAISS Index**: Dedicated `dockerfile_index.faiss` for container security analysis
- **ENTRYPOINT Script Analysis**: Automatic analysis of container entrypoint scripts
- **Transport Security Detection**: Automatic TLS/HTTPS configuration identification
- **Security Pattern Recognition**: Intelligent detection of security-relevant Dockerfile patterns

#### GPT-5 Model Family Support
- **NEW**: Full compatibility with OpenAI's GPT-5 family of models
- **Automatic Parameter Detection**: Smart handling of `max_tokens` vs `max_completion_tokens`
- **Temperature Restrictions**: Automatic handling of GPT-5 temperature parameter limitations
- **Backward Compatibility**: All existing models (GPT-4, GPT-3.5) continue to work unchanged
- **Future-Proof**: Easy to add support for new model restrictions

### ✨ Enhancements

#### Dockerfile Control Mapping
- **Comprehensive Coverage**: Maps 20+ Dockerfile instruction types to NIST controls
- **Evidence Generation**: Line-specific evidence for each security control implementation
- **OSCAL Integration**: Structured properties for automated compliance reporting
- **Control Families**: Covers AC, CM, SC, CP, SI, IA families with detailed mappings

#### Container Security Features
- **User Management**: Non-root user detection and analysis (AC-6, CM-6)
- **Network Security**: Port exposure analysis and TLS port identification (CM-7, SC-7, SC-8)
- **File Security**: Permission and ownership analysis (CM-6, AC-6)
- **Process Control**: Signal handling and health monitoring (CP-10, SI-4)
- **Data Protection**: Volume declarations and credential file detection (CP-9, SC-28)

#### Enhanced Analysis Workflow
- **Separate Processing**: Dockerfiles excluded from regular repository analysis
- **Integrated Results**: Container evidence combined with code evidence for comprehensive control mapping
- **Performance Optimization**: Independent FAISS indexing for efficient container queries
- **Metadata Management**: Comprehensive tracking of container security features

### 🐛 Bug Fixes
- Fixed Analyzer.config attribute error for Dockerfile analysis initialization
- Resolved GPT-5 model parameter compatibility issues
- Fixed temperature parameter restrictions for new OpenAI models
- Improved error handling in Dockerfile instruction parsing

### 🔧 Technical Improvements
- **Dockerfile Parser**: Robust parsing of all Dockerfile instruction types
- **Multi-line Support**: Proper handling of complex multi-line instructions (HEALTHCHECK, etc.)
- **Language Detection**: Automatic script language identification for entrypoint scripts
- **Pattern Matching**: Intelligent security pattern recognition in container configurations
- **FAISS Integration**: Seamless integration with existing vector search infrastructure

### 📚 Documentation
- **Comprehensive Implementation Guide**: Complete Dockerfile analysis documentation
- **Configuration Examples**: Sample Dockerfile and entrypoint script examples
- **Control Mapping Reference**: Detailed NIST 800-53 control mappings
- **Usage Examples**: Practical examples of container security analysis
- **Architecture Documentation**: Detailed system design and integration details

### 🔄 Migration Notes
- **No Breaking Changes**: All existing functionality remains intact
- **Configuration Updates**: New Dockerfile configuration options available
- **Automatic Benefits**: Container security analysis works automatically when Dockerfiles are present
- **Performance**: Minimal impact on existing analysis workflows
- **Backward Compatibility**: All existing CLI commands and configurations continue to work

---

## [0.3.0-alpha] - 2025-01-16

### 🚀 Major Features

#### Selective Security Summary Context
- **NEW**: Intelligent security context filtering for control mapping
- **Token Reduction**: Achieves ~47% reduction in prompt tokens while maintaining quality
- **Smart Mapping**: Different control families get relevant security sections only:
  - `AC` (Access Control) → Service Overview + Authentication & Authorization
  - `AU` (Audit & Accountability) → Service Overview + Audit Logging & Monitoring  
  - `SC` (System & Communications Protection) → Service Overview + Encryption & Data Protection
  - `CM` (Configuration Management) → Service Overview + Authentication & Authorization
  - And more intelligent mappings for all NIST 800-53 families
- **Backward Compatible**: Gracefully falls back to full security overview if parsing fails

### ✨ Enhancements

#### Cryptographic Operations Detection
- **Enhanced Security Analysis**: Automatic detection of cryptographic operations in source code
- **Language Support**: Added cryptographic pattern detection for Python and Go
- **Control Integration**: Cryptographic summaries automatically included in relevant control mappings
- **Compliance Context**: Better mapping accuracy for encryption-related controls (SC family)

#### Control Mapping Improvements
- **Better Context**: LLM receives more focused, relevant security information
- **Improved Accuracy**: Reduced noise in prompts leads to better control status determination
- **Cost Efficiency**: Significant reduction in API token usage
- **Performance**: Faster processing due to smaller prompt sizes

#### Language Inspector Enhancements
- **Python Inspector**: Enhanced module identification and cryptographic detection
- **Go Inspector**: Added cryptographic operations detection
- **Error Handling**: Improved robustness in module identification
- **Configuration Settings**: Better handling of configuration detection

### 🐛 Bug Fixes
- Fixed UnboundLocalError in Python inspector for configuration_settings access
- Improved error handling in module identification processes
- Enhanced validation for control evaluation with configuration requirements

### 🔧 Technical Improvements
- **Security Section Mapper**: New comprehensive mapping system for control families
- **Prompt Template Updates**: All prompt functions now support selective security sections
- **Validation Enhancements**: Better structure validation for security overviews
- **Logging Improvements**: More detailed logging for debugging and monitoring

### 📚 Documentation
- Enhanced CLI functionality documentation
- Improved error messages and user guidance
- Better code organization and modularity

### 🔄 Migration Notes
- **No Breaking Changes**: All existing functionality remains intact
- **Automatic Benefits**: Selective security summaries work automatically
- **Configuration**: No configuration changes required
- **Performance**: Immediate improvements in token usage and processing speed

---

## [0.2.0-alpha] - 2024-12-xx

### Features
- Security overview generation and integration
- Enhanced control mapping with service context
- Comprehensive validation and evaluation capabilities
- Quality assurance and reporting features

### Technical Improvements
- Template-based OSCAL generation
- Improved error handling and validation
- Enhanced metadata tracking
- Better logging and debugging capabilities

---

## [0.1.0] - 2024-11-xx

### Initial Release
- Core MapOSCAL functionality
- Basic control mapping capabilities
- OSCAL component definition generation
- Repository analysis and semantic search
- Initial CLI interface

---

## Release Comparison

| Feature | v0.1.0 | v0.2.0-alpha | v0.3.0-alpha | v0.4.0-alpha | v0.5.0-alpha |
|---------|--------|--------------|--------------|---------------|---------------|
| Basic Control Mapping | ✅ | ✅ | ✅ | ✅ | ✅ |
| Security Overview | ❌ | ✅ | ✅ | ✅ | ✅ |
| Selective Context | ❌ | ❌ | ✅ | ✅ | ✅ |
| Crypto Detection | ❌ | ❌ | ✅ | ✅ | ✅ |
| Token Optimization | ❌ | ❌ | ✅ | ✅ | ✅ |
| Advanced Validation | ❌ | ✅ | ✅ | ✅ | ✅ |
| Dockerfile Analysis | ❌ | ❌ | ❌ | ✅ | ✅ |
| Container Security | ❌ | ❌ | ❌ | ✅ | ✅ |
| GPT-5 Model Support | ❌ | ❌ | ❌ | ✅ | ✅ |
| Container Control Mapping | ❌ | ❌ | ❌ | ✅ | ✅ |
| Kubernetes Analysis | ❌ | ❌ | ❌ | ❌ | ✅ |
| K8s Control Mapping | ❌ | ❌ | ❌ | ❌ | ✅ |
| Compliance-Trestle Integration | ❌ | ❌ | ❌ | ❌ | ✅ |
| Standards-Compliant OSCAL | ❌ | ❌ | ❌ | ❌ | ✅ |
| Enhanced Documentation | ❌ | ❌ | ❌ | ❌ | ✅ |
| Performance Optimizations | ❌ | ❌ | ❌ | ❌ | ✅ |

## Upgrade Path

### From v0.4.0-alpha to v0.5.0-alpha
1. **No Breaking Changes**: All existing functionality remains intact
2. **Kubernetes Support**: New `k8s-process` command for Kubernetes manifest analysis
3. **Compliance-Trestle Integration**: All commands now generate standards-compliant OSCAL
4. **Enhanced OSCAL**: Proper OSCAL 1.1.3 compliance with full validation
5. **Better Documentation**: Comprehensive guides for K8s and compliance-trestle integration
6. **Improved Error Handling**: More robust error recovery and validation feedback

### From v0.3.0-alpha to v0.5.0-alpha
1. All benefits from v0.4.0-alpha upgrade
2. Plus container security analysis capabilities
3. Plus GPT-5 model family support
4. Plus Kubernetes manifest analysis capabilities
5. Plus compliance-trestle integration for standards-compliant OSCAL

### From v0.2.0-alpha to v0.5.0-alpha
1. All benefits from v0.3.0-alpha upgrade
2. Plus container security analysis capabilities
3. Plus GPT-5 model family support
4. Plus Kubernetes manifest analysis capabilities
5. Plus compliance-trestle integration for standards-compliant OSCAL

### Performance Expectations
- **Token Usage**: ~47% reduction in security context tokens (v0.3.0-alpha feature)
- **Processing Speed**: Faster due to smaller prompts (v0.3.0-alpha feature)
- **API Costs**: Significant reduction in LLM API costs (v0.3.0-alpha feature)
- **Accuracy**: Improved control mapping quality through focused context (v0.3.0-alpha feature)
- **Container Analysis**: Independent processing with dedicated FAISS indices (v0.4.0-alpha feature)
- **GPT-5 Support**: Automatic parameter optimization for new models (v0.4.0-alpha feature)
- **Kubernetes Analysis**: Independent processing with dedicated K8s analysis workflow (v0.5.0-alpha feature)
- **OSCAL Compliance**: 100% standards-compliant OSCAL generation with full validation (v0.5.0-alpha feature)
- **Type Safety**: Strong typing and validation for all OSCAL elements (v0.5.0-alpha feature)

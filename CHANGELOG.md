# Changelog

All notable changes to MapOSCAL will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-08-15

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

| Feature | v0.1.0 | v0.2.0-alpha | v0.3.0-alpha | v0.4.0 |
|---------|--------|--------------|--------------|---------|
| Basic Control Mapping | ✅ | ✅ | ✅ | ✅ |
| Security Overview | ❌ | ✅ | ✅ | ✅ |
| Selective Context | ❌ | ❌ | ✅ | ✅ |
| Crypto Detection | ❌ | ❌ | ✅ | ✅ |
| Token Optimization | ❌ | ❌ | ✅ | ✅ |
| Advanced Validation | ❌ | ✅ | ✅ | ✅ |
| Dockerfile Analysis | ❌ | ❌ | ❌ | ✅ |
| Container Security | ❌ | ❌ | ❌ | ✅ |
| GPT-5 Model Support | ❌ | ❌ | ❌ | ✅ |
| Container Control Mapping | ❌ | ❌ | ❌ | ✅ |

## Upgrade Path

### From v0.3.0-alpha to v0.4.0
1. **No Breaking Changes**: All existing functionality remains intact
2. **Dockerfile Analysis**: Automatically enabled when Dockerfiles are present
3. **GPT-5 Models**: Immediate support for new OpenAI models
4. **Configuration**: Optional Dockerfile configuration available in `sample_control_config.yaml`
5. **Performance**: Container analysis runs independently, no impact on existing workflows

### From v0.2.0-alpha to v0.4.0
1. All benefits from v0.3.0-alpha upgrade
2. Plus container security analysis capabilities
3. Plus GPT-5 model family support

### Performance Expectations
- **Token Usage**: ~47% reduction in security context tokens (v0.3.0 feature)
- **Processing Speed**: Faster due to smaller prompts (v0.3.0 feature)
- **API Costs**: Significant reduction in LLM API costs (v0.3.0 feature)
- **Accuracy**: Improved control mapping quality through focused context (v0.3.0 feature)
- **Container Analysis**: Independent processing with dedicated FAISS indices
- **GPT-5 Support**: Automatic parameter optimization for new models

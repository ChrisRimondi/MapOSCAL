# Changelog

All notable changes to MapOSCAL will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

| Feature | v0.1.0 | v0.2.0-alpha | v0.3.0-alpha |
|---------|--------|--------------|--------------|
| Basic Control Mapping | ✅ | ✅ | ✅ |
| Security Overview | ❌ | ✅ | ✅ |
| Selective Context | ❌ | ❌ | ✅ |
| Crypto Detection | ❌ | ❌ | ✅ |
| Token Optimization | ❌ | ❌ | ✅ |
| Advanced Validation | ❌ | ✅ | ✅ |

## Upgrade Path

### From v0.2.0-alpha to v0.3.0-alpha
1. No configuration changes required
2. Existing security overviews will automatically benefit from selective context
3. Control mapping operations will immediately see token usage reduction
4. All existing CLI commands continue to work unchanged

### Performance Expectations
- **Token Usage**: ~47% reduction in security context tokens
- **Processing Speed**: Faster due to smaller prompts
- **API Costs**: Significant reduction in LLM API costs
- **Accuracy**: Improved control mapping quality through focused context

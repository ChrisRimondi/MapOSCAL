# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of MapOSCAL seriously. If you believe you have found a security vulnerability, please report it to us as described below.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to [security@maposcal.org](mailto:security@maposcal.org).

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include the requested information listed below (as much as you can provide) to help us better understand the nature and scope of the possible issue:

- Type of issue (buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the vulnerability
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

This information will help us triage your report more quickly.

## Preferred Languages

We prefer all communications to be in English.

## Policy

MapOSCAL follows the principle of [Responsible Disclosure](https://en.wikipedia.org/wiki/Responsible_disclosure).

## Security Best Practices

When using MapOSCAL, please follow these security best practices:

1. **API Key Security**: Never commit your OpenAI API key to version control. Use environment variables or secure secret management.

2. **Input Validation**: Always validate and sanitize any input data before processing.

3. **Network Security**: Ensure secure communication channels when transmitting sensitive data.

4. **Access Control**: Implement proper access controls for any systems that use MapOSCAL outputs.

5. **Regular Updates**: Keep MapOSCAL and its dependencies updated to the latest secure versions.

6. **Audit Logging**: Enable comprehensive logging for security-relevant events.

## Security Features

MapOSCAL includes several security features:

- **Local Processing**: Code analysis is performed locally to minimize data exposure
- **Secure Embeddings**: Uses local embedding models to avoid sending code to external services
- **Input Validation**: Comprehensive validation of all inputs and configurations
- **Error Handling**: Secure error handling that doesn't expose sensitive information
- **Dependency Scanning**: Automated security scanning of dependencies via GitHub Actions

## Security Contacts

- **Security Team**: [security@maposcal.org](mailto:security@maposcal.org)
- **Project Maintainer**: [chrisrimondi](https://github.com/chrisrimondi)

## Acknowledgments

We would like to thank all security researchers and contributors who help keep MapOSCAL secure by reporting vulnerabilities and suggesting improvements. 
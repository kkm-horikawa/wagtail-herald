# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.x.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, use GitHub's Security Advisories feature:

1. Go to the [Security tab](https://github.com/kkm-horikawa/wagtail-seo-toolkit/security) of this repository
2. Click "Report a vulnerability"
3. Fill out the form with details about the vulnerability

### What to Include

Please include the following information in your report:

- Type of vulnerability (e.g., XSS, code injection, etc.)
- Full paths of source file(s) related to the vulnerability
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Resolution Target**: Within 30 days (depending on complexity)

### Disclosure Policy

- We will acknowledge receipt of your vulnerability report
- We will confirm the vulnerability and determine its impact
- We will release a fix and publicly disclose the vulnerability once a fix is available
- We will credit you in the security advisory (unless you prefer to remain anonymous)

## Security Best Practices for Users

When using wagtail-seo-toolkit:

1. Always use the latest version
2. Keep your Wagtail and Django installations up to date
3. Follow Wagtail's security recommendations
4. Be cautious with user-generated HTML content (consider sanitization)

## Dependencies

This package depends on:
- Wagtail (follows Wagtail's security policy)
- Django (follows Django's security policy)

Please ensure you're using supported versions of these dependencies.

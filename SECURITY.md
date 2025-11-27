# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

The Riso team takes security vulnerabilities seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via one of the following methods:

1. **Preferred**: Use GitHub's Security Advisory feature:
   - Navigate to https://github.com/wyattowalsh/riso/security/advisories
   - Click "Report a vulnerability"
   - Fill out the advisory form with details

2. **Alternative**: Email the maintainers:
   - Contact information available on the [GitHub profile](https://github.com/wyattowalsh)

### What to Include

Please include as much of the following information as possible:

- Type of vulnerability (e.g., SQL injection, XSS, authentication bypass)
- Full paths of source file(s) related to the vulnerability
- The location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability, including how an attacker might exploit it
- Any potential mitigations you've identified

### Response Timeline

- **Initial Response**: Within 48 hours of receipt
- **Status Update**: Within 7 days with an assessment of the report
- **Fix Timeline**: Depends on severity and complexity
  - Critical: 7-14 days
  - High: 14-30 days
  - Medium: 30-60 days
  - Low: 60-90 days

### Disclosure Policy

- We follow a coordinated disclosure policy
- Security advisories will be published after a fix is released
- Credit will be given to security researchers who responsibly disclose vulnerabilities (unless anonymity is requested)
- We request 90 days from initial report before public disclosure

## Security Best Practices for Users

### Template Usage

When using Riso templates, follow these security practices:

1. **Environment Variables**
   - Never commit `.env` files to version control
   - Use `.env.example` for documentation only
   - Rotate secrets regularly

2. **Dependencies**
   - Keep dependencies up to date
   - Run `uv sync` regularly to get security patches
   - Monitor security advisories for dependencies

3. **Authentication**
   - Always implement proper JWT validation (don't use TODO placeholders in production)
   - Use strong secret keys (minimum 32 characters, randomly generated)
   - Enable HTTPS in production

4. **Database**
   - Use connection pooling with limits
   - Enable SSL/TLS for database connections
   - Use parameterized queries (already configured in templates)
   - Never expose database credentials in code

5. **API Security**
   - Implement rate limiting (see spec 011)
   - Enable CORS with appropriate origins
   - Validate all input data with Pydantic
   - Use API versioning (see spec 010)

6. **File Uploads**
   - Validate file types and sizes
   - Scan uploaded files for malware
   - Store files outside web root
   - Use signed URLs for access

### CI/CD Security

1. **Secrets Management**
   - Use GitHub Secrets for sensitive data
   - Never print secrets in CI logs
   - Rotate CI/CD secrets regularly

2. **Dependency Scanning**
   - Enable Dependabot
   - Run `safety check` in CI
   - Use `bandit` for Python security scanning

3. **Code Signing**
   - Sign commits with GPG
   - Verify signatures on merge

### Template-Specific Security

#### GraphQL Templates

- **Current Status**: Authentication is placeholder (TODO comments)
- **Required Actions**:
  - Implement JWT validation in `graphql_api/auth.py`
  - Add `@auth` decorator to protected mutations
  - Configure proper CORS settings

#### SaaS Templates

- Webhook signature verification is implemented
- OAuth state validation is configured
- CSRF protection is enabled by default

#### API Templates

- Input validation with Pydantic
- SQL injection protection via SQLAlchemy
- XSS protection in responses

## Known Security Limitations

### Current TODOs (DO NOT USE IN PRODUCTION)

1. **GraphQL Authentication** (`template/files/python/graphql_api/auth.py:108`)
   - Status: Placeholder implementation
   - Risk: No authentication validation
   - Mitigation: Implement JWT validation before production use

2. **Database Sessions** (`template/files/python/graphql_api/main.py:24`)
   - Status: Commented out
   - Risk: Queries cannot execute
   - Mitigation: Implement `get_db_session` dependency

3. **Email Templates** (`template/files/node/saas/integrations/email/resend/client.ts:209`)
   - Status: TODO for React Email component
   - Risk: Unstyled emails
   - Mitigation: Create proper email templates

## Security Tools

We use the following tools for security:

- **Bandit**: Python security scanner
- **Safety**: Dependency vulnerability scanner
- **detect-secrets**: Secret detection in commits
- **Dependabot**: Automated dependency updates
- **actionlint**: GitHub Actions workflow validation

## Security Contacts

For sensitive security information that should not be disclosed publicly:

- GitHub Security Advisories (preferred)
- Project maintainer via GitHub profile

## Attribution

This security policy is adapted from:
- [GitHub's Security Advisory Guidelines](https://docs.github.com/en/code-security/security-advisories)
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)

## Updates

This security policy was last updated: 2025-11-27

Check back regularly for updates to our security practices and supported versions.

# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

## Reporting a Vulnerability

We take the security of education-services seriously. If you believe you have
found a security vulnerability, please report it to us as described below.

### Where to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via one of the following channels:

- **Email**: security@education-services.local
- **GitHub Security Advisories**: https://github.com/education-services/education-services/security/advisories/new

You should receive a response within 48 hours. If for some reason you do not,
please follow up via email to ensure we received your original message.

### What to Include

Please include the following information in your report:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

This information will help us triage your report more quickly.

### What to Expect

After you submit a report, you can expect:

1. **Acknowledgment** within 48 hours
2. **Triage and assessment** within 7 days
3. **Regular updates** about progress
4. **Credit** in the security advisory (if desired)

## Security Architecture

education-services implements multiple layers of security:

### 1. Strict Non-Mock Mode
- All dependencies (PostgreSQL, Anthropic API, PyMuPDF) must be real
- Application refuses to start with missing dependencies
- No silent degradation to mock data

### 2. Citation Requirements
- All educational content must reference specific textbook pages
- Agent refuses to fabricate content not in the source material

### 3. Privacy Protection
- Student data is anonymized in logs
- Homework images are redacted
- No PII is sent to external training

### 4. Prompt Injection Defense
- User uploads (PDFs, homework images) are treated as data, not instructions
- Hidden instructions in documents are explicitly ignored
- See [docs/guardrails.md](docs/guardrails.md) for details

### 5. Permission Isolation
- Subagents have read-only access by default
- Only the `feedback-writer` subagent has write permissions
- Parent role cannot modify other students' mastery

### 6. Audit Logging
- All agent outputs are logged with safety flags
- Sensitive content is redacted before logging
- See [docs/observability.md](docs/observability.md)

## Known Security Considerations

### Educational LLM Risks

- **Hallucination**: LLMs can generate plausible but incorrect information.
  We mitigate this with mandatory citation requirements.
- **Out-of-scope requests**: Users may try to make agents perform unrelated
  tasks. Our guardrails explicitly reject these.
- **PII in user data**: Student work may contain PII. We recommend running
  on-premise for sensitive deployments.

### Supply Chain

- We pin all dependencies in `requirements.txt`
- We use GitHub Dependabot to monitor for CVEs
- We sign releases (planned for v0.2.0)

## Best Practices for Deployment

1. **Never commit API keys** to the repository
2. **Use environment variables** for all secrets
3. **Enable HTTPS** in production
4. **Restrict database access** to trusted networks
5. **Monitor logs** for safety flag triggers
6. **Review agent outputs** before sharing with students
7. **Update regularly** for security patches

## Security Hall of Fame

We thank the following researchers for responsibly disclosing security issues:

<!-- This section will be populated as we receive and resolve reports -->

## Contact

For general security questions (non-vulnerability): security@education-services.local

For emergencies (active exploitation): Please use the GitHub Security Advisory
private disclosure for fastest response.

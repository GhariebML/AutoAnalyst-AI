# Security Policy

## Secrets and API Keys

- Never commit API keys.
- Never commit `.env` files.
- Use `.env.example` only for placeholder variable names.
- If a key is leaked, rotate it immediately and notify the Team Lead.

## Sample Data

- Do not include real customer data in sample files.
- Do not include private business data, emails, phone numbers, addresses, or credentials.
- Use placeholder values in JSON samples.

## External Services

Phase 1 should not call real external APIs unless explicitly approved.

## Reporting Security Issues

Report security issues directly to the Team Lead.

Include:

- What was exposed or vulnerable.
- Which file/branch/commit is affected.
- Whether any credentials need rotation.
- Suggested mitigation if known.

Do not open public issues for sensitive security problems.

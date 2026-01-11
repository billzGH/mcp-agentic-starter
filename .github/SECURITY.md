# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

### How to Report

1. **Do NOT open a public issue** - This could expose the vulnerability to malicious actors
2. **Use GitHub's Private Vulnerability Reporting**:
   - Navigate to the Security tab
   - Click "Report a vulnerability"
   - Fill out the advisory form with details

### What to Include

Please provide:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)
- Your contact information for follow-up

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 1 week
- **Fix Timeline**: Depends on severity, but critical issues will be prioritized

I take security seriously and will work with you to understand and address the issue promptly.

## Supported Versions

| Version/Branch   | Supported |
| --------------   | --------- |
| main (latest)    | ✅ Yes    |
| feature branches | ❌ No     |

Since this is an educational project in active development, only the `main` branch receives security updates.

## Security Considerations

This project is designed for **learning and development purposes**. If you're deploying MCP servers in production, please be aware of the following:

### File System Server Risks

The file system server (`examples/file-system/`) can:

- Read and write files on the host system
- Execute file operations with the permissions of the running process
- Access any path the process has permissions for

**Recommendations:**

- Run with minimal necessary permissions
- Configure strict allowed/blocked paths in Claude Desktop config
- Never run as root/administrator
- Audit file operations regularly
- Consider using Docker or containers for isolation

### Data Analysis Server Risks

The data analysis server (`examples/data-analysis/`) can:

- Read CSV/JSON files from configured directories
- Execute Python code for data aggregation
- Load potentially large datasets into memory

**Recommendations:**

- Restrict data directory to known safe locations
- Validate input file paths
- Monitor resource usage (memory, CPU)
- Sanitize file paths to prevent directory traversal

### General Best Practices

When using or modifying this project:

1. **Never commit secrets**
   - No API keys, tokens, or credentials in code
   - Use environment variables (`.env` files)
   - Add `.env` to `.gitignore`

2. **Keep dependencies updated**
   - Monitor Dependabot alerts
   - Review and update `pyproject.toml` dependencies
   - Test updates before deploying

3. **Review third-party code**
   - Audit MCP server code before running
   - Understand what permissions servers request
   - Be cautious with community-contributed servers

4. **Limit MCP server capabilities**
   - Use principle of least privilege
   - Configure Claude Desktop with appropriate restrictions
   - Disable servers you're not actively using

5. **Validate data sources**
   - Only use trusted datasets
   - Sanitize user-provided data
   - Be aware of CSV/JSON injection risks

## Known Limitations

As an educational project:

- Code examples prioritize clarity over production-hardening
- Some error handling may be minimal for teaching purposes
- Not all edge cases are covered in example code

**This is intentional** - the goal is learning. However, please adapt and harden code appropriately for production use.

## Security Features Enabled

This repository has the following GitHub security features enabled:

- ✅ Dependabot alerts
- ✅ Dependabot security updates
- ✅ Secret scanning
- ✅ Push protection (prevents committing secrets)
- ✅ Private vulnerability reporting
- ✅ Branch protection on `main`

## Scope

### In Scope for Security Reports

- Path traversal vulnerabilities
- Command injection risks
- Dependency vulnerabilities
- Information disclosure
- Authentication/authorization bypass
- Unsafe file operations
- Code execution vulnerabilities

### Out of Scope

- Theoretical vulnerabilities without proof of concept
- Issues in deprecated/archived branches
- Social engineering attacks
- DoS attacks requiring significant resources
- Issues already reported and acknowledged

## Recognition

Security researchers who responsibly disclose vulnerabilities will be:

- Acknowledged in the fix commit/PR (if desired)
- Credited in release notes
- Added to a security acknowledgments section (if we create one)

Your contributions to keeping this project secure are greatly appreciated!

## Questions?

If you have questions about this security policy or general security best practices for MCP servers, feel free to:

- Open a regular issue (for non-sensitive questions)
- Join the discussion in the Anthropic Discord
- Reach out via email

---

**Note**: This project is a learning resource. While we take security seriously, it should not be used in production without appropriate security hardening and review.

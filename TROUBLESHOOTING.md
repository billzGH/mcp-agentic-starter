# Troubleshooting Guide

Common issues and their solutions when setting up MCP servers.

## Python Version Issues

### Problem: Multiple Python Versions

**Symptoms**:

- `ModuleNotFoundError: No module named 'mcp'` even after installing
- `uv pip list` shows package installed but Python can't find it
- Different Python versions when running `python --version` vs `python3 --version`

**Root Cause**: You have multiple Python installations and they're not aligned.

**Solution**:

```bash
# 1. Check what you have
which python
which python3
python --version
python3 --version
uv run python --version

# 2. Check where UV installed mcp
uv pip list | grep mcp

# 3. Use the right Python
# Option A: Always use uv run (RECOMMENDED)
uv run server.py

# Option B: Use python3 explicitly
python3 server.py

# Option C: Fix your shell alias
# Edit ~/.zshrc or ~/.bashrc and remove or update:
# alias python=/usr/local/bin/python3
```

### Problem: Shell Aliases Interfering

**Symptoms**:

- Virtual environment is activated but wrong Python runs
- `$VIRTUAL_ENV` is set but `python` uses system Python

**Root Cause**: Shell aliases override virtual environment activation.

**Solution**:

```bash
# Check for problematic aliases
alias | grep python

# Remove the alias temporarily
unalias python

# Or edit your shell config (~/.zshrc or ~/.bashrc)
# Remove lines like: alias python=/usr/local/bin/python3

# Better alias that respects virtual environments:
alias python='[ -n "$VIRTUAL_ENV" ] && command python || python3'
```

## UV-Specific Issues

### Problem: UV Not Found

**Symptoms**: `command not found: uv`

**Solution**:

```bash
# Install UV
# Mac:
brew install uv

# Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify
uv --version
```

### Problem: Wrong Python Version with UV

**Symptoms**: UV uses old Python version

**Solution**:

```bash
# Check UV's Python
uv run python --version

# Install specific Python version with UV
uv python install 3.12

# Use specific Python with UV
uv venv --python 3.12
```

## Claude Desktop Configuration Issues

### Problem: Server Not Showing in Claude

**Symptoms**: Claude says it doesn't have access to tools

**Common Causes**:

1. **Wrong Path Format**

   ```json
   ❌ Wrong: "~/git/mcp-agentic-starter/..."
   ❌ Wrong: "./examples/data-analysis/server.py"
   ✅ Correct: "/Users/yourname/git/mcp-agentic-starter/..."
   ```

2. **Wrong Command**

   ```json
   ❌ Wrong: "python" (might use wrong version)
   ✅ Better: "python3"
   ✅ Best: "uv" with proper args
   ```

3. **Config File Location**
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - NOT `~/.claude/` or `~/.config/claude/`

**Solutions**:

```bash
# 1. Get absolute path
cd ~/git/mcp-agentic-starter/examples/data-analysis
pwd
# Copy this EXACT output

# 2. Use UV-based config (RECOMMENDED)
{
  "mcpServers": {
    "data-analysis": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/yourname/git/mcp-agentic-starter/examples/data-analysis",
        "server.py"
      ]
    }
  }
}

# 3. OR use python3 with full path
{
  "mcpServers": {
    "data-analysis": {
      "command": "/usr/local/bin/python3",
      "args": [
        "/Users/yourname/git/mcp-agentic-starter/examples/data-analysis/server.py"
      ]
    }
  }
}

# 4. Restart Claude Desktop COMPLETELY
# Don't just close window - quit the app entirely
```

### Problem: Server Starts But Tools Don't Work

**Symptoms**: Claude sees tools but they error when called

**Solutions**:

```bash
# 1. Test server manually
cd examples/data-analysis
uv run server.py
# Should start without errors

# 2. Check file permissions
ls -la server.py
# Should be readable

# 3. Check datasets exist
ls -la ../../datasets/sales/
# Should show CSV and JSON files

# 4. Generate data if missing
uv run generate_sales_data.py

# 5. Check logs
tail -f ~/Library/Logs/Claude/mcp-*.log
```

## Module Import Errors

### Problem: Can't Import MCP

**Symptoms**: `ModuleNotFoundError: No module named 'mcp'`

**Solutions**:

```bash
# 1. Verify installation
uv pip list | grep mcp
# Should show: mcp  1.24.0 (or similar)

# 2. Reinstall
uv pip install --force-reinstall mcp

# 3. Check Python version (needs 3.10+)
uv run python --version

# 4. Try in a fresh environment
cd ~/git/mcp-agentic-starter
rm -rf .venv
uv venv
uv pip install mcp

# 5. Use uv run instead of python
uv run server.py
```

### Problem: Other Import Errors

**Symptoms**: `ModuleNotFoundError` for pandas, numpy, etc.

**Solutions**:

```bash
# Install all dependencies
uv pip install -r requirements.txt

# Or install just what you need
uv pip install mcp pandas numpy

# Verify
uv pip list
```

## Testing Your Setup

### Quick Diagnostic

Run this script to check your setup:

```bash
#!/bin/bash
echo "=== Python Diagnostic ==="
echo "which python: $(which python)"
echo "which python3: $(which python3)"
echo "python --version: $(python --version 2>&1)"
echo "python3 --version: $(python3 --version 2>&1)"
echo ""
echo "=== UV Diagnostic ==="
echo "which uv: $(which uv)"
echo "uv --version: $(uv --version 2>&1)"
echo "uv run python --version: $(uv run python --version 2>&1)"
echo ""
echo "=== Environment ==="
echo "VIRTUAL_ENV: $VIRTUAL_ENV"
echo ""
echo "=== MCP Package ==="
uv pip list | grep mcp
echo ""
echo "=== Aliases ==="
alias | grep python
```

Save as `diagnostic.sh`, make executable with `chmod +x diagnostic.sh`, and run it.

### Test Server Manually

```bash
# 1. Navigate to server directory
cd ~/git/mcp-agentic-starter/examples/data-analysis

# 2. Test server starts
uv run server.py
# Should start without errors (Ctrl+C to stop)

# 3. Success indicators:
# - No ModuleNotFoundError
# - No import errors
# - Server waits for input (cursor blinking)
# - Press Ctrl+C to stop

# 4. If that works, your server is ready for Claude Desktop!
```

## Still Stuck?

### Collect Information

```bash
# Run diagnostic
./diagnostic.sh > diagnostic.txt

# Check logs
tail -100 ~/Library/Logs/Claude/mcp-*.log > claude-logs.txt

# Test server
cd examples/data-analysis
uv run server.py 2>&1 | head -20 > server-test.txt
```

### Common Solutions Checklist

- [ ] UV is installed: `uv --version`
- [ ] Python 3.10+: `uv run python --version`
- [ ] MCP installed: `uv pip list | grep mcp`
- [ ] Using `uv run` instead of `python`
- [ ] Absolute paths in Claude config
- [ ] Claude Desktop fully restarted
- [ ] Data files generated: `ls datasets/sales/`
- [ ] No shell aliases interfering: `alias | grep python`

### Clean Slate Approach

If nothing works, start fresh:

```bash
# 1. Remove everything
cd ~/git/mcp-agentic-starter
rm -rf .venv

# 2. Reinstall UV
brew reinstall uv

# 3. Create fresh environment
uv venv

# 4. Install dependencies
uv pip install mcp

# 5. Test
cd examples/data-analysis
uv run server.py
```

## Platform-Specific Issues

### macOS

**Issue**: Permission denied

```bash
chmod +x server.py
```

**Issue**: Gatekeeper blocking Python

```bash
# Go to System Preferences > Security & Privacy
# Allow Python to run
```

### Linux

**Issue**: Python version too old

```bash
# Install newer Python
sudo apt update
sudo apt install python3.12

# Use with UV
uv venv --python python3.12
```

### Windows

**Issue**: PowerShell execution policy

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Issue**: Path separators

- Use forward slashes `/` or escaped backslashes `\\` in config
- Example: `C:/projects/mcp-agentic-starter/...`

## Getting Help

If you're still stuck after trying these solutions:

1. Run the diagnostic script
2. Check the logs
3. Create a minimal test case
4. Report the issue with:
   - Diagnostic output
   - Log files
   - What you tried
   - Exact error messages

Remember: Most issues are environment-related, not code-related. The server code works - it's usually about getting Python/UV/paths aligned correctly!

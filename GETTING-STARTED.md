# Getting Started with MCP Agentic AI

This guide will get you up and running with your first MCP server and agentic workflow in about 30 minutes.

## Prerequisites

- **Claude Desktop** (free download from claude.ai)
- **Python 3.10+** or **Node.js 18+**
- **Basic terminal/command line knowledge**
- **Text editor** (VS Code, Sublime, etc.)

## Step 1: Clone and Setup (5 minutes)

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-agentic-starter.git
cd mcp-agentic-starter

# Install UV (Python package manager)
# Mac:
brew install uv
# Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install dependencies with UV
uv sync
```

## Step 2: Generate Sample Data (2 minutes)

```bash
cd examples/data-analysis
uv run generate_sales_data.py
```

This creates realistic e-commerce data in `datasets/sales/`:

- `customers.csv` - 1,000 customers
- `products.csv` - 100 products  
- `transactions.csv` - 10,000 transactions

## Step 3: Test the Data Analysis Server (5 minutes)

```bash
# Test the server locally - it should start without errors
uv run server.py
```

The server will start and wait for input from Claude Desktop. If it starts without any errors, it's working correctly! Press Ctrl+C to stop it.

**What success looks like:**

- No error messages
- Server is waiting (you can see the cursor blinking)
- No "ModuleNotFoundError" or import errors

If you see any errors, check the [Troubleshooting Guide](TROUBLESHOOTING.md).

## Step 4: Connect to Claude Desktop (10 minutes)

### Find Your Config File

**Mac/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Edit the Config

Add your MCP server:

```json
{
  "mcpServers": {
    "data-analysis": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/FULL/PATH/TO/mcp-agentic-starter/examples/data-analysis",
        "server.py"
      ]
    }
  }
}
```

**Important**: Replace `/FULL/PATH/TO/` with your actual path.

To find your full path:

```bash
# Run this in your project directory:
cd ~/git/mcp-agentic-starter/examples/data-analysis
pwd
# Copy the output and use it in your config
```

**Alternative (using python3 directly)**:

```json
{
  "mcpServers": {
    "data-analysis": {
      "command": "python3",
      "args": [
        "/FULL/PATH/TO/mcp-agentic-starter/examples/data-analysis/server.py"
      ]
    }
  }
}
```

Note: This requires `mcp` to be installed in your system Python 3.12+ or a virtual environment that python3 uses.

### Restart Claude Desktop

Completely quit and restart Claude Desktop (not just close the window).

## Step 5: Test in Claude (5 minutes)

Open Claude Desktop and try these prompts:

### Test 1: Check Connection

```plaintext
Do you have access to data analysis tools?
```

Claude should confirm it can see the tools.

### Test 2: Explore Data

```plaintext
What data files are available?
```

You should see your sales data files listed.

### Test 3: Basic Analysis

```plaintext
Give me a summary of the customers.csv file
```

Claude will analyze the customer data.

### Test 4: Real Analysis

```plaintext
Analyze the transactions data:
1. What's the total revenue?
2. What are the top 5 products by sales?
3. Which region has the highest sales?
```

Claude will use multiple tool calls to answer these questions!

## Step 6: Try More Complex Tasks (5 minutes)

Now try some agentic workflows:

### Exploratory Analysis

```plaintext
I'm new to this sales data. Help me understand:
- What time period does it cover?
- What's the average transaction value?
- Are there any interesting patterns?
```

### Customer Segmentation

```plaintext
Analyze customers and group them into:
- High value (>$1000 total spend)
- Medium value ($500-$1000)
- Low value (<$500)

How many are in each segment?
```

### Product Performance

```plaintext
Find products with:
- High revenue but low ratings
- Low stock quantities (<50)

Which ones should we focus on?
```

## Understanding What Just Happened

When you give Claude a task:

1. **Claude reads your request** and decides it needs external data
2. **Calls MCP tools** like `list_data_files` or `analyze_column`
3. **Your server processes** the request and returns results
4. **Claude synthesizes** the information into a helpful response
5. **Repeats as needed** until the task is complete

This is **agentic AI** - Claude autonomously using tools to accomplish goals!

## Troubleshooting

### Server Not Appearing

**Problem**: Claude says it doesn't have data analysis tools

**Solutions**:

1. Check config file path is correct
2. Verify you used ABSOLUTE path (not relative)
3. Make sure Python is in your PATH
4. Restart Claude Desktop completely
5. Check logs: `~/Library/Logs/Claude/mcp*.log`

### Tools Not Working

**Problem**: Claude sees tools but they fail

**Solutions**:

1. Check file paths in server.py are correct
2. Run server manually to see errors: `uv run server.py`
3. Check datasets exist: `ls ../../datasets/sales/`
4. Verify UV is using the correct Python: `uv run python --version`

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'mcp'`

**Solutions**:

1. Ensure UV is installed: `uv --version`
2. Reinstall: `uv sync`
3. Check Python version: `python3 --version` (needs 3.10+)
4. Use `uv run server.py` instead of `python server.py`
5. If using `python3` directly, make sure it points to Python 3.10+ with `mcp` installed
6. Check which Python: `which python3` and verify it's using the right version

## What's Next?

### Learn More

1. 📚 Read [Tutorial 1: MCP Basics](tutorials/01-mcp-basics.md)
2. 🛠️ Follow [Tutorial 2: First Server](tutorials/02-first-server.md)
3. 🎯 Study [Effective Prompts](prompts/effective-prompts.md)

### Build Something

1. Modify the data analysis server to add new features
2. Create your own dataset
3. Build a server for your own use case

### Explore Examples

- **File System Server**: Read/write files
- **Task Manager**: Manage todos
- **Database Server**: Query SQLite databases

### Join the Community

- Share your MCP servers
- Contribute examples
- Help others get started

## Quick Reference

### Useful Commands

```bash
# Install dependencies
uv sync

# Run server manually (should start without errors)
uv run server.py

# Generate new sample data
uv run generate_sales_data.py

# View logs
tail -f ~/Library/Logs/Claude/mcp-*.log

# Check UV and Python versions
uv --version
uv run python --version
```

### Config File Locations

- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Logs Mac**: `~/Library/Logs/Claude/`
- **Logs Windows**: `%APPDATA%\Claude\logs\`

### Example Prompts

See [prompts/effective-prompts.md](prompts/effective-prompts.md) for a comprehensive collection of proven prompts.

## Success Checklist

You're successfully set up when you can:

- ✅ Start the server without errors
- ✅ See tools in Claude Desktop
- ✅ List available data files
- ✅ Run analysis queries
- ✅ Get helpful responses from Claude

## Getting Help

If you're stuck:

1. Check the [troubleshooting section](#troubleshooting) above
2. Review your config file syntax
3. Check server logs for errors
4. Make sure data files exist
5. Try running the server manually to see error messages

## What You've Learned

Congratulations! You now understand:

- ✅ What MCP servers are and how they work
- ✅ How to connect external tools to Claude
- ✅ How to design agentic workflows
- ✅ How to write effective prompts
- ✅ How to build and test your own servers

You're ready to start building your own agentic AI applications!

## Next Steps

Choose your own adventure:

**Path 1: Learn More Theory**
→ Read all tutorials in order
→ Understand design patterns
→ Study best practices

**Path 2: Build Projects**
→ Create a server for your own data
→ Automate a repetitive task
→ Integrate with APIs you use

**Path 3: Contribute**
→ Add new examples
→ Improve documentation
→ Share your servers

Happy building! 🚀

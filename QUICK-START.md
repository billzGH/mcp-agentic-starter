# MCP Agentic Starter - Quick Reference

## 🚀 5-Minute Setup

```bash
# 1. Clone repo
git clone [your-repo-url]
cd mcp-agentic-starter

# 2. Install UV (Python package manager) and dependencies
# Mac/Linux:
brew install uv
# Or visit: https://github.com/astral-sh/uv

# OR for Node.js examples
npm install

# Activate it
# On Mac/Linux:
source .venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# 3. Generate sample data
cd examples/data-analysis
uv run generate_sales_data.py

# 4. Configure Claude Desktop
# Edit: ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "data-analysis": {
      "command": "python",
      "args": ["/full/path/to/examples/data-analysis/server.py"]
    }
  }
}

# 5. Restart Claude Desktop and test!
```

## 📁 Project Structure

```file-tree
mcp-agentic-starter/
├── README.md                    # Start here
├── GETTING-STARTED.md          # Detailed setup guide
├── tutorials/                  # Learning materials
│   ├── 01-mcp-basics.md       # What is MCP?
│   └── 02-first-server.md     # Build your first server
├── examples/                   # Working examples
│   ├── data-analysis/         # Analyze CSV/JSON data
│   ├── file-system/           # Read/write files
│   └── task-manager/          # Coming soon
├── datasets/                   # Sample data
│   └── sales/                 # E-commerce transactions
├── prompts/                    # Effective prompts
│   └── effective-prompts.md   # Proven patterns
└── projects/                   # Project ideas
    └── PROJECT-IDEAS.md       # 19 project templates
```

## 🎯 What's Included

### Working MCP Servers

1. **Data Analysis Server** - Query and analyze CSV/JSON files
2. **File System Server** - Safe file operations in a workspace
3. **Task Manager Server** (tutorial) - Manage todos

### Sample Datasets

- **Sales Data**: 10K transactions, 1K customers, 100 products
- Ready to analyze with the data analysis server

### Tutorials

1. MCP Basics (30 min)
2. Your First Server (45 min)
3. Agentic Patterns (coming soon)

### Resources

- 30+ proven prompt templates
- 19 project ideas with implementation guides
- Best practices and patterns

## 💡 Try These First

### With Data Analysis Server

What data files are available?
Analyze transactions.csv - what's the total revenue?
Show me the top 5 products by sales
Which region has the highest sales?

### With File System Server

Create a file called notes.txt with my daily tasks
List all files in my workspace
Search for files containing "meeting"

## 🔧 Troubleshooting

### Server not connecting?

- Check config file location
- Use absolute paths, not relative
- Restart Claude Desktop completely
- Check logs: `~/Library/Logs/Claude/`

### Tools not working?

- Activate virtual environment
- Verify dependencies installed
- Test server manually: `uv run server.py`

## 📚 Next Steps

1. **Learn**: Read tutorials in order
2. **Experiment**: Modify example servers
3. **Build**: Pick a project from PROJECT-IDEAS.md
4. **Share**: Contribute your work back

## 🔗 Quick Links

- [Full Setup Guide](GETTING-STARTED.md)
- [MCP Basics Tutorial](tutorials/01-mcp-basics.md)
- [Build First Server](tutorials/02-first-server.md)
- [Effective Prompts](prompts/effective-prompts.md)
- [Project Ideas](projects/PROJECT-IDEAS.md)

## 🆘 Get Help

- Check troubleshooting sections in docs
- Review example prompts
- Test with sample data first
- Read MCP official docs

## ✨ Key Concepts

**MCP Server**: Bridge between Claude and external tools
**Tool**: Function Claude can call (read file, query DB, etc.)
**Agentic AI**: AI that uses tools autonomously to complete tasks
**Workspace**: Safe directory for file operations

## 🎓 Learning Path

**Day 1**: Setup + understand MCP basics
**Day 2**: Build your first server
**Day 3**: Write effective prompts
**Day 4**: Start a real project
**Week 2**: Iterate and improve
**Week 3**: Build something new
**Week 4**: Share with community

Happy building! 🚀

# MCP Agentic AI Starter Kit

A practical guide and toolkit for learning how to build agentic AI applications using Model Context Protocol (MCP) servers. This repository contains tutorials, examples, and sample datasets to help you understand how MCP servers enable AI agents to interact with external tools and data sources.

## 🎯 What You'll Learn

- How MCP servers work and why they're useful
- Building custom MCP servers for different use cases
- Connecting AI agents to databases, APIs, and file systems
- Practical agentic workflows (research, data analysis, task automation)
- Best practices for prompt engineering with tools

## 🚀 Quick Start

### Prerequisites

- Python 3.10+ or Node.js 18+
- Claude Desktop app (for testing MCP servers)
- Basic understanding of AI/LLMs

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/mcp-agentic-starter.git
cd mcp-agentic-starter

# Install UV (fast Python package manager)
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install all dependencies
uv sync

# Optional: Install PostgreSQL support
uv sync --extra postgres

# Optional: Install FastAPI/mock API support
uv sync --extra api

# Optional: Install visualization tools
uv sync --extra viz

# Optional: Install development tools (ruff, black, pytest)
uv sync --extra dev

# Install all extras at once
uv sync --all-extras
```

## 📚 Repository Structure

```file-tree
mcp-agentic-starter/
├── tutorials/              # Step-by-step learning guides
│   ├── 01-mcp-basics.md
│   ├── 02-first-server.md
│   ├── 03-agentic-patterns.md
│   ├── 04-advanced-workflows.md
│   └── 05-testing-mcp-servers.md
├── examples/               # Working MCP server examples
│   ├── file-system/       # File operations server
│   ├── data-analysis/     # CSV/JSON data processing
│   ├── database/          # SQL database server (SQLite/PostgreSQL)
│   ├── web-api/           # REST API integration with mock server
│   ├── task-manager/      # Persistent task list server
│   └── data-pipeline/     # Multi-stage data processing pipeline
├── datasets/              # Synthetic datasets for practicing
│   ├── sales/             # E-commerce transactions, customers, products
│   └── customer-support/  # Support tickets with categories and sentiment
├── tests/                 # Unit test suite (80 tests across all servers)
├── prompts/               # Effective prompts for agentic tasks
└── projects/              # Complete project templates
```

## 🛠️ Example Use Cases

### 1. **Personal Knowledge Base** (Beginner)

Build an MCP server that lets AI agents search and retrieve information from your personal notes, documents, and bookmarks.

**What you'll learn**: File system operations, text search, context management

### 2. **Data Analysis Assistant** (Intermediate)

Create an agent that can query databases, generate visualizations, and produce reports from business data.

**What you'll learn**: SQL integration, data processing, multi-step workflows

### 3. **Research Automation** (Intermediate)

Develop an agent that searches academic papers, extracts key findings, and synthesizes research summaries.

**What you'll learn**: API integration, content extraction, structured outputs

### 4. **Task Management System** (Advanced)

Build a complete system where agents can create, track, and manage tasks across multiple platforms (GitHub, Jira, etc.).

**What you'll learn**: Multi-tool coordination, state management, error handling

## 🔧 Included MCP Servers

1. **File System Server** - Read, write, search, and manage local files
2. **Data Analysis Server** - Analyze CSV and JSON datasets with aggregations
3. **Database Server** - Query SQL databases (SQLite local, PostgreSQL cloud)
4. **Web API Server** - Integrate with REST APIs (includes mock API for testing)
5. **Task Manager Server** - Persistent task list with create, complete, and delete
6. **Data Pipeline Server** - Multi-stage processing pipeline with state persistence

All servers include comprehensive documentation and work without paid API accounts.

## 📊 Sample Datasets

Realistic, synthetic datasets included for practicing:

- **E-commerce** (`datasets/sales/`): 10K transactions, 1K customers, 44 products across 5 categories
- **Customer Support** (`datasets/customer-support/`): 1K support tickets with categories, priorities, sentiment scores, and resolution times

All datasets are generated with fixed random seeds for reproducibility and are free to use for learning.

## 🎓 Tutorials

### Tutorial 1: MCP Basics (30 min)

Learn what MCP is, how it works, and why it's useful for AI agents.

### Tutorial 2: Your First MCP Server (45 min)

Build a simple calculator server and connect it to Claude.

### Tutorial 3: Agentic Patterns (60 min)

Discover common patterns for building effective AI agents with tools.

### Tutorial 4: Advanced Workflows (90 min)

Create complex multi-step workflows with error handling and state management.

### Tutorial 5: Testing MCP Servers (60 min)

Write a unit test suite for MCP servers using pytest — async testing, mocking, and isolation patterns.

## 🌟 Real-World Projects

Each project includes:

- Complete source code
- Step-by-step guide
- Sample data
- Effective prompts
- Common pitfalls and solutions

### Project Ideas Included

1. **Personal Research Assistant** - Helps you research topics and compile findings
2. **Code Documentation Generator** - Analyzes codebases and generates docs
3. **Meeting Notes Analyzer** - Extracts action items and decisions
4. **Content Repurposing Tool** - Transforms content between formats
5. **Data Quality Checker** - Validates and cleans datasets

## 🧪 Test Suite

The project includes 80 unit tests covering all example servers:

```bash
uv sync --extra dev
uv run pytest tests/ -v
```

Tests cover business logic directly (no MCP framework mocking needed) and run in under 2 seconds. See [Tutorial 5](tutorials/05-testing-mcp-servers.md) for a full walkthrough of the testing approach.

## 🤝 Contributing

Contributions welcome! Whether it's:

- New tutorial sections
- Additional MCP server examples
- More sample datasets
- Bug fixes or improvements

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📖 Additional Resources

- [MCP Official Documentation](https://modelcontextprotocol.io/)
- [Anthropic's MCP Guide](https://docs.anthropic.com/en/docs/build-with-claude/mcp)
- [Community MCP Servers](https://github.com/modelcontextprotocol/servers)

## 📝 License

MIT License - feel free to use for learning and commercial projects.

## 🙏 Acknowledgments

Built with inspiration from the MCP community and practical experience building agentic AI applications.

---

**Ready to get started?** Head to [tutorials/01-mcp-basics.md](tutorials/01-mcp-basics.md) to begin your journey!

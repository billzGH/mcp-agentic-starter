# Tutorial 1: Understanding MCP and Agentic AI

**Time**: 30 minutes  
**Difficulty**: Beginner

## What is MCP?

Model Context Protocol (MCP) is an open standard that allows AI models like Claude to securely connect to external data sources and tools. Think of it as a universal adapter that lets AI agents interact with databases, APIs, file systems, and more.

## Why MCP Matters for Agentic AI

Traditional AI interactions are limited to:

- The model's training data (which has a cutoff date)
- Information you paste into the conversation

With MCP, AI agents can:

- ✅ Query live databases
- ✅ Read and write files
- ✅ Call external APIs
- ✅ Execute code and tools
- ✅ Access real-time information

This transforms AI from a conversational assistant into an **autonomous agent** that can complete complex tasks.

## How MCP Works

```plaintext
┌──────────┐         ┌─────────────┐         ┌──────────────┐
│  Claude  │ ◄─────► │ MCP Server  │ ◄─────► │ Data Source  │
│  (Agent) │         │  (Bridge)   │         │  (Tool/API)  │
└──────────┘         └─────────────┘         └──────────────┘
```

1. **Claude** (the AI) decides it needs to use a tool
2. **MCP Server** receives the request and executes it
3. **Data Source** provides the information or performs the action
4. Results flow back to Claude, which continues its task

## Key Concepts

### Tools

Functions that the AI can call. Examples:

- `read_file(path)` - Read a file's contents
- `query_database(sql)` - Execute a SQL query
- `search_web(query)` - Search the internet

### Resources

Data that the AI can access. Examples:

- Files in a directory
- Database tables
- API endpoints

### Prompts

Pre-configured instructions that guide the AI's behavior with specific tools.

## Agentic AI Patterns

### 1. **Single-Tool Pattern** (Simplest)

AI uses one tool repeatedly to accomplish a task.

**Example**: "Analyze all CSV files in the data folder"

- Agent reads each CSV file
- Processes the data
- Generates summary

### 2. **Sequential Pattern**

AI uses multiple tools in sequence.

**Example**: "Create a report from database data"

1. Query database
2. Process results
3. Generate visualization
4. Write report to file

### 3. **Iterative Pattern**

AI refines its approach based on results.

**Example**: "Debug this application"

1. Read error logs
2. Examine source code
3. Identify issue
4. Propose fix
5. Verify solution

### 4. **Multi-Source Pattern**

AI combines information from multiple sources.

**Example**: "Compare our sales to industry benchmarks"

1. Query internal database
2. Search external reports
3. Analyze differences
4. Generate insights

## Real-World Examples

### Example 1: Research Assistant

**Task**: "Summarize recent developments in quantum computing"

**Agentic Workflow**:

1. Search academic paper databases
2. Retrieve relevant papers
3. Extract key findings
4. Identify common themes
5. Generate structured summary
6. Save to file for future reference

**MCP Servers Needed**:

- Web search server
- File system server
- PDF reader server

### Example 2: Business Analytics

**Task**: "Identify our top customers and their trends"

**Agentic Workflow**:

1. Query sales database
2. Calculate customer metrics
3. Identify patterns
4. Generate visualizations
5. Create PowerPoint report
6. Email to stakeholders

**MCP Servers Needed**:

- Database server
- Data analysis server
- File creation server
- Email server (optional)

### Example 3: Code Maintenance

**Task**: "Update all API endpoints to use new authentication"

**Agentic Workflow**:

1. Search codebase for API calls
2. Read each file with matches
3. Analyze current auth pattern
4. Propose updated code
5. Write changes
6. Create git commit

**MCP Servers Needed**:

- File system server
- Git server
- Code analysis server

## When to Use Agentic AI

✅ **Good Use Cases**:

- Repetitive tasks with clear rules
- Data processing and analysis
- Information gathering and synthesis
- Content generation with research
- System monitoring and reporting

❌ **Not Ideal For**:

- Tasks requiring human judgment on edge cases
- Real-time critical decisions
- Creative work requiring human intuition
- Sensitive operations without oversight

## Getting Started Checklist

Before building your first MCP server, make sure you have:

- [ ] Claude Desktop installed (or API access)
- [ ] Python 3.10+ or Node.js 18+
- [ ] A clear use case in mind
- [ ] Sample data to test with
- [ ] Basic understanding of the tool/API you want to integrate

## What's Next?

In **Tutorial 2**, you'll build your first MCP server - a simple calculator that demonstrates the core concepts. You'll learn:

- How to structure an MCP server
- How to define tools
- How to connect it to Claude
- How to test and debug

Continue to [Tutorial 2: Your First MCP Server](02-first-server.md) →

## Quick Quiz

Test your understanding:

1. What are the three main components that MCP connects?
2. Name three types of tools an MCP server might provide
3. What's the difference between the Sequential and Iterative patterns?
4. Give an example of a task that's a good fit for agentic AI

**Answers:**

1. Claude (AI agent), MCP Server (bridge), and Data Sources (tools/APIs)
2. Any three of: file operations, database queries, API calls, code execution, web search, etc.
3. Sequential uses tools in a predetermined order; Iterative adjusts based on results
4. Any task that's repetitive, rule-based, and doesn't require real-time human judgment

## Additional Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Official MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- [Anthropic's Guide to Building with MCP](https://docs.anthropic.com/en/docs/build-with-claude/mcp)

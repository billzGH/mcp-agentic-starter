# Contributing to MCP Agentic Starter

Thank you for your interest in contributing! This project aims to help people learn MCP and agentic AI through practical examples.

## Ways to Contribute

### 1. Share Your MCP Servers

Have you built an interesting MCP server? We'd love to include it!

**What makes a good contribution:**

- ✅ Works with free/open-source tools
- ✅ Includes clear documentation
- ✅ Has practical use cases
- ✅ Includes example prompts
- ✅ Well-commented code

### 2. Add Tutorials

Help others learn by contributing tutorials on:

- New MCP server patterns
- Integration with specific tools/APIs
- Advanced agentic workflows
- Debugging and troubleshooting

### 3. Improve Documentation

- Fix typos or unclear explanations
- Add missing details
- Create diagrams or illustrations
- Translate to other languages

### 4. Create Sample Datasets

Generate realistic datasets for:

- Different industries (healthcare, finance, etc.)
- Various data types (text, time series, etc.)
- Specific use cases

### 5. Add Example Prompts

Share prompts that work well for:

- Specific industries or roles
- Complex multi-step workflows
- Creative use cases

## Getting Started

1. **Fork the repository**
2. **Create a branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

## Guidelines

### Code Style

**Python:**

- Use Black for formatting: `black .`
- Follow PEP 8
- Type hints where helpful
- Docstrings for functions

**JavaScript/TypeScript:**

- Use Prettier for formatting
- ESLint for linting
- Clear function names

### Documentation

- Use clear, simple language
- Include code examples
- Add screenshots when helpful
- Test all commands/instructions

### MCP Servers

New servers should include:

```file-tree
examples/your-server/
├── server.py (or server.js)
├── README.md
├── requirements.txt (or package.json)
├── config-example.json
└── test_prompts.md
```

**README.md should include:**

- What the server does
- Installation steps
- Configuration instructions
- Example prompts
- Troubleshooting tips

### Tutorials

Follow this structure:

```markdown
# Tutorial Title

**Time**: X minutes
**Difficulty**: Beginner/Intermediate/Advanced
**Prerequisites**: What you need to know

## What You'll Learn
- Bullet point 1
- Bullet point 2

## Step-by-step Instructions
...

## What's Next?
Link to related content
```

### Datasets

Include:

- Generation script (Python preferred)
- README explaining the data
- Sample queries/analyses
- Data dictionary (column descriptions)

Keep datasets:

- Synthetic (no real personal data)
- Reasonably sized (<100MB)
- Realistic and useful

## Pull Request Process

1. **Describe your changes**
   - What does this add/fix?
   - Why is it useful?
   - Any breaking changes?

2. **Checklist**
   - [ ] Code tested locally
   - [ ] Documentation updated
   - [ ] Examples work as described
   - [ ] No sensitive data included

3. **Review process**
   - Maintainers will review within a few days
   - Address feedback
   - Once approved, it'll be merged!

## Code of Conduct

### Our Standards

- ✅ Be respectful and inclusive
- ✅ Welcome newcomers
- ✅ Accept constructive criticism
- ✅ Focus on what's best for learners

### Not Acceptable

- ❌ Harassment or discrimination
- ❌ Trolling or insulting comments
- ❌ Publishing others' private information
- ❌ Unethical or illegal content

## Questions?

- Open an issue for questions
- Tag it with "question"
- Be specific about what you need help with

## Recognition

Contributors will be:

- Listed in the project README
- Credited in release notes
- Mentioned in related documentation

Thank you for helping make MCP accessible to everyone! 🙏

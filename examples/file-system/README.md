# File System MCP Server

A safe, sandboxed file system server that lets Claude read, write, and manage files in a designated workspace.

## Features

- 📄 Read and write files
- 📁 List directory contents
- 🔍 Search files by name or content
- 🗑️ Delete files
- 🔒 Sandboxed to a safe directory

## Safety Features

All operations are restricted to: `~/Documents/claude-workspace/`

This prevents accidental access to sensitive system files.

## Installation

```bash
# Install UV (Python package manager)
# Mac/Linux:
brew install uv
# Or visit: https://github.com/astral-sh/uv

# Install dependencies with UV
uv pip install -r requirements.txt

# OR for Node.js examples
npm install

# Test the server
python server.py
```

## Configuration

Add to your Claude Desktop config:

**Mac/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "python",
      "args": ["/absolute/path/to/examples/file-system/server.py"]
    }
  }
}
```

## Example Prompts

### Basic File Operations

Create a file called "notes.txt" with:

- Meeting at 2pm
- Call John tomorrow
- Review Q4 report

Read the contents of notes.txt

Add "Prepare presentation" to notes.txt

### Working with Multiple Files

Create three files:

1. todo.txt - my daily tasks
2. ideas.txt - project ideas
3. contacts.txt - important contacts

Add some sample content to each.

List all files in my workspace

### Searching

Search for files containing the word "meeting"

Find all .txt files

### Organization

Read all my .txt files and create a summary.md file with:

- Total number of tasks
- Important deadlines
- Key contacts

### Note Taking

I want to keep a daily journal. Create today's entry with:

- What I accomplished
- What I'm working on tomorrow
- Any blockers

### Content Analysis

Read all markdown files and create an index.md listing:

- File name
- First line (title)
- Last modified date

## Use Cases

### 1. Personal Knowledge Base

Store and organize notes, ideas, and information.

**Workflow**:

- Create topic-based files
- Search across all notes
- Generate summaries

### 2. Task Management

Maintain todo lists and project notes.

**Workflow**:

- Daily task files
- Project documentation
- Progress tracking

### 3. Research Notes

Collect and organize research findings.

**Workflow**:

- Create topic files
- Add sources and notes
- Generate synthesis documents

### 4. Writing Projects

Draft and organize written content.

**Workflow**:

- Chapter/section files
- Outline and notes
- Revision tracking

### 5. Learning Journal

Document learning progress.

**Workflow**:

- Daily learning logs
- Code snippets
- Resources and references

## Advanced Patterns

### Template System

Create a template file "daily-log-template.txt" with sections:

```text
- Date: 
- Goals:
- Progress:
- Notes:
- Tomorrow:
```

Then create today's log from this template.

### Backup System

Create a backup folder and copy all my .txt files there
with today's date in the filename.

### Content Processing

Read all my notes and:

1. Extract all todo items (lines starting with "- [ ]")
2. Create a master-todo.txt with all tasks
3. Organize by priority if mentioned

## Tips for Best Results

### 1. Use Relative Paths

✅ "notes/meeting.txt"
❌ "/Users/you/Documents/claude-workspace/notes/meeting.txt"

### 2. Organize with Folders

Create structure:
notes/
  work/
  personal/
  projects/

### 3. Name Files Descriptively

✅ "2024-01-15-meeting-notes.txt"
❌ "notes.txt"

### 4. Use Consistent Formats

For tasks: `- [ ] Task description`
For dates: `YYYY-MM-DD format`
For tags: `#tag-name`

### 5. Regular Cleanup

List all files older than 30 days and help me decide
what to keep or delete.

## Troubleshooting

### "Path outside workspace"

- All paths must be relative to the workspace
- Don't use `..` to go up directories

### "File not found"

- Check the exact filename (case-sensitive)
- Use `list_files` to see what exists

### "Permission denied"

- Check file permissions
- Ensure workspace directory is writable

## Limitations

- Only works with text files
- Maximum file size: system dependent
- No binary file support
- Restricted to workspace directory

## Extending This Server

Ideas for enhancements:

1. **Version Control** - Save file history
2. **Templates** - Pre-defined file templates
3. **Backups** - Automatic backup system
4. **Tags** - Tag-based organization
5. **Encryption** - Encrypt sensitive files

## Security Notes

- All operations are sandboxed
- No access to system files
- No execution of arbitrary code
- Read-only for system directories

## Example Workflows

### Morning Routine

1. Create today's date file (YYYY-MM-DD.txt)
2. Add my goals for the day
3. Review yesterday's notes
4. Create action items

### Project Documentation

1. Create project folder
2. Add README.md with overview
3. Create task list
4. Add meeting notes
5. Track progress in log file

### Research Organization

1. Create topic file
2. Add sources and notes
3. Tag key concepts
4. Generate summary
5. Create citations list

## Support

If you encounter issues:

1. Check the workspace directory exists
2. Verify file paths are relative
3. Ensure files are text-based
4. Review logs for errors

## Related Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [File System Best Practices](../../tutorials/)
- [Effective Prompts Guide](../../prompts/effective-prompts.md)

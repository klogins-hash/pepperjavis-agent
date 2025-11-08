# Pepper Potts AI Chief of Staff & JARVIS Agent

A comprehensive AI agent system built with Strands Agents framework - your personal Chief of Staff and JARVIS assistant combined into one intelligent system.

## Project Overview

This project consolidates all core Strands Agents repositories to build a powerful, multi-capability AI assistant platform for:
- **Chief of Staff Functions**: Calendar management, scheduling, reminders, priority management
- **JARVIS Functions**: Information retrieval, task automation, smart assistants, workflow management
- **Custom Capabilities**: Extensible tool system for specialized operations

## Repository Structure

```
strands-agent-project/
├── sdk-python/              # Core Strands Agents SDK (Python)
├── tools/                   # Pre-built tools for agents
├── samples/                 # Example implementations
├── agent-builder/           # Interactive agent builder UI
├── mcp-server/              # Model Context Protocol server
├── docs/                    # Complete documentation
├── pepperjavis/             # Main application (to be created)
└── README.md               # This file
```

### Cloned Repositories

#### 1. **sdk-python** - Core Framework
- Model-driven approach to building AI agents
- Multi-model provider support (Bedrock, OpenAI, Anthropic, etc.)
- Built-in MCP protocol support
- Streaming and async capabilities
- **Path**: `./sdk-python`

#### 2. **tools** - Tool Library
- Pre-built tools (web search, file operations, etc.)
- Easy tool creation with Python decorators
- Hot-reloading from directories
- **Path**: `./tools`

#### 3. **samples** - Example Implementations
- Complete working examples
- Best practices and patterns
- Reference implementations
- **Path**: `./samples`

#### 4. **agent-builder** - Interactive UI
- Visual agent building tool
- Streaming, tool use, and interactivity demos
- Development assistance
- **Path**: `./agent-builder`

#### 5. **mcp-server** - Protocol Support
- Model Context Protocol (MCP) server integration
- Documentation and context management
- Tool discovery and integration
- **Path**: `./mcp-server`

#### 6. **docs** - Documentation
- Complete user guide
- API reference
- Deployment guides
- Architecture documentation
- **Path**: `./docs`

## Quick Start

### Prerequisites
- Python 3.10+
- pip/poetry for package management
- AWS credentials (for Bedrock) or API keys for your preferred LLM provider

### Installation

```bash
# Navigate to project
cd /Users/franksimpson/Desktop/strands-agent-project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Strands Agents and tools
pip install strands-agents strands-agents-tools

# Optional: Install additional dependencies
pip install -r requirements.txt  # When created
```

### Creating Your First Agent

```python
from strands import Agent
from strands_tools import calculator, web_search

# Create a simple agent
agent = Agent(
    tools=[calculator, web_search],
    instructions="You are Pepper Potts, Tony Stark's trusted chief of staff AI."
)

# Use the agent
response = agent("What time should I schedule the board meeting tomorrow?")
print(response)
```

## Architecture Plan

### Phase 1: Foundation (Current)
- ✅ Clone all repositories
- ✅ Understand SDK structure
- Create project structure
- Set up basic agent template

### Phase 2: Core Features
- Multi-model provider setup
- Tool integration and extension
- Calendar/scheduling support
- Task management system

### Phase 3: Chief of Staff Functions
- Meeting coordination
- Priority management
- Executive briefing generation
- Calendar optimization

### Phase 4: JARVIS Functions
- Natural language task execution
- Smart automation
- Information synthesis
- Cross-system integration

### Phase 5: Advanced Features
- Multi-agent orchestration
- Autonomous workflow execution
- Context persistence
- Learning and adaptation

### Phase 6: Deployment
- Production configuration
- Monitoring and logging
- Security hardening
- Cloud deployment

## Key Features

### 1. Multi-Model Support
- Amazon Bedrock (Claude Sonnet, Nova)
- OpenAI (GPT-4, GPT-4o)
- Anthropic (Claude)
- Google Gemini
- Local models (Ollama, LlamaCpp)
- Custom providers

### 2. Advanced Capabilities
- Streaming responses
- Async operations
- Multi-agent systems
- Tool composition
- MCP protocol support

### 3. Built-in Tools
- Web search and information retrieval
- Calculator for numeric operations
- File operations
- Email/communication stubs
- Calendar integration hooks

### 4. Extensibility
- Custom tool creation with decorators
- Directory-based tool loading
- MCP server integration
- Custom model providers

## Development Workflow

### Creating Custom Tools

```python
from strands import tool

@tool
def send_meeting_invite(
    attendees: list[str],
    date: str,
    time: str,
    title: str
) -> str:
    """Schedule and send meeting invites to specified attendees.

    The attendees should be email addresses. Date should be YYYY-MM-DD format.
    Time should be HH:MM in 24-hour format.
    """
    # Implementation here
    return f"Meeting '{title}' scheduled for {date} at {time} with {len(attendees)} attendees"

# Use in agent
agent = Agent(tools=[send_meeting_invite])
```

### Hot Reloading Tools

```python
# Create a tools/ directory with Python files
# Each file can contain @tool decorated functions
# The agent will automatically load and reload them

agent = Agent(load_tools_from_directory=True)
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Model Provider Configuration
STRANDS_MODEL_PROVIDER=bedrock  # or openai, anthropic, gemini, etc.
STRANDS_MODEL_ID=us.amazon-nova-pro-v1:0

# AWS Credentials (for Bedrock)
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# OpenAI (if using OpenAI)
OPENAI_API_KEY=your_key

# Anthropic (if using Anthropic)
ANTHROPIC_API_KEY=your_key

# Gemini (if using Gemini)
GEMINI_API_KEY=your_key

# Logging
LOG_LEVEL=INFO
```

## Testing

```bash
# Run agent tests
pytest tests/

# Test individual tools
python -m pytest tests/tools/

# Integration tests
python -m pytest tests/integration/
```

## Documentation References

- [Strands Agents Official Docs](https://strandsagents.com/)
- [SDK API Reference](./docs/api-reference)
- [Examples](./samples)
- [Tool Development Guide](./tools/README.md)

## Next Steps

1. **Review Examples**: Check `./samples` for reference implementations
2. **Explore Tools**: Examine `./tools` for available tools and patterns
3. **Read Documentation**: Start with `./docs/user-guide/quickstart`
4. **Create Main Agent**: Build `pepperjavis/main.py` with your configuration
5. **Extend Tools**: Add custom tools for your specific needs
6. **Test Integration**: Validate multi-tool workflows

## Common Use Cases

### Executive Scheduling
```python
from strands import Agent
from custom_tools import calendar_manager, email_notifier

agent = Agent(
    tools=[calendar_manager, email_notifier],
    instructions="You are an executive scheduling assistant. Optimize calendars and send professional notifications."
)
```

### Information Synthesis
```python
from strands import Agent
from strands_tools import web_search
from custom_tools import document_summarizer

agent = Agent(
    tools=[web_search, document_summarizer],
    instructions="Research topics and provide comprehensive, well-sourced summaries."
)
```

### Workflow Automation
```python
from strands import Agent
from custom_tools import file_processor, email_sender, task_manager

agent = Agent(
    tools=[file_processor, email_sender, task_manager],
    instructions="Automate routine workflows and send status updates."
)
```

## Production Deployment

For production deployment and monitoring, refer to:
- [Production Guide](./docs/user-guide/deploy/operating-agents-in-production/)
- Security best practices
- Monitoring and logging setup
- Error handling and recovery

## Support & Contributing

- [Contributing Guide](./SDK-PYTHON/CONTRIBUTING.md)
- Report issues on GitHub
- Join community discussions
- Submit feature requests

## License

This project uses components from Strands Agents which is licensed under Apache License 2.0. See individual repositories for specific license information.

---

**Ready to build your AI assistant?** Start with the Quick Start section above, explore the samples, and customize for your needs!

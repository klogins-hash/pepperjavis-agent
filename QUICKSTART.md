# PepperJarvis Agent - Quick Start Guide

Welcome to your Pepper Potts AI Chief of Staff & JARVIS Agent! This guide will get you up and running in minutes.

## Prerequisites

- Python 3.10 or higher
- pip or poetry
- API keys for your preferred LLM provider (optional - defaults to AWS Bedrock)

## Installation

### 1. Navigate to the project directory

```bash
cd /Users/franksimpson/Desktop/strands-agent-project
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# OR for development with all extras
pip install -e ".[dev,providers,full]"
```

### 4. Set up configuration (Optional)

Create a `.env` file in the project root for customization:

```bash
# Model Provider Configuration
STRANDS_MODEL_PROVIDER=bedrock  # or: openai, anthropic, gemini, ollama
STRANDS_MODEL_ID=us.amazon.nova-pro-v1:0
TEMPERATURE=0.7

# For OpenAI
# OPENAI_API_KEY=your_key_here

# For Anthropic
# ANTHROPIC_API_KEY=your_key_here

# For Google Gemini
# GEMINI_API_KEY=your_key_here

# AWS Configuration (for Bedrock)
AWS_REGION=us-west-2
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret

# Logging
LOG_LEVEL=INFO
```

## Usage

### Interactive Mode (Default)

Start chatting with PepperJarvis:

```bash
python main.py
```

Commands in interactive mode:
- Type your request and press Enter
- `help` - Show available commands
- `capabilities` - Show agent capabilities
- `quit` or `exit` - End the conversation

### Demo Mode

See PepperJarvis in action with predefined scenarios:

```bash
python main.py demo
```

This demonstrates:
- Telling the current time
- Prioritizing tasks
- Scheduling meetings
- Creating reminders
- Researching topics

### Test Mode

Run basic tests on the agent:

```bash
python main.py test
```

## Example Conversations

### Example 1: Task Prioritization

```
You: I have tasks: 'Complete quarterly report', 'Review budget', 'Send client proposal'. Please prioritize them.

PepperJarvis: I'll help you prioritize these tasks. Based on typical business impact and urgency:

1. Complete quarterly report - This is likely time-sensitive and organization-critical
2. Send client proposal - Client-facing and impacts revenue/relationships
3. Review budget - Important but can typically be scheduled around client-critical items

Would you like me to create reminders for each task?
```

### Example 2: Meeting Scheduling

```
You: Help me schedule a meeting with alice@example.com, bob@example.com for tomorrow at 2 PM for 1 hour about Q4 planning.

PepperJarvis: Meeting scheduled:
Title: Q4 Planning
Date: [Tomorrow's date]
Time: 14:00 - 15:00
Duration: 60 minutes
Attendees: alice@example.com, bob@example.com
Status: Confirmation pending

I can also send them notification emails if you'd like.
```

### Example 3: Executive Briefing

```
You: Create a daily briefing on our AI initiatives, market trends, and team updates.

PepperJarvis: Executive Daily Briefing
Generated: [Current date and time]

1. AI Initiatives
   - Status: In progress
   - Key metrics: TBD
   - Action items: TBD

2. Market Trends
   - Status: In progress
   - Key metrics: TBD
   - Action items: TBD

3. Team Updates
   - Status: In progress
   - Key metrics: TBD
   - Action items: TBD
```

## Project Structure

```
strands-agent-project/
├── sdk-python/                 # Strands Agents SDK
├── tools/                      # Pre-built tools library
├── samples/                    # Example implementations
├── agent-builder/              # Interactive UI builder
├── mcp-server/                 # MCP protocol support
├── docs/                       # Full documentation
├── pepperjavis/               # Main agent package
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Configuration management
│   ├── agent.py              # Main agent implementation
│   └── tools.py              # Custom tools
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Project configuration
├── README.md                 # Comprehensive documentation
└── QUICKSTART.md             # This file
```

## Available Tools

### Chief of Staff Tools
- **Schedule Meeting** - Coordinate meetings with attendees
- **Send Notification** - Send notifications to recipients
- **Create Reminder** - Set up reminders for tasks
- **Analyze Schedule** - Optimize calendar and meeting times
- **Extract Action Items** - Pull action items from meeting notes

### JARVIS/Assistant Tools
- **Research Topic** - Research topics and provide summaries
- **Create Briefing** - Generate executive briefings
- **Prioritize Tasks** - Rank tasks by importance/urgency
- **Get Current Time** - Check current date and time
- **Built-in Tools** - Calculator, web search (when available)

## Customization

### Using a Different LLM Provider

```python
from pepperjavis import PepperJarvisAgent, AgentConfig

# Use OpenAI
config = AgentConfig(
    model_provider="openai",
    model_id="gpt-4o",
    openai_api_key="your_key_here",
    temperature=0.7
)
agent = PepperJarvisAgent(config=config)

# Or use Anthropic
config = AgentConfig(
    model_provider="anthropic",
    model_id="claude-3-5-sonnet-20241022",
    anthropic_api_key="your_key_here"
)
agent = PepperJarvisAgent(config=config)
```

### Custom Personality

```python
from pepperjavis import AgentConfig, PepperJarvisAgent

custom_personality = """You are Tony Stark's personal AI assistant, enhanced with executive
scheduling capabilities. You're professional, witty, and efficient. You anticipate needs
and provide strategic insights."""

config = AgentConfig(
    agent_personality=custom_personality
)
agent = PepperJarvisAgent(config=config)
```

### Adding Custom Tools

Edit `pepperjavis/tools.py` and add your tools using the `@tool` decorator:

```python
from strands import tool

@tool
def my_custom_tool(parameter: str) -> str:
    """Tool description for the AI to understand."""
    # Implementation
    return f"Result: {parameter}"
```

## Building Programmatically

Instead of using the CLI, embed PepperJarvis in your application:

```python
from pepperjavis import PepperJarvisAgent, AgentConfig

# Create agent
agent = PepperJarvisAgent()

# Use the agent
response = agent("What tasks should I prioritize today?")
print(response)

# Get capabilities
capabilities = agent.get_capabilities()
print(capabilities)
```

## Troubleshooting

### Import Errors

If you get import errors, ensure you're in the virtual environment:

```bash
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

### Model Provider Errors

Ensure your API keys are set correctly in `.env` or as environment variables.

For Bedrock:
```bash
aws configure
```

For OpenAI:
```bash
export OPENAI_API_KEY=your_key
```

### Tool Loading Errors

If tools aren't loading:
1. Check that `pepperjavis/tools.py` exists
2. Verify Python version is 3.10+
3. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

## Next Steps

1. **Explore Examples**: Check the `samples/` directory for advanced patterns
2. **Read Documentation**: Start with `docs/user-guide/quickstart/`
3. **Customize Tools**: Add your own tools to `pepperjavis/tools.py`
4. **Integrate APIs**: Connect to your calendar, email, task management systems
5. **Deploy**: Follow deployment guide in `docs/user-guide/deploy/`

## Resources

- [Strands Agents Documentation](https://strandsagents.com/)
- [Python SDK Docs](./sdk-python/README.md)
- [Tools Library](./tools/README.md)
- [Examples](./samples/)
- [API Reference](./docs)

## Support

- Check the main [README.md](./README.md)
- Review example implementations in `samples/`
- Check [Strands Agents docs](https://strandsagents.com/)
- Examine your agent logs for errors

## Tips for Best Results

1. **Be Specific**: The more details you provide, the better the results
2. **Use Natural Language**: Write requests as you would speak them
3. **Set Personality**: Customize the agent personality for your use case
4. **Enable Appropriate Tools**: Only enable tools you actually need
5. **Monitor Logs**: Watch `LOG_LEVEL=DEBUG` for detailed information

---

**Ready to boost your productivity with PepperJarvis?** Start with `python main.py` and begin delegating!

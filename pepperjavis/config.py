"""
Configuration management for the PepperJarvis Agent.
"""

from typing import Optional, Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class AgentConfig(BaseSettings):
    """Agent configuration settings."""

    # Agent Identity
    agent_name: str = Field(default="PepperJarvis", description="Name of the agent")
    agent_role: str = Field(
        default="Chief of Staff and Executive Assistant",
        description="Agent's primary role"
    )
    agent_personality: str = Field(
        default="""You are Pepper Potts, an intelligent executive assistant and chief of staff AI.
You combine the organizational prowess of Pepper Potts with JARVIS's technical capabilities.
You excel at:
- Executive scheduling and meeting coordination
- Task prioritization and management
- Information retrieval and synthesis
- Workflow automation
- Professional communication
- Strategic planning assistance

Always maintain professional demeanor, think strategically, and anticipate user needs.""",
        description="System prompt defining agent personality and behavior"
    )

    # Model Configuration
    model_provider: Literal[
        "bedrock",
        "openai",
        "anthropic",
        "gemini",
        "ollama",
        "llamacpp",
        "llamaapi"
    ] = Field(default="bedrock", description="LLM provider")

    model_id: Optional[str] = Field(
        default="us.amazon.nova-pro-v1:0",
        description="Model ID for the selected provider"
    )

    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Model temperature for creativity vs consistency"
    )

    max_tokens: Optional[int] = Field(
        default=4096,
        description="Maximum tokens in response"
    )

    streaming: bool = Field(
        default=True,
        description="Enable streaming responses"
    )

    # AWS Configuration (for Bedrock)
    aws_region: str = Field(
        default="us-west-2",
        description="AWS region for Bedrock"
    )

    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )

    # Anthropic Configuration
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key"
    )

    # Gemini Configuration
    gemini_api_key: Optional[str] = Field(
        default=None,
        description="Gemini API key"
    )

    # Tool Configuration
    enable_web_search: bool = Field(
        default=True,
        description="Enable web search capability"
    )

    enable_calculator: bool = Field(
        default=True,
        description="Enable calculator tool"
    )

    load_tools_from_directory: bool = Field(
        default=False,
        description="Auto-load tools from tools/ directory"
    )

    tools_directory: str = Field(
        default="./tools",
        description="Directory to load tools from"
    )

    # MCP Configuration
    enable_mcp: bool = Field(
        default=False,
        description="Enable Model Context Protocol integration"
    )

    mcp_servers: list[dict] = Field(
        default_factory=list,
        description="MCP server configurations"
    )

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )

    log_file: Optional[str] = Field(
        default=None,
        description="Log file path (None for console only)"
    )

    # System Configuration
    max_tool_calls: int = Field(
        default=10,
        description="Maximum number of tool calls per request"
    )

    timeout_seconds: int = Field(
        default=30,
        description="Timeout for tool execution"
    )

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def get_system_prompt(self) -> str:
        """Get the complete system prompt."""
        return self.agent_personality


class ToolConfig:
    """Configuration for tools."""

    @staticmethod
    def get_default_tools() -> list[str]:
        """Get list of default tool names to enable."""
        return [
            "calculator",
            "web_search",
            "file_operations",
        ]

    @staticmethod
    def get_chief_of_staff_tools() -> list[str]:
        """Get tools for Chief of Staff functionality."""
        return [
            "calendar_manager",
            "meeting_coordinator",
            "task_manager",
            "email_notifier",
            "reminder_system",
        ]

    @staticmethod
    def get_jarvis_tools() -> list[str]:
        """Get tools for JARVIS functionality."""
        return [
            "web_search",
            "information_retriever",
            "code_executor",
            "document_processor",
            "knowledge_assistant",
        ]

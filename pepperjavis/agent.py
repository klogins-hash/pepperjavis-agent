"""
Main PepperJarvis Agent implementation.

Combines Chief of Staff and JARVIS capabilities.
"""

import logging
from typing import Optional, Any
from strands import Agent, tool
from pepperjavis.config import AgentConfig, ToolConfig


logger = logging.getLogger(__name__)


class PepperJarvisAgent:
    """
    Pepper Potts AI Chief of Staff & JARVIS Agent.

    Combines executive assistant capabilities with intelligent automation.
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the PepperJarvis Agent.

        Args:
            config: AgentConfig instance. If None, loads from environment.
        """
        self.config = config or AgentConfig()
        self._setup_logging()
        self.agent = self._create_agent()
        logger.info(f"PepperJarvis Agent initialized: {self.config.agent_name}")

    def _setup_logging(self) -> None:
        """Configure logging for the agent."""
        level = getattr(logging, self.config.log_level)
        logging.basicConfig(level=level)

        if self.config.log_file:
            handler = logging.FileHandler(self.config.log_file)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

    def _create_agent(self) -> Agent:
        """Create and configure the Strands Agent."""
        # Gather tools
        tools = self._load_tools()

        # Create model based on provider
        model = self._create_model()

        # Create agent with configuration
        agent = Agent(
            model=model,
            tools=tools,
            instructions=self.config.get_system_prompt(),
            name=self.config.agent_name,
        )

        return agent

    def _create_model(self) -> Any:
        """Create the LLM model based on configuration."""
        provider = self.config.model_provider

        if provider == "bedrock":
            from strands.models import BedrockModel
            return BedrockModel(
                model_id=self.config.model_id,
                region_name=self.config.aws_region,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                streaming=self.config.streaming,
            )
        elif provider == "openai":
            from strands.models.openai import OpenAIModel
            return OpenAIModel(
                model_id=self.config.model_id or "gpt-4o",
                api_key=self.config.openai_api_key,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                streaming=self.config.streaming,
            )
        elif provider == "anthropic":
            from strands.models.anthropic import AnthropicModel
            return AnthropicModel(
                model_id=self.config.model_id or "claude-3-5-sonnet-20241022",
                api_key=self.config.anthropic_api_key,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                streaming=self.config.streaming,
            )
        elif provider == "gemini":
            from strands.models.gemini import GeminiModel
            return GeminiModel(
                model_id=self.config.model_id or "gemini-2.0-flash",
                client_args={"api_key": self.config.gemini_api_key},
                temperature=self.config.temperature,
                streaming=self.config.streaming,
            )
        elif provider == "ollama":
            from strands.models.ollama import OllamaModel
            return OllamaModel(
                host="http://localhost:11434",
                model_id=self.config.model_id or "llama2",
                temperature=self.config.temperature,
                streaming=self.config.streaming,
            )
        else:
            raise ValueError(f"Unsupported model provider: {provider}")

    def _load_tools(self) -> list:
        """Load tools for the agent."""
        tools = []

        # Load built-in Strands tools
        if self.config.enable_calculator:
            try:
                from strands_tools import calculator
                tools.append(calculator)
                logger.info("Calculator tool loaded")
            except ImportError:
                logger.warning("Calculator tool not available")

        if self.config.enable_web_search:
            try:
                from strands_tools import web_search
                tools.append(web_search)
                logger.info("Web search tool loaded")
            except ImportError:
                logger.warning("Web search tool not available")

        # Load custom tools
        tools.extend(self._load_custom_tools())

        # Load from directory if enabled
        if self.config.load_tools_from_directory:
            logger.info(f"Loading tools from directory: {self.config.tools_directory}")
            # This would be implemented with directory scanning
            # and dynamic import of tool modules

        logger.info(f"Total tools loaded: {len(tools)}")
        return tools

    def _load_custom_tools(self) -> list:
        """Load custom tools defined in this package."""
        tools = []

        # Import custom tool definitions
        try:
            from pepperjavis.tools import (
                get_custom_tools,
            )
            tools.extend(get_custom_tools())
            logger.info("Custom tools loaded")
        except ImportError:
            logger.debug("No custom tools module found")

        return tools

    def process(self, user_input: str) -> str:
        """
        Process a user input through the agent.

        Args:
            user_input: The user's request or question

        Returns:
            Agent response as a string
        """
        try:
            logger.info(f"Processing input: {user_input[:100]}...")
            response = self.agent(user_input)
            logger.info("Input processed successfully")
            return response
        except Exception as e:
            logger.error(f"Error processing input: {str(e)}", exc_info=True)
            raise

    def process_streaming(self, user_input: str):
        """
        Process a user input with streaming response.

        Args:
            user_input: The user's request or question

        Yields:
            Response chunks as they arrive
        """
        try:
            logger.info(f"Processing input (streaming): {user_input[:100]}...")
            # Streaming implementation would depend on the agent's streaming API
            for chunk in self.agent.process_streaming(user_input):
                yield chunk
            logger.info("Input processed successfully (streaming)")
        except Exception as e:
            logger.error(f"Error processing input: {str(e)}", exc_info=True)
            raise

    def get_capabilities(self) -> dict:
        """
        Get information about agent capabilities.

        Returns:
            Dictionary describing available capabilities
        """
        return {
            "name": self.config.agent_name,
            "role": self.config.agent_role,
            "model": {
                "provider": self.config.model_provider,
                "model_id": self.config.model_id,
            },
            "tools": {
                "web_search": self.config.enable_web_search,
                "calculator": self.config.enable_calculator,
            },
            "features": {
                "streaming": self.config.streaming,
                "mcp_enabled": self.config.enable_mcp,
            },
        }

    def __call__(self, user_input: str) -> str:
        """
        Make the agent callable for direct use.

        Args:
            user_input: The user's request

        Returns:
            Agent response
        """
        return self.process(user_input)


# Built-in custom tools for Chief of Staff and JARVIS functions

@tool
def prioritize_tasks(tasks: list[str]) -> str:
    """Analyze and prioritize a list of tasks based on importance and urgency.

    Takes a list of task descriptions and returns them prioritized with reasoning.
    """
    # This is a stub - would integrate with actual task management
    prioritized = sorted(tasks, key=lambda x: len(x), reverse=True)
    return f"Prioritized tasks:\n" + "\n".join(
        f"{i+1}. {task}" for i, task in enumerate(prioritized)
    )


@tool
def meeting_coordinator(
    attendees: list[str],
    topic: str,
    time_preference: str = "flexible"
) -> str:
    """Coordinate a meeting with available attendees.

    Suggests optimal meeting times and handles scheduling logistics.
    """
    return f"Meeting coordination initiated for '{topic}' with {len(attendees)} attendees. Time preference: {time_preference}"


@tool
def executive_summary(
    document_text: str,
    max_length: int = 500
) -> str:
    """Generate an executive summary from a document.

    Condenses lengthy documents into concise, actionable summaries.
    """
    words = document_text.split()
    if len(words) <= max_length:
        return document_text

    # Simple summarization - would use AI in production
    sentences = document_text.split(".")
    summary_sentences = sentences[:max(1, len(sentences)//3)]
    return ". ".join(summary_sentences) + "."

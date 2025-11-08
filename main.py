#!/usr/bin/env python3
"""
Main entry point for PepperJarvis Agent.

This script demonstrates how to use the Pepper Potts AI Chief of Staff & JARVIS Agent.
"""

import sys
import logging
from pathlib import Path

# Add the project to the path
sys.path.insert(0, str(Path(__file__).parent))

from pepperjavis import PepperJarvisAgent, AgentConfig


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def interactive_mode(agent: PepperJarvisAgent):
    """Run agent in interactive chat mode."""
    print("\n" + "="*60)
    print("🤖 PepperJarvis Agent - Interactive Mode")
    print("="*60)
    print(f"Agent: {agent.config.agent_name}")
    print(f"Role: {agent.config.agent_role}")
    print(f"Model: {agent.config.model_provider} - {agent.config.model_id}")
    print("\nType 'quit' or 'exit' to end the conversation")
    print("Type 'help' for available commands")
    print("="*60 + "\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit']:
                print("\nPepperJarvis: Goodbye! It was a pleasure assisting you.")
                break

            if user_input.lower() == 'help':
                print_help()
                continue

            if user_input.lower() == 'capabilities':
                print_capabilities(agent)
                continue

            print("\nPepperJarvis: ", end="", flush=True)
            response = agent(user_input)
            print(response)
            print()

        except KeyboardInterrupt:
            print("\n\nPepperJarvis: Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            logging.exception("Error processing input")
            print()


def demo_mode(agent: PepperJarvisAgent):
    """Run agent in demo mode with predefined scenarios."""
    print("\n" + "="*60)
    print("🤖 PepperJarvis Agent - Demo Mode")
    print("="*60)
    print(f"Agent: {agent.config.agent_name}")
    print(f"Demonstrating Chief of Staff and JARVIS capabilities\n")

    # Demo scenarios
    demo_scenarios = [
        "What is the current time?",
        "I have tasks: 'Complete quarterly report', 'Review budget', 'Send client proposal'. Please prioritize them.",
        "Help me schedule a meeting with alice@example.com, bob@example.com, and carol@example.com for tomorrow at 2 PM for 1 hour about Q4 planning.",
        "Create a reminder for me to follow up on the Johnson project by Friday at 5 PM.",
        "Research the latest AI trends and create a brief summary.",
    ]

    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"\n{'─'*60}")
        print(f"Demo {i}/{len(demo_scenarios)}: {scenario}\n")
        print("You: " + scenario)
        print("\nPepperJarvis: ", end="", flush=True)

        try:
            response = agent(scenario)
            print(response)
        except Exception as e:
            print(f"Error: {str(e)}")
            logging.exception("Error in demo scenario")

    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60)


def print_help():
    """Print available commands."""
    help_text = """
Available Commands:
  quit, exit      - Exit the agent
  help            - Show this help message
  capabilities    - Show agent capabilities

Tips:
  - Ask the agent to schedule meetings
  - Request task prioritization
  - Ask for research summaries
  - Request executive briefings
  - Create reminders and notifications
  - Analyze your schedule
    """
    print(help_text)


def print_capabilities(agent: PepperJarvisAgent):
    """Print agent capabilities."""
    capabilities = agent.get_capabilities()
    print("\n" + "="*40)
    print("🎯 Agent Capabilities")
    print("="*40)
    print(f"Name: {capabilities['name']}")
    print(f"Role: {capabilities['role']}")
    print(f"Model: {capabilities['model']['provider']} ({capabilities['model']['model_id']})")
    print(f"\nTools Available:")
    for tool, enabled in capabilities['tools'].items():
        status = "✓ Enabled" if enabled else "✗ Disabled"
        print(f"  - {tool}: {status}")
    print(f"\nFeatures:")
    for feature, enabled in capabilities['features'].items():
        status = "✓ Enabled" if enabled else "✗ Disabled"
        print(f"  - {feature}: {status}")
    print("="*40 + "\n")


def main():
    """Main entry point."""
    setup_logging()

    # Create agent with default configuration
    # You can pass a custom AgentConfig for different settings
    print("🚀 Initializing PepperJarvis Agent...")

    try:
        # Create agent with default config
        # To customize, create AgentConfig instance:
        # config = AgentConfig(
        #     model_provider="openai",
        #     model_id="gpt-4o",
        #     temperature=0.7,
        # )
        # agent = PepperJarvisAgent(config=config)

        agent = PepperJarvisAgent()
        print("✓ Agent initialized successfully!\n")

        if len(sys.argv) > 1:
            if sys.argv[1].lower() == 'demo':
                demo_mode(agent)
            elif sys.argv[1].lower() == 'test':
                test_agent(agent)
            else:
                print(f"Unknown command: {sys.argv[1]}")
                print("Usage: python main.py [demo|test]")
                interactive_mode(agent)
        else:
            interactive_mode(agent)

    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        logging.exception("Failed to initialize agent")
        sys.exit(1)


def test_agent(agent: PepperJarvisAgent):
    """Run basic tests on the agent."""
    print("\n" + "="*60)
    print("🧪 Agent Testing Mode")
    print("="*60 + "\n")

    test_cases = [
        ("What is your name and role?", "Identity"),
        ("What tools do you have available?", "Tools"),
        ("What is the current time?", "Current Time"),
    ]

    passed = 0
    failed = 0

    for test_input, test_name in test_cases:
        print(f"Test: {test_name}")
        print(f"Input: {test_input}")
        try:
            response = agent(test_input)
            if response and len(response) > 0:
                print(f"Result: ✓ PASSED")
                print(f"Response: {response[:100]}...\n")
                passed += 1
            else:
                print(f"Result: ✗ FAILED (Empty response)\n")
                failed += 1
        except Exception as e:
            print(f"Result: ✗ FAILED ({str(e)})\n")
            failed += 1

    print("="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60)


if __name__ == "__main__":
    main()

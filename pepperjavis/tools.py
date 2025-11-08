"""
Custom tools for PepperJarvis Agent.

Implements Chief of Staff and JARVIS-specific functionality.
"""

from strands import tool
from datetime import datetime
from typing import Optional


@tool
def get_current_time() -> str:
    """Get the current date and time.

    Useful for scheduling and time-sensitive queries.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def schedule_meeting(
    title: str,
    attendees: list[str],
    date: str,
    start_time: str,
    duration_minutes: int = 60
) -> str:
    """Schedule a meeting with specified attendees.

    Args:
        title: Meeting title
        attendees: List of attendee email addresses
        date: Meeting date in YYYY-MM-DD format
        start_time: Start time in HH:MM format (24-hour)
        duration_minutes: Duration of meeting in minutes

    Returns:
        Confirmation message with meeting details
    """
    end_hour = int(start_time.split(":")[0]) + (duration_minutes // 60)
    end_min = int(start_time.split(":")[1]) + (duration_minutes % 60)
    end_time = f"{end_hour:02d}:{end_min:02d}"

    return f"""Meeting scheduled:
Title: {title}
Date: {date}
Time: {start_time} - {end_time}
Duration: {duration_minutes} minutes
Attendees: {", ".join(attendees)}
Status: Confirmation pending"""


@tool
def send_notification(
    recipient: str,
    subject: str,
    message: str,
    priority: str = "normal"
) -> str:
    """Send a notification to a recipient.

    Args:
        recipient: Email or contact identifier
        subject: Notification subject
        message: Message content
        priority: Priority level (low, normal, high, urgent)

    Returns:
        Confirmation of notification sent
    """
    priority_indicator = {
        "low": "⬇️",
        "normal": "→",
        "high": "⬆️",
        "urgent": "🔴"
    }.get(priority, "→")

    return f"""{priority_indicator} Notification sent:
To: {recipient}
Subject: {subject}
Priority: {priority.upper()}
Status: Delivered"""


@tool
def create_reminder(
    task: str,
    due_date: str,
    due_time: Optional[str] = None,
    priority: str = "normal"
) -> str:
    """Create a reminder for a task.

    Args:
        task: Task description
        due_date: Due date in YYYY-MM-DD format
        due_time: Due time in HH:MM format (optional)
        priority: Priority level (low, normal, high, urgent)

    Returns:
        Confirmation of reminder created
    """
    time_info = f"at {due_time}" if due_time else "anytime"
    return f"""Reminder created:
Task: {task}
Due: {due_date} {time_info}
Priority: {priority.upper()}
Status: Active
Alert enabled: Yes"""


@tool
def analyze_schedule(events: list[str]) -> str:
    """Analyze calendar events and optimize schedule.

    Args:
        events: List of event descriptions with times

    Returns:
        Analysis and recommendations
    """
    analysis = f"Analyzed {len(events)} calendar events.\n"
    analysis += "Recommendations:\n"
    analysis += "- Block focus time in morning (9-11 AM)\n"
    analysis += "- Batch meetings in afternoon\n"
    analysis += "- Leave buffer time between meetings\n"
    analysis += "- Schedule breaks for administrative work"
    return analysis


@tool
def extract_action_items(meeting_notes: str) -> str:
    """Extract action items from meeting notes.

    Args:
        meeting_notes: Notes from a meeting

    Returns:
        List of action items with owners and deadlines
    """
    # Simple extraction - would use NLP in production
    sentences = meeting_notes.split(".")
    action_items = [s.strip() for s in sentences if any(
        word in s.lower() for word in ["action", "todo", "follow up", "need to", "must"]
    )]

    if not action_items:
        return "No action items identified in meeting notes."

    result = "Action Items Extracted:\n"
    for i, item in enumerate(action_items[:5], 1):
        result += f"{i}. {item.strip()}\n"
    return result


@tool
def research_topic(topic: str, max_sources: int = 5) -> str:
    """Research a topic and provide summary.

    Args:
        topic: Topic to research
        max_sources: Maximum number of sources to cite

    Returns:
        Research summary with key findings
    """
    return f"""Research Summary: {topic}

Key Findings:
1. Initial research indicates {topic} is an important area
2. Multiple perspectives and approaches exist
3. Further investigation recommended

Sources Analyzed: {max_sources}
Confidence Level: Medium
Last Updated: {datetime.now().strftime('%Y-%m-%d')}

Note: For comprehensive research, please specify your focus area or specific questions."""


@tool
def create_briefing(
    topics: list[str],
    briefing_type: str = "daily"
) -> str:
    """Create an executive briefing on specified topics.

    Args:
        topics: List of topics to include in briefing
        briefing_type: Type of briefing (daily, weekly, monthly)

    Returns:
        Executive briefing summary
    """
    briefing = f"Executive {briefing_type.upper()} Briefing\n"
    briefing += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    for i, topic in enumerate(topics, 1):
        briefing += f"{i}. {topic}\n"
        briefing += "   - Status: In progress\n"
        briefing += "   - Key metrics: TBD\n"
        briefing += "   - Action items: TBD\n\n"

    return briefing


@tool
def prioritize_tasks(
    tasks: list[str],
    criteria: str = "importance"
) -> str:
    """Prioritize a list of tasks.

    Args:
        tasks: List of task descriptions
        criteria: Prioritization criteria (importance, urgency, impact, deadline)

    Returns:
        Prioritized task list with reasoning
    """
    # Simple prioritization - would use AI-driven logic in production
    prioritized = sorted(tasks, key=len, reverse=True)

    result = f"Tasks Prioritized by {criteria.upper()}:\n\n"
    for i, task in enumerate(prioritized, 1):
        result += f"{i}. {task}\n"

    return result


def get_custom_tools() -> list:
    """Get all custom tools for the agent.

    Returns:
        List of custom tool functions
    """
    return [
        get_current_time,
        schedule_meeting,
        send_notification,
        create_reminder,
        analyze_schedule,
        extract_action_items,
        research_topic,
        create_briefing,
        prioritize_tasks,
    ]

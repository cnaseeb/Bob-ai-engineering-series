"""
Multi-agent orchestration framework.
"""

from .models import (
    AgentStatus,
    TaskStatus,
    AgentCapability,
    AgentMetadata,
    Task
)
from .agent_registry import AgentRegistry
from .context_store import SharedContextStore
from .message_bus import MessageBus
from .coordinator import WorkflowCoordinator
from .workflows import CustomerOnboardingWorkflow

__all__ = [
    'AgentStatus',
    'TaskStatus',
    'AgentCapability',
    'AgentMetadata',
    'Task',
    'AgentRegistry',
    'SharedContextStore',
    'MessageBus',
    'WorkflowCoordinator',
    'CustomerOnboardingWorkflow'
]

__version__ = '1.0.0'
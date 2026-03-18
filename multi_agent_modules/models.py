"""
Data models and enums for multi-agent orchestration.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

class AgentStatus(Enum):
    """Agent availability status."""
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AgentCapability:
    """Agent capability definition."""
    name: str
    version: str
    performance_score: float = 1.0
    cost_per_invocation: float = 0.01

@dataclass
class AgentMetadata:
    """Complete agent metadata."""
    agent_id: str
    agent_type: str
    capabilities: List[AgentCapability]
    status: AgentStatus = AgentStatus.AVAILABLE
    current_load: int = 0
    max_concurrent_tasks: int = 10
    average_response_time: float = 1.0
    success_rate: float = 1.0
    last_heartbeat: str = ""

@dataclass
class Task:
    """Task definition."""
    task_id: str
    agent_id: str
    action: str
    parameters: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None


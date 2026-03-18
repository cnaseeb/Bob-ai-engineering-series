"""
Agent registry for service discovery and selection.
"""

from typing import List, Dict, Optional
import logging
from .models import AgentMetadata, AgentStatus, AgentCapability

logger = logging.getLogger(__name__)

class AgentRegistry:
    """
    Service registry for agent discovery and selection.
    Manages agent metadata and provides selection algorithms.
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentMetadata] = {}
        logger.info("✓ AgentRegistry initialized")
    
    def register_agent(self, metadata: AgentMetadata):
        """Register new agent in the registry."""
        self.agents[metadata.agent_id] = metadata
        logger.info(f"✓ Registered agent: {metadata.agent_id}")
    
    def get_agent(self, agent_id: str) -> Optional[AgentMetadata]:
        """Get agent by ID."""
        return self.agents.get(agent_id)
    
    def find_by_capability(self, capability_name: str) -> List[AgentMetadata]:
        """Find all agents with specific capability."""
        return [
            agent for agent in self.agents.values()
            if any(cap.name == capability_name for cap in agent.capabilities)
            and agent.status == AgentStatus.AVAILABLE
        ]
    
    def select_best_agent(
        self, 
        capability: str, 
        criteria: str = 'performance'
    ) -> Optional[AgentMetadata]:
        """
        Select best agent based on criteria:
        - performance: highest success rate
        - cost: lowest cost
        - load: lowest current load
        - balanced: weighted combination
        """
        candidates = self.find_by_capability(capability)
        
        if not candidates:
            return None
        
        if criteria == 'performance':
            return max(candidates, key=lambda a: a.success_rate)
        elif criteria == 'cost':
            return min(
                candidates,
                key=lambda a: sum(c.cost_per_invocation for c in a.capabilities)
            )
        elif criteria == 'load':
            return min(
                candidates,
                key=lambda a: a.current_load / a.max_concurrent_tasks
            )
        else:  # balanced
            return max(candidates, key=lambda a: self._calculate_score(a))
    
    def _calculate_score(self, agent: AgentMetadata) -> float:
        """Calculate weighted score for agent selection."""
        performance_score = agent.success_rate * 0.4
        cost_score = (1 / sum(c.cost_per_invocation for c in agent.capabilities)) * 0.3
        load_score = (1 - agent.current_load / agent.max_concurrent_tasks) * 0.3
        return performance_score + cost_score + load_score
    
    def update_agent_status(self, agent_id: str, status: AgentStatus):
        """Update agent availability status."""
        if agent_id in self.agents:
            self.agents[agent_id].status = status
    
    def list_all_agents(self) -> List[AgentMetadata]:
        """Get list of all registered agents."""
        return list(self.agents.values())
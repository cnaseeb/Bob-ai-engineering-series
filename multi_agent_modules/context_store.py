"""
Shared context store for multi-agent workflows.
"""

from typing import Any, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SharedContextStore:
    """
    Shared context store for multi-agent workflows.
    In production, this would use Redis or similar.
    This is a simple in-memory implementation for testing.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.contexts: Dict[str, Dict[str, Any]] = {}
        self.redis_url = redis_url
        logger.info("✓ SharedContextStore initialized")
    
    def create_workflow_context(self, workflow_id: str):
        """Create new workflow context."""
        self.contexts[workflow_id] = {
            'created_at': datetime.utcnow().isoformat(),
            'data': {}
        }
        logger.info(f"✓ Created context for workflow: {workflow_id}")
    
    def set_context(self, workflow_id: str, key: str, value: Any):
        """Store context data for workflow."""
        if workflow_id not in self.contexts:
            self.create_workflow_context(workflow_id)
        self.contexts[workflow_id]['data'][key] = value
    
    def get_context(self, workflow_id: str, key: str) -> Optional[Any]:
        """Retrieve context data."""
        if workflow_id in self.contexts:
            return self.contexts[workflow_id]['data'].get(key)
        return None
    
    def get_all_context(self, workflow_id: str) -> Dict[str, Any]:
        """Get entire workflow context."""
        if workflow_id in self.contexts:
            return self.contexts[workflow_id]['data']
        return {}
    
    def update_context(self, workflow_id: str, updates: Dict[str, Any]):
        """Batch update context."""
        if workflow_id not in self.contexts:
            self.create_workflow_context(workflow_id)
        self.contexts[workflow_id]['data'].update(updates)
        logger.info(f"✓ Updated context for workflow: {workflow_id}")
    
    def delete_context(self, workflow_id: str):
        """Clean up workflow context."""
        if workflow_id in self.contexts:
            del self.contexts[workflow_id]
        logger.info(f"✓ Deleted context for workflow: {workflow_id}")
    
    def cleanup_workflow(self, workflow_id: str):
        """Alias for delete_context."""
        self.delete_context(workflow_id)
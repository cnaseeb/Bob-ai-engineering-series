"""
Workflow coordinator for multi-agent orchestration.
"""

import asyncio
from typing import Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WorkflowCoordinator:
    """
    Coordinator for multi-agent workflows.
    Handles task delegation, result aggregation, and error recovery.
    """
    
    def __init__(self, agent_registry, context_store, message_bus):
        self.agents = agent_registry
        self.context = context_store
        self.message_bus = message_bus
        logger.info("✓ WorkflowCoordinator initialized")
    
    async def execute_workflow(self, workflow_definition: Dict) -> Dict:
        """Execute workflow."""
        workflow_id = workflow_definition['workflow_id']
        logger.info(f"🚀 Starting workflow: {workflow_id}")
        
        try:
            # Initialize context
            self.context.create_workflow_context(workflow_id)
            
            # Execute stages
            results = {}
            for stage in workflow_definition['stages']:
                logger.info(f"▶️  Executing stage: {stage['name']}")
                
                stage_result = await self.execute_stage(workflow_id, stage)
                results[stage['name']] = stage_result
                
                # Update context
                self.context.update_context(workflow_id, {stage['name']: stage_result})
                
                logger.info(f"✅ Stage {stage['name']} completed")
            
            logger.info(f"🎉 Workflow {workflow_id} completed successfully")
            
            return {
                'status': 'success',
                'workflow_id': workflow_id,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"❌ Workflow {workflow_id} failed: {str(e)}")
            return {
                'status': 'failed',
                'workflow_id': workflow_id,
                'error': str(e)
            }
        finally:
            self.context.cleanup_workflow(workflow_id)
    
    async def execute_stage(self, workflow_id: str, stage: Dict) -> Dict:
        """Execute a workflow stage."""
        if stage.get('parallel', False):
            return await self.execute_parallel(workflow_id, stage)
        else:
            return await self.execute_sequential(workflow_id, stage)
    
    async def execute_parallel(self, workflow_id: str, stage: Dict) -> Dict:
        """Execute agents in parallel."""
        tasks = []
        for agent_config in stage['agents']:
            task = self.execute_agent(agent_config)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = [r for r in results if not isinstance(r, Exception)]
        failed = [r for r in results if isinstance(r, Exception)]
        
        return {
            'stage': stage['name'],
            'successful': successful,
            'failed': [str(f) for f in failed],
            'success_rate': len(successful) / len(results) if results else 0
        }
    
    async def execute_sequential(self, workflow_id: str, stage: Dict) -> Dict:
        """Execute agents sequentially."""
        results = []
        for agent_config in stage['agents']:
            result = await self.execute_agent(agent_config)
            results.append(result)
        
        return {
            'stage': stage['name'],
            'results': results
        }
    
    async def execute_agent(self, agent_config: Dict) -> Dict:
        """Execute single agent."""
        agent_id = agent_config['agent_id']
        action = agent_config['action']
        
        message = {
            'message_id': f"msg_{agent_id}_{datetime.utcnow().timestamp()}",
            'action': action,
            'parameters': agent_config.get('parameters', {}),
            'timeout': agent_config.get('timeout', 60)
        }
        
        response = await self.message_bus.send_and_wait(agent_id, message)
        return response
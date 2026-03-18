## Coordinator Agent Implementation

### Full Coordinator Agent

# coordinator_agent.py

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class Task:
    task_id: str
    agent_id: str
    action: str
    parameters: Dict[str, Any]
    priority: int = 5
    timeout: int = 60
    max_retries: int = 3
    retry_count: int = 0
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None

class WorkflowCoordinator:
    """
    Master coordinator agent for multi-agent workflows
    """
    
    def __init__(self, agent_registry, context_store, message_bus):
        self.agents = agent_registry
        self.context = context_store
        self.message_bus = message_bus
        self.active_workflows = {}
        
    async def execute_workflow(self, workflow_definition: Dict) -> Dict:
        """
        Execute a complete workflow with multiple agents
        """
        workflow_id = workflow_definition['workflow_id']
        logger.info(f"Starting workflow {workflow_id}")
        
        try:
            # Initialize workflow context
            self.context.create_workflow_context(workflow_id)
            
            # Parse workflow definition
            stages = self.parse_workflow_stages(workflow_definition)
            
            # Execute stages
            results = {}
            for stage in stages:
                stage_result = await self.execute_stage(
                    workflow_id, 
                    stage
                )
                results[stage['name']] = stage_result
                
                # Update context with stage results
                self.context.update_context(
                    workflow_id, 
                    {stage['name']: stage_result}
                )
                
                # Check if we should continue
                if not self.should_continue(stage_result, stage):
                    break
            
            # Aggregate final results
            final_result = self.aggregate_results(results)
            
            logger.info(f"Workflow {workflow_id} completed successfully")
            return {
                'status': 'success',
                'workflow_id': workflow_id,
                'results': final_result
            }
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {str(e)}")
            return {
                'status': 'failed',
                'workflow_id': workflow_id,
                'error': str(e)
            }
        finally:
            # Cleanup
            self.context.cleanup_workflow(workflow_id)
    
    async def execute_stage(
        self, 
        workflow_id: str, 
        stage: Dict
    ) -> Dict:
        """
        Execute a single workflow stage
        """
        if stage.get('parallel', False):
            return await self.execute_parallel_stage(workflow_id, stage)
        else:
            return await self.execute_sequential_stage(workflow_id, stage)
    
    async def execute_parallel_stage(
        self, 
        workflow_id: str, 
        stage: Dict
    ) -> Dict:
        """
        Execute multiple agents in parallel
        """
        tasks = []
        for agent_config in stage['agents']:
            task = self.create_task(workflow_id, agent_config)
            tasks.append(self.execute_task(task))
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful = []
        failed = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed.append({
                    'agent': stage['agents'][i]['agent_id'],
                    'error': str(result)
                })
            else:
                successful.append(result)
        
        return {
            'stage': stage['name'],
            'successful': successful,
            'failed': failed,
            'success_rate': len(successful) / len(results)
        }
    
    async def execute_sequential_stage(
        self, 
        workflow_id: str, 
        stage: Dict
    ) -> Dict:
        """
        Execute agents sequentially
        """
        results = []
        
        for agent_config in stage['agents']:
            task = self.create_task(workflow_id, agent_config)
            result = await self.execute_task(task)
            results.append(result)
            
            # Stop if critical task failed
            if result['status'] == 'failed' and agent_config.get('critical', False):
                break
        
        return {
            'stage': stage['name'],
            'results': results
        }
    
    async def execute_task(self, task: Task) -> Dict:
        """
        Execute a single task with retry logic
        """
        while task.retry_count <= task.max_retries:
            try:
                # Get agent
                agent = self.agents.get_agent(task.agent_id)
                
                # Send task to agent
                result = await self.send_task_to_agent(agent, task)
                
                task.status = TaskStatus.COMPLETED
                task.result = result
                
                return {
                    'status': 'success',
                    'task_id': task.task_id,
                    'agent_id': task.agent_id,
                    'result': result
                }
                
            except Exception as e:
                task.retry_count += 1
                task.error = str(e)
                
                if task.retry_count <= task.max_retries:
                    # Exponential backoff
                    delay = 2 ** task.retry_count
                    logger.warning(
                        f"Task {task.task_id} failed, retrying in {delay}s"
                    )
                    await asyncio.sleep(delay)
                else:
                    task.status = TaskStatus.FAILED
                    logger.error(f"Task {task.task_id} failed after max retries")
                    return {
                        'status': 'failed',
                        'task_id': task.task_id,
                        'agent_id': task.agent_id,
                        'error': str(e)
                    }
    
    async def send_task_to_agent(self, agent: Any, task: Task) -> Dict:
        """
        Send task to agent and wait for response
        """
        message = {
            'message_id': f"msg_{task.task_id}",
            'task_id': task.task_id,
            'action': task.action,
            'parameters': task.parameters,
            'timeout': task.timeout
        }
        
        # Send via message bus
        response = await self.message_bus.send_and_wait(
            agent.agent_id,
            message,
            timeout=task.timeout
        )
        
        return response
    
    def create_task(self, workflow_id: str, agent_config: Dict) -> Task:
        """
        Create task from agent configuration
        """
        return Task(
            task_id=f"{workflow_id}_{agent_config['agent_id']}_{id(agent_config)}",
            agent_id=agent_config['agent_id'],
            action=agent_config['action'],
            parameters=agent_config.get('parameters', {}),
            priority=agent_config.get('priority', 5),
            timeout=agent_config.get('timeout', 60),
            max_retries=agent_config.get('max_retries', 3)
        )
    
    def parse_workflow_stages(self, workflow_def: Dict) -> List[Dict]:
        """
        Parse workflow definition into executable stages
        """
        stages = []
        for stage_def in workflow_def['stages']:
            stages.append({
                'name': stage_def['name'],
                'agents': stage_def['agents'],
                'parallel': stage_def.get('parallel', False),
                'depends_on': stage_def.get('depends_on', []),
                'condition': stage_def.get('condition')
            })
        return stages
    
    def should_continue(self, stage_result: Dict, stage: Dict) -> bool:
        """
        Determine if workflow should continue after stage
        """
        # Check if stage has condition
        if 'condition' in stage:
            return self.evaluate_condition(stage['condition'], stage_result)
        
        # Check success rate for parallel stages
        if stage.get('parallel', False):
            min_success_rate = stage.get('min_success_rate', 0.8)
            return stage_result['success_rate'] >= min_success_rate
        
        # For sequential, continue if no critical failures
        return True
    
    def aggregate_results(self, results: Dict) -> Dict:
        """
        Aggregate results from all stages
        """
        aggregated = {
            'stages_completed': len(results),
            'stage_results': results,
            'overall_status': 'success'
        }
        
        # Check for any failures
        for stage_name, stage_result in results.items():
            if isinstance(stage_result, dict):
                if stage_result.get('status') == 'failed':
                    aggregated['overall_status'] = 'partial_success'
        
        return aggregated

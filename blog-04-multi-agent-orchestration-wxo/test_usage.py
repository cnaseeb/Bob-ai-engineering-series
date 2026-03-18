""" # Usage example
from typing import Dict
import asyncio

async def main():
    # Initialize components
    agent_registry = AgentRegistry() #AgentRegistry
    context_store = SharedContextStore("redis://localhost:6379")
    message_bus = MessageBus("redis://localhost:6379")
    
    # Create coordinator
    coordinator = WorkflowCoordinator(
        agent_registry,
        context_store,
        message_bus
    )
    
    # Create workflow
    workflow = CustomerOnboardingWorkflow(coordinator)
    
    # Execute
    customer_data = {
        'customer_id': 'CUST_12345',
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '+1234567890'
    }
    
    result = await workflow.onboard_customer(customer_data)
    
    print(f"Onboarding result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
 """ 
 ##old
 ##new

"""
Complete standalone test file for multi-agent orchestration.
All classes included - no external imports needed.

Usage:
    python test_usage.py
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# MODELS AND ENUMS
# ============================================================================

class AgentStatus(Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AgentCapability:
    name: str
    version: str
    performance_score: float = 1.0
    cost_per_invocation: float = 0.01

@dataclass
class AgentMetadata:
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
    task_id: str
    agent_id: str
    action: str
    parameters: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None

# ============================================================================
# AGENT REGISTRY
# ============================================================================

class AgentRegistry:
    """Service registry for agent discovery and selection."""
    
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
    
    def list_all_agents(self) -> List[AgentMetadata]:
        """Get list of all registered agents."""
        return list(self.agents.values())

# ============================================================================
# CONTEXT STORE
# ============================================================================

class SharedContextStore:
    """Shared context store for multi-agent workflows."""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.contexts: Dict[str, Dict[str, Any]] = {}
        self.redis_url = redis_url
        logger.info(f"✓ SharedContextStore initialized")
    
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
    
    def cleanup_workflow(self, workflow_id: str):
        """Clean up workflow context."""
        if workflow_id in self.contexts:
            del self.contexts[workflow_id]
        logger.info(f"✓ Cleaned up context for workflow: {workflow_id}")

# ============================================================================
# MESSAGE BUS
# ============================================================================

class MessageBus:
    """Message bus for agent communication (mock implementation)."""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.messages = []
        self.pending_responses = {}
        logger.info(f"✓ MessageBus initialized")
    
    async def send_message(self, recipient_id: str, message: Dict) -> str:
        """Send message to agent."""
        message_id = message['message_id']
        self.messages.append({
            'recipient': recipient_id,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        })
        logger.info(f"📤 Sent message {message_id} to {recipient_id}")
        return message_id
    
    async def send_and_wait(
        self, 
        recipient_id: str, 
        message: Dict,
        timeout: int = 60
    ) -> Dict:
        """Send message and wait for response (mock)."""
        message_id = await self.send_message(recipient_id, message)
        
        # Simulate agent processing
        await asyncio.sleep(0.1)
        
        # Generate mock response
        response = {
            'status': 'success',
            'message_id': f"resp_{message_id}",
            'in_reply_to': message_id,
            'result': {
                'agent_id': recipient_id,
                'action': message.get('action'),
                'data': f"Processed by {recipient_id}",
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        
        logger.info(f"📥 Received response from {recipient_id}")
        return response

# ============================================================================
# WORKFLOW COORDINATOR
# ============================================================================

class WorkflowCoordinator:
    """Coordinator for multi-agent workflows."""
    
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

# ============================================================================
# CUSTOMER ONBOARDING WORKFLOW
# ============================================================================

class CustomerOnboardingWorkflow:
    """Complete multi-agent workflow for customer onboarding."""
    
    def __init__(self, coordinator):
        self.coordinator = coordinator
        logger.info("✓ CustomerOnboardingWorkflow initialized")
    
    async def onboard_customer(self, customer_data: Dict) -> Dict:
        """Execute complete onboarding workflow."""
        workflow_definition = {
            'workflow_id': f"onboarding_{customer_data['customer_id']}",
            'stages': [
                {
                    'name': 'document_collection',
                    'agents': [{
                        'agent_id': 'document_agent',
                        'action': 'collect_documents',
                        'parameters': {
                            'customer_id': customer_data['customer_id'],
                            'required_documents': [
                                'identity_proof',
                                'address_proof',
                                'income_proof'
                            ]
                        },
                        'timeout': 300,
                        'critical': True
                    }],
                    'parallel': False
                },
                {
                    'name': 'parallel_verification',
                    'agents': [
                        {
                            'agent_id': 'identity_verification_agent',
                            'action': 'verify_identity',
                            'parameters': {},
                            'timeout': 180
                        },
                        {
                            'agent_id': 'credit_check_agent',
                            'action': 'check_credit',
                            'parameters': {
                                'customer_id': customer_data['customer_id']
                            },
                            'timeout': 120
                        },
                        {
                            'agent_id': 'compliance_agent',
                            'action': 'compliance_check',
                            'parameters': {
                                'customer_data': customer_data
                            },
                            'timeout': 150
                        }
                    ],
                    'parallel': True,
                    'min_success_rate': 1.0
                },
                {
                    'name': 'account_setup',
                    'agents': [{
                        'agent_id': 'account_setup_agent',
                        'action': 'create_account',
                        'parameters': {
                            'customer_data': customer_data
                        },
                        'timeout': 120,
                        'critical': True
                    }],
                    'parallel': False
                },
                {
                    'name': 'notifications',
                    'agents': [{
                        'agent_id': 'notification_agent',
                        'action': 'send_welcome',
                        'parameters': {
                            'customer_id': customer_data['customer_id']
                        },
                        'timeout': 30
                    }],
                    'parallel': False
                }
            ]
        }
        
        return await self.coordinator.execute_workflow(workflow_definition)

# ============================================================================
# MAIN USAGE EXAMPLE
# ============================================================================

async def main():
    """Main usage example."""
    print("\n" + "="*70)
    print("🚀 MULTI-AGENT ORCHESTRATION - USAGE EXAMPLE")
    print("="*70 + "\n")
    
    # Initialize components
    agent_registry = AgentRegistry()
    context_store = SharedContextStore("redis://localhost:6379")
    message_bus = MessageBus("redis://localhost:6379")
    
    # Register mock agents
    agents_to_register = [
        AgentMetadata(
            agent_id='document_agent',
            agent_type='data_extraction',
            capabilities=[AgentCapability('collect_documents', '1.0')]
        ),
        AgentMetadata(
            agent_id='identity_verification_agent',
            agent_type='validation',
            capabilities=[AgentCapability('verify_identity', '1.0')]
        ),
        AgentMetadata(
            agent_id='credit_check_agent',
            agent_type='analysis',
            capabilities=[AgentCapability('check_credit', '1.0')]
        ),
        AgentMetadata(
            agent_id='compliance_agent',
            agent_type='validation',
            capabilities=[AgentCapability('compliance_check', '1.0')]
        ),
        AgentMetadata(
            agent_id='account_setup_agent',
            agent_type='action',
            capabilities=[AgentCapability('create_account', '1.0')]
        ),
        AgentMetadata(
            agent_id='notification_agent',
            agent_type='communication',
            capabilities=[AgentCapability('send_welcome', '1.0')]
        )
    ]
    
    for agent in agents_to_register:
        agent_registry.register_agent(agent)
    
    # Create coordinator
    coordinator = WorkflowCoordinator(
        agent_registry,
        context_store,
        message_bus
    )
    
    # Create workflow
    workflow = CustomerOnboardingWorkflow(coordinator)
    
    # Execute
    customer_data = {
        'customer_id': 'CUST_12345',
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '+1234567890'
    }
    
    result = await workflow.onboard_customer(customer_data)
    
    # Display results
    print("\n" + "="*70)
    print("📊 ONBOARDING RESULT")
    print("="*70)
    print(json.dumps(result, indent=2))
    print("\n" + "="*70)
    print("✅ Test completed successfully!")
    print("="*70 + "\n")

if __name__ == "__main__":
    """
    Run this file:
        python test_usage.py
    
    No external dependencies required except Python 3.7+
    """
    asyncio.run(main())



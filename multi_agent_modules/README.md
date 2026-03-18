# Multi-Agent Orchestration Framework

Professional modular implementation of multi-agent orchestration for watsonx Orchestrate.

## Structure

```
multi_agent_modules/
├── __init__.py              # Package initialization and exports
├── models.py                # Data models and enums
├── agent_registry.py        # Agent discovery and selection
├── context_store.py         # Shared workflow context
├── message_bus.py           # Agent communication
├── coordinator.py           # Workflow orchestration
└── workflows.py             # Workflow definitions
```

## Installation

No external dependencies required except Python 3.7+

## Usage

### Option 1: Import from Package

```python
from multi_agent_modules import (
    AgentRegistry,
    SharedContextStore,
    MessageBus,
    WorkflowCoordinator,
    CustomerOnboardingWorkflow,
    AgentMetadata,
    AgentCapability
)

# Use the classes
agent_registry = AgentRegistry()
context_store = SharedContextStore("redis://localhost:6379")
message_bus = MessageBus("redis://localhost:6379")
coordinator = WorkflowCoordinator(agent_registry, context_store, message_bus)
```

### Option 2: Import Individual Modules

```python
from multi_agent_modules.agent_registry import AgentRegistry
from multi_agent_modules.context_store import SharedContextStore
from multi_agent_modules.message_bus import MessageBus
from multi_agent_modules.coordinator import WorkflowCoordinator
from multi_agent_modules.workflows import CustomerOnboardingWorkflow
from multi_agent_modules.models import AgentMetadata, AgentCapability
```

## Quick Start

```bash
# Navigate to the directory
cd Eminence/Technical_Guides

# Run the modular test
python test_modular.py
```

## Module Descriptions

### models.py
Data models and enums used throughout the framework:
- `AgentStatus`: Agent availability states
- `TaskStatus`: Task execution states
- `AgentCapability`: Agent capability definition
- `AgentMetadata`: Complete agent information
- `Task`: Task definition

### agent_registry.py
Service registry for agent discovery and selection:
- Register agents
- Find agents by capability
- Select best agent based on criteria (performance, cost, load)
- Update agent status

### context_store.py
Shared context store for workflow state:
- Create workflow context
- Store/retrieve context data
- Update context in batch
- Cleanup workflow context

### message_bus.py
Message bus for agent communication:
- Send messages to agents
- Send and wait for responses
- Subscribe to agent inbox
- Handle responses

### coordinator.py
Workflow coordinator for orchestration:
- Execute complete workflows
- Execute stages (parallel or sequential)
- Execute individual agents
- Handle errors and retries

### workflows.py
Pre-defined workflow implementations:
- `CustomerOnboardingWorkflow`: 4-stage onboarding process

## Example: Customer Onboarding

```python
import asyncio
from multi_agent_modules import (
    AgentRegistry,
    SharedContextStore,
    MessageBus,
    WorkflowCoordinator,
    CustomerOnboardingWorkflow,
    AgentMetadata,
    AgentCapability
)

async def main():
    # Initialize
    agent_registry = AgentRegistry()
    context_store = SharedContextStore("redis://localhost:6379")
    message_bus = MessageBus("redis://localhost:6379")
    
    # Register agents
    agent_registry.register_agent(
        AgentMetadata(
            agent_id='document_agent',
            agent_type='data_extraction',
            capabilities=[AgentCapability('collect_documents', '1.0')]
        )
    )
    # ... register more agents
    
    # Create coordinator and workflow
    coordinator = WorkflowCoordinator(agent_registry, context_store, message_bus)
    workflow = CustomerOnboardingWorkflow(coordinator)
    
    # Execute
    customer_data = {
        'customer_id': 'CUST_12345',
        'name': 'John Doe',
        'email': 'john.doe@example.com'
    }
    
    result = await workflow.onboard_customer(customer_data)
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Benefits of Modular Structure

✅ **Reusability**: Use components across multiple projects  
✅ **Testability**: Test each module independently  
✅ **Maintainability**: Update one file without affecting others  
✅ **Collaboration**: Multiple developers work without conflicts  
✅ **Professional**: Industry-standard organization  

## Testing

Two test files are provided:

1. **test_usage.py**: All-in-one file with all classes included
2. **test_modular.py**: Uses modular imports (recommended)

```bash
# Test with modular imports
python test_modular.py

# Test with all-in-one file
python test_usage.py
```

## Extending the Framework

### Add a New Agent

```python
# In agent_registry
agent_registry.register_agent(
    AgentMetadata(
        agent_id='my_new_agent',
        agent_type='custom',
        capabilities=[AgentCapability('my_action', '1.0')]
    )
)
```

### Add a New Workflow

```python
# In workflows.py or your own file
class MyCustomWorkflow:
    def __init__(self, coordinator):
        self.coordinator = coordinator
    
    async def execute(self, data):
        workflow_definition = {
            'workflow_id': f"my_workflow_{data['id']}",
            'stages': [
                # Define your stages here
            ]
        }
        return await self.coordinator.execute_workflow(workflow_definition)
```

## Production Considerations

For production use, replace mock implementations:

1. **MessageBus**: Use Redis pub/sub or Kafka
2. **ContextStore**: Use Redis or distributed cache
3. **AgentRegistry**: Use service discovery (Consul, etcd)

## License

MIT License

## Version

1.0.0
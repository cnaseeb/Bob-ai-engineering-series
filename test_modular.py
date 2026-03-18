"""
Test file using modular structure with separate class files.

This demonstrates how to use the multi-agent orchestration framework
when classes are organized in separate module files.

Usage:
    python test_modular.py
"""

import asyncio
import json
import logging

# Import from multi_agent_modules package
from multi_agent_modules import (
    AgentRegistry,
    SharedContextStore,
    MessageBus,
    WorkflowCoordinator,
    CustomerOnboardingWorkflow,
    AgentMetadata,
    AgentCapability
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main usage example with modular imports."""
    print("\n" + "="*70)
    print("🚀 MULTI-AGENT ORCHESTRATION - MODULAR TEST")
    print("="*70 + "\n")
    
    # Step 1: Initialize components
    logger.info("Initializing components...")
    agent_registry = AgentRegistry()
    context_store = SharedContextStore("redis://localhost:6379")
    message_bus = MessageBus("redis://localhost:6379")
    
    # Step 2: Register mock agents
    logger.info("Registering agents...")
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
    
    # Step 3: Create coordinator
    logger.info("Creating workflow coordinator...")
    coordinator = WorkflowCoordinator(
        agent_registry,
        context_store,
        message_bus
    )
    
    # Step 4: Create workflow
    logger.info("Creating customer onboarding workflow...")
    workflow = CustomerOnboardingWorkflow(coordinator)
    
    # Step 5: Prepare customer data
    customer_data = {
        'customer_id': 'CUST_12345',
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '+1234567890',
        'address': '123 Main St, City, State 12345'
    }
    
    # Step 6: Execute workflow
    logger.info(f"Starting onboarding for customer {customer_data['customer_id']}...")
    
    try:
        result = await workflow.onboard_customer(customer_data)
        
        # Display results
        print("\n" + "="*70)
        print("📊 ONBOARDING RESULT")
        print("="*70)
        print(json.dumps(result, indent=2))
        print("\n" + "="*70)
        
        if result['status'] == 'success':
            logger.info("✅ Customer onboarding completed successfully!")
        else:
            logger.error(f"❌ Customer onboarding failed: {result.get('error')}")
    
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise
    
    print("\n" + "="*70)
    print("✅ Test completed successfully!")
    print("="*70 + "\n")

if __name__ == "__main__":
    """
    Run this test:
    
    1. Ensure you're in the correct directory:
       cd Eminence/Technical_Guides
    
    2. Run the test:
       python test_modular.py
    
    The test will import classes from the multi_agent_modules package
    and execute a complete customer onboarding workflow.
    """
    asyncio.run(main())



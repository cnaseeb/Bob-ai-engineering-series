# Usage example
async def main():
    # Initialize components
    agent_registry = AgentRegistry()
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

## Complete Workflow Example

### Customer Onboarding Workflow

# customer_onboarding_workflow.py

import asyncio
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class CustomerOnboardingWorkflow:
    """
    Complete multi-agent workflow for customer onboarding
    """
    
    def __init__(self, coordinator):
        self.coordinator = coordinator
    
    async def onboard_customer(self, customer_data: Dict) -> Dict:
        """
        Execute complete onboarding workflow
        """
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
                            'parameters': {
                                'documents': '${document_collection.documents}'
                            },
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
                    'min_success_rate': 1.0,
                    'depends_on': ['document_collection']
                },
                {
                    'name': 'account_setup',
                    'agents': [{
                        'agent_id': 'account_setup_agent',
                        'action': 'create_account',
                        'parameters': {
                            'customer_data': customer_data,
                            'verification_results': '${parallel_verification}'
                        },
                        'timeout': 120,
                        'critical': True
                    }],
                    'parallel': False,
                    'depends_on': ['parallel_verification'],
                    'condition': 'all_verifications_passed'
                },
                {
                    'name': 'notifications',
                    'agents': [{
                        'agent_id': 'notification_agent',
                        'action': 'send_welcome',
                        'parameters': {
                            'customer_id': customer_data['customer_id'],
                            'account_details': '${account_setup.account}'
                        },
                        'timeout': 30
                    }],
                    'parallel': False,
                    'depends_on': ['account_setup']
                }
            ]
        }
        
        # Execute workflow
        result = await self.coordinator.execute_workflow(workflow_definition)
        
        return result
    

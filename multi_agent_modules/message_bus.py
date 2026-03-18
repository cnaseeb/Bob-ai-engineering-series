"""
Message bus for agent communication.
"""

import asyncio
from typing import Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MessageBus:
    """
    Message bus for agent communication (mock implementation).
    In production, this would use Redis pub/sub or similar.
    """
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.messages = []
        self.pending_responses = {}
        logger.info("✓ MessageBus initialized")
    
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
    
    async def subscribe(self, agent_id: str, handler):
        """Subscribe agent to its inbox."""
        # Mock implementation
        pass
    
    async def send_response(self, original_message_id: str, response: Dict):
        """Send response to original sender."""
        response['in_reply_to'] = original_message_id
        if original_message_id in self.pending_responses:
            future = self.pending_responses[original_message_id]
            future.set_result(response)
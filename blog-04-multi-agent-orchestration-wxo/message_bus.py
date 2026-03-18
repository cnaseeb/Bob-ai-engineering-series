## Communication Layer

### Message Bus Implementation

# message_bus.py

import asyncio
import json
from typing import Dict, Callable, Optional
import redis.asyncio as redis
import logging

logger = logging.getLogger(__name__)

class MessageBus:
    """
    Asynchronous message bus for agent communication
    """
    
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.subscribers = {}
        self.pending_responses = {}
    
    async def send_message(
        self, 
        recipient_id: str, 
        message: Dict
    ) -> str:
        """
        Send message to agent
        """
        message_id = message['message_id']
        channel = f"agent:{recipient_id}:inbox"
        
        await self.redis.publish(
            channel,
            json.dumps(message)
        )
        
        logger.debug(f"Sent message {message_id} to {recipient_id}")
        return message_id
    
    async def send_and_wait(
        self, 
        recipient_id: str, 
        message: Dict,
        timeout: int = 60
    ) -> Dict:
        """
        Send message and wait for response
        """
        message_id = await self.send_message(recipient_id, message)
        
        # Create future for response
        future = asyncio.Future()
        self.pending_responses[message_id] = future
        
        try:
            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            logger.error(f"Timeout waiting for response to {message_id}")
            raise
        finally:
            # Cleanup
            if message_id in self.pending_responses:
                del self.pending_responses[message_id]
    
    async def subscribe(
        self, 
        agent_id: str, 
        handler: Callable
    ):
        """
        Subscribe agent to its inbox
        """
        channel = f"agent:{agent_id}:inbox"
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        
        logger.info(f"Agent {agent_id} subscribed to {channel}")
        
        async for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    await handler(data)
                except Exception as e:
                    logger.error(f"Error handling message: {str(e)}")
    
    async def send_response(
        self, 
        original_message_id: str, 
        response: Dict
    ):
        """
        Send response to original sender
        """
        response['in_reply_to'] = original_message_id
        
        # Resolve pending future if exists
        if original_message_id in self.pending_responses:
            future = self.pending_responses[original_message_id]
            future.set_result(response)
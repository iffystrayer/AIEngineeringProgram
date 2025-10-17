"""
Conversation engine module for U-AIP Scoping Assistant.

This module provides stateful conversation management with:
- Turn-taking between agent and user
- Quality validation loops
- Context management
- Reflection agent integration
"""

from src.conversation.engine import ConversationEngine, ConversationState
from src.conversation.context import ConversationContext
from src.conversation.types import Message, MessageRole, Turn

__all__ = [
    'ConversationEngine',
    'ConversationState',
    'ConversationContext',
    'Message',
    'MessageRole',
    'Turn'
]

"""
Pydantic models for API request/response schemas.
"""

from pydantic import BaseModel
from typing import Dict, List, Literal


class Message(BaseModel):
    """Chat message with role and content."""
    role: Literal['user', 'assistant']
    content: str


class GenerationRequest(BaseModel):
    """Request for text generation with optional steering."""
    messages: List[Message]
    steering_config: Dict[str, Dict[int, float]] = {"pc_values": {}}
    num_tokens: int = 100
    is_partial: bool = False  # If True, last assistant message is incomplete (for step mode)


class GenerationResponse(BaseModel):
    """Response containing generated text and termination status."""
    content: str
    terminating: bool
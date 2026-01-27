from typing import Any, Dict, List, Literal, Optional, Union, AsyncIterator
from pydantic import BaseModel, Field
from datetime import datetime

class AgentMessage(BaseModel):
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class AgentEvent(BaseModel):
    """Base class for all agent events streamed to the UI."""
    type: str
    timestamp: datetime = Field(default_factory=datetime.now)

class TokenEvent(AgentEvent):
    type: Literal["token"] = "token"
    content: str

class ThoughtEvent(AgentEvent):
    type: Literal["thought"] = "thought"
    content: str

class ToolCallEvent(AgentEvent):
    type: Literal["tool_call"] = "tool_call"
    tool_name: str
    tool_args: Dict[str, Any]
    tool_call_id: str

class ToolResultEvent(AgentEvent):
    type: Literal["tool_result"] = "tool_result"
    tool_name: str
    result: str
    tool_call_id: str
    is_error: bool = False

class ErrorEvent(AgentEvent):
    type: Literal["error"] = "error"
    message: str

class AgentState(BaseModel):
    """Represents the current state of the agent."""
    messages: List[AgentMessage] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)

class AgentConfig(BaseModel):
    """Configuration for an agent."""
    name: str = "Assistant"
    model: str = "gpt-4"
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    tools: List[Any] = Field(default_factory=list)

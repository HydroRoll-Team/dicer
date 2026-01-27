import abc
import asyncio
from typing import AsyncIterator, List, Optional, Any, Dict
from loguru import logger

from .types import (
    AgentConfig, 
    AgentEvent, 
    AgentMessage, 
    TokenEvent, 
    ThoughtEvent, 
    ToolCallEvent, 
    ToolResultEvent, 
    ErrorEvent
)

class BaseAgent(abc.ABC):
    """
    Base class for all agents. 
    Users should inherit from this class and implement the `generate_response` method
    or use the provided `ReactAgent` which implements standard ReAct logic.
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig(name="BaseAgent")
        self.history: List[AgentMessage] = []
        if self.config.system_prompt:
            self.history.append(AgentMessage(role="system", content=self.config.system_prompt))

    def add_message(self, role: str, content: str, **kwargs):
        """Add a message to the agent's memory."""
        msg = AgentMessage(role=role, content=content, **kwargs)
        self.history.append(msg)
        return msg

    @abc.abstractmethod
    async def run(self, input_text: str) -> AsyncIterator[AgentEvent]:
        """
        Process a user input and yield events.
        This is the main entry point for the TUI runner.
        """
        if False: yield
        pass

class ReactAgent(BaseAgent):
    """
    A standard ReAct agent implementation.
    This is a placeholder for the actual LangGraph or custom loop implementation.
    """
    
    async def run(self, input_text: str) -> AsyncIterator[AgentEvent]:
        self.add_message("user", input_text)
        
        # Simulation of an agent loop for demonstration
        yield ThoughtEvent(content="I need to process the user's request.")
        await asyncio.sleep(0.5)
        
        yield ThoughtEvent(content=f"User asked: {input_text}. I should think about this.")
        await asyncio.sleep(0.5)
        
        # Simulate tool use if "tool" is in input
        if "weather" in input_text.lower():
            yield ThoughtEvent(content="I should check the weather tool.")
            tool_call_id = "call_123"
            yield ToolCallEvent(
                tool_name="get_weather", 
                tool_args={"location": "New York"},
                tool_call_id=tool_call_id
            )
            await asyncio.sleep(1.0)
            yield ToolResultEvent(
                tool_name="get_weather",
                result="Sunny, 25C",
                tool_call_id=tool_call_id
            )
            yield ThoughtEvent(content="The weather is sunny. I will inform the user.")

        # Simulate streaming response
        response = f"I processed: {input_text}"
        for word in response.split():
            yield TokenEvent(content=word + " ")
            await asyncio.sleep(0.1)
            
        self.add_message("assistant", response)

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Union,
)
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.callbacks import BaseCallbackHandler
from app.configs import logging

logger = logging.getLogger()

class ToollCallbackHanlder(BaseCallbackHandler):
    """Base callback handler that can be used to handle callbacks from langchain."""

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        """Run when LLM starts running."""
        logger.debug("LLM start")
        

    def on_chat_model_start(
        self, serialized: Dict[str, Any], messages: List[List[BaseMessage]], **kwargs: Any
    ) -> Any:
        """Run when Chat Model starts running."""
        logger.debug("Chat model Start")
        

    def on_llm_new_token(self, token: str, **kwargs: Any) -> Any:
        """Run on new LLM token. Only available when streaming is enabled."""
        logger.debug(f"LLM new token: {token}")
        

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        """Run when LLM ends running."""
        logger.debug("LLM end")
        

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when LLM errors."""
        logger.debug("LLM Error")
        

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> Any:
        """Run when chain starts running."""
        logger.debug("Chain start")


    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> Any:
        """Run when chain ends running."""
        logger.debug("Chain end")
        

    def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when chain errors."""
        logger.debug("Chain error")
        

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> Any:
        """Run when tool starts running."""
        logger.debug("Tool start")
        logger.debug(f'Tool Name: {serialized['name']}')
        # logger.debug(f'Tool Description: {serialized['description']}')
        # logger.debug(f'Tool Input: {input_str}')
        # logger.debug(f'Run ID: {kwargs['run_id']}')
        # logger.debug(f'Parent Run ID: {kwargs['parent_run_id']}')
        
        

    def on_tool_end(self, output: Any, **kwargs: Any) -> Any:
        """Run when tool ends running."""
        logger.debug("Tool end")

    
    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when tool errors."""
        logger.debug("Tool error")
        

    def on_text(self, text: str, **kwargs: Any) -> Any:
        """Run on arbitrary text."""
        logger.debug("On text")
        

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Run on agent action."""
        logger.debug("Agent action")
        

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """Run on agent end."""
        logger.debug("Agent finish")
        
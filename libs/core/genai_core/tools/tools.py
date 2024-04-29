from typing import Any, Union, Dict, Optional, Type, List
from pydantic import BaseModel, ValidationError
from abc import ABC, abstractmethod

from genai_core.logging import logging

logger = logging.getLogger()

class BaseTool(ABC):
    
    name: str
    description: str
    args_schema: Optional[Type[BaseModel]] = None
    
    @abstractmethod
    async def _run(self, **kwargs: Any) -> Any:
        pass
    
    def _parse_input(self, tool_input: Union[str, Dict]) -> Union[str, Dict[str, Any]]:
        """Convert tool input to pydantic model."""
        
        input_args = self.args_schema
        if isinstance(tool_input, str):
            if input_args is not None:
                key_ = next(iter(input_args.model_fields.keys()))
                input_args.model_validate({key_: tool_input})
            return tool_input
        else:
            if input_args is not None:
                result = input_args.model_validate(tool_input)
                return {
                    k: getattr(result, k)
                    for k, v in result.model_dump().items()
                    if k in tool_input
                }
        return tool_input
    
    async def run(self, tool_input: Union[str, Dict[str, Any]], 
            tags: Optional[List[str]] = None) -> Any:
        try:
            tool_kwargs = self._parse_input(tool_input)
            return await self._run(**tool_kwargs)
        except TypeError as e:
            logger.error(f"Tool input type error: {e}")
        except ValidationError as e:
            logger.error(f"Tool input validation error: {e}")
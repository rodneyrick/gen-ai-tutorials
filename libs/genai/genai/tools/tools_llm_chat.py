from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from typing import Optional, Type


from genai_core.telemetry import instrumented_trace, TraceInstruments
from genai_core.callbacks import ToollCallbackHanlder
from genai_core.logging import logging
from genai_core.tools import BaseTool

logger = logging.getLogger()

class ChatInput(BaseModel):
    model: str = Field(description="Repository Name")
    api_key: str = Field(description="OpenAI Key")
    api_base: str = Field(description="OpenAI Base")
    prompt: list = Field(description="Model input message")
    temperature: Optional[float] = Field(description="Model Temperature", default=0.3)
    streaming: Optional[bool] = Field(description="Defines model return token or full response", default=False)
    
class ToolChatLLM(BaseTool):
    name = "LLM Chat"
    description = "useful for when you need to interact model llm"
    args_schema: Type[BaseModel] = ChatInput

    @instrumented_trace()
    async def _run(self, model: str, api_key: str, api_base: str, prompt: list, 
                    temperature: Optional[float] = 0.3, 
                    streaming: Optional[bool] = False) -> str:

        chat = self.chat(api_base=api_base, api_key=api_key, model=model, temperature=temperature, 
                             streaming=streaming)
        
        return chat.invoke(input=prompt, config={"callbacks": [ToollCallbackHanlder()]})

    @instrumented_trace(span_name="Creating Chat", span_parameters=False)
    def chat(self, api_base: str, api_key: str, model: str, temperature: float, streaming: bool):
        chat = ChatOpenAI(openai_api_base=api_base,
                          openai_api_key=api_key,
                          streaming=streaming, 
                          model=model,
                          temperature=temperature)

        return chat
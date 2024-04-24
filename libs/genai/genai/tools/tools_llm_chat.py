from langchain.pydantic_v1 import BaseModel, Field
# from langfuse.callback import CallbackHandler
from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool
from typing import Optional, Type


from genai_core.telemetry import instrumented_trace, TraceInstruments
from genai_core.callbacks import ToollCallbackHanlder
from genai_core.logging import logging

logger = logging.getLogger()

class ChatInput(BaseModel):
    model: str = Field(description="Repository Name")
    api_key: str = Field(description="OpenAI Key")
    api_base: str = Field(description="OpenAI Base")
    prompt: list = Field(description="Model input message")
    langfuse_secret_key: Optional[str] = Field(description="Langfuse Secret Key")
    langfuse_public_key: Optional[str] = Field(description="Langfuse Public Key")
    temperature: Optional[str] = Field(description="Model Temperature")
    streaming: Optional[bool] = Field(description="Defines model return token or full response")
    
class ToolChatLLM(BaseTool):
    name = "LLM Chat"
    description = "useful for when you need to interact model llm"
    args_schema: Type[BaseModel] = ChatInput
    return_direct: bool = True

    @instrumented_trace()
    def _run(self, model: str, api_key: str, api_base: str, prompt: list, 
             langfuse_secret_key: Optional[str] = None,
             langfuse_public_key: Optional[str] = None, temperature: Optional[str] = 0.3, 
             streaming: Optional[bool] = False) -> str:
        """Use the tool."""
        try:
            # if langfuse_secret_key is not None:
            #     return self.chat_langfuse(model=model, api_base=api_base, api_key=api_key,
            #                               prompt=prompt, temperature=temperature, streaming=streaming, 
            #                               langfuse_public_key=langfuse_public_key,
            #                               langfuse_secret_key=langfuse_secret_key)
            
            chat = self.chat(api_base=api_base, api_key=api_key, model=model, temperature=temperature, 
                             streaming=streaming)
            return chat.invoke(input=prompt, config={"callbacks": [ToollCallbackHanlder()]})
                
        except Exception as e:
            logger.error(e)
            raise ValueError(e)

    async def _arun(self) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")

    @instrumented_trace(span_name="Creating Chat")
    def chat(self, api_base: str, api_key: str, model: str, temperature: str, streaming: bool):
        chat = ChatOpenAI(openai_api_base=api_base,
                          openai_api_key=api_key,
                          streaming=streaming, 
                          model=model,
                          temperature=temperature)

        return chat
    
    # @instrumented_trace(span_name="Creating Chat Langfuse")
    # def chat_langfuse(self,  api_base: str, api_key: str, model: str, temperature: str, streaming: bool,
    #                   langfuse_secret_key: str, langfuse_public_key: str, prompt: list):
        
    #     langfuse_handler = CallbackHandler(
    #         secret_key=langfuse_secret_key,
    #         public_key=langfuse_public_key,
    #         host=api_base
    #     )
    #     chat = self.chat(api_base=api_base, api_key=api_key, model=model, temperature=temperature, streaming=streaming)
    #     return chat.invoke(input=prompt, config={"callbacks": [langfuse_handler]})
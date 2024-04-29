from httpx import AsyncClient, Timeout, ConnectTimeout
from typing import Optional, Dict, Type
from abc import ABC, abstractmethod
from genai_core.telemetry import instrumented_trace, TraceInstruments
from genai_core.logging import logging
import asyncio

logger = logging.getLogger()

class HttpBaseInterface(ABC):
    
    @abstractmethod
    async def post(self, url: str, headers: Optional[Dict[str, str]] = None):
        pass
    
    @abstractmethod
    async def get(self, url: str, headers: Optional[Dict[str, str]] = None):
        pass

class HttpxClient(HttpBaseInterface):
    DEFAULT_TIMEOUT_CONFIG = Timeout(timeout=10.0)
    DEFAULT_RETRY_INTERVAL = 5
    DEFAULT_MAX_RETRIES = 5

    @instrumented_trace(span_name="Request POST", kind=TraceInstruments.SPAN_KIND_CLIENT, span_parameters=False)
    async def post(self, url: str, headers: Optional[Dict[str, str]] = None):
        retries = 0
        while retries < self.DEFAULT_MAX_RETRIES:
            try:
                async with AsyncClient() as client:
                    response = await client.post(
                        url=url,
                        headers=headers,
                        timeout=self.DEFAULT_TIMEOUT_CONFIG,
                    )
                    return response
            except ConnectTimeout:
                retries += 1
                logger.warning(f"Timeout na tentativa {retries}/{self.DEFAULT_MAX_RETRIES}. Retentando em {self.DEFAULT_RETRY_INTERVAL} segundos...")
                await asyncio.sleep(self.DEFAULT_RETRY_INTERVAL)
                
    @instrumented_trace(span_name="Request GET", kind=TraceInstruments.SPAN_KIND_CLIENT, span_parameters=False)
    async def get(self, url: str, headers: Optional[Dict[str, str]] = None):
        retries = 0
        while retries < self.DEFAULT_MAX_RETRIES:
            try:
                async with AsyncClient() as client:
                    response = await client.get(
                        url=url,
                        headers=headers,
                        timeout=self.DEFAULT_TIMEOUT_CONFIG,
                    )
                    return response
            except ConnectTimeout:
                retries += 1
                logger.warning(f"Timeout na tentativa {retries}/{self.DEFAULT_MAX_RETRIES}. Retentando em {self.DEFAULT_RETRY_INTERVAL} segundos...")
                await asyncio.sleep(self.DEFAULT_RETRY_INTERVAL)

class HttpClient:
    _instance = None 

    @classmethod
    def get_instance(cls, client_class: Optional[Type] = None):
        if cls._instance is None:
            cls._instance = client_class() if client_class else HttpxClient()
        return cls._instance
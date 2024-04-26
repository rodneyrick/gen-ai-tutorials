from httpx import AsyncClient
from typing import Optional, Dict, Type
from abc import ABC, abstractmethod

class HttpBaseInterface(ABC):
    
    @abstractmethod
    async def post(self, url: str, headers: Optional[Dict[str, str]] = None):
        pass
    
    @abstractmethod
    async def get(self, url: str, headers: Optional[Dict[str, str]] = None):
        pass

class HttpxClient(HttpBaseInterface):

    async def post(self, url: str, headers: Optional[Dict[str, str]] = None):
        async with AsyncClient() as client:
            response = await client.post(
                url=url,
                headers=headers,
            )
            return response
    
    async def get(self, url: str, headers: Optional[Dict[str, str]] = None):
        async with AsyncClient() as client:
            response = await client.get(
                url=url,
                headers=headers,
            )
            return response

class HttpClient:
    _instance = None 

    @classmethod
    def get_instance(cls, client_class: Optional[Type] = None):
        if cls._instance is None:
            cls._instance = client_class() if client_class else HttpxClient()
        return cls._instance
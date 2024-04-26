# from httpx import AsyncClient

# async def request_post(url, headers=None):
    
#     async with AsyncClient() as client:
#         response = await client.post(
#             url=url,
#             headers=headers
#         )
        
#         return response
    
# async def request_get(url, headers=None):
    
#     async with AsyncClient() as client:
#         response = await client.post(
#             url=url,
#             headers=headers
#         )
        
#         return response


from httpx import AsyncClient
from typing import Optional, Dict

# Classe base para a fábrica de clientes HTTP
class HttpClientFactory:
    def __init__(self):
        self.client_class = AsyncClient  # Cliente padrão é httpx

    def set_client_class(self, client_class):
        self.client_class = client_class  # Permite alterar o cliente HTTP

    # Função para criar um cliente HTTP
    def create_client(self):
        return self.client_class()

# Classe para encapsular operações HTTP usando o cliente da fábrica
class HttpClient:
    def __init__(self, factory: HttpClientFactory):
        self.factory = factory  # Injeção de dependência

    async def request_post(self, url: str, headers: Optional[Dict[str, str]] = None):
        # Use um cliente HTTP da fábrica
        async with self.factory.create_client() as client:
            response = await client.post(
                url=url,
                headers=headers,
            )
            return response
    
    async def request_get(self, url: str, headers: Optional[Dict[str, str]] = None):
        async with self.factory.create_client() as client:
            response = await client.get(
                url=url,
                headers=headers,
            )
            return response
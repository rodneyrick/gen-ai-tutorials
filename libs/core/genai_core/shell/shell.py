from genai_core.logging import logging, write_log, LogsConfigurations
from genai_core.telemetry import instrumented_trace, TraceInstruments
from typing import Optional, Dict, Type
from abc import ABC, abstractmethod
from datetime import datetime
import asyncio

logger = logging.getLogger()

class ShellBaseInterface(ABC):
    
    @abstractmethod
    async def exec(self, url: str, headers: Optional[Dict[str, str]] = None):
        pass
    
    @abstractmethod
    async def log(self, url: str, headers: Optional[Dict[str, str]] = None):
        pass

class AsyncIoSubprocess(ShellBaseInterface):

    #@instrumented_trace(span_name="Exec Command Bash", kind=TraceInstruments.SPAN_KIND_CLIENT)   
    async def exec(self, comando: list=[], log_name: str="log", cwd=None, return_stdout=False):

        process = await asyncio.create_subprocess_exec(
            *comando,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            return await self.log(stderr=stderr, process=process, comando=comando, log_name=log_name)
        
        if return_stdout:
            return stdout
        
        return True

    #@instrumented_trace(span_name="Write Log Error", span_parameters=False, type=TraceInstruments.INSTRUMENTS_EVENT)
    async def log(self, stderr, process, comando, log_name):
        now = datetime.now()
        timestamp= now.strftime("%Y%m%d-%H:%M:%S")
        log_name = f"{log_name}-{timestamp}.log"
        
        await write_log(log_name=log_name, content=stderr.decode())
        logger.error(
            f"Execucao falhou com codigo de erro: {process.returncode}\n"
            f"Verifique a saida no arquivo de log: {LogsConfigurations.LOG_PATH}/{log_name}"
            )
        raise ValueError(f"Nao foi possivel executar este comando shell: {' '.join(comando)}")
    
class ShellClient:
    _instance = None 

    @classmethod
    def get_instance(cls, client_class: Optional[Type] = None):
        if cls._instance is None:
            cls._instance = client_class() if client_class else AsyncIoSubprocess()
        return cls._instance
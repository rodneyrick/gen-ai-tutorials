from genai_core.logging import logging, write_log
from genai_core.telemetry import instrumented_trace, TraceInstruments
import subprocess
import os
import sys
import asyncio
from datetime import datetime

logs = "/var/tmp/genai/logs"
logger = logging.getLogger()

def exec_command(comando: list=[], log_path: str=f"{logs}/log.log", cwd: str=None):
    if not os.path.exists(logs):
        os.makedirs(logs)
        
    with open(os.path.join(logs,log_path), 'w') as log_file:
        try:
            subprocess.check_call(comando, stdout=log_file, stderr=subprocess.STDOUT, cwd=cwd)
        except subprocess.CalledProcessError as e:
            logger.error(f"Uma execução falhou com código de erro: {e.returncode}")
            logger.error(f"Verifique a saída no arquivo de log: {log_file.name}")
            logger.error(f"Comando executado: {' '.join(comando)}")
            sys.exit()

@instrumented_trace(span_name="Exec Command Bash", kind=TraceInstruments.SPAN_KIND_CLIENT)   
async def exec_commands(comando: list=[], log_name: str="log", cwd=None, return_stdout=False):

    process = await asyncio.create_subprocess_exec(
        *comando,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        now = datetime.now()
        timestamp= now.strftime("%Y%m%d-%H:%M:%S")
        log_name = f"{log_name}-{timestamp}.log"
        
        await write_log(log_name=log_name, content=stderr.decode())
        logger.error(
            f"Execucao falhou com codigo de erro: {process.returncode}\n"
            f"Verifique a saida no arquivo de log: {logs}/{log_name}"
            )
        raise ValueError(f"Nao foi possivel executar este comando shell: {' '.join(comando)}")
    
    if return_stdout:
        return stdout
    
    return True
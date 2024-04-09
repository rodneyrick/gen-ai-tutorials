import subprocess
import os
import logging
import sys

logs = "/workspaces/gen-ai-tutorials/app/logs"

def exec_command(comando: list=[], log_path: str=f"{logs}/log.log", cwd: str=None):
    if not os.path.exists(logs):
        os.makedirs(logs)
        
    with open(os.path.join(logs,log_path), 'w') as log_file:
        try:
            subprocess.check_call(comando, stdout=log_file, stderr=subprocess.STDOUT, cwd=cwd)
        except subprocess.CalledProcessError as e:
            logging.error(f"Uma execução falhou com código de erro: {e.returncode}")
            logging.error(f"Verifique a saída no arquivo de log: {log_file.name}")
            logging.error(f"Comando executado: {' '.join(comando)}")
            sys.exit()
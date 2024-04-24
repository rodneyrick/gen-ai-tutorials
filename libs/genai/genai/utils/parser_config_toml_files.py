
import tomllib
from pathlib import Path
import datetime

def run(config_name: str, dir_path: str = None):
    
    cwd = Path.cwd()
    if dir_path is not None:
        cwd = Path(dir_path)

    configs_ini_file_list = cwd.glob('*.toml')

    for f in configs_ini_file_list:
        if config_name == f.stem:
            f_path = f"{str(cwd)}/{f.name}"

            # Opening a Toml file using tomlib 
            with open(f_path,"rb") as toml: 
                toml_dict: dict = tomllib.load(toml) 

            return toml_dict

def convert_to_json_default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()

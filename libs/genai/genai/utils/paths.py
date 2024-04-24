import os

def get_cwd(file_path: str):
    return os.path.abspath(os.path.dirname(file_path))
from app.configs.settings import load_dotenv
from app.configs.settings import logging
from app.configs.settings import AppSettings

app_settings = AppSettings()

__all__ = [
    'load_dotenv', 'logging', 'app_settings'
]
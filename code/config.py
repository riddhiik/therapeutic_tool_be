from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # database related
    
    db_host: str
    db_port: int
    db_name: str
    db_pwd: str
    db_usr: str
    port: str
    SERVER: str

    class Config:
        env_file = Path(Path(__file__).resolve().parent) / ".env"
        print('The application started successfully 🚀')


setting = Settings()

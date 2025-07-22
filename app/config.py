from pydantic import BaseSettings, PostgresDsn, AnyHttpUrl, EmailStr
from typing import Optional
from typing import Any

class Settings(BaseSettings):
    # Database
    DATABASE_URL: PostgresDsn
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    ADMIN_EMAIL: str

    # misc.
    ADMIN_EMAIL: EmailStr
    MAIN_URL: AnyHttpUrl
    STREAMLIT_URL: AnyHttpUrl
    PROJECT_NAME: str

    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
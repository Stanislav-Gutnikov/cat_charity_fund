from pydantic import BaseSettings, EmailStr
from typing import Optional


class Settings(BaseSettings):
    app_title: str = 'QRKot'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'SECRET'
    first_superuser_email: Optional[EmailStr] = 'FIRST_SUPERUSER_EMAIL'
    first_superuser_password: Optional[str] = 'FIRST_SUPERUSER_PASSWORD'
    type: Optional[str] = 'TYPE'
    project_id: Optional[str] = 'PROJECT_ID'
    private_key_id: Optional[str] = 'PRIVATE_KEY_ID'
    private_key: Optional[str] = 'PRIVATE_KEY'
    client_email: Optional[str] = 'CLIENT_EMAIL'
    client_id: Optional[str] = 'CLIENT_ID'
    auth_uri: Optional[str] = 'AUTH_URI'
    token_uri: Optional[str] = 'TOKEN_URI'
    auth_provider_x509_cert_url: Optional[str] = 'AUTH_PROVIDER_X509_CERT_URL'
    client_x509_cert_url: Optional[str] = 'CLIENT_X509_CERT_URL'
    email: Optional[str] = 'EMAIL'

    class Config:
        env_file = '.env'


settings = Settings()

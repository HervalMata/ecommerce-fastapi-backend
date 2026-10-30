from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore", 
        case_sensitive=False
    )
    
    PROJECT_NAME: str = "Ecommerce FastAPI"

    DATABASE_URL: str
    BACKEND_URL: str
    FRONTEND_URL: str
    
settings = Settings()    
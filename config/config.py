from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    TOKEN: str
    PROXY: str

    @property
    def database_url_aiosqlite(self) -> str:
        return "sqlite+aiosqlite:///database/database.db"
    
    model_config = SettingsConfigDict(env_file="config/.env",extra="ignore")
settings = Settings()
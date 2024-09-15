from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Map AI App"
    MONGODB_URL: str
    DATABASE_NAME: str
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()

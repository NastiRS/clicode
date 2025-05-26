from pydantic_settings import BaseSettings


class AgentSettings(BaseSettings):
    MISTRAL_API_KEY: str
    MISTRAL_MODEL: str = "devstral-small-2505"

    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4.1-mini"

    DATABASE_PATH: str = "tmp/agent.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = AgentSettings()

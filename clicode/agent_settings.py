from pydantic_settings import BaseSettings


class AgentSettings(BaseSettings):
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    DATABASE_PATH: str = "./agent_sessions.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def get_settings():
    """Get settings and validate API key"""
    try:
        settings = AgentSettings()

        # If no API key is configured, show help message
        if not settings.OPENAI_API_KEY:
            print("⚠️  OPENAI_API_KEY not found")
            print("💡 Configure your OpenAI API key:")
            print("   - As environment variable: set OPENAI_API_KEY=your_key")
            print("   - Or create a .env file with: OPENAI_API_KEY=your_key")
            raise ValueError("OPENAI_API_KEY is required")

        return settings
    except Exception as e:
        if "OPENAI_API_KEY is required" in str(e):
            raise
        print(f"❌ Configuration error: {e}")
        raise


settings = get_settings()

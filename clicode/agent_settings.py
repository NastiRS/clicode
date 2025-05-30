from pydantic_settings import BaseSettings


class AgentSettings(BaseSettings):
    OPENROUTER_MODEL: str = "gpt-4.1-mini"
    OPENROUTER_API_KEY: str = ""
    DATABASE_PATH: str = "./agent_sessions.db"
    GITHUB_ACCESS_TOKEN: str = ""
    EXA_API_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def get_settings():
    """Get settings and validate API key"""
    try:
        settings = AgentSettings()

        # If no API key is configured, show help message
        if not settings.OPENROUTER_API_KEY:
            print("⚠️  OPENROUTER_API_KEY not found")
            print("💡 Configure your OpenRouter API key:")
            print("   - As environment variable: set OPENROUTER_API_KEY=your_key")
            print("   - Or create a .env file with: OPENROUTER_API_KEY=your_key")
            raise ValueError("OPENROUTER_API_KEY is required")

        return settings
    except Exception as e:
        if "OPENROUTER_API_KEY is required" in str(e):
            raise
        print(f"❌ Configuration error: {e}")
        raise


settings = get_settings()

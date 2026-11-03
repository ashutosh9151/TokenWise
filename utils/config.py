import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

load_dotenv()

class Settings(BaseModel):
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
    
    default_model: str = os.getenv("DEFAULT_MODEL", "groq/llama-3.3-70b-versatile")
    max_daily_budget_usd: float = float(os.getenv("MAX_DAILY_BUDGET_USD", "2.00"))
    
    enable_local_models: bool = os.getenv("ENABLE_LOCAL_MODELS", "true").lower() == "true"
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    use_bifrost: bool = os.getenv("USE_BIFROST", "true").lower() == "true"
    bifrost_base_url: str = os.getenv("BIFROST_BASE_URL", "http://localhost:8080")
    
    require_approval_file: bool = os.getenv("REQUIRE_APPROVAL_FOR_FILE_WRITES", "true").lower() == "true"
    require_approval_shell: bool = os.getenv("REQUIRE_APPROVAL_FOR_SHELL", "true").lower() == "true"

settings = Settings()

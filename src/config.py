"""
Xe-Bot Configuration Module
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()


class OpenRouterConfig(BaseModel):
    """OpenRouter API Configuration"""
    api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    default_model: str = os.getenv("DEFAULT_MODEL", "openai/gpt-4o-mini")


class DatabaseConfig(BaseModel):
    """Neon Database Configuration"""
    database_url: str = os.getenv("DATABASE_URL", os.getenv("NEON_DATABASE_URL", ""))


class AnimationConfig(BaseModel):
    """Animation Generation Configuration"""
    output_dir: Path = Path(os.getenv("ANIMATION_OUTPUT_DIR", "./output/animations"))
    quality: str = os.getenv("ANIMATION_QUALITY", "medium_quality")
    fps: int = int(os.getenv("ANIMATION_FPS", "30"))
    
    def __init__(self, **data):
        super().__init__(**data)
        self.output_dir.mkdir(parents=True, exist_ok=True)


class Config:
    """Main configuration class"""
    openrouter: OpenRouterConfig = OpenRouterConfig()
    database: DatabaseConfig = DatabaseConfig()
    animation: AnimationConfig = AnimationConfig()
    
    # Project paths
    BASE_DIR: Path = Path(__file__).parent.parent
    OUTPUT_DIR: Path = BASE_DIR / "output"
    CACHE_DIR: Path = BASE_DIR / "cache"
    
    @classmethod
    def setup_directories(cls):
        """Create necessary directories"""
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cls.animation.output_dir.mkdir(parents=True, exist_ok=True)


# Initialize config
config = Config()
config.setup_directories()

"""
Configuration management for the AI Proposal Deck Generator.
Handles environment variables, settings, and system requirements.
"""

import os
import sys
import logging
from typing import Tuple, List
from dataclasses import dataclass

# Default configuration values
DEFAULT_MODEL = "gemini-1.5-flash"
MEMORY_FILE = "proposal_agent_memory.json"
MAX_RETRIES = 3
RETRY_DELAY = 1

# Check if Gemini SDK is available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError as e:
    GEMINI_AVAILABLE = False

@dataclass
class AppConfig:
    """Application configuration class."""
    api_key: str = ""
    model: str = DEFAULT_MODEL
    memory_file: str = MEMORY_FILE
    max_retries: int = MAX_RETRIES
    retry_delay: float = RETRY_DELAY
    log_level: str = "INFO"
    output_dir: str = "proposals"
    logs_dir: str = "logs"

class ConfigManager:
    """Manages application configuration and environment setup."""
    
    def __init__(self):
        self.config = self._load_config()
        self._setup_logging()
    
    def _load_config(self) -> AppConfig:
        """Load configuration from environment variables."""
        return AppConfig(
            api_key=os.environ.get("GEMINI_API_KEY", ""),
            model=os.environ.get("GEMINI_MODEL", DEFAULT_MODEL),
            memory_file=os.environ.get("MEMORY_FILE", MEMORY_FILE),
            max_retries=int(os.environ.get("MAX_RETRIES", MAX_RETRIES)),
            retry_delay=float(os.environ.get("RETRY_DELAY", RETRY_DELAY)),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
            output_dir=os.environ.get("OUTPUT_DIR", "proposals"),
            logs_dir=os.environ.get("LOGS_DIR", "logs")
        )
    
    def _setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(f"{self.config.logs_dir}/app.log", mode='a')
            ]
        )
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate configuration and return issues."""
        issues = []
        
        if not self.config.api_key:
            issues.append("GEMINI_API_KEY environment variable not set")
        
        if not GEMINI_AVAILABLE:
            issues.append("google.generativeai package not installed (pip install google-generativeai)")
        
        # Check write permissions
        try:
            test_file = "test_write_permission.tmp"
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except Exception:
            issues.append("No write permission in current directory")
        
        return len(issues) == 0, issues
    
    def setup_directories(self):
        """Create necessary directories."""
        try:
            os.makedirs(self.config.output_dir, exist_ok=True)
            os.makedirs(self.config.logs_dir, exist_ok=True)
            return True
        except Exception as e:
            logging.error(f"Failed to create directories: {e}")
            return False
    
    def get_config(self) -> AppConfig:
        """Get current configuration."""
        return self.config

def check_system_requirements() -> bool:
    """Check system requirements and dependencies."""
    requirements = {
        'Python Version': {
            'check': lambda: sys.version_info >= (3, 7),
            'message': 'Python 3.7+ required'
        },
        'Gemini SDK': {
            'check': lambda: GEMINI_AVAILABLE,
            'message': 'Install with: pip install google-generativeai'
        },
        'Write Permissions': {
            'check': lambda: os.access('.', os.W_OK),
            'message': 'Write permission needed in current directory'
        }
    }
    
    print("🔍 Checking system requirements...")
    
    all_good = True
    for name, req in requirements.items():
        try:
            if req['check']():
                print(f"✅ {name}: OK")
            else:
                print(f"❌ {name}: {req['message']}")
                all_good = False
        except Exception as e:
            print(f"❌ {name}: Error checking - {e}")
            all_good = False
    
    return all_good

# Global configuration instance
config_manager = ConfigManager()
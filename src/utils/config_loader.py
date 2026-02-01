"""Configuration loader for the competitive intelligence system."""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


class ConfigLoader:
    """Loads and manages configuration from YAML and environment variables."""

    def __init__(self, config_path: str = None):
        """Initialize the config loader.

        Args:
            config_path: Path to the config.yaml file. If None, uses default location.
        """
        # Load environment variables
        load_dotenv()

        # Determine config file path
        if config_path is None:
            config_path = os.getenv('CONFIG_PATH')

        if config_path is None:
            # Default to config/config.yaml relative to project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / 'config' / 'config.yaml'

        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        return config

    def _validate_config(self):
        """Validate required configuration fields and environment variables."""
        required_sections = ['competitors', 'collection', 'processing', 'reporting', 'database']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required config section: {section}")

        # Validate environment variables
        required_env_vars = ['ANTHROPIC_API_KEY', 'NEWSAPI_KEY', 'GMAIL_USERNAME', 'GMAIL_APP_PASSWORD']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]

        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation.

        Args:
            key_path: Dot-separated path to the config value (e.g., 'collection.lookback_days')
            default: Default value if key not found

        Returns:
            The configuration value
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_env(self, key: str, default: str = None) -> str:
        """Get an environment variable.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            The environment variable value
        """
        return os.getenv(key, default)

    def get_competitors(self) -> list:
        """Get the list of competitors."""
        return self.config.get('competitors', [])

    def get_database_path(self) -> Path:
        """Get the absolute path to the database file."""
        db_path = self.config.get('database', {}).get('path', 'data/competitive_intel.db')

        if not Path(db_path).is_absolute():
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / db_path

        return Path(db_path)

    def get_log_path(self) -> Path:
        """Get the absolute path to the log file."""
        log_path = self.config.get('logging', {}).get('file', 'data/logs/competitive_intel.log')

        if not Path(log_path).is_absolute():
            project_root = Path(__file__).parent.parent.parent
            log_path = project_root / log_path

        return Path(log_path)

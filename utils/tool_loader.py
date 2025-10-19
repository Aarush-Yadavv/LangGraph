import os
import re
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def replace_env_variables(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Replace environment variable placeholders in config with actual values
    
    Placeholders format: {{ENV_VAR_NAME}}
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dict with environment variables replaced
    """
    def replace_value(value):
        if isinstance(value, str):
            # Find all {{VAR_NAME}} patterns
            pattern = r'\{\{([A-Z_]+)\}\}'
            matches = re.findall(pattern, value)
            
            for match in matches:
                env_value = os.getenv(match, '')
                if not env_value:
                    print(f"Warning: Environment variable {match} not found")
                value = value.replace(f'{{{{{match}}}}}', env_value)
            
            return value
        elif isinstance(value, dict):
            return {k: replace_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [replace_value(item) for item in value]
        else:
            return value
    
    return replace_value(config)


def load_tools_config(step: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Load and configure tools for a workflow step
    
    Args:
        step: Workflow step configuration
        
    Returns:
        Dictionary of configured tools
    """
    tools = {}
    
    for tool in step.get('tools', []):
        tool_name = tool['name']
        tool_config = replace_env_variables(tool.get('config', {}))
        tools[tool_name] = tool_config
    
    return tools


def get_env_variable(name: str, default: str = None) -> str:
    """
    Get environment variable with optional default
    
    Args:
        name: Environment variable name
        default: Default value if not found
        
    Returns:
        Environment variable value
    """
    value = os.getenv(name, default)
    if value is None:
        raise ValueError(f"Environment variable {name} is required but not set")
    return value


def validate_api_keys(required_keys: list) -> bool:
    """
    Validate that required API keys are set
    
    Args:
        required_keys: List of required environment variable names
        
    Returns:
        True if all keys are set, False otherwise
    """
    missing_keys = []
    
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        print(f"Missing required API keys: {', '.join(missing_keys)}")
        return False
    
    return True
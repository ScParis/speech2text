import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configuration file path
CONFIG_FILE = os.path.expanduser('~/.speech2text_config.json')

def update_gemini_config(api_url, api_key):
    """
    Update Gemini API configuration securely.
    
    Args:
        api_url (str): URL for the Gemini API endpoint
        api_key (str): API key for authentication
    """
    # Validate inputs
    if not api_url or not api_key:
        logging.error("API URL and Key must not be empty")
        return False
    
    # Mask the API key for logging
    masked_key = api_key[:5] + '*' * (len(api_key) - 10) + api_key[-5:]
    logging.info(f"Updating Gemini API configuration with URL: {api_url}")
    logging.info(f"API Key (masked): {masked_key}")
    
    # Create configuration dictionary
    config = {
        'gemini_api_url': api_url,
        'gemini_api_key': api_key
    }
    
    # Write to config file with restricted permissions
    try:
        # Ensure config directory exists with secure permissions
        config_dir = os.path.dirname(CONFIG_FILE)
        os.makedirs(config_dir, exist_ok=True)
        os.chmod(config_dir, 0o700)  # Only readable by the owner
        
        # Write config file
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        
        # Set secure file permissions
        os.chmod(CONFIG_FILE, 0o600)  # Only readable and writable by the owner
        
        # Set environment variables
        os.environ['GEMINI_API_URL'] = api_url
        os.environ['GEMINI_API_KEYVS'] = api_key
        
        return True
    except Exception as e:
        logging.error(f"Failed to save configuration: {e}")
        return False

def load_gemini_config():
    """
    Load Gemini API configuration from file.
    
    Returns:
        dict: Configuration with API URL and key, or empty dict
    """
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            
            # Validate configuration
            if not config.get('gemini_api_url') or not config.get('gemini_api_key'):
                logging.warning("Incomplete API configuration")
                return {}
            
            # Set environment variables
            os.environ['GEMINI_API_URL'] = config['gemini_api_url']
            os.environ['GEMINI_API_KEYVS'] = config['gemini_api_key']
            
            return config
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
    
    return {}

# Suppress printing of API key
GEMINI_API_KEY = None  # Remove direct printing of API key

# Load configuration on module import
load_gemini_config()

# GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent'
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent'
import os
import json

CONFIG_FILE = os.path.expanduser('~/.speech2text_config.json')

def update_gemini_config(api_url, api_key):
    """
    Update Gemini API configuration.
    
    Args:
        api_url (str): URL for the Gemini API endpoint
        api_key (str): API key for authentication
    """
    # Validate inputs
    if not api_url or not api_key:
        raise ValueError("API URL and Key must not be empty")
    
    # Create configuration dictionary
    config = {
        'gemini_api_url': api_url,
        'gemini_api_key': api_key
    }
    
    # Write to config file
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        
        # Set environment variables
        os.environ['GEMINI_API_URL'] = api_url
        os.environ['GEMINI_API_KEYVS'] = api_key
    except Exception as e:
        raise RuntimeError(f"Failed to save configuration: {str(e)}")

def load_gemini_config():
    """
    Load Gemini API configuration from file.
    
    Returns:
        dict: Configuration with API URL and key
    """
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            
            # Set environment variables
            os.environ['GEMINI_API_URL'] = config.get('gemini_api_url', '')
            os.environ['GEMINI_API_KEYVS'] = config.get('gemini_api_key', '')
            
            return config
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
    
    return {}

# Load configuration on module import
load_gemini_config()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEYVS')
print(GEMINI_API_KEY)


# GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent'
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent'
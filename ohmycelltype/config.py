from ohmycelltype import write_json,load_json
import os

BASE_CONFIG = {
    "n1n": {
        "base_url":"https://api.n1n.ai/v1",
        "api":"",
        
        "parm_collect_model": "gpt-5.4",
        "report_model": "claude-sonnet-4-6",
        
        "annotation_model": [
            "gpt-5.4",
            "qwen3.5-397b-a17b",
            "grok-4.2",
            "glm-5",
            "deepseek-v3.2"
        ],
        
        "audit_model": "claude-sonnet-4-6",
        "consensus_model": "claude-sonnet-4-6",
        
        "max_reflect_times": 3,
        "reliability_threshold": 70,

        "max_retry": 3
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api": "",
        
        "parm_collect_model": "openai/gpt-4o-mini",
        "report_model": "openai/gpt-4o-mini",
        
        "annotation_model": [
            "openai/gpt-5.4",
            "z-ai/glm-5",
            "google/gemini-3.1-pro-preview"
        ],
        
        "audit_model": "anthropic/claude-sonnet-4.6",
        "consensus_model": "anthropic/claude-sonnet-4.6",
        
        "max_reflect_times": 3,
        "reliability_threshold": 70,

        "max_retry": 3
    }
}

class Config:
    def __init__(self) -> None:
        self.config = BASE_CONFIG
        self.home_dir = os.environ.get('HOME')
    
    def init(self):
        write_json(self.config, f"{self.home_dir}/ohmycelltype.json")
    
    def load_config(self):
        return load_json(f"{self.home_dir}/ohmycelltype.json")

    def set_api(self, provider, api_key):
        
        if os.path.exists(f"{self.home_dir}/ohmycelltype.json"):
            self.config = self.load_config()
        
        else:
            raise FileNotFoundError(f"Config file not found at {self.home_dir}/ohmycelltype.json. Please run ohmycelltype init_config  to create it.")

        if provider in self.config:
            self.config[provider]['api'] = api_key
            write_json(self.config, f"{self.home_dir}/ohmycelltype.json")
        else:
            print(f"Provider {provider} not found in config.")
    
    def get_path(self):
        return f"{self.home_dir}/ohmycelltype.json"

    def show(self):
        if os.path.exists(f"{self.home_dir}/ohmycelltype.json"):
            config = self.load_config()
            for provider, details in config.items():
                print(f"Provider: {provider}")
                for key, value in details.items():
                    if key == 'api':
                        print(f"  {key}: {'*' * len(value) if value else 'Not Set'}")
                    else:
                        print(f"  {key}: {value}")
        else:
            print(f"Config file not found at {self.home_dir}/ohmycelltype.json. Please run ohmycelltype init_config  to create it.")
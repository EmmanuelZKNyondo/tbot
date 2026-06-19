# core/loader.py

import json
import os
from core.exceptions import ConfigError

def load_dotenv(env_path: str = ".env", override: bool = False):
    if not os.path.exists(env_path):
        return False

    with open(env_path, "r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            if "=" not in stripped:
                continue

            key, value = stripped.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if override or key not in os.environ:
                os.environ[key] = value

    return True


class ConfigLoader:
  """
  Central config loader for Tbot. 
  Loads and validates config safely (structure).
  """
  
  def __init__(self, config_path="config/settings.json"):
      self.config_path = config_path
      self._config = None
      load_dotenv()
      self._load_config()
      self._validate_config()
  
      
  def _load_config(self):
    if not os.path.exists(self.config_path):
      raise FileNotFoundError(f"Config file not found: {self.config_path}")
    
    try:
      with open(self.config_path, "r") as file:
        self._config = json.load(file)

    except json.JSONDecodeError as e:
      raise ConfigError(
        f"Invalid JSON in '{self.config_path}'. "
        f"Line {e.lineno}, Column {e.colno}: {e.msg}"
      )

    except Exception as e:
      raise ConfigError(
        f"Unable to load config file: {e}"
      )
  
      
  def _validate_config(self):
    required_sections = [
      "system", 
      "account_profiles", 
      "risk_governor",
      "execution_engine", 
      "decision_engine", 
      "pairs"
    ]
    
    for section in required_sections:
      if section not in self._config:
        raise ValueError(f"Missing required config section: {section}")
      
    if "name" not in self._config["system"]:
      raise ValueError("Missing 'name' in system config")
  
  
  # --------------------------------------
  # ACCOUNT RESOLUTION (NEW CORE FEATURE)
  # --------------------------------------    
  def get_active_account(self):
    """
    Resolves account credentials from: JSON profile + .env
    """
    profiles = self._config["account_profiles"]
    active = profiles["active_profile"]
    profile = profiles["profiles"][active]
    env_key = profile["env_key"]
    
    account_id = os.getenv(env_key)
    password = os.getenv(env_key.replace("ACCOUNT", "PASSWORD"))
    server = os.getenv(env_key.replace("ACCOUNT", "SERVER"))
    
    if not account_id:
      raise ValueError(f"Missing account id in .env for {env_key}")
    
    return {
      "profile": active,
      "account_id": account_id,
      "password": password,
      "server": server,
      "mode": profile.get("risk_mode", "live"),
      "base_currency": profile.get("base_currency", "USD")
    }
      
  
  # -----------------------
  # GENERIC SECTION LOADER
  # -----------------------
  def get(self, section, key=None, default=None):
    try:
      value = self._config[section]

      if key:
        return value.get(key, default)
          
      return value
    except KeyError:
      return default
      
  # --------------------
  # SAFE ACCESS METHODS
  # --------------------
  def get_system_config(self):
    return self._config["system"]

  
  def get_account_profiles(self):
    return self._config["account_profiles"]

  
  def get_risk_governor_config(self):
    return self._config["risk_governor"]


  def get_execution_engine_config(self):
    return self._config["execution_engine"]


  def get_decision_engine_config(self):
    return self._config["decision_engine"]


  def get_pairs(self):
    return self._config["pairs"]    


  def get_pairs_config(self, symbol: str):
    pairs = self._config["pairs"]
    
    if symbol not in pairs:
      raise ValueError(f"Symbol/Pair not found in config: {symbol}")
    
    return pairs[symbol]
  
  
  def reload(self):
    """ Manual config reload (useful for live tuning). """
    self._load_config()
    self._validate_config()
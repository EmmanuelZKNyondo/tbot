# engine/filters.py

from datetime import datetime

class TradingFilters:
  """
  Env trade filters
  Determines whether trading conditions are acceptable
  """
  
  def __init__(self, config_loader, logger = None):
    self.config = config_loader
    self.logger = logger
  
  
  # ---------------------------
  # MAIN ENTRY 
  # ---------------------------
  def validate(self, symbol, market_metrics):
    checks = [
      self._check_spread(market_metrics),
      self._check_session(symbol, market_metrics),
      self._check_weekend(),
      self._check_volatility(symbol, market_metrics)
    ]
    
    for approved, reason in checks:
      if not approved:
        if self.logger:
          self.logger.log_rejected_trade(symbol, reason, market_metrics)
          
        return False, reason
    
    return True, "Approved"
  
  
  # ----------------------------
  # SPREAD FILTER
  # ----------------------------
  def _check_spread(self, market_metrics):
    execution_config = (self.config.get_execution_engine())
    
    if not execution_config["spread_filter_enabled"]:
      return True, "OK"
    
    maximum = execution_config["max_allowed_spread"]
    current = market_metrics["spread"]
    
    if current > maximum:
      return False, "Spread too high"
    
    return True, "OK"
  
  
  # ----------------------------
  # SESSION FILTER
  # ----------------------------
  def _check_session(self, symbol, market_metrics):
    pair_config = (self.config.get_pair_config(symbol))
    
    allowed_sessions = (pair_config["sessions"]["allowed"])
    current_session = (market_metrics["session"])
    
    if current_session not in allowed_sessions:
      return False, "Session not allowed / listed"
    
    return True, "OK"
  
  
  # ----------------------------
  # WEEKEND FILTER
  # ----------------------------
  def _check_weekend(self):
    filters = (self.config_get_global_filters())
    
    if not filters["avoid_weekends"]:
      return True, "OK"
    
    weekday = datetime.now(datetime.timezone.utc).weekday()
    if weekday >= 5:
      return False, "Weekend"
    
    return True, "OK"
  
  
  # ---------------------------
  # VOLATILITY FILTER
  # ---------------------------
  def _check_volatility(self, symbol, market_metrics):
    pair_config = (self.config.get_pair_config(symbol))
    conditions = pair_config["market_conditions"]
    atr = market_metrics["atr"]
    
    if conditions.get("avoid_low_volatility", False): 
      minimum = conditions["min_atr_threshold"]
      
      if atr < minimum:
        return (False, "Low volatility")
      
    if "max_atr_threshold" in conditions:
      maximum = conditions["max_atr_threshold"]
      
      if atr > maximum:
        return (False, "High Volatility")
    
    return True, "OK"
  
  
     
# market/market_metrics.py
from datetime import datetime

class MarketMetrics:
  
  def __init__(self, executor, logger = None):
    self.executor = executor
    self.logger = logger
    
  
  def build(self, symbol, atr_value):
    return {
      "spread": self.executor.get_spread(symbol),
      "session": self.get_current_session(),
      "atr": atr_value
    }
    
    
  def get_current_session(self):
    hour = datetime.now(datetime.timezone.utc).hour
    
    # Asian
    if 0 <= hour < 8:
      return "asian"
    
    # London
    if 8 <= hour < 13:
      return "london"
    
    # New York
    if 13 <= hour < 22:
      return "new_york"
    
    return "closed"
    
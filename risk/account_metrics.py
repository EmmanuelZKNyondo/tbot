# risk/account_metrics.py

from datetime import datetime

class AccountMetrics:
  
  def __init__(self, executor, logger = None):
    self.executor = executor
    self.logger = logger
    
  
  # -----------------------
  # BUILD METRICS
  # -----------------------
  def build(self):
    info = self.executor.get_account_info()
    balance = info["balance"]
    equity = info["equity"]
    
    floating_profit = info["profit"]
    
    total_drawdown_percent = ( max(0, ((balance - equity)/balance) * 100) if balance > 0 else 0 )
    
    metrics = {
      "balance": balance,
      "equity": equity,
      "floating_profit": floating_profit,
      "total_drawdown_percent": round(total_drawdown_percent, 2),
      "daily_drawdown_percent": 0,
      "weekly_drawdown_percent": 0
    }
    
    return metrics
# risk/exposure.py
from datetime import datetime, timedelta
 
class ExposureManager:
  """
  Capital protection layer
  
  Prevents excessive risk exposure at trade, portfolio and account levels
  """ 
  
  def __init__(self, config_loader, logger = None):
    self.config = config_loader
    self.logger = logger
    
  
  # ======================================
  # MAIN ENTRY
  # ======================================
  def validate(self, symbol:str, account_metrics: dict, portfolio_metrics: dict, pair_metrics: dict) -> tuple[bool, str]:
    """
    Returns: 
    
    (True, "Approved")
    or
    
    (False, reason)
    """
    
    checks = [
      self._check_max_open_positions( symbol, pair_metrics),
      self._check_daily_trade_limit(symbol, pair_metrics),
      self._check_weekly_trade_limit(symbol, pair_metrics),
      self._check_consecutive_losses(symbol, pair_metrics),
      self._check_cooldown_period(symbol, pair_metrics),
      
      self._check_portfolio_positions(portfolio_metrics),
      
      self._check_daily_drawdown(account_metrics),
      self._check_weekly_drawdown(account_metrics),
      self._check_total_drawdown(account_metrics)
    ]
    
    for approved, reason in checks:
      if not approved: 
        if self.logger:
          self.logger.log_rejected_trade(symbol, reason, {})
        
        return False, reason
      
    return True, "Approved"
  
  
  # -----------------------------------
  # PAIR LEVEL
  # -----------------------------------
  def _check_max_open_positions(self, symbol, pair_metrics):
    pair_config = self.config.get_pair_config(symbol)
    
    allowed = pair_config["risk_management"]["max_open_positions"]
    
    current = pair_metrics["open_positions"]
    
    if current >= allowed: 
      return False, "Maximum open positions reached"
    
    return True, "OK"
  
  
  def _check_daily_trade_limit(self, symbol, pair_metrics):
    pair_config = self.config.get_pair_config(symbol)
    limit_ = pair_config["trade_limits"]["max_trades_per_day"] 
    current = pair_metrics["trades_today"]
    
    if current >= limit_:
      return False, "Maximum daily trades reached"
    
    return True, "OK"
  
  
  def _check_weekly_trade_limit(self, symbol, pair_metrics):
    pair_config = self.config.get_pair_config(symbol)
    limit_ = pair_config["trade_limits"].get("max_trades_per_week", 99)
    current = pair_metrics["trades_this_week"]
    
    if current >= limit_:
      return False, "Maximum weekly trades reached"
    
    return True, "OK"
  
  
  def _check_consecutive_losses(self, symbol, pair_metrics):
    pair_config = self.config.get_pair_config(symbol)
    allowed = pair_config["trade_limits"]["max_consecutive_losses"]
    losses = pair_metrics["consecutive_losses"]
    
    if losses >= allowed: 
      return False, "Maximum consecutive losses reached"
    
    return True, "OK"
  
  
  def _check_cooldown_period(self, symbol, pair_metrics):
    pair_config = self.config.get_pair_config(symbol)
    cooldown_minutes = pair_config["trade_limits"]["cooldown_after_loss_minutes"]
    last_loss_time = pair_metrics.get("last_loss_time")
    
    if last_loss_time is None:
      return True, "OK"
    
    elapsed = (datetime.now(datetime.timezone.utc) - last_loss_time)
    
    if elapsed < timedelta(minutes = cooldown_minutes):
      return False, "Loss cooldown active"
    
    return True, "OK"
  
  
  # ---------------------------
  # PORTFOLIO LEVEL
  # ---------------------------
  def _check_portfolio_positions(self, portfolio_metrics):
    maximum = self.config._config["portfolio_layer"]["max_simultaneous_positions"]
    current = portfolio_metrics["open_positions"]
    
    if current >= maximum:
      return False, "Portfolio position limit reached"
    
    return True, "OK"
  
  
  # ------------------------
  # ACCOUNT LEVEL
  # ------------------------
  def _check_daily_drawndown(self, account_metrics):
    governor = self.config.get_risk_governor()
    limit_ = governor["daily_drawdown_limit_percent"]
    current = account_metrics["daily_drawdown_percent"]
    
    if current >= limit_:
      return False, "Daily drawdown limit exceeded"
    
    return True, "OK"
  
  
  def _check_weekly_drawdown(self, account_metrics):
    governor = self.config.get_risk_governor()
    limit_ = governor["weekly_drawdown_limit_percent"]
    current = account_metrics["weekly_drawdown_percent"]
    
    if current >= limit_:
      return False, "Weekly drawdown limit exceeded"
    
    return True, "OK"
  
  
  def _check_total_drawdown(self, account_metrics):
    governor = self.config.get_risk_governor()
    limit_ = governor["max_total_drawdown_percent"]
    current = account_metrics["total_drawdown_percent"]
    
    if current >= limit_:
      return False, "Maximum drawdown exceeded"
    
    return True, "OK"
# risk/sltp.py

class SLTPManager:
  """
  Central stop loss and take profit engine
  """
  
  def __init__(self, config_loader, logger = None):
    self.config = config_loader
    self.logger = logger
  
  
  # ----------------------
  # STOP LOSS
  # ----------------------
  def calculate_stop_loss(self, symbol, entry_price, direction, atr_value):
    pair_config = self.config.get_pair_config(symbol)
    settings = pair_config["stop_loss_take_profit"]
    multiplier = settings["atr_multiplier"]
    
    distance = atr_value * multiplier
    
    if direction == "BUY":
      stop_loss = (entry_price - distance)
    else:
      stop_loss = (entry_price + distance)
      
    return stop_loss
  
  
  # -----------------------
  # TAKE PROFIT
  # -----------------------
  def calculate_take_profit(self, symbol, entry_price, stop_loss, direction):
    pair_config = self.config.get_pair_config(symbol)
    settings = pair_config["stop_loss_take_profit"]
    rr = settings["risk_reward_ratio"]
    
    risk_distance = abs(entry_price - stop_loss)
    reward_distance = (risk_distance * rr)
    
    if direction == "BUY":
      take_profit = (entry_price + reward_distance)
    else:
      take_profit = (entry_price - reward_distance)
    
    return take_profit
  
  
  # -----------------------
  # BREAK EVEN
  # -----------------------
  def should_move_to_break_even(self, symbol, current_rr):
    pair_config = self.config.get_pair_config(symbol)
    trigger = pair_config["stop_loss_take_profit"]["break_even_at_rr"]
    
    return current_rr >= trigger
  
  
  # ----------------------
  # TRAILING STOP
  # ----------------------
  def trailing_enabled(self, symbol):
    return self.config.get_pair_config(symbol)["stop_loss_take_profit"]["trailing_stop_enabled"]
    
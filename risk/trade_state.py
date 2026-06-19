# risk/trade_state.py

from datetime import datetime

class TradeState: 
  def __init__(self):
    self.state = {}
    
  
  def initialize_symbol(self, symbol: str):
    if symbol not in self.state:
      self.state[symbol] = {
        "trades_today": 0,
        "trades_this_week": 0,
        "consecutive_losses": 0,
        "cooldown_active": False,
        "last_trade_time": None,
        "open_positions": 0
      }
      
  
  def get_symbol_state(self, symbol: str):
    self.initialize_symbol(symbol)
    return self.state[symbol]
  
  
  def register_trade_open(self, symbol: str, direction: str):
    self.initialize_symbol(symbol)
    state = self.state[symbol]

    state["trades_today"] += 1
    state["trades_this_week"] += 1

    state["open_positions"] += 1
    state["last_trade_time"] = datetime.now(datetime.timezone.utc)
    state["last_direction"] = direction
        
        
  def register_trade_close( self, symbol: str ):
    self.initialize_symbol(symbol)
    state = self.state[symbol]

    if state["open_positions"] > 0:
        state["open_positions"] -= 1
            
  
  def register_win( self, symbol: str ):
    self.initialize_symbol(symbol)
    state = self.state[symbol]
    
    state["wins"] += 1
    state["consecutive_wins"] += 1
    state["consecutive_losses"] = 0
        
        
  def register_loss( self, symbol: str ):
    self.initialize_symbol(symbol)
    state = self.state[symbol]

    state["losses"] += 1
    state["consecutive_losses"] += 1
    state["consecutive_wins"] = 0
        
  
  def set_cooldown( self, symbol: str, until ):
    self.initialize_symbol(symbol)
    self.state[symbol]["cooldown_until"] = until
        
  
  def is_in_cooldown(self, symbol: str):
    self.initialize_symbol(symbol)
    cooldown = self.state[symbol]["cooldown_until"]

    if cooldown is None:
      return False

    return datetime.now(datetime.timezone.utc) < cooldown
  
  
  def reset_daily(self):
    for symbol in self.state:
      self.state[symbol]["trades_today"] = 0


  def reset_weekly(self):
    for symbol in self.state:
      self.state[symbol]["trades_this_week"] = 0
# risk/pair_metrics.py

class PairMetrics:
  """
  Maintains pair-specific trading state
  """
  
  def __init__(self, trade_state):
    self.trade_state = trade_state
    
  
  def build(self, symbol):
    state = self.trade_state.get_symbol_state(symbol)
    return {
      "trades_today": state["trades_today"],
      "consecutive_losses": state["consecutive_losses"],
      "cooldown_active": state["cooldown_active"],
      "open_positions": state["open_positions"]
    }
    
# execution/executor.py
from execution.broker_mt5_direct import MT5DirectBroker

class ExecutionRouter:
  """
  Central execution abstraction layer
  
  Routes all trading operations to the correct backend
  - mt5_direct
  - mt5_bridge
  """
  
  def __init__(self, config_loader, logger = None):
    self.config = config_loader
    self.logger = logger
    self.mode = self.config.get_execution_engine_config().get("mode", "mt5_direct")
    self.account = self.config.get_active_account()
    self.broker = self._initialize_broker()
    
    
  # ---------------------------
  # INITIALIZATION
  # --------------------------- 
  def _initialize_broker(self):
    if self.mode == "mt5_direct":
      broker = MT5DirectBroker(account_config = self.account, logger = self.logger)
      broker.connect()
      return broker
    elif self.mode == "mt5_bridge":
      raise NotImplementedError("MT5 Bridge mode not implemented yet")
    else:
      raise ValueError(f"Unknown execution mode: {self.mode}")
    
  # --------------------------
  # UNIFIED INTERFACE
  # --------------------------
  def place_order(self, symbol: str, direction: str, volume: float, sl: float = None, tp: float = None):
    return self.broker.place_order(
      symbol=symbol,
      order_type=direction,
      volume=volume,
      sl=sl,
      tp=tp
    )
  
    
  def close_position(self, ticket: int, volume: float, symbol: str):
    return self.broker_close_position(
      ticket=ticket,
      volume=volume,
      symbol=symbol
    )
  
    
  def get_position(self, symbol: str = None):
    return self.broker.get_positions(symbol)
  
  
  def get_account_info(self):
    return self.broker.get_account_info()
  
  
  # -----------------------------
  # MARKET DATA DELEGATION
  # -----------------------------
  def get_tick(self, symbol: str):
    return self.broker.get_tick(symbol)
  
  
  def get_candles(self, symbol: str, timeframe, count: int = 100):
    return self.broker.get_candles(
      symbol, 
      timeframe, 
      count
    )
    
  
  def get_spread(self, symbol: str):
    return self.broker.get_spread(symbol)
  
  
  # ---------------------------
  # SAFE SHUTDOWN
  # ---------------------------
  def shutdown(self):
    if self.logger:
      self.logger.log_system("Shutting down execution router")
      
    self.broker.disconnect()
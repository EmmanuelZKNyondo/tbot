# execution/broker_mt5_direct.py

import MetaTrader5 as mt5
from datetime import datetime

class MT5DirectBroker:
  """
  Direct MT5 integration
  - Login to MT5 terminal
  - Fetch market data
  - Execute trades
  - Manage positions
  """
  
  
  def __init__(self, account_config, logger = None):
    self.account = account_config
    self.logger = logger
    self.connected = False
    
    
  # ------------------------
  # CONNECTION
  # ------------------------
  def connect(self):
    """
    Initialize MT5 session
    """
    initialized= mt5.initialize()
    
    if not initialized: 
      raise ConnectionError(f"MT5 Initialization Failed")
    
    login = int(self.account["account_id"])
    password = self.account["password"]
    server = self.account["server"]
    
    authorized = mt5.login(login, password = password, server = server)
    
    if not authorized:
      raise ConnectionError("MT5 Login Failed")

    self.connected = True
    
    if self.logger:
      self.logger.log_system(f"MT5 connected: {login}")
      
    return True
  
  
  # -------------------------
  # MARKET DATA
  # -------------------------
  def get_tick(self, symbol: str):
    """
    Get latest tick data
    """
    
    tick = mt5.symbol_info_tick(symbol)
    
    if tick is None:
      return None
    
    return {
      "symbol": symbol,
      "bid": tick.bid,
      "ask": tick.ask,
      "time": tick.time
    }
    
  
  def get_spread(self, symbol: str):
    """
    Calculate current spread
    """
    tick = self.get_tick(symbol)
    
    if not tick:
      return None
    
    return tick["ask"] - tick["bid"]
  
  
  
  def get_candles(self, symbol: str, timeframe, count: int = 100):
    """
    Fetch OHLC candles
    """
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
    
    if rates is None:
      return None
    
    candles = []
    
    for r in rates:
      candles.append({
        "time": datetime.utcfromtimestamp(r["time"]),
        "open": r["open"],
        "high": r["high"],
        "low": r["low"],
        "close": r["close"],
        "volume": r["tick_volume"]
      })
      
    return candles
  
  
  # ----------------------------
  # ORDER EXECUTION
  # ----------------------------
  def place_order(self, symbol: str, order_type: str, volume: float, sl: float = None, tp: float = None):
    """
    Execute market order
    """
    if order_type == "BUY":
      trade_type = mt5.ORDER_TYPE_BUY
    elif order_type == "SELL":
      trade_type = mt5.ORDER_TYPE_SELL
    else:
      raise ValueError("invalid order type")
    
    tick = mt5.symbol_info_tick(symbol)
    
    price = tick.ask if order_type == "BUY" else tick.bid
    
    request = {
      "action": mt5.TRADE_ACTION_DEAL,
      "symbol": symbol,
      "volume": volume,
      "type": trade_type,
      "price": price,
      "sl": sl,
      "tp": tp,
      "deviation": 20,
      "magic": 123456,
      "comment": "TBot execution",
      "type_time": mt5.ORDER_TIME_GTC,
      "type_filling": mt5.ORDER_FILLING_IOC
    }
    
    result = mt5.order_send(request)
    
    if self.logger:
      self.logger.log_trade_execution(
        symbol,
        order_type,
        volume,
        result.retcode
      )
      
    return result
  
  
  # -----------------------
  # POSITION MANAGEMENT
  # -----------------------
  def get_positions(self, symbol: str = None):
    """
    Get open positions
    """
    positions = mt5.positions_get(symbol = symbol)
    
    if not positions is None:
      return None
    
    return positions
    
  
  def close_position(self, ticket: int, volume: float, symbol: str):
    """
    Close existing position
    """
    position = mt5.positions_get(ticket = ticket)
    
    if not position: 
      return None
    
    pos = position[0]
    
    close_type = ( mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY )
    
    tick = mt5.symbol_info_tick(symbol)
    
    price = tick.bid if close_type == mt5.ORDER_TYPE_SELL else tick.ask
    
    request = {
      "action": mt5.TRADE_ACTION_DEAL,
      "symbol": symbol,
      "volume": volume,
      "type": close_type,
      "position": ticket,
      "price": price,
      "deviation": 20,
      "magic": 123456,
      "comment": "TBot close",
      "type_time": mt5.ORDER_TIME_GTC,
      "type_filling": mt5.ORDER_FILLINF_IOC
    }
    
    return mt5.order_send(request)
  
  
  # -----------------------------
  # ACCOUNT INFO
  # -----------------------------
  def get_account_info(self):
    """
    Get account state
    """
    info = mt5.account_info()
    
    if info is None:
      return None
    
    return {
      "balance": info.balance,
      "equity": info.equity,
      "margin": info.margin,
      "free_margin": info.margin_free,
      "profit": info.profit
    }
    
  
  # ----------------------------
  # DISCONNECT
  # ----------------------------
  def disconnect(self):
    """
    Shutdown MT5 connection
    """
    mt5.shutdown()
    self.connect = False
    
    if self.logger:
      self.logger.log_system("MT5 disconnected")
    
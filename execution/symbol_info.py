# execution/symbol_info.py

import MetaTrader5 as mt5

class SymbolInfoProvider:
  """
  Broker symbol specifications
  """
  
  def __init__(self, logger = None):
    self.logger = logger
    
    
  def get(self, symbol):
    info = mt5.symbol_info(symbol)
    
    if info is None: 
      raise ValueError(f"Unable to retreive symbol info: {symbol}")
    
    return {
      "symbol": symbol,
      "digits": info.digits,
      "point": info.point,
      "tick_size": info.trade_tick_size,
      "tick_value": info.trade_tick_value,
      "contract_size": info.trade_contract_size,
      "volume_step": info.volume_step,
      "min_volume": info.volume_min,
      "max_volume": info.volume_max,
      "spread": info.spread
    }
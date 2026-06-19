# data/feed.py
# Live candle ingestion and multi-timeframe structuring (no decision making)

import time
from collections import defaultdict

class MarketDataFeed:
  """
  Handles incoming market data streams for all symbols and timeframes.
  Normalizes and stores structured OHLC data
  """
  
  def __init__(self, logger=None):
    self.logger = logger
    self.data = defaultdict(lambda: defaultdict(list))  # {symbol: {timeframe: [candles]}}
    
    
  # ------------------
  # INGESTION
  # ------------------
  def update_candle(self, symbol: str, timeframe: str, candle: dict):
    """
    candle format expected: { "time": timestamp, "open": float, "high": float, "low": float, "close": float, "volume": float }
    """
    self._validate_candle(candle)
    self.data[symbol][timeframe].append(candle)
    
    if self.logger:
      self.logger.log_system(f"New candle received: {symbol} {timeframe} {candle}")
      
  
  # ------------------
  # VALIDATION
  # ------------------
  def _validate_candle(self, candle: dict):
    required_keys = ["time", "open", "high", "low", "close", "volume"]
    
    for key in required_keys:
      if key not in candle:
        raise ValueError(f"Candle missing required field key: {key}")
      
    if candle["high"] < candle["low"]:
      raise ValueError("Invalid candle: high < low")
    
  
  # ------------------
  # DATA ACCESS
  # ------------------
  def get_candles(self, symbol: str, timeframe: str, limit: int = 100):
    """Returns latest candles for analysis layer"""
    return self.data[symbol][timeframe][-limit:]
  
  
  def get_latest_candle(self, symbol: str, timeframe: str):
    """Returns the most recent candle for a given symbol and timeframe"""
    if not self.data[symbol][timeframe]:
      return None
    
    candles = self.data[symbol][timeframe]
    return candles[-1] if candles else None
  
  
  # ------------------
  # UTILITY
  # ------------------
  def clear_old_data(self, symbol: str, timeframe: str, max_candles: int = 1000):
    """Keeps only the most recent candles to manage memory usage (prevents memory overflow in long-running systems)"""
    if len(self.data[symbol][timeframe]) > max_candles:
      self.data[symbol][timeframe] = self.data[symbol][timeframe][-max_candles:]
      
      if self.logger:
        self.logger.log_system(f"Cleared old candles for {symbol} {timeframe}, kept last {max_candles}")
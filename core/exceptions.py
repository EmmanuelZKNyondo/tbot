# core/exceptions.py

class TBotError(Exception):
  """Base exception for all TBot errors"""
  pass

class ConfigError(TBotError):
  """Configuration-related errors."""
  pass

class BrokerConnectionError(TBotError):
  """Broker connection or related failures"""
  pass

class SymbolError(TBotError):
  """Invalid or unsupported or unregistered symbol"""
  pass

class TradeExecutionError(TBotError):
  """Trade execution error"""
  pass

class RiskViolationError(TBotError):
  """Risk rules violated"""
  pass

class DataFeedError(TBotError):
  """Market data related failure"""
  pass
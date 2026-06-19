# core/logger.py
# Audit everything (trade siginasl, rejected trades, risk violations, execution attempts, system error, config loads)

import json 
import os
from datetime import datetime

class Logger:
  """
  Central audit logger for Tbot.
  Captures every system event for full traceability and accountability.
  """
  
  def __init__(self, log_dir="logs"):
    self.log_dir = log_dir
    self._ensure_log_directory()
    self.system_log_file = os.path.join(log_dir, "system.log")
    self.trade_log_file = os.path.join(log_dir, "trades.log")
    self.error_log_file = os.path.join(log_dir, "errors.log")
    self.decision_log_file = os.path.join(log_dir, "decisions.log")
    self.reject_log_file = os.path.join(log_dir, "rejected_trades.log")
    
    
  # --------------------
  # INTERNAL UTILITIES
  # --------------------
  def _ensure_log_directory(self):
    if not os.path.exists(self.log_dir):
      os.makedirs(self.log_dir)
      
      
  def _timestamp(self):
    return datetime.now(datetime.timezone.utc).isoformat()
  
  
  def _write(self, file_path, data: dict):
    with open(file_path, "a") as file:
      file.write(json.dumps(data) + "\n")
      
      
  # --------------------
  # SYSTEM LOGGING
  # --------------------
  def log_system(self, message: str, level="INFO"):
    log_entry = {
      "timestamp": self._timestamp(),
      "level": level,
      "type": "SYSTEM",
      "message": message
    }
    self.write(self.system_log_file, log_entry)
    
  
  # -------------------
  # TRADE LOGGING
  # -------------------
  def log_trade(self, trade_data: dict, level="INFO"):
    log_entry = {
      "timestamp": self._timestamp(),
      "level": level,
      "type": "TRADE",
      "data": trade_data
    }
    self._write(self.trade_log_file, log_entry)
    
    
  # -------------------
  # DECISION LOGGING
  # -------------------
  def log_decision(self, symbol: str, decision: str, reason: str, level="INFO"):
    log_entry = {
      "timestamp": self._timestamp(),
      "level": level,
      "type": "DECISION",
      "symbol": symbol,
      "decision": decision,
      "reason": reason
    }
    self._write(self.decision_log_file, log_entry)
    
  
  # -------------------
  # REJECTED TRADE LOGGING
  # -------------------
  def log_rejected_trade(self, symbol: str, reason: str, context: str, level="WARNING"):
    log_entry = {
      "timestamp": self._timestamp(),
      "level": level,
      "type": "REJECTED_TRADE",
      "symbol": symbol,
      "reason": reason,
      "context": context
    }
    self._write(self.reject_log_file, log_entry)
    
  
  # -------------------
  # ERROR LOGGING
  # -------------------
  def log_error(self, error_message: str, context: dict = None, level="ERROR"):
    log_entry = {
      "timestamp": self._timestamp(),
      "level": level,
      "type": "ERROR",
      "message": error_message,
      "context": context or {}
    }
    self._write(self.error_log_file, log_entry)
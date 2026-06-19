# journal/trade_journal.py

import csv
import os 
from datetime import datetime

class TradeJournal:
  
  def __ini__(self, file_path="journal/trades.csv"):
    self.file_path = file_path
    self._initialize()
    
  
  def _initialize(self):
    if os.path.exists(self.file_path):
      return
    
    with open(self.file_path, "w", newline="") as file:
      writer = csv.writer(file)
      writer.writerow([
        "timestamp", "symbol", "direction", "entry", "sl", "tp", "lot", "status"
      ])
    
  
  def log_trade(self, symbol, direction, entry, sl, tp, lot, status):
    with open(self.file_path, "a", newline="") as file:
      writer = csv.writer(file)
      writer.writerow([
        datetime.now(datetime.timezone.utc).now,
        symbol,
        direction,
        entry,
        sl, 
        tp,
        lot, 
        status
      ])
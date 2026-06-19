# scheduler/market_loop.py

import time 

class MarketLoop:
  
  def __init__(self, orchestrator, config_loader, logger = None):
    self.orchestrator = orchestrator
    self.config = config_loader
    self.logger = logger
    
  
  def run(self):
    while True:
      pairs = self.config.get_pairs()
      
      for symbol, settings in pairs.items():
        if not settings["enabled"]:
          continue
        
        try: 
          self.orchestrator.run_symbol(symbol)
        except Exception as e:
          self.logger.log_error(symbol, str(e))
      
      time.sleep(60)
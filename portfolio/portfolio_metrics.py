# portfolio/portfolio_metrics.py

class PortfolioMetrics:
  """
  Computes portfolio-level metrics
  """
  
  def __init__(self, executor, logger = None):
    self.executor = executor
    self.logger = logger
    
    
  def build(self):
    positions = self.executor.get_positions()
    
    if positions is None:
      positions = []
      
    symbols = set()
    exposure = 0
    
    for position in positions:
      symbols.add(position.symbol)
      exposure += abs(position.volume)
      
    return {
      "simultaneous_positions": len(positions),
      "portfolio_exposure": exposure,
      "symbols_open": list(symbols)
    }
    
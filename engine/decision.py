# engine/decision.py
# takes topdown.py output, apply trade style rules, enforce bos confirmation logic, produce final decision (BUY, SELL, REJECT)

class DecisionEngine:
  """
  Final decision layer. Converts trade into actionable BUY/SELL/REJECT signals
  """
  
  def __init__(self, config_loader, logger=None):
    self.config = config_loader
    self.logger = logger
    
    
  # --------------------
  # MAIN ENTRY POINT
  # --------------------
  def evaluate(self, setup: dict, pair_config: dict):
    """
    Takes output from TopDownAnalyzer and returns final decision
    """
    if setup is None:
      return None
    
    symbol = setup["symbol"]
    bias = setup["bias"]
    score = setup["score"]
    trade_style = setup["trade_style"]
    
    min_score = pair_config["top_down_analysis"]["min_confluence_score"]
    
    # Step 1: score validation
    if score < min_score:
      return self._reject(symbol, "Low confluence score", setup)
    
    # Step 2: directional decision
    direction = self._resolve_direction(bias, setup)
    
    if direction is None:
      return self._reject(symbol, "No valid directional setup", setup)
    
    # Step 3: trade style validation (THIS IS WHERE THE IDEA LIVES)
    style_rules = pair_config.get("trade_style", {}).get("bos_validation", {})
    style_config = style_rules.get(trade_style, {})
    
    requires_retest = setup.get("requires_retest", False)
    
    if style_config.get("require_retest", False):
      # Only enforcing whether setup is valid without retest
      if not requires_retest:
        return self._reject(symbol, "Retest required but not confirmed", setup)
      
    # Step 4: Final approval
    decision = {
      "symbol": symbol,
      "direction": direction,
      "status": "APPROVED",
      "score": score,
      "trade_style": trade_style,
      "setup": setup
    } 
    
    if self.logger:
      self.logger.log_decision(symbol, decision)
      
    return decision
  

  # -----------------------
  # DIRECTION RESOLUTION
  # -----------------------
  def _resolve_direction(self, bias: str, setup: dict):
    bos = setup.get("bos")
    
    if bias == "BULLISH" and bos and bos["type"] == "BULLISH_BOS":
      return "BUY"
    
    if bias == "BEARISH" and bos and bos["type"] == "BEARISH_BOS":
      return "SELL"
    
    return None
  
  
  # ----------------------
  # REJECTION HANDLER
  # ----------------------
  def _reject(self, symbol: str, reason: str, setup: dict):
    rejection = {
      "symbol": symbol,
      "status": "REJECTED",
      "reason": reason,
      "setup": setup
    }  
    
    if self.logger:
      self.logger.log_rejected_trade(symbol, reason, setup)
      
    return rejection
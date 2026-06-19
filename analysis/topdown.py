# analysis/topdown.py
# full multi-timefram bias engine

class TopDownAnalyzer:
  """
  Builds multi-timeframe market bias and trade context
  from raw structure data
  """
  
  def __init__(self, config_loader, structure_analyzer, logger=None):
    self.config = config_loader
    self.structure = structure_analyzer
    self.logger = logger
    
  
  # --------------------------
  # MAIN ENTRY POINT
  # --------------------------
  def analyze(self, symbol: str, candles_by_tf: dict, pair_config: dict):
    """
    cancldes_by_tf format: { "D1": [...], "H4": [...], "H1": [...], "M15": [...] }
    """
    
    trade_style = pair_config.get("trade_style", {}).get("mode", "day_trade")
    
    # Step 1: analyze each timeframe structure
    tf_structure = {}
    
    for tf, candles in candles_by_tf.items():
      swings = self.structure.find_swings(candles)
      bos = self.structure.detect_bos(candles, swings)
      choch = self.structure.detect_choch(candles, swings)
      
      tf_structure[tf] = {
        "swings": swings,
        "bos": bos,
        "choch": choch
      }
      
    # Step 2: build directional bias
    bias = self._build_bias(tf_structure)
    
    # Step 3: evaluate trade setup
    setup = self._evaluate_setup(
      symbol,
      tf_structure,
      bias,
      trade_style,
      pair_config
    )
    
    return setup
  
  
  # --------------------------
  # BIAS ENGINE
  # --------------------------
  def _build_bias(self, tf_structure: dict):
    """
    Determines overall market direction using higher timeframes
    """
    
    d1 = tf_structure.get("D1", {})
    h4 = tf_structure.get("H4", {})
    
    bias = "NEUTRAL"
    
    if d1.get("bos", {}).get("type") == "BULLISH_BOS":
      bias = "BULLISH"
      
    if d1.get("bos", {}).get("type") == "BEARISH_BOS":
      bias = "BEARISH"
      
    # H4 refinement
    if h4.get("choch", {}).get("type") == "BEARISH_CHOCH":
      bias = "BEARISH"
      
    if h4.get("choch", {}).get("type") == "BULLISH_CHOCH":
      bias = "BULLISH"
      
    return bias
  
  # ---------------------------
  # SETUP ENGINE
  # ---------------------------
  def _evaluate_setup(self, symbol, tf_structure, bias, trade_style, pair_config):
    """
    Converts structure into trade candidate
    """
    entry_tf = "M15"
     
    entry_structure = tf_structure.get(entry_tf, {})
     
    bos = entry_structure.get("bos")
    choch = entry_structure.get('choch')
     
    min_score = pair_config["top_down_analysis"]["min_confluence_score"]
     
    # Step 1: basic direction alignment
    direction_ok = False
     
    if bias == "BULLISH" and bos and bos["type"] == "BULLISH_BOS":
      direction_ok = True
      
    if bias == "BEARISH" and bos and bos["type"] == "BEARISH_BOS":
      direction_ok = True
      
    if not direction_ok:
      return None
       
    # Step 2: compute confluence score
    score = self._calculate_score(tf_structure, bias)
    
    if score < min_score:
      return None
    
    # Step 3: apply trade style rules
    style_rules = pair_config.get("trade_style", {}).get("bos_validation", {})
    requires_retest = style_rules.get(trade_style, {}).get("require_retest", False)
    
    # We only flag retest (to implement in next engine layer)
    return {
      "symbol": symbol,
      "bias": bias,
      "score": score,
      "bos": bos,
      "choch": choch,
      "trade_style": trade_style,
      "requires_retest": requires_retest,
      "status": "PENDING_EXECUTION"
    }
    
  
  # -------------------------
  # SCORING ENGINE
  # -------------------------
  def _calculate_score(self, tf_structure: dict, bias: str):
    """
    Simple deterministic scoring model
    """
    score = 50 # base score
    
    d1 = tf_structure.get("D1", {})
    h4 = tf_structure.get("H4", {})
    h1 = tf_structure.get("H1", {})
    
    # higher timeframe alignment
    if d1.get("bos"):
      score += 20
      
    if h4.get("bos"):
      score += 10
      
    if h1.get("bos"):
      score += 10
      
    # CHOCH confirmation bonus
    if h4.get("choch"):
      score += 10
      
    return score
    
      
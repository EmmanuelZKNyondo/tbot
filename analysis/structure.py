# analysis/structure.py
# Break of Structure (BOS) engine (real logic starts here), swing detection, market structure labeling
# Interpret price action, use raw data from data/feed.py
# be deterministic (no randomness, no ML, no inference ambiguity)
class MarketStructureAnalyzer:
  """
  Detects market structure (HH, HL, LH, LL)
  BOS (Break of Structure),
  and CHOCH (Change of Character).
  """
  
  def __init__(self, logger = None):
    self.logger = logger
    
  
  # -------------------
  # SWING DETECTION
  # -------------------
  def find_swings(self, candles: list):
    """
    Identifies swing highs and lows
    Returns: { "swing_highs": [...], "swing_lows": [...]}
    """
    highs = []
    lows = []
    
    for i in range(1, len(candles) - 1):
      prev_candle = candles[i - 1]
      curr_candle = candles[i]
      next_candle = candles[i + 1]
      
      # swing high
      if curr_candle["high"] > prev_candle["high"] and curr_candle["high"] > next_candle["high"]:
        highs.append({
          "index": i,
          "price": curr_candle["high"],
          "time": curr_candle["time"]
        })
      
      # swing low  
      if curr_candle["low"] < prev_candle["low"] and curr_candle["low"] < next_candle["low"]:
        lows.append({
          "index": i,
          "price": curr_candle["low"],
          "time": curr_candle["time"]
        })
        
    return { "swing_highs": highs, "swing_lows": lows }
  

  # --------------------
  # MARKET STRUCTURE
  # --------------------
  def classify_structure(self, swings: dict):
    """
    Classifies market structure into HH, HL, LH, LL sequence
    """
    structure = []
    highs = swings["swing_highs"]
    lows = swings["swing_lows"]
    
    all_points = sorted(highs + lows, key=lambda x: x["index"])
    
    for i in range(1, len(all_points)):
      prev = all_points[i - 1]
      curr = all_points[i]
      
      if prev in highs and curr in highs:
        label = "HH" if curr["price"] > prev["price"] else "LH"
        
      elif prev in lows and curr in lows:
        label = "HL" if curr["price"] > prev["price"] else "LL"
        
      else:
        label = "transition"
        
      structure.append({
        "type": label,
        "price": curr["price"],
        "time": curr["time"]
      })
      
    return structure
  
  
  # ----------------------
  # BOS DETECTION
  # ----------------------
  def detect_bos(self, candles: list, swings: dict):
    """
    Detect Break of Structure
    """
    if len(swings["swing_highs"]) < 2 or len(swings["swing_lows"]) < 2:
      return None
    
    last_high = swings["swing_highs"][-1]
    last_prev_high = swings["swing_highs"][-2]
    
    last_low = swings["swing_lows"][-1]
    last_prev_low = swings["swing_lows"][-2]
    
    last_close = candles[-1]["close"]
    
    # Bullish BOS
    if last_close > last_high["price"] and last_high["price"] > last_prev_high["price"]:
      return {
        "type": "BULLISH_BOS",
        "level_broken": last_high["price"],
        "time": candles[-1]["time"]
      }
      
    # Bearish BOS
    if last_close < last_low["price"] and last_low["price"] < last_prev_low["price"]:
      return {
        "type": "BEARISH_BOS",
        "level_broken": last_low["price"],
        "time": candles[-1]["time"]
      }

    return None
  
  
  # -----------------------------
  # CHOCH DETECTION
  # -----------------------------

  def detect_choch(self, candles: list, swings: dict):
      """
      Detect Change of Character (reversal signal).
      """

      if len(swings["swing_highs"]) < 2 or len(swings["swing_lows"]) < 2:
          return None

      last_close = candles[-1]["close"]

      last_high = swings["swing_highs"][-1]
      last_low = swings["swing_lows"][-1]

      # bullish to bearish shift
      if last_close < last_low["price"]:
          return {
              "type": "BEARISH_CHOCH",
              "time": candles[-1]["time"]
          }

      # bearish to bullish shift
      if last_close > last_high["price"]:
          return {
              "type": "BULLISH_CHOCH",
              "time": candles[-1]["time"]
          }

      return None
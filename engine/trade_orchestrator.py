# engine/trade_orchestrator.py

class TradeOrchestrator: 
  """
  Coordinates the entire TBot trading pipeline. 
  
  Delegates all work to specialised modules
  """
  
  def __init__(self, config_loader, logger, executor, structure_analyzer, topdown_analyzer, decision_engine, position_sizer, exposure_manager, trading_filters):
    self.config = config_loader
    self.logger = logger
    self.executor = executor
    self.structure = structure_analyzer
    self.topdown = topdown_analyzer
    self.decision = decision_engine
    self.position_sizer = position_sizer
    self.exposure = exposure_manager
    self.filters = trading_filters
    
  
  # ------------------------------
  # MAIN ENTRY
  # ------------------------------
  def run_symbol(self, symbol):
    """
    Process one symbo completely
    """
    pair_config = self.config.get_pair_config(symbol)
    
    # SKIP DISABLED SYMBOLS
    if not pair_config["enabled"]:
      return
    
    # FETCH CANDLES
    candles_by_tf = self._fetch_timeframes(symbol, pair_config)
    
    # BUILD SETUP
    setup = self.topdown.analyze(symbol, candles_by_tf, pair_config)
    
    if setup is None:
      return
    
    # DECISION ENGINE
    decision = self.decision.evaluate(setup, pair_config)
    
    if decision["status"] != "APPROVED":
      return
    
    # ACCOUNT METRICS
    account_metrics = self._build_account_metrics()
    portfolio_metrics = self._build_portfolio_metrics()
    pair_metrics = self.build_pair_metrics(symbol)
    
    # EXPOSURE MANAGER
    approved, reason = self.exposure.validate(
      symbol,
      account_metrics,
      portfolio_metrics,
      pair_metrics
    )
    
    if not approved:
      return
    
    # MARKET METRICS
    market_metrics = self._build_market_metrics(symbol)
    
    approved, reason = self.filters.validate(symbol, market_metrics)
    
    if not approved:
      return
    
    # CALCULATE SL/TP
    stop_loss = self._calculate_stop_loss(symbol)
    take_profit = self._calculate_take_profit(symbol)
    
    # POSITION SIZE
    account_info = self.executor.get_account_info()
    
    symbol_info = self._get_symbol_info(symbol)
    
    volume = self.position_sizer.calculate(
      symbol = symbol,
      account_balance = account_info["balance"],
      stop_loss_points = symbol_info["stop_loss_points"],
      tick_value = symbol_info["tick_value"],
      tick_size = symbol_info["tick_size"],
      volume_step = symbol_info["volume_step"],
      min_volume = symbol_info["min_volume"],
      max_volume = symbol_info["max_volume"]
    )
    
    # - EXECUTE TRADE - #
    result = self.executor.place_order(
      symbol = symbol,
      direction = decision["direction"],
      volume = volume,
      sl = stop_loss,
      tp = take_profit
    )
    
    return result
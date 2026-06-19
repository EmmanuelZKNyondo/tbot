# main_test.py

from core.loader import ConfigLoader

from execution.executor import ExecutionRouter

from scheduler.market_loop import MarketLoop

from engine.trade_orchestrator import TradeOrchestrator

from analysis.structure import MarketStructureAnalyzer

from journal.trade_journal import TradeJournal

from core.error_handler import ErrorHandler

def main():
    
    error_handler = ErrorHandler(show_traceback=False)

    # LOAD CONFIG
    try:
        config = ConfigLoader()
    except Exception as e:
        error_handler.handle(e, context="main_test")
        
    # JOURNAL
    try:
        journal = TradeJournal()
    except Exception as e:
        error_handler.handle(e, context="main_test")
        
    # EXECUTION (DRY RUN)
    try:
        executor = ExecutionRouter(config)
    except Exception as e:
        error_handler.handle(e, context="main_test")

    # FORCE SAFE MODE HERE
    try:
        executor.broker.place_order = lambda *args, **kwargs: print(
            "[DRY RUN ORDER BLOCKED]",
            args,
            kwargs
        )
    except Exception as e:
        error_handler.handle(e, context="main_test")
    
    # STRUCTURE ENGINE
    try:
        structure = MarketStructureAnalyzer()
    except Exception as e:
        error_handler.handle(e, context="main_test")
    
    # ORCHESTRATOR (you already built dependencies)
    try:
        orchestrator = TradeOrchestrator(
            config_loader=config,
            logger=None,
            executor=executor,
            structure_analyzer=structure,
            topdown_analyzer=None,
            decision_engine=None,
            position_sizer=None,
            exposure_manager=None,
            trading_filters=None
        )
    except Exception as e:
        error_handler.handle(e, context="main_test")

    # MARKET LOOP
    try:
        loop = MarketLoop(
            orchestrator=orchestrator,
            config_loader=config,
            logger=None
        )
    except Exception as e:
        error_handler.handle(e, context="main_test")

    print("TBot TEST MODE STARTED (DRY RUN)")

    loop.run()


if __name__ == "__main__":
    main()
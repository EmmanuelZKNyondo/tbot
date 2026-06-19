# main.py

from core.loader import ConfigLoader

from execution.executor import ExecutionRouter

from scheduler.market_loop import MarketLoop

from engine.trade_orchestrator import TradeOrchestrator

from analysis.structure import MarketStructureAnalyzer

from journal.trade_journal import TradeJournal


def main():

    # -------------------------
    # LOAD CONFIG
    # -------------------------
    config = ConfigLoader()

    # IMPORTANT: set dry_run = false in config
    print("TBot DEMO MODE STARTING")

    # -------------------------
    # JOURNAL
    # -------------------------
    journal = TradeJournal()

    # -------------------------
    # EXECUTION (REAL MT5)
    # -------------------------
    executor = ExecutionRouter(config)

    # CONNECT TO MT5
    executor.broker.connect()

    # -------------------------
    # CORE MODULES
    # -------------------------
    structure = MarketStructureAnalyzer()

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

    # -------------------------
    # START LOOP
    # -------------------------
    loop = MarketLoop(
        orchestrator=orchestrator,
        config_loader=config,
        logger=None
    )

    loop.run()


if __name__ == "__main__":
    main()
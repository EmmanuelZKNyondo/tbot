# risk/position_sizing.py

from math import floor


class PositionSizer:
    """
    Production-grade position sizing engine.

    Priority:
    1. Use fixed lot size from JSON if provided.
    2. Otherwise calculate lot size from account risk.

    This module performs no broker interaction.
    All symbol specifications must be supplied externally.
    """

    def __init__(self, config_loader, logger=None):
        self.config = config_loader
        self.logger = logger


    def calculate(
        self,
        symbol: str,
        account_balance: float,
        stop_loss_points: float,
        tick_value: float,
        tick_size: float,
        volume_step: float,
        min_volume: float,
        max_volume: float
    ) -> float:
        """
        Calculate position size.

        Parameters
        ----------
        symbol : str
            Trading symbol.

        account_balance : float
            Current account balance.

        stop_loss_points : float
            Distance from entry to stop loss in price points.

        tick_value : float
            Monetary value of one tick.

        tick_size : float
            Minimum price movement.

        volume_step : float
            Broker lot increment.

        min_volume : float
            Broker minimum lot.

        max_volume : float
            Broker maximum lot.

        Returns
        -------
        float
            Final lot size normalized to broker requirements.
        """

        pair_config = self.config.get_pair_config(symbol)
        risk_config = pair_config["risk_management"]

        fixed_lot_size = risk_config.get("fixed_lot_size")

        # -----------------------------------------------------
        # PRIORITY 1 : FIXED LOT OVERRIDE
        # -----------------------------------------------------
        if fixed_lot_size not in [None, "", " ", 0]:
            lot_size = self._normalize_volume(
                float(fixed_lot_size),
                volume_step,
                min_volume,
                max_volume
            )

            self._log(
                symbol,
                "FIXED_LOT",
                lot_size
            )

            return lot_size

        # -----------------------------------------------------
        # PRIORITY 2 : RISK-BASED POSITION SIZE
        # -----------------------------------------------------

        risk_percent = risk_config["risk_per_trade_percent"]

        risk_amount = account_balance * (risk_percent / 100)

        money_per_point_per_lot = tick_value / tick_size

        stop_loss_value_per_lot = stop_loss_points * money_per_point_per_lot

        if stop_loss_value_per_lot <= 0:
            raise ValueError(
                f"{symbol}: invalid stop loss value."
            )

        raw_lot_size = risk_amount / stop_loss_value_per_lot

        lot_size = self._normalize_volume(
            raw_lot_size,
            volume_step,
            min_volume,
            max_volume
        )

        self._log(
            symbol,
            "RISK_BASED",
            lot_size
        )

        return lot_size


    def _normalize_volume(
        self,
        volume: float,
        volume_step: float,
        min_volume: float,
        max_volume: float
    ) -> float:
        """
        Normalize volume according to broker constraints.
        """

        volume = max(min_volume, volume)
        volume = min(max_volume, volume)

        normalized = floor(volume / volume_step) * volume_step

        return round(normalized, 2)


    def _log(
        self,
        symbol: str,
        sizing_mode: str,
        lot_size: float
    ):
        """
        Internal logging.
        """

        if self.logger:
            self.logger.log_system(
                f"{symbol} position sizing "
                f"mode={sizing_mode}, "
                f"lot={lot_size}"
            )
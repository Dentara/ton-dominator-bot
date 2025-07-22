from datetime import datetime

class RiskManager:
    def __init__(self, max_daily_loss: float = 50.0, max_consecutive_losses: int = 3, min_balance: float = 20.0):
        self.daily_loss = 0.0
        self.consecutive_losses = 0
        self.max_daily_loss = max_daily_loss
        self.max_consecutive_losses = max_consecutive_losses
        self.min_balance = min_balance
        self.last_trade_pnl = 0.0
        self.daily_reset_time = datetime.now().date()

    def update_pnl(self, pnl: float):
        today = datetime.now().date()
        if today != self.daily_reset_time:
            self.daily_loss = 0.0
            self.consecutive_losses = 0
            self.daily_reset_time = today

        self.last_trade_pnl = pnl
        self.daily_loss += max(-pnl, 0)

        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

    def is_risk_limit_exceeded(self, current_balance: float) -> bool:
        if self.daily_loss >= self.max_daily_loss:
            return True
        if self.consecutive_losses >= self.max_consecutive_losses:
            return True
        if current_balance <= self.min_balance:
            return True
        return False

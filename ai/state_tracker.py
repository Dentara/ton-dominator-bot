class StateTracker:
    def __init__(self):
        self.last_position = None  # "LONG" or "SHORT" or None
        self.active = False

    def update_position(self, position: str):
        self.last_position = position
        self.active = True if position else False

    def should_trade(self, new_position: str) -> bool:
        if not self.active:
            return True
        return new_position != self.last_position

    def reset(self):
        self.last_position = None
        self.active = False

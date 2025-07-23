class StateTracker:
    def __init__(self):
        self.last_position = None  # "LONG" or "SHORT"

    def update_position(self, position: str):
        self.last_position = position

    def get_position(self) -> str:
        return self.last_position or "NONE"

    def reset(self):
        self.last_position = None
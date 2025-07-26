# ai/state_tracker.py

class StateTracker:
    def __init__(self):
        self.positions = {}  # symbol => { "position": str, "hold": int }

        # Candle sayı limiti – istədikdə dəyişmək olar
        self.cooldown_required = 3

    def update_position(self, symbol: str, position: str):
        if symbol not in self.positions:
            self.positions[symbol] = {"position": position, "hold": 1}
        else:
            current = self.positions[symbol]
            if current["position"] == position:
                current["hold"] += 1
            else:
                self.positions[symbol] = {"position": position, "hold": 1}

    def get_position(self, symbol: str) -> str:
        if symbol not in self.positions:
            return "NONE"
        return self.positions[symbol]["position"]

    def can_close_position(self, symbol: str) -> bool:
        if symbol not in self.positions:
            return True
        return self.positions[symbol]["hold"] >= self.cooldown_required

    def reset(self, symbol: str):
        if symbol in self.positions:
            del self.positions[symbol]
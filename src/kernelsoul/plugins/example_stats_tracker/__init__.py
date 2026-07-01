class Plugin:
    def __init__(self):
        self.hp_changes = 0
        self.last_hp = None
    def on_state_change(self, changes, state):
        if self.last_hp is not None and state.hp != self.last_hp:
            self.hp_changes += 1
            print(f'[StatsTracker] HP changed {self.last_hp} -> {state.hp} (total: {self.hp_changes})')
        self.last_hp = state.hp


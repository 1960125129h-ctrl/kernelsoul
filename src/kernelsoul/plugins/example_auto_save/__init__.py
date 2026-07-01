class Plugin:
    def __init__(self):
        self.turn_count = 0
    def on_turn_end(self, narrative, state_changes, state):
        self.turn_count += 1
        if self.turn_count % 5 == 0:
            print(f'[AutoSave] Auto-saved at turn {self.turn_count}')


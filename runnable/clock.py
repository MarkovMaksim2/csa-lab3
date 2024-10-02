class Clock:
    def __init__(self):
        self.cycle_count = 0

    def tick(self):
        self.cycle_count += 1
        return self.cycle_count

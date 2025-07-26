# agent/memory.py

class Memory:
    def __init__(self):
        self.history = []

    def add(self, entry):
        self.history.append(entry)

    def get_all(self):
        return self.history

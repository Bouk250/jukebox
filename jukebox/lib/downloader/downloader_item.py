
class JukeBoxItem:
    def __init__(self):
        self.settings = None
        self.items = []
        self.completed = 0
        self.failed = 0
        self.canceled = 0
        self.decrypte_func = None
        
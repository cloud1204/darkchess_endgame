class Piece:
    def __init__(self, type, color, revealed = False):
        self.type = type
        self.color = color
        self.revealed = revealed
    def __str__(self):
        return self.type if self.revealed else "?"
class board:
    def __init__(self) -> None:
        self.squares = [[None for i in range(4)] for j in range(8)]
    def random_generate(self):
        import random
        'K', ''
        pool = [('r', '')]
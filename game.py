class Piece:
    def __init__(self, type, color, revealed = False):
        self.type = type
        self.color = color
        self.revealed = revealed
        self.position = [-1, -1]
    def __str__(self):
        return self.type if self.revealed else "?"
class Board:
    def __init__(self, pos = []) -> None:
        self.squares = [[None for i in range(8)] for j in range(4)]
        for (x, y, tp, color) in pos:
            self.squares[x][y] = Piece(tp, color, revealed=True)
    def get_pool(self):
        type_pool = ['K'] + ['G', 'M', 'R', 'N', 'C'] * 2 + ['P'] * 5
        pool = [Piece(tp, 0) for tp in type_pool] + [Piece(tp, 1) for tp in type_pool]
        return pool
    def random_generate(self):
        import random
        random.seed(42)
        pool = self.get_pool()
        random.shuffle(pool)
        for i in range(4):
            for j in range(8):
                self.squares[i][j] = pool[i * 8 + j]
    def pos_empty(self, pos):
        return self.squares[pos[0]][pos[1]] is None
    def count_line(self, pos_a, pos_b):
        if pos_a[0] == pos_b[0]:
            l = min(pos_a[1], pos_b[1])
            r = max(pos_a[1], pos_b[1])
            return sum((1 - self.pos_empty([pos_a[0], x])) for x in range(l, r + 1))
        elif pos_a[1] == pos_b[1]:
            l = min(pos_a[0], pos_b[0])
            r = max(pos_a[0], pos_b[0])
            return sum((1 - self.pos_empty([x, pos_a[1]])) for x in range(l, r + 1))
        else:
            # not a same line
            return -1
    def eatable (self, pos_a, pos_b):
        A = self.squares[pos_a[0]][pos_a[1]]
        B = self.squares[pos_b[0]][pos_b[1]]
        if A.color == B.color or not A.revealed or not B.revealed:
            return False
        if A.type == 'C':
            cnt = self.count_line(pos_a, pos_b)
            return cnt == 3
        if abs(pos_a[0] - pos_b[0]) + abs(pos_a[1] - pos_b[1]) != 1:
            return False
        if A.type == 'K':
            return B.type != 'P'
        elif A.type == 'P':
            return B.type == 'K' or B.type == 'P'
        else:
            partial_order = {'K': 6, 'G': 5, 'M': 4, 'R': 3, 'N': 2, 'C': 1, 'P': 0}
            return partial_order[A.type] >= partial_order[B.type]
    def get_unrevealed(self):
        l = []
        output_order = {'K': 6, 'G': 5, 'M': 4, 'R': 3, 'N': 2, 'C': 1, 'P': 0}
        for i in self.squares:
            for j in i:
                if j is not None and not j.revealed:
                    l.append((j.type, j.color))
        return sorted(l, key=lambda item: (item[1], -output_order[item[0]]))
    
    def Print(self):
        for i in range(4):
            row_str = ""
            for j in range(8):
                piece = self.squares[i][j]
                if piece is None:
                    row_str += ".  "
                elif not piece.revealed:
                    row_str += "?  "
                else:
                    color_code = "\033[91m" if piece.color == 1 else "\033[34m"
                    row_str += f"{color_code}{piece.type}\033[0m  "
            print(row_str)
        print()

if __name__ == '__main__':
    board = Board()
    board.random_generate()
    board.Print()
    for i in range(4):
        for j in range(8):
            import random
            case = random.randint(0, 2)
            if case == 0:
                board.squares[i][j] = None
            elif case == 1:
                board.squares[i][j].revealed = 1
            elif case == 2:
                board.squares[i][j].revealed = 0
    board.Print()
    print(board.eatable([0, 2], [0, 6]))
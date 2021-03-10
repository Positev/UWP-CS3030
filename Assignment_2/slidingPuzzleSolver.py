from typing import List, Tuple
import itertools


# Puzzle state represents a 3 by 3 board of spaces.
# 8 spaces are occupied by a tile. One space is blank.
# Each tile has a label.
class PuzzleState:
    BLANK = -1
    BOARD_SIZE = 3
    VALID_TILE_VALUE_RANGE = list(range(1, 9)) + [-1]
    print(VALID_TILE_VALUE_RANGE)

    # The state is represented by a list of lists.
    def __init__(self, rows: List[List[int]]):
        self._rows = rows

        existing_vals = []
        for row in rows:
            if len(row) != self.BOARD_SIZE:
                raise Exception("Bad game state.")
            for val in row:
                if type(val) != int or val not in self.VALID_TILE_VALUE_RANGE:
                    raise Exception(f"Bad tile value. {val}")
                elif val in existing_vals:
                    raise Exception("Val already in state.")
                else:
                    existing_vals.append(val)

    def __str__(self):

        def val_or_b(row, col):
            return self.rows[row][col] if self.rows[row][col] != self.BLANK else "B"

        out = [
            "+--------------+",
            f"| {val_or_b(0, 0)}    {val_or_b(0, 1)}    {val_or_b(0, 2)}  |",
            f"| {val_or_b(1, 0)}    {val_or_b(1, 1)}    {val_or_b(1, 2)}  |",
            f"| {val_or_b(2, 0)}    {val_or_b(2, 1)}    {val_or_b(2, 2)}  |",
            "+--------------+"
        ]

        return '\n'.join(out)

    def __hash__(self):
        return hash(str(self))

    @property
    def rows(self):
        return self._rows

    def __eq__(self, other):

        def tiles_are_equal(i, j):
            return self.get_tile(i, j) == other.get_tile(i, j)

        b_range = range(self.BOARD_SIZE)

        equalities = [tiles_are_equal(i, j) for i, j in itertools.product(b_range, b_range)]
        return all(equalities)

    def in_board_coords(self, row, col):

        mrow = row % self.BOARD_SIZE
        mcol = col % self.BOARD_SIZE
        return mrow, mcol

    def get_tile(self, row, col):
        mrow, mcol = self.in_board_coords(row, col)
        return self._rows[mrow][mcol]

    def set_tile(self, row, col, val):
        mrow, mcol = self.in_board_coords(row, col)
        self._rows[mrow][mcol] = val

    def can_swap_with_blank(self, tile_pos: Tuple[int, int]):
        tile_pos = self.in_board_coords(tile_pos[0], tile_pos[1])
        blank_x, blank_y = self.get_blank_node()

        allowed_moves = [
            self.in_board_coords(blank_x + 1, blank_y) == tile_pos,
            self.in_board_coords(blank_x, blank_y + 1) == tile_pos,
            self.in_board_coords(blank_x - 1, blank_y) == tile_pos,
            self.in_board_coords(blank_x, blank_y - 1) == tile_pos,
        ]

        return any(allowed_moves)

    def swap_with_blank(self, tile_pos: Tuple[int, int]):
        blank = self.get_blank_node()
        val = self.get_tile(tile_pos[0], tile_pos[1])
        self.set_tile(blank[0], blank[1], val)
        self.set_tile(tile_pos[0], tile_pos[1], self.BLANK)

    def get_blank_node(self):
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                val = self._rows[i][j]
                if val == self.BLANK:
                    return i, j

    def copy(self):
        new_state = [[x for x in row] for row in self._rows]
        return PuzzleState(new_state)

    # Lower weight means better option
    def get_heuristic_weight(self, goal):
        out_of_place_tiles = 0
        board_range = range(self.BOARD_SIZE)
        for i, j in itertools.product(board_range, board_range):
            if self.get_tile(i, j) != self.BLANK and self.get_tile(i, j) != goal.get_tile(i, j):
                out_of_place_tiles += 1

        return out_of_place_tiles


class SearchNode:
    def __init__(self, state: PuzzleState):
        self._puzzle_state = state

    @property
    def state(self):
        return self._puzzle_state

    def neighbors(self):
        state = self._puzzle_state
        blank = state.get_blank_node()
        neighbors = []

        new_state = self._puzzle_state.copy()
        if new_state.can_swap_with_blank((blank[0] + 1, blank[1])):
            new_state.swap_with_blank((blank[0] + 1, blank[1]))
            neighbors.append(new_state)

        new_state = self._puzzle_state.copy()
        if new_state.can_swap_with_blank((blank[0], blank[1] + 1)):
            new_state.swap_with_blank((blank[0], blank[1] + 1))
            neighbors.append(new_state)

        new_state = self._puzzle_state.copy()
        if new_state.can_swap_with_blank((blank[0] - 1, blank[1])):
            new_state.swap_with_blank((blank[0] - 1, blank[1]))

            neighbors.append(new_state)

        new_state = self._puzzle_state.copy()
        if new_state.can_swap_with_blank((blank[0], blank[1] - 1)):
            new_state.swap_with_blank((blank[0], blank[1] - 1))
            neighbors.append(new_state)

        return neighbors


def breadth_first_search(start, goal):
    mfront = [start]
    parents = {}

    def bfs(front, goal, parents):
        node = front.pop()
        if not node == goal:
            neighbors = [cNode for cNode in SearchNode(node).neighbors()]
            if neighbors:
                front = neighbors + front
                for neighbor in neighbors:
                    if neighbor not in parents:
                        parents[neighbor] = node
                bfs(front, goal, parents)

    bfs(mfront, goal, parents)

    print(goal)
    node = parents[goal]
    while node != start:
        print(node)
        node = parents[node]
    print(start)


def iterative_deepening_depth_first_search(start, goal):
    mdepth = 1
    parents = {}

    def dldfs(front, cgoal, depth, max_depth, cvisited):
        depth = depth + 1
        if len(front) == 0:
            return False
        else:
            node = front.pop()
            if node == cgoal:
                return True
            elif depth < max_depth:
                visited.append(node)
                for c in SearchNode(node).neighbors():
                    if c not in cvisited:
                        front.append(c)
                        if not c in parents:
                            parents[c] = node
                return dldfs(front, cgoal, depth, max_depth, cvisited)

    found = False
    current_max_depth = 2
    while not found:
        mfront = [start]
        visited = []
        found = dldfs(mfront, goal, 1, current_max_depth, visited)
        # print(goal in mfront)
        current_max_depth += 1

    print(goal)
    node = parents[goal]
    while node != start:
        print(node)
        node = parents[node]
    print(start)


def a_star_search(start, goal):
    front = [start]
    visited = []
    parents = {}

    def a_star(front, visited, goal):
        if len(front) == 0:
            return False
        node = front.pop()
        if node != goal:
            visited.append(node),
            for neighbor in SearchNode(node).neighbors():
                if neighbor not in visited:
                    front.append(neighbor)
                    if neighbor not in parents:
                        parents[neighbor] = node

            front.sort(key=lambda x: x.get_heuristic_weight(goal), reverse=True)
            a_star(front, visited, goal)
        else:
            return True

    a_star(front,visited,goal)

    print(goal)
    node = parents[goal]
    while node != start:
        print(node)
        node = parents[node]
    print(start)


problems = [
    {
        "start": PuzzleState([[1, 2,-1,], [4, 3,  6], [7, 5, 8]]),
        "goal": PuzzleState([[1, 2, 3], [4, 5, 6], [7, 8, -1]])
    },
    {
        "start": PuzzleState([[1, 2, 3], [4, 5, 6], [-1, 7, 8]]),
        "goal": PuzzleState([[1, 2, 3], [4, 5, 6], [7, 8, -1]])
    },

    {
        "start": PuzzleState([[-1, 2, 3], [4, 1, 6], [7, 5, 8]]),
        "goal": PuzzleState([[1, 2, 3], [4, 5, 6], [7, 8, -1]])
    }
]

if __name__ == '__main__':

    for problem in problems:

        # breadth_first_search(*problem)
        #iterative_deepening_depth_first_search(*problem.values())
        a_star_search(*problem.values())


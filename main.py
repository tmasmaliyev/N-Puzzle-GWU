import heapq
import argparse

from read import read_matrix_from_filepath
    
class NPuzzle:
    def __init__(self, initial_state):
        self.n = len(initial_state)
        self.initial_state = tuple(tuple(row) for row in initial_state)
        self.goal_state = self.generate_goal_state()
        self.blank_pos = self.find_blank_position(self.initial_state)

    def generate_goal_state(self):

        goal = [[(i * self.n + j + 1) % (self.n * self.n) for j in range(self.n)] for i in range(self.n)]
        return tuple(tuple(row) for row in goal)

    def find_blank_position(self, state):

        for i in range(self.n):
            for j in range(self.n):
                if state[i][j] == 0:
                    return (i, j)
        return None

    def get_neighbors(self, state, blank_pos):

        x, y = blank_pos
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.n and 0 <= ny < self.n:
                new_state = [list(row) for row in state]
                new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
                neighbors.append((tuple(tuple(row) for row in new_state), (nx, ny)))

        return neighbors

    def manhattan_distance(self, state):

        distance = 0
        for i in range(self.n):
            for j in range(self.n):
                value = state[i][j]
                if value != 0:
                    target_x, target_y = (value - 1) // self.n, (value - 1) % self.n
                    distance += abs(i - target_x) + abs(j - target_y)
        return distance

    def a_star_search(self):

        priority_queue = []
        heapq.heappush(priority_queue, (0, self.initial_state, self.blank_pos, 0, []))  
        visited = set()

        while priority_queue:
            f, current_state, blank_pos, g, path = heapq.heappop(priority_queue)

            if current_state == self.goal_state:
                return path  

            if current_state in visited:
                continue

            visited.add(current_state)

            for neighbor, new_blank_pos in self.get_neighbors(current_state, blank_pos):
                if neighbor not in visited:
                    move = (current_state[blank_pos[0]][blank_pos[1]], new_blank_pos)
                    new_g = g + 1
                    new_f = new_g + self.manhattan_distance(neighbor)
                    heapq.heappush(priority_queue, (new_f, neighbor, new_blank_pos, new_g, path + [move]))

        return None  


def main(initial_state):
    solver = NPuzzle(initial_state) 
    solution = solver.a_star_search()

    if solution:
        print("Solution found in", len(solution), "moves:")
        # print(" -> ".join(solution))
        # print(solution)
        ...
    else:
        print("No solution exists for this puzzle.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', type=str, required=True, help='Filepath of initial matrix as .txt file')

    args = parser.parse_args()

    initial_state = read_matrix_from_filepath(args.filepath)

    main(initial_state)
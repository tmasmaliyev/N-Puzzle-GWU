# Import functionality of Priority Queue
import heapq

# Import Argument Parser
import argparse

# Import `read_matrix_from_filepath` from `read.py`
from read import read_matrix_from_filepath
    
class NPuzzle:
    def __init__(self, initial_state):
        # Define length of row & column (in this case, row and column is same)
        self.n = len(initial_state)

        # Define initial_state of problem and assign to Tuple for hashability
        self.initial_state = tuple(tuple(row) for row in initial_state)
        
        # Define end goal state
        self.goal_state = self.generate_goal_state()

        # Define blank position as (row, col)
        self.blank_pos = self.find_blank_position(self.initial_state)

    def generate_goal_state(self):
        # Define end goal state
        goal = [
            [(i * self.n + j + 1) % (self.n * self.n) for j in range(self.n)] for i in range(self.n)
        ]

        return tuple(tuple(row) for row in goal)

    def find_blank_position(self, state):
        # Iterate over matrix and check which element is `0`
        for i in range(self.n):
            for j in range(self.n):
                if state[i][j] == 0:
                    return (i, j)
        return None

    def get_neighbors(self, state, blank_pos):
        # Extract blank pos as (x, y) coordinates
        x, y = blank_pos
        neighbors = []
        directions = {
            (-1, 0) :  'Up'   ,
            (1, 0)  :  'Down' ,
            (0, -1) :  'Left' ,
            (0, 1)  :  'Right'
        }

        # Iterate over all directions and add direction indices to (x, y) coordinates
        # This is to move blank position
        for (dx, dy), direction in directions.items():
            nx, ny = x + dx, y + dy

            # If new coordinates are in range of [0, n), it is possible to work with it
            # Otherwise, it means, out of bounds
            if 0 <= nx < self.n and 0 <= ny < self.n:

                # Create new state of matrix
                new_state = [list(row) for row in state]

                # Swap places of previous blank position to new position
                new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]

                # Save the state as (new_state, blank position coordinate)
                neighbors.append(
                    (tuple(tuple(row) for row in new_state), (nx, ny), direction)
                )

        return neighbors

    def manhattan_distance(self, state):
        distance = 0

        # Iterate over matrix and find L1 distance of where that item should be and where it is
        for i in range(self.n):
            for j in range(self.n):
                value = state[i][j]
                
                # If the value is different from blank, then find distance
                if value != 0:
                    target_x, target_y = (value - 1) // self.n, (value - 1) % self.n
                    distance += abs(i - target_x) + abs(j - target_y)

        return distance

    def a_star_search(self):
        
        # Define empty Priority queue
        priority_queue = []

        # Push item as (f-score, initial_state, blank_pos, g-score, Move-array) to heap as MIN-Heap
        heapq.heappush(priority_queue, (0, self.initial_state, self.blank_pos, 0, []))  

        # Visited array
        visited = set()

        while priority_queue:
            # Pop top element from heap
            f, current_state, blank_pos, g, path = heapq.heappop(priority_queue)

            # If the current state equals to goal state, it means, the goal is reached
            if current_state == self.goal_state:
                return path  

            # If the state is previously seen, then no need to continue again
            if current_state in visited:
                continue
            
            # Add the state to visited set to indicate it is seen
            visited.add(current_state)

            # Get neighbouring states with corresponding blank positions as (row, column)
            for neighbor, new_blank_pos, direction in self.get_neighbors(current_state, blank_pos):

                # Check if neighbouring state is visited or not
                # If so, then no need to continue
                if neighbor not in visited:
                    # Add new step
                    new_g = g + 1

                    # f_new = g_new + h_new, so step size + L1 distance
                    new_f = new_g + self.manhattan_distance(neighbor)

                    # Add new item (f-score, initial_state, blank_pos, g-score, Move-array) to heap and form as MIN-Heap
                    heapq.heappush(priority_queue, (new_f, neighbor, new_blank_pos, new_g, path + [direction]))

        return None  


def main(initial_state):
    solver = NPuzzle(initial_state) 
    solution = solver.a_star_search()

    if solution:
        print("Solution found in", len(solution), "moves:")
        print(" -> ".join(solution))

    else:
        print("Puzzle is already solved !")


if __name__ == '__main__':
    # Define Argument parser and add argument
    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', 
                        type=str, required=True, 
                        help='Filepath of initial matrix as .txt file'
    )

    # Parse arguments from command line
    args = parser.parse_args()

    # Read matrix from filepath 
    initial_state = read_matrix_from_filepath(args.filepath)

    # Start Main process
    main(initial_state)
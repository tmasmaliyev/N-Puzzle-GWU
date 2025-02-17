import heapq
import argparse

import re
from collections import defaultdict

class NPuzzle:
    def __init__(self, initial, n=3):
        self.n = len(initial)
        self.initial = tuple(map(tuple, initial))

        self.goal = tuple( 
            tuple(range(i * n + 1, (i + 1) * n + 1)) for i in range(n)
        )
        self.goal = tuple(
            row[:-1] + (0,) if i == n - 1 else row for i, row in enumerate(self.goal)
        )

        self.moves = [
            (-1, 0, "Up"), (1, 0, "Down"), (0, -1, "Left"), (0, 1, "Right")
        ]

    def manhattan_distance(self, state):

        distance = 0
        for i in range(self.n):
            for j in range(self.n):
                if state[i][j] != 0:  # Ignore the blank space
                    target_x, target_y = divmod(state[i][j] - 1, self.n)
                    distance += abs(target_x - i) + abs(target_y - j)
        return distance

    def find_blank(self, state):
        for i in range(self.n):
            for j in range(self.n):
                if state[i][j] == 0:
                    return i, j

    def get_neighbors(self, state):
        blank_x, blank_y = self.find_blank(state)
        neighbors = []
        
        for dx, dy, move in self.moves:
            new_x, new_y = blank_x + dx, blank_y + dy

            if 0 <= new_x < self.n and 0 <= new_y < self.n:
                new_state = [list(row) for row in state]
                new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]

                neighbors.append((tuple(map(tuple, new_state)), move))
        
        return neighbors

    def solve(self):
        heap = []
        g_score = {self.initial: 0}
        f_score = {self.initial: self.manhattan_distance(self.initial)}
        came_from = {self.initial: None}
        move_from = {self.initial: None}

        heapq.heappush(heap, (f_score[self.initial], self.initial))

        while heap:
            _, current = heapq.heappop(heap)

            if current == self.goal:
                return self.reconstruct_path(came_from, move_from, current)

            for neighbor, move in self.get_neighbors(current):
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.manhattan_distance(neighbor)
                    came_from[neighbor] = current
                    move_from[neighbor] = move
                    heapq.heappush(heap, (f_score[neighbor], neighbor))
        
        return None  

    def reconstruct_path(self, came_from, move_from, current):
        path = []

        while move_from[current]:
            path.append(move_from[current])
            current = came_from[current]

        return path[::-1]


def read_matrix_from_filepath(path):
    with open(path, 'r') as f:
        # Matrix of digit places [start, end] group of Reguler Expression
        matrix_of_re_group = []

        # Result Matrix
        output_matrix = []

        # List of each line
        lines = f.readlines()

        # region Possible max value in n-puzzle problem and getting length
        row_length = col_length = len(lines)
        max_element = row_length ** 2 - 1
        max_element_str_length = len(str(max_element))
        #endregion

        # region Zero appended position as (row, col)
        zero_appended_row_ind = -1
        zero_appended_col_ind = -1
        # endregion

        # Iterate over each line and get [start, end] positions of digits and append to `matrix_of_re_group`
        for ind, line in enumerate(lines):
            # Remove unnecessary `\n` from line
            line = line.replace('\n', '')

            # `Ind` row and column length
            row = []
            col_length_of_row = 0

            for matched in re.finditer(r'\d+', line):                    
                row.append(matched)

                col_length_of_row += 1
            
            # If column length is different from row length, it means either Zero must be appended for first time
            # Otherwise, it is done second time, and raise Exception
            if col_length_of_row != row_length:
                # Never seen empty cell
                if zero_appended_row_ind == -1:
                    zero_appended_row_ind = ind
                
                # Seen second time of empty cell
                else:
                    raise TypeError('Make sure to put only one empty cell in order to solve N-Puzzle problem ')

            matrix_of_re_group.append(row)
        
        # If no empty cell is encountered, raise Exception to put empty cell in string
        if zero_appended_row_ind == -1:
            raise TypeError("Make sure to insert empty cell in order to solve N-Puzzle problem !")


        # Get lookup vector indices except Zero appended
        row_lookup_indices = list(
            set(range(row_length)) - set([zero_appended_row_ind])
        )
        # Expected column end indices 
        expected_col_end_indices = [-1] * col_length

        # Iterate over all columns and get corresponding row indices (except Zero appended row ) and
        # check if all ending positions of digits are same. If not, there is alignment problem !
        for i in range(col_length): 
            # Dictionary of endind place of digits
            end_place_digits = defaultdict(int)

            # Iterate over row lookup indices and count how many times end places of digits take place
            # Here, it is assumed that if dictionary has multiple end places, the most repetitive one (value, not key) is selected to be correct alignment
            # and rest of them will be incorrect ones, resulting Exception.  
            for j in range(len(row_lookup_indices)):
                end_place = matrix_of_re_group[row_lookup_indices[j]][i].end()
                
                end_place_digits[end_place] += 1

            # It is for sorting dictionary by `values` and getting most repetitive key value, Then, assign it to List[Tuple[int, int]]
            sorted_end_place_digits = sorted(
                end_place_digits.items(),
                key=lambda x : x[1], 
                reverse=True
            )

            # If there is multiple end places of digits, raise Exception
            if len(sorted_end_place_digits) > 1:
                raise TypeError(f'Column : {i} alignment problem' + 
                                '\nMake sure to fix alignments to proceed `N - Puzzle Problem`!')

            # Set most repetetive end place of digit to expected column end indices
            expected_col_end_indices[i] = sorted_end_place_digits[0][0]


        # Find intersection between expected column end indices and Zero appended row index, Set it to `List`
        intersection_of_end_indices = list(
            set(expected_col_end_indices) - set([matched.end() for matched in matrix_of_re_group[zero_appended_row_ind]])
        )

        # If the end places doesn't align between expected and Zero appended row index, raise Exception
        if len(intersection_of_end_indices) > 1:
            raise TypeError(f'Row : {zero_appended_row_ind} alignment problem' + 
                        '\nMake sure to fix alignments to proceed `N - Puzzle Problem`!')        

        # If there is one element left, It means, that is the position that 0 has to be inserted (Line index place, not column index)
        zero_appended_col_ind = [i for i in range(len(expected_col_end_indices)) if intersection_of_end_indices[0] == expected_col_end_indices[i]][0]
        
        # Region Generating Output Matrix and insert 0 to corresponding (row, column)
        output_matrix = [[int(matched.group()) for matched in row] for row in matrix_of_re_group]
        output_matrix[zero_appended_row_ind].insert(zero_appended_col_ind, 0)
        #endregion

        return output_matrix

def main(initial_state):
    solver = NPuzzle(initial_state) 
    solution = solver.solve()

    if solution:
        print("Solution found in", len(solution), "moves:")
        print(" -> ".join(solution))
    else:
        print("No solution exists for this puzzle.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', type=str, required=True, help='Filepath of initial matrix as .txt file')

    args = parser.parse_args()

    initial_state = read_matrix_from_filepath(args.filepath)

    print(initial_state)
    # main(initial_state)
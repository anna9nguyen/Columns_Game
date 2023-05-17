empty_cell = 'empty'
faller_moving_cell = 'faller moving'
faller_stopped_cell = 'faller stopped'
occupied_cell = 'occupied'
matching_cell = 'matching'


def matchable_state(state: str) -> bool:
    '''
    Determines if matching is possible
    '''
    return state == occupied_cell or state == matching_cell


left = -1
right = 1
down = 0
down_left = 2


none = 'none'
empty = ' '


class GameState:
    def __init__(self, rows: int, columns: int):
        self._rows = rows
        self._columns = columns
        
        self._board_rows = []
        self._board_states = []
        
        self._faller = Faller()
        
        for i in range(rows):
            row = []
            row_state = []
            
            for j in range(columns):
                row.append(empty)
                row_state.append(empty_cell)
                
            self._board_rows.append(row)
            self._board_states.append(row_state)



    def board_contents(self, contents: [[str]]) -> None:
        '''
        Assigns contents to game board
        Gravity is applied and matching is attempted
        
        '''
        for row in range(self.number_of_rows()):
            for column in range(self.number_of_columns()):
                value = contents[row][column]
                
                if value is empty:
                    self._cell(row, column, empty, empty_cell)
                    
                else:
                    self._cell(row, column, value, occupied_cell)

        self._gravity()
        self._matching()



    def clock(self) -> bool:
        '''
        Moves fallers down
        '''
        if self._faller.active:
            if self._faller.state == faller_stopped:
                self._update_faller_state()

                if self._faller.state == faller_stopped:
                    value = False

                    if self._faller.row_value() - 2 < 0:
                        value = True

                    for i in range(3):
                        self._cell(self._faller.row_value() - i, self._faller.column_value(), self._faller.contents[i], occupied_cell)
                    self._faller.active = False

                    self._matching()
                    
                    return value

            self._move_faller_down()

            self._update_faller_state()

        self._matching()
        
        return False



    def generate_faller(self, column: int, faller: [str, str, str]) -> None:
        '''
        Generates a faller in the specied column
        '''
        if self._faller.active:
            return

        self._faller.active = True
        
        self._faller.contents = faller
        
        self._faller.assign_row(0)
        self._faller.assign_column(column - 1)
        
        self._cell(0, self._faller.column_value(), self._faller.contents[0], faller_moving_cell)

        self._update_faller_state()



    def active_faller(self) -> bool:
        '''
        Determines if there is an active faller
        '''
        return self._faller.active



    def rotate(self) -> None:
        '''
        Rotates faller
        '''
        if not self._faller.active:
            return

        first_faller = self._faller.contents[0]
        second_faller = self._faller.contents[1]
        third_faller = self._faller.contents[2]

        self._faller.contents = [second_faller, third_faller, first_faller]
        
        for i in range(3):
            self._cell_contents(self._faller.row_value() - i, self._faller.column_value(), self._faller.contents[i])
            
        self._update_faller_state()



    def move_side(self, direction: int) -> None:
        '''
        Moves faller in specified direction when not blocked
        '''
        if not self._faller.active:
            return

        if not direction == right and not direction == left:
            return

        if (direction == left and self._faller.column_value() == 0) or (direction == right and self._faller.column_value() == self.number_of_columns() - 1):
            return

        target_move_column = self._faller.column_value() + direction

        for i in range(3):
            if self._faller.row_value() - i < 0:
                break

            if self.current_cell_state(self._faller.row_value() - i, target_move_column) == occupied_cell:
                return

        for i in range(3):
            if self._faller.row_value() - i < 0:
                break

            self._move_cell(self._faller.row_value() - i, self._faller.column_value(), direction)

        self._faller.assign_column(target_move_column)

        self._update_faller_state()



    def number_of_rows(self) -> int:
        '''
        Returns number of rows in current game board
        '''
        return self._rows



    def number_of_columns(self) -> int:
        '''
        Returns number of columns in current game board
        '''
        return self._columns



    def current_cell_state(self, row: int, column: int) -> str:
        '''
        Returns state of cell for the specified row and column
        '''
        return self._board_states[row][column]



    def current_cell_contents(self, row: int, column: int) -> str:
        '''
        Returns contents of cell for the specifid row and column
        '''
        return self._board_rows[row][column]



    def _cell(self, row: int, column: int, contents: str, state: str) -> None:
        '''
        Sets characteristics of cell for specified row and column
        '''

        if row < 0:
            return
        
        self._cell_contents(row, column, contents)
        self._cell_state(row, column, state)



    def _cell_contents(self, row: int, column: int, contents: str) -> None:
        '''
        Sets contents of cell for specified row and column
        '''
        if row < 0:
            return
        
        self._board_rows[row][column] = contents



    def _cell_state(self, row: int, column: int, state: str) -> None:
        '''
        Sets state of cell for specified row and column
        '''
        if row < 0:
            return
        
        self._board_states[row][column] = state



    def _gravity(self) -> None:
        '''
        Gravity is applied to all cells until it reaches a solid cell
        '''
        for column in range(self.number_of_columns()):
            for row in range(self.number_of_rows() - 1, -1, -1):
                state = self.current_cell_state(row, column)

                if state == faller_moving_cell or state == faller_stopped_cell:
                    continue
                
                if state == occupied_cell:
                    i = 1
                    
                    while not self._solid_faller(row + i, column):
                        self._move_cell(row + i - 1, column, down)
                        i += 1



    def _matching(self) -> None:
        '''
        Removes cells that are matching and applies gravity to remaining cells
        '''
        for row in range(self.number_of_rows()):
            for column in range(self.number_of_columns()):
                if self.current_cell_state(row, column) == matching_cell:
                    self._cell(row, column, empty, empty_cell)

        self._gravity()

        self._match_horizontal()
        self._match_vertical()
        self._match_diagonal()



    def _match_horizontal(self) -> None:
        '''
        Checks if cells are matching horizontally
        '''
        for current_row in range(self.number_of_rows() - 1, -1, -1):
            matches = 0
            jewel = none
            
            for column in range(0, self.number_of_columns()):
                contents = self.current_cell_contents(current_row, column)
                state = self.current_cell_state(current_row, column)
                
                cell_match = (contents == jewel and matchable_state(state))

                if cell_match:
                    matches += 1

                if column == self.number_of_columns() - 1:
                    if matches >= 3:
                        if cell_match:
                            self._mark_matched_cells(current_row, column, left, matches)

                        else:
                            self._mark_matched_cells(current_row, column-1, left, matches)
                            
                elif not cell_match:
                    if matches >= 3:
                        self._mark_matched_cells(current_row, column-1, left, matches)

                    if matchable_state(state):
                        jewel = contents
                        matches = 1
                    else:
                        jewel = none
                        matches = 1



    def _match_vertical(self) -> None:
        '''
        Checks if cells are matching vertically
        '''
        for current_column in range(0, self.number_of_columns()):
            matches = 0
            jewel = none
            
            for row in range(self.number_of_rows() - 1, -1, -1):
                contents = self.current_cell_contents(row, current_column)
                state = self.current_cell_state(row, current_column)
                
                cell_match = (contents == jewel and matchable_state(state))

                if cell_match:
                    matches += 1

                if row == 0:
                    if matches >= 3:
                        if cell_match:
                            self._mark_matched_cells(row, current_column, down, matches)
                            
                        else:
                            self._mark_matched_cells(row + 1, current_column, down, matches)
                            
                elif not cell_match:
                    if matches >= 3:
                        self._mark_matched_cells(row + 1, current_column, down, matches)

                    if matchable_state(state):
                        jewel = contents
                        matches = 1
                        
                    else:
                        jewel = none
                        matches = 1



    def _match_diagonal(self) -> None:
        '''
        Checks if cells are matching diagonally
        '''
        for current_row in range(self.number_of_rows() - 1, -1, -1):
            for current_column in range(0, self.number_of_columns()):
                matches = 0
                jewel = none
                
                row_count = 0
                column_count = 0
                
                while True:
                    row = current_row-row_count
                    column = current_column+column_count

                    contents = self.current_cell_contents(row, column)
                    state = self.current_cell_state(row, column)
                    
                    cell_match = (contents == jewel and matchable_state(state))

                    if cell_match:
                        matches += 1

                    if column == self.number_of_columns()-1 or row == 0:
                        if matches >= 3:
                            if cell_match:
                                self._mark_matched_cells(row, column, down_left, matches)
                                
                            else:
                                self._mark_matched_cells(row + 1, column - 1, down_left, matches)
                                
                    elif not cell_match:
                        if matches >= 3:
                            self._mark_matched_cells(row + 1, column - 1, down_left, matches)

                        if matchable_state(state):
                            jewel = contents
                            matches = 1
                            
                        else:
                            jewel = none
                            matches = 1

                    row_count += 1
                    column_count += 1

                    if current_row-row_count < 0 or current_column+column_count >= self.number_of_columns():
                        break



    def _mark_matched_cells(self, row: int, column: int, direction: int, amount: int) -> None:
        '''
        Determines that number of cells in specified direction are matching
        '''
        if direction == left:
            for target_column in range(column, column - amount, -1):
                self._cell_state(row, target_column, matching_cell)
                
        elif direction == down:
            for target_row in range(row, row + amount):
                self._cell_state(target_row, column, matching_cell)
                
        elif direction == down_left:
            for i in range(amount):
                self._cell_state(row + i, column - i, matching_cell)



    def _update_faller_state(self) -> None:
        '''
        Updates states of fallers on the current game board
        '''
        state = None
        target_row = self._faller.row_value() + 1
        
        if self._solid_faller(target_row, self._faller.column_value()):
            state = faller_stopped_cell
            self._faller.state = faller_stopped
            
        else:
            state = faller_moving_cell
            self._faller.state = faller_moving

        for i in range(3):
            row = self._faller.row_value() - i
            
            if row < 0:
                return
            
            self._cell(row, self._faller.column_value(), self._faller.contents[i], state)



    def _solid_faller(self, row: int, column: int) -> bool:
        '''
        Determines if faller is a solid or not
        '''
        if row >= self.number_of_rows():
            return True

        if self.current_cell_state(row, column) == occupied_cell:
            return True

        return False



    def _move_faller_down(self) -> None:
        '''
        Moves faller down
        '''
        if self._solid_faller(self._faller.row_value() + 1, self._faller.column_value()):
            return

        self._move_cell(self._faller.row_value(), self._faller.column_value(), down)

        if self._faller.row_value() - 1 >= 0:
            self._move_cell(self._faller.row_value() - 1, self._faller.column_value(), down)
            
            if self._faller.row_value() - 2 >= 0:
                self._move_cell(self._faller.row_value() - 2, self._faller.column_value(), down)

            else:
                self._cell(self._faller.row_value() - 1, self._faller.column_value(), self._faller.contents[2],
                               faller_moving_cell)

        else:
            self._cell(self._faller.row_value(), self._faller.column_value(), self._faller.contents[1], faller_moving_cell)

        self._faller.assign_row(self._faller.row_value() + 1)



    def _move_cell(self, row: int, column: int, direction: int) -> None:
        '''
        Moves cell in specified direction
        '''
        original_value = self._board_rows[row][column]
        original_state = self._board_states[row][column]

        self._board_rows[row][column] = empty
        self._board_states[row][column] = empty_cell

        if direction == down:
            target_row = row + 1
            self._board_rows[target_row][column] = original_value
            self._board_states[target_row][column] = original_state

        else:
            target_column = column + direction
            self._board_rows[row][target_column] = original_value
            self._board_states[row][target_column] = original_state


faller_stopped = 0
faller_moving = 1


class Faller:
    def __init__(self):
        self.active = False
        
        self._row = 0
        self._column = 0
        
        self.contents = [empty, empty, empty]
        self.state = faller_moving



    def row_value(self) -> int:
        '''
        Returns row value of faller
        '''
        return self._row



    def column_value(self) -> int:
        '''
        Return column value of faller
        '''
        return self._column



    def assign_row(self, row: int) -> None:
        '''
        Assigns the row value for faller
        '''
        self._row = row



    def assign_column(self, column: int) -> None:
        '''
        Assigns the column value for faller
        '''
        self._column = column

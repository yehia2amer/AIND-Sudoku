assignments = []

import collections

rows = "ABCDEFGHI"
cols = "123456789"

def cross(a,b):
    return [s+t for s in a for t in b]

boxes = cross(rows,cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(r,x) for r in ("ABC","DEF","GHI") for x in ("123","456","789")]
diagonal_units = [['A1', 'B2', 'C3', 'D4', 'E5', 'F6' , 'G7', 'H8' , 'I9'],['A9', 'B8', 'C7', 'D6', 'E5', 'F4' , 'G3', 'H2' , 'I1']]
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def grid_values(grid):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    assert len(grid) == 81
    values = []
    for item in grid:
        if item == '.':
            values.append('123456789')
        else:
            values.append(item)
    return dict(zip(boxes,values))

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def eliminate(values):
    """
    Use Elimination constraint propagation technique to eliminate values.
    Input: The sudoku in dictionary form
    Output: Reduced sudoku puzzle in dictionary form
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for value in solved_values:
        for peer in peers[value]:
            values[peer] = values[peer].replace(values[value],"")
    return values

def only_choice(values):
    """
    Use Only Choice constraint propogation technique to reduce values.
    Input: The sudoku in dictionary form
    Output: Reduced sudoku puzzle in dictionary form
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values

def reduce_puzzle(values):
    """
    Iteratively use eliminate and only choice strategy.
    Input: The sudoku in dictionary form
    Output: Reduced sudoku puzzle in dictionary form
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy
        values = eliminate(values)
        
        #  Use the Only Choice Strategy
        values = only_choice(values)

        #  Use the naked Twins Strategy
        values = naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    "Using depth-first search and propagation, try all possible values..
    Input: The sudoku in dictionary form
    Output: Reduced sudoku puzzle in dictionary form
    """
    
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)

    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!

    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers

    # Find all possible twins
    possible_twins = [box for box in values.keys() if len(values[box]) == 2]

    # Find all Naked twins
    naked_twins = {}
    for ptwin in possible_twins:
        for peer in peers[ptwin]:
            if (values[ptwin] == values[peer] and peer in possible_twins):
                    if (peer + ptwin not in naked_twins.keys() and ptwin + peer not in naked_twins.keys() ):
                        naked_twins[ptwin + peer] = values[ptwin]

    #Remove Naked Twins
    for naked_twin in naked_twins:
        first_cell = naked_twin[:2]
        second_cell = naked_twin[-2:]

        value = list(values[first_cell])

        first_cell_peers = set(peers[first_cell])
        second_cell_peers = set(peers[second_cell])
    
        naked_twin_peers_intersection = [x for x in first_cell_peers.intersection(second_cell_peers) if len(values[x]) != 1]
        for x in naked_twin_peers_intersection:

            table = {ord(char): None for char in values[first_cell]}
            assign_value(values, x, values[x].translate(table))

    return values

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = search(grid_values(grid))
    #If puzzle is solved return the values in dictionary form, else return False
    if all(len(values[s]) == 1 for s in boxes):
        return values
    else:
        return False

if __name__ == '__main__':
    diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')

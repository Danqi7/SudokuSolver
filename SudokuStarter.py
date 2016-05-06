#!/usr/bin/env python
import struct, string, math, time

class SudokuBoard:
    """This will be the sudoku board game object your player will manipulate."""

    def __init__(self, size, board):
      """the constructor for the SudokuBoard"""
      self.BoardSize = size #the size of the board
      self.CurrentGameBoard= board #the current state of the game board

    def set_value(self, row, col, value):
        """This function will create a new sudoku board object with the input
        value placed on the GameBoard row and col are both zero-indexed"""

        #add the value to the appropriate position on the board
        self.CurrentGameBoard[row][col]=value
        #return a new board of the same size with the value added
        return SudokuBoard(self.BoardSize, self.CurrentGameBoard)


    def print_board(self):
        """Prints the current game board. Leaves unassigned spots blank."""
        div = int(math.sqrt(self.BoardSize))
        dash = ""
        space = ""
        line = "+"
        sep = "|"
        for i in range(div):
            dash += "----"
            space += "    "
        for i in range(div):
            line += dash + "+"
            sep += space + "|"
        for i in range(-1, self.BoardSize):
            if i != -1:
                print "|",
                for j in range(self.BoardSize):
                    if self.CurrentGameBoard[i][j] > 9:
                        print self.CurrentGameBoard[i][j],
                    elif self.CurrentGameBoard[i][j] > 0:
                        print "", self.CurrentGameBoard[i][j],
                    else:
                        print "  ",
                    if (j+1 != self.BoardSize):
                        if ((j+1)//div != j/div):
                            print "|",
                        else:
                            print "",
                    else:
                        print "|"
            if ((i+1)//div != i/div):
                print line
            else:
                print sep

def parse_file(filename):
    """Parses a sudoku text file into a BoardSize, and a 2d array which holds
    the value of each cell. Array elements holding a 0 are considered to be
    empty."""

    f = open(filename, 'r')
    BoardSize = int( f.readline())
    NumVals = int(f.readline())

    #initialize a blank board
    board= [ [ 0 for i in range(BoardSize) ] for j in range(BoardSize) ]

    #populate the board with initial values
    for i in range(NumVals):
        line = f.readline()
        chars = line.split()
        row = int(chars[0])
        col = int(chars[1])
        val = int(chars[2])
        board[row-1][col-1]=val

    return board

def is_complete(sudoku_board):
    """Takes in a sudoku board and tests to see if it has been filled in
    correctly."""
    BoardArray = sudoku_board.CurrentGameBoard
    size = len(BoardArray)
    subsquare = int(math.sqrt(size))

    #check each cell on the board for a 0, or if the value of the cell
    #is present elsewhere within the same row, column, or square
    for row in range(size):
        for col in range(size):
            if BoardArray[row][col]==0:
                return False
            for i in range(size):
                if ((BoardArray[row][i] == BoardArray[row][col]) and i != col):
                    return False
                if ((BoardArray[i][col] == BoardArray[row][col]) and i != row):
                    return False
            #determine which square the cell is in
            SquareRow = row // subsquare
            SquareCol = col // subsquare
            for i in range(subsquare):
                for j in range(subsquare):
                    if((BoardArray[SquareRow*subsquare+i][SquareCol*subsquare+j]
                            == BoardArray[row][col])
                        and (SquareRow*subsquare + i != row)
                        and (SquareCol*subsquare + j != col)):
                            return False
    return True

def init_board(file_name):
    """Creates a SudokuBoard object initialized with values from a text file"""
    board = parse_file(file_name)
    return SudokuBoard(len(board), board)

def is_valid(sudoku_board, row, col, value):
    """Check whether it would be valid to put value at the input position"""
    BoardArray = sudoku_board.CurrentGameBoard
    size = len(BoardArray)
    subsquare = int(math.sqrt(size))
    SquareRow = row // subsquare
    SquareCol = col // subsquare

    for i in range(size):
        if BoardArray[row][i] == value:
            return False
        if BoardArray[i][col] == value:
            return False

    for i in range(subsquare):
        for j in range(subsquare):
            if BoardArray[SquareRow*subsquare+i][SquareCol*subsquare+j] == value:
                return False

    return True


def MRV_checking(initial_board, empty, visited, rowmap, colmap, sqrmap):
    """MRV_check recursively searches the right value to fill the board
    and return True if a solution is found otherwise return False"""
    BoardArray = initial_board.CurrentGameBoard
    size = initial_board.BoardSize
    subsquare = int(math.sqrt(initial_board.BoardSize))

    #compute the variable with the minimum remaining values
    minValue = 1000
    minIndex = 0
    num_empty = 0

    for i in range(len(empty)):
        cell = empty[i]
        tr = cell[0]
        tc = cell[1]
        if visited[i] == 0:
            num_empty = num_empty + 1
            Squaretr = tr // subsquare
            Squaretc = tc // subsquare
            temp = 0
            for j in range(size):
                if rowmap[tr][j] == 0 and colmap[tc][j] == 0 and sqrmap[Squaretr*subsquare+Squaretc][j] == 0:
                    temp = temp + 1
            if temp < minValue:
                minValue = temp
                minIndex = i

    if num_empty == 0:
        return True

    currentCell = empty[minIndex]
    row = currentCell[0]
    col = currentCell[1]
    SquareRow = row // subsquare
    SquareCol = col // subsquare

    visited[minIndex] = 1
    for num in range(1,initial_board.BoardSize+1):
        #if num doesn't exit in its row, col nor square
        if rowmap[row][num-1] == 0 and colmap[col][num-1] == 0 and sqrmap[SquareRow*subsquare+SquareCol][num-1] == 0:
            initial_board.set_value(row, col, num)
            #mark the map
            rowmap[row][num-1] = 1
            colmap[col][num-1] = 1
            sqrmap[SquareRow*subsquare+SquareCol][num-1] = 1

            #success
            if MRV_checking(initial_board, empty, visited, rowmap, colmap, sqrmap) == True:
                return True
            else:
                #fail -> unmark the map
                #initial_board.set_value(row, col, 0)
                rowmap[row][num-1] = 0
                colmap[col][num-1] = 0
                sqrmap[SquareRow*subsquare+SquareCol][num-1] = 0


    visited[minIndex] = 0
    return False

def degree_checking(initial_board, empty, visited, rowmap, colmap, sqrmap):
    """degree_checking recursively searches the right value to fill the board
    and return True if a solution is found otherwise return False"""
    BoardArray = initial_board.CurrentGameBoard
    size = initial_board.BoardSize
    subsquare = int(math.sqrt(initial_board.BoardSize))

    #compute the variable invloved with the largest constraint on unassigned variables
    maxValue = -1
    maxIndex = 0
    num_empty = 0

    for i in range(len(empty)):
        cell = empty[i]
        tr = cell[0]
        tc = cell[1]
        if visited[i] == 0:
            num_empty = num_empty + 1
            Squaretr = tr // subsquare
            Squaretc = tc // subsquare
            temp = 0
            for j in range(size):
                if rowmap[tr][j] == 0:
                    temp = temp + 1
                if colmap[tc][j] == 0:
                    temp = temp + 1
                if sqrmap[Squaretr*subsquare+Squaretc][j] == 0:
                    temp = temp + 1
            if temp > maxValue:
                maxValue = temp
                maxIndex = i

    if num_empty == 0:
        return True

    currentCell = empty[maxIndex]
    row = currentCell[0]
    col = currentCell[1]
    SquareRow = row // subsquare
    SquareCol = col // subsquare

    visited[maxIndex] = 1
    for num in range(1,initial_board.BoardSize+1):
        #if num doesn't exit in its row, col nor square
        if rowmap[row][num-1] == 0 and colmap[col][num-1] == 0 and sqrmap[SquareRow*subsquare+SquareCol][num-1] == 0:
            initial_board.set_value(row, col, num)
            #mark the map
            rowmap[row][num-1] = 1
            colmap[col][num-1] = 1
            sqrmap[SquareRow*subsquare+SquareCol][num-1] = 1

            #success
            if degree_checking(initial_board, empty, visited, rowmap, colmap, sqrmap) == True:
                return True
            else:
                #fail -> unmark the map
                rowmap[row][num-1] = 0
                colmap[col][num-1] = 0
                sqrmap[SquareRow*subsquare+SquareCol][num-1] = 0


    visited[maxIndex] = 0
    return False

def LCV_checking(initial_board, empty, visited, rowmap, colmap, sqrmap, index):
    """LCV_check recursively searches the right value to fill the board
    and return True if a solution is found otherwise return False"""

    if index == len(empty):
        return True

    size = initial_board.BoardSize
    currentCell = empty[index]
    row = currentCell[0]
    col = currentCell[1]

    subsquare = int(math.sqrt(initial_board.BoardSize))
    SquareRow = row // subsquare
    SquareCol = col // subsquare


    used_value = [0]*size
    for j in range(size):
        if rowmap[row][j] == 1:
            used_value[j] = 1
        if colmap[col][j] == 1:
            used_value[j] = 1
        if sqrmap[SquareRow*subsquare+SquareCol][j] == 1:
            used_value[j] = 1


    visited[index] = 1
    while sum(used_value) != size:
        minSum = 1000
        temp_sum = 0
        bestValue = 1
        for num in range(1,initial_board.BoardSize+1):
            if rowmap[row][num-1] == 0 and colmap[col][num-1] == 0 and sqrmap[SquareRow*subsquare+SquareCol][num-1] == 0:
                #haven't tried this value yet
                if used_value[num-1] == 0:
                    #compute its impact on other unassigned
                    for i in range(len(empty)):
                        if visited[i] == 0:
                            temprow = empty[i][0]
                            tempcol = empty[i][1]
                            temprowsub = temprow // subsquare
                            tempcolsub = tempcol // subsquare
                            if temprow == row:
                                if colmap[tempcol][num-1] == 0:
                                    temp_sum = temp_sum + 1
                                if sqrmap[temprowsub*subsquare+tempcolsub][num-1] == 0:
                                    temp_sum = temp_sum + 1
                            if tempcol == col:
                                if rowmap[temprow][num-1] == 0:
                                    temp_sum = temp_sum + 1
                                if sqrmap[temprowsub*subsquare+tempcolsub][num-1] == 0:
                                    temp_sum = temp_sum + 1
                            if temprowsub*subsquare+tempcolsub == SquareRow*subsquare+SquareCol:
                                if colmap[tempcol][num-1] == 0:
                                    temp_sum = temp_sum + 1
                                if rowmap[temprow][num-1] == 0:
                                    temp_sum = temp_sum + 1
                    if temp_sum < minSum:
                        minSum = temp_sum
                        bestValue = num

        #first try the best value
        initial_board.set_value(row, col, bestValue)
        used_value[bestValue-1] = 1
        #mark the map
        rowmap[row][bestValue-1] = 1
        colmap[col][bestValue-1] = 1
        sqrmap[SquareRow*subsquare+SquareCol][bestValue-1] = 1

        #success
        if LCV_checking(initial_board, empty, visited, rowmap, colmap, sqrmap, index+1) == True:
            return True
        else:
            #fail -> unmark the map
            rowmap[row][bestValue-1] = 0
            colmap[col][bestValue-1] = 0
            sqrmap[SquareRow*subsquare+SquareCol][bestValue-1] = 0

    visited[index] = 0

    return False

def forward_check(initial_board, empty, visited, rowmap, colmap, sqrmap, index, MRV = False, Degree = False,
    LCV = False):
    """forward_check recursively searches the right value to fill the board
    and return True if a solution is found otherwise return False"""

    BoardArray = initial_board.CurrentGameBoard
    size = initial_board.BoardSize
    subsquare = int(math.sqrt(initial_board.BoardSize))

    if MRV == True:
        #compute the variable with the minimum remaining values
        minValue = 1000
        num_empty = 0

        for i in range(len(empty)):
            cell = empty[i]
            tr = cell[0]
            tc = cell[1]
            if visited[i] == 0:
                num_empty = num_empty + 1
                Squaretr = tr // subsquare
                Squaretc = tc // subsquare
                temp = 0
                for j in range(size):
                    if rowmap[tr][j] == 0 and colmap[tc][j] == 0 and sqrmap[Squaretr*subsquare+Squaretc][j] == 0:
                        temp = temp + 1
                if temp < minValue:
                    minValue = temp
                    targetIndex = i
    elif Degree == True:
        #compute the variable invloved with the largest constraint on unassigned variables
        maxValue = -1
        num_empty = 0

        for i in range(len(empty)):
            cell = empty[i]
            tr = cell[0]
            tc = cell[1]
            if visited[i] == 0:
                num_empty = num_empty + 1
                Squaretr = tr // subsquare
                Squaretc = tc // subsquare
                temp = 0
                for j in range(size):
                    if rowmap[tr][j] == 0:
                        temp = temp + 1
                    if colmap[tc][j] == 0:
                        temp = temp + 1
                    if sqrmap[Squaretr*subsquare+Squaretc][j] == 0:
                        temp = temp + 1
                if temp > maxValue:
                    maxValue = temp
                    targetIndex= i
    else:
        targetIndex = index

    if MRV == False and Degree == False:
        if index == len(empty):
            return True
    else:
        if num_empty == 0:
            return True

    currentCell = empty[targetIndex]
    row = currentCell[0]
    col = currentCell[1]
    SquareRow = row // subsquare
    SquareCol = col // subsquare

    visited[targetIndex] = 1
    for num in range(1,initial_board.BoardSize+1):
        #if num doesn't exit in its row, col nor square
        if rowmap[row][num-1] == 0 and colmap[col][num-1] == 0 and sqrmap[SquareRow*subsquare+SquareCol][num-1] == 0:
            initial_board.set_value(row, col, num)
            #mark the map
            rowmap[row][num-1] = 1
            colmap[col][num-1] = 1
            sqrmap[SquareRow*subsquare+SquareCol][num-1] = 1

            #success
            if forward_check(initial_board, empty, visited, rowmap, colmap, sqrmap, index+1, MRV, Degree, LCV) == True:
                return True
            else:
                rowmap[row][num-1] = 0
                colmap[col][num-1] = 0
                sqrmap[SquareRow*subsquare+SquareCol][num-1] = 0

    visited[targetIndex] = 0

    return False

def backtrack(initial_board, empty, index):
    """Backtrack recursively searches the right value to fill the board
    and return True if a solution is found otherwise return False"""
    if index == len(empty)-1:
        return True

    currentCell = empty[index]
    row = currentCell[0]
    col = currentCell[1]
    for num in range(1,initial_board.BoardSize+1):
        if is_valid(initial_board, row, col, num):
            initial_board.set_value(row, col, num)
            if backtrack(initial_board, empty, index+1) == True:
                return True
            else:
                initial_board.set_value(row, col, 0)
    return False


def solve(initial_board, forward_checking = False, MRV = False, Degree = False,
    LCV = False):
    """Takes an initial SudokuBoard and solves it using back tracking, and zero
    or more of the heuristics and constraint propagation methods (determined by
    arguments). Returns the resulting board solution. """


    BoardArray = initial_board.CurrentGameBoard
    size = initial_board.BoardSize

    empty = []
    rowmap = []
    colmap = []
    sqrmap = []
    subsquare = int(math.sqrt(initial_board.BoardSize))

    #construct the map that marks the valid input
    for i in range(size):
        rowmap.append([0]*size)
        colmap.append([0]*size)
        sqrmap.append([0]*size)

    #construct the initial empty cell list and mark the valid input
    for row in range(size):
        for col in range(size):
            current = BoardArray[row][col]
            SquareRow = row // subsquare
            SquareCol = col // subsquare
            if current == 0:
                empty.append((row,col))
            else:
                rowmap[row][current-1] = 1
                colmap[col][current-1] = 1
                sqrmap[SquareRow*subsquare+SquareCol][current-1] = 1



    start_time = time.time()
    visited = [0]*len(empty)

    if forward_checking == True:
        forward_check(initial_board, empty, visited, rowmap, colmap, sqrmap, 0, MRV, Degree, LCV)
    elif MRV == True:
         MRV_checking(initial_board, empty, visited, rowmap, colmap, sqrmap)
    elif Degree == True:
         degree_checking(initial_board, empty, visited, rowmap, colmap, sqrmap)
    elif LCV == True:
        LCV_checking(initial_board, empty, visited, rowmap, colmap, sqrmap, 0)
    else:
        backtrack(initial_board, empty, 0)

    elapsed_time = time.time() - start_time;
    print "The time used: "
    print elapsed_time
    initial_board.print_board()
    return initial_board



if __name__ == '__main__':
    sb = init_board("input_puzzles/more/16x16/16x16.5.sudoku")
    sb1 = init_board("input_puzzles/more/25x25/25x25.2.sudoku")
    sb2 = init_board("input_puzzles/easy/25_25.sudoku")
    sb3 = init_board("input_puzzles/easy/25_25.sudoku")
    # fb = solve(sb,False,True,False,False)
    # if is_complete(fb) == True:
    #     print "YAY!"
    #fb1 = solve(sb1,False,True,False,False)
    #if is_complete(fb1) == True:
    #    print "YAY AGAIN!"
    #sb2.print_board()
    #fb2 = solve(sb2,False,True,False,False)
    #fb2 = solve(sb2,True)
    #if is_complete(fb2) == True:
    # print "YAY!"
    sb3.print_board()
    fb3 = solve(sb3,True,False,True,False)
    if is_complete(fb3) == True:
     print "YAY!"

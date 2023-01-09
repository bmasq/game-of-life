import random
import time
import os
clear = lambda : os.system("clear")

# sef-note: length, width, chars, etc. as arguments if not exception

CHARA = '\u2588'  # alive
CHARD = ' ' # dead
PROB = 0.5 # probability to birth a cell
WIDTH = 78
HEIGHT = 22

def init(width, length):
    cells = list()
    for i in range(length):
        cells.append(list())
        for j in range(width):
            if random.random() < PROB:
                cells[i].append(CHARA)
            else:
                cells[i].append(CHARD)
    return cells

# def boardtoStr(cells):
#     centre = ''
#     for row in cells:
#         centre += '|' + '|'.join(row) + '|\n'
#     row_length = len(row) + 2 + len(row) - 1
#     border = ['+' + '-' * row_length + '+']
#     border += ['|' + ' ' * row_length + '|' for row in cells]
#     border += ['+' + '-' * row_length + '+']
#     output = '\n'.join(border)
#     return output

def cellsToStr(cells):
    out = ""
    for row in cells:
        out += ''.join(row) + '\n'
    return out

# returns a new matrix of cells
def updateState(cells):
    new = cells[:]
    for i in range(len(cells)):
        for j in range(len(cells[0])):
            neighbours = countNeighbours(cells, i, j)
            # The cell dies
            if (isAlive(cells, i, j) and
                    not (neighbours == 2 or neighbours == 3)):
                new[i][j] = CHARD
            # A cell is born
            elif (not isAlive(cells, i, j) and neighbours == 3):
                new[i][j] = CHARA
    return new

# counts the alive neighbours, horizontally, vertically and diagonally
def countNeighbours(cells, i, j):
    count = 0
    if isAlive(cells, i-1, j): # 12 o'clock
        count += 1
    if isAlive(cells, i-1, j+1): # 2 o'clock
        count += 1
    if isAlive(cells, i, j+1): # 3 o'clock
        count += 1
    if isAlive(cells, i+1, j+1): # 4 o'clock
        count += 1
    if isAlive(cells, i+1, j): # 6 o'clock
        count += 1
    if isAlive(cells, i+1, j-1): # 8 o'clock
        count += 1
    if isAlive(cells, i, j-1): # 9 o'clock
        count += 1
    if isAlive(cells, i-1, j-1): # 10 o'clock
        count += 1
    return count

# deals with out of bounds checks
def isAlive(cells, i, j):
    if i < 0 or j < 0:
        return False
    try:
        return cells[i][j] == CHARA
    except IndexError:
        return False

# for now only works with enter
def pressKey(message):
    input(message)

# main

# beautiful title if figlet is installed
try:
    os.system("figlet GAME OF LIFE")
except:
    print("GAME OF LIFE")
print()

first_batch = init(WIDTH, HEIGHT)[:]
print("ESTAT INICIAL")
print()
print(cellsToStr(first_batch))
pressKey("Prem ENTER per començar...")

batch = first_batch[:]
while True:
    clear()
    batch = updateState(batch)[:]
    print(cellsToStr(batch))
    # here goes if stable state: END / or inside updateState
    time.sleep(0.75)
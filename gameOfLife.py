import random
import time
import os
import subprocess
import copy
import sys

if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
    clear = lambda : os.system("clear")
elif sys.platform.startswith("win"):
    clear = lambda : os.system("cls")

CHARA = '\u2588'  # alive
CHARD = ' ' # dead
PROB = 0.1 # probability to birth a cell
WIDTH = 75
HEIGHT = 15
DELAY = 0.5 # delay between generations

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

def cellsToStr(cells):
    out = ""
    for row in cells:
        out += ''.join(row) + '\n'
    return out

def borderedCells(cells):
    border_length = len(cells[0])
    out = '+' + '-' * border_length + "+\n"
    rows = ['|' + ''.join(row) + '|' for row in cells]
    out += '\n'.join(rows) + '\n'
    out += '+' + '-' * border_length + "+\n"
    return out

# failure in use of decorator
""" # decorates the string of cells with upper and lower borders
def wrapCells(func):
    def wrapper(*args, **kwargs):
        print('+' + '-'*len(args[0]) + '+\n')
        print(func(*args, **kwargs))
        print('+' + '-'*len(args[0]) + '+\n')
    return wrapper()

wrappedCells = wrapCells(cellsToStr) """

# returns a new matrix of cells
def updateState(cells):
    new = copy.deepcopy(cells)
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
    # if listsEqual(cells, new):
    if cells == new:
        clear()
        display(new, startTime, genCount)
        print("The game has reached a stable, ummutable state")
        print()
        print("The initial state was this:")
        print()
        print(borderedCells(firstBatch))
        exit()
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

def display(cells, time0, gen):
    output = ""
    # returns a tuple of ints
    now = clock(int(time.time()) - time0)
    # converts the ints to strings
    now = map(str, now)
    # adds a leading zero (if one digit)
    now = tuple(s.zfill(2) for s in now)
    output += ':'.join(now) + "   "
    output += "Generation: {}   ".format(gen)
    cellCount = countCells(cells)
    output += "Cells: {}  ".format(cellCount[0])
    output += "Cells alive: {}   ".format(cellCount[1])
    output += "Cells dead: {}".format(cellCount[2])
    title(len(output))
    output += '\n' + '_'*len(output) + '\n'*2
    print(output + cellsToStr(cells))

def countCells(cells):
    alive = 0
    dead = 0
    for row in cells:
        alive += row.count(CHARA)
        dead += row.count(CHARD)
    return alive+dead, alive, dead

# converts a time in seconds to hours, minutes and seconds
def clock(s):
    h = s // 3600
    s -= h*3600
    m = s // 60
    s -= m*60
    return h, m, s

# returns true if the two lists are exactly the same
def listsEqual(l1, l2):
    for a, b in zip(l1,l2):
        for c, d in zip(a,b):
            if c != d:
                return False
    return True

# beautiful title if figlet is installed
def title(centred=0):
    try:
        subprocess.run(["figlet", "GAME OF LIFE"],
                        check=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("GAME OF LIFE".center(centred))
        print()


# main

clear()
title(WIDTH)
firstBatch = init(WIDTH, HEIGHT)
print("INITIAL STATE".center(WIDTH))
print()
print(cellsToStr(firstBatch))
print()
pressKey("Press ENTER to start...")
startTime = int(time.time())

batch = copy.deepcopy(firstBatch)
genCount = 0
while True:
    clear()
    batch = updateState(batch)
    genCount += 1
    display(batch, startTime, genCount)
    # here goes if stable state: END / or inside updateState
    time.sleep(DELAY)
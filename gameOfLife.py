import random
import time
import os
import subprocess
import copy
import sys
import math
import re

def main():
    # makes clear function cross-platform
    global clear
    if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
        clear = lambda : os.system("clear")
    elif sys.platform.startswith("win"):
        clear = lambda : os.system("cls")
    else:
        print("Your OS seems to be incompatible...")
        exit()

    # Constants initialization (defalut, as args or from input)
    try:
        if len(sys.argv) <= 1:
            setConstants()
            # menu()
        elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
            displayHelp()
            exit()
        else:
            args = dict(arg.split('=') for arg in sys.argv[1:])
            setConstants(**args)
    except (ValueError, KeyError) as e:
        print("\nERROR: " + e.args[0])
        displayHelp()
        exit()

    #program starts
    try:
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
            updateRes = updateState(batch)
            batch = updateRes[0]
            if updateRes[1]: # true if reached still-live
                clear()
                display(batch, startTime, genCount)
                print("The game has reached a still-live state")
                print()
                print("The initial state was this:")
                print()
                print(borderedCells(firstBatch))
                exit()
            genCount += 1
            display(batch, startTime, genCount)
            # here goes if stable state: END / or inside updateState
            time.sleep(DELAY)
    except KeyboardInterrupt:
        print("\nProgram terminated\n")

###

def setConstants(**kwargs):
    # checks for typos
    validParams = ["prob", "delay", "width", "height", "time", "gens"]
    for param in kwargs.keys():
        if param not in validParams:
            raise KeyError("'{}': invalid parameter".format(param))
    # alive, dead, probability of a cell to start alive, delay between generations
    global CHARA, CHARD, PROB, DELAY, WIDTH, HEIGHT, GENMAX, MAXTIME
    CHARA = '\u2588'
    CHARD = ' '

    PROB = float(kwargs.get("prob", 0.3)) / 100
    if not isinstance(PROB, float) or PROB <= 0:
        raise ValueError("Invalid value for 'prob', it should be a positive decimal.")

    DELAY = float(kwargs.get("delay", 0.5))
    if not isinstance(DELAY, float) or DELAY <= 0:
        raise ValueError("Invalid value for 'delay', it should be a positive decimal.")
    
    WIDTH = int(kwargs.get("width", 75))
    if not isinstance(WIDTH, int) or WIDTH <= 0:
        raise ValueError("Invalid value for 'width', it should be a positive integer.")
    
    HEIGHT = int(kwargs.get("height", 15))
    if not isinstance(HEIGHT, int) or HEIGHT <= 0:
        raise ValueError("Invalid value for 'height', it should be a positive integer.")
    
    MAXTIME = kwargs.get("time", math.inf)
    # Xdies | Xhores | Xminuts | X[segons] | [h]:m:s
    match = re.search("^([0-9]+d|[0-9]+h|[0-9]+m|[0-9]+s?)$|^([0-9]+:)?[0-5]?[0-9]:[0-5]?[0-9]$",
                        str(MAXTIME))
    matches = match != None
    if matches:
        MAXTIME = strToSeconds(MAXTIME)
    elif (MAXTIME != math.inf or MAXTIME <= 0):
        raise ValueError("Invalid value for 'time', it should be a positive integer or a correct expression.")
    
    try:
        GENMAX = int(kwargs.get("gens", math.inf))
        if (not isinstance(GENMAX, int) or GENMAX != math.inf) or GENMAX <= 0:
            raise ValueError("Invalid value for 'gens', it should be a positive integer.")
    except OverflowError:
        GENMAX = math.inf

def displayHelp():
    text="""
usage: python3 {filename} [prob=<decimal>] [delay=<seconds>] [width=<integer>] [height=<integer>] [time=<expr>] [gens=<integer>] [-h | --help]

PARAMETERS

    prob
        Probability in percentage (do not include '%') that a cell starts alive
    
    delay
        Seconds between each generation (can be in fractions of a second)

    width
        Number of cells horizontally
    
    height
        Number of cells vertically

    time
        Expression for the time the program will run (n is an integer):
            {{nd|nh|nm|n[s]}}| {{[h:]m:s}}

    gens
        Number of generations where the program will stop when reached

    -h, --help
        Displays this help
    
    """.format(filename=sys.argv[0].split(os.sep)[-1])
    print(text)

def init(width, height):
    cells = list()
    for i in range(height):
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

# returns the new generation of cells,
# and true if it is equal to the previous one
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
    # if cells == new:
    #     clear()
    #     display(new, startTime, genCount)
    #     print("The game has reached a stable, ummutable state")
    #     print()
    #     print("The initial state was this:")
    #     print()
    #     print(borderedCells(firstBatch))
    #     exit()
    return new, cells == new

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
    output += "Elapsed time " + ':'.join(now) + "   "
    output += "Generation: {}   ".format(gen)
    cellCount = countCells(cells)
    output += "Cells: {}  ".format(cellCount[0])
    output += "Alive: {}   ".format(cellCount[1])
    output += "Dead: {}".format(cellCount[2])
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

# converts a string matching the desired pattern (setConstants) into an int
def strToSeconds(st):
    def days(d):
        return round(int(d)/24/3600)
    def hours(h):
        return round(int(h)/3600)
    def minutes(m):
        return round(int(m)/60)

    sec = 0
    lis = st.split(':')
    if len(lis) == 1:
        st = lis[0]
        if st.endswith('d'):
            return days(st.rstrip('d'))
        elif st.endswith('h'):
            return hours(st.rstrip('h'))
        elif st.endswith('m'):
            return minutes(st.rstrip('m'))
        elif st.endswith('s'):
            return int(st.rstrip('s'))
        else:
            return int(st)
    elif len(lis) == 2:
        sec += minutes(lis[0])
        sec += int(lis[1])
        return sec
    elif len(lis) == 3:
        sec += hours(lis[0])
        sec += minutes(lis[1])
        sec += int(lis[2])
        return sec

# beautiful title if figlet is installed
def title(centred=0):
    try:
        subprocess.run(["figlet", "GAME OF LIFE"],
                        check=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("GAME OF LIFE".center(centred))
        print()

###

main()
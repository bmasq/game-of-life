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
            mainMenu()
        elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
            displayHelp()
            exit()
        else:
            args = dict(arg.split('=') for arg in sys.argv[1:])
            setConstants(**args)
        # it will be used to store a past state and check for cycles
        pastState = {"cells":[], "gen":0, "count":0}
        cycleDetected = False

    #program starts
        clear()
        title(WIDTH)
        print("INITIAL STATE".center(WIDTH))
        print()
        print(cellsToStr(FIRST_BATCH))
        print()
        pressKey("Press ENTER to start...")
        batch = copy.deepcopy(FIRST_BATCH)
        genCount = 0
        startTime = int(time.time())

        while True:
            clear()
            updateRes = updateState(batch)
            batch = updateRes[0]
            if updateRes[1]:
                stop(batch, startTime, genCount,
                    "The game has reached a still-live state")
            elif genCount >= GENMAX:
                stop(batch, startTime, genCount,
                    "The game has reached the maximum number of generations")
            elif (int(time.time() - startTime)) >= MAXTIME:
                stop(batch, startTime, genCount,
                    "The game has reached the maximum time limit")
            genCount += 1
            display(batch, startTime, genCount)
            if not cycleDetected:
              res = cycleCheck(pastState, batch, genCount)
              cycleDetected = res[0]
              period = res[1] + 1
            else:
                print("A cycle of period {} has been detected, the cells will not evolve further".format(period))
            time.sleep(DELAY)
    except (ValueError, KeyError) as e:
        print("\nERROR: " + e.args[0])
        displayHelp()
        exit()
    except KeyboardInterrupt:
        try:
            clear()
            cycle = ""
            if cycleDetected:
                cycle = "\nThe cells were cycling with a period of {}".format(period)
            stop(batch, startTime, genCount,
                "\nProgram terminated by user\n" + cycle)
        # if KeyboardInterrupt is pressed before start
        except UnboundLocalError:
            pass

###

def mainMenu():
    message = """
DEFAULT VALUES:
- Horizontal cells_____________________75
- Vertical cells_______________________15
  (cells are rectangular characters)
- Probability__________________________30%
  (of a cell to be alive at the start)
- Secons between generations___________0.5
- Maximum running time_________________infinite
  (expression {{nd|nh|nm|n[s]}} | {{[h:]m:s}},
  as in days or hours or minutes or seconds, or
  hh:mm:ss - hours optional)
- Maximum number of generations________infinite
- Cycling period_______________________10
  (number of generations it will check
  to find a cycling pattern)
    """
    title()
    print()
    print(message)
    print()
    try:
        answ = tryInput("Do you want to customize these parameters? ",
                        "^$|^[y,Y,n,Y]$")
        if matches(answ, "^$|^[y,Y]$"):
            paramsMenu()
        else:
            setConstants()
    except (KeyboardInterrupt, ValueError):
        raise

def paramsMenu():
    keyLis = ["width", "height", "prob", "delay", "time", "gens", "period"]
    friendlyNames = [
        "Horizontal cells",
        "Vertical cells",
        "Probability",
        "Seconds between generations",
        "Maximum running time",
        "Maximum number of generations",
        "Cycling period"
        ]
    # builds a dict relating code keys with user friendly names
    friendly = dict()
    for k, f in zip(keyLis, friendlyNames):
        friendly[k] = f
    keys = iter(keyLis)
    params = dict()
    print("\nLeave blank for default value\n")
    try:
        params[next(keys)] = tryInput("Horizontal cells? ", "^$|^[0-9]+$")
        params[next(keys)] = tryInput("Vertical cells? ", "^$|^[0-9]+$")
        params[next(keys)] = tryInput("Probability? ", "^$|^[0-9]+(.[0-9]+)?$")
        params[next(keys)] = tryInput("Secons between generations? ", "^$|^[0-9]+(.[0-9]+)?$")
        params[next(keys)] = tryInput("Maximum running time? ",
        # Xdays | Xhours | Xminutes | X[seconds] | [h:]m:s
        "^$|^([0-9]+d|[0-9]+h|[0-9]+m|[0-9]+s?)$|^([0-9]+:)?[0-5]?[0-9]:[0-5]?[0-9]$")
        params[next(keys)] = tryInput("Maximum number of generations? ", "^$|^[0-9]+$")
        params[next(keys)] = tryInput("Cycling period? ", "^$|^[0-9]+$")
        # removes empty strings, so the params will be set to default
        aux = copy.deepcopy(params)
        for key, val in aux.items():
            if val == "":
                params.pop(key)
        setConstants(**params)
    except KeyboardInterrupt:
        raise
    # asks the user to correct only wrong parameters
    except ValueError as e:
        ok = False
        key = e.args[1]
        while not ok:
            if key in ["width", "height", "gens", "period"]:
                pattern = "^$|^[0-9]+$"
            elif key in ["prob", "delay"]:
                pattern = "^$|^[0-9]+(.[0-9]+)?$"
            elif key == "time":
                pattern = "^$|^([0-9]+d|[0-9]+h|[0-9]+m|[0-9]+s?)$|^([0-9]+:)?[0-5]?[0-9]:[0-5]?[0-9]$"
            else:
                pattern = ""
            print("\nWrong value for {}\n".format(friendly[key]))
            params[key] = tryInput("Please, try again: ", pattern)
            try:
                setConstants(**params)
                ok = True
            except ValueError:
                ok = False
    
def tryInput(question, regex):
    ok = False
    while not ok:
        try:
            answ = input(question)
            ok = matches(answ, regex)
            if not ok:
                print("\nERROR: invalid input\n")
        except KeyboardInterrupt:
            raise
    return answ
    
def setConstants(**kwargs):
    # checks for typos
    validParams = ["prob", "delay", "width", "height", "time", "gens", "period"]
    for param in kwargs.keys():
        if param not in validParams:
            raise KeyError("'{}': invalid parameter".format(param))
    # alive, dead, probability of a cell to start alive, delay between generations
    global CHARA, CHARD, PROB, DELAY, WIDTH, HEIGHT
    global  GENMAX, MAXTIME, FIRST_BATCH, PERIOD
    CHARA = '\u2588' # this character █
    CHARD = ' '

    PROB = float(kwargs.get("prob", 30)) / 100
    if not isinstance(PROB, float) or PROB <= 0:
        raise ValueError("Invalid value for 'prob', it should be a positive decimal.", "prob")

    DELAY = float(kwargs.get("delay", 0.5))
    if not isinstance(DELAY, float) or DELAY <= 0:
        raise ValueError("Invalid value for 'delay', it should be a positive decimal.", "delay")
    
    WIDTH = int(kwargs.get("width", 75))
    if not isinstance(WIDTH, int) or WIDTH <= 0:
        raise ValueError("Invalid value for 'width', it should be a positive integer.", "width")
    
    HEIGHT = int(kwargs.get("height", 15))
    if not isinstance(HEIGHT, int) or HEIGHT <= 0:
        raise ValueError("Invalid value for 'height', it should be a positive integer.", "height")
    
    MAXTIME = kwargs.get("time", math.inf)
    if matches(str(MAXTIME),
    # Xdays | Xhours | Xminutes | X[seconds] | [h:]m:s
    "^([0-9]+d|[0-9]+h|[0-9]+m|[0-9]+s?)$|^([0-9]+:)?[0-5]?[0-9]:[0-5]?[0-9]$"):
        MAXTIME = strToSeconds(MAXTIME)
    elif (MAXTIME != math.inf or MAXTIME <= 0):
        raise ValueError("Invalid value for 'time', it should be a positive integer or a correct expression.", "time")
    
    try:
        GENMAX = int(kwargs.get("gens", math.inf))
        # not sure about this expression, but it works
        if (not isinstance(GENMAX, int) and GENMAX != math.inf) or GENMAX <= 0:
            raise ValueError("Invalid value for 'gens', it should be a positive integer.")
    except OverflowError:
        GENMAX = math.inf

    FIRST_BATCH = init(WIDTH, HEIGHT)
    
    PERIOD = int(kwargs.get("period", 10))
    if not isinstance(PERIOD, int) or PERIOD <= 0:
        raise ValueError("Invalid value for 'period', it should be a positive integer.")

def displayHelp():
    text="""
usage: python3 {filename} [prob=<decimal>] [delay=<seconds>] [width=<integer>] [height=<integer>] [time=<expr>] [gens=<integer>] [period=<integer>] [-h | --help]

PARAMETERS

    prob
        Probability in percentage (do not include '%') that a cell starts alive
        default=30
    
    delay
        Seconds between each generation (can be in fractions of a second)
        default=0.5

    width, height
        Number of cells horizontally and vertically (cells are monospace characters, they occupy rectangular spaces)
        defaultWidth=75
        defaultHeight=15

    time
        Expression for the time the program will run (n is an integer):
        expression={{nd|nh|nm|n[s]}} | {{[h:]m:s}}
        default=infinite

    gens
        Number of generations where the program will stop when reached
        default=infinite
        

    period
        Number of generations it will check to find a cycling pattern
        default=10

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
    return new, cells == new

# checks if the program is in a cycle
# past -> {"cells":list, "gen":int, "count":int}
def cycleCheck(past, current, currGen):
    if past["cells"] == current and (past["gen"] + PERIOD) >= currGen:
        past["count"] += 1
    elif not (past["gen"] + PERIOD) >= currGen:
        past["cells"] = copy.deepcopy(current)
        past["gen"] = currGen
        past["count"] = 0
    return past["count"] >= 1, past["count"]

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

# stops the program displaying a message
def stop(cells, startTime, genCount, message=""):
    pass
    clear()
    display(cells, startTime, genCount)
    print(message)
    print()
    print("The initial state was this:")
    print()
    print(borderedCells(FIRST_BATCH))
    exit()

# returns true if 1st param matches regex (2n param)
def matches(chars, regex):
    match = re.search(regex, chars)
    return match != None

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
        return round(int(d)*24*3600)
    def hours(h):
        return round(int(h)*3600)
    def minutes(m):
        return round(int(m)*60)

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
    # check=true throws CPE exeption if command does not exist
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("GAME OF LIFE".center(centred))
        print()

# for now only works with enter
def pressKey(message):
    input(message)

###

main()
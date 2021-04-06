import sys
import tkinter.filedialog
import os

def clear():
    os.system('cls')


try:
    inputFile = sys.argv[1]
    outputFile = sys.argv[2]
except IndexError:
    inputFile = tkinter.filedialog.askopenfilename()
    outputFile = inputFile + '.py'

# reads until ; or { or } symbols
def readStatement(file):
    char = None
    result = ''
    comment = False
    blockComment = False
    while char not in [';', '}', '{', '']:
        char = file.read(1)
        if char == '#':
            comment = True
        if char == '/' and not blockComment:
            blockComment = True
            continue
        if (not comment) and (not blockComment):
            result += char
        if char == '\n':
            comment = False
        if char == '/' and blockComment:
            blockComment = False
    return result

# breaks text into a list of statements
allLines = []
with open(inputFile, 'r') as f:
    newStatement = 'junk'
    while len(newStatement) > 0:
        newStatement = readStatement(f).replace(' ', '').replace('\n', '').replace('\t', '')
        allLines.append(newStatement)

# control variables
linesLeft = len(allLines)
currentLine = 0

# dictionaries holding functions that will return python instructions depending on keywords
simProperties = {'width': lambda file, argument: None,
                 'height': lambda file, argument: None,
                 'camPosX': lambda file, argument: file.write('sim.cam.pos.x = ' + argument + '\n'),
                 'camPosY': lambda file, argument: file.write('sim.cam.pos.y = ' + argument + '\n'),
                 'camWidth': lambda file, argument: file.write('sim.cam.res.x = ' + argument + '\n'),
                 'camHeight': lambda file, argument: file.write('sim.cam.res.x = ' + argument + '\n'),
                 'collision': lambda file, argument: file.write('sim.collision = ' + argument + '\n'),
                 't': lambda file, argument: file.write('sim.t = ' + argument + '\n'),
                 'dt': lambda file, argument: file.write('sim.dt = ' + argument + '\n'),
                 'ops': lambda file, argument: file.write('sim.ops = ' + argument + '\n'),
                 'fps': lambda file, argument: file.write('sim.fps = ' + argument + '\n'),
                 }

bodyProperties = {'x': lambda file, argument, number: file.write(f'b{number}.coor.x = {argument}\n'),
                  'y': lambda file, argument, number: file.write(f'b{number}.coor.y = {argument}\n'),
                  'mass': lambda file, argument, number: file.write(f'b{number}.mass = {argument}\n'),
                  'charge': lambda file, argument, number: file.write(f'b{number}.charge = {argument}\n'),
                  'width': lambda file, argument, number: file.write(f'b{number}.width = {argument}\n'),
                  'name': lambda file, argument, number: file.write(f'b{number}.name = {argument}\n'),
                  'velocity': lambda file, argument, number: file.write(f'b{number}.append(cp.Velocity({argument}))\n'),
                  'acceleration': lambda file, argument, number: file.write(f'b{number}.append(cp.Acceleration({argument}))\n'),
                  'force': lambda file, argument, number: file.write(f'b{number}.append(cp.Force({argument}))\n'),
                  'priority': lambda file, argument, number: file.write(f'b{number}.priority = {argument}\n'),
                  'color': lambda file, argument, number: file.write(f'b{number}.drawProp["color"] = {argument}\n'),
                  'showBody': lambda file, argument, number: file.write(f'b{number}.drawProp["showBody"] = {argument}\n'),
                  'showVelocity': lambda file, argument, number: file.write(f'b{number}.drawProp["showVelocity"] = {argument}\n'),
                  'showAcceleration': lambda file, argument, number: file.write(f'b{number}.drawProp["showAcceleration"] = {argument}\n'),
                  'showForce': lambda file, argument, number: file.write(f'b{number}.drawProp["showForce"] = {argument}\n'),
                  'showTrail': lambda file, argument, number: file.write(f'b{number}.drawProp["showTrail"] = {argument}\n'),
                  'doMove': lambda file, argument, number: file.write(f'b{number}.drawProp["doMove"] = {argument}\n'),
                  'generateGravity': lambda file, argument, number: file.write(f'b{number}.moveProp["generateGravity"] = {argument}\n'),
                  'affectedByGravity': lambda file, argument, number: file.write(f'b{number}.moveProp["affectedByGravity"] = {argument}\n'),
                  'generateCharge': lambda file, argument, number: file.write(f'b{number}.moveProp["generateCharge"] = {argument}\n'),
                  'affectedByCharge': lambda file, argument, number: file.write(f'b{number}.moveProp["affectedByCharge"] = {argument}\n'),
                  }


def createSimulation():
    prop = {}

    global currentLine
    currentLine += 1
    while allLines[currentLine] != '}':
        temp = allLines[currentLine]
        temp = temp.replace(';', '')
        temp = temp.split('=')
        prop[temp[0]] = temp[1]
        currentLine += 1

    with open(outputFile, 'w') as f:
        f.write('import CasualPhysics2 as cp\n')
        f.write(f'sim = cp.Simulation({prop["width"]}, {prop["height"]})\n')
        for x, y in prop.items():
            try:
                simProperties[x](f, y)
            except KeyError:
                print(f'UnindetifiedProperty: {x}')
    currentLine += 1


bodyCount = 0


def createBody():
    prop = {}

    global bodyCount
    global currentLine
    currentLine += 1
    while allLines[currentLine] != '}':
        temp = allLines[currentLine]
        temp = temp.replace(';', '')
        temp = temp.split('=')
        prop[temp[0]] = temp[1]
        currentLine += 1

    with open(outputFile, 'a') as f:
        f.write('\n')
        f.write(f'b{bodyCount} = cp.Body(sim, cp.V({prop["x"]}, {prop["y"]}))\n')
        for x, y in prop.items():
            try:
                argument = y
                if y in ['blue', 'yellow', 'red', 'gray', 'pink', 'lightPink', 'green',]:
                    argument = 'cp.' + argument
                if x == 'name':
                    argument = '"' + argument + '"'
                bodyProperties[x](f, argument, bodyCount)
            except KeyError:
                print(f'UnindetifiedProperty: {x}')

    currentLine += 1
    bodyCount += 1


while allLines[currentLine] != '':
    temp = allLines[currentLine]
    if temp == 'Simulation{':
        createSimulation()
        continue
    if temp == 'Body{':
        createBody()
        continue

with open(outputFile, 'a') as f:
    f.write('\nsim.start()\n')

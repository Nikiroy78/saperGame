import json, os, random, time
from threading import Thread


response = open('response.json', 'wt', encoding='utf-8')
response.write(json.dumps({
    "error": "Unknown error"
}, indent="\t", ensure_ascii=False))
response.close()

noConfig = not('config.json' in os.listdir())

if not(noConfig):
    config = open('config.json', 'r', encoding='utf-8')
    config = config.read()
    config = json.loads(config)


class tools(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.exitUnlocked = True
        self.outputs = list()
        self.logpath = None
    
    def choose_logPath(self, logpath=None):
        self.logpath = logpath
    
    def logfilecreate(self):
        log = open(self.logpath, 'wt', encoding='utf-8')
        log.close()
    
    def echo(self, *args, sep=' ', end='\n'):
        print(*args, sep=sep, end=end)
        if type(self.logpath) is str:
            log = open(self.logpath, 'at', encoding='utf-8')
            log.write(sep.join([str(word) for word in args]) + end)
            log.close()
    
    def output(self, output_content, finaly=False):
        self.echo('[Core]: output...')
        if self.exitUnlocked:
            response = open('response.json', 'wt', encoding='utf-8')
            response.write(json.dumps(output_content, indent="\t", ensure_ascii=False))
            response.close()
            self.echo('[Core]: output finished')
            
            self.finish()
        else:
            self.echo('[Core]: output from multiMethod')
            self.outputs.append(output_content)
            if finaly:
                response = open('response.json', 'wt', encoding='utf-8')
                response.write(json.dumps({
                    'responses': self.outputs
                }, indent="\t", ensure_ascii=False))
                response.close()
                self.echo('[Core]: output finished')
            
    
    def finish(self):
        self.echo('[Core]: core was been finished')
        os.abort()
    
    def coreFailed(self, exceptionText):
        import sys
        response = open('response.json', 'wt', encoding='utf-8')
        response.write(json.dumps({
            "error": exceptionText,
            "error_randomID": random.randint(0, 99999999)
        }, indent="\t", ensure_ascii=False))
        response.close()
        self.echo(f"[Core failed]: {exceptionText}")
        os.abort()
    
    def toggleExit(self, flag=None):
        if flag is None:
            flag = not(self.exitUnlocked)
        
        if flag:
            def exitvoid():
                self.echo('[Core]: core was been finished')
                os.abort()
            
            self.finish = exitvoid
        else:
            self.finish = lambda: self.echo('[Core]: finish was been blocked.')
        
        self.exitUnlocked = flag
    
    def run(self):  # Таймер
        self.echo('[Core]: TimeOut connection Service was been started')
        time.sleep(config['max_responseTime'])
        self.coreFailed("Request Timeout. Response time exceeded")


tools = tools()
if noConfig:
    tools.coreFailed('Config file "config.json" not founded.')

if config['log_enable']:
    tools.choose_logPath(f"logs/{int(time.time())}.log")
    tools.logfilecreate()

tools.echo("[Core]: Saper game core v. 1.0 beta")

coreFailed = tools.coreFailed
tools.start()  # Запускаем службу принудительной остановки при превышении времени ответа от ядра

# while True:  # Для проверки timeout connection
    # pass


def clear_cfg():
    f = open('gamestat.json', 'wt', encoding='utf-8')
    f.write(json.dumps({"status": "output needs", "request": []}, indent="\t", ensure_ascii=False))
    f.close()


def importCfg():
    f = open('gamestat.json', 'rt', encoding='utf-8')
    fD = f.read()
    f.close()
    return json.loads(fD)


Data = importCfg()
clear_cfg()


if Data["status"] == "output needs":
    coreFailed('No output info, output status: output needs')


def checkFinGame(field):
    mapCells = list()
    noOpens = False
    for row in field:
        for cell in row:
            mapCells.append(cell)
            if 'R' in cell and not(':O' in cell) and not(noOpens):
                noOpens = True
    if not(noOpens):
        return 'noOpens!'
    return 'M:O' in mapCells


def rgReplace(field, setV, replaceTo):
    tools.echo('[rgReplace function]: started.')
    for r in range(len(field)):
        tools.echo('[rgReplace function]: row#%s' % r)
        for c in range(len(field[r])):
            tools.echo('[rgReplace function]: cell#%s' % c)
            cell = field[r][c]
            if cell == setV:
                tools.echo('[rgReplace function]: replacing...')
                field[r][c] = replaceTo
    return field


def regionGen(size, mines):
    import random
    # M - Мина
    # ...:F - Флаг
    # R(0...X) - Регионы
    # E - свободно (core)
    # ..:O - ячейка открыта игроком
    
    field = list()
    for x in range(size):
        field.append(list())
        for y in range(size):
            field[x].append('E')
    
    while mines > 0:
        for X in range(len(field)):
            for Y in range(len(field[X])):
                if mines > 0 and random.randint(0, 100) >= random.randint(68, 90):
                    field[X][Y] = 'M'
                    mines -= 1
    
    emptyField = True
    filedNum = 0
    while emptyField:
        rgCreated = False
        for Y in range(len(field)):
            for X in range(len(field[Y])):
                if field[Y][X] == 'E':
                    tools.echo(f"[Generate map] create region#{filedNum}")
                    field[Y][X] = f"R{filedNum}"
                    rgCoords = {"X": X, "Y": Y}
                    rgCreated = True
                    break
            if rgCreated:
                break
        if rgCreated:
            # rgSize = random.randint(1, ((size ** 2) - mines) // 6)
            rgSize = 1  # (!) Ради эксперимента поставим 1
            for _ in range(rgSize):
                stop = False
                while True:
                    upMove = rgCoords["Y"] != 0
                    if upMove:
                        upMove &= field[rgCoords["Y"] - 1][rgCoords["X"]] != 'M'
                    downMove = rgCoords["Y"] != size - 1
                    if downMove:
                        downMove &= field[rgCoords["Y"] + 1][rgCoords["X"]] != 'M'
                    leftMove = rgCoords["X"] != 0
                    if leftMove:
                        leftMove &= field[rgCoords["Y"]][rgCoords["X"] - 1] != 'M'
                    rightMove = rgCoords["X"] != size - 1
                    if rightMove:
                        rightMove &= field[rgCoords["Y"]][rgCoords["X"] + 1] != 'M'
                    if not(upMove and downMove and leftMove or rightMove):
                        stop = True
                        break
                    
                    moveID = random.randint(0, 3)
                    if upMove and moveID == 0:
                        rgCoords["Y"] -= 1
                        tools.echo(f"[Generate map]: upMove creating in {rgCoords}")
                        field[rgCoords["Y"]][rgCoords["X"]] = f"R{filedNum}"
                        break
                    elif downMove and moveID == 1:
                        rgCoords["Y"] += 1
                        tools.echo(f"[Generate map]: downMove creating in {rgCoords}")
                        field[rgCoords["Y"]][rgCoords["X"]] = f"R{filedNum}"
                        break
                    elif leftMove and moveID == 2:
                        rgCoords["X"] -= 1
                        tools.echo(f"[Generate map]: leftMove creating in {rgCoords}")
                        field[rgCoords["Y"]][rgCoords["X"]] = f"R{filedNum}"
                        break
                    elif rightMove and moveID == 3:
                        rgCoords["X"] += 1
                        tools.echo(f"[Generate map]: rightMove creating in {rgCoords}")
                        field[rgCoords["Y"]][rgCoords["X"]] = f"R{filedNum}"
                        break
                
                if stop:
                    break
        
        emptyField = False
        for row in field:
            for cell in row:
                if cell == 'E':
                    emptyField = True
                    filedNum += 1
                    break
    # Объединение регионов
    
    tools.echo('[Generate map]: combine the regions')
    for rowID in range(len(field)):
        tools.echo('[Generate map]: cursore in rowID %s' % rowID)
        for cellID in range(len(field[rowID])):
            tools.echo('[Generate map]: cursore in cellID %s' % cellID)
            cell = field[rowID][cellID]
            if 'R' in cell:
                tools.echo('[Generate map]: combine region %s' % cell)
                sawUp = rowID != 0
                sawDown = rowID != len(field) - 1
                sawLeft = cellID != 0
                sawRight = cellID != len(field) - 1
                if sawUp:
                    genAllow = True
                    if genAllow and (sawUp and sawLeft):
                        genAllow = field[rowID - 1][cellID - 1] != 'M'
                    if genAllow and (sawUp and sawRight):
                        genAllow = field[rowID - 1][cellID + 1] != 'M'
                    if genAllow and (sawDown and sawLeft):
                        genAllow = field[rowID + 1][cellID - 1] != 'M'
                    if genAllow and (sawDown and sawRight):
                        genAllow = field[rowID + 1][cellID + 1] != 'M'
                    
                    if genAllow and cell != field[rowID - 1][cellID] and 'R' in field[rowID - 1][cellID]:
                        if int(cell.split('R')[-1]) > int(field[rowID - 1][cellID].split('R')[-1]):
                            field = rgReplace(field, cell, field[rowID - 1][cellID])
                            rgMax = field[rowID - 1][cellID]
                            tools.echo('[Generate map]: combine the region to %s' % field[rowID - 1][cellID])
                        else:
                            field = rgReplace(field, field[rowID - 1][cellID], cell)
                            rgMax = cell
                            tools.echo('[Generate map]: combine the region to %s' % cell)
                if sawDown:
                    genAllow = True
                    if genAllow and (sawUp and sawLeft):
                        genAllow = field[rowID - 1][cellID - 1] != 'M'
                    if genAllow and (sawUp and sawRight):
                        genAllow = field[rowID - 1][cellID + 1] != 'M'
                    if genAllow and (sawDown and sawLeft):
                        genAllow = field[rowID + 1][cellID - 1] != 'M'
                    if genAllow and (sawDown and sawRight):
                        genAllow = field[rowID + 1][cellID + 1] != 'M'
                    
                    if genAllow and cell != field[rowID + 1][cellID] and 'R' in field[rowID + 1][cellID]:
                        if int(cell.split('R')[-1]) > int(field[rowID + 1][cellID].split('R')[-1]):
                            field = rgReplace(field, cell, field[rowID + 1][cellID])
                            rgMax = field[rowID + 1][cellID]
                            tools.echo('[Generate map]: combine the region to %s' % field[rowID + 1][cellID])
                        else:
                            field = rgReplace(field, field[rowID + 1][cellID], cell)
                            rgMax = cell
                            tools.echo('[Generate map]: combine the region to %s' % cell)
                if sawLeft:
                    genAllow = True
                    if genAllow and (sawUp and sawLeft):
                        genAllow = field[rowID - 1][cellID - 1] != 'M'
                    if genAllow and (sawUp and sawRight):
                        genAllow = field[rowID - 1][cellID + 1] != 'M'
                    if genAllow and (sawDown and sawLeft):
                        genAllow = field[rowID + 1][cellID - 1] != 'M'
                    if genAllow and (sawDown and sawRight):
                        genAllow = field[rowID + 1][cellID + 1] != 'M'
                    
                    if genAllow and cell != field[rowID][cellID - 1] and 'R' in field[rowID][cellID - 1]:
                        if int(cell.split('R')[-1]) > int(field[rowID][cellID - 1].split('R')[-1]):
                            field = rgReplace(field, cell, field[rowID][cellID - 1])
                            rgMax = field[rowID][cellID - 1]
                            tools.echo('[Generate map]: combine the region to %s' % field[rowID][cellID - 1])
                        else:
                            field = rgReplace(field, field[rowID][cellID - 1], cell)
                            rgMax = cell
                            tools.echo('[Generate map]: combine the region to %s' % cell)
                if sawRight:
                    genAllow = True
                    if genAllow and (sawUp and sawLeft):
                        genAllow = field[rowID - 1][cellID - 1] != 'M'
                    if genAllow and (sawUp and sawRight):
                        genAllow = field[rowID - 1][cellID + 1] != 'M'
                    if genAllow and (sawDown and sawLeft):
                        genAllow = field[rowID + 1][cellID - 1] != 'M'
                    if genAllow and (sawDown and sawRight):
                        genAllow = field[rowID + 1][cellID + 1] != 'M'
                    
                    if genAllow and cell != field[rowID][cellID + 1] and 'R' in field[rowID][cellID + 1]:
                        if int(cell.split('R')[-1]) > int(field[rowID][cellID + 1].split('R')[-1]):
                            field = rgReplace(field, cell, field[rowID][cellID + 1])
                            rgMax = field[rowID][cellID + 1]
                            tools.echo('[Generate map]: combine the region to %s' % field[rowID][cellID + 1])
                        else:
                            field = rgReplace(field, field[rowID][cellID + 1], cell)
                            rgMax = cell
                            tools.echo('[Generate map]: combine the region to %s' % cell)
    
    ret_values = {"field": field, "regionMax_index": filedNum}
    
    return ret_values


def randtk(lentk=16):
    from random import randint as rand
    token = ''
    for _ in range(lentk):
        token += '0123456789abcdef'[rand(0, 15)]
    
    return token


def int_check(string):
    for num in str(string):
        if num not in '0123456789':
            coreFailed("Int value failed.")
    return int(string)


methods = list()
multiMethod_connected = Data["status"] == 'multiMethod' and 'requests' in Data

if multiMethod_connected:
    methods = Data["requests"]
    outputs = list()
    tools.echo('[Core]: multiMethod: on')
else:
    methods = [Data]

for DataID in range(len(methods)):
    Data = methods[DataID]
    enlessloop = DataID == len(methods) - 1
    tools.toggleExit(enlessloop)
    if multiMethod_connected:
        tools.echo(f"[Core]: method init: {Data['status']}")
    
    if Data["status"] == 'newGame':
        if "Mines" in Data["request"]:
            mines = Data["request"]["Mines"]
        else:
            coreFailed('missing param "Mines"')
        if "size" in Data["request"]:
            fieldsize = Data["request"]["size"]
        else:
            coreFailed('missing param "size"')
        if "ID" in Data["request"]:
            useridaccess = Data["request"]["ID"]
        else:
            coreFailed('missing param "ID"')
        gamesession = randtk()
        Map = regionGen(fieldsize, mines)
        while gamesession in os.listdir('generatedGameSessions'):
            gamesession = randtk()
        os.mkdir(f"generatedGameSessions/{gamesession}")
        gameinfoF = open(f"generatedGameSessions/{gamesession}/config.json", 'wt', encoding='utf-8')
        gameinfoF.write(json.dumps({
            "fieldSize": fieldsize,
            "mines": mines,
            "map": Map["field"],
            "regionMax_index": Map["regionMax_index"],
            "continue": True
        }, indent="\t", ensure_ascii=False))
        gameinfoF.close()
        
        if not(multiMethod_connected):
            response = open('response.json', 'wt', encoding='utf-8')
            response.write(json.dumps({
                "response": {
                    "gamesession": gamesession,
                    "map": Map['field'],
                    "regionMax_index": Map['regionMax_index']
                },
                "response_randomID": random.randint(0, 99999999)
            }, indent="\t", ensure_ascii=False))
            response.close()
        else:
            outputs.append({
                "response": {
                    "gamesession": gamesession,
                    "map": Map['field'],
                    "regionMax_index": Map['regionMax_index']
                },
                "response_randomID": random.randint(0, 99999999)
            })
        if not(multiMethod_connected):
            tools.finish()
    elif Data["status"] == 'toggleFlag':
        if "gamesession" in Data["request"]:
            gamesession = Data["request"]["gamesession"]
            if gamesession not in os.listdir('generatedGameSessions'):
                coreFailed("Invalid Game session")
        else:
            coreFailed('missing param "gamesession"')
        if "X" in Data["request"]:
            coordX = int_check(Data["request"]["X"])
        else:
            coreFailed('missing param "X"')
        if "Y" in Data["request"]:
            coordY = int_check(Data["request"]["Y"])
        else:
            coreFailed('missing param "Y"')
        
        F = open(f"generatedGameSessions/{gamesession}/config.json", 'r', encoding='utf-8')
        gameSessionData = json.loads(F.read())
        F.close()
        del F
        if not(gameSessionData["continue"]):
            coreFailed('This game was been finished')
        
        if coordX >= int(gameSessionData["fieldSize"]) or coordX < 0:
            coreFailed('CursorX outed to field')
        elif coordY >= int(gameSessionData["fieldSize"]) or coordY < 0:
            coreFailed('CursorY outed to field')
        
        flag = gameSessionData["map"][coordY][coordX]
        if ':F' in flag:
            gameSessionData["map"][coordY][coordX] = flag[:-2]
        elif ':O' in flag:
            coreFailed('You can\'t flag this cell. Cell was been opened.')
        else:
            gameSessionData["map"][coordY][coordX] = f"{flag}:F"
        
        writef = open(f"generatedGameSessions/{gamesession}/config.json", 'wt', encoding='utf-8')
        writef.write(json.dumps(gameSessionData, indent="\t", ensure_ascii=False))
        writef.close()
        
        if not(multiMethod_connected):
            response = open('response.json', 'wt', encoding='utf-8')
            response.write(json.dumps({
                "response": 1,
                "response_randomID": random.randint(0, 99999999)
            }, indent="\t", ensure_ascii=False))
            response.close()
        else:
            outputs.append({
                "response": 1,
                "response_randomID": random.randint(0, 99999999)
            })
        if not(multiMethod_connected):
            tools.finish()
    elif Data["status"] == 'getGameSession':
        if "gamesession" in Data["request"]:
            gamesession = Data["request"]["gamesession"]
            if gamesession not in os.listdir('generatedGameSessions'):
                coreFailed("Invalid Game session")
        else:
            coreFailed('missing param "gamesession"')
        
        with open(f"generatedGameSessions/{gamesession}/config.json") as gameData:
            gameData = json.loads(gameData.read())
        
        if not(multiMethod_connected):
            response = open('response.json', 'wt', encoding='utf-8')
            response.write(json.dumps({
                "response": {
                    "gamesession": gamesession,
                    "continue": gameData['continue'],
                    "map": gameData['map'],
                    "regionMax_index": gameData['regionMax_index']
                },
                "response_randomID": random.randint(0, 99999999)
            }, indent="\t", ensure_ascii=False))
            response.close()
        else:
            outputs.append({
                "response": {
                    "gamesession": gamesession,
                    "continue": gameData['continue'],
                    "map": gameData['map'],
                    "regionMax_index": gameData['regionMax_index']
                },
                "response_randomID": random.randint(0, 99999999)
            })
        
        if not(multiMethod_connected):
            tools.finish()
    elif Data["status"] == 'openItem':
        if "gamesession" in Data["request"]:
            gamesession = Data["request"]["gamesession"]
            if gamesession not in os.listdir('generatedGameSessions'):
                coreFailed("Invalid Game session")
        else:
            coreFailed('missing param "gamesession"')
        if "X" in Data["request"]:
            coordX = int_check(Data["request"]["X"])
        else:
            coreFailed('missing param "X"')
        if "Y" in Data["request"]:
            coordY = int_check(Data["request"]["Y"])
        else:
            coreFailed('missing param "Y"')
        F = open(f"generatedGameSessions/{gamesession}/config.json", 'r', encoding='utf-8')
        gameSessionData = json.loads(F.read())
        F.close()
        del F
        if not(gameSessionData["continue"]):
            coreFailed('This game was been finished')
        
        if coordX >= int(gameSessionData["fieldSize"]) or coordX < 0:
            coreFailed('CursorX outed to field')
        elif coordY >= int(gameSessionData["fieldSize"]) or coordY < 0:
            coreFailed('CursorY outed to field')
        
        flag = gameSessionData["map"][coordY][coordX]
        if ':O' in flag:
            coreFailed('This cell was been opened')
        elif ':F' in flag:
            coreFailed('This cell was been flagged. Action was been blocked.')
        else:
            if flag == 'M':
                gameSessionData["continue"] = False
            for X in range(len(gameSessionData["map"])):
                for Y in range(len(gameSessionData["map"][X])):
                    if gameSessionData["map"][X][Y] == flag:
                        gameSessionData["map"][X][Y] = f"{flag}:O"
        
        gameSessionData["continue"] = checkFinGame(gameSessionData["map"])
        if str(gameSessionData["continue"]) == 'noOpens!':
            gameSessionData["continue"] = True
            gameSessionData["map"] = rgReplace(
                gameSessionData["map"], 
                'M', 
                'M:F'
            )
        gameSessionData["continue"] = not(gameSessionData["continue"])
        writef = open(f"generatedGameSessions/{gamesession}/config.json", 'wt', encoding='utf-8')
        writef.write(json.dumps(gameSessionData, indent="\t", ensure_ascii=False))
        writef.close()
        
        if not(multiMethod_connected):
            response = open('response.json', 'wt', encoding='utf-8')
            response.write(json.dumps({
                "response": 1,
                "response_randomID": random.randint(0, 99999999)
            }, indent="\t", ensure_ascii=False))
            response.close()
        else:
            outputs.append({
                "response": 1,
                "response_randomID": random.randint(0, 99999999)
            })
        if not(multiMethod_connected):
            tools.finish()
    elif Data['status'] != 'multiMethod':
        coreFailed(f"Unknown method \"{Data['status']}\"")
    if multiMethod_connected and enlessloop:
        response = open('response.json', 'wt', encoding='utf-8')
        response.write(json.dumps({
            "responses": outputs,
            "response_randomID": random.randint(0, 99999999)
        }, indent="\t", ensure_ascii=False))
        response.close()
        tools.finish()
if multiMethod_connected:
    response = open('response.json', 'wt', encoding='utf-8')
    response.write(json.dumps({
        "responses": [],
        "response_randomID": random.randint(0, 99999999)
    }, indent="\t", ensure_ascii=False))
    response.close()
    tools.finish()
coreFailed('Crash the kernel.')
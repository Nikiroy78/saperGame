from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.Qt import *
import SQLEasy, json, os, random, corelib
import launcher  # Интерфейс


def game(gameStyle, databaseObj, gamerID, gamehash, muzicOn=True, MINES=random.randint(25, 55)):
    MINES_COMPR = False
    import pygame
    
    corelib.tool.showGUI_wait()
    
    databaseObj.setItem('lastGame', gameStyle, 'ID', gamerID, DatabaseName='users')
    # Импорт конфига
    with open(f"source/{gameStyle}/about.json", 'r', encoding='utf-8') as gameconfig:
        gameconfig = json.loads(gameconfig.read())
    # Функции


    def checkEnd(field):
        endgame = True
        for r in field:
            for c in r:
                if c in ('M:O', 'M', 'M:F'):
                    return True
                if 'R' in c and ':O' not in c:
                    endgame = False 
        return endgame


    def checkWin(field, endgamecheck=False):
        fieldCheck = list()
        endgame = True
        for r in field:
            for c in r:
                fieldCheck.append(c)
                if 'R' in c and ':O' not in c:
                    endgame = False
        if endgamecheck:
            return 'M:O' not in fieldCheck and endgame
        else:
            return 'M:O' not in fieldCheck


    def compareFields(old_field, field):
        if checkWin(field, True):
            return
        
        class emptySound:
            def play(self):
                pass
        
        sounds = [
            emptySound(),
            pygame.mixer.Sound(f"source/{gameStyle}/openCell.wav"),
            pygame.mixer.Sound(f"source/{gameStyle}/flag.wav")
        ]
        
        actID = 0
        
        comlete = False
        
        for rowID in range(len(field)):
            for cellID in range(len(field[rowID])):
                if field[rowID][cellID] != old_field[rowID][cellID]:
                    if ':F' in field[rowID][cellID]:
                        actID = 2
                        comlete = True
                        break
                    elif ':O' in field[rowID][cellID] and field[rowID][cellID] != 'M:O':
                        actID = 1
                        comlete = True
                        break
            if comlete:
                break
        
        sounds[actID].play()
    # Классы игровых объектов


    class controlBanner(pygame.sprite.Sprite):
        def __init__(self, X, Y, platform='XBox', info_contentID=0):
            infocontent = ['openCell', 'flagCell', 'restart']
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.Surface((228, 77))
            self.platform = platform
            self.info_contentID = info_contentID
            self.image = pygame.image.load(f"source/{gameStyle}/{platform}_{infocontent[info_contentID]}.png")
            self.rect = self.image.get_rect()
            self.rect.x = X
            self.rect.y = Y
        
        def changePlatform(self, platform):
            infocontent = ['openCell', 'flagCell', 'restart']
            self.platform = platform
            self.image = pygame.image.load(f"source/{gameStyle}/{platform}_{infocontent[self.info_contentID]}.png")


    class Border(pygame.sprite.Sprite):
        def __init__(self, X, Y, borderType='Left'):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.Surface((228, 77))
            self.animationFrameTime = 0
            self.borderType = borderType
            self.image = pygame.image.load(f"source/{gameStyle}/score_end{borderType}(0).png")
            self.rect = self.image.get_rect()
            self.rect.x = X
            self.rect.y = Y
        
        def update(self):
            self.animationFrameTime += 1
            if self.animationFrameTime >= 45:
                self.animationFrameTime = 0
            self.image = pygame.image.load(f"source/{gameStyle}/score_end{self.borderType}({self.animationFrameTime // 15}).png")


    class resetButton(pygame.sprite.Sprite):
        def __init__(self, X, Y):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.Surface((228, 77))
            self.hide = 'noHover'
            self.endStatus = ''
            self.image = pygame.image.load(f"source/{gameStyle}/resetButton_{self.endStatus}_{self.hide}.png")
            self.rect = self.image.get_rect()
            self.x = X
            self.y = Y
            
            self.rect.x = X
            self.rect.y = Y
        
        def editCond(self, hide=None, endStatus=None):
            if not(hide is None):
                self.hide = hide
            if not(endStatus is None):
                self.endStatus = endStatus
            
            self.image = pygame.image.load(f"source/{gameStyle}/resetButton_{self.endStatus}_{self.hide}.png")
        
        def check_myself_Location(self, X, Y):
            if X >= self.x and X <= self.x + 32 and Y >= self.y and Y <= self.y + 32:
                return self


    class timerCell(pygame.sprite.Sprite):
        def __init__(self, X, Y, value='off'):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.Surface((228, 77))
            self.value = value
            self.image = pygame.image.load(f"source/{gameStyle}/score_{value}.png")
            self.rect = self.image.get_rect()
            self.rect.x = X
            self.rect.y = Y
        
        def editValue(self, value='off'):
            self.value = value
            self.image = pygame.image.load(f"source/{gameStyle}/score_{self.value}.png")
        
        def update(self):
            self.image = pygame.image.load(f"source/{gameStyle}/score_{self.value}.png")


    class tablet(pygame.sprite.Sprite):
        def __init__(self, X, Y):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.Surface((228, 77))
            self.image = pygame.image.load(f"source/{gameStyle}/Tablet.png")
            self.rect = self.image.get_rect()
            self.rect.x = X
            self.rect.y = Y


    class fieldCursor(pygame.sprite.Sprite):
        def __init__(self, X, Y):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.Surface((32, 32))
            self.image = pygame.image.load(f"source/{gameStyle}/Cursor.png")
            self.cellPos = (X, Y)
            self.rect = self.image.get_rect()
            self.rect.x = 93 + X * 31
            self.rect.y = 133 + Y * 31
        
        def setCell_coord(self, X, Y):
            self.rect.x = 93 + X * 31
            self.rect.y = 133 + Y * 31
            self.cellPos = (X, Y)


    class cell(pygame.sprite.Sprite):
        def __init__(self, X, Y, coords, condition='CLOSED'):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.Surface((32, 32))
            self.image = pygame.image.load(f"source/{gameStyle}/closed_cell.png")
            self.rect = self.image.get_rect()
            self.rect.x = X
            self.rect.y = Y
            self.cellPosition = {
                "X": coords[0],
                "Y": coords[1]
            }
            
            self.condition = condition
            self.animationFrameS = 0
        
        def getCondition(self):
            return self.condition
        
        def update(self):
            if self.condition == 'CLOSED':
                self.image.blit(pygame.image.load(f"source/{gameStyle}/closed_cell.png"), (0, 0))
            elif 'num_' in self.condition:
                number = int(self.condition.split('_')[-1])
                self.animationFrameS += 1
                if self.animationFrameS >= 40:
                    self.animationFrameS = 0
                self.image.blit(pygame.image.load(f"source/{gameStyle}/mines_{number}({self.animationFrameS // 20}).png"), (0, 0))
            elif self.condition == 'OPENED':
                self.animationFrameS += 1
                if self.animationFrameS >= 40:
                    self.animationFrameS = 0
                self.image.blit(pygame.image.load(f"source/{gameStyle}/open_cell_{self.animationFrameS // 20}.png"), (0, 0))
            elif self.condition == 'FLAG':
                self.animationFrameS += 1
                if self.animationFrameS >= 40:
                    self.animationFrameS = 0
                self.image.blit(pygame.image.load(f"source/{gameStyle}/flag_{self.animationFrameS // 20}.png"), (0, 0))
            elif self.condition == 'BOMB':
                self.animationFrameS += 1
                if self.animationFrameS >= 40:
                    self.animationFrameS = 0
                self.image.blit(pygame.image.load(f"source/{gameStyle}/mine_bombed({self.animationFrameS // 20}).png"), (0, 0))
            elif self.condition == 'DEFUSE':
                self.animationFrameS += 1
                if self.animationFrameS >= 40:
                    self.animationFrameS = 0
                self.image.blit(pygame.image.load(f"source/{gameStyle}/mine_finded({self.animationFrameS // 20}).png"), (0, 0))
        
        def setCondition(self, value):
            self.condition = value


    class sceneGame(pygame.sprite.Group):
        def __init__(self, platform):
            pygame.sprite.Group.__init__(self)
            # Sounds
            self.bombSound = pygame.mixer.Sound(f"source/{gameStyle}/bomb.wav")
            self.winSound = pygame.mixer.Sound(f"source/{gameStyle}/win.wav")
            
            self.soundNotPlayed = True
            
            self.PLATFORM = platform
            self.cells = list()
            for row in range(10):
                self.cells.append(list())
                for _cell in range(10):
                    addCell = cell(93 + _cell * 31, 133 + row * 31, (_cell, row))
                    self.add(addCell)
                    self.cells[-1].append({
                        "cellObject": addCell,
                        "coord_start": [93 + _cell * 31, 133 + row * 31],
                        "coord_last": [93 + (_cell + 1) * 31, 133 + (row + 1) * 31],
                        "coords_in_field": (_cell, row)
                    })
            self.add(tablet(130, 14))
            self.positionCursor = (0, 0)
            self.cursor = fieldCursor(*self.positionCursor)
            self.add(self.cursor)
            self.add(Border(166, 93))
            self.timeCells = list()
            for i in range(3):
                timerCellObj = timerCell(198 + i * 32, 93)
                self.add(timerCellObj)
                self.timeCells.append(timerCellObj)
            self.add(Border(294, 93, 'Right'))
            self.resetButton = resetButton(228, 448)
            self.add(self.resetButton)
            
            self.InfoTables = list()
            
            for i in range(3):
                control_banner = controlBanner(0, 404 + i * 32, platform, i)
                self.add(control_banner)
                self.InfoTables.append(control_banner)
        
        def changePlatform(self, PLATFORM):
            self.PLATFORM = PLATFORM
            for tableObj in self.InfoTables:
                tableObj.changePlatform(PLATFORM)
        
        def setScoreBoard_value(self, value=None):
            if not(value is None):
                value = str(value)
                if len(value) == 1:
                    value = '00' + value
                elif len(value) == 2:
                    value = '0' + value
                
                for numID in range(len(value)):
                    self.timeCells[numID].editValue(int(value[numID]))
            else:
                for cellT in self.timeCells:
                    cellT.editValue()
        
        def getCell_intoCoords(self, x, y):
            for row in self.cells:
                for _cell in row:
                    if (x >= _cell["coord_start"][0] and x <= _cell["coord_last"][0]) and (y >= _cell["coord_start"][1] and y <= _cell["coord_last"][1]):
                        return _cell["cellObject"]
        
        def cursorMove(self, x, y):
            self.positionCursor = (x, y)
            self.cursor.setCell_coord(x, y)
        
        def get_cursorPos(self):
            return list(self.positionCursor)
        
        def updateField(self, field, gamefinished=None):
            global MINES_COMPR
            
            listcells = list()
            for r in field:
                for c in r:
                    listcells.append(c)
            if gamefinished is None:
                gamefinished = 'M:O' in listcells
            
            for rowId in range(len(field)):
                row = field[rowId]
                for cellID in range(len(field[rowId])):
                    _cell = field[rowId][cellID]
                    
                    actCell = self.cells[rowId][cellID]["cellObject"]
                    if ':O' in _cell:
                        if not(gamefinished):
                            gamefinished = _cell == 'M:O'
                        
                        if _cell == 'M:O':
                            actCell.setCondition('BOMB')
                        else:
                            SeeUp = rowId != 0
                            SeeDown = rowId != len(field) - 1
                            SeeLeft = cellID != 0
                            SeeRight = cellID != len(field) - 1
                            
                            mines = 0
                            frontire = False
                            if SeeUp:
                                if field[rowId - 1][cellID] in ('M', 'M:F', 'M:O'):
                                    mines += 1
                                if not(frontire):
                                    frontire = _cell != field[rowId - 1][cellID] and ':O' not in field[rowId - 1][cellID]
                            if SeeDown:
                                if field[rowId + 1][cellID] in ('M', 'M:F', 'M:O'):
                                    mines += 1
                                if not(frontire):
                                    frontire = _cell != field[rowId + 1][cellID] and ':O' not in field[rowId + 1][cellID]
                            if SeeLeft:
                                if field[rowId][cellID - 1] in ('M', 'M:F', 'M:O'):
                                    mines += 1
                                if not(frontire):
                                    frontire = _cell != field[rowId][cellID - 1] and ':O' not in field[rowId][cellID - 1]
                            if SeeRight:
                                if field[rowId][cellID + 1] in ('M', 'M:F', 'M:O'):
                                    mines += 1
                                if not(frontire):
                                    frontire = _cell != field[rowId][cellID + 1] and ':O' not in field[rowId][cellID + 1]
                            # Диагонали
                            if SeeUp and SeeLeft:
                                if field[rowId - 1][cellID - 1] in ('M', 'M:F', 'M:O'):
                                    mines += 1
                            if SeeUp and SeeRight:
                                if field[rowId - 1][cellID + 1] in ('M', 'M:F', 'M:O'):
                                    mines += 1
                            if SeeDown and SeeLeft:
                                if field[rowId + 1][cellID - 1] in ('M', 'M:F', 'M:O'):
                                    mines += 1
                            if SeeDown and SeeRight:
                                if field[rowId + 1][cellID + 1] in ('M', 'M:F', 'M:O'):
                                    mines += 1
                            
                            if mines > 0:
                                actCell.setCondition('num_%s' % mines)
                            elif frontire:
                                actCell.setCondition('num_1')
                            else:
                                actCell.setCondition('OPENED')
                    elif ':F' in _cell:
                        if gamefinished and _cell == 'M:F':
                            actCell.setCondition('DEFUSE')
                        else:
                            actCell.setCondition('FLAG')
                    else:
                        actCell.setCondition('CLOSED')
            if not(gamefinished):
                self.resetButton.editCond(endStatus='')
            elif checkWin(field):
                MINES_COMPR = True
                self.resetButton.editCond(endStatus='win')
                self.winSound.play()
                minesDefused = 0
                scores = 0
                
                for row in field:
                    for _cell in row:
                        if _cell == 'M:F':
                            minesDefused += 1
                
                for row in field:
                    for _cell in row:
                        if _cell == 'M:F':
                            if (minesDefused // 5) ** 2 > 15:
                                scores += (minesDefused // 5) ** 2 > 10
                            else:
                                scores += 15
                
                databaseObj.setItem(
                    'minesDefuse', 
                    SQLEasy.compareKey(databaseObj.getBase('users'), 'ID')[gamerID]['minesDefuse'] + minesDefused, 
                    'ID', 
                    gamerID, 
                    DatabaseName='users'
                )
                
                databaseObj.setItem(
                    'points', 
                    SQLEasy.compareKey(databaseObj.getBase('users'), 'ID')[gamerID]['points'] + scores, 
                    'ID', 
                    gamerID, 
                    DatabaseName='users'
                )
            else:
                MINES_COMPR = True
                self.resetButton.editCond(endStatus='lose')
                self.bombSound.play()
                
                minesDefused = 0
                scores = 0
                
                for row in field:
                    for _cell in row:
                        if _cell == 'M:F':
                            minesDefused += 1
                            scores += 10
                
                databaseObj.setItem(
                    'minesDefuse', 
                    SQLEasy.compareKey(databaseObj.getBase('users'), 'ID')[gamerID]['minesDefuse'] + minesDefused, 
                    'ID', 
                    gamerID, 
                    DatabaseName='users'
                )
                
                databaseObj.setItem(
                    'points', 
                    SQLEasy.compareKey(databaseObj.getBase('users'), 'ID')[gamerID]['points'] + scores, 
                    'ID', 
                    gamerID, 
                    DatabaseName='users'
                )


    # код игры
    logicGame = corelib.getGameSession(gamehash)['response']
    gamesession = logicGame["gamesession"]
    field = logicGame["map"]
    
    if gamesession not in SQLEasy.compareKey(databaseObj.getBase('gamehashes'), 'hash'):
        databaseObj.add({
            "hash": gamesession,
            "userID": gamerID,
            "mines": MINES,
            "game": gameStyle,
            "fieldJSON": json.dumps(field, indent="\t", ensure_ascii=False)
        }, 'gamehashes')

    pygame.init()

    screen = pygame.display.set_mode((500, 500))

    pygame.display.set_caption(gameconfig['title'])
    pygame.display.set_icon(pygame.image.load(f"source/{gameStyle}/gameico.png"))
    bg = pygame.image.load(f"source/{gameStyle}/bg.png")
    screen.blit(bg, (0, 0))

    PLATFORM = 'XBox'  # (!) Сделать проверку
    # Прорисовка полей
    sceneGame = sceneGame(PLATFORM)

    pygame.display.flip()

    program_running = True

    cursor_moveUp = False
    cursor_moveDown = False
    cursor_moveLeft = False
    cursor_moveRight = False

    #  Muzic
    pygame.mixer.music.load(f"source/{gameStyle}/muzic.wav")
    if muzicOn:
        pygame.mixer.music.play()
    pygame.mixer.Sound(f"source/{gameStyle}/resetField.wav").play()
    databaseObj.setItem(
        'games', 
        SQLEasy.compareKey(databaseObj.getBase('users'), 'ID')[gamerID]['games'] + 1, 
        'ID', 
        gamerID, 
        DatabaseName='users'
    )
    
    sceneGame.updateField(field)
    
    while program_running:
        pygame.time.Clock().tick(60)  # max FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                program_running = False
                break
            elif event.type == pygame.MOUSEMOTION:
                POSITION = event.pos
                cellSel = sceneGame.getCell_intoCoords(int(POSITION[0]), int(POSITION[1]))
                
                resetButtonSel = sceneGame.resetButton.check_myself_Location(int(POSITION[0]), int(POSITION[1]))
                if not(cellSel is None):
                    sceneGame.cursorMove(cellSel.cellPosition["X"], cellSel.cellPosition["Y"])
                    del POSITION, cellSel
                if not(resetButtonSel is None):
                    resetButtonSel.editCond(hide='hover')
                else:
                    sceneGame.resetButton.editCond(hide='noHover')
            elif event.type == pygame.KEYDOWN:
                cursor_moveUp = event.key == 1073741906
                cursor_moveDown = event.key == 1073741905
                cursor_moveLeft = event.key == 1073741904
                cursor_moveRight = event.key == 1073741903
                
                cursor_coords = sceneGame.get_cursorPos()
                if cursor_moveUp:
                    cursor_coords[1] -= 1
                if cursor_moveDown:
                    cursor_coords[1] += 1
                if cursor_moveLeft:
                    cursor_coords[0] -= 1
                if cursor_moveRight:
                    cursor_coords[0] += 1
                
                if cursor_coords[0] <= -1:
                    cursor_coords[0] = 9
                if cursor_coords[0] >= 10:
                    cursor_coords[0] = 0
                if cursor_coords[1] <= -1:
                    cursor_coords[1] = 9
                if cursor_coords[1] >= 10:
                    cursor_coords[1] = 0
                
                sceneGame.cursorMove(*cursor_coords)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                POSITION = event.pos
                cellSel = sceneGame.getCell_intoCoords(int(POSITION[0]), int(POSITION[1]))
                
                resetButtonSel = sceneGame.resetButton.check_myself_Location(int(POSITION[0]), int(POSITION[1]))
                if not(cellSel is None):
                    corelib.openItem(gamesession, X=cellSel.cellPosition["X"], Y=cellSel.cellPosition["Y"])
                    respObj = corelib.getGameSession(gamesession)['response']
                    old_field = field
                    field = respObj['map']
                    compareFields(old_field, field)
                    sceneGame.updateField(field, gamefinished=not(respObj['continue']))
                    del POSITION, cellSel
                if not(resetButtonSel is None):
                    pygame.mixer.Sound(f"source/{gameStyle}/resetField.wav").play()
                    MINES = random.randint(25, 55)
                    logicGame = corelib.newGame(gamerID, mines=MINES)['response']
                    gamesession = logicGame["gamesession"]
                    sceneGame.updateField(logicGame["map"])
                    if muzicOn:
                        pygame.mixer.music.play()
                    MINES_COMPR = False
                    
                    databaseObj.setItem(
                        'games', 
                        SQLEasy.compareKey(databaseObj.getBase('users'), 'ID')[gamerID]['games'] + 1, 
                        'ID', 
                        gamerID, 
                    DatabaseName='users')
                    
                    databaseObj.add({
                        "hash": gamesession,
                        "userID": gamerID,
                        "game": gameStyle,
                        "mines": MINES,
                        "fieldJSON": json.dumps(field, indent="\t", ensure_ascii=False)
                    }, 'gamehashes')
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                POSITION = event.pos
                cellSel = sceneGame.getCell_intoCoords(int(POSITION[0]), int(POSITION[1]))
                if not(cellSel is None):
                    if MINES > 0 and cellSel.getCondition() == 'CLOSED' and not(MINES_COMPR):
                        if 'response' in corelib.toggleFlag(gamesession, X=cellSel.cellPosition["X"], Y=cellSel.cellPosition["Y"]):
                            MINES -= 1
                        respObj = corelib.getGameSession(gamesession)['response']
                        old_field = field
                        field = respObj['map']
                        compareFields(old_field, field)
                        sceneGame.updateField(field, gamefinished=not(respObj['continue']))
                        del POSITION, cellSel
                    elif cellSel.getCondition() == 'FLAG' and not(MINES_COMPR):
                        if 'response' in corelib.toggleFlag(gamesession, X=cellSel.cellPosition["X"], Y=cellSel.cellPosition["Y"]):
                            MINES += 1
                        respObj = corelib.getGameSession(gamesession)['response']
                        old_field = field
                        field = respObj['map']
                        compareFields(old_field, field)
                        sceneGame.updateField(field, gamefinished=not(respObj['continue']))
                        del POSITION, cellSel
                databaseObj.setItem(
                    'mines', 
                    MINES, 
                    'hash', 
                    gamesession, 
                    DatabaseName='gamehashes'
                )
                
        sceneGame.setScoreBoard_value(MINES)
        
        sceneGame.draw(screen)
        sceneGame.update()
        pygame.display.flip()

    pygame.quit()


def getGamesDict():
    listGames = dict()
    for directory in [f for f in os.listdir('source') if len(f.split('.')) == 1]:
        if 'about.json' in os.listdir(f"source/{directory}"):
            f = open(f"source/{directory}/about.json", 'r', encoding='utf-8')
            content = json.loads(f.read())
            listGames[directory] = {
                "gamename": content['title'],
                "path": f"source/{directory}"
            }
    return listGames


def getGameName(name):
    if name in getGamesDict():
        return getGamesDict()[name]["gamename"]
    else:
        return 'Game not founded.'


class app_win(QMainWindow):
    def __init__(self):
        super(app_win, self).__init__()
        self.ui = launcher.Ui_Form()
        self.ui.setupUi(self)
        
        self.database = SQLEasy.database('gameDataBase.db')
        
        # Во-первых, наполним список игроков
        self.ui.StatTable.removeRow(0)
        rowPosition = 0
        for user in self.database.getBase(DatabaseName='users'):
            self.ui.StatTable.insertRow(rowPosition)
            self.ui.StatTable.setItem(rowPosition, 0, QTableWidgetItem(user["username"]))
            self.ui.StatTable.setItem(rowPosition, 1, QTableWidgetItem(str(user["points"])))
            self.ui.StatTable.setItem(rowPosition, 2, QTableWidgetItem(str(user["minesDefuse"])))
            if user["games"] != 0:
                st = str(user["minesDefuse"] // user["games"])
            else:
                st = '0'
            self.ui.StatTable.setItem(rowPosition, 3, QTableWidgetItem(st))
            self.ui.StatTable.setItem(rowPosition, 4, QTableWidgetItem(getGameName(user["lastGame"])))
            
            rowPosition += 1
        self.ui.usernamesList.clear()
        self.accs = list()
        for user in self.database.getBase(DatabaseName='users'):  # Обновляем во вкладке Профили
            self.ui.usernamesList.addItem(user["username"])
            self.accs.append(user)
        
        # Заполним список вариаций сапёра
        self.ui.gameList.clear()
        for gameDir in getGamesDict():
            item = QtWidgets.QListWidgetItem(getGamesDict()[gameDir]['gamename'])
            icon1 = QtGui.QIcon()
            icon1.addPixmap(QtGui.QPixmap(f"source/{gameDir}/gameico.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            item.setIcon(icon1)
            self.ui.gameList.addItem(item)
        
        self.show()
        
        self.ui.usernamesList.doubleClicked.connect(self.importLogin)
        self.ui.regButton.clicked.connect(self.register)
        self.ui.loginButton.clicked.connect(self.logIn)
        self.ui.play.clicked.connect(self.play)
        self.ui.logOut.clicked.connect(self.logOut)
        self.ui.updateGames.clicked.connect(self.upDate_sapers)
        self.ui.loadGame.clicked.connect(self.LoadGame)
        # Список сохранений...
        self.ui.SaveList.clear()
        self.savedGames = list()
        
        multiMethod = corelib.multiMethod()
        
        for save in self.database.getBase('gamehashes'):
            if save['game'] in getGamesDict() and save['userID'] == self.database.getBase('gamedata')[0]['activeprofile']:
                multiMethod.append(corelib.Method('getGameSession', gamesession=save['hash']))
        
        resp = multiMethod.start()['responses']
        respID = -1
        
        for save in self.database.getBase('gamehashes'):
            if save['game'] in getGamesDict() and save['userID'] == self.database.getBase('gamedata')[0]['activeprofile']:
                respID += 1
                if 'response' in resp[respID]:
                    if resp[respID]['response']['continue']:
                        item = QtWidgets.QListWidgetItem(
                            f"{getGamesDict()[save['game']]['gamename']}, мин: {save['mines']}"
                        )
                        icon1 = QtGui.QIcon()
                        icon1.addPixmap(QtGui.QPixmap(f"source/{save['game']}/gameico.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                        item.setIcon(icon1)
                        self.ui.SaveList.addItem(item)
                        self.savedGames.append([
                            save['hash'], 
                            save['mines'],
                            save['game']
                        ])
        
        # Сделаем таймер
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.timerVoid)
        self.timer.start(1)
    
    def upDate_sapers(self):
        self.ui.gameList.clear()
        for gameDir in getGamesDict():
            item = QtWidgets.QListWidgetItem(getGamesDict()[gameDir]['gamename'])
            icon1 = QtGui.QIcon()
            icon1.addPixmap(QtGui.QPixmap(f"source/{gameDir}/gameico.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            item.setIcon(icon1)
            self.ui.gameList.addItem(item)
    
    def logOut(self):
        self.database.setItem(
            'activeprofile', 
            '-', 
            'ID', 
            1, 
        DatabaseName='gamedata')
        self.ui.SaveList.clear()
        QMessageBox.information(self, 'Успех!', 'Вы успешно вышли!!!', QMessageBox.Ok)
    
    def logIn(self):
        if self.ui.loginUsernameLine.text() in [user['username'] for user in self.database.getBase('users')]:
            if SQLEasy.compareKey(self.database.getBase('users'), key='username')[self.ui.loginUsernameLine.text()]['password'] is None:
                self.database.setItem(
                    'activeprofile', 
                    SQLEasy.compareKey(self.database.getBase('users'), key='username')[self.ui.loginUsernameLine.text()]['ID'], 
                    'ID', 
                    1, 
                DatabaseName='gamedata')
                QMessageBox.information(self, 'Успех!', 'Вы успешно вошли!!!', QMessageBox.Ok)
            elif SQLEasy.compareKey(self.database.getBase('users'), key='username')[self.ui.loginUsernameLine.text()]['password'] == self.ui.loginHasloLine.text():
                self.database.setItem(
                    'activeprofile', 
                    SQLEasy.compareKey(self.database.getBase('users'), key='username')[self.ui.loginUsernameLine.text()]['ID'], 
                    'ID', 
                    1, 
                DatabaseName='gamedata')
                QMessageBox.information(self, 'Успех!', 'Вы успешно вошли!!!', QMessageBox.Ok)
            else:
                QMessageBox.critical(self, 'Упс...', 'Неверный пароль!', QMessageBox.Ok)
        else:
            QMessageBox.critical(self, 'Упс...', 'Такого пользователя просто нет :(', QMessageBox.Ok)
        
        self.ui.SaveList.clear()
        self.savedGames = list()
        
        multiMethod = corelib.multiMethod()
        
        for save in self.database.getBase('gamehashes'):
            if save['game'] in getGamesDict() and save['userID'] == self.database.getBase('gamedata')[0]['activeprofile']:
                multiMethod.append(corelib.Method('getGameSession', gamesession=save['hash']))
        
        resp = multiMethod.start()['responses']
        respID = -1
        
        for save in self.database.getBase('gamehashes'):
            if save['game'] in getGamesDict() and save['userID'] == self.database.getBase('gamedata')[0]['activeprofile']:
                respID += 1
                if 'response' in resp[respID]:
                    if resp[respID]['response']['continue']:
                        item = QtWidgets.QListWidgetItem(
                            f"{getGamesDict()[save['game']]['gamename']}, мин: {save['mines']}"
                        )
                        icon1 = QtGui.QIcon()
                        icon1.addPixmap(QtGui.QPixmap(f"source/{save['game']}/gameico.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                        item.setIcon(icon1)
                        self.ui.SaveList.addItem(item)
                        self.savedGames.append([
                            save['hash'], 
                            save['mines'],
                            save['game']
                        ])
    
    def register(self):
        if self.ui.regLoginLine.text() in [user['username'] for user in self.database.getBase('users')]:
            QMessageBox.critical(self, 'Упс...', 'Есть такой пользователь, ЕСТЬ!!!', QMessageBox.Ok)
            return
        if len(self.ui.regHasloLine.text()) > 0:
            if len(self.ui.regHasloLine.text()) >= 65:
                QMessageBox.warning(self, 'Warning!', 'Too many symbols on password!', QMessageBox.Ok)
                return
        
        if len(self.ui.regLoginLine.text()) >= 65:
            QMessageBox.warning(self, 'Warning!', 'Too many symbols on login!', QMessageBox.Ok)
            return
        
        self.database.add({
            "ID": len(self.database.getBase('users')),
            "username": self.ui.regLoginLine.text()
        }, 'users')
        QMessageBox.information(self, 'Успех!', 'Профиль создан!', QMessageBox.Ok)
        
        self.ui.usernamesList.clear()
        self.accs = list()
        for user in self.database.getBase(DatabaseName='users'):  # Обновляем во вкладке Профили
            self.ui.usernamesList.addItem(user["username"])
            self.accs.append(user)
    
    def importLogin(self):
        if self.ui.usernamesList.currentRow() >= 0 and self.ui.usernamesList.currentRow() < len(self.ui.usernamesList):
            user = self.accs[self.ui.usernamesList.currentRow()]
            self.ui.loginUsernameLine.setText(user['username'])
    
    def LoadGame(self):
        global game
        
        self.hide()
        hashK = self.savedGames[self.ui.SaveList.currentRow()][0]
        mines = self.savedGames[self.ui.SaveList.currentRow()][1]
        
        game(
            self.savedGames[self.ui.SaveList.currentRow()][2], 
            gamerID=self.database.getBase('gamedata')[0]['activeprofile'],
            databaseObj=self.database,
            gamehash=hashK,
            MINES=mines,
            muzicOn=self.ui.soundOn.isChecked()
        )
        os.abort()
        del self
        
    
    def play(self):
        global game
        
        self.hide()
        hashK = corelib.newGame(ID=self.database.getBase('gamedata')[0]['activeprofile'], mines=25, fieldsize=10)['response']
        mines = random.randint(25, 55)
        
        game(
            [k for k in getGamesDict()][self.ui.gameList.currentRow()], 
            gamerID=self.database.getBase('gamedata')[0]['activeprofile'],
            databaseObj=self.database,
            gamehash=hashK['gamesession'],
            MINES=mines,
            muzicOn=self.ui.soundOn.isChecked()
        )
        os.abort()
        del self
    
    def timerVoid(self):
        def getCoorectLogin(string):
            login = ''
            for symbol in string:
                if symbol in '0123456789qwertyuiopasdfghjklzxcvbnm_-.' + 'qwertyuiopasdfghjklzxcvbnm'.upper():
                    login += symbol
            if len(login) > 64:
                login = login[:64]
            return login
        
        self.ui.play.setEnabled(
            self.ui.gameList.currentRow() >= 0 and 
            self.ui.gameList.currentRow() < len(self.ui.gameList) and
            not(self.database.getBase('gamedata')[0]['activeprofile'] is None or self.database.getBase('gamedata')[0]['activeprofile'] == '-')
        )
        
        self.ui.logOut.setEnabled(not(self.database.getBase('gamedata')[0]['activeprofile'] is None or self.database.getBase('gamedata')[0]['activeprofile'] == '-'))
        self.ui.loadGame.setEnabled(len(self.ui.SaveList) > 0)
        
        if not(self.database.getBase('gamedata')[0]['activeprofile'] is None or self.database.getBase('gamedata')[0]['activeprofile'] == '-'):
            nickname = SQLEasy.compareKey(self.database.getBase('users'), 'ID')
            nickname = nickname[self.database.getBase('gamedata')[0]['activeprofile']]['username']
            self.ui.gameinfo.setText(f"Добро пожаловать, {nickname}!")
        else:
            self.ui.gameinfo.setText("Войдите или зарегайте профиль, чтобы играть!")
        
        self.ui.loginButton.setEnabled(
            len(self.ui.loginUsernameLine.text()) > 8 and (len(self.ui.loginHasloLine.text()) > 8 or len(self.ui.loginHasloLine.text()) == 0)
        )
        self.ui.regButton.setEnabled(
            len(self.ui.regLoginLine.text()) > 8 and (len(self.ui.regHasloLine.text()) > 8 or len(self.ui.regHasloLine.text()) == 0)
        )
        
        if self.ui.loginUsernameLine.text() != getCoorectLogin(self.ui.loginUsernameLine.text()):
            self.ui.loginUsernameLine.setText(getCoorectLogin(self.ui.loginUsernameLine.text()))
        if self.ui.regLoginLine.text() != getCoorectLogin(self.ui.regLoginLine.text()):
            self.ui.regLoginLine.setText(getCoorectLogin(self.ui.regLoginLine.text()))
        if self.ui.loginHasloLine.text() != getCoorectLogin(self.ui.loginHasloLine.text()):
            self.ui.loginHasloLine.setText(getCoorectLogin(self.ui.loginHasloLine.text()))
        if self.ui.regHasloLine.text() != getCoorectLogin(self.ui.regHasloLine.text()):
            self.ui.regHasloLine.setText(getCoorectLogin(self.ui.regHasloLine.text()))
        
        if self.ui.logPasShow.isChecked():
            self.ui.loginHasloLine.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.ui.loginHasloLine.setEchoMode(QtWidgets.QLineEdit.Password)
        
        if self.ui.regPasShow.isChecked():
            self.ui.regHasloLine.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.ui.regHasloLine.setEchoMode(QtWidgets.QLineEdit.Password)
        
        # Запрещаем редактировать стату
        self.ui.StatTable.setRowCount(0)
        rowPosition = 0
        for user in sorted(self.database.getBase(DatabaseName='users'), key=lambda x: x['points'], reverse=True):
            self.ui.StatTable.insertRow(rowPosition)
            self.ui.StatTable.setItem(rowPosition, 0, QTableWidgetItem(user["username"]))
            self.ui.StatTable.setItem(rowPosition, 1, QTableWidgetItem(str(user["points"])))
            self.ui.StatTable.setItem(rowPosition, 2, QTableWidgetItem(str(user["minesDefuse"])))
            
            if user["games"] != 0:
                st = str(user["minesDefuse"] // user["games"])
            else:
                st = '0'
            self.ui.StatTable.setItem(rowPosition, 3, QTableWidgetItem(st))
            self.ui.StatTable.setItem(rowPosition, 4, QTableWidgetItem(getGameName(user["lastGame"])))
            
            rowPosition += 1


app = QApplication([])
application = app_win()
app.exec()
os.abort()
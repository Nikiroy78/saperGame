import corelib, os, termcolor, colorama
colorama.init()

clear = lambda: os.system('cls')
gamedata = corelib.newGame(ID=0, mines=25, fieldsize=10)['response']
gamedata['continue'] = True
clear()


def getuserfield(field, gamefinnised=False):
    maxFieldCoord = len(field) - 1
    # ░ свободная клетка
    # █ Не открытая клетка
    # F Помечена флагом
    # 1..4 Мины рядом
    # X Минa взорвана
    # S Минa обезврежена
    retfield = list()
    for row in field:
        X = field.index(row)
        retfield.append(list())
        for cell in row:
            Y = field[X].index(cell)
            if ':O' in cell and cell != 'M:O':
                mines = 0
                # Проверим наличие мин
                upCoord = Y != 0
                downCoord = Y != maxFieldCoord
                leftCoord = X != 0
                rightCoord = X != maxFieldCoord
                
                if upCoord and field[X][Y - 1] != cell and ':O' not in field[X][Y - 1]:
                    mines += 1
                if downCoord and field[X][Y + 1] != cell and ':O' not in field[X][Y + 1]:
                    mines += 1
                if leftCoord and field[X - 1][Y] != cell and ':O' not in field[X - 1][Y]:
                    mines += 1
                if rightCoord and field[X + 1][Y] != cell and ':O' not in field[X + 1][Y]:
                    mines += 1
                if mines == 0:
                    if upCoord and field[X][Y - 1] != cell:
                        mines = 1
                    elif downCoord and field[X][Y + 1] != cell:
                        mines = 1
                    elif leftCoord and field[X - 1][Y] != cell:
                        mines = 1
                    elif rightCoord and field[X + 1][Y] != cell:
                        mines = 1
                
                if mines == 0:
                    retfield[-1].append('░')
                elif mines >= 3:
                    retfield[-1].append(termcolor.colored(f"{mines}", "red"))
                elif mines == 2:
                    retfield[-1].append(termcolor.colored(f"{mines}", "yellow"))
                elif mines == 1:
                    retfield[-1].append(termcolor.colored(f"{mines}", "green"))
            elif cell == 'M:F':
                if gamefinnised:
                    retfield[-1].append('S')
                else:
                    retfield[-1].append('F')
            elif ':F' in cell:
                retfield[-1].append('F')
            elif cell == 'M':
                if gamefinnised:
                    retfield[-1].append('X')
                else:
                    retfield[-1].append('█')
            else:
                retfield[-1].append('█')
    
    return retfield


clear()
while gamedata['continue']:
    print('Y/X| 0123456789\n---|=============')
    i = 0
    for row in getuserfield(gamedata['map'], gamefinnised=not(gamedata['continue'])):
        print(f"{i}|. ", ''.join(row))
        i += 1
    
    while True:
        try:
            X = int(input('Введите X: '))
            break
        except:
            pass
    while True:
        try:
            Y = int(input('Введите Y: '))
            break
        except:
            pass
    if input('Введите 0 если хотите поставить флаг: ') == '0':
        corelib.toggleFlag(gamedata['gamesession'], X, Y)
    else:
        corelib.openItem(gamedata['gamesession'], X, Y)
    
    gamedata = corelib.getGameSession(gamedata['gamesession'])['response']
    clear()

print('Y/X| 0123456789\n---|=============')
i = 0
for row in getuserfield(gamedata['map'], gamefinnised=not(gamedata['continue'])):
    print(f"{i}|. ", ''.join(row))
    i += 1
print('Игра окончена!')
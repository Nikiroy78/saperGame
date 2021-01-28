def rgReplace(field, setV, replaceTo):
    print('[rgReplace function]: started.')
    for r in range(len(field)):
        print('[rgReplace function]: row#%s' % r)
        for c in range(len(field[r])):
            print('[rgReplace function]: cell#%s' % c)
            cell = field[r][c]
            if cell == setV:
                print('[rgReplace function]: replacing...')
                field[r][c] = replaceTo
    return field

def vold_regionGen(size, mines):
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
                    print(f"[Generate map] create region#{filedNum}")
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
                        print(f"[Generate map]: upMove creating in {rgCoords}")
                        field[rgCoords["Y"]][rgCoords["X"]] = f"R{filedNum}"
                        break
                    elif downMove and moveID == 1:
                        rgCoords["Y"] += 1
                        print(f"[Generate map]: downMove creating in {rgCoords}")
                        field[rgCoords["Y"]][rgCoords["X"]] = f"R{filedNum}"
                        break
                    elif leftMove and moveID == 2:
                        rgCoords["X"] -= 1
                        print(f"[Generate map]: leftMove creating in {rgCoords}")
                        field[rgCoords["Y"]][rgCoords["X"]] = f"R{filedNum}"
                        break
                    elif rightMove and moveID == 3:
                        rgCoords["X"] += 1
                        print(f"[Generate map]: rightMove creating in {rgCoords}")
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
    
    print('[Generate map]: combine the regions')
    for rowID in range(len(field)):
        print('[Generate map]: cursore in rowID %s' % rowID)
        for cellID in range(len(field[rowID])):
            print('[Generate map]: cursore in cellID %s' % cellID)
            cell = field[rowID][cellID]
            if 'R' in cell:
                print('[Generate map]: combine region %s' % cell)
                sawUp = rowID != 0
                sawDown = rowID != len(field) - 1
                sawLeft = cellID != 0
                sawRight = cellID != len(field) - 1
                print('[Generate map]: debug: %s %s %s %s' % (sawUp, sawDown, sawLeft, sawRight))  # DEBUG
                if sawUp:
                    print('sawUp')  # DEBUG
                    if cell != field[rowID - 1][cellID] and 'R' in field[rowID - 1][cellID]:
                        print('yes!')  # DEBUG
                        if int(cell.split('R')[-1]) > int(field[rowID - 1][cellID].split('R')[-1]):
                            print('Poi')  # DEBUG
                            field = rgReplace(field, cell, field[rowID - 1][cellID])
                            rgMax = field[rowID - 1][cellID]
                            print('[Generate map]: combine the region to %s' % field[rowID - 1][cellID])
                        else:
                            print('Poi2')  # DEBUG
                            field = rgReplace(field, field[rowID - 1][cellID], cell)
                            rgMax = cell
                            print('[Generate map]: combine the region to %s' % cell)
                if sawDown:
                    print('sawDown')  # DEBUG
                    if cell != field[rowID + 1][cellID] and 'R' in field[rowID + 1][cellID]:
                        print('yes!')  # DEBUG
                        if int(cell.split('R')[-1]) > int(field[rowID + 1][cellID].split('R')[-1]):
                            print('Poi')  # DEBUG
                            field = rgReplace(field, cell, field[rowID + 1][cellID])
                            rgMax = field[rowID + 1][cellID]
                            print('[Generate map]: combine the region to %s' % field[rowID + 1][cellID])
                        else:
                            print('Poi2')  # DEBUG
                            field = rgReplace(field, field[rowID + 1][cellID], cell)
                            rgMax = cell
                            print('[Generate map]: combine the region to %s' % cell)
                if sawLeft:
                    if cell != field[rowID][cellID - 1] and 'R' in field[rowID][cellID - 1]:
                        if int(cell.split('R')[-1]) > int(field[rowID][cellID - 1].split('R')[-1]):
                            field = rgReplace(field, cell, field[rowID][cellID - 1])
                            rgMax = field[rowID][cellID - 1]
                            print('[Generate map]: combine the region to %s' % field[rowID][cellID - 1])
                        else:
                            field = rgReplace(field, field[rowID][cellID - 1], cell)
                            rgMax = cell
                            print('[Generate map]: combine the region to %s' % cell)
                if sawRight:
                    if cell != field[rowID][cellID + 1] and 'R' in field[rowID][cellID + 1]:
                        if int(cell.split('R')[-1]) > int(field[rowID][cellID + 1].split('R')[-1]):
                            field = rgReplace(field, cell, field[rowID][cellID + 1])
                            rgMax = field[rowID][cellID + 1]
                            print('[Generate map]: combine the region to %s' % field[rowID][cellID + 1])
                        else:
                            field = rgReplace(field, field[rowID][cellID + 1], cell)
                            rgMax = cell
                            print('[Generate map]: combine the region to %s' % cell)
    
    ret_values = {"field": field, "regionMax_index": filedNum}
    
    return ret_values

def old_regionGen(size, mines):
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
    
    # сгенерируем минимальные 6 больших регионов
    EmptyFiled = True
    filedNum = 0
    while EmptyFiled:
        sizeReg = random.randint(1, (size ** 2) // 8)
        # Определим "Точку развития"
        for X in range(len(field)):
            for Y in range(len(field[X])):
                if field[X][Y] != 'M' and random.randint(0, 100) >= random.randint(85, 90):
                    field[X][Y] = f"R{filedNum}"
                    regionCoords = [X, Y]
        
        cursor = regionCoords.copy()
        for _ in range(sizeReg):
            # Определим "Правила расширения региона"
            moveUp = cursor[0] != 0
            moveDown = cursor[0] != size - 1
            moveLeft = cursor[1] != 0
            moveRight = cursor[1] != size - 1
            
            while True:
                print('void:', cursor[0], cursor[1])
                randSel = ['R', 'L', 'U', 'D'][random.randint(0, 3)]
                if randSel == 'R' and moveRight:
                    cursor[1] += 1
                    if field[cursor[0]][cursor[1]] == 'E':
                        field[cursor[0]][cursor[1]] = f"R{filedNum}"
                    sizeReg -= 1
                    break
                elif randSel == 'L' and moveLeft:
                    cursor[1] -= 1
                    if field[cursor[0]][cursor[1]] == 'E':
                        field[cursor[0]][cursor[1]] = f"R{filedNum}"
                    sizeReg -= 1
                    break
                elif randSel == 'U' and moveUp :
                    cursor[0] -= 1
                    if field[cursor[0]][cursor[1]] == 'E':
                        field[cursor[0]][cursor[1]] = f"R{filedNum}"
                    sizeReg -= 1
                    break
                elif randSel == 'D' and moveDown:
                    cursor[0] += 1
                    if field[cursor[0]][cursor[1]] == 'E':
                        field[cursor[0]][cursor[1]] = f"R{filedNum}"
                    sizeReg -= 1
                    break
        
        valuesoffield = list()
        for Row in field:
            for item in Row:
                valuesoffield.append(item)
        
        EmptyFiled = 'E' in valuesoffield
        if EmptyFiled:
            filedNum += 1
    
    return {"field": field, "regionMax_index": filedNum}

def regionGen_from_core(size, mines):
    print("[Core]: map creating...")
    import random
    # M - Мина
    # ..:F - Флаг
    # R(0..X) - Регионы
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
    
    # сгенерируем регионы
    EmptyFiled = True
    filedNum = 0
    while EmptyFiled:
        print(f"[Core]: Create Region#{filedNum}")
        sizeReg = random.randint(1, (size ** 2) // 8)
        # Определим "Точку развития"
        generated = False
        for X in range(len(field)):
            for Y in range(len(field[X])):
                if field[X][Y] != 'M' and random.randint(0, 100) >= random.randint(85, 90):
                    field[X][Y] = f"R{filedNum}"
                    regionCoords = [X, Y]
                    generated = True
                    break
            if generated:
                break
        
        cursor = regionCoords.copy()
        for _ in range(sizeReg):
            if not(generated):
                break
            # Определим "Правила расширения региона"
            moveUp = cursor[0] != 0
            moveDown = cursor[0] != size - 1
            moveLeft = cursor[1] != 0
            moveRight = cursor[1] != size - 1
            
            while True:
                randSel = ['R', 'L', 'U', 'D'][random.randint(0, 3)]
                if randSel == 'R' and moveRight:
                    cursor[1] += 1
                    if field[cursor[0]][cursor[1]] == 'E':
                        field[cursor[0]][cursor[1]] = f"R{filedNum}"
                    sizeReg -= 1
                    break
                elif randSel == 'L' and moveLeft:
                    cursor[1] -= 1
                    if field[cursor[0]][cursor[1]] == 'E':
                        field[cursor[0]][cursor[1]] = f"R{filedNum}"
                    sizeReg -= 1
                    break
                elif randSel == 'U' and moveUp:
                    cursor[0] -= 1
                    if field[cursor[0]][cursor[1]] == 'E':
                        field[cursor[0]][cursor[1]] = f"R{filedNum}"
                    sizeReg -= 1
                    break
                elif randSel == 'D' and moveDown:
                    cursor[0] += 1
                    if field[cursor[0]][cursor[1]] == 'E':
                        field[cursor[0]][cursor[1]] = f"R{filedNum}"
                    sizeReg -= 1
                    break
        
        valuesoffield = list()
        for Row in field:
            for item in Row:
                valuesoffield.append(item)
        
        EmptyFiled = 'E' in valuesoffield
        if EmptyFiled and generated:
            filedNum += 1
    
    print('[Core]: generating finished')
    return {"field": field, "regionMax_index": filedNum}

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
                    print(f"[Generate map] create region#{filedNum}")
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
                        print(f"[Generate map]: upMove creating in {rgCoords}")
                        field[rgCoords["Y"]][rgCoords["X"]] = f"R{filedNum}"
                        break
                    elif downMove and moveID == 1:
                        rgCoords["Y"] += 1
                        print(f"[Generate map]: downMove creating in {rgCoords}")
                        field[rgCoords["Y"]][rgCoords["X"]] = f"R{filedNum}"
                        break
                    elif leftMove and moveID == 2:
                        rgCoords["X"] -= 1
                        print(f"[Generate map]: leftMove creating in {rgCoords}")
                        field[rgCoords["Y"]][rgCoords["X"]] = f"R{filedNum}"
                        break
                    elif rightMove and moveID == 3:
                        rgCoords["X"] += 1
                        print(f"[Generate map]: rightMove creating in {rgCoords}")
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
    
    print('[Generate map]: combine the regions')
    for rowID in range(len(field)):
        print('[Generate map]: cursore in rowID %s' % rowID)
        for cellID in range(len(field[rowID])):
            print('[Generate map]: cursore in cellID %s' % cellID)
            cell = field[rowID][cellID]
            if 'R' in cell:
                print('[Generate map]: combine region %s' % cell)
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
                            print('[Generate map]: combine the region to %s' % field[rowID - 1][cellID])
                        else:
                            field = rgReplace(field, field[rowID - 1][cellID], cell)
                            rgMax = cell
                            print('[Generate map]: combine the region to %s' % cell)
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
                            print('[Generate map]: combine the region to %s' % field[rowID + 1][cellID])
                        else:
                            field = rgReplace(field, field[rowID + 1][cellID], cell)
                            rgMax = cell
                            print('[Generate map]: combine the region to %s' % cell)
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
                            print('[Generate map]: combine the region to %s' % field[rowID][cellID - 1])
                        else:
                            field = rgReplace(field, field[rowID][cellID - 1], cell)
                            rgMax = cell
                            print('[Generate map]: combine the region to %s' % cell)
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
                            print('[Generate map]: combine the region to %s' % field[rowID][cellID + 1])
                        else:
                            field = rgReplace(field, field[rowID][cellID + 1], cell)
                            rgMax = cell
                            print('[Generate map]: combine the region to %s' % cell)
    
    ret_values = {"field": field, "regionMax_index": filedNum}
    
    return ret_values

field = regionGen(10, 25)
for f in field["field"]:
    print('\t'.join(f))
input()
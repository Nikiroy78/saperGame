import os, sys, json

import threading, Gamecore.guiDrawWaiting
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.Qt import *

with open('Gamecore/config.json', 'r', encoding='utf-8') as cfg:
    cfg = json.loads(cfg.read())

if cfg["pythonRun"]:
    if sys.platform == 'win32':
        runCoreApp = cfg["pythonPath_win32"]
    else:
        runCoreApp = cfg["pythonPath_unix"]
else:
    if sys.platform == 'win32':
        runCoreApp = 'start '
    else:
        runCoreApp = './'


class tool:
    def __init__(self):        
        def showGUI():            
            class coreGUI(threading.Thread):
                def run(self):
                    class app_win(QMainWindow):
                        def __init__(self):
                            super(app_win, self).__init__()
                            self.ui = Gamecore.guiDrawWaiting.Ui_Form()
                            self.ui.setupUi(self)
                            self.show()
                
                    self.app = QApplication([])
                    self.application = app_win()
                    self.app.exec()
                
                def stop(self):
                    self.application.hide()
                    del self
            
            thrObj = coreGUI()
            thrObj.start()
            return thrObj
        
        def noneGUI(*args, **kwargs):
            pass
        
        def stopGUI(thrObj):
            thrObj.stop()
        
        self.showGUI = showGUI
        self.noneGUI = noneGUI
        self.stopGUI = stopGUI
        
        self.wait = self.noneGUI
        self.resp = self.noneGUI
    
    def showGUI_wait(self, show=True):
        if show:
            print('WARNING! You will be using GUI corelib!!!')
            self.wait = self.showGUI
            self.resp = self.stopGUI
        else:
            self.wait = self.noneGUI
            self.resp = self.noneGUI
        
    def response(self, resp):
        waitObj = self.wait()
        
        respf = open('Gamecore/gamestat.json', 'wt', encoding='utf-8')
        respf.write(json.dumps(resp, indent="\t", ensure_ascii=False))
        respf.close()
        
        shellScript = open('runCore.sh', 'wt', encoding='utf-8')
        print(f"cd Gamecore\n{runCoreApp}{cfg['core_file']}")
        shellScript.write(f"cd Gamecore\n{runCoreApp}{cfg['core_file']}")
        shellScript.close()
        if sys.platform != 'win32':
            os.system("./runCore.sh")
        else:
            os.system("runCore.sh")
        
        output = open('Gamecore/response.json', 'r', encoding='utf-8')
        outp = output.read()
        output.close()
        
        returnObj = json.loads(outp)
        self.resp(waitObj)
        return returnObj


tool = tool()


def newGame(ID, mines=25, fieldsize=10):
    return tool.response({
        "status": "newGame",
        "request": {
            "ID": ID,
            "Mines": mines,
            "size": fieldsize
        }
    })


def openItem(gamesession, X, Y):
    return tool.response({
        "status": "openItem",
        "request": {
            "gamesession": gamesession,
            "X": X,
            "Y": Y
        }
    })


def getGameSession(gamesession):
    return tool.response({
        "status": "getGameSession",
        "request": {
            "gamesession": gamesession
        }
    })


def toggleFlag(gamesession, X, Y):
    return tool.response({
        "status": "toggleFlag",
        "request": {
            "gamesession": gamesession,
            "X": X,
            "Y": Y
        }
    })


class Method:
    def __init__(self, method, **kwargs):
        self.method = method
        self.kwargs = kwargs
    
    def start(self):
        return eval(self.method)(**kwargs)


class multiMethod:
    def __init__(self, *methods):
        self.methods = list(methods)
    
    def append(self, method):
        self.methods.append(method)
    
    def pop(self, index):
        self.methods.pop(index)
    
    def __len__(self):
        return len(self.methods)
    
    def start(self):
        request = {"status": 'multiMethod', 'requests': list()}
        for method in self.methods:
            request['requests'].append({
                "status": method.method,
                "request": method.kwargs
            })
        return tool.response(request)
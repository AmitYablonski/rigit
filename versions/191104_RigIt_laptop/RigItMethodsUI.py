from maya import cmds
import os, sys


def reloadRigIt(path='', *args):
    import setupRigIt
    reload(setupRigIt)
    if path:
        setupRigIt.setupRigIt(path)

# get 2 list of files from directory (python and mel) -> .mel files will return with path
def getFilesForButtons(path):
    if os.path.exists(path):
        if not path in sys.path:
            sys.path.append(path)
    pyFiles = []
    melFiles = []
    for content in os.listdir(path):
        if content.endswith('.py'):
            pyFiles.append(content.rpartition('.py')[0])
        if content.endswith('.mel'):
            melFiles.append((content.rpartition('.mel')[0], path + '/' + content))
    return pyFiles, melFiles

# Get all the requested file type in a directory
# Example1: files = getFilesFromPath(path, ['.py', '.mel'])
# Example2: files = getFilesFromPath(path, '.py')
def getFilesFromPath(path, typE):
    '''
    :param path: the folder containing the desired files
    :param typE: file type. example: '.ma', '.py'
    :return: a list of path files
    '''
    files = []
    try:
        if isinstance(typE, list) or isinstance(typE, tuple):
            for t in typE:
                for content in os.listdir(path):
                    if content.endswith(t):
                        files.append(content)
        elif isinstance(typE, str):
            for content in os.listdir(path):
                if content.endswith(typE):
                    files.append(content)
        else:
            print('Error!! getFilesFromPath method - Type variable must be either a list of strings or a string')
            return
        if len(files) == 0:
            print(' // no %s files found in path: ' + (typE, path))
    except:
        print ' // Get files failed, check if path exists: %s' % path
    return files

# Get all the Maya files in a directory
def getMayaFiles(path):
    maya_files = getFilesFromPath(path, [".ma", ".mb"])
    return maya_files

def getMelFiles(path):
    mel_files = getFilesFromPath(path, ".mel")
    return mel_files

def getPythonFiles(path):
    py_files = getFilesFromPath(path, ".py")
    return py_files

def getFoldersFromPath(path):
    folders = []
    for content in os.listdir(path):
        if "." not in content:
            folders.append(content)
    return folders

def readFile(filePath):
    print ' // Reading file: %s' % filePath
    if cmds.file(filePath, query=True, exists=True):
        f = open(filePath, 'r')
        read = ""
        for line in f:
            read += line
        return read + " "
    else:
        print ' // failed reading file: %s' % filePath
        return ''

# Traverse a directory and all subdirectories for fbx files
def getAllFilesFBX(pathExtension):
    fbx_files = []
    # for root, dirs, files in os.walk('/my/tools/directory'):
    for root, dirs, files in os.walk(pathExtension):
        print 'Currently searching {0}'.format(root)
        for file_name in files:
            if file_name.endswith('.fbx'):
                fbx_files.append(os.path.join(root, file_name))
    return fbx_files

# todo error window to make a selection
def makeSelectionWin(*args):
    if cmds.window("Make_Selection", exists=True):
        cmds.deleteUI("Make_Selection")
    Make_SelectionUI = cmds.window("Make_Selection", t="Make Selection", rtf=True)
    mainLayout = cmds.columnLayout()
    cmds.text(label="Make a selection and try again", h=40, w=170)
    buttonLayout = cmds.rowLayout(parent=mainLayout, numberOfColumns=2)
    cmds.button(label='OK', h=30, w=170, parent=buttonLayout,
                command=('cmds.deleteUI(\"' + Make_SelectionUI + '\", window=True)'))
    cmds.showWindow(Make_SelectionUI)

def showScript(text):
    cmds.window(title="Script It!", sizeable=1, rtf=True)
    cmds.rowColumnLayout(nc=1, adj=True)
    sField = cmds.scrollField(tx=text, w=550)
    numOfLines = cmds.scrollField(sField, q=True, numberOfLines=True)
    hight = numOfLines * 16
    if hight > 700:
        hight = 700
    if hight < 150:
        hight = 150
    cmds.scrollField(sField, e=True, h=hight)
    cmds.showWindow()

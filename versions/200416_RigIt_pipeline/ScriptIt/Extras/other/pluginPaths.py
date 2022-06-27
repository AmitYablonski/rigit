import pymel.core, os

for p in os.getenv('MAYA_PLUG_IN_PATH').split(os.pathsep):
    print p


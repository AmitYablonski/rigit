from maya import cmds, mel
import pymel.core as pm
from functools import partial
import generalMayaTools as gmt
import SnowRigMethodsUI as srm

reload(gmt)


class SpringsCollider:

    def __init__(self):

        self.selection = []
        self.widgets = {}
        self.collideMesh = ''
        self.collideObject = ''
        self.xDir = 0
        self.yDir = 1
        self.zDir = 0
        self.fat = 0.1
        self.colliderWin()
        self.offsetLocators = {}

    def colliderWin(self):
        if cmds.window("sprCollider_window", exists=True):
            cmds.deleteUI("sprCollider_window")
        self.widgets["sprCollider_window"] = cmds.window("sprCollider_window", title="Springs Collider", sizeable=1,
                                                         rtf=True)
        self.widgets["topMain_Layout"] = cmds.rowColumnLayout(numberOfColumns=1, adj=True)
        self.widgets["main_Layout"] = cmds.rowColumnLayout(numberOfColumns=1, adj=True)
        topMain = self.widgets["topMain_Layout"]
        main = self.widgets["main_Layout"]
        colW = 100
        cmds.separator(h=7, p=main)
        cmds.text("Step 1 - Select mesh/s to collide with.", p=main)
        self.widgets["sprCollider_meshLayout"] = cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, p=main)
        cmds.button("Collider Mesh/s:", w=colW, c=partial(self.updateFields, "sprCollider_mesh"))
        self.widgets["sprCollider_mesh"] = cmds.textField(text="")

        cmds.separator(h=7, p=main)
        cmds.text("Step 2 - Select Spring Chain/s to collide.\n" +
                  "Note: the ctl selected will be the first in the chain to be affected\n" +
                  "To affect the entire hierarchy, select the top ctl",
                  p=main)
        self.widgets["sprCollider_objectLayout"] = cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, p=main)
        cmds.button("  sprCollider Object/s: ", w=colW, c=partial(self.updateFields, "sprCollider_object"))
        self.widgets["sprCollider_object"] = cmds.textField(text="")

        cmds.separator(h=7, p=main, visible=False)
        self.widgets["hierarchy_radio"] = cmds.radioButtonGrp(numberOfRadioButtons=2, cw2=[130, 130], select=1,
                                                              labelArray2=['affect from selection',
                                                                           'affect entire hierarchy (from top ctl)'],
                                                              p=main)  # ,onc=self.renameChange)

        cmds.separator(h=10, p=main)
        cmds.text("Step 3 - Name the new collider setup group.", p=main)
        self.widgets["sprCollider_grpLayout"] = cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, p=main)
        cmds.button("Group name:", w=colW, c=partial(self.updateFields, "sprCollider_grp"))
        self.widgets["sprCollider_grp"] = cmds.textField(text='new_collide_setup')

        cmds.separator(h=10, p=main)
        cmds.text("Step 4 - Choose axis for collider to move along.", p=main)
        # radio buttons
        self.widgets["sprCollider_axisLayout"] = cmds.rowColumnLayout(nc=2, adjustableColumn=2, p=main)
        cmds.text("     axis:    ")
        self.widgets["axis_floatFieldGrp"] = cmds.floatFieldGrp(numberOfFields=3,
                                                                value1=self.xDir, value2=self.yDir, value3=self.zDir,
                                                                cc=self.updateAxis)
        self.widgets['flipForR_X'] = cmds.checkBox(l='Flip collider for X axis on right side (newX = X * -1)', v=False,
                                                   p=main)
        self.widgets['flipForR_Y'] = cmds.checkBox(l='Flip collider for Y axis on right side', v=True, p=main)
        self.widgets['flipForR_Z'] = cmds.checkBox(l='Flip collider for Z axis on right side', v=False, p=main)

        cmds.separator(h=10, p=main)
        self.widgets["fatFloat"] = cmds.floatSliderGrp(l="fat:", field=True, min=0, max=2, v=0.1,
                                                       fieldMinValue=-100.0, fieldMaxValue=100.0, cc=self.fatFloat,
                                                       p=main)

        cmds.separator(h=7, p=main)
        # extra options
        self.widgets['updateTargets'] = cmds.checkBox(
            l='Reposition collider targets (Must create and position the Offset Locators)',
            p=main, enable=False)
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=1, p=main)
        cmds.button(l='Create Offset Locators (WIP)', c=self.CreateOffsetLocators)
        self.widgets['deleteOffsetLocators_button'] = cmds.button(l='Delete Offset Locators',
                                                                  c=self.DeleteOffsetLocators, enable=False)
        self.widgets['selectOffsetLocators_button'] = cmds.button(l='Select Locators',
                                                                  c=partial(self.DeleteOffsetLocators, True),
                                                                  enable=False)

        cmds.separator(h=15, p=main)
        cmds.button(l="Make Spring Collider", c=self.makeCollider, p=main)
        cmds.separator(h=15, p=topMain)
        cmds.button(l="Create Script", c=self.script_makeCollider, p=main)
        cmds.separator(h=15, p=topMain)

        self.widgets["feedbackTextField"] = cmds.textField(tx="", editable=False, p=topMain)
        self.defaultFeedback()

        # todo ? button to only create the hierarchy ?
        # todo add some kind of ctrl to allow repositioning of the collider after creation.

        cmds.showWindow()

    def updateFields(self, field, *args):
        self.defaultFeedback()
        sel = pm.ls(sl=True)
        # todo check for duplicates in collide object selection (find first in hierarchy and compare)
        mesh = sel[0].name()
        for i in range(1, len(sel)):
            mesh += ", " + sel[i].name()
        if "mesh" in field:
            self.collideMesh = sel
        else:
            self.collideObject = sel
        cmds.textField(self.widgets[field], e=True, tx=mesh)

    def fatFloat(self, *args):
        self.defaultFeedback()
        self.fat = cmds.floatSliderGrp(self.widgets["fatFloat"], q=True, v=True)

    def updateAxis(self, *args):
        self.defaultFeedback()
        self.xDir = cmds.floatFieldGrp(self.widgets["axis_floatFieldGrp"], q=True, value1=True)
        self.yDir = cmds.floatFieldGrp(self.widgets["axis_floatFieldGrp"], q=True, value2=True)
        self.zDir = cmds.floatFieldGrp(self.widgets["axis_floatFieldGrp"], q=True, value3=True)

    def CreateOffsetLocators(self, *args):
        print ' // CreateOffsetLocators()'
        self.defaultFeedback()
        if self.offsetLocators:
            print ' *note* deleting offset locators to avoid double issues'
            self.DeleteOffsetLocators()
        if not self.collideObject:
            self.changeFeedback("No collide object selected", 'red')
            return
        # allLocators = []
        allLocators = {}
        hierarchy = cmds.radioButtonGrp(self.widgets["hierarchy_radio"], q=True, select=True) - 1
        for ctl in self.collideObject:
            print 'Creating offsetLocators for %s' % ctl
            if hierarchy:
                oldCtl = ctl
                ctl = self.find_mGearChainParent(ctl)
                if ctl != oldCtl:
                    print ' *note* - changed ctrl %s to be the first collider instead of %s' % (ctl, oldCtl)
            print '\n //*// Creating offset locators for chain starting from ctl - "%s""' % ctl
            locs = self.OffsetLocatorsForChain(ctl, {})
            # allLocators.append(locs)
            allLocators[ctl] = locs
        print 'allLocators %s' % allLocators
        for locs1 in allLocators:
            for locs2 in allLocators[locs1]:
                self.offsetLocators[locs2.name()] = allLocators[locs1][locs2]
        cmds.checkBox(self.widgets['updateTargets'], e=True, enable=True, v=1)
        cmds.button(self.widgets['deleteOffsetLocators_button'], e=True, enable=True)
        cmds.button(self.widgets['selectOffsetLocators_button'], e=True, enable=True)
        self.changeFeedback("Created offset-locators under the collide objects selected", 'green')

    def OffsetLocatorsForChain(self, ctl, locators={}, lastSize=3):
        print ' // OffsetLocatorsForChain(ctl, locators, lastSize)'
        print 'ctl = %s\nlocators = %s\nlastSize = %s' % (ctl, locators, lastSize)
        # SpaceLocators Creation under current ctl
        newLoc = pm.spaceLocator(n='colliderOffset_' + ctl + '_loc')
        locators[ctl] = newLoc
        newLoc.attr('overrideEnabled').set(1)
        newLoc.attr('overrideColor').set(9)
        newLoc.attr('s').set([2, 2, 2])
        pm.parent(newLoc, ctl)

        collideChild = self.get_mGearChild(ctl)
        if collideChild:
            pm.delete(pm.pointConstraint(collideChild, newLoc))
            newLoc.attr('r').set([0, 0, 0])
            print 'new found child : %s' % collideChild
            locators = self.OffsetLocatorsForChain(collideChild, locators, newLoc.attr('tx').get())
            return locators
        else:
            print 'no more children found'
            newLoc.attr('t').set([lastSize, 0, 0])
            newLoc.attr('r').set([0, 0, 0])
            return locators

    def DeleteOffsetLocators(self, select=False, *args):
        if self.offsetLocators:
            locDic = self.offsetLocators
            pm.select(cl=True)
            for ctl in locDic:
                if select:
                    print 'Selecting locator: %s' % locDic[ctl]
                    pm.select(locDic[ctl], add=True)
                else:
                    print 'Deleting locator: %s' % locDic[ctl]
                    pm.delete(locDic[ctl])
            if not select:
                self.offsetLocators = {}
        else:
            # todo search under the controller to see if an old locator can be found
            self.changeFeedback('No offset locators found associated to current window', 'red')

    def initialChecksOk(self, *args):
        self.defaultFeedback()
        if not self.collideMesh:
            self.changeFeedback("No collide mesh selected", 'red')
            return False
        if not self.collideObject:
            self.changeFeedback("No collide object selected", 'red')
            return False
        return True

    def getUIdata(self):
        hierarchy = cmds.radioButtonGrp(self.widgets["hierarchy_radio"], q=True, select=True) - 1
        grpName = cmds.textField(self.widgets["sprCollider_grp"], q=True, tx=True)
        flipForR_X = cmds.checkBox(self.widgets['flipForR_X'], q=True, v=True)
        flipForR_Y = cmds.checkBox(self.widgets['flipForR_Y'], q=True, v=True)
        flipForR_Z = cmds.checkBox(self.widgets['flipForR_Z'], q=True, v=True)
        return hierarchy, grpName, flipForR_X, flipForR_Y, flipForR_Z

    def makeCollider(self, *args):
        print '\n\n\n   *~* Collider creation stated *~*\n\n'
        if not self.initialChecksOk():
            return
        hierarchy, grpName, flipForR_X, flipForR_Y, flipForR_Z = self.getUIdata()
        setupGrp = pm.group(n=grpName, em=True, w=True)

        # make colliderMesh object a muscle object
        self.addCollideMesh(self.collideMesh, self.fat)

        doneCtls = []
        allKeepOuts = []
        # create the new hierarchy
        for ctl in self.collideObject:
            print "\n /****/ start of new spring chain collider setup for - %s" % ctl
            if hierarchy:
                oldCtl = ctl
                ctl = self.find_mGearChainParent(ctl)
                if ctl != oldCtl:
                    print ' *note* - changed ctrl %s to be the first collider instead of %s' % (ctl, oldCtl)
            # childList = find_mGearChildren(ctl, [ctl])
            ctlCopyList, collideObjects, aimPairs = self.duplicate_mGearHierarchy(ctl, setupGrp, [], [], [])
            print ' // ctlCopyList: //'
            print ctlCopyList
            print ' // collideObjects: //'
            print collideObjects
            print ' // aimPairs: //'
            for pair in aimPairs:
                print pair
            updateTargets = cmds.checkBox(self.widgets['updateTargets'], q=True, v=True)
            if updateTargets:
                if not self.offsetLocators:
                    self.changeFeedback(
                        "Can't find offset locators (either create them or uncheck reposition checkbox)", 'red')
                    print " /error/ Can't find offset locators (either create them or uncheck reposition checkbox)"
                    return

            # create colliding objects
            keepOuts = {}
            for obj in collideObjects:
                locCtl = ""
                if updateTargets:  # This is where the self.offsetLocators is addressed
                    locCtl = obj.rpartition('_collider_target')[0]
                    locator = self.offsetLocators[locCtl]
                    print 'Repositioning obj "%s" according to locator "%s"' % (obj, locator)
                    pm.delete(pm.parentConstraint(locator, obj))
                if locCtl:
                    print 'keepOuts thingy on : %s' % locCtl
                obj = pm.PyNode(obj)
                if not obj.name() in doneCtls:
                    print '// adding %s as a collider (keepOut stage)' % obj
                    xDir = self.xDir
                    yDir = self.yDir
                    zDir = self.zDir
                    if '_R' in obj.name():
                        if flipForR_X:
                            print 'flipping collider x direction for %s' % obj
                            xDir *= -1
                        if flipForR_Y:
                            print 'flipping collider y direction for %s' % obj
                            yDir *= -1
                        if flipForR_Z:
                            print 'flipping collider z direction for %s' % obj
                            zDir *= -1
                    keepOuts[obj] = self.addCollider(obj, xDir, yDir, zDir, name=obj.name() + '_coll')
                    allKeepOuts.append([obj, keepOuts[obj][0]])
                    doneCtls.append(obj.name())

            for i in keepOuts:
                self.flipColliderParents(i, keepOuts[i][0], keepOuts[i][1])  # flipColliderParents(obj, keepout, driven)
                self.connectKeepOut(keepOuts[i][0], self.collideMesh)
            # Finished collider creation!

            # create aim constraints
            for pairCtl, aimGrp, target in aimPairs:
                # for testing: set = aimPairs[0]
                pairCtl = pm.PyNode(pairCtl)
                aimGrp = pm.PyNode(aimGrp)
                target = pm.PyNode(target)
                keepOut = target.getParent()
                # setup the ctrl's aim grp
                ctlCnsParent = self.addParent(pairCtl, "_coll")
                aimGrp.rz >> ctlCnsParent.rz
                # create aim constraint
                # todo aim contraint doesn't work well for right side (possibly also if the main axis isn't Z)
                aim = 1
                if "_R" in aimGrp.name():
                    aim *= -1
                aimCns = pm.aimConstraint(target, aimGrp, worldUpType="object", worldUpObject=aimGrp.getParent(),
                                          aimVector=(aim, 0, 0), upVector=(0, 1, 0), mo=True, skip=["x", "y"])
                # create condition and connect to aimCns
                conNode = pm.shadingNode('condition', asUtility=True, name='conNode_' + aimGrp.name())
                keepOut.ty >> conNode.ft
                conNode.outColorR >> aimCns.attr(target + "W0")
            ctlCopyList, collideObjects, aimPairs = [], [], []  # todo remove?
            print "\n /****/ end of new spring chain collider setup for - %s" % ctl

        # output messege
        messege = "Finished! ['%s" % self.collideObject[0].name()
        for i in range(1, len(self.collideObject)):
            messege += "', '" + self.collideObject[i].name()
        messege += "'] are now colliding with ['%s" % self.collideMesh[0].name()
        for i in range(1, len(self.collideMesh)):
            messege += "', '" + self.collideMesh[i].name()
        print " /// " + messege + "'] ///"
        self.changeFeedback(messege + "']", 'green')
        # give controller for the created colliders
        self.UIcolliderControl(allKeepOuts)
        # self.DeleteOffsetLocators()

    def script_listPyNodes(self, objList):
        if not objList:
            return ''
        if isinstance(objList, list) or isinstance(objList, tuple):
            script = '[pm.PyNode("%s")' % objList[0]
            for i in range(1, len(objList)):
                script += ', pm.PyNode("%s")' % objList[i]
            return script + ']'
        else:
            script = '[pm.PyNode("%s")]' % objList
        return script

    def script_makeCollider(self, *args):
        if not self.initialChecksOk():
            return

        hierarchy, grpName, flipForR_X, flipForR_Y, flipForR_Z = self.getUIdata()

        updateTargets = cmds.checkBox(self.widgets['updateTargets'], q=True, v=True)
        # make offset values from locators
        offsetScript = ''
        offsetDict = {}
        if updateTargets:
            if not self.offsetLocators:
                self.changeFeedback(
                    "Can't find offset locators (either create them or uncheck reposition checkbox)", 'red')
                print " /error/ Can't find offset locators (either create them or uncheck reposition checkbox)"
                return
            for locCtl in self.offsetLocators:
                locator = self.offsetLocators[locCtl]
                attrs = []
                for i in 'tr':
                    val = locator.attr(i).get()
                    out = []
                    for ii in val:
                        out.append(ii)
                    attrs.append(out)
                offsetDict['' + locCtl] = attrs
            offsetScript = 'offsetDict = {'
            i = 0
            for ctl in offsetDict:
                if 0 < i:
                    offsetScript += ','
                i += 1
                trans, rot = offsetDict[ctl]
                transS = '[%0.3f, %0.3f, %0.3f]' % (trans[0], trans[1], trans[2])
                rotS = '[%0.3f, %0.3f, %0.3f]' % (rot[0], rot[1], rot[2])
                offsetScript += '\n\t\t\t "%s": [%s, %s]' % (ctl, transS, rotS)
            offsetScript += '\n\t\t\t }\n'

        print '\n\n   *~* Collider *SCRIPT* creation stated *~*\n'
        script = self.script_getImportsAndMethods()

        # find the first in hierarchy if required
        collideObjList = self.collideObject
        if hierarchy:
            collideObjList = []
            for ctl in self.collideObject:
                oldCtl = ctl
                ctl = self.find_mGearChainParent(ctl)
                collideObjList.append(ctl)
                if ctl != oldCtl:
                    print ' *note* - changed ctrl %s to be the first collider instead of %s' % (ctl, oldCtl)

        script += "\ncollideObject = %s\n" % self.script_listPyNodes(collideObjList)
        script += "collideMesh = %s\n" % self.script_listPyNodes(self.collideMesh)
        script += "fat=%s\n" \
                  "hierarchy = %s\nupdateTargets = %s\n" % (self.fat, hierarchy, updateTargets)
        script += "xDirection = %s\nyDirection = %s\nzDirection = %s\n" % (self.xDir, self.yDir, self.zDir)
        script += "# Use this if there's a need for an axis to collide the opposite way for Right side\n" \
                  "flipForR_X = %s\nflipForR_Y = %s\nflipForR_Z = %s\n" % (flipForR_X, flipForR_Y, flipForR_Z)
        if offsetScript:
            script += 'offsetDict = %s' % offsetScript
        script += "\nsetupGrp = pm.group(n='%s', em=True, w=True) # don't forget to parent this group\n" % grpName

        script += "\n# make colliderMesh object a muscle object (multiple meshes work well)\n" \
                  "addCollideMesh(collideMesh, fat)\n"

        script += "\ndoneCtls = []\nallKeepOuts = []\n" \
                  "# create the new hierarchy\n"

        # the actual script portion
        script += "for ctl in collideObject:\n\t" \
                  "print \"\\n /****/ start of new spring chain collider setup for - %s\" % ctl\n\t"

        script += "ctlCopyList, collideObjects, aimPairs = duplicate_mGearHierarchy(ctl, setupGrp, [], [], [])\n\t" \
                  "print '\\n // ctlCopyList: //'\n\t" \
                  "print ctlCopyList\n\t" \
                  "print ' // collideObjects: //'\n\t" \
                  "print collideObjects\n\t" \
                  "print ' // aimPairs: //'\n\t" \
                  "for pair in aimPairs:\n\t\t" \
                  "print pair\n\t"

        # todo offsetDict shouldn't be necessary (if no offset locators were made)
        script += "# create colliding objects\n\t" \
                  "keepOuts = {}\n\t" \
                  "for obj in collideObjects:\n\t\t" \
                  "obj = pm.PyNode(obj)\n\t\t" \
                  "locCtl = ''\n\t\t" \
                  "if updateTargets:  # setting up the offset\n\t\t\t" \
                  "locCtl = obj.name().rpartition('_collider_target')[0]\n\t\t\t" \
                  "trans, rot = offsetDict[locCtl]\n\t\t\t" \
                  "print 'Repositioning obj \"%s\" according to offsetDict' % (obj)\n\t\t\t" \
                  "obj.attr('t').set(trans)\n\t\t\t" \
                  "obj.attr('r').set(rot)\n\t\t" \
                  "if not obj.name() in doneCtls:\n\t\t\t" \
                  "print '// adding %s as a collider (keepOut stage)' % obj\n\t\t\t" \
                  "xDir = xDirection\n\t\t\t" \
                  "yDir = yDirection\n\t\t\t" \
                  "zDir = zDirection\n\t\t\t" \
                  "if '_R' in obj.name():\n\t\t\t\t" \
                  "if flipForR_X:\n\t\t\t\t\t" \
                  "print 'flipping collider x direction for %s' % obj\n\t\t\t\t\t" \
                  "xDir *= -1\n\t\t\t\t" \
                  "if flipForR_Y:\n\t\t\t\t\t" \
                  "print 'flipping collider y direction for %s' % obj\n\t\t\t\t\t" \
                  "yDir *= -1\n\t\t\t\t" \
                  "if flipForR_Z:\n\t\t\t\t\t" \
                  "print 'flipping collider z direction for %s' % obj\n\t\t\t\t\t" \
                  "zDir *= -1\n\t\t\t" \
                  "keepOuts[obj] = addCollider(obj, xDir, yDir, zDir, name=obj.name() + '_coll')\n\t\t\t" \
                  "allKeepOuts.append([obj, keepOuts[obj][0]])\n\t\t\t" \
                  "doneCtls.append(obj.name())\n\t"

        script += "print '/**/ finished adding colliders (keepout creation stage)\\n'\n\n\t" \
                  "for i in keepOuts:\n\t\t" \
                  "flipColliderParents(i, keepOuts[i][0], keepOuts[i][1])  " \
                  "# flipColliderParents(obj, keepout, driven)\n\t\t" \
                  "print 'flipped parents for %s' % keepOuts[i][0]\n\t\t" \
                  "if isinstance(collideMesh, list) or isinstance(collideMesh, tuple):\n\t\t\t" \
                  "for mesh in collideMesh:\n\t\t\t\t" \
                  "connectKeepOut(keepOuts[i][0], mesh)\n\t\t" \
                  "else:\n\t\t\t" \
                  "connectKeepOut(keepOuts[i][0], collideMesh)\n\t" \
                  "# Finished collider creation!\n\n\t" \
                  "# create aim constraints\n\t" \
                  "for pairCtl, aimGrp, target in aimPairs:\n\t\t" \
                  "pairCtl = pm.PyNode(pairCtl)\n\t\t" \
                  "aimGrp = pm.PyNode(aimGrp)\n\t\t" \
                  "target = pm.PyNode(target)\n\t\t" \
                  "keepOut = target.getParent()\n\t\t" \
                  "# setup the ctrl's aim grp\n\t\t" \
                  "ctlCnsParent = addParent(pairCtl, '_coll')\n\t\t" \
                  "aimGrp.rz >> ctlCnsParent.rz\n\t\t" \
                  "# create aim constraint\n\t\t" \
                  "# todo test that the aim contraint works well for right side.\n\t\t" \
                  "aim = 1\n\t\t" \
                  "if '_R' in aimGrp.name():\n\t\t\t" \
                  "aim *= -1\n\t\t" \
                  "aimCns = pm.aimConstraint(target, aimGrp, worldUpType='object', worldUpObject=aimGrp.getParent(),\n\t\t" \
                  "                          aimVector=(aim, 0, 0), upVector=(0, 1, 0), mo=True, skip=['x', 'y'])\n\t\t" \
                  "# create condition and connect to aimCns\n\t\t" \
                  "conNode = pm.shadingNode('condition', asUtility=True, name='conNode_' + aimGrp.name())\n\t\t" \
                  "keepOut.ty >> conNode.ft\n\t\t" \
                  "conNode.outColorR >> aimCns.attr(target + 'W0')\n\t" \
                  "ctlCopyList, collideObjects, aimPairs = [], [], []\n\t" \
                  "print \"\\n /****/ end of new spring chain collider setup for - %s\" % ctl\n\n\t"
        srm.showScript(script)
        # output messege
        self.changeFeedback("Script Created", 'green')

    def script_getImportsAndMethods(self):
        script = "import pymel.core as pm\n"
        script += self.script_addCollideMesh()
        script += self.script_addMuscle()
        script += self.script_addCollider()
        script += self.script_flipColliderParents()
        script += self.script_connectKeepOut()
        script += self.script_addParent()
        script += self.script_is_mGearParent()
        script += self.script_find_mGearChainParent()
        script += self.script_get_mGearChild()
        script += self.script_get_mGearCtlFromNpo()
        script += self.script_find_mGearChildren()
        script += self.script_duplicate_mGearHierarchy()
        script += self.script_setOffsetForCollider()
        return script

    def addCollideMesh(self, obj, fat):
        if isinstance(obj, (list, tuple)):
            muscleMeshes = []
            for o in obj:
                newMus = self.addMuscle(o, fat)
                if newMus:
                    muscleMeshes.append(newMus)
            return muscleMeshes
        else:
            return self.addMuscle(obj, fat)

    def script_addCollideMesh(self):
        script = "\ndef addCollideMesh(obj, fat):\n\t" \
                 "if isinstance(obj, (list, tuple)):\n\t\t" \
                 "muscleMeshes = []\n\t\t" \
                 "for o in obj:\n\t\t\t" \
                 "newMus = addMuscle(o, fat)\n\t\t\t" \
                 "if newMus:\n\t\t\t\t" \
                 "muscleMeshes.append(newMus)\n\t\t" \
                 "return muscleMeshes\n\t" \
                 "else:\n\t\t" \
                 "return addMuscle(obj, fat)\n"
        return script

    def addMuscle(self, obj, fat):
        # check if object is already a muscle object
        relatives = obj.listRelatives()
        for rel in relatives:
            if isinstance(rel, pm.nodetypes.CMuscleObject):
                print(" /#/ Collider --> %s already connected" % obj.name())
                return ""
        pm.select(obj)
        # todo should possibly add following line:
        # mel.eval('catch(`loadPlugin "C:/Program Files/Autodesk/Maya2017/bin/plug-ins/MayaMuscle.mll"`)')
        muscleMesh = pm.PyNode(mel.eval('cMuscle_makeMuscle(0)')[0])
        muscleMesh.setAttr("fat", fat)
        return muscleMesh

    def script_addMuscle(self):
        script = "\n# todo should possibly add following line:\n" \
                 "# mel.eval(" \
                 "'catch(`loadPlugin \"C:/Program Files/Autodesk/Maya2017/bin/plug-ins/MayaMuscle.mll\"`)')\n" \
                 "def addMuscle(obj, fat):\n\t" \
                 "# check if object is already a muscle object\n\t" \
                 "relatives = obj.listRelatives()\n\t" \
                 "for rel in relatives:\n\t\t" \
                 "if isinstance(rel, pm.nodetypes.CMuscleObject):\n\t\t\t" \
                 "print(' /#/ Collider --> %s already connected' % obj.name())\n\t\t\t" \
                 "return ''\n\t" \
                 "pm.select(obj)\n\t" \
                 "muscleMesh = pm.PyNode(mel.eval('cMuscle_makeMuscle(0)')[0])\n\t" \
                 "muscleMesh.setAttr('fat', fat)\n\t" \
                 "return muscleMesh\n"
        return script

    def addCollider(self, obj, xDir, yDir, zDir, name=''):
        pm.select(obj)
        tempList = mel.eval('cMuscle_rigKeepOutSel()')
        if tempList:
            keepOut, keepOutShape, driven = tempList
        else:
            pm.select(obj)
            print ' /*/ tempList is empty - check if the collider was made - LAST SELECTED: %s' % obj
        pm.setAttr(keepOut + ".inDirectionX", xDir)
        pm.setAttr(keepOut + ".inDirectionY", yDir)
        pm.setAttr(keepOut + ".inDirectionZ", zDir)
        keepOut, driven = pm.PyNode(keepOut), pm.PyNode(driven)
        if name != '':
            pm.rename(keepOut, name)
            pm.rename(driven, name + '_cMuscleKeepOutDriven')
        return keepOut, driven

    def script_addCollider(self):
        script = "\ndef addCollider(obj, xDir, yDir, zDir, name=''):\n\t" \
                 "pm.select(obj)\n\t" \
                 "tempList = mel.eval('cMuscle_rigKeepOutSel()')\n\t" \
                 "if tempList:\n\t\t" \
                 "keepOut, keepOutShape, driven = tempList\n\t" \
                 "else:\n\t\t" \
                 "pm.select(obj)\n\t\t" \
                 "print ' /*/ tempList is empty - check if the collider was made - LAST SELECTED: %s' % obj\n\t" \
                 "pm.setAttr(keepOut + '.inDirectionX', xDir)\n\t" \
                 "pm.setAttr(keepOut + '.inDirectionY', yDir)\n\t" \
                 "pm.setAttr(keepOut + '.inDirectionZ', zDir)\n\t" \
                 "keepOut, driven = pm.PyNode(keepOut), pm.PyNode(driven)\n\t" \
                 "if name != '':\n\t\t" \
                 "pm.rename(keepOut, name)\n\t\t" \
                 "pm.rename(driven, name + '_cMuscleKeepOutDriven')\n\t" \
                 "return keepOut, driven\n"
        return script

    def flipColliderParents(self, obj, keepout, driven):
        objParent = obj.getParent()
        if objParent:
            pm.parent(keepout, objParent)
        else:
            pm.parent(keepout, w=True)
        pm.parent(obj, driven)

    def script_flipColliderParents(self):
        script = '\ndef flipColliderParents(obj, keepout, driven):\n\t' \
                 'objParent = obj.getParent()\n\t' \
                 'if objParent:\n\t\t' \
                 'pm.parent(keepout, objParent)\n\t' \
                 'else:\n\t\t' \
                 'pm.parent(keepout, w=True)\n\t' \
                 'pm.parent(obj, driven)\n'
        return script

    def connectKeepOut(self, keepOut, collideMesh):
        pm.select(keepOut, collideMesh)
        mel.eval('cMuscle_keepOutAddRemMuscle(1)')

    def script_connectKeepOut(self):
        script = "\ndef connectKeepOut(keepOut, collideMesh):\n\t" \
                 "pm.select(keepOut, collideMesh)\n\t" \
                 "mel.eval('cMuscle_keepOutAddRemMuscle(1)')\n"
        return script

    def addParent(self, obj, suffix):
        objParent = obj.listRelatives(p=True)
        if objParent:
            newParent = pm.group(n=obj.name() + suffix, em=True, p=objParent[0])
        else:
            newParent = pm.group(n=obj.name() + suffix, em=True, w=True)
        pm.delete(pm.parentConstraint(obj, newParent))
        pm.parent(obj, newParent)
        return newParent

    def script_addParent(self):
        script = "\ndef addParent(obj, suffix):\n\t" \
                 "objParent = obj.listRelatives(p=True)\n\t" \
                 "if objParent:\n\t\t" \
                 "newParent = pm.group(n=obj.name() + suffix, em=True, p=objParent[0])\n\t" \
                 "else:\n\t\t" \
                 "newParent = pm.group(n=obj.name() + suffix, em=True, w=True)\n\t" \
                 "pm.delete(pm.parentConstraint(obj, newParent))\n\t" \
                 "pm.parent(obj, newParent)\n\t" \
                 "return newParent\n"
        return script

    def is_mGearParent(self, ctl, name):
        ctlParent = ctl.getParent()
        if not ctlParent:
            return False
        if ctlParent.name() == name:
            return True
        else:
            return self.is_mGearParent(ctlParent, name)

    def script_is_mGearParent(self):
        script = "\ndef is_mGearParent(ctl, name):\n\t" \
                 "ctlParent = ctl.getParent()\n\t" \
                 "if not ctlParent:\n\t\t" \
                 "return False\n\t" \
                 "if ctlParent.name() == name:\n\t\t" \
                 "return True\n\t" \
                 "else:\n\t\t" \
                 "return self.is_mGearParent(ctlParent, name)\n"
        return script

    def find_mGearChainParent(self, ctl):
        ctlParent = ctl.getParent()
        if not ctlParent:
            return ctl
        baseName = ctl.rpartition('_ctl')[0]
        number = baseName.rpartition('_fk')[2]
        ver = int(number)
        if ver == 0:
            return ctl
        name = baseName.rpartition(number)[0]
        testName = name + '0_ctl'
        if pm.objExists(testName):
            if self.is_mGearParent(ctl, testName):
                return pm.PyNode(testName)
        else:
            testName = name + str(ver - 1) + '_ctl'
            if pm.objExists(testName):
                if self.is_mGearParent(ctl, testName):
                    if ver - 1 == 0:
                        return pm.PyNode(testName)
                    return self.find_mGearChainParent(pm.PyNode(testName), name)
            else:
                print " // SpringsCollider.find_mGearChainParent() wasn't really expecting to get here..\n" \
                      " // returning the following ctl %s" \
                      " // line 291 in SpringsCollider.py" % ctl
                return pm.PyNode(ctl)

    def script_find_mGearChainParent(self):
        script = "\ndef find_mGearChainParent(ctl):\n\t" \
                 "ctlParent = ctl.getParent()\n\t" \
                 "if not ctlParent:\n\t\t" \
                 "return ctl\n\t" \
                 "baseName = ctl.rpartition('_ctl')[0]\n\t" \
                 "number = baseName.rpartition('_fk')[2]\n\t" \
                 "ver = int(number)\n\t" \
                 "if ver == 0:\n\t\t" \
                 "return ctl\n\t" \
                 "name = baseName.rpartition(number)[0]\n\t" \
                 "testName = name + '0_ctl'\n\t" \
                 "if pm.objExists(testName):\n\t\t" \
                 "if is_mGearParent(ctl, testName):\n\t\t\t" \
                 "return pm.PyNode(testName)\n\t" \
                 "else:\n\t\t" \
                 "testName = name + str(ver - 1) + '_ctl'\n\t\t" \
                 "if pm.objExists(testName):\n\t\t\t" \
                 "if is_mGearParent(ctl, testName):\n\t\t\t\t" \
                 "if ver - 1 == 0:\n\t\t\t\t\t" \
                 "return pm.PyNode(testName)\n\t\t\t\t" \
                 "return find_mGearChainParent(pm.PyNode(testName), name)\n\t\t" \
                 "else:\n\t\t\t" \
                 "print \" // SpringsCollider.find_mGearChainParent() wasn't really expecting to get here.." \
                 "\\n\" \\\n\t\t\t\t" \
                 "  \" // returning the following ctl %s\" \\\n\t\t\t\t" \
                 "  \" // line 291 in SpringsCollider.py\" % ctl\n\t\t\t" \
                 "return pm.PyNode(ctl)\n"
        return script

    def get_mGearChild(self, ctl):
        childs = ctl.listRelatives(c=True, type="transform")
        if childs:
            for ch in childs:
                baseName = ctl.rpartition('_')[0]
                print 'baseName : %s' % baseName
                number = baseName.rpartition('_fk')[2]
                print 'number : %s' % number
                ver = int(number)
                length = len(baseName)
                if ver > 9 and ver < 100:
                    print "ver is between 9 and 100"
                    testName = baseName[:length - 2] + str(ver + 1)
                elif ver < 10:
                    print "ver is under 9"
                    testName = baseName[:length - 1] + str(ver + 1)
                if testName + '_npo' == ch.name():
                    return self.get_mGearCtlFromNpo(ch)
        else:
            return ''

    def script_get_mGearChild(self):
        script = "\ndef get_mGearChild(ctl):\n\t" \
                 "childs = ctl.listRelatives(c=True, type='transform')\n\t" \
                 "if childs:\n\t\t" \
                 "for ch in childs:\n\t\t\t" \
                 "baseName = ctl.rpartition('_')[0]\n\t\t\t" \
                 "print 'baseName : %s' % baseName\n\t\t\t" \
                 "number = baseName.rpartition('_fk')[2]\n\t\t\t" \
                 "print 'number : %s' % number\n\t\t\t" \
                 "ver = int(number)\n\t\t\t" \
                 "length = len(baseName)\n\t\t\t" \
                 "if ver > 9 and ver < 100:\n\t\t\t\t" \
                 "print 'ver is between 9 and 100'\n\t\t\t\t" \
                 "testName = baseName[:length - 2] + str(ver + 1)\n\t\t\t" \
                 "elif ver < 10:\n\t\t\t\t" \
                 "print 'ver is under 9'\n\t\t\t\t" \
                 "testName = baseName[:length - 1] + str(ver + 1)\n\t\t\t" \
                 "if testName + '_npo' == ch.name():\n\t\t\t\t" \
                 "return get_mGearCtlFromNpo(ch)\n\t" \
                 "else:\n\t\t" \
                 "return ''\n"
        return script

    def get_mGearCtlFromNpo(self, ctl):
        childs = ctl.listRelatives(c=True, type="transform")
        if childs:
            for ch in childs:
                if '_cns' in ch.name():
                    return ch.listRelatives(type='transform', c=True)[0]

    def script_get_mGearCtlFromNpo(self):
        script = "\ndef get_mGearCtlFromNpo(ctl):\n\t" \
                 "childs = ctl.listRelatives(c=True, type='transform')\n\t" \
                 "if childs:\n\t\t" \
                 "for ch in childs:\n\t\t\t" \
                 "if '_cns' in ch.name():\n\t\t\t\t" \
                 "return ch.listRelatives(type='transform', c=True)[0]\n"
        return script

    def find_mGearChildren(self, ctl, childList):
        collideChild = self.get_mGearChild(ctl)
        if collideChild:
            print 'new found child : %s' % collideChild
            childList.append(collideChild)
            childList = self.find_mGearChildren(collideChild, childList)
            return childList
        else:
            print 'no more children found'
            return childList

    def script_find_mGearChildren(self):
        script = "\ndef find_mGearChildren(ctl, childList):\n\t" \
                 "collideChild = get_mGearChild(ctl)\n\t" \
                 "if collideChild:\n\t\t" \
                 "print 'new found child : %s' % collideChild\n\t\t" \
                 "childList.append(collideChild)\n\t\t" \
                 "childList = find_mGearChildren(collideChild, childList)\n\t\t" \
                 "return childList\n\t" \
                 "else:\n\t\t" \
                 "print 'no more children found'\n\t\t" \
                 "return childList\n"
        return script

    def duplicate_mGearHierarchy(self, ctl, newParent='', ctlCopyList=[], collideObjects=[], aimPairs=[], lastSize=3,
                                 offsetLocs=False):
        print '/*//*/ doing duplicate_mGearHierarchy with %s' % ctl
        print 'ctl = %s\nnewParent = %s\nctlCopyList = %s\ncollideObjects = %s\naimPairs = %s\nlastSize = %s' % (
            ctl, newParent, ctlCopyList, collideObjects, aimPairs, lastSize)
        if newParent:
            collideParent = pm.group(n=ctl + '_collider', em=True, p=newParent)
        else:
            collideParent = pm.group(n=ctl + '_collider', em=True, w=True)
        ctlCopyList.append(collideParent.name())
        cnsGrp = self.addParent(collideParent, "_cns")
        pm.parentConstraint(ctl.getParent(), cnsGrp)
        targetGrp = pm.group(n=collideParent.name() + "_target", p=cnsGrp, em=True)
        collideObjects.append(targetGrp.name())
        aimGrp = pm.group(n=collideParent.name() + "_aim", p=cnsGrp, em=True)
        pm.delete(pm.pointConstraint(collideParent, aimGrp))  # <-- necessary?
        pm.parent(collideParent, aimGrp)
        # make ctrl connections
        for attr in "trs":
            ctl.attr(attr) >> collideParent.attr(attr)
        aimPairs.append([ctl.name(), aimGrp.name(), targetGrp.name()])
        # search for more children
        collideChild = self.get_mGearChild(ctl)
        if collideChild:
            if offsetLocs:
                self.setOffsetForCollider(ctl, targetGrp)
            else:
                pm.delete(pm.pointConstraint(collideChild, targetGrp))
            print 'new found child : %s' % collideChild
            ctlCopyList, collideObjects, aimPairs = self.duplicate_mGearHierarchy(collideChild, collideParent,
                                                                                  ctlCopyList, collideObjects, aimPairs,
                                                                                  targetGrp.attr('tx').get())
            return ctlCopyList, collideObjects, aimPairs
        else:
            print 'no more children found'
            if offsetLocs:
                self.setOffsetForCollider(ctl, targetGrp)
                return
            else:
                targetGrp.attr("tx").set(lastSize)
            return ctlCopyList, collideObjects, aimPairs

    def script_duplicate_mGearHierarchy(self):
        script = "\ndef duplicate_mGearHierarchy(ctl, newParent='', ctlCopyList=[], collideObjects=[], aimPairs=[], lastSize=3,\n" \
                 "                             offsetLocs=False):\n\t" \
                 "print '/*//*/ doing duplicate_mGearHierarchy with %s' % ctl\n\t" \
                 "print 'ctl = %s\\nnewParent = %s\\nctlCopyList = %s\\ncollideObjects = %s\\naimPairs = %s\\nlastSize = %s'" \
                 " % \\\n\t\t" \
                 "          (ctl, newParent, ctlCopyList, collideObjects, aimPairs, lastSize)\n\t" \
                 "if newParent:\n\t\t" \
                 "collideParent = pm.group(n=ctl + '_collider', em=True, p=newParent)\n\t" \
                 "else:\n\t\t" \
                 "collideParent = pm.group(n=ctl + '_collider', em=True, w=True)\n\t" \
                 "ctlCopyList.append(collideParent.name())\n\t" \
                 "cnsGrp = addParent(collideParent, '_cns')\n\t" \
                 "pm.parentConstraint(ctl.getParent(), cnsGrp)\n\t" \
                 "targetGrp = pm.group(n=collideParent.name() + '_target', p=cnsGrp, em=True)\n\t" \
                 "collideObjects.append(targetGrp.name())\n\t" \
                 "aimGrp = pm.group(n=collideParent.name() + '_aim', p=cnsGrp, em=True)\n\t" \
                 "pm.delete(pm.pointConstraint(collideParent, aimGrp))  # <-- necessary?\n\t" \
                 "pm.parent(collideParent, aimGrp)\n\t" \
                 "# make ctrl connections\n\t" \
                 "for attr in 'trs':\n\t\t" \
                 "ctl.attr(attr) >> collideParent.attr(attr)\n\t" \
                 "aimPairs.append([ctl.name(), aimGrp.name(), targetGrp.name()])\n\t" \
                 "# search for more children\n\t" \
                 "collideChild = get_mGearChild(ctl)\n\t" \
                 "if collideChild:\n\t\t" \
                 "if offsetLocs:\n\t\t\t" \
                 "setOffsetForCollider(ctl, targetGrp)\n\t\t" \
                 "else:\n\t\t\t" \
                 "pm.delete(pm.pointConstraint(collideChild, targetGrp))\n\t\t" \
                 "print 'new found child : %s' % collideChild\n\t\t" \
                 "ctlCopyList, collideObjects, aimPairs = duplicate_mGearHierarchy(collideChild, collideParent,\n\t" \
                 "                                                                     " \
                 "ctlCopyList, collideObjects, aimPairs,\n\t" \
                 "                                                                     " \
                 "targetGrp.attr('tx').get())\n\t\t" \
                 "return ctlCopyList, collideObjects, aimPairs\n\t" \
                 "else:\n\t\t" \
                 "print 'no more children found'\n\t\t" \
                 "if offsetLocs:\n\t\t\t" \
                 "setOffsetForCollider(ctl, targetGrp)\n\t\t\t" \
                 "return\n\t\t" \
                 "else:\n\t\t\t" \
                 "targetGrp.attr('tx').set(lastSize)\n\t\t" \
                 "return ctlCopyList, collideObjects, aimPairs\n"
        return script

    def setOffsetForCollider(self, ctl, targetGrp):
        # todo finish this method
        # todo find the associated locator
        # self.offsetLocators

        baseName = ctl.rpartition('_')[0]
        print 'baseName : %s' % baseName
        number = baseName.rpartition('_fk')[2]
        print 'number : %s' % number
        ver = int(number)
        length = len(baseName)
        if ver > 9 and ver < 100:
            print "ver is between 9 and 100"
            testName = baseName[:length - 2] + str(ver + 1)
        elif ver < 10:
            print "ver is under 9"
            testName = baseName[:length - 1] + str(ver + 1)

    def script_setOffsetForCollider(self):
        script = "\ndef setOffsetForCollider(ctl, targetGrp):\n\t" \
                 "# find the associated locator\n\t" \
                 "baseName = ctl.rpartition('_')[0]\n\t" \
                 "print 'baseName : %s' % baseName\n\t" \
                 "number = baseName.rpartition('_fk')[2]\n\t" \
                 "print 'number : %s' % number\n\t" \
                 "ver = int(number)\n\t" \
                 "length = len(baseName)\n\t" \
                 "if ver > 9 and ver < 100:\n\t\t" \
                 "print 'ver is between 9 and 100'\n\t\t" \
                 "testName = baseName[:length - 2] + str(ver + 1)\n\t" \
                 "elif ver < 10:\n\t\t" \
                 "print 'ver is under 9'\n\t\t" \
                 "testName = baseName[:length - 1] + str(ver + 1)\n"
        return script

    def UIcolliderControl(self, keepOuts):
        '''
        This creates a window to control the colliders after creation
        :param keepOuts:
        :return:
        '''
        i = 0
        winName = "colliderCtrl_window"
        while cmds.window(winName + str(i), exists=True):
            i += 1
        cmds.window(winName + str(i), title="Collider Settings", sizeable=1, rtf=True)
        mainLayout = cmds.rowColumnLayout(numberOfColumns=1, adj=True)
        cmds.separator(h=7)
        # set header with proper names:
        '''
        colStr = gmt.stringMyPmList(self.collideObject)
        meshStr = gmt.stringMyPmList(self.collideMesh)
        if not colStr:
            colStr = ""
        if not meshStr:
            meshStr = ""
        '''
        cmds.text('Settings for the new collider/s and Muscle object/s', font='boldLabelFont')
        cmds.separator(h=7)
        fatLayout = cmds.rowColumnLayout(nc=1, p=mainLayout)
        cmds.separator(h=7, p=mainLayout)
        axisLayout = cmds.rowColumnLayout(nc=1, p=mainLayout)

        self.UIconnectColliderAttrs(fatLayout, axisLayout, keepOuts)

        cmds.showWindow()

    def UIconnectColliderAttrs(self, fatLayout, axisLayout, keepOuts):
        # connect meshes
        if isinstance(self.collideMesh, (list, tuple)):
            for obj in self.collideMesh:
                self.UIcolliderMeshConnect(obj, fatLayout)
                print("connect %s collider attrs" % obj)
        else:
            self.UIcolliderMeshConnect(self.collideMesh, fatLayout)
            print("connect %s collider attrs" % self.collideMesh)
        # connect objects
        for set in keepOuts:
            self.colliderObjConnect(set[1], set[0], axisLayout)
            print("connect %s collider attrs" % set[0])

    def UIcolliderMeshConnect(self, obj, layoutP):
        relatives = obj.listRelatives()
        muscles = []
        for rel in relatives:
            if isinstance(rel, pm.nodetypes.CMuscleObject):
                muscles.append(rel)
        for mus in muscles:
            cmds.text('muscle object "' + obj.name() + '":', p=layoutP, align="left")
            pm.attrFieldSliderGrp(at='%s.fat' % mus, p=layoutP,
                                  min=0, max=5, fieldMinValue=-100.0, fieldMaxValue=100.0)

    def colliderObjConnect(self, keepOut, obj, layoutP):
        cmds.text('collider object "%s":' % obj.name(), p=layoutP, align="left")
        field = pm.attrFieldGrp(p=layoutP)
        field.setAttribute(keepOut.inDirection)
        field.setLabel('axis')

    def defaultFeedback(self):
        self.changeFeedback("Collider Tool")

    def changeFeedback(self, messege, error=''):
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.6, .3, .3)
        if error == "green":
            bg = (.3, .6, .3)
        cmds.textField(self.widgets["feedbackTextField"], e=True, bgc=bg, tx=messege)

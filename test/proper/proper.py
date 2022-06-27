import pymel.core as pm
from maya import cmds
import os
import mutils
from MBA_SE02.legacy import asset_helper

class Proper:
    def __init__(self):
        self.char_name = []
        self.char_ns = []
        self.tricycle_name = []
        self.helmet_name = []
        self.pose_path = []
        char_dir = 'P:/MBA_SE02/assets/characters'
        self.characters_options = os.listdir(char_dir)
        var_dir = 'P:/MBA_SE02/assets/variants'
        self.variant_options = os.listdir(var_dir)
        self.asset_helper = asset_helper.AssetHelper()
        self.helmetConstraintException = ['piggy', 'summer']
        self.errorLog = []
        self.warningLog = []


    def run(self, selection, tricycles=True, align_tricycles=True, dress_tricycles=True, mode_tricycles=False, helmet=True):
        self.clearData()
        if self.extractChar(selection):
            # todo: manage multiple characters selection
            if not(helmet or tricycles):
                self.errorLog.append("No props selected")
                return
            # Helmet
            if helmet:
                # check if helmet already constraint to this character
                if pm.ls(self.char_ns+"*helmet*parentConstraint"):
                    if not pm.confirmBox("Double prop warning","This character has helmet already, are you sure you want to add another one?", "Continue", "Cancel"):
                        self.warningLog.append("Helmet canceled")
                        return
                if self.loadHelmet():
                    self.constraintHelmet()
                    if not self.helmetMode():
                        self.warningLog.append("No helmet mode found for this character")
                else:
                    self.errorLog.append("No helmet found for this character")

            # Tricycles
            if tricycles:
                # check if tricycles already constraint to this character
                if pm.ls(self.char_ns+"*tricycles*parentConstraint"):
                    if not pm.confirmBox("Double prop warning","This character has tricycles already, are you sure you want to add another one?", "Continue", "Cancel"):
                        self.warningLog.append("Tricycles canceled")
                        return
                if self.getPose():
                    if dress_tricycles:
                        self.loadTricycle()
                    else:
                        self.extractTricycles(selection)
                    if self.tricycle_name:
                        if align_tricycles:
                            self.alignTricycle()
                        self.applyPose()
                        self.constraintToTricycle()
                        if mode_tricycles:
                            self.changeTricyclesMode()
                        else:
                            self.warningLog.append("This character does not have a tricycle mode")
                    else:
                        self.errorLog.append("No tricycles selected")
                else:
                    self.errorLog.append("This character does not have a tricycle pose")
        else:
            self.errorLog.append("No character selected")

    def clearData(self):
        self.char_name = []
        self.char_ns = []
        self.tricycle_name = []
        self.helmet_name = []
        self.pose_path = []
        self.errorLog = []
        self.warningLog = []

    def assetName(self, asset_ns):
        split_asset_name = asset_ns.split('_')
        asset_name = split_asset_name[0]
        if len(split_asset_name) > 2:
            for n in range(len(split_asset_name) - 2):
                asset_name = asset_name + '_' + split_asset_name[n + 1]
        return asset_name

    def extractTricycles(self, selection):
        for item in selection:
            item_ns = item.split(':')[0]
            item_name = self.assetName(item_ns)
            if 'tricycles' in item_name:
                self.tricycle_name = item_ns
                break
        if self.tricycle_name:
            return True
        else:
            return False

    def extractChar(self, selection):
        for item in selection:
            item_ns = item.split(':')[0]
            item_name = self.assetName(item_ns)
            if item_name in self.characters_options:
                self.char_name = item_name
                self.char_ns = item_ns
                break
            elif item_name in self.variant_options:
                self.char_name = item_name.split('_')[0]
                self.char_ns = item_ns
                break
        if self.char_name:
            return True
        else:
                return False

    def getPose(self):
        self.pose_path = "P:/MBA_SE02/assets/characters/%s/anim_lib/RIG/Tricycles_Pose.pose/pose.json" % self.char_name
        if os.path.exists(self.pose_path):
            return True
        else:
            return False

    def applyPose(self):
        pose = mutils.Pose.fromPath(self.pose_path)
        # pose.select(namespaces=[char_ns])
        pose.load(namespaces=[self.char_ns])

    def constraintToTricycle(self):
        pm.parentConstraint(self.tricycle_name + ':cog_C0_ctl', self.char_ns + ':global_C0_ctl_cns_ctl', mo=1, n=self.char_ns + "_" + self.tricycle_name + "_parentConstraint")
        pm.parentConstraint(self.tricycle_name + ':pedal_L0_ctl', self.char_ns + ':leg_L0_ikcns_ctl', mo=1)
        pm.parentConstraint(self.tricycle_name + ':pedal_R0_ctl', self.char_ns + ':leg_R0_ikcns_ctl', mo=1)
        pm.parentConstraint(self.tricycle_name + ':frontWheel_L1_fk2_ctl', self.char_ns + ':arm_L0_ikcns_ctl', mo=1)
        pm.parentConstraint(self.tricycle_name + ':frontWheel_R1_fk2_ctl', self.char_ns + ':arm_R0_ikcns_ctl', mo=1)

    def alignTricycle(self):
        # todo: check rosy, sweetums and robin tricycles size issue
        tricycles = pm.PyNode(self.tricycle_name + ':global_C0_ctl')
        char = pm.PyNode(self.char_ns + ':global_C0_ctl')
        constraint = pm.parentConstraint(char, tricycles, mo=False)
        pm.delete(constraint)

    def loadTricycle(self):
        self.tricycle_name = self.asset_helper.load_asset(asset_name="tricycles",
                                                          asset_path="P:/MBA_SE02/assets/props/tricycles/public/tricycles_rigging.mb",
                                                          as_reference=True, asset_namespace=False)[0]

    def loadHelmet(self):
        helmet_name = 'helmet_' + self.char_name
        helmet_path = "P:/MBA_SE02/assets/props/"+helmet_name+"/public/"+helmet_name+"_rigging.mb"
        print helmet_name
        print helmet_path
        if os.path.exists(helmet_path):
            self.helmet_name = self.asset_helper.load_asset(asset_name=helmet_name,
                                                              asset_path=helmet_path,
                                                              as_reference=True, asset_namespace=False)[0]
            return True
        else:
            return False

    def constraintHelmet(self):
        constraint_name = self.char_ns + "_" + self.helmet_name + "_parentConstraint"
        if self.char_name in self.helmetConstraintException:
            pm.parentConstraint(self.char_ns + ':faceAutoOri_C0_ctl', self.helmet_name + ':local_C0_ctl_cns', mo=False, n=constraint_name)
        else:
            pm.parentConstraint(self.char_ns+':JawMainUp_C0_0_jnt', self.helmet_name+':local_C0_ctl_cns', mo=False, n=constraint_name)

    def helmetMode(self):
        helmetModes = ["helmetMode", "helmet_mode", "helmetHair"]

        charLocal = pm.PyNode(self.char_ns+':local_C0_ctl')
        for helmetMode in helmetModes:
            if pm.hasAttr(charLocal, helmetMode):
                pm.PyNode(charLocal+"."+helmetMode).set(1)
                return True

        return False

    def changeTricyclesMode(self):
        # todo: change rozy name in tricycles asset to lowercase
        if self.char_name in ["skeeter", "scooter"]:
            pm.setAttr(self.tricycle_name+":global_C0_ctl.type", 10)
        else:
            enumNames = cmds.addAttr(self.tricycle_name+":global_C0_ctl.type", enumName=True, q=True).split(":")
            if self.char_name in enumNames:
                pm.setAttr(self.tricycle_name + ":global_C0_ctl.type", enumNames.index(self.char_name))


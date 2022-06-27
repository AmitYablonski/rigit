import pymel.core as pm
# from PyQt5 import QtCore, QtGui, QtWidgets
# from PySide2 import QtWidgets, QtCore, QtGui
from sb_libs.latest.Qt import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance
from maya import OpenMayaUI as omui
import sb_ui

# import paper
# reload(paper)


def getMayaMainWindow():
    win = omui.MQtUtil_mainWindow()
    return wrapInstance(long(win), QtWidgets.QMainWindow)


class paperUI(QtWidgets.QDialog):
    def __init__(self):
        # todo: singleton
        parent = getMayaMainWindow()
        super(paperUI, self).__init__(parent=parent)
        self.setStyleSheet(sb_ui.load_stylesheets(["main_window"]))

        self.setWindowTitle("paper")
        # self.paperInst = paper.paper()
        self.setEnabled(True)
        self.setToolTip("")
        self.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.setMinimumHeight(340)
        self.setMinimumWidth(400)

        # main vertical layout
        self.verticalLayoutWidget = QtWidgets.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(30, 30, 201, 200))
        self.mainVerticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.mainVerticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)

        # instruction label
        self.instructionLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.instructionLabel.setText("Select a character, add props and PropIt!\n")
        self.mainVerticalLayout.addWidget(self.instructionLabel)

        # Tricycle checkbox
        self.TricyclesCheckBox = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.TricyclesCheckBox.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.TricyclesCheckBox.setFont(font)
        self.TricyclesCheckBox.setText("Tricycles")
        self.mainVerticalLayout.addWidget(self.TricyclesCheckBox)

        # Tricycles options horizontal layout
        self.tricyclesOptionsHorizontalLayout = QtWidgets.QHBoxLayout()

        # Tricycles options vertical layout spacer
        self.tricyclesOptionsVerticalLayout_Spacer = QtWidgets.QVBoxLayout()
        # todo: replace with a spacer
        self.spacerLabel_1 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.spacerLabel_1.setText("   ")
        self.tricyclesOptionsVerticalLayout_Spacer.addWidget(self.spacerLabel_1)
        self.tricyclesOptionsHorizontalLayout.addLayout(self.tricyclesOptionsVerticalLayout_Spacer)

        # Tricycles options vertical layout
        self.tricyclesOptionsVerticalLayout = QtWidgets.QVBoxLayout()

        # Dress Tricycle radio buttons Layout
        self.dressTricyclesOptionsHorizontalLayout = QtWidgets.QHBoxLayout()
        self.tricyclesOptionsVerticalLayout.addLayout(self.dressTricyclesOptionsHorizontalLayout)

        # Dress Tricycle radio buttons
        self.DressRadionButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.dressTricyclesOptionsHorizontalLayout.addWidget(self.DressRadionButton)
        self.DressRadionButton.setText("Dress new tricycles    ")
        self.DressRadionButton.setChecked(True)
        self.DressRadionButton.setEnabled(False)
        self.selectTricycles = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.dressTricyclesOptionsHorizontalLayout.addWidget(self.selectTricycles)
        self.selectTricycles.setText("Select tricycles")
        self.selectTricycles.setEnabled(False)

        # Tricycle align checkbox
        self.AlignCheckBox = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.AlignCheckBox.setEnabled(False)
        self.AlignCheckBox.setChecked(True)
        self.tricyclesOptionsVerticalLayout.addWidget(self.AlignCheckBox)
        self.AlignCheckBox.setText("Align tricycles to character")

        # # Tricycle dress checkbox
        # self.DressCheckBox = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        # self.DressCheckBox.setEnabled(False)
        # self.DressCheckBox.setChecked(True)
        # self.tricyclesOptionsVerticalLayout.addWidget(self.DressCheckBox)
        # self.DressCheckBox.setText("Dress new tricycles")

        # Tricycle mode check box
        self.ModeCheckBox = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.ModeCheckBox.setEnabled(False)
        self.ModeCheckBox.setChecked(True)
        self.ModeCheckBox.setText("Mode - Match tricycles mode to character")
        self.tricyclesOptionsVerticalLayout.addWidget(self.ModeCheckBox)

        # Add tricycle option layout to main layout
        self.tricyclesOptionsHorizontalLayout.addLayout(self.tricyclesOptionsVerticalLayout)
        self.mainVerticalLayout.addLayout(self.tricyclesOptionsHorizontalLayout)

        # todo: replace with a spacer
        # spacer label
        self.spacerLabel_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.spacerLabel_2.setText("")
        self.mainVerticalLayout.addWidget(self.spacerLabel_2)

        # Helmet checkbox
        self.HelmetCheckBox = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.HelmetCheckBox.setFont(font)
        self.mainVerticalLayout.addWidget(self.HelmetCheckBox)
        self.HelmetCheckBox.setText("Helmet")

        # todo: replace with a spacer
        # spacer2 label
        self.spacerLabel_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.spacerLabel_3.setText("")
        self.mainVerticalLayout.addWidget(self.spacerLabel_3)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.pushButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton.clicked.connect(self.propItFunc)
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton.setText("Prop it")
        self.CloseButtonBox = QtWidgets.QDialogButtonBox(self.verticalLayoutWidget)
        self.CloseButtonBox.setEnabled(True)
        self.CloseButtonBox.setToolTip("")
        self.CloseButtonBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.CloseButtonBox.setAutoFillBackground(False)
        self.CloseButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.CloseButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.CloseButtonBox.setCenterButtons(False)
        self.horizontalLayout.addWidget(self.CloseButtonBox)
        self.mainVerticalLayout.addLayout(self.horizontalLayout)
        self.CloseButtonBox.rejected.connect(self.close)
        self.TricyclesCheckBox.clicked['bool'].connect(self.AlignCheckBox.setEnabled)
        self.TricyclesCheckBox.clicked['bool'].connect(self.ModeCheckBox.setEnabled)
        # self.TricyclesCheckBox.clicked['bool'].connect(self.DressCheckBox.setEnabled)
        self.TricyclesCheckBox.clicked['bool'].connect(self.DressRadionButton.setEnabled)
        self.TricyclesCheckBox.clicked['bool'].connect(self.selectTricycles.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(self)






    def propItFunc(self):

        # Get tricycles' checkboxes values
        tricycles = self.TricyclesCheckBox.checkState()
        align_tricycles = self.AlignCheckBox.checkState()
        dress_tricycles = self.DressRadionButton.isChecked()
        mode_tricycles = self.ModeCheckBox.checkState()

        # Get helmet's checkboxes values
        helmet = self.HelmetCheckBox.checkState()

        # Get selected objects
        objects = pm.ls(sl=True)

        # Run paper
        self.paperInst.run(selection=objects, tricycles=tricycles, align_tricycles=align_tricycles, dress_tricycles=dress_tricycles, mode_tricycles=mode_tricycles, helmet=helmet)

        # print log
        message = 'Props added successfully'
        if self.paperInst.errorLog:
            message = "ERROR:\n"+"\n".join(self.paperInst.errorLog)
        elif self.paperInst.warningLog:
            message = "WARNING:\n"+"\n".join(self.paperInst.warningLog)
        title = "LOG"
        self.UserMassage(title, message)


    def UserMassage(self, title, message):
        reply = QtWidgets.QMessageBox()
        reply.setText(message)
        reply.setWindowTitle(title)
        reply.setStandardButtons(QtWidgets.QMessageBox.Close)
        reply.setStyleSheet(sb_ui.load_stylesheets(["main_window"]))
        reply.exec_()
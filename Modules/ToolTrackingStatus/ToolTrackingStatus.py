import vtk, qt, ctk, slicer
import os
import numpy as np

from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

import logging

# TrainUS parameters
import TrainUSLib.TrainUSParameters as Parameters

#------------------------------------------------------------------------------
#
# ToolTrackingStatus
#
#------------------------------------------------------------------------------
class ToolTrackingStatus(ScriptedLoadableModule):
  
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "ToolTrackingStatus"
    self.parent.categories = ["TrainUS"]
    self.parent.dependencies = []
    self.parent.contributors = ["David Garcia Mato (Ebatinca), Csaba Pinter (Ebatinca)"]
    self.parent.helpText = """ Module to display US image and modify display settings. """
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """EBATINCA, S.L."""

#------------------------------------------------------------------------------
#
# ToolTrackingStatusWidget
#
#------------------------------------------------------------------------------
class ToolTrackingStatusWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  
  def __init__(self, parent):
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)

    # Create logic class
    self.logic = ToolTrackingStatusLogic(self)

    # TrainUS widget
    self.trainUsWidget = slicer.trainUsWidget

  #------------------------------------------------------------------------------
  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Set up UI
    self.setupUi()

    # Setup connections
    self.setupConnections()

    # The parameter node had defaults at creation, propagate them to the GUI
    self.updateGUIFromMRML()

    # Layout
    self.logic.updateSliceControllerVisibility(True)
    self.logic.setup3DView()

  #------------------------------------------------------------------------------
  def onClose(self, unusedOne, unusedTwo):
    pass

  #------------------------------------------------------------------------------
  def cleanup(self):
    self.disconnect()

  #------------------------------------------------------------------------------
  def enter(self):
    """
    Runs whenever the module is reopened
    """
    # Layout
    self.logic.updateSliceControllerVisibility(True)
    self.logic.setup3DView()

    # Watch transforms
    self.logic.watchToolTransforms()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def setupUi(self):
    
    # Load widget from .ui file (created by Qt Designer).
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/ToolTrackingStatus.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Customize widgets
    resizeMode = qt.QHeaderView.ResizeToContents
    self.ui.toolsTableWidget.horizontalHeader().setSectionResizeMode(resizeMode)

  #------------------------------------------------------------------------------
  def setupConnections(self):
    self.ui.backToMenuButton.clicked.connect(self.onBackToMenuButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    self.ui.backToMenuButton.clicked.disconnect()

  #------------------------------------------------------------------------------
  def updateGUIFromMRML(self, caller=None, event=None):
    """
    Set selections and other settings on the GUI based on the parameter node.

    Calls the updateGUIFromMRML function of all tabs so that they can take care of their own GUI.
    """
    pass

  #------------------------------------------------------------------------------
  def onBackToMenuButtonClicked(self):
    
    # Go back to Home module
    slicer.util.selectModule('Home') 


#---------------------------------------------------------------------------------------------#
#                                                                                             #
#                                                                                             #
#                                                                                             #
#                                       ToolTrackingStatusLogic                                          #
#                                                                                             #
#                                                                                             #
#                                                                                             #
#---------------------------------------------------------------------------------------------#
class ToolTrackingStatusLogic(ScriptedLoadableModuleLogic, VTKObservationMixin):
  
  def __init__(self, widgetInstance, parent=None):
    ScriptedLoadableModuleLogic.__init__(self, parent)
    VTKObservationMixin.__init__(self)

    # Define member variables
    self.fileDir = os.path.dirname(__file__)
    # Only defined in case there is no other way but having to use the widget from the logic
    self.moduleWidget = widgetInstance
    self.trainUsWidget = slicer.trainUsWidget

    # Setup keyboard shortcuts
    self.setupKeyboardShortcuts()

    # Watchdog
    self.watchdogNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLWatchdogNode')
    self.addObserver(self.watchdogNode, vtk.vtkCommand.ModifiedEvent, self.onWatchdogNodeModified)        

  #------------------------------------------------------------------------------
  def watchToolTransforms(self):

    if not self.watchdogNode:
        return

    # Get list of transforms in the scene
    toolTransformNames = ['ProbeToTracker', 'StylusToTracker', 'ReferenceToTracker']

    # Get current watched nodes
    watchedNodeIds = list()
    numberOfWatchedNodes = self.watchdogNode.GetNumberOfWatchedNodes()
    for watchedNodeIndex in range(numberOfWatchedNodes):
      node = self.watchdogNode.GetWatchedNode(watchedNodeIndex)
      watchedNodeIds.append(node.GetID())

    # Add transforms to watchdog node
    for transformName in toolTransformNames:
      # Get transform
      transformNode = None
      try:
        transformNode = slicer.util.getNode(transformName)
      except:
        logging.warning('WARNING: Transform node with name "%s" was not found.' % transformName)
        return

      # Add new watched nodes
      transformNodeId = transformNode.GetID()
      if transformNodeId not in watchedNodeIds:
        self.watchdogNode.AddWatchedNode(transformNode)

    # Update table
    self.updateToolsTable()

  #------------------------------------------------------------------------------
  def updateToolsTable(self):

    toolsTableWidget = self.moduleWidget.ui.toolsTableWidget

    toolsTableWidget.blockSignals(True)

    # Get number of watched transform nodes
    numberOfWatchedNodes = self.watchdogNode.GetNumberOfWatchedNodes()

    # Set row count for table widget
    if numberOfWatchedNodes > toolsTableWidget.rowCount:
      # Add rows to table
      rowStartIndex = toolsTableWidget.rowCount
      toolsTableWidget.setRowCount(numberOfWatchedNodes)
      for rowIndex in range(rowStartIndex, numberOfWatchedNodes):
        # name
        nameItem = qt.QTableWidgetItem()
        toolsTableWidget.setItem(rowIndex, 0, nameItem)

        # Qt alignment variables from qnamespace.h
        AlignHCenter = 0x0004
        AlignVCenter = 0x0080
        AlignCenter = AlignVCenter | AlignHCenter
        
        # status
        pStatusIconWidget = qt.QWidget()
        label = qt.QLabel()
        label.setObjectName("StatusIcon")
        pStatusLayout = qt.QHBoxLayout(pStatusIconWidget)
        pStatusLayout.addWidget(label)
        pStatusLayout.setAlignment(AlignCenter)
        pStatusLayout.setContentsMargins(0,0,0,0)
        pStatusIconWidget.setLayout(pStatusLayout)
        toolsTableWidget.setCellWidget( rowIndex, 2, pStatusIconWidget)

        # sound
        pSoundWidget = qt.QWidget()
        pCheckBox = qt.QCheckBox()
        pCheckBox.setObjectName("Sound")
        pSoundLayout = qt.QHBoxLayout(pSoundWidget)
        pSoundLayout.addWidget(pCheckBox)
        pSoundLayout.setAlignment(AlignCenter)
        pCheckBox.setStyleSheet("margin-left:2px; margin-right:2px;margin-top:2px; margin-bottom:2px;")
        pSoundWidget.setLayout(pSoundLayout)
        toolsTableWidget.setCellWidget( rowIndex, 1, pSoundWidget)
        pCheckBox.stateChanged.connect(self.onSoundCheckBoxStateChanged)

    elif (numberOfWatchedNodes < toolsTableWidget.rowCount):
      # Removes rows from table
      toolsTableWidget.setRowCount(numberOfWatchedNodes)

    # Fill table
    for watchedNodeIndex in range(numberOfWatchedNodes):
      node = self.watchdogNode.GetWatchedNode(watchedNodeIndex)

      toolsTableWidget.item(watchedNodeIndex, 0).setText(node.GetName())

      soundCheckBox = toolsTableWidget.cellWidget(watchedNodeIndex, 1).findChild(qt.QCheckBox, 'Sound')
      if soundCheckBox:
        soundActive = self.watchdogNode.GetWatchedNodePlaySound(watchedNodeIndex)
        if soundActive:
          soundCheckBox.setCheckState(2) # checked
        else:
          soundCheckBox.setCheckState(0) # unchecked

      statusIcon = toolsTableWidget.cellWidget(watchedNodeIndex,2).findChild(qt.QLabel, 'StatusIcon')
      if statusIcon:
        if self.watchdogNode.GetWatchedNodeUpToDate(watchedNodeIndex):
          statusIcon.setPixmap(qt.QPixmap(":/Icons/NodeValid.png"))
          statusIcon.setToolTip("valid")
        else:
          statusIcon.setPixmap(qt.QPixmap(":/Icons/NodeInvalid.png"))
          statusIcon.setToolTip("invalid")

    toolsTableWidget.resizeRowsToContents()
    toolsTableWidget.blockSignals(False)

  #------------------------------------------------------------------------------
  def onWatchdogNodeModified(self, caller=None, event=None):
    self.updateToolsTable() # to update status icon

  #------------------------------------------------------------------------------
  def onSoundCheckBoxStateChanged(self, state):
    # TODO: update sound property in watchdog node (self.watchdogNode.SetWatchedNodePlaySound())
    pass

  #------------------------------------------------------------------------------
  def exitApplication(self, status=slicer.util.EXIT_SUCCESS, message=None):
    """Exit application.
    If ``status`` is ``slicer.util.EXIT_SUCCESS``, ``message`` is logged using ``logging.info(message)``
    otherwise it is logged using ``logging.error(message)``.
    """
    def _exitApplication():
      if message:
        if status == slicer.util.EXIT_SUCCESS:
          logging.info(message)
        else:
          logging.error(message)
      slicer.util.mainWindow().hide()
      slicer.util.exit(slicer.util.EXIT_FAILURE)
    qt.QTimer.singleShot(0, _exitApplication)

  #------------------------------------------------------------------------------
  def setup3DView(self):
    layoutManager = slicer.app.layoutManager()
    layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)

    # Modify slice viewers
    for name in layoutManager.sliceViewNames():
      sliceWidget = layoutManager.sliceWidget(name)
      self.showViewerPinButton(sliceWidget, show = True)

  #------------------------------------------------------------------------------
  def showViewerPinButton(self, sliceWidget, show):
    try:
      sliceControlWidget = sliceWidget.children()[1]
      pinButton = sliceControlWidget.children()[1].children()[1]
      if show:
        pinButton.show()
      else:
        pinButton.hide()
    except: # pylint: disable=w0702
      pass

  #------------------------------------------------------------------------------
  def updateSliceControllerVisibility(self, visible):
    # Update visibility of slice controllers
    for name in slicer.app.layoutManager().sliceViewNames():
      sliceWidget = slicer.app.layoutManager().sliceWidget(name)
      sliceWidget.sliceController().setVisible(visible)

  #------------------------------------------------------------------------------
  def setupKeyboardShortcuts(self):
    shortcuts = [
        ('Ctrl+3', lambda: slicer.util.mainWindow().pythonConsole().parent().setVisible(not slicer.util.mainWindow().pythonConsole().parent().visible))
        ]

    for (shortcutKey, callback) in shortcuts:
        shortcut = qt.QShortcut(slicer.util.mainWindow())
        shortcut.setKey(qt.QKeySequence(shortcutKey))
        shortcut.connect('activated()', callback)
    

#------------------------------------------------------------------------------
#
# ToolTrackingStatusTest
#
#------------------------------------------------------------------------------
class ToolTrackingStatusTest(ScriptedLoadableModuleTest):
  """This is the test case for your scripted module.
  """

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    ScriptedLoadableModuleTest.runTest(self)

#
# Class for avoiding python error that is caused by the method SegmentEditor::setup
# http://issues.slicer.org/view.php?id=3871
#
class ToolTrackingStatusFileWriter(object):
  def __init__(self, parent):
    pass

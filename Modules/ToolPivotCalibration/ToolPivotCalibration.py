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
# ToolPivotCalibration
#
#------------------------------------------------------------------------------
class ToolPivotCalibration(ScriptedLoadableModule):
  
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "ToolPivotCalibration"
    self.parent.categories = ["TrainUS"]
    self.parent.dependencies = []
    self.parent.contributors = ["David Garcia Mato (Ebatinca), Csaba Pinter (Ebatinca)"]
    self.parent.helpText = """ Module to calibrate tracked tools by pivoting around their tip. """
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """EBATINCA, S.L."""

#------------------------------------------------------------------------------
#
# ToolPivotCalibrationWidget
#
#------------------------------------------------------------------------------
class ToolPivotCalibrationWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  
  def __init__(self, parent):
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)

    # Create logic class
    self.logic = ToolPivotCalibrationLogic(self)

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
    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def exit(self):
    """
    Runs when exiting the module.
    """
    pass

  #------------------------------------------------------------------------------
  def setupUi(self):
    
    # Load widget from .ui file (created by Qt Designer).
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/ToolPivotCalibration.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

  #------------------------------------------------------------------------------
  def setupConnections(self):
    self.ui.toolSelectorComboBox.currentTextChanged.connect(self.onToolSelectorComboBoxTextChanged)
    self.ui.backToMenuButton.clicked.connect(self.onBackToMenuButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    self.ui.toolSelectorComboBox.currentTextChanged.disconnect()
    self.ui.backToMenuButton.clicked.disconnect()

  #------------------------------------------------------------------------------
  def updateGUIFromMRML(self, caller=None, event=None):
    """
    Set selections and other settings on the GUI based on the parameter node.

    Calls the updateGUIFromMRML function of all tabs so that they can take care of their own GUI.
    """
    # Update GUI
    self.ui.settingGroupBox.enabled = self.logic.validToolSelection
    self.ui.pivotingGroupBox.enabled = self.logic.validToolSelection
    self.ui.inputTransformLabel.text = self.logic.inputTransformName
    self.ui.outputTransformLabel.text = self.logic.outputTransformName

  #------------------------------------------------------------------------------
  def onToolSelectorComboBoxTextChanged(self, toolName):

    # Select tool
    self.logic.updateToolSelection(toolName)

    # TEST
    print('Selected tool: ', toolName)
    print('Input transform: ', self.logic.inputTransformName)
    print('Output transform: ', self.logic.outputTransformName)

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onBackToMenuButtonClicked(self):
    
    # Go back to Home module
    slicer.util.selectModule('Home') 


#---------------------------------------------------------------------------------------------#
#                                                                                             #
#                                                                                             #
#                                                                                             #
#                                       ToolPivotCalibrationLogic                                          #
#                                                                                             #
#                                                                                             #
#                                                                                             #
#---------------------------------------------------------------------------------------------#
class ToolPivotCalibrationLogic(ScriptedLoadableModuleLogic, VTKObservationMixin):
  
  def __init__(self, widgetInstance, parent=None):
    ScriptedLoadableModuleLogic.__init__(self, parent)
    VTKObservationMixin.__init__(self)

    # Define member variables
    self.fileDir = os.path.dirname(__file__)
    # Only defined in case there is no other way but having to use the widget from the logic
    self.moduleWidget = widgetInstance
    self.trainUsWidget = slicer.trainUsWidget 

    # Tool selection
    self.validToolSelection = False
    self.validInputTransformSelected = False
    self.inputTransformNode = None
    self.inputTransformName = None
    self.validOutputTransformSelected = False
    self.outputTransformNode = None
    self.outputTransformName = None

  def updateToolSelection(self, toolName):

    # Look for input transform (ToolToReference)
    try:
      self.inputTransformName = toolName + 'ToTracker'
      self.inputTransformNode = slicer.util.getNode(self.inputTransformName)
      self.validInputTransformSelected = True
    except:
      self.inputTransformName = 'Not found'
      self.inputTransformNode = None
      self.validInputTransformSelected = False

    # Look for output transform (ToolTipToTool)
    try:
      self.outputTransformName = toolName + 'TipTo' + toolName
      self.outputTransformNode = slicer.util.getNode(self.outputTransformName)
      self.validOutputTransformSelected = True
    except:
      self.outputTransformName = 'Not found'
      self.outputTransformNode = None
      self.validOutputTransformSelected = False
      outputTransformName = 'None'

    # Valid tool selection
    self.validToolSelection = self.validInputTransformSelected #TODO: and self.validOutputTransformSelected


#------------------------------------------------------------------------------
#
# ToolPivotCalibrationTest
#
#------------------------------------------------------------------------------
class ToolPivotCalibrationTest(ScriptedLoadableModuleTest):
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
class ToolPivotCalibrationFileWriter(object):
  def __init__(self, parent):
    pass

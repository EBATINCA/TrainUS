import vtk, qt, ctk, slicer
import os

from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

import logging

#------------------------------------------------------------------------------
#
# UltrasoundDisplaySettings
#
#------------------------------------------------------------------------------
class UltrasoundDisplaySettings(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UltrasoundDisplaySettings"
    self.parent.categories = ["TrainUS"]
    self.parent.dependencies = []
    self.parent.contributors = ["David Garcia Mato (Ebatinca), Csaba Pinter (Ebatinca)"]
    self.parent.helpText = """ Module to display US image and modify display settings. """
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """EBATINCA, S.L."""

#------------------------------------------------------------------------------
#
# UltrasoundDisplaySettingsWidget
#
#------------------------------------------------------------------------------
class UltrasoundDisplaySettingsWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  
  def __init__(self, parent):
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)

    # Create logic class
    self.logic = UltrasoundDisplaySettingsLogic(self)

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
    # Apply singleton parameter node settings to application
    self.logic.setParameterNode(self.logic.getParameterNode())

    # Display US image
    self.logic.displayUSImage()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def setupUi(self):
    
    # Load widget from .ui file (created by Qt Designer).
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/UltrasoundDisplaySettings.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Customize widgets
    self.ui.connectionStatusLabel.text = '-'
    self.ui.sliceControllerVisibilityCheckBox.checked = True
    self.ui.freezeUltrasoundButton.setText('Un-freeze')
    self.ui.fitUltrasoundButton.setText('Fit')
    self.ui.flipUltrasoundButton.setText('Un-flip')

  #------------------------------------------------------------------------------
  def setupConnections(self):
    self.ui.freezeUltrasoundButton.clicked.connect(self.onFreezeUltrasoundButtonClicked)
    self.ui.fitUltrasoundButton.clicked.connect(self.onFitUltrasoundButtonClicked)
    self.ui.flipUltrasoundButton.clicked.connect(self.onFlipUltrasoundButtonClicked)
    self.ui.brightnessContrastNormalButton.clicked.connect(self.onBrightnessContrastNormalButtonClicked)
    self.ui.brightnessContrastBrightButton.clicked.connect(self.onBrightnessContrastBrightButtonClicked)
    self.ui.brightnessContrastBrighterButton.clicked.connect(self.onBrightnessContrastBrighterButtonClicked)
    self.ui.brightnessContrastCustomButton.clicked.connect(self.onBrightnessContrastCustomButtonClicked)
    self.ui.brightnessSliderWidget.valuesChanged.connect(self.onBrightnessSliderWidgetValuesChanged)
    self.ui.sliceControllerVisibilityCheckBox.toggled.connect(self.onSliceControllerVisibilityCheckBoxToggled)
    self.ui.backToMenuButton.clicked.connect(self.onBackToMenuButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    self.ui.freezeUltrasoundButton.clicked.disconnect()
    self.ui.fitUltrasoundButton.clicked.disconnect()
    self.ui.flipUltrasoundButton.clicked.disconnect()
    self.ui.brightnessContrastNormalButton.clicked.disconnect()
    self.ui.brightnessContrastBrightButton.clicked.disconnect()
    self.ui.brightnessContrastBrighterButton.clicked.disconnect()
    self.ui.brightnessContrastCustomButton.clicked.disconnect()
    self.ui.brightnessSliderWidget.valuesChanged.disconnect()
    self.ui.sliceControllerVisibilityCheckBox.toggled.disconnect()
    self.ui.backToMenuButton.clicked.disconnect()

  #------------------------------------------------------------------------------
  def getParameterNode(self):
    """
    Convenience function to get the parameter node from the module logic.

    :return vtkMRMLScriptedModuleNode: Parameter node containing the data roles as node references
      and parameters as Get/SetParameter with parameter name in the style 'Group.Parameter'
    """
    return self.logic.getParameterNode()

  #------------------------------------------------------------------------------
  def updateGUIFromMRML(self, caller=None, event=None):
    """
    Set selections and other settings on the GUI based on the parameter node.

    Calls the updateGUIFromMRML function of all tabs so that they can take care of their own GUI.
    """
    # Get parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('updateGUIFromMRML: Failed to get parameter node')
      return

    # Enable buttons only if US image is available in the scene
    usImageAvailable = self.logic.isUSImageAvailable()
    self.ui.parametersGroupBox.enabled = usImageAvailable
    self.ui.brightnessContrastGroupBox.enabled = usImageAvailable
    self.ui.controlGroupBox.enabled = usImageAvailable

    # Connection status
    connectorStatus = parameterNode.GetParameter(self.trainUsWidget.logic.plusConnectionStatusParameterName)
    self.ui.connectionStatusLabel.text = connectorStatus

    # Freeze ultrasound button
    if self.logic.usFrozen:
      self.ui.freezeUltrasoundButton.setText('Un-freeze')
    else:
      self.ui.freezeUltrasoundButton.setText('Freeze')

    # Flip ultrasound button
    if self.logic.usFlipped:
      self.ui.flipUltrasoundButton.setText('Un-flip')
    else:
      self.ui.flipUltrasoundButton.setText('Flip')

    # Window/level adjustment
    self.ui.brightnessSliderWidget.visible = self.ui.brightnessContrastCustomButton.checked

  #------------------------------------------------------------------------------
  def onSliceControllerVisibilityCheckBoxToggled(self, state):
    self.logic.updateSliceControllerVisibility(not state)

  #------------------------------------------------------------------------------
  def onFreezeUltrasoundButtonClicked(self):
    self.logic.freezeUltrasoundImage()
    self.updateGUIFromMRML()   

  #------------------------------------------------------------------------------
  def onFitUltrasoundButtonClicked(self):
    self.logic.fitUltrasoundImage()
    self.updateGUIFromMRML()   

  #------------------------------------------------------------------------------
  def onFlipUltrasoundButtonClicked(self):
    self.logic.flipUltrasoundImage()
    self.updateGUIFromMRML()   

  #------------------------------------------------------------------------------
  def onBrightnessContrastNormalButtonClicked(self):
    self.ui.brightnessSliderWidget.setMinimumValue(0)
    self.ui.brightnessSliderWidget.setMaximumValue(200)   

  #------------------------------------------------------------------------------
  def onBrightnessContrastBrightButtonClicked(self):
    self.ui.brightnessSliderWidget.setMinimumValue(0)
    self.ui.brightnessSliderWidget.setMaximumValue(120)   

  #------------------------------------------------------------------------------
  def onBrightnessContrastBrighterButtonClicked(self):
    self.ui.brightnessSliderWidget.setMinimumValue(0)
    self.ui.brightnessSliderWidget.setMaximumValue(60)   

  #------------------------------------------------------------------------------
  def onBrightnessContrastCustomButtonClicked(self):
    self.logic.updateBrightnessContrastInteraction(self.ui.brightnessContrastCustomButton.checked)
    self.updateGUIFromMRML()   

  #------------------------------------------------------------------------------
  def onBrightnessSliderWidgetValuesChanged(self, minVal, maxVal):
    # Update us image level
    self.logic.setImageMinMaxLevel(minVal, maxVal)  

  #------------------------------------------------------------------------------
  def onBackToMenuButtonClicked(self):
    # Deactivate custom brightness-contrast interaction mode
    self.ui.brightnessContrastCustomButton.checked = False
    self.logic.updateBrightnessContrastInteraction(False)
    self.updateGUIFromMRML()

    # Go back to Home module
    slicer.util.selectModule('Home') 
      


#---------------------------------------------------------------------------------------------#
#                                                                                             #
#                                                                                             #
#                                                                                             #
#                                       UltrasoundDisplaySettingsLogic                                          #
#                                                                                             #
#                                                                                             #
#                                                                                             #
#---------------------------------------------------------------------------------------------#
class UltrasoundDisplaySettingsLogic(ScriptedLoadableModuleLogic, VTKObservationMixin):
  
  def __init__(self, widgetInstance, parent=None):
    ScriptedLoadableModuleLogic.__init__(self, parent)
    VTKObservationMixin.__init__(self)

    # Define member variables
    self.fileDir = os.path.dirname(__file__)
    # Only defined in case there is no other way but having to use the widget from the logic
    self.moduleWidget = widgetInstance
    self.trainUsWidget = slicer.trainUsWidget
    # Pointer to the parameter node so that we have access to the old one before setting the new one
    self.parameterNode = None

    # Default parameters map
    self.defaultParameters = {}

    # Parameter node reference roles
    # self.modelReferenceRolePrefix = 'Model_'

    # Parameter node parameter names

    # Ultrasound variables
    self.usFrozen = False
    self.usFlipped = False

    # Custom W/L
    self.crosshairNode = None
    self.mouseObserverID = None

    # Setup scene
    self.setupScene()

    # Setup keyboard shortcuts
    self.setupKeyboardShortcuts()

  #------------------------------------------------------------------------------
  def setParameterNode(self, inputParameterNode, force=False):
    """
    Set parameter node as main parameter node in the application.
    - When importing a scene the parameter node from the scene is set
    - When closing the scene, the parameter node is reset
    - Handle observations of managed nodes (remove from old ones, add to new ones)
    - Set default parameters if not specified in the given node
    """
    if inputParameterNode == self.parameterNode and not force:
      return

    # Remove observations from nodes referenced in the old parameter node
    if self.parameterNode is not None:
      self.removeObserver(self.parameterNode, vtk.vtkCommand.ModifiedEvent, self.moduleWidget.updateGUIFromMRML)

    # Set parameter node member variable (so that we have access to the old one before setting the new one)
    self.parameterNode = inputParameterNode
    if self.parameterNode is None:
      return

    # Add observations on referenced nodes
    if self.parameterNode:
      self.addObserver(self.parameterNode, vtk.vtkCommand.ModifiedEvent, self.moduleWidget.updateGUIFromMRML)

    # Set default parameters if missing
    self.setDefaultParameters()

    # Add observations on referenced nodes
    #TODO:

    # Update widgets
    self.moduleWidget.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def setDefaultParameters(self, force=False):
    """
    Set default parameters to the parameter node. The default parameters are stored in the map defaultParameters

    :param bool force: Set default parameter even if the parameter is already set. False by default
    """
    parameterNode = self.getParameterNode()
    if not parameterNode:
      logging.error('Failed to set default parameters due to missing parameter node')
      return

    existingParameterNames = parameterNode.GetParameterNames()

    wasModified = parameterNode.StartModify()  # Modify all properties in a single batch

    for name, value in self.defaultParameters.items():
      if not force and name in existingParameterNames:
        continue
      parameterNode.SetParameter(name, str(value))

    parameterNode.EndModify(wasModified)

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
  def setupScene(self):
    # Observe scene loaded and closed events. In those cases we need to make sure the scene is set up correctly afterwards
    # if not self.hasObserver(slicer.mrmlScene, slicer.vtkMRMLScene.EndImportEvent, self.onSceneEndImport):
    #   self.addObserver(slicer.mrmlScene, slicer.vtkMRMLScene.EndImportEvent, self.onSceneEndImport)
    # if not self.hasObserver(slicer.mrmlScene, slicer.vtkMRMLScene.EndCloseEvent, self.onSceneEndClose):
    #   self.addObserver(slicer.mrmlScene, slicer.vtkMRMLScene.EndCloseEvent, self.onSceneEndClose)

    # Set up the layout / 3D View
    self.setup2DView()
    self.updateSliceControllerVisibility(False)

  #------------------------------------------------------------------------------
  def setup2DView(self):
    layoutManager = slicer.app.layoutManager()
    layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)

    # Modify slice viewers
    for name in slicer.app.layoutManager().sliceViewNames():
      sliceWidget = slicer.app.layoutManager().sliceWidget(name)
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
  def setupKeyboardShortcuts(self):
    shortcuts = [
        ('Ctrl+3', lambda: slicer.util.mainWindow().pythonConsole().parent().setVisible(not slicer.util.mainWindow().pythonConsole().parent().visible))
        ]

    for (shortcutKey, callback) in shortcuts:
        shortcut = qt.QShortcut(slicer.util.mainWindow())
        shortcut.setKey(qt.QKeySequence(shortcutKey))
        shortcut.connect('activated()', callback)

  #------------------------------------------------------------------------------
  def displayUSImage(self):    
    # Get parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('displayUSImage: Failed to get parameter node')
      return

    # Get image name from parameter node
    usImageName = parameterNode.GetParameter(self.trainUsWidget.logic.usImageNameParameterName)

    # Volume reslice driver
    try:
      volumeResliceDriverLogic = slicer.modules.volumereslicedriver.logic()
    except:
      logging.error('Volume Reslice Driver module was not found.')
      return

    # Set US image display
    if self.isUSImageAvailable():
      # Get volume node from image name
      usImageVolumeNode = slicer.util.getNode(usImageName)

      # Set ultrasound image as background in slice view
      redSliceLogic = slicer.app.layoutManager().sliceWidget("Red").sliceLogic()
      redSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(usImageVolumeNode.GetID())

      # Volume reslice driver
      redSliceNode = slicer.util.getNode('vtkMRMLSliceNodeRed')
      volumeResliceDriverLogic.SetDriverForSlice(usImageVolumeNode.GetID(), redSliceNode)
      volumeResliceDriverLogic.SetModeForSlice(volumeResliceDriverLogic.MODE_TRANSVERSE, redSliceNode)

    # Fit to view      
    self.fitUltrasoundImage()

  #------------------------------------------------------------------------------
  def isUSImageAvailable(self):    
    # Get parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('displayUSImage: Failed to get parameter node')
      return

    # Get image name from parameter node
    usImageName = parameterNode.GetParameter(self.trainUsWidget.logic.usImageNameParameterName)

    # Get US volume from name
    try:
      usImageVolumeNode = slicer.util.getNode(usImageName)
    except:
      return False
    return True

  #------------------------------------------------------------------------------
  def updateSliceControllerVisibility(self, visible):
    # Update visibility of slice controllers
    for name in slicer.app.layoutManager().sliceViewNames():
      sliceWidget = slicer.app.layoutManager().sliceWidget(name)
      sliceWidget.sliceController().setVisible(visible)

  #------------------------------------------------------------------------------
  def freezeUltrasoundImage(self):
    # Get parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('displayUSImage: Failed to get parameter node')
      return

    # Get IGTL connector node ID from parameter node
    connectorNodeID = parameterNode.GetParameter(self.trainUsWidget.logic.igtlConnectorNodeIDParameterName)

    # Get IGTL connector node ID
    try:
      connectorNode = slicer.util.getNode(connectorNodeID)
    except:
      logging.error('UltrasoundDisplaySettings.freezeUltrasoundImage Unable to get connector node from ID')
      return

    # Update frozen state
    if self.usFrozen:
      connectorNode.Start()
      self.usFrozen = False
    else:
      connectorNode.Stop()
      self.usFrozen = True

  #------------------------------------------------------------------------------
  def fitUltrasoundImage(self):
    # Set ultrasound image as background in slice view
    redSliceLogic = slicer.app.layoutManager().sliceWidget("Red").sliceLogic()
    redSliceLogic.FitSliceToAll()

  #------------------------------------------------------------------------------
  def flipUltrasoundImage(self):
    # Get slice node
    redSliceNode = slicer.util.getNode('vtkMRMLSliceNodeRed')
      
    # Volume reslice driver
    try:
      volumeResliceDriverLogic = slicer.modules.volumereslicedriver.logic()
    except:
      logging.error('Volume Reslice Driver module was not found.')
      return

    # Flip image
    self.usFlipped = not self.usFlipped
    volumeResliceDriverLogic.SetFlipForSlice(self.usFlipped, redSliceNode)

  #------------------------------------------------------------------------------
  def setImageMinMaxLevel(self, minLevel, maxLevel):    
    # Get parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('displayUSImage: Failed to get parameter node')
      return

    # Get image name from parameter node
    usImageName = parameterNode.GetParameter(self.trainUsWidget.logic.usImageNameParameterName)

    # Display US image in slice view
    try:
      # Get volume node
      usImageVolumeNode = slicer.util.getNode(usImageName)
      # Get display node
      usImageDisplayNode = usImageVolumeNode.GetDisplayNode()
      usImageDisplayNode.SetAutoWindowLevel(False)
      usImageDisplayNode.SetWindowLevelMinMax(minLevel, maxLevel)
    except:
      logging.error('Ultrasound image not found in current scene...')

  #------------------------------------------------------------------------------
  def getImageMinMaxLevel(self, caller=None, event=None):    
    # Get parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('displayUSImage: Failed to get parameter node')
      return

    # Get image name from parameter node
    usImageName = parameterNode.GetParameter(self.trainUsWidget.logic.usImageNameParameterName)

    # Get volume and display node
    try:
      # Get volume node
      usImageVolumeNode = slicer.util.getNode(usImageName)
      # Get display node
      usImageDisplayNode = usImageVolumeNode.GetDisplayNode()
    except:
      logging.error('Ultrasound image not found in current scene...')
      return

    # Get min and max level
    minLevel = usImageDisplayNode.GetWindowLevelMin()
    maxLevel = usImageDisplayNode.GetWindowLevelMax()

    # Update slider
    self.moduleWidget.ui.brightnessSliderWidget.setMinimumValue(minLevel)
    self.moduleWidget.ui.brightnessSliderWidget.setMaximumValue(maxLevel)

  #------------------------------------------------------------------------------
  def updateBrightnessContrastInteraction(self, custom):
    if custom:
      # Change to AdjustWindowLevel interaction mode
      slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(slicer.vtkMRMLInteractionNode.AdjustWindowLevel)
      # Add observer to mouse movement
      self.crosshairNode = slicer.util.getNode("Crosshair")
      self.mouseObserverID = self.crosshairNode.AddObserver(slicer.vtkMRMLCrosshairNode.CursorPositionModifiedEvent, self.getImageMinMaxLevel)
    else:
      # Change to normal interaction mode
      slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(slicer.vtkMRMLInteractionNode.ViewTransform)
      # Remove observer to mouse movement
      if self.crosshairNode and self.mouseObserverID:
        self.crosshairNode.RemoveObserver(self.mouseObserverID)
    

#------------------------------------------------------------------------------
#
# UltrasoundDisplaySettingsTest
#
#------------------------------------------------------------------------------
class UltrasoundDisplaySettingsTest(ScriptedLoadableModuleTest):
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
class UltrasoundDisplaySettingsFileWriter(object):
  def __init__(self, parent):
    pass

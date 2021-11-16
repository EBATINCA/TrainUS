import vtk, qt, ctk, slicer
import os
import numpy as np

from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

import logging

#------------------------------------------------------------------------------
#
# UltrasoundDisplaySettings
#
#------------------------------------------------------------------------------
class UltrasoundDisplaySettings(ScriptedLoadableModule):
  
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
    # Display US image
    usImageDisplayed = self.logic.displayUSImage()

    # Setup plus remote node
    if usImageDisplayed:
      remoteControlAvailable = self.setupPlusRemote()
      self.updateUltrasoundParametersGroupBoxState(remoteControlAvailable)

    # Setup brightness slider range
    if usImageDisplayed:
      [minVal, maxVal] = self.logic.getImageMinMaxIntensity()
      self.updateBrightnessSliderRange(minVal, maxVal)

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def setupUi(self):
    
    # Load widget from .ui file (created by Qt Designer).
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/UltrasoundDisplaySettings.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Create parameter sliders
    ultrasoundParametersFrame = qt.QFrame()
    ultrasoundParametersLayout = qt.QFormLayout(ultrasoundParametersFrame)
    self.ui.parametersGroupBox.layout().addWidget(ultrasoundParametersFrame)

    self.depthSlider = slicer.qSlicerUltrasoundDoubleParameterSlider()
    self.depthSlider.setParameterName("DepthMm")
    self.depthSlider.setSuffix(" mm")
    self.depthSlider.setMinimum(10.0)
    self.depthSlider.setMaximum(150.0)
    self.depthSlider.setSingleStep(1.0)
    self.depthSlider.setPageStep(10.0)
    ultrasoundParametersLayout.addRow("Depth:",  self.depthSlider)

    self.gainSlider = slicer.qSlicerUltrasoundDoubleParameterSlider()
    self.gainSlider.setParameterName("GainPercent")
    self.gainSlider.setSuffix("%")
    self.gainSlider.setMinimum(0.0)
    self.gainSlider.setMaximum(100.0)
    self.gainSlider.setSingleStep(1.0)
    self.gainSlider.setPageStep(10.0)
    ultrasoundParametersLayout.addRow("Gain:", self.gainSlider)

    self.frequencySlider = slicer.qSlicerUltrasoundDoubleParameterSlider()
    self.frequencySlider.setParameterName("FrequencyMhz")
    self.frequencySlider.setSuffix(" MHz")
    self.frequencySlider.setMinimum(2.0)
    self.frequencySlider.setMaximum(5.0)
    self.frequencySlider.setSingleStep(0.5)
    self.frequencySlider.setPageStep(1.0)
    ultrasoundParametersLayout.addRow("Frequency:", self.frequencySlider)

    self.dynamicRangeSlider = slicer.qSlicerUltrasoundDoubleParameterSlider()
    self.dynamicRangeSlider.setParameterName("DynRangeDb")
    self.dynamicRangeSlider.setSuffix(" dB")
    self.dynamicRangeSlider.setMinimum(10.0)
    self.dynamicRangeSlider.setMaximum(100.0)
    self.dynamicRangeSlider.setSingleStep(1.0)
    self.dynamicRangeSlider.setPageStep(10.0)
    ultrasoundParametersLayout.addRow("Dynamic Range:", self.dynamicRangeSlider)

    self.powerSlider = slicer.qSlicerUltrasoundDoubleParameterSlider()
    self.powerSlider.setParameterName("PowerDb")
    self.powerSlider.setSuffix("Db")
    self.powerSlider.setMinimum(-20.0)
    self.powerSlider.setMaximum(0.0)
    self.powerSlider.setSingleStep(1.0)
    self.powerSlider.setPageStep(5.0)
    ultrasoundParametersLayout.addRow("Power:", self.powerSlider)

    self.focusDepthSlider = slicer.qSlicerUltrasoundDoubleParameterSlider()
    self.focusDepthSlider.setParameterName("FocusDepthPercent")
    self.focusDepthSlider.setSuffix("%")
    self.focusDepthSlider.setMinimum(0)
    self.focusDepthSlider.setMaximum(100)
    self.focusDepthSlider.setSingleStep(3)
    self.focusDepthSlider.setPageStep(10)
    ultrasoundParametersLayout.addRow("Focus Zone:", self.focusDepthSlider)

    self.parameterWidgets = [
    self.depthSlider,
    self.gainSlider,
    self.frequencySlider,
    self.dynamicRangeSlider,
    self.powerSlider,
    self.focusDepthSlider
    ]

    # Customize widgets
    self.ui.connectionStatusLabel.text = '-'
    self.ui.sliceControllerVisibilityCheckBox.checked = True
    self.ui.freezeUltrasoundButton.setText('Un-freeze')
    self.ui.fitUltrasoundButton.setText('Fit')
    self.ui.flipUltrasoundButton.setText('Un-flip')

  #------------------------------------------------------------------------------
  def updateUltrasoundParametersGroupBoxState(self, active):
    self.ui.parametersGroupBox.visible = active

  #------------------------------------------------------------------------------
  def updateBrightnessSliderRange(self, minVal, maxVal):
    absRange = abs(maxVal - minVal)
    intensityMargin = 0.25 * absRange # 25% margin
    self.ui.brightnessSliderWidget.minimum = minVal - intensityMargin
    self.ui.brightnessSliderWidget.maximum = maxVal + intensityMargin

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
  def setupPlusRemote(self):
    # Get parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('setupPlusRemote: Failed to get parameter node')
      return

    # Get IGTL connector node
    igtlConnectorNodeID = parameterNode.GetParameter(self.trainUsWidget.logic.igtlConnectorNodeIDParameterName)  
    self.igtlConnectorNode = slicer.mrmlScene.GetNodeByID(igtlConnectorNodeID)
    if self.igtlConnectorNode is None:
      logging.error('setupPlusRemote: IGTL connector node was not found')
      return

    # Plus remote node
    self.plusRemoteNode = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLPlusRemoteNode')
    if self.plusRemoteNode is None:
      self.plusRemoteNode = slicer.vtkMRMLPlusRemoteNode()
      self.plusRemoteNode.SetName("PlusRemoteNode")
      slicer.mrmlScene.AddNode(self.plusRemoteNode)

    # Observe connector node
    self.plusRemoteNode.SetAndObserveOpenIGTLinkConnectorNode(self.igtlConnectorNode)
    for widget in self.parameterWidgets:
      widget.setConnectorNode(self.igtlConnectorNode)

    # Search for video device for remote control
    if (self.igtlConnectorNode.GetState() == slicer.vtkMRMLIGTLConnectorNode.StateConnected):
      self.plusRemoteNode.SetDeviceIDType("")
      slicer.modules.plusremote.logic().RequestDeviceIDs(self.plusRemoteNode)
    deviceIDs = vtk.vtkStringArray()
    self.plusRemoteNode.GetDeviceIDs(deviceIDs)
    ultrasoundDeviceID = 'VideoDevice'
    remoteControlAvailable = False
    for valueIndex in range(deviceIDs.GetNumberOfValues()):
      deviceID = deviceIDs.GetValue(valueIndex)
      if deviceID == ultrasoundDeviceID:
        remoteControlAvailable = True

    # Set ultrasound device ID for remote control
    if remoteControlAvailable:
      self.plusRemoteNode.SetCurrentDeviceID(ultrasoundDeviceID)
      for widget in self.parameterWidgets:
        widget.setDeviceID(ultrasoundDeviceID)
    else:
      slicer.mrmlScene.RemoveNode(self.plusRemoteNode)
      logging.warning('WARNING: Current device is not compatible with US remote control.')

    return remoteControlAvailable

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

    # Current US device
    deviceName = parameterNode.GetParameter(self.trainUsWidget.logic.selectedUltrasoundDeviceParameterName)
    self.ui.deviceNameLabel.text = deviceName

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
      return False

    # Get image name from parameter node
    usImageName = parameterNode.GetParameter(self.trainUsWidget.logic.usImageNameParameterName)

    # Volume reslice driver
    try:
      volumeResliceDriverLogic = slicer.modules.volumereslicedriver.logic()
    except:
      logging.error('Volume Reslice Driver module was not found.')
      return False

    # Check US image availability
    if not self.isUSImageAvailable():
      return False

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

    return True

  #------------------------------------------------------------------------------
  def isUSImageAvailable(self):    
    # Get parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('isUSImageAvailable: Failed to get parameter node')
      return

    # Get image name from parameter node
    usImageName = parameterNode.GetParameter(self.trainUsWidget.logic.usImageNameParameterName)

    # Get US volume from name
    try:
      usImageVolumeNode = slicer.util.getNode(usImageName)
      self.updateSliceViewText('') # Delete corner annotation within slice view
    except:
      self.updateSliceViewText('No image is available.') # Show corner annotation within slice view
      return False
    return True

  #------------------------------------------------------------------------------
  def updateSliceControllerVisibility(self, visible):
    # Update visibility of slice controllers
    for name in slicer.app.layoutManager().sliceViewNames():
      sliceWidget = slicer.app.layoutManager().sliceWidget(name)
      sliceWidget.sliceController().setVisible(visible)

  #------------------------------------------------------------------------------
  def updateSliceViewText(self, text):
    # Update visibility of slice controllers
    for name in slicer.app.layoutManager().sliceViewNames():
      view = slicer.app.layoutManager().sliceWidget(name).sliceView()
      view.cornerAnnotation().SetText(vtk.vtkCornerAnnotation.UpperLeft, text)
      view.cornerAnnotation().GetTextProperty().SetColor(1,1,1)
      view.forceRender()

  #------------------------------------------------------------------------------
  def freezeUltrasoundImage(self):
    # Get parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('freezeUltrasoundImage: Failed to get parameter node')
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
      logging.error('setImageMinMaxLevel: Failed to get parameter node')
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
      logging.error('getImageMinMaxLevel: Failed to get parameter node')
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
  def getImageMinMaxIntensity(self):    
    # Get parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('getImageMinMaxLevel: Failed to get parameter node')
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

    # Get image array
    usImageArray = slicer.util.arrayFromVolume(usImageVolumeNode)

    # Get max and min intensity values
    minVal = np.min(usImageArray)
    maxVal = np.max(usImageArray)

    return (minVal, maxVal)
    

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

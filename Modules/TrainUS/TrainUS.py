import vtk, qt, ctk, slicer
import os

from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
# from Resources import TrainUSResourcesResources

import logging

import Managers

try:
  #TODO: Contribute this to PerkTutor (PerkTutorCouchDB.py, line 8)
  import couchdb # For PerkTutor
except: # pylint: disable=w0702
  qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)
  logging.info('Installing couchdb...')
  slicer.util.pip_install('couchdb')
  logging.info('Installing couchdb finished')
  qt.QApplication.restoreOverrideCursor()

#------------------------------------------------------------------------------
#
# TrainUS
#
#------------------------------------------------------------------------------
class TrainUS(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "TrainUS"
    self.parent.categories = ["TrainUS"]
    self.parent.dependencies = []
    self.parent.contributors = ["Csaba Pinter (Ebatinca), David Garcia Mato (Ebatinca)"]
    self.parent.helpText = """The entry module for the TrainUS custom application"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """EBATINCA, S.L.""" # replace with organization, grant and thanks.

#------------------------------------------------------------------------------
#
# TrainUSWidget
#
#------------------------------------------------------------------------------
class TrainUSWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)

    # Create logic class
    self.logic = TrainUSLogic(self)

  #------------------------------------------------------------------------------
  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Launcher panel
    launcherCollapsibleButton = ctk.ctkCollapsibleButton()
    launcherCollapsibleButton.text = "Slicelet launcher"
    self.layout.addWidget(launcherCollapsibleButton)
    self.launcherFormLayout = qt.QFormLayout(launcherCollapsibleButton)

    # Show Home widget button
    self.showHomeButton = qt.QPushButton("Switch to Home")
    self.showHomeButton.toolTip = "Switch to the TrainUS application home dashboard"
    self.launcherFormLayout.addWidget(self.showHomeButton)
    self.showHomeButton.connect('clicked()', lambda: slicer.util.selectModule('Home'))

    # Add vertical spacer
    self.layout.addStretch(1)

    # Add slicer variable for global access of this central class
    slicer.trainUsWidget = self

    # Remove unneeded UI elements
    self.modifyWindowUI()

    # Setup connections
    self.setupConnections()

    # Apply style
    self.applyApplicationStyle()

    # Avoid style to be applied by default
    self.settingsUI.CustomStyleCheckBox.checked = False

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

  #------------------------------------------------------------------------------
  def setupConnections(self):
    pass

  #------------------------------------------------------------------------------
  def disconnect(self):
    pass

  #------------------------------------------------------------------------------
  def hideSlicerUI(self):
    slicer.util.setDataProbeVisible(False)
    slicer.util.setMenuBarsVisible(False, ignore=['MainToolBar', 'ViewToolBar'])
    slicer.util.setModuleHelpSectionVisible(False)
    slicer.util.setModulePanelTitleVisible(False)
    slicer.util.setPythonConsoleVisible(False)
    slicer.util.setToolbarsVisible(True)
    mainToolBar = slicer.util.findChild(slicer.util.mainWindow(), 'MainToolBar')
    keepToolbars = [
      slicer.util.findChild(slicer.util.mainWindow(), 'MainToolBar'),
      slicer.util.findChild(slicer.util.mainWindow(), 'ViewToolBar'),
      slicer.util.findChild(slicer.util.mainWindow(), 'CustomToolBar'),
      ]
    slicer.util.setToolbarsVisible(False, keepToolbars)

  #------------------------------------------------------------------------------
  def showSlicerUI(self):
    slicer.util.setDataProbeVisible(True)
    slicer.util.setMenuBarsVisible(True)
    slicer.util.setModuleHelpSectionVisible(True)
    slicer.util.setModulePanelTitleVisible(True)
    slicer.util.setPythonConsoleVisible(True)
    slicer.util.setToolbarsVisible(True)

  #------------------------------------------------------------------------------
  def modifyWindowUI(self):
    slicer.util.setModuleHelpSectionVisible(False)

    mainToolBar = slicer.util.findChild(slicer.util.mainWindow(), 'MainToolBar')

    self.CustomToolBar = qt.QToolBar("CustomToolBar")
    self.CustomToolBar.name = "CustomToolBar"
    slicer.util.mainWindow().insertToolBar(mainToolBar, self.CustomToolBar)

    # central = slicer.util.findChild(slicer.util.mainWindow(), name='CentralWidget')
    # central.setStyleSheet("background-color: #464449")

    gearIcon = qt.QIcon(self.resourcePath('Icons/Gears.png'))
    self.settingsAction = self.CustomToolBar.addAction(gearIcon, "")

    self.settingsDialog = slicer.util.loadUI(self.resourcePath('UI/Settings.ui'))
    self.settingsUI = slicer.util.childWidgetVariables(self.settingsDialog)

    self.settingsUI.CustomUICheckBox.toggled.connect(self.toggleUI)
    self.settingsUI.CustomStyleCheckBox.toggled.connect(self.toggleStyle)

    self.settingsAction.triggered.connect(self.raiseSettings)
    self.hideSlicerUI()

  #------------------------------------------------------------------------------
  def toggleStyle(self,visible):
    if visible:
      self.applyApplicationStyle()
    else:
      slicer.app.styleSheet = ''

  #------------------------------------------------------------------------------
  def toggleUI(self, visible):
    if visible:
      self.hideSlicerUI()
    else:
      self.showSlicerUI()

  #------------------------------------------------------------------------------
  def raiseSettings(self, unused):
    self.settingsDialog.exec()

  #------------------------------------------------------------------------------
  def applyApplicationStyle(self):
    # Style
    self.applyStyle([slicer.app], 'TrainUS.qss')

  #------------------------------------------------------------------------------
  def applyStyle(self, widgets, styleSheetName):
    stylesheetfile = self.resourcePath(styleSheetName)
    with open(stylesheetfile,"r") as fh:
      style = fh.read()
      for widget in widgets:
        widget.styleSheet = style

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
    parameterNode = self.logic.getParameterNode()
    if not parameterNode:
      logging.error('updateGUIFromMRML: Failed to get parameter node')
      return


#---------------------------------------------------------------------------------------------#
#                                                                                             #
#                                                                                             #
#                                                                                             #
#                                       TrainUSLogic                                          #
#                                                                                             #
#                                                                                             #
#                                                                                             #
#---------------------------------------------------------------------------------------------#
class TrainUSLogic(ScriptedLoadableModuleLogic, VTKObservationMixin):
  """This class should implement all the actual computation done by your module.  The interface
  should be such that other python code can import this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, widgetInstance, parent=None):
    ScriptedLoadableModuleLogic.__init__(self, parent)
    VTKObservationMixin.__init__(self)

    # Define member variables
    self.fileDir = os.path.dirname(__file__)
    # Only defined in case there is no other way but having to use the widget from the logic
    self.moduleWidget = widgetInstance
    # Pointer to the parameter node so that we have access to the old one before setting the new one
    self.parameterNode = None

    # Constants
    self.rootDirectoryPath = self.setupRootDirectory()
    self.deviceDirectoryPath = os.path.join(self.moduleWidget.resourcePath(''), 'Devices')

    # Data manager to handle participants and recordings
    self.recordingManager = Managers.RecordingManager()
    self.recordingManager.setRootDirectory(self.rootDirectoryPath)

    # Device manager to access device info
    self.deviceManager = Managers.DeviceManager()
    self.deviceManager.setMainDirectory(self.deviceDirectoryPath)

    # Hardware configurations
    self.ultrasoundDeviceOptions = ['None', 'Simulated US - Linear Probe', 'Simulated US - Convex Probe', 'Telemed MicrUS - Linear Probe', 'Telemed MicrUS - Convex Probe']
    self.trackingSystemOptions = ['None', 'Optitrack Duo (OTS)', 'trakSTAR 3D Guidance (EMTS)']
    self.simulationPhantomOptions = ['None', 'Soft biopsy phantom', 'Vascular access phantom']

    # Default parameters map
    self.defaultParameters = {}
    self.defaultParameters["AppMode"] = '0'
    self.defaultParameters["SelectedParticipantID"] = ''
    self.defaultParameters["SelectedRecordingID"] = ''
    self.defaultParameters["SelectedUltrasoundDevice"] = self.ultrasoundDeviceOptions[1]
    self.defaultParameters["SelectedTrackingSystem"] = self.trackingSystemOptions[0]
    self.defaultParameters["SelectedSimulationPhantom"] = self.simulationPhantomOptions[0]
    self.defaultParameters["UltrasoundImageName"] = 'Image_Reference'
    self.defaultParameters["UltrasoundPlusServerPort"] = '18944'
    self.defaultParameters["UltrasoundPlusConfigPath"] = ''
    self.defaultParameters["UltrasoundPlusConfigTextNodeID"] = ''
    self.defaultParameters["TrackerPlusServerPort"] = '18945'
    self.defaultParameters["TrackerPlusConfigPath"] = ''
    self.defaultParameters["TrackerPlusConfigTextNodeID"] = ''
    self.defaultParameters["PlusServerRunning"] = 'False'
    self.defaultParameters["PlusServerPath"] = ''
    self.defaultParameters["PlusServerLauncherPath"] = ''
    self.defaultParameters["PlusConnectionStatus"] = 'OFF'
    self.defaultParameters["IGTLConnectionStatus"] = 'OFF'
    self.defaultParameters["IGTLConnectorNodeID"] = ''

    # Parameter node reference roles
    # self.modelReferenceRolePrefix = 'Model_'

    # Parameter node parameter names
    self.selectedAppModeParameterName = 'AppMode'
    self.selectedParticipantIDParameterName = 'SelectedParticipantID'
    self.selectedRecordingIDParameterName = 'SelectedRecordingID'
    self.selectedUltrasoundDeviceParameterName = 'SelectedUltrasoundDevice'
    self.selectedTrackingSystemParameterName = 'SelectedTrackingSystem'
    self.selectedSimulationPhantomParameterName = 'SelectedSimulationPhantom'
    self.usImageNameParameterName = 'UltrasoundImageName'
    self.usPlusServerPortParameterName = 'UltrasoundPlusServerPort'
    self.usPlusConfigPathParameterName = 'UltrasoundPlusConfigPath'
    self.usPlusConfigTextNodeIDParameterName = 'UltrasoundPlusConfigTextNodeID'
    self.trackerPlusServerPortParameterName = 'TrackerPlusServerPort'
    self.trackerPlusConfigPathParameterName = 'TrackerPlusConfigPath'
    self.trackerPlusConfigTextNodeIDParameterName = 'TrackerPlusConfigTextNodeID'
    self.plusServerRunningParameterName = 'PlusServerRunning'
    self.plusServerPathParameterName = 'PlusServerPath'
    self.plusServerLauncherPathParameterName = 'PlusServerLauncherPath'
    self.plusConnectionStatusParameterName = 'PlusConnectionStatus'
    self.igtlConnectionStatusParameterName = 'IGTLConnectionStatus'
    self.igtlConnectorNodeIDParameterName = 'IGTLConnectorNodeID'

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
    self.setup3DView()
    self.setupSliceViewers()

  #------------------------------------------------------------------------------
  def setup3DView(self):
    layoutManager = slicer.app.layoutManager()
    # layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView)
    # controller = slicer.app.layoutManager().threeDWidget(0).threeDController()
    # controller.setBlackBackground()
    # controller.set3DAxisVisible(False)
    # controller.set3DAxisLabelVisible(False)
    # controller.setOrientationMarkerType(3)  #Axis marker
    # controller.setStyleSheet("background-color: #000000")

  #------------------------------------------------------------------------------
  def setupSliceViewers(self):
    for name in slicer.app.layoutManager().sliceViewNames():
        sliceWidget = slicer.app.layoutManager().sliceWidget(name)
        self.setupSliceViewer(sliceWidget)

    # Set linked slice views  in all existing slice composite nodes and in the default node
    sliceCompositeNodes = slicer.util.getNodesByClass('vtkMRMLSliceCompositeNode')
    defaultSliceCompositeNode = slicer.mrmlScene.GetDefaultNodeByClass('vtkMRMLSliceCompositeNode')
    if not defaultSliceCompositeNode:
      defaultSliceCompositeNode = slicer.mrmlScene.CreateNodeByClass('vtkMRMLSliceCompositeNode')
      defaultSliceCompositeNode.UnRegister(None)  # CreateNodeByClass is factory method, need to unregister the result to prevent memory leaks
      slicer.mrmlScene.AddDefaultNode(defaultSliceCompositeNode)
    sliceCompositeNodes.append(defaultSliceCompositeNode)
    for sliceCompositeNode in sliceCompositeNodes:
      sliceCompositeNode.SetLinkedControl(True)

  #Settings for slice views
  def setupSliceViewer(self, sliceWidget):
    controller = sliceWidget.sliceController()
    # controller.setOrientationMarkerType(3)  #Axis marker
    # controller.setRulerType(1)  #Thin ruler
    # controller.setRulerColor(0) #White ruler
    # controller.setStyleSheet("background-color: #000000")
    # controller.sliceViewLabel = ''

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
  def setupRootDirectory(self):
    # Get internal path
    slicerUserSettingsDirectory = os.path.dirname(slicer.app.slicerUserSettingsFilePath)
    # Create folder if it does not exist
    dataFolderName = 'TrainUS_Database'
    rootDirectory = os.path.join(slicerUserSettingsDirectory, dataFolderName)
    try:
      os.makedirs(rootDirectory)
      logging.debug('Root directory was created at %s' % rootDirectory)
    except FileExistsError:
      logging.debug('Root directory already exists...')
    return rootDirectory


#------------------------------------------------------------------------------
#
# TrainUSTest
#
#------------------------------------------------------------------------------
class TrainUSTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_TrainUS1()

  def test_TrainUS1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #

    logic = TrainUSLogic()
    self.delayDisplay('Test passed!')


#
# Class for avoiding python error that is caused by the method SegmentEditor::setup
# http://issues.slicer.org/view.php?id=3871
#
class TrainUSFileWriter(object):
  def __init__(self, parent):
    pass

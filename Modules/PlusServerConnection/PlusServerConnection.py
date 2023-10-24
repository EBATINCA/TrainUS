import vtk, qt, ctk, slicer
import os
import subprocess
import time
import logging
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

# TrainUS parameters
import TrainUSLib.TrainUSParameters as Parameters

#------------------------------------------------------------------------------
#
# PlusServerConnection
#
#------------------------------------------------------------------------------
class PlusServerConnection(ScriptedLoadableModule):
  
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "PlusServerConnection"
    self.parent.categories = ["TrainUS"]
    self.parent.dependencies = []
    self.parent.contributors = ["David Garcia Mato (Ebatinca), Csaba Pinter (Ebatinca)"]
    self.parent.helpText = """ Module to establish connection with PLUS server. """
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """This project has been funded by NEOTEC grant from the Centre for the Development of Technology and Innovation (CDTI) of the Ministry for Science and Innovation of the Government of Spain."""

#------------------------------------------------------------------------------
#
# PlusServerConnectionWidget
#
#------------------------------------------------------------------------------
class PlusServerConnectionWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  
  def __init__(self, parent):
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)

    # Create logic class
    self.logic = PlusServerConnectionLogic(self)

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
    self.logic.stopPlusConnection() # stop PLUS server subprocess
    self.disconnect()

    # Terminate Plus Server Launcher if running
    if self.logic.plusServerLauncherRunning:
      self.logic.stopPlusServerLauncher()

    # Remove observers to connector node
    if self.logic.connector:
      self.removeObserver(self.logic.connector, slicer.vtkMRMLIGTLConnectorNode.ConnectedEvent, self.logic.getIGTLConnectionStatus)
      self.removeObserver(self.logic.connector, slicer.vtkMRMLIGTLConnectorNode.DisconnectedEvent, self.logic.getIGTLConnectionStatus)
      self.removeObserver(self.logic.connector, slicer.vtkMRMLIGTLConnectorNode.ActivatedEvent, self.logic.getIGTLConnectionStatus)
      self.removeObserver(self.logic.connector, slicer.vtkMRMLIGTLConnectorNode.DeactivatedEvent, self.logic.getIGTLConnectionStatus) 

  #------------------------------------------------------------------------------
  def enter(self):
    """
    Runs when reopening the module.
    """
    self.logic.setParameterNode()
    self.updateSliceWidgetVisibility(False)

    # Update IGTL connection status
    self.logic.getIGTLConnectionStatus()

  #------------------------------------------------------------------------------
  def exit(self):
    """
    Runs when exiting the module.
    """
    self.updateSliceWidgetVisibility(True)

  #------------------------------------------------------------------------------
  def updateSliceWidgetVisibility(self, visible):
    for name in slicer.app.layoutManager().sliceViewNames():
      sliceWidget = slicer.app.layoutManager().sliceWidget(name)
      sliceWidget.visible = visible

  #------------------------------------------------------------------------------
  def setupUi(self):
    
    # Load widget from .ui file (created by Qt Designer).
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/PlusServerConnection.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Customize widgets
    self.ui.plusConnectionStatusLabel.text = 'OFF'
    self.ui.igtlConnectionStatusLabel.text = '-'
    self.ui.startConnectionButton.enabled = True
    self.ui.stopConnectionButton.enabled = False
    self.ui.refreshButton.setIcon(qt.QIcon(':/Icons/Small/SlicerCheckForUpdates.png'))
    self.ui.refreshButton.minimumWidth = self.ui.refreshButton.sizeHint.height()

  #------------------------------------------------------------------------------
  def setupConnections(self):
    self.ui.startConnectionButton.clicked.connect(self.onStartConnectionButtonClicked)
    self.ui.stopConnectionButton.clicked.connect(self.onStopConnectionButtonClicked)
    self.ui.refreshButton.clicked.connect(self.onRefreshButtonClicked)
    self.ui.backToMenuButton.clicked.connect(self.onBackToMenuButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    self.ui.startConnectionButton.clicked.disconnect()
    self.ui.stopConnectionButton.clicked.disconnect()
    self.ui.refreshButton.clicked.disconnect()
    self.ui.backToMenuButton.clicked.disconnect()

  #------------------------------------------------------------------------------
  def updateGUIFromMRML(self, caller=None, event=None):
    """
    Set selections and other settings on the GUI based on the parameter node.

    Calls the updateGUIFromMRML function of all tabs so that they can take care of their own GUI.
    """
    parameterNode = Parameters.instance.getParameterNode()
    # PLUS server connection status
    plusConnectionStatus = parameterNode.GetParameter(self.trainUsWidget.logic.plusConnectionStatusParameterName) #TODO: Move to parameter class
    plusConnectionStatus = Parameters.instance.getParameterString(Parameters.PLUS_CONNECTION_STATUS)
    self.ui.plusConnectionStatusLabel.text = plusConnectionStatus

    # Start/stop buttons
    if plusConnectionStatus == 'ON':
      self.ui.startConnectionButton.enabled = False
      self.ui.stopConnectionButton.enabled = True
    else:
      self.ui.startConnectionButton.enabled = True
      self.ui.stopConnectionButton.enabled = False

    # IGTL connection status
    igtlConnectionStatus = Parameters.instance.getParameterString(Parameters.IGTL_CONNECTION_STATUS)
    self.ui.igtlConnectionStatusLabel.text = igtlConnectionStatus

    # Update list of incoming nodes
    tableWidget = self.ui.incomingNodesTable
    tableWidget.clearContents() # reset table
    numIncomingNodes = len(self.logic.incomingNodesNames)
    tableWidget.setRowCount(numIncomingNodes)
    for nodeIndex in range(numIncomingNodes):
      nodeNameTableItem = qt.QTableWidgetItem(self.logic.incomingNodesNames[nodeIndex])
      nodeTypeTableItem = qt.QTableWidgetItem(self.logic.incomingNodesTypes[nodeIndex])
      tableWidget.setItem(nodeIndex, 0, nodeNameTableItem)
      tableWidget.setItem(nodeIndex, 1, nodeTypeTableItem)

  #------------------------------------------------------------------------------
  def onStartConnectionButtonClicked(self):
    # Set wait cursor
    qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)

    # Disable button
    self.ui.startConnectionButton.enabled = False

    # Create message window to indicate to user what is happening
    progressDialog = self.showProgressDialog()
    progressDialog.show()

    # Execute Plus Server Launcher if not running
    windowVisible = True
    if not self.logic.plusServerLauncherRunning:
      # Start connection with PLUS server
      self.logic.startPlusServerLauncher(windowVisible, progressDialog)

    # Load config file
    self.logic.loadPlusConfigFile()

    # Start connection with PLUS server
    self.logic.startPlusConnection(progressDialog)

    # Restore cursor and hide dialog
    qt.QApplication.restoreOverrideCursor()
    progressDialog.hide()
    progressDialog.deleteLater()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onStopConnectionButtonClicked(self):
    # Set wait cursor
    qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)

    # Disable button
    self.ui.stopConnectionButton.enabled = False

    # Create message window to indicate to user what is happening
    progressDialog = self.showProgressDialog()
    progressDialog.show()

    # Stop connection with PLUS server
    self.logic.stopPlusConnection(progressDialog)

    # Restore cursor and hide dialog
    qt.QApplication.restoreOverrideCursor()
    progressDialog.hide()
    progressDialog.deleteLater()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onRefreshButtonClicked(self):
    
    # Refresh connection status
    self.logic.getIGTLConnectionStatus()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onBackToMenuButtonClicked(self):
    # Go back to Home module
    slicer.util.selectModule('Home') 

  #------------------------------------------------------------------------------
  def showProgressDialog(self):
    """
    Show progress dialog with label for long processes.
    """
    progressDialog = qt.QProgressDialog('Loading...', 'Cancel', 0, 100, slicer.util.mainWindow())
    progressDialog.setCancelButton(None) # hide cancel button in dialog
    progressDialog.setMinimumWidth(300) # dialog size
    font = qt.QFont()
    font.setPointSize(12)
    progressDialog.setFont(font) # font size
    progressDialog.show()
    slicer.app.processEvents()
    return progressDialog


#---------------------------------------------------------------------------------------------#
#                                                                                             #
#                                                                                             #
#                                                                                             #
#                                       PlusServerConnectionLogic                                          #
#                                                                                             #
#                                                                                             #
#                                                                                             #
#---------------------------------------------------------------------------------------------#
class PlusServerConnectionLogic(ScriptedLoadableModuleLogic, VTKObservationMixin):
  
  def __init__(self, widgetInstance, parent=None):
    ScriptedLoadableModuleLogic.__init__(self, parent)
    VTKObservationMixin.__init__(self)

    # Define member variables
    self.fileDir = os.path.dirname(__file__)
    # Only defined in case there is no other way but having to use the widget from the logic
    self.moduleWidget = widgetInstance
    self.trainUsWidget = slicer.trainUsWidget

    # PLUS connection variables
    self.plusServerLauncherRunning = False
    self.incomingNodesNames = list()
    self.incomingNodesTypes = list()
    self.plusServerLauncherNode = None
    self.plusServerLauncherSubprocess = None
    self.ultrasoundPlusServerNode = None
    self.trackerPlusServerNode = None
    self.ultrasoundConnector = None
    self.trackerConnector = None

    # Setup scene
    self.setupScene()

    # Setup keyboard shortcuts
    self.setupKeyboardShortcuts()

  #------------------------------------------------------------------------------
  def setParameterNode(self):
    # Get parameter node
    parameterNode = Parameters.instance.getParameterNode()
    if not parameterNode:
      logging.error('setParameterNode: Failed to get parameter node')
      return

    # Remove observations from nodes referenced in the old parameter node
    if parameterNode is not None:
      self.removeObserver(parameterNode, vtk.vtkCommand.ModifiedEvent, self.moduleWidget.updateGUIFromMRML)

    # Add observations on referenced nodes
    if parameterNode:
      self.addObserver(parameterNode, vtk.vtkCommand.ModifiedEvent, self.moduleWidget.updateGUIFromMRML)  

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
  def isUltrasoundDeviceSelectionValid(self):
    # Get parameter node
    parameterNode = Parameters.instance.getParameterNode()
    if not parameterNode:
      logging.error('isUltrasoundDeviceSelectionValid: Failed to get parameter node')
      return


    # Get config file path
    ultrasoundPlusConfigPath = Parameters.instance.getParameterString(Parameters.ULTRASOUND_PLUS_CONFIG_PATH)
    return os.path.isfile(ultrasoundPlusConfigPath)

  #------------------------------------------------------------------------------
  def isTrackerDeviceSelectionValid(self):
    # Get parameter node
    # Get parameter node
    parameterNode = Parameters.instance.getParameterNode()
    if not parameterNode:
      logging.error('isTrackerDeviceSelectionValid: Failed to get parameter node')
      return

    # Get config file path
    trackerPlusConfigPath = Parameters.instance.getParameterString(Parameters.TRACKER_PLUS_CONFIG_PATH)
    return os.path.isfile(trackerPlusConfigPath)

  #------------------------------------------------------------------------------
  def loadPlusConfigFile(self):
    # Get parameter node
    parameterNode = Parameters.instance.getParameterNode()
    if not parameterNode:
      logging.error('loadPlusConfigFile: Failed to get parameter node')
      return

    #
    # Ultrasound device
    #
    if self.isUltrasoundDeviceSelectionValid():
      # Get config path and text node ID
      ultrasoundPlusConfigPath = Parameters.instance.getParameterString(Parameters.ULTRASOUND_PLUS_CONFIG_PATH)
      ultrasoundPlusConfigTextNodeID = Parameters.instance.getParameterString(Parameters.ULTRASOUND_PLUS_CONFIG_TEXTNODEID)
      
      # Get config file text node
      self.ultrasoundPlusConfigTextNode = slicer.mrmlScene.GetNodeByID(ultrasoundPlusConfigTextNodeID)
      if self.ultrasoundPlusConfigTextNode:
        slicer.mrmlScene.RemoveNode(self.ultrasoundPlusConfigTextNode)
      self.ultrasoundPlusConfigTextNode = slicer.util.loadText(ultrasoundPlusConfigPath) # load XML as text node
      self.ultrasoundPlusConfigTextNode.SetName('Ultrasound_Plus_Config_File')

      # Add node ID to parameter node
      Parameters.instance.setParameter(Parameters.ULTRASOUND_PLUS_CONFIG_TEXTNODEID, self.ultrasoundPlusConfigTextNode.GetID())

    #
    # Tracker device
    #
    if self.isTrackerDeviceSelectionValid():
      # Get config path and text node ID
      trackerPlusConfigPath = Parameters.instance.getParameterString(Parameters.TRACKER_PLUS_CONFIG_PATH)
      trackerPlusConfigTextNodeID = Parameters.instance.getParameterString(Parameters.TRACKER_PLUS_CONFIG_TEXTNODEID)

      # Get config file text node
      self.trackerPlusConfigTextNode = slicer.mrmlScene.GetNodeByID(trackerPlusConfigTextNodeID)
      if self.trackerPlusConfigTextNode:
        slicer.mrmlScene.RemoveNode(self.trackerPlusConfigTextNode)
      self.trackerPlusConfigTextNode = slicer.util.loadText(trackerPlusConfigPath) # load XML as text node
      self.trackerPlusConfigTextNode.SetName('Tracker_Plus_Config_File')

      # Add node ID to parameter node
      Parameters.instance.setParameter(Parameters.TRACKER_PLUS_CONFIG_TEXTNODEID, self.trackerPlusConfigTextNode.GetID())

  #------------------------------------------------------------------------------
  def startPlusServerLauncher(self, windowVisible = False, progressDialog=None):
    # Get parameter node
    parameterNode = Parameters.instance.getParameterNode()
    if not parameterNode:
      logging.error('startPlusServerLauncher: Failed to get parameter node')
      return

    # Location of PLUS server launcher    
    plusServerLauncherPath = parameterNode.GetParameter(self.trainUsWidget.logic.plusServerLauncherPathParameterName) #TODO: To param class
    plusServerLauncherPath = Parameters.instance.getParameterString(Parameters.PLUS_SERVER_LAUNCHER_PATH)

    # Start PlusServerLauncher.exe
    info = subprocess.STARTUPINFO()
    info.dwFlags = 1
    info.wShowWindow = windowVisible # show Plus Server Launcher window
    self.plusServerLauncherSubprocess = subprocess.Popen(plusServerLauncherPath, startupinfo=info)

    # Activate flag
    self.plusServerLauncherRunning = True

    # Wait
    if progressDialog:
      self.sleepWithProgressDialog(5, progressDialog, 'Starting PLUS launcher. Please wait...')
    else:
      time.sleep(5)

  #------------------------------------------------------------------------------
  def stopPlusServerLauncher(self):
    # Close Plus server launcher
    self.plusServerLauncherSubprocess.terminate()

    # Deactivate flag
    self.plusServerLauncherRunning = False

  #------------------------------------------------------------------------------
  def startPlusConnection(self, progressDialog=None):
    """
    Start connection with PLUS server.
    """
    logging.debug('PlusServerConnection.startPlusConnection')

    # Get parameter node
    parameterNode = Parameters.instance.getParameterNode()
    if not parameterNode:
      logging.error('startPlusConnection: Failed to get parameter node')
      return

    # Create Plus server launcher node
    if not self.plusServerLauncherNode:
      self.plusServerLauncherNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLPlusServerLauncherNode')

    # Connect ultrasound device
    if self.isUltrasoundDeviceSelectionValid():
      # Create Plus server node
      if not self.ultrasoundPlusServerNode:
        self.ultrasoundPlusServerNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlusServerNode")

      # Set plus server and launcher nodes
      self.ultrasoundPlusServerNode.SetAndObserveConfigNode(self.ultrasoundPlusConfigTextNode) 
      self.plusServerLauncherNode.AddAndObserveServerNode(self.ultrasoundPlusServerNode)

      # Start server
      self.ultrasoundPlusServerNode.StartServer()

    # Connect tracker device
    if self.isTrackerDeviceSelectionValid():
      # Create Plus server node
      if not self.trackerPlusServerNode:
        self.trackerPlusServerNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlusServerNode")

      # Set plus server and launcher nodes
      self.trackerPlusServerNode.SetAndObserveConfigNode(self.trackerPlusConfigTextNode) 
      self.plusServerLauncherNode.AddAndObserveServerNode(self.trackerPlusServerNode)

      # Start server
      self.trackerPlusServerNode.StartServer()

    # Wait
    if progressDialog:
      self.sleepWithProgressDialog(5, progressDialog, 'Starting PLUS server. Please wait...')
    else:
      time.sleep(5)

    # Get ultrasound IGTL connector from server port
    ultrasoundConnectorFound = False
    if self.isUltrasoundDeviceSelectionValid():
      usPlusServerPort = int(Parameters.instance.getParameterString(Parameters.ULTRASOUND_PLUS_SERVER_PORT))
      connectorNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLIGTLConnectorNode')
      for connectorNode in connectorNodes:
        serverPort = connectorNode.GetServerPort()
        if serverPort == usPlusServerPort:
          self.ultrasoundConnector = connectorNode
          ultrasoundConnectorFound = True
      if not ultrasoundConnectorFound:
        logging.error('ERROR: Could not find IGTL connector for ultrasound device...')
        self.stopPlusConnection()
        return

    # Get tracker IGTL connector from server port
    trackerConnectorFound = False
    if self.isTrackerDeviceSelectionValid():
      trackerPlusServerPort = int(Parameters.instance.getParameterString(Parameters.TRACKER_PLUS_SERVER_PORT))
      connectorNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLIGTLConnectorNode')
      for connectorNode in connectorNodes:
        serverPort = connectorNode.GetServerPort()
        if serverPort == trackerPlusServerPort:
          self.trackerConnector = connectorNode
          trackerConnectorFound = True
      if not trackerConnectorFound:
        logging.error('ERROR: Could not find IGTL connector for tracker device...')
        self.stopPlusConnection()
        return

    # Add observers to connector nodes
    if self.ultrasoundConnector:
      if not self.ultrasoundConnector.HasObserver(slicer.vtkMRMLIGTLConnectorNode.ConnectedEvent):
        self.addObserver(self.ultrasoundConnector, slicer.vtkMRMLIGTLConnectorNode.ConnectedEvent, self.getIGTLConnectionStatus)
        self.addObserver(self.ultrasoundConnector, slicer.vtkMRMLIGTLConnectorNode.DisconnectedEvent, self.getIGTLConnectionStatus)
        self.addObserver(self.ultrasoundConnector, slicer.vtkMRMLIGTLConnectorNode.ActivatedEvent, self.getIGTLConnectionStatus)
        self.addObserver(self.ultrasoundConnector, slicer.vtkMRMLIGTLConnectorNode.DeactivatedEvent, self.getIGTLConnectionStatus)    
    if self.trackerConnector:
      if not self.trackerConnector.HasObserver(slicer.vtkMRMLIGTLConnectorNode.ConnectedEvent):
        self.addObserver(self.trackerConnector, slicer.vtkMRMLIGTLConnectorNode.ConnectedEvent, self.getIGTLConnectionStatus)
        self.addObserver(self.trackerConnector, slicer.vtkMRMLIGTLConnectorNode.DisconnectedEvent, self.getIGTLConnectionStatus)
        self.addObserver(self.trackerConnector, slicer.vtkMRMLIGTLConnectorNode.ActivatedEvent, self.getIGTLConnectionStatus)
        self.addObserver(self.trackerConnector, slicer.vtkMRMLIGTLConnectorNode.DeactivatedEvent, self.getIGTLConnectionStatus)    

    # Save connector node ID into parameter node
    if ultrasoundConnectorFound:
      Parameters.instance.setParameter(Parameters.ULTRASOUND_IGTL_CONNECTOR_NODE_ID, self.ultrasoundConnector.GetID())
    if trackerConnectorFound:
      Parameters.instance.setParameter(Parameters.TRACKER_IGTL_CONNECTOR_NODE_ID, self.trackerConnector.GetID())

    # Wait
    if progressDialog:
      self.sleepWithProgressDialog(2, progressDialog, 'Getting streamed data. Please wait...')
    else:
      time.sleep(2)

    # Get IGTL connection status
    slicer.app.processEvents()
    self.getIGTLConnectionStatus()

    # Update Plus server status in parameter node
    plusServerConnectionStatus = self.getPlusServerConnectionStatus()
    if (plusServerConnectionStatus == 'ON'):
      logging.debug('Plus Servers were successfully connected.')
      plusServerRunning = True
    else:
      logging.error('ERROR: Plus Servers were not successfully connected.')
      plusServerRunning = False

    # Plus servers running
    Parameters.instance.setParameter(Parameters.PLUS_SERVER_RUNNING, plusServerRunning)

  #------------------------------------------------------------------------------
  def stopPlusConnection(self, progressDialog=None):
    """
    Stop connection with PLUS server.
    """
    logging.debug('PlusServerConnection.stopPlusConnection')
    
    # Stop Plus server
    if self.ultrasoundPlusServerNode:
      self.ultrasoundPlusServerNode.StopServer()
    if self.trackerPlusServerNode:
      self.trackerPlusServerNode.StopServer()

    # Wait
    if progressDialog:
      self.sleepWithProgressDialog(5, progressDialog, 'Stopping Plus Server. Please wait...')
    else:
      time.sleep(5)

    # Save PLUS connection status
    plusServerConnectionStatus = self.getPlusServerConnectionStatus()
    if (plusServerConnectionStatus == 'OFF'):
      logging.debug('Plus Servers were successfully disconnected.')
      plusServerRunning = False
    else:
      logging.error('ERROR: Plus Servers were not successfully disconnected.')
      plusServerRunning = False
    
    # Plus server running
    Parameters.instance.setParameter(Parameters.PLUS_SERVER_RUNNING, plusServerRunning)

    # Remove previous incoming MRML nodes
    incomingNodes = list()
    if self.ultrasoundConnector:
      for i in range(self.ultrasoundConnector.GetNumberOfIncomingMRMLNodes()):
        incomingNodes.append(self.ultrasoundConnector.GetIncomingMRMLNode(i))
    if self.trackerConnector:
      for i in range(self.trackerConnector.GetNumberOfIncomingMRMLNodes()):
        incomingNodes.append(self.trackerConnector.GetIncomingMRMLNode(i))
    for incomingNode in incomingNodes:
      slicer.mrmlScene.RemoveNode(incomingNode)

    # Remove connector node
    if self.ultrasoundConnector:
      slicer.mrmlScene.RemoveNode(self.ultrasoundConnector)
      self.ultrasoundConnector = None
    if self.trackerConnector:
      slicer.mrmlScene.RemoveNode(self.trackerConnector)
      self.trackerConnector = None
      
    # Reset connector node ID into parameter node
    Parameters.instance.setParameter(Parameters.ULTRASOUND_IGTL_CONNECTOR_NODE_ID, '')
    Parameters.instance.setParameter(Parameters.TRACKER_IGTL_CONNECTOR_NODE_ID, '')

    # Remove Plus server nodes
    if self.ultrasoundPlusServerNode:
      slicer.mrmlScene.RemoveNode(self.ultrasoundPlusServerNode)
      self.ultrasoundPlusServerNode = None
    if self.trackerPlusServerNode:
      slicer.mrmlScene.RemoveNode(self.trackerPlusServerNode)
      self.trackerPlusServerNode = None

    # Get IGTL connection status
    slicer.app.processEvents()
    self.getIGTLConnectionStatus()

  #------------------------------------------------------------------------------
  def pauseIGTLConnection(self):
    """
    Pause OpenIGTLink connection.
    """    
    # Get IGTL connector node IDs
    ultrasoundConnectorID = Parameters.instance.getParameterString(Parameters.ULTRASOUND_IGTL_CONNECTOR_NODE_ID)   
    trackerConnectorID = Parameters.instance.getParameterString(Parameters.TRACKER_IGTL_CONNECTOR_NODE_ID)

    # Get IGTL connector nodes
    ultrasoundIGTLConnectorNode = slicer.mrmlScene.GetNodeByID(ultrasoundConnectorID)
    trackerIGTLConnectorNode = slicer.mrmlScene.GetNodeByID(trackerConnectorID)

    # Stop connection
    if ultrasoundIGTLConnectorNode:
      ultrasoundIGTLConnectorNode.Stop()
    if trackerIGTLConnectorNode:
      trackerIGTLConnectorNode.Stop()

  #------------------------------------------------------------------------------
  def unpauseIGTLConnection(self):
    """
    Unpause OpenIGTLink connection.
    """    
    # Get IGTL connector node IDs
    ultrasoundConnectorID = Parameters.instance.getParameterString(Parameters.ULTRASOUND_IGTL_CONNECTOR_NODE_ID)   
    trackerConnectorID = Parameters.instance.getParameterString(Parameters.TRACKER_IGTL_CONNECTOR_NODE_ID)

    # Get IGTL connector nodes
    ultrasoundIGTLConnectorNode = slicer.mrmlScene.GetNodeByID(ultrasoundConnectorID)
    trackerIGTLConnectorNode = slicer.mrmlScene.GetNodeByID(trackerConnectorID)

    # Start connection
    if ultrasoundIGTLConnectorNode:
      ultrasoundIGTLConnectorNode.Start()
    if trackerIGTLConnectorNode:
      trackerIGTLConnectorNode.Start()

  #------------------------------------------------------------------------------
  def getPlusServerConnectionStatus(self):
    logging.debug('PlusServerConnection.getPlusServerConnectionStatus')

    # Get state of plus server nodes
    if self.ultrasoundPlusServerNode:
      ultrasoundPlusServerState = self.ultrasoundPlusServerNode.GetState()
    if self.trackerPlusServerNode:
      trackerPlusServerState = self.trackerPlusServerNode.GetState()

    # Possible connection states
    stateOn = slicer.vtkMRMLPlusServerNode().On
    stateStopping = slicer.vtkMRMLPlusServerNode().Stopping
    stateOff = slicer.vtkMRMLPlusServerNode().Off

    # Get overall connection status
    status = 'UNKNOWN'
    if self.ultrasoundPlusServerNode and self.trackerPlusServerNode:
      if (ultrasoundPlusServerState == stateOn) and (trackerPlusServerState == stateOn):
        status = 'ON'
      elif (ultrasoundPlusServerState == stateStopping) or (trackerPlusServerState == stateStopping):
        status = 'STOPPING'
      elif (ultrasoundPlusServerState == stateOff) or (trackerPlusServerState == stateOff):
        status = 'OFF'
      else:
        status = 'UNKNOWN'
    elif self.ultrasoundConnector:
      if ultrasoundPlusServerState == stateOn:
        status = 'ON'
      elif ultrasoundPlusServerState == stateStopping:
        status = 'STOPPING'
      elif ultrasoundPlusServerState == stateOff:
        status = 'OFF'
      else:
        status = 'UNKNOWN'
    elif self.trackerConnector:
      if trackerPlusServerState == stateOn:
        status = 'ON'
      elif trackerPlusServerState == stateStopping:
        status = 'STOPPING'
      elif trackerPlusServerState == stateOff:
        status = 'OFF'
      else:
        status = 'UNKNOWN'
    else:
      logging.debug('getPlusServerConnectionStatus: No Plus Server nodes were found')
      status = 'OFF'

    parameterNode = Parameters.instance.getParameterNode()
    # Update parameter node    
    Parameters.instance.setParameter(Parameters.PLUS_CONNECTION_STATUS, status)

    return status

  #------------------------------------------------------------------------------
  def getIGTLConnectionStatus(self, caller=None, event=None):
    logging.debug('PlusServerConnection.getIGTLConnectionStatus')

    # Get parameter node
    parameterNode = Parameters.instance.getParameterNode()
    if not parameterNode:
      logging.error('getIGTLConnectionStatus: Failed to get parameter node')
      return

    # Get state from connectors
    if self.ultrasoundConnector:
      ultrasoundConnectorState = self.ultrasoundConnector.GetState()
    if self.trackerConnector:
      trackerConnectorState = self.trackerConnector.GetState()

    # Possible connection states
    stateConnected = slicer.vtkMRMLIGTLConnectorNode.StateConnected
    stateWaiting = slicer.vtkMRMLIGTLConnectorNode.StateWaitConnection
    stateOff = slicer.vtkMRMLIGTLConnectorNode.StateOff

    # Get overall connection status
    if self.ultrasoundConnector and self.trackerConnector:
      if (ultrasoundConnectorState == stateConnected) and (trackerConnectorState == stateConnected):
        status = 'ON'
      elif (ultrasoundConnectorState == stateWaiting) or (trackerConnectorState == stateWaiting):
        status = 'WAIT'
      elif (ultrasoundConnectorState == stateOff) or (trackerConnectorState == stateOff):
        status = 'OFF'
      else:
        status = 'UNKNOWN'
    elif self.ultrasoundConnector:
      if ultrasoundConnectorState == stateConnected:
        status = 'ON'
      elif ultrasoundConnectorState == stateWaiting:
        status = 'WAIT'
      elif ultrasoundConnectorState == stateOff:
        status = 'OFF'
      else:
        status = 'UNKNOWN'
    elif self.trackerConnector:
      if trackerConnectorState == stateConnected:
        status = 'ON'
      elif trackerConnectorState == stateWaiting:
        status = 'WAIT'
      elif trackerConnectorState == stateOff:
        status = 'OFF'
      else:
        status = 'UNKNOWN'
    else:
      logging.debug('getIGTLConnectionStatus: No IGTL connector was found')
      status = 'OFF'

    # Update list of incoming nodes
    self.getListOfIncomingNodes()

    # Update parameter node
    Parameters.instance.setParameter(Parameters.IGTL_CONNECTION_STATUS, status)

  #------------------------------------------------------------------------------
  def getListOfIncomingNodes(self):
    # Reset lists of node info
    self.incomingNodesNames = list()
    self.incomingNodesTypes = list()
    
    # Get incoming MRML nodes - ultrasound connector
    if self.ultrasoundConnector:
      if self.ultrasoundConnector.GetState() == slicer.vtkMRMLIGTLConnectorNode.StateConnected:
        numIncomingNodes = self.ultrasoundConnector.GetNumberOfIncomingMRMLNodes()
        for nodeIndex in range(numIncomingNodes):
          node = self.ultrasoundConnector.GetIncomingMRMLNode(nodeIndex)
          self.incomingNodesNames.append(node.GetName())
          self.incomingNodesTypes.append(node.GetClassName())
    
    # Get incoming MRML nodes - tracker connector
    if self.trackerConnector:
      if self.trackerConnector.GetState() == slicer.vtkMRMLIGTLConnectorNode.StateConnected:
        numIncomingNodes = self.trackerConnector.GetNumberOfIncomingMRMLNodes()
        for nodeIndex in range(numIncomingNodes):
          node = self.trackerConnector.GetIncomingMRMLNode(nodeIndex)
          self.incomingNodesNames.append(node.GetName())
          self.incomingNodesTypes.append(node.GetClassName())

  #------------------------------------------------------------------------------
  def sleepWithProgressDialog(self, totalTime, progressDialog, progressLabel, numSteps = 10):
    # Update label
    progressDialog.setLabelText(progressLabel)

    # Iterate
    for i in range(numSteps):
      progress = i * (progressDialog.maximum - progressDialog.minimum) / numSteps
      progressDialog.setValue(progress)
      time.sleep(totalTime/numSteps)
      slicer.app.processEvents()


#------------------------------------------------------------------------------
#
# PlusServerConnectionTest
#
#------------------------------------------------------------------------------
class PlusServerConnectionTest(ScriptedLoadableModuleTest):
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
class PlusServerConnectionFileWriter(object):
  def __init__(self, parent):
    pass

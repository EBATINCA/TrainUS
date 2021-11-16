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
    self.parent.acknowledgementText = """EBATINCA, S.L."""

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

  #------------------------------------------------------------------------------
  def setupConnections(self):
    self.ui.startConnectionButton.clicked.connect(self.onStartConnectionButtonClicked)
    self.ui.stopConnectionButton.clicked.connect(self.onStopConnectionButtonClicked)
    self.ui.backToMenuButton.clicked.connect(self.onBackToMenuButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    self.ui.startConnectionButton.clicked.disconnect()
    self.ui.stopConnectionButton.clicked.disconnect()
    self.ui.backToMenuButton.clicked.disconnect()

  #------------------------------------------------------------------------------
  def updateGUIFromMRML(self, caller=None, event=None):
    """
    Set selections and other settings on the GUI based on the parameter node.

    Calls the updateGUIFromMRML function of all tabs so that they can take care of their own GUI.
    """
    # PLUS server connection status
    plusConnectionStatus = Parameters.instance.getParameterString(Parameters.PLUS_CONNECTION_STATUS)
    self.ui.plusConnectionStatusLabel.text = plusConnectionStatus

    # Start/stop buttons
    if plusConnectionStatus == 'SUCCESSFUL':
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
    self.connector = None
    self.plusServerLauncherRunning = False
    self.incomingNodesNames = list()
    self.incomingNodesTypes = list()
    self.plusServerNode = None
    self.plusServerLauncherNode = None
    self.plusServerLauncherSubprocess = None

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
  def loadPlusConfigFile(self):
    # Get config file path and text node ID
    plusConfigPath = Parameters.instance.getParameterString(Parameters.PLUS_CONFIG_PATH)
    logging.debug(' - PLUS config path: %s' % plusConfigPath)    
    plusConfigTextNodeID = Parameters.instance.getParameterString(Parameters.PLUS_CONFIG_TEXT_NODE_ID)

    # Get config file text node
    self.plusConfigTextNode = slicer.mrmlScene.GetNodeByID(plusConfigTextNodeID)
    if self.plusConfigTextNode:
      slicer.mrmlScene.RemoveNode(self.plusConfigTextNode)
    self.plusConfigTextNode = slicer.util.loadText(plusConfigPath) # load XML as text node
    self.plusConfigTextNode.SetName('Plus_Config_File')

    # Add node ID to parameter node
    Parameters.instance.setParameter(Parameters.PLUS_CONFIG_TEXT_NODE_ID, self.plusConfigTextNode.GetID())

  #------------------------------------------------------------------------------
  def startPlusServerLauncher(self, windowVisible = False, progressDialog=None):
    # Location of PLUS server launcher    
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

    # Create Plus server launcher node
    if not self.plusServerLauncherNode:
      self.plusServerLauncherNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLPlusServerLauncherNode')

    # Create Plus server node
    if not self.plusServerNode:
      self.plusServerNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlusServerNode")

    # Set plus server and launcher nodes
    self.plusServerNode.SetAndObserveConfigNode(self.plusConfigTextNode) 
    self.plusServerLauncherNode.AddAndObserveServerNode(self.plusServerNode)

    # Start server
    self.plusServerNode.StartServer()

    # Wait
    if progressDialog:
      self.sleepWithProgressDialog(5, progressDialog, 'Starting PLUS server. Please wait...')
    else:
      time.sleep(5)

    # Get IGTL connector
    connectorNodeFound = False
    referencedNodes = slicer.mrmlScene.GetReferencedNodes(self.plusServerNode)
    for node in referencedNodes:
      if node.GetClassName() == 'vtkMRMLIGTLConnectorNode':
        if node.GetID() != self.plusServerLauncherNode.GetConnectorNode().GetID():
          self.connector = node
          connectorNodeFound = True    
    if not connectorNodeFound:
      logging.error('ERROR: Could not find IGTL connector with name: PlusOpenIGTLinkServer_VideoStream_Connector')
      return

    # Add observer to connector
    if not self.connector.HasObserver(slicer.vtkMRMLIGTLConnectorNode.ConnectedEvent):
      self.addObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.ConnectedEvent, self.getIGTLConnectionStatus)
      self.addObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.DisconnectedEvent, self.getIGTLConnectionStatus)
      self.addObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.ActivatedEvent, self.getIGTLConnectionStatus)
      self.addObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.DeactivatedEvent, self.getIGTLConnectionStatus)    

    # Save connector node ID into parameter node
    Parameters.instance.setParameter(Parameters.IGTL_CONNECTOR_NODE_ID, self.connector.GetID())

    # Wait
    if progressDialog:
      self.sleepWithProgressDialog(2, progressDialog, 'Getting streamed data. Please wait...')
    else:
      time.sleep(2)

    # Get IGTL connection status
    slicer.app.processEvents()
    self.getIGTLConnectionStatus()

    # Get Plus server state
    if (self.plusServerNode.GetState() == slicer.vtkMRMLPlusServerNode().On):
      plusConnectionStatus ='SUCCESSFUL'
      plusServerRunning = 'True'
    else:
      logging.error('ERROR: Plus Server is not connected.')
      plusConnectionStatus ='FAILED'
      plusServerRunning = 'False'
    Parameters.instance.setParameter(Parameters.PLUS_CONNECTION_STATUS, plusConnectionStatus)
    Parameters.instance.setParameter(Parameters.PLUS_SERVER_RUNNING, plusServerRunning)

  #------------------------------------------------------------------------------
  def stopPlusConnection(self, progressDialog=None):
    """
    Stop connection with PLUS server.
    """
    logging.debug('PlusServerConnection.stopPlusConnection')
    
    # Stop Plus server
    self.plusServerNode.StopServer()

    # Wait
    if progressDialog:
      self.sleepWithProgressDialog(5, progressDialog, 'Stopping Plus Server. Please wait...')
    else:
      time.sleep(5)

    # Save PLUS connection status
    if (self.plusServerNode.GetState() == slicer.vtkMRMLPlusServerNode().Off) or (self.plusServerNode.GetState() == slicer.vtkMRMLPlusServerNode().Stopping):
      plusConnectionStatus ='OFF'
      plusServerRunning = 'False'      
    else:
      logging.error('ERROR: Plus Server was not successfully disconnected.')
      plusConnectionStatus ='FAILED'    
      plusServerRunning = 'False'
    Parameters.instance.setParameter(Parameters.PLUS_CONNECTION_STATUS, plusConnectionStatus)
    Parameters.instance.setParameter(Parameters.PLUS_SERVER_RUNNING, plusServerRunning)

    # Remove previous incoming MRML nodes
    incomingNodes = list()
    for i in range(self.connector.GetNumberOfIncomingMRMLNodes()):
      incomingNodes.append(self.connector.GetIncomingMRMLNode(i))
    for incomingNode in incomingNodes:
      slicer.mrmlScene.RemoveNode(incomingNode)

    # Remove connector node
    if self.connector:
      slicer.mrmlScene.RemoveNode(self.connector)
      # Reset connector node ID into parameter node
      Parameters.instance.setParameter(Parameters.IGTL_CONNECTOR_NODE_ID, '')

    # Get IGTL connection status
    slicer.app.processEvents()
    self.getIGTLConnectionStatus()

  #------------------------------------------------------------------------------
  def getIGTLConnectionStatus(self, caller=None, event=None):
    logging.debug('PlusServerConnection.getIGTLConnectionStatus')

    # Connector
    if self.connector:
      # Get state from connector
      connectorState = self.connector.GetState()
      if connectorState == slicer.vtkMRMLIGTLConnectorNode.StateOff:
        status = 'OFF'
      elif connectorState == slicer.vtkMRMLIGTLConnectorNode.StateConnected:
        status = 'ON'
      elif connectorState == slicer.vtkMRMLIGTLConnectorNode.StateWaitConnection:
        status = 'WAIT'
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
    
    # Get number of incoming MRML nodes
    if not self.connector:
      return
    numIncomingNodes = self.connector.GetNumberOfIncomingMRMLNodes()

    # Get name and type of each node
    if self.connector.GetState() == slicer.vtkMRMLIGTLConnectorNode.StateConnected:
      for nodeIndex in range(numIncomingNodes):
        node = self.connector.GetIncomingMRMLNode(nodeIndex)
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

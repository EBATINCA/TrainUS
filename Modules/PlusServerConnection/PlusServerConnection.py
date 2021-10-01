import vtk, qt, ctk, slicer
import os
import subprocess
import time
import logging
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

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

  #------------------------------------------------------------------------------
  def enter(self):
    """
    Runs whenever the module is reopened
    """
    self.logic.setParameterNode()

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
    # Get parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('updateGUIFromMRML: Failed to get parameter node')
      return

    # PLUS server connection status
    plusConnectionStatus = parameterNode.GetParameter(self.trainUsWidget.logic.plusConnectionStatusParameterName)
    self.ui.plusConnectionStatusLabel.text = plusConnectionStatus

    # Start/stop buttons
    if plusConnectionStatus == 'SUCCESSFUL':
      self.ui.startConnectionButton.enabled = False
      self.ui.stopConnectionButton.enabled = True
    else:
      self.ui.startConnectionButton.enabled = True
      self.ui.stopConnectionButton.enabled = False

    # IGTL connection status
    igtlConnectionStatus = parameterNode.GetParameter(self.trainUsWidget.logic.igtlConnectionStatusParameterName)
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
    [dialog, progressLabel] = self.showProgressDialog()
    dialog.show()
    slicer.app.processEvents()

    # Start connection with PLUS server
    self.logic.startPlusConnection(progressLabel)

    # Restore cursor and hide dialog
    qt.QApplication.restoreOverrideCursor()
    dialog.hide()
    dialog.deleteLater()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onStopConnectionButtonClicked(self):
    # Set wait cursor
    qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)

    # Disable button
    self.ui.stopConnectionButton.enabled = False

    # Stop connection with PLUS server
    self.logic.stopPlusConnection()

    # Restore cursor
    qt.QApplication.restoreOverrideCursor()

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
    #TODO: Use context manager
    #TODO: Use an actual progress bar (at least progress by processing the scans)
    """
    progressDialog = qt.QDialog(slicer.util.mainWindow(), qt.Qt.FramelessWindowHint | qt.Qt.Dialog)
    layout = qt.QVBoxLayout()
    progressDialog.setLayout(layout)
    frame = qt.QFrame()
    frame.setFrameStyle(qt.QFrame.Panel | qt.QFrame.Sunken)
    layout.addWidget(frame)
    innerLayout = qt.QVBoxLayout()
    frame.setLayout(innerLayout)
    innerLayout.setMargin(20)
    label = qt.QLabel()
    label.text = '                         Please wait...                                     '
    innerLayout.addWidget(label)
    progressDialog.show()
    slicer.app.processEvents()
    return [progressDialog, label]


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

    # Parameter node
    self.parameterNode = None

    # PLUS connection variables
    self.connector = None
    self.isRunning = False
    self.plusLauncherPath = 'C:/PLUS TOOLKIT/PlusApp-2.8.0.20191105-Win32/bin/PlusServer.exe'
    self.plusConfigFilePath = 'C:/D/TUS/US simulation data/l20171207_113513_config.xml'
    #self.plusLauncherPath = 'C:/PLUS TOOLKIT/PlusApp-2.3.0.4272-Win32/bin/PlusServer.exe'
    #self.plusConfigFilePath = 'C:/PLUS TOOLKIT/PlusApp-2.3.0.4272-Win32/config/PlusDeviceSet_Server_Sim_NwirePhantom.xml'
    self.incomingNodesNames = list()
    self.incomingNodesTypes = list()

    # Setup scene
    self.setupScene()

    # Setup keyboard shortcuts
    self.setupKeyboardShortcuts()

  #------------------------------------------------------------------------------
  def setParameterNode(self):
    
    # Get parameter node
    self.parameterNode = self.trainUsWidget.getParameterNode()
    if not self.parameterNode:
      logging.error('setParameterNode: Failed to get parameter node')
      return

    # Remove observations from nodes referenced in the old parameter node
    if self.parameterNode is not None:
      self.removeObserver(self.parameterNode, vtk.vtkCommand.ModifiedEvent, self.moduleWidget.updateGUIFromMRML)

    # Add observations on referenced nodes
    if self.parameterNode:
      self.addObserver(self.parameterNode, vtk.vtkCommand.ModifiedEvent, self.moduleWidget.updateGUIFromMRML)  

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
  def startPlusConnection(self, progressLabel=None):
    """
    Start connection with PLUS server.
    """
    logging.debug('PlusServerConnection.startPlusConnection')

    # Get parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('getIGTLConnectionStatus: Failed to get parameter node')
      return

    # Update progress label
    if progressLabel:
      progressLabel.text = 'Launching PLUS server. Please wait...'
      slicer.app.processEvents()

    # Location of PLUS configuration file    
    plusConfigPath = self.plusConfigFilePath #self.writeConfigFile(plusConfigTemplatePath, plusDataPath)

    # Start connection PLUS server is not running already
    if not self.isRunning:
      # Start PlusServer.exe
      self.isRunning = True
      info = subprocess.STARTUPINFO()
      info.dwFlags = 1
      info.wShowWindow = 0
      self.p = subprocess.Popen([self.plusLauncherPath, '--config-file='+plusConfigPath ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=info)

      # Wait
      time.sleep(10)

      # Create IGTL connector node if it does not exist
      if not self.connector:
        self.connector = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLIGTLConnectorNode')
        self.connector.SetTypeClient("localhost", 18944)

      # Save connector node ID into parameter node
      parameterNode.SetParameter(self.trainUsWidget.logic.igtlConnectorNodeIDParameterName, self.connector.GetID())    

      # Add observer to connector
      self.addObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.ConnectedEvent, self.getIGTLConnectionStatus)
      self.addObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.DisconnectedEvent, self.getIGTLConnectionStatus)
      self.addObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.ActivatedEvent, self.getIGTLConnectionStatus)
      self.addObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.DeactivatedEvent, self.getIGTLConnectionStatus)

      # Start connector
      self.connector.Start()

      # Update progress label
      if progressLabel:
        progressLabel.text = 'Starting IGTL connector. Please wait...'
        slicer.app.processEvents()

      # Wait
      time.sleep(5)

      # Get state of connector      
      slicer.app.processEvents()
      if self.connector.GetState() != slicer.vtkMRMLIGTLConnectorNode.StateConnected: # no connection
        logging.error('PLUS Server failed to launch')  
        self.stopPlusConnection()

        # Set status
        plusConnectionStatus = 'FAILED'

        # Remove observers to connector node
        self.removeObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.ConnectedEvent, self.getIGTLConnectionStatus)
        self.removeObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.DisconnectedEvent, self.getIGTLConnectionStatus)
        self.removeObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.ActivatedEvent, self.getIGTLConnectionStatus)
        self.removeObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.DeactivatedEvent, self.getIGTLConnectionStatus)

        # Print output in Python Console
        output = self.p.stdout.read()
        output = output.decode("utf-8")
        print(output)

      else: # connected
        logging.debug('Start connection with PLUS server.')
        # Set status
        plusConnectionStatus ='SUCCESSFUL'

    else:
      self.stopPlusConnection()

      # Set status
      plusConnectionStatus = 'OFF'

      # Remove observers to connector node
      if self.connector:
        self.removeObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.ConnectedEvent, self.getIGTLConnectionStatus)
        self.removeObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.DisconnectedEvent, self.getIGTLConnectionStatus)
        self.removeObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.ActivatedEvent, self.getIGTLConnectionStatus)
        self.removeObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.DeactivatedEvent, self.getIGTLConnectionStatus)

    # Save connection status
    parameterNode.SetParameter(self.trainUsWidget.logic.plusConnectionStatusParameterName, plusConnectionStatus)

  #------------------------------------------------------------------------------
  def stopPlusConnection(self):
    """
    Stop connection with PLUS server.
    """
    logging.debug('PlusServerConnection.stopPlusConnection')
    
    # Get parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('getIGTLConnectionStatus: Failed to get parameter node')
      return

    # Stop PLUS server and IGTL connector
    if self.isRunning:
      self.connector.Stop()
      self.p.terminate()
      self.isRunning = False
      logging.debug('Stop connection with PLUS server.')

      # Wait
      time.sleep(2)

      # Remove observers
      if self.connector:
        self.removeObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.ConnectedEvent, self.getIGTLConnectionStatus)
        self.removeObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.DisconnectedEvent, self.getIGTLConnectionStatus)
        self.removeObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.ActivatedEvent, self.getIGTLConnectionStatus)
        self.removeObserver(self.connector, slicer.vtkMRMLIGTLConnectorNode.DeactivatedEvent, self.getIGTLConnectionStatus)

    # Save IGTL connection status
    self.getIGTLConnectionStatus()

    # Save PLUS connection status
    plusConnectionStatus = 'OFF'
    parameterNode.SetParameter(self.trainUsWidget.logic.plusConnectionStatusParameterName, plusConnectionStatus)

  #------------------------------------------------------------------------------
  def getIGTLConnectionStatus(self, caller=None, event=None):
    logging.debug('PlusServerConnection.getIGTLConnectionStatus')

    # Wait
    time.sleep(0.5) # some time is required for connection status to update

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

    # Get parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('getIGTLConnectionStatus: Failed to get parameter node')
      return

    # Update list of incoming nodes
    self.getListOfIncomingNodes()

    # Update parameter node    
    parameterNode.SetParameter(self.trainUsWidget.logic.igtlConnectionStatusParameterName, status)

  #------------------------------------------------------------------------------
  def getListOfIncomingNodes(self):    
    if not self.connector:
      return

    # Get number of incoming MRML nodes
    numIncomingNodes = self.connector.GetNumberOfIncomingMRMLNodes()

    # Get name and type of each node
    self.incomingNodesNames = list()
    self.incomingNodesTypes = list()
    if self.connector.GetState() == slicer.vtkMRMLIGTLConnectorNode.StateConnected:
      for nodeIndex in range(numIncomingNodes):
        node = self.connector.GetIncomingMRMLNode(nodeIndex)
        self.incomingNodesNames.append(node.GetName())
        self.incomingNodesTypes.append(node.GetClassName())


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

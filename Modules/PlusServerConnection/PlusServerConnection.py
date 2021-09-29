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
    self.disconnect()

  #------------------------------------------------------------------------------
  def enter(self):
    """
    Runs whenever the module is reopened
    """
    pass

  #------------------------------------------------------------------------------
  def setupUi(self):
    
    # Load widget from .ui file (created by Qt Designer).
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/PlusServerConnection.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Customize widgets
    self.ui.connectionStatusLabel.text = '-'
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
  def updateGUIFromMRML(self):
    """
    Set selections and other settings on the GUI based on the parameter node.

    Calls the updateGUIFromMRML function of all tabs so that they can take care of their own GUI.
    """
    # Get parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('updateGUIFromMRML: Failed to get parameter node')
      return

    # Connection status
    connectorStatus = parameterNode.GetParameter(self.trainUsWidget.logic.plusConnectionStatusParameterName)
    self.ui.connectionStatusLabel.text = connectorStatus

    # Start/stop buttons
    if connectorStatus == 'OFF':
      self.ui.startConnectionButton.enabled = True
      self.ui.stopConnectionButton.enabled = False
    else:
      self.ui.startConnectionButton.enabled = False
      self.ui.stopConnectionButton.enabled = True

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

    # Check connection status
    self.logic.getPlusConnectionStatus()

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

    # Check connection status
    self.logic.getPlusConnectionStatus()

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

    # PLUS connection variables
    self.connector = None
    self.isRunning = False
    self.plusLauncherPath = 'C:/PLUS TOOLKIT/PlusApp-2.3.0.4272-Win32/bin/PlusServer.exe'
    self.plusConfigFilePath = 'C:/PLUS TOOLKIT/PlusApp-2.3.0.4272-Win32/config/PlusDeviceSet_Server_Sim_NwirePhantom.xml'

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
      time.sleep(5)

      # Create IGTL connector node if it does not exist
      if not self.connector:
        self.connector = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLIGTLConnectorNode')
        self.connector.SetTypeClient("localhost", 18944)

      # Add observer to connector
      self.addObserver(self.connector, vtk.vtkCommand.ModifiedEvent, self.getPlusConnectionStatus)

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
      if self.connector.GetState() != slicer.vtkMRMLIGTLConnectorNode.StateConnected:
        logging.error('PLUS Server failed to launch')        
        self.stopPlusConnection()
        self.removeObserver(self.connector, vtk.vtkCommand.ModifiedEvent, self.getPlusConnectionStatus)
        # Print output in Python Console
        output = self.p.stdout.read()
        output = output.decode("utf-8")
        print(output)
        return
      print('Start connection with PLUS server.')

    else:
      self.stopPlusConnection()
      if self.connector:
        self.removeObserver(self.connector, vtk.vtkCommand.ModifiedEvent, self.getPlusConnectionStatus)

  #------------------------------------------------------------------------------
  def stopPlusConnection(self):
    """
    Stop connection with PLUS server.
    """
    logging.debug('PlusServerConnection.stopPlusConnection')
    if self.isRunning:
      self.connector.Stop()
      self.p.terminate()
      self.isRunning = False
      print('Stop connection with PLUS server.')
      if self.connector:
        self.removeObserver(self.connector, vtk.vtkCommand.ModifiedEvent, self.getPlusConnectionStatus)

  #------------------------------------------------------------------------------
  def getPlusConnectionStatus(self, caller=None, event=None):
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
      logging.error('getPlusConnectionStatus: Failed to get parameter node')
      return

    # Update parameter node    
    parameterNode.SetParameter(self.trainUsWidget.logic.plusConnectionStatusParameterName, status)


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

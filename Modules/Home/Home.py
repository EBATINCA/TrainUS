import vtk, qt, ctk, slicer
import os
import numpy as np

from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
# from Resources import HomeResourcesResources

import logging
import TabWidgets

#------------------------------------------------------------------------------
#
# Home
#
#------------------------------------------------------------------------------
class Home(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Home"
    self.parent.categories = ["TrainUS"]
    self.parent.dependencies = []
    self.parent.contributors = ["Csaba Pinter (Ebatinca), David Garcia Mato (Ebatinca)"]
    self.parent.helpText = """The Home screen of the custom application"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """EBATINCA, S.L.""" # replace with organization, grant and thanks.


#------------------------------------------------------------------------------
#
# Home dialog class
#
#------------------------------------------------------------------------------
class QHomeWidget(qt.QDialog):
  """
  QHomeWidget extends QDialog class to have a modified close event for required home screen functionality
  """
  def __init__(self):
    """
    Initializes required window options for the widget

    :return void:
    """
    qt.QDialog.__init__(self)
    self.setWindowFlags(qt.Qt.Window)
    self.setWindowTitle('TrainUS')

    self.homeLayout = qt.QHBoxLayout(self)
    self.homeLayout.margin = 0

  def closeEvent(self, event):
    """
    Handle closing

    :param QCloseEvent event: The parameters that describe the close event

    :return void:
    """
    confirmCloseBox = qt.QMessageBox()
    confirmCloseBox.setIcon(qt.QMessageBox.Warning)
    confirmCloseBox.setWindowTitle('Confirm Close')
    confirmCloseBox.setText(
      'Are you sure you want to close TrainUS?\n\nAny unsaved changes will be lost.')
    confirmCloseBox.setStandardButtons(qt.QMessageBox.Ok | qt.QMessageBox.Cancel)
    confirmCloseBox.setDefaultButton(qt.QMessageBox.Cancel)
    confirmCloseBox.setModal(True)
    retval = confirmCloseBox.exec_()
    if retval == qt.QMessageBox.Ok:
      self.hide()
      slicer.mrmlScene.Clear(0)
      # qt.QTimer.singleShot(0, slicer.app, slicer.app.closeAllWindows())
      #TODO: Use slicer.trainUsWidget.exitApplication()
    else:
      event.ignore()


#------------------------------------------------------------------------------
#
# HomeWidget
#
#------------------------------------------------------------------------------
class HomeWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    """
    Initialize the window and main GUI for the TrainUS home screen

    :param QWidget parent: The parent widget for the QHomeWidget class

    :return void:
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)

    self.homeWidget = QHomeWidget()
    self.trainUsWidget = slicer.trainUsWidget
    # self.homeWidget.setStyleSheet(self.loadStyleSheet())

  #------------------------------------------------------------------------------
  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer)
    self.uiWidget = slicer.util.loadUI(self.resourcePath('UI/Home.ui'))
    self.homeWidget.homeLayout.addWidget(self.uiWidget)
    self.ui = slicer.util.childWidgetVariables(self.uiWidget)

    # Create logic class
    self.logic = HomeLogic(self)

    # Setup connections
    self.setupConnections()

    # Dark palette does not propagate on its own?
    self.uiWidget.setPalette(slicer.util.mainWindow().style().standardPalette())   

    # Setup participant interface
    self.setupUi()

    # Update UI tables
    self.updateDashboardTable()
    self.updateParticipantsTable()

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
    self.showHome()

  #------------------------------------------------------------------------------
  def showHome(self):
    """
    Open the home screen by setting positioning and raising to modal widget

    :return void:
    """
    mainWindow = slicer.util.mainWindow()
    if mainWindow:
      self.popupGeometry = mainWindow.geometry
      self.homeWidget.setGeometry(self.popupGeometry)
      self.homeWidget.show()
      if mainWindow.isFullScreen():
        self.homeWidget.showFullScreen()
      if mainWindow.isMaximized():
        self.homeWidget.showMaximized()
      mainWindow.hide()
    self.creatingNewStudy = False

  #------------------------------------------------------------------------------
  def hideHome(self):
    """
    Hide the home screen and reveals the main interface after loading a scene

    :return void:
    """
    mainWindow = slicer.util.mainWindow()
    if mainWindow:
      self.popupGeometry = self.homeWidget.geometry
      mainWindow.show()
      mainWindow.setGeometry(self.popupGeometry)
      if self.homeWidget.isFullScreen():
        mainWindow.showFullScreen()
      #if self.homeWidget.isMaximized():
      #  mainWindow.showMaximized()
      self.homeWidget.hide()

  #------------------------------------------------------------------------------
  def setupConnections(self):
    pass

  #------------------------------------------------------------------------------
  def disconnect(self):
    pass

  #------------------------------------------------------------------------------
  def loadStyleSheet(self):
    """
    Loading style sheet for the home screen

    :return string: Returns stylesheet as a string to be applied to the home screen
    """
    moduleDir = os.path.dirname(__file__)
    styleFile = os.path.join(moduleDir, 'Resources', 'StyleSheets', 'HomeStyle.qss')
    f = qt.QFile(styleFile)

    # Adding logging statement for when a particular file does not exist
    if not f.exists():
      logging.debug("Unable to load stylesheet, file not found")
      return ""
    else:
      f.open(qt.QFile.ReadOnly | qt.QFile.Text)
      ts = qt.QTextStream(f)
      stylesheet = ts.readAll()
      return stylesheet

  #------------------------------------------------------------------------------
  def updateGUIFromMRML(self, caller=None, event=None):
    """
    Set selections and other settings on the GUI based on the parameter node.

    Calls the updateGUIFromMRML function of all tabs so that they can take care of their own GUI.
    """
    if not hasattr(slicer, 'trainUsWidget'):
      # The TrainUS module has not been set up yet
      return

    # Get parameter node
    parameterNode = slicer.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('updateGUIFromMRML: Failed to get parameter node')
      return

  #------------------------------------------------------------------------------
  def setupUi(self):
    logging.debug('Home.setupUi')

    # Dashboard tab
    self.ui.DashboardPanel = TabWidgets.Dashboard(self.ui.dashboardTab)
    self.ui.DashboardPanel.homeWidget = self
    self.ui.DashboardPanel.setupUi()
    self.ui.dashboardTab.layout().addWidget(self.ui.DashboardPanel)

    # Participants tab
    self.ui.ParticipantsPanel = TabWidgets.Participants(self.ui.participantsTab)
    self.ui.ParticipantsPanel.homeWidget = self
    self.ui.ParticipantsPanel.setupUi()
    self.ui.participantsTab.layout().addWidget(self.ui.ParticipantsPanel)

    # Recordings tab
    self.ui.RecordingsPanel = TabWidgets.Recordings(self.ui.recordingsTab)
    self.ui.RecordingsPanel.homeWidget = self
    self.ui.RecordingsPanel.setupUi()
    self.ui.recordingsTab.layout().addWidget(self.ui.RecordingsPanel)

    # Configuration tab
    self.ui.ConfigurationPanel = TabWidgets.Configuration(self.ui.configurationTab)
    self.ui.ConfigurationPanel.homeWidget = self
    self.ui.ConfigurationPanel.setupUi()
    self.ui.configurationTab.layout().addWidget(self.ui.ConfigurationPanel)

  def updateDashboardTable(self):
    """
    Updates content of dashboard table by reading the database in root directory.
    """
    # Get data from directory
    [participantID_list, participantName_list, participantSurname_list, participantNumRecordings_list] = self.logic.readRootDirectory()

    # Get table widget
    tableWidget = self.ui.DashboardPanel.ui.participantsTable

    # Reset table
    tableWidget.clearContents()
    
    # Update table content
    numParticipants = len(participantID_list)
    tableWidget.setRowCount(numParticipants)
    for participantPos in range(numParticipants):
      participantIDTableItem = qt.QTableWidgetItem(participantID_list[participantPos])
      participantNameTableItem = qt.QTableWidgetItem(participantName_list[participantPos])
      participantSurnameTableItem = qt.QTableWidgetItem(participantSurname_list[participantPos])
      participantNumRecordingsTableItem = qt.QTableWidgetItem(str(participantNumRecordings_list[participantPos]))
      tableWidget.setItem(participantPos, 0, participantIDTableItem)
      tableWidget.setItem(participantPos, 1, participantNameTableItem)
      tableWidget.setItem(participantPos, 2, participantSurnameTableItem)
      tableWidget.setItem(participantPos, 3, participantNumRecordingsTableItem)

  def getDataFromDashboardTable(self):
    """
    Gets data from dashboard table.

    :return tuple: participant IDs (list), participant names (list), participant surname (list), participant number of recordings (list).
    """
    # Get table widget
    tableWidget = self.ui.DashboardPanel.ui.participantsTable

    # Get table elements
    participantID_list = []
    participantName_list = []
    participantSurname_list = []
    participantNumRecordings_list = []
    numRows = tableWidget.rowCount
    for rowID in range(numRows):
      participantID = tableWidget.model().index(rowID,0).data()
      participantName = tableWidget.model().index(rowID,1).data()
      participantSurname = tableWidget.model().index(rowID,2).data()
      participantNumRecordings = tableWidget.model().index(rowID,3).data()
      participantID_list.append(participantID)
      participantName_list.append(participantName)
      participantSurname_list.append(participantSurname)
      participantNumRecordings_list.append(participantNumRecordings)

    return participantID_list, participantName_list, participantSurname_list, participantNumRecordings_list

  def updateParticipantsTable(self):
    """
    Updates content of participants table by reading the database in root directory.
    """
    # Get data from directory
    [participantID_list, participantName_list, participantSurname_list, participantNumRecordings_list] = self.logic.readRootDirectory()

    # Get table widget
    tableWidget = self.ui.ParticipantsPanel.ui.participantsTable

    # Reset table
    tableWidget.clearContents()
    
    # Update table content
    numParticipants = len(participantID_list)
    tableWidget.setRowCount(numParticipants)
    for participantPos in range(numParticipants):
      participantIDTableItem = qt.QTableWidgetItem(participantID_list[participantPos])
      participantNameTableItem = qt.QTableWidgetItem(participantName_list[participantPos])
      participantSurnameTableItem = qt.QTableWidgetItem(participantSurname_list[participantPos])
      participantNumRecordingsTableItem = qt.QTableWidgetItem(str(participantNumRecordings_list[participantPos]))
      tableWidget.setItem(participantPos, 0, participantIDTableItem)
      tableWidget.setItem(participantPos, 1, participantNameTableItem)
      tableWidget.setItem(participantPos, 2, participantSurnameTableItem)
      tableWidget.setItem(participantPos, 3, participantNumRecordingsTableItem)



#---------------------------------------------------------------------------------------------#
#                                                                                             #
#                                                                                             #
#                                                                                             #
#                                       HomeLogic                                             #
#                                                                                             #
#                                                                                             #
#                                                                                             #
#---------------------------------------------------------------------------------------------#
class HomeLogic(ScriptedLoadableModuleLogic, VTKObservationMixin):
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

    # Store whether python console was floating so that it is restored when hidden
    self.pythonConsoleWasFloating = False

    # Constants
    #TODO:

    # Default parameters map
    self.defaultParameters = {}
    # self.defaultParameters["DecimationFactor"] = 0.85

    # Parameter node reference roles
    # self.modelReferenceRolePrefix = 'Model_'

    # Setup keyboard shortcuts
    self.setupKeyboardShortcuts()

  #------------------------------------------------------------------------------
  def setupKeyboardShortcuts(self):
    shortcuts = [
        ('Ctrl+3', self.showPythonConsoleFromHome)
        ]

    for (shortcutKey, callback) in shortcuts:
        shortcut = qt.QShortcut(self.moduleWidget.homeWidget)
        shortcut.setKey(qt.QKeySequence(shortcutKey))
        shortcut.connect('activated()', callback)

  #------------------------------------------------------------------------------
  def showPythonConsoleFromHome(self):
    pythonConsoleDockWidget = slicer.util.mainWindow().pythonConsole().parent()
    wasVisible = pythonConsoleDockWidget.visible
    pythonConsoleDockWidget.setVisible(not wasVisible)
    if not wasVisible:
      self.pythonConsoleWasFloating = pythonConsoleDockWidget.floating
      pythonConsoleDockWidget.floating = True
    else:
      pythonConsoleDockWidget.floating = self.pythonConsoleWasFloating

  #------------------------------------------------------------------------------
  def readRootDirectory(self):
    """
    Reads all the files in the root directory to get the list of participants and recordings in the database.

    :return tuple: participant IDs (list), participant names (list), participant surnames (list), and participant
                  number of recordings (list)
    """
    
    # Set root directory
    dataPath = slicer.trainUsWidget.logic.DATA_PATH

    # Get participants
    participantID_list = self.getListOfFoldersInDirectory(dataPath)

    # Get participant info
    participantName_list = []
    participantSurname_list = []
    participantNumRecordings_list = []
    for participantID in participantID_list:
      # Participant directory
      participant_directory = os.path.join(dataPath, participantID)

      # Get name and surname
      participantInfo_file = os.path.join(participant_directory, 'Participant_Info.txt')
      [participantName, participantSurname] = self.readParticipantInfoFile(participantInfo_file)
      participantName_list.append(participantName)
      participantSurname_list.append(participantSurname)

      # Get number of recordings
      recordingID_list = self.getListOfFoldersInDirectory(participant_directory)
      numRecordings = len(recordingID_list)
      participantNumRecordings_list.append(numRecordings)

    # Display
    print('\nDirectory: ', dataPath)
    print('\nParticipants in directory: ', participantID_list)
    print('\nNames: ', participantName_list)
    print('\nSurnames: ', participantSurname_list)
    print('\nNumber of recordings: ', participantNumRecordings_list)

    return participantID_list, participantName_list, participantSurname_list, participantNumRecordings_list

  #------------------------------------------------------------------------------
  def getListOfFoldersInDirectory(self, directory):
    """
    Gets list of folders contained in input directory.

    :param directory: input directory (string)

    :return list of folder names (list)
    """
    dirfiles = os.listdir(directory)
    fullpaths = map(lambda name: os.path.join(directory, name), dirfiles)
    folderList = []
    for fileID, filePath in enumerate(fullpaths):
      if os.path.isdir(filePath): 
        folderList.append(dirfiles[fileID])
    return list(folderList)

  #------------------------------------------------------------------------------
  def readParticipantInfoFile(self, filePath):
    """
    Reads participant's information from .txt file.

    :param filePath: path to file (string)

    :return tuple: participant name (string), participant surname (string)
    """
    file = open(filePath, "r")
    participantName = file.readline()[len('Name:'):-1] # read name
    participantSurname = file.readline()[len('Surname:'):-1] # read surname
    file.close()
    return participantName, participantSurname

  #------------------------------------------------------------------------------
  def getParticipantInfoFromID(self, participantID):
    """
    Get participant's information from participant ID.

    :param participantID: participant ID (string)

    :return tuple: participant name (string), participant surname (string)
    """
    # Set root directory
    dataPath = slicer.trainUsWidget.logic.DATA_PATH

    # Participant directory
    participant_directory = os.path.join(dataPath, participantID)

    # Participant info file
    participantInfo_file = os.path.join(participant_directory, 'Participant_Info.txt')
    
    # Read participant info
    [participantName, participantSurname] = self.readParticipantInfoFile(participantInfo_file)

    return participantName, participantSurname
  
  #------------------------------------------------------------------------------
  def writeParticipantInfoFile(self, filePath, participantName, participantSurname):
    """
    Writes participant's information (name and surname) to .txt file.

    :param filePath: path to file (string)
    :param participantName: participant name (string)
    :param participantSurname: participant surname (string)
    """
    file = open(filePath, "w") 
    file.write("Name: " + participantName) 
    file.write("\n") 
    file.write("Surname: " + participantSurname) 
    file.write("\n") 
    file.close()

  #------------------------------------------------------------------------------
  def createNewParticipant(self, participantName, participantSurname):
    """
    Adds new participant to database by generating a unique ID, creating a new folder, 
    and creating a new .txt file containing participant information.

    :param participantName: participant name (string)
    :param participantSurname: participant surname (string)

    :return new participant ID (string)
    """
    
    # Get data from directory
    [participantID_list, participantName_list, participantSurname_list, participantNumRecordings_list] = self.readRootDirectory()

    # Generate new participant ID
    participantID_array = np.array(participantID_list).astype(int)
    maxParticipantID = np.max(participantID_array)
    newParticipantID = "{:05d}".format(maxParticipantID + 1) # leading zeros, 5 digits

    # Set root directory
    dataPath = slicer.trainUsWidget.logic.DATA_PATH

    # Create participant folder
    participant_directory = os.path.join(dataPath, str(newParticipantID))
    try:
      os.makedirs(participant_directory)    
      print("Directory " , participant_directory ,  " Created ")
    except FileExistsError:
      print("Directory " , participant_directory ,  " already exists")  

    # Create participant info file
    participantInfo_file = os.path.join(participant_directory, 'Participant_Info.txt')
    self.writeParticipantInfoFile(participantInfo_file, participantName, participantSurname)

    return str(newParticipantID)


#------------------------------------------------------------------------------
#
# HomeTest
#
#------------------------------------------------------------------------------
class HomeTest(ScriptedLoadableModuleTest):
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
    self.test_Home1()

  def test_Home1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the participant would interact with your code and confirm that it still works
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

    logic = HomeLogic()
    self.delayDisplay('Test passed!')


#
# Class for avoiding python error that is caused by the method SegmentEditor::setup
# http://issues.slicer.org/view.php?id=3871
#
class HomeFileWriter(object):
  def __init__(self, parent):
    pass

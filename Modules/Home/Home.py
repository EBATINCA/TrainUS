import vtk, qt, ctk, slicer
import os
import numpy as np
import json
import shutil

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

    # Setup user interface
    self.setupUi()

    # Tab widget visibility
    self.updateTrainingMenuVisibility(visible = False)

    # Update UI tables
    self.updateDashboardTable()
    self.updateParticipantsTable()
    self.updateRecordingsTable()

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
    self.ui.backToSlicerButton.clicked.connect(self.onBackToSlicerButtonClicked)
    self.ui.exitAppButton.clicked.connect(self.onExitAppButtonClicked)
    self.ui.finishTrainingButton.clicked.connect(self.onFinishTrainingButtonClicked)
    self.ui.languageComboBox.currentIndexChanged.connect(self.onLanguageComboBoxIndexChanged)

  #------------------------------------------------------------------------------
  def disconnect(self):    
    self.ui.backToSlicerButton.clicked.disconnect()
    self.ui.exitAppButton.clicked.disconnect()
    self.ui.finishTrainingButton.clicked.disconnect()
    self.ui.languageComboBox.currentIndexChanged.disconnect()
    
  #------------------------------------------------------------------------------
  def onBackToSlicerButtonClicked(self):    
    # Shows slicer interface
    self.hideHome()

    # Change to TrainUS module
    slicer.util.selectModule('TrainUS')
    
  #------------------------------------------------------------------------------
  def onExitAppButtonClicked(self):
    # Confirm exit message box
    exitFlag = self.exitApplicationMessageBox()
    if exitFlag:    
      # Shows slicer interface
      self.hideHome()

      # Change to TrainUS module
      slicer.util.selectModule('TrainUS')

      # Exit application
      self.trainUsWidget.logic.exitApplication()
    
  #------------------------------------------------------------------------------
  def onFinishTrainingButtonClicked(self):
    # Hides training menu
    self.updateTrainingMenuVisibility(visible = False)

  #------------------------------------------------------------------------------
  def onLanguageComboBoxIndexChanged(self):
    # Update UI
    self.logic.updateLanguageUI(self.ui.languageComboBox.currentIndex)
    
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
    parameterNode = self.trainUsWidget.getParameterNode()
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

    # Basic training tab
    self.ui.BasicTrainingPanel = TabWidgets.BasicTraining(self.ui.basicTrainingTab)
    self.ui.BasicTrainingPanel.homeWidget = self
    self.ui.BasicTrainingPanel.setupUi()
    self.ui.basicTrainingTab.layout().addWidget(self.ui.BasicTrainingPanel)

    # Advanced training tab
    self.ui.AdvancedTrainingPanel = TabWidgets.AdvancedTraining(self.ui.advancedTrainingTab)
    self.ui.AdvancedTrainingPanel.homeWidget = self
    self.ui.AdvancedTrainingPanel.setupUi()
    self.ui.advancedTrainingTab.layout().addWidget(self.ui.AdvancedTrainingPanel)

    # Update UI language
    self.logic.updateLanguageUI(selectedLanguageIndex = 0) # english by default

  #------------------------------------------------------------------------------
  def updateTrainingMenuVisibility(self, visible):
    logging.debug('Home.TrainingMenuVisibility')

    # Update visibility tab widgets
    self.ui.dashboardTabWidget.visible = not visible 
    self.ui.trainingInfoGroupBox.visible = visible
    self.ui.trainingTabWidget.visible = visible
    self.ui.finishTrainingFrame.visible = visible    

  #------------------------------------------------------------------------------
  def updateDashboardTable(self):
    """
    Updates content of dashboard table by reading the database in root directory.
    """
    # Get data from directory
    participantInfo_list = self.logic.readRootDirectory()

    # Filter participants according to search text
    searchText = self.ui.DashboardPanel.ui.participantSearchText.text
    if searchText is not '':
      participantInfo_list = self.logic.filterParticipantInfoListFromSearchText(participantInfo_list, searchText)

    # Get table widget
    tableWidget = self.ui.DashboardPanel.ui.participantsTable

    # Reset table
    tableWidget.clearContents()
    
    # Update table content
    if len(participantInfo_list) >= 0:
      numParticipants = len(participantInfo_list)
      tableWidget.setRowCount(numParticipants)
      for participantPos in range(numParticipants):
        participantIDTableItem = qt.QTableWidgetItem(participantInfo_list[participantPos]['id'])
        participantNameTableItem = qt.QTableWidgetItem(participantInfo_list[participantPos]['name'])
        participantSurnameTableItem = qt.QTableWidgetItem(participantInfo_list[participantPos]['surname'])
        participantBirthDateTableItem = qt.QTableWidgetItem(participantInfo_list[participantPos]['birthdate'])
        participantEmailTableItem = qt.QTableWidgetItem(participantInfo_list[participantPos]['email'])
        tableWidget.setItem(participantPos, 0, participantIDTableItem)
        tableWidget.setItem(participantPos, 1, participantNameTableItem)
        tableWidget.setItem(participantPos, 2, participantSurnameTableItem)
        tableWidget.setItem(participantPos, 3, participantBirthDateTableItem)
        tableWidget.setItem(participantPos, 4, participantEmailTableItem)
    else:
      tableWidget.setRowCount(0)
      logging.debug('Home.updateDashboardTable: No participants found in database...')

  #------------------------------------------------------------------------------
  def updateDashboardTableSelection(self):
    """
    Updates selected item of dashboard table from parameter node.
    """
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get selected participant
    selectedParticipantID = parameterNode.GetParameter(self.trainUsWidget.logic.selectedParticipantIDParameterName)

    # Get table widget
    tableWidget = self.ui.DashboardPanel.ui.participantsTable

    # Select row corresponding to selected participant
    numRows = tableWidget.rowCount
    for row in range(numRows):
      item = tableWidget.item(row, 0)
      if item.text() == selectedParticipantID:
        tableWidget.setCurrentItem(item)

  #------------------------------------------------------------------------------
  def updateParticipantsTable(self):
    """
    Updates content of participants table by reading the database in root directory.
    """
    # Get data from directory
    participantInfo_list = self.logic.readRootDirectory()

    # Filter participants according to search text
    searchText = self.ui.ParticipantsPanel.ui.participantSearchText.text
    if searchText is not '':
      participantInfo_list = self.logic.filterParticipantInfoListFromSearchText(participantInfo_list, searchText)

    # Get table widget
    tableWidget = self.ui.ParticipantsPanel.ui.participantsTable

    # Reset table
    tableWidget.clearContents()
    
    # Update table content
    if len(participantInfo_list) >= 0:
      numParticipants = len(participantInfo_list)
      tableWidget.setRowCount(numParticipants)
      for participantPos in range(numParticipants):
        participantIDTableItem = qt.QTableWidgetItem(participantInfo_list[participantPos]['id'])
        participantNameTableItem = qt.QTableWidgetItem(participantInfo_list[participantPos]['name'])
        participantSurnameTableItem = qt.QTableWidgetItem(participantInfo_list[participantPos]['surname'])
        participantBirthDateTableItem = qt.QTableWidgetItem(participantInfo_list[participantPos]['birthdate'])
        participantEmailTableItem = qt.QTableWidgetItem(participantInfo_list[participantPos]['email'])
        tableWidget.setItem(participantPos, 0, participantIDTableItem)
        tableWidget.setItem(participantPos, 1, participantNameTableItem)
        tableWidget.setItem(participantPos, 2, participantSurnameTableItem)
        tableWidget.setItem(participantPos, 3, participantBirthDateTableItem)
        tableWidget.setItem(participantPos, 4, participantEmailTableItem)
    else:
      tableWidget.setRowCount(0)
      logging.debug('Home.updateParticipantsTable: No participants found in database...')

  #------------------------------------------------------------------------------
  def updateParticipantsTableSelection(self):
    """
    Updates selected item of dashboard table from parameter node.
    """
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get selected participant
    selectedParticipantID = parameterNode.GetParameter(self.trainUsWidget.logic.selectedParticipantIDParameterName)

    # Get table widget
    tableWidget = self.ui.ParticipantsPanel.ui.participantsTable

    # Select row corresponding to selected participant
    numRows = tableWidget.rowCount
    for row in range(numRows):
      item = tableWidget.item(row, 0)
      if item.text() == selectedParticipantID:
        tableWidget.setCurrentItem(item)

  #------------------------------------------------------------------------------
  def updateRecordingsTable(self):
    """
    Updates selected participant in recordings table.
    """
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    #
    # Update selected participant
    #

    # Get selected participant
    selectedParticipantID = parameterNode.GetParameter(self.trainUsWidget.logic.selectedParticipantIDParameterName)

    # Get participant info from ID
    selectedParticipantInfo = self.logic.getParticipantInfoFromID(selectedParticipantID)

    # Create string to display in GUI
    if selectedParticipantInfo:
      participantID = selectedParticipantInfo['id']
      participantName= selectedParticipantInfo['name']
      participantSurname = selectedParticipantInfo['surname']
      selectedParticipantLabel = f'[{participantID}] {participantSurname}, {participantName}'
    else:
      selectedParticipantLabel = ''

    # Update GUI
    self.ui.RecordingsPanel.ui.participantSelectionText.text = selectedParticipantLabel

    #
    # Update table content
    #
    
    # Get table widget
    tableWidget = self.ui.RecordingsPanel.ui.recordingsTable

    # Reset table
    tableWidget.clearContents()

    # Update table if participant is selected
    if selectedParticipantID is not '':
      # Get data from directory
      recordingInfo_list = self.logic.readParticipantDirectory(selectedParticipantID)

      # Update table content
      if len(recordingInfo_list) >= 0:
        numRecordings = len(recordingInfo_list)
        tableWidget.setRowCount(numRecordings)
        for recordingPos in range(numRecordings):
          recordingIDTableItem = qt.QTableWidgetItem(recordingInfo_list[recordingPos]['id'])
          recordingDateTableItem = qt.QTableWidgetItem(recordingInfo_list[recordingPos]['date'])
          recordingExerciseTableItem = qt.QTableWidgetItem(recordingInfo_list[recordingPos]['exercise'])
          recordingDurationTableItem = qt.QTableWidgetItem(recordingInfo_list[recordingPos]['duration'])
          tableWidget.setItem(recordingPos, 0, recordingIDTableItem)
          tableWidget.setItem(recordingPos, 1, recordingDateTableItem)
          tableWidget.setItem(recordingPos, 2, recordingExerciseTableItem)
          tableWidget.setItem(recordingPos, 3, recordingDurationTableItem)
      else:
        tableWidget.setRowCount(0)
        logging.debug('Home.updateRecordingsTable: No recordings found in database...')
    else:
      tableWidget.setRowCount(0)
      logging.debug('Home.updateRecordingsTable: No participant is selected')

  #------------------------------------------------------------------------------
  def exitApplicationMessageBox(self):
    """
    Display message box for the user to confirm if the partipant data must be deleted.
    :return bool: True if delete action is confirmed, False otherwise
    """
    confirmExit = qt.QMessageBox()
    confirmExit.setIcon(qt.QMessageBox.Warning)
    confirmExit.setWindowTitle(self.logic.home_exitAppMessageBoxTitle)
    confirmExit.setText(self.logic.home_exitAppMessageBoxLabel)
    confirmExit.setStandardButtons(qt.QMessageBox.Yes | qt.QMessageBox.No)
    confirmExit.setDefaultButton(qt.QMessageBox.No)
    confirmExit.setModal(True)
    retval = confirmExit.exec_()
    if retval == qt.QMessageBox.Yes:
      return True
    else:
      return False

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
    self.trainUsWidget = self.moduleWidget.trainUsWidget
    # Pointer to the parameter node so that we have access to the old one before setting the new one
    self.parameterNode = None

    # Store whether python console was floating so that it is restored when hidden
    self.pythonConsoleWasFloating = False

    # Constants
    #TODO:

    # UI variables
    self.home_exitAppMessageBoxTitle = ''
    self.home_exitAppMessageBoxLabel = ''
    self.dashboard_warningMessageTextLabel = ''
    self.participants_warningMessageTextLabel = ''
    self.participants_deleteMessageBoxTitle = ''
    self.participants_deleteMessageBoxLabel = ''
    self.recordings_deleteMessageBoxTitle = ''
    self.recordings_deleteMessageBoxLabel = ''

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
    Reads all the files in the root directory to get the list of participants in the database.

    :return list: list of dictionaries containing the information of all participants in the database
    """
    logging.debug('Home.readRootDirectory')

    # Get root directory
    dataPath = self.trainUsWidget.logic.DATA_PATH

    # Get participants
    participantID_list = self.getListOfFoldersInDirectory(dataPath)

    # Get participant info
    participantInfo_list = list() # list of dictionaries
    for participantID in participantID_list:
      # Participant info file
      participantInfoFilePath = self.getParticipantInfoFilePath(participantID)

      # Get participant info
      participantInfo = self.readParticipantInfoFile(participantInfoFilePath)
      participantInfo_list.append(participantInfo)

    # Display
    print('\n>>>>>Home.readRootDirectory<<<<<<<<<<<<')
    print('\nDirectory: ', dataPath)
    print('\nParticipants in directory: ', participantID_list)
    print('\nInfo JSON: ', participantInfo_list)

    return participantInfo_list

  #------------------------------------------------------------------------------
  def filterParticipantInfoListFromSearchText(self, participantInfo_list, searchText):
    """
    Filters participant information list of dictionaries to keep only those participant matching the search criteria.

    :param participantInfo_list: list of dictionaries containing the information of all participants in the database (list)
    :param searchText: input text in search box (string)

    :return list: list of dictionaries containing the information of all participants matching search criteria
    """
    logging.debug('Home.filterParticipantInfoListFromSearchText')

    # Get number of participants in input list
    numParticipants = len(participantInfo_list)

    # Convert input search text to lower case
    searchText = searchText.lower()

    # Create filtered list
    participantInfoFiltered_list = list()
    if numParticipants >= 0:
      for participantPos in range(numParticipants):
        participantName = participantInfo_list[participantPos]['name'] # Get name
        participantSurname = participantInfo_list[participantPos]['surname'] # Get surname
        participantString = participantName + ' ' + participantSurname # Create single string with participant name and surname
        participantString = participantString.lower() # convert to lower case
        if searchText in participantString: # keep participants meeting search criteria
          participantInfoFiltered_list.append(participantInfo_list[participantPos])
    return participantInfoFiltered_list  

  #------------------------------------------------------------------------------
  def readParticipantDirectory(self, participantID):
    """
    Reads participant directory to get the list of recordings in the database.

    :return tuple: participant IDs (list), participant names (list), participant surnames (list), and participant
                  number of recordings (list)
    """
    logging.debug('Home.readParticipantDirectory')

    # Get root directory
    dataPath = self.trainUsWidget.logic.DATA_PATH

    # Participant directory
    participantDirectory = os.path.join(dataPath, participantID)
    print('Home.readParticipantDirectory: participant directory: ', participantDirectory)

    # Get recordings
    recordingID_list = self.getListOfFoldersInDirectory(participantDirectory)
    print('Home.readParticipantDirectory: participant directory: ', recordingID_list)

    # Get participant info
    recordingInfo_list = list() # list of dictionaries
    for recordingID in recordingID_list:
      # Get recording info
      recordingInfo = self.getRecordingInfoFromID(participantID, recordingID)
      if recordingInfo is not None:
        recordingInfo_list.append(recordingInfo)

    # Display
    print('\n>>>>>Home.readParticipantDirectory<<<<<<<<<<<<')
    print('\nDirectory: ', participantDirectory)
    print('\nRecordings in directory: ', recordingID_list)
    print('\nInfo JSON: ', recordingInfo_list)  

    return recordingInfo_list  

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
    Reads participant's information from .json file.

    :param filePath: path to JSON file (string)

    :return participant info (dict)
    """
    try:
      with open(filePath, 'r') as inputFile:
        participantInfo =  json.loads(inputFile.read())
    except:
      logging.error('Cannot read participant information from JSON file at ' + filePath)
      participantInfo = None
    return participantInfo
  
  #------------------------------------------------------------------------------
  def readRecordingInfoFile(self, filePath):
    """
    Reads recording's information from .json file.

    :param filePath: path to JSON file (string)

    :return recording info (dict)
    """
    try:
      with open(filePath, 'r') as inputFile:
        recordingInfo =  json.loads(inputFile.read())
    except:
      logging.error('Cannot read recording information from JSON file at ' + filePath)
      recordingInfo = None
    return recordingInfo
  
  #------------------------------------------------------------------------------
  def writeParticipantInfoFile(self, filePath, participantInfo):
    """
    Writes participant's information (name and surname) to .txt file.

    :param filePath: path to file (string)
    :param participantInfo: participant information (dict)
    """
    with open(filePath, "w") as outputFile:
      json.dump(participantInfo, outputFile, indent = 4)

  #------------------------------------------------------------------------------
  def getParticipantInfoFromID(self, participantID):
    """
    Get participant's information from participant ID.

    :param participantID: participant ID (string)

    :return participant info (dict)
    """
    # Abort if participant ID is not invalid
    if participantID == '':
      return

    # Participant info file
    participantInfoFilePath = self.getParticipantInfoFilePath(participantID)
    
    # Read participant info
    participantInfo = self.readParticipantInfoFile(participantInfoFilePath)

    return participantInfo

  #------------------------------------------------------------------------------
  def getRecordingInfoFromID(self, participantID, recordingID):
    """
    Get recording's information from participant ID and recording ID.

    :param participantID: participant ID (string)
    :param recordingID: recording ID (string)

    :return recording info (dict)
    """
    # Abort if recording ID is not invalid
    if (participantID == '') or (recordingID == ''):
      return

    # Recording info file
    recordingInfoFilePath = self.getRecordingInfoFilePath(participantID, recordingID)
    
    # Read recording info
    recordingInfo = self.readRecordingInfoFile(recordingInfoFilePath)

    return recordingInfo

  #------------------------------------------------------------------------------
  def getParticipantInfoFromSelection(self):
    """
    Get participant's information from selection stored in parameter node.

    :return participant info (dict)
    """
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get selected participant
    selectedParticipantID = parameterNode.GetParameter(self.trainUsWidget.logic.selectedParticipantIDParameterName)

    # Get participant info from ID
    selectedParticipantInfo = self.getParticipantInfoFromID(selectedParticipantID)

    return selectedParticipantInfo

  #------------------------------------------------------------------------------
  def getRecordingInfoFromSelection(self):
    """
    Get recording's information from selection stored in parameter node.

    :return recording info (dict)
    """
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get selected participant and recording
    selectedParticipantID = parameterNode.GetParameter(self.trainUsWidget.logic.selectedParticipantIDParameterName)
    selectedRecordingID = parameterNode.GetParameter(self.trainUsWidget.logic.selectedRecordingIDParameterName)

    # Get participant info from ID
    selectedRecordingInfo = self.getRecordingInfoFromID(selectedParticipantID, selectedRecordingID)

    return selectedRecordingInfo

  #------------------------------------------------------------------------------
  def getParticipantInfoFilePath(self, participantID):
    """
    Get path to participant's information JSON file.

    :param participantID: participant ID (string)

    :return participant info (dict)
    """
    # Set root directory
    dataPath = self.trainUsWidget.logic.DATA_PATH

    # Participant directory
    participantDirectory = os.path.join(dataPath, participantID)

    # Participant info file
    participantInfoFilePath = os.path.join(participantDirectory, 'Participant_Info.json')

    return participantInfoFilePath

  #------------------------------------------------------------------------------
  def getRecordingInfoFilePath(self, participantID, recordingID):
    """
    Get path to recording's information JSON file.

    :param participantID: participant ID (string)
    :param recordingID: recording ID (string)

    :return recording info (dict)
    """
    # Set root directory
    dataPath = self.trainUsWidget.logic.DATA_PATH

    # Participant directory
    participantDirectory = os.path.join(dataPath, participantID)

    # Recording directory
    recordingDirectory = os.path.join(participantDirectory, recordingID)

    # Participant info file
    recordingInfoFilePath = os.path.join(recordingDirectory, 'Recording_Info.json')

    return recordingInfoFilePath

  #------------------------------------------------------------------------------
  def deleteParticipant(self, participantID):
    """
    Delete participant from root directory.

    :param participantID: participant ID (string)
    """
    logging.debug('Home.deleteParticipant')

    # Set root directory
    dataPath = self.trainUsWidget.logic.DATA_PATH

    # Participant directory
    participantDirectory = os.path.join(dataPath, participantID)

    # Delete folder
    shutil.rmtree(participantDirectory, ignore_errors=True)

  #------------------------------------------------------------------------------
  def deleteRecording(self, participantID, recordingID):
    """
    Delete recording from root directory.

    :param participantID: participant ID (string)
    :param recordingID: recording ID (string)
    """
    logging.debug('Home.deleteRecording')

    # Set root directory
    dataPath = self.trainUsWidget.logic.DATA_PATH

    # Recording directory
    participantDirectory = os.path.join(dataPath, participantID)
    recordingDirectory = os.path.join(participantDirectory, recordingID)

    # Delete folder
    shutil.rmtree(recordingDirectory, ignore_errors=True)

  #------------------------------------------------------------------------------
  def createNewParticipant(self, participantName, participantSurname, participantBirthDate, participantEmail):
    """
    Adds new participant to database by generating a unique ID, creating a new folder, 
    and creating a new .txt file containing participant information.

    :param participantName: participant name (string)
    :param participantSurname: participant surname (string)
    :param participantBirthDate: participant birth date (string)
    :param participantEmail: participant email (string)

    :return new participant info (dict)
    """
    logging.debug('Home.createNewParticipant')

    # Get data from directory
    participantInfo_list = self.readRootDirectory()

    # Get existing participant IDs
    numParticipants = len(participantInfo_list)
    participantID_list = []
    for participant in range(numParticipants):
      participantID_list.append(participantInfo_list[participant]['id'])

    # Generate new participant ID (TODO: improve to ensure uniqueness)
    participantID_array = np.array(participantID_list).astype(int)
    try:
      maxParticipantID = np.max(participantID_array)
    except:
      maxParticipantID = 0
    newParticipantID = str("{:05d}".format(maxParticipantID + 1)) # leading zeros, 5 digits

    # Set root directory
    dataPath = self.trainUsWidget.logic.DATA_PATH

    # Create participant folder
    participantDirectory = os.path.join(dataPath, str(newParticipantID))
    try:
      os.makedirs(participantDirectory)    
      logging.debug('Participant directory was created')
    except FileExistsError:
      logging.debug('Participant directory already exists')

    # Create participant info dictionary
    participantInfo = {}
    participantInfo['id'] = newParticipantID
    participantInfo['name'] = participantName
    participantInfo['surname'] = participantSurname
    participantInfo['birthdate'] = participantBirthDate
    participantInfo['email'] = participantEmail

    # Create info file
    participantInfoFilePath = self.getParticipantInfoFilePath(newParticipantID)
    self.writeParticipantInfoFile(participantInfoFilePath, participantInfo)

    return participantInfo

  #------------------------------------------------------------------------------
  def isParticipantSelected(self):
    """
    Check if a participant is selected.
    :return bool: True if valid participant is selected, False otherwise
    """    
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get selected participant
    selectedParticipantID = parameterNode.GetParameter(self.trainUsWidget.logic.selectedParticipantIDParameterName)

    # Check valid selection
    if (selectedParticipantID == '') :
      participantSelected = False
    else:
      participantSelected = True
    return participantSelected

  #------------------------------------------------------------------------------
  def readLanguageFile(self, filePath):
    """
    Load data from language .json file into a dictionary.

    :param filePath: path to JSON file (string)

    :return language UI info (dict)
    """
    try:
      with open(filePath, 'r') as inputFile:
        languageInfo =  json.loads(inputFile.read())
    except:
      logging.error('Cannot read language texts from JSON file at ' + filePath)
      languageInfo = None
    return languageInfo

  #------------------------------------------------------------------------------
  def updateLanguageUI(self, selectedLanguageIndex):
    """
    Update UI texts according to the selected language.

    :param selectedLanguageIndex: index of the selected language (int)
    """
    logging.debug('Home.updateLanguageUI')

    # Language JSON files
    #dataPath = 'C:/D/TUS/TrainUS/Modules/Home/Resources/Language/'
    dataPath = self.moduleWidget.resourcePath('UI/')
    if selectedLanguageIndex == 0:
      fileName = 'LanguageFile_English.json'
    elif selectedLanguageIndex == 1:
      fileName = 'LanguageFile_Spanish.json'
    else:
      fileName = 'LanguageFile_English.json'
    filePath = os.path.join(dataPath, fileName)

    # Read JSON file
    languageTexts = self.readLanguageFile(filePath)
    if languageTexts is None:
      return

    # Update UI widgets texts from language file
    ## Home
    self.moduleWidget.ui.languageLabel.setText(languageTexts['Home.languageLabel'])
    self.moduleWidget.ui.dashboardTabWidget.setTabText(0, languageTexts['Home.dashboardTab'])
    self.moduleWidget.ui.dashboardTabWidget.setTabText(1, languageTexts['Home.participantsTab'])
    self.moduleWidget.ui.dashboardTabWidget.setTabText(2, languageTexts['Home.recordingsTab'])
    self.moduleWidget.ui.dashboardTabWidget.setTabText(3, languageTexts['Home.configurationTab'])
    self.moduleWidget.ui.backToSlicerButton.setText(languageTexts['Home.backToSlicerButton'])
    self.moduleWidget.ui.exitAppButton.setText(languageTexts['Home.exitAppButton'])
    self.moduleWidget.ui.trainingTabWidget.setTabText(0, languageTexts['Home.basicTrainingTab'])
    self.moduleWidget.ui.trainingTabWidget.setTabText(1, languageTexts['Home.advancedTrainingTab'])
    self.moduleWidget.ui.trainingInfoGroupBox.setTitle(languageTexts['Home.trainingInfoGroupBox'])
    self.moduleWidget.ui.participantInfoLabel_1.setText(languageTexts['Home.participantInfoLabel_1'])
    self.moduleWidget.ui.participantInfoLabel_2.setText(languageTexts['Home.participantInfoLabel_2'])
    self.moduleWidget.ui.participantInfoLabel_3.setText(languageTexts['Home.participantInfoLabel_3'])
    self.moduleWidget.ui.finishTrainingButton.setText(languageTexts['Home.finishTrainingButton'])
    self.home_exitAppMessageBoxTitle = languageTexts['Home.exitAppMessageBoxTitle']
    self.home_exitAppMessageBoxLabel = languageTexts['Home.exitAppMessageBoxText_1'] + '\n\n' + languageTexts['Home.exitAppMessageBoxText_2']
    ## Dashboard
    self.moduleWidget.ui.DashboardPanel.ui.startButton.setText(languageTexts['Dashboard.startButton'])
    self.moduleWidget.ui.DashboardPanel.ui.newParticipantRadioButton.setText(languageTexts['Dashboard.newParticipantRadioButton'])
    self.moduleWidget.ui.DashboardPanel.ui.existingParticipantRadioButton.setText(languageTexts['Dashboard.existingParticipantRadioButton'])
    self.moduleWidget.ui.DashboardPanel.ui.newParticipantGroupBox.setTitle(languageTexts['Dashboard.newParticipantGroupBox'])
    self.moduleWidget.ui.DashboardPanel.ui.existingParticipantGroupBox.setTitle(languageTexts['Dashboard.existingParticipantGroupBox'])
    self.moduleWidget.ui.DashboardPanel.ui.label_1.setText(languageTexts['Dashboard.label_1'])
    self.moduleWidget.ui.DashboardPanel.ui.label_2.setText(languageTexts['Dashboard.label_2'])
    self.moduleWidget.ui.DashboardPanel.ui.label_3.setText(languageTexts['Dashboard.label_3'])
    self.moduleWidget.ui.DashboardPanel.ui.label_4.setText(languageTexts['Dashboard.label_4'])
    self.moduleWidget.ui.DashboardPanel.ui.label_5.setText(languageTexts['Dashboard.label_5'])
    self.moduleWidget.ui.DashboardPanel.ui.label_6.setText(languageTexts['Dashboard.label_6'])
    self.moduleWidget.ui.DashboardPanel.ui.participantsTable.setHorizontalHeaderItem(0, qt.QTableWidgetItem(languageTexts['Dashboard.participantsTable_column1']))
    self.moduleWidget.ui.DashboardPanel.ui.participantsTable.setHorizontalHeaderItem(1, qt.QTableWidgetItem(languageTexts['Dashboard.participantsTable_column2']))
    self.moduleWidget.ui.DashboardPanel.ui.participantsTable.setHorizontalHeaderItem(2, qt.QTableWidgetItem(languageTexts['Dashboard.participantsTable_column3']))
    self.moduleWidget.ui.DashboardPanel.ui.participantsTable.setHorizontalHeaderItem(3, qt.QTableWidgetItem(languageTexts['Dashboard.participantsTable_column4']))
    self.moduleWidget.ui.DashboardPanel.ui.participantsTable.setHorizontalHeaderItem(4, qt.QTableWidgetItem(languageTexts['Dashboard.participantsTable_column5']))
    self.dashboard_warningMessageTextLabel = languageTexts['Dashboard.warningMessageText']
    ## Participants
    self.moduleWidget.ui.ParticipantsPanel.ui.label_1.setText(languageTexts['Participants.label_1'])
    self.moduleWidget.ui.ParticipantsPanel.ui.label_2.setText(languageTexts['Participants.label_2'])
    self.moduleWidget.ui.ParticipantsPanel.ui.participantsTable.setHorizontalHeaderItem(0, qt.QTableWidgetItem(languageTexts['Dashboard.participantsTable_column1']))
    self.moduleWidget.ui.ParticipantsPanel.ui.participantsTable.setHorizontalHeaderItem(1, qt.QTableWidgetItem(languageTexts['Dashboard.participantsTable_column2']))
    self.moduleWidget.ui.ParticipantsPanel.ui.participantsTable.setHorizontalHeaderItem(2, qt.QTableWidgetItem(languageTexts['Dashboard.participantsTable_column3']))
    self.moduleWidget.ui.ParticipantsPanel.ui.participantsTable.setHorizontalHeaderItem(3, qt.QTableWidgetItem(languageTexts['Dashboard.participantsTable_column4']))
    self.moduleWidget.ui.ParticipantsPanel.ui.participantsTable.setHorizontalHeaderItem(4, qt.QTableWidgetItem(languageTexts['Dashboard.participantsTable_column5']))
    self.moduleWidget.ui.ParticipantsPanel.ui.optionsGroupBox.setTitle(languageTexts['Participants.optionsGroupBox'])
    self.moduleWidget.ui.ParticipantsPanel.ui.checkRecordingsButton.setText(languageTexts['Participants.checkRecordingsButton'])
    self.moduleWidget.ui.ParticipantsPanel.ui.editParticipantButton.setText(languageTexts['Participants.editParticipantButton'])
    self.moduleWidget.ui.ParticipantsPanel.ui.deleteParticipantButton.setText(languageTexts['Participants.deleteParticipantButton'])
    self.moduleWidget.ui.ParticipantsPanel.ui.editParticipantGroupBox.setTitle(languageTexts['Participants.editParticipantGroupBox'])
    self.moduleWidget.ui.ParticipantsPanel.ui.editPartipantLabel_1.setText(languageTexts['Participants.editPartipantLabel_1'])
    self.moduleWidget.ui.ParticipantsPanel.ui.editPartipantLabel_2.setText(languageTexts['Participants.editPartipantLabel_2'])
    self.moduleWidget.ui.ParticipantsPanel.ui.editPartipantLabel_3.setText(languageTexts['Participants.editPartipantLabel_3'])
    self.moduleWidget.ui.ParticipantsPanel.ui.editPartipantLabel_4.setText(languageTexts['Participants.editPartipantLabel_4'])
    self.moduleWidget.ui.ParticipantsPanel.ui.saveEditButton.setText(languageTexts['Participants.saveEditButton'])
    self.moduleWidget.ui.ParticipantsPanel.ui.cancelEditButton.setText(languageTexts['Participants.cancelEditButton'])
    self.participants_warningMessageTextLabel = languageTexts['Participants.warningMessageText']
    self.participants_deleteMessageBoxTitle = languageTexts['Participants.deleteMessageBoxTitle']
    self.participants_deleteMessageBoxLabel = languageTexts['Participants.deleteMessageBoxText_1'] + '\n\n' + languageTexts['Participants.deleteMessageBoxText_2']
    ## Recordings
    self.moduleWidget.ui.RecordingsPanel.ui.label_1.setText(languageTexts['Recordings.label_1'])
    self.moduleWidget.ui.RecordingsPanel.ui.label_2.setText(languageTexts['Recordings.label_2'])
    self.moduleWidget.ui.RecordingsPanel.ui.recordingsTable.setHorizontalHeaderItem(0, qt.QTableWidgetItem(languageTexts['Recordings.recordingsTable_column1']))
    self.moduleWidget.ui.RecordingsPanel.ui.recordingsTable.setHorizontalHeaderItem(1, qt.QTableWidgetItem(languageTexts['Recordings.recordingsTable_column2']))
    self.moduleWidget.ui.RecordingsPanel.ui.recordingsTable.setHorizontalHeaderItem(2, qt.QTableWidgetItem(languageTexts['Recordings.recordingsTable_column3']))
    self.moduleWidget.ui.RecordingsPanel.ui.recordingsTable.setHorizontalHeaderItem(3, qt.QTableWidgetItem(languageTexts['Recordings.recordingsTable_column4']))
    self.moduleWidget.ui.RecordingsPanel.ui.optionsGroupBox.setTitle(languageTexts['Recordings.optionsGroupBox'])
    self.moduleWidget.ui.RecordingsPanel.ui.recordingDetailsButton.setText(languageTexts['Recordings.recordingDetailsButton'])
    self.moduleWidget.ui.RecordingsPanel.ui.evaluateRecordingButton.setText(languageTexts['Recordings.evaluateRecordingButton'])
    self.moduleWidget.ui.RecordingsPanel.ui.deleteRecordingButton.setText(languageTexts['Recordings.deleteRecordingButton'])
    self.moduleWidget.ui.RecordingsPanel.ui.recordingDetailsGroupBox.setTitle(languageTexts['Recordings.recordingDetailsGroupBox'])
    self.moduleWidget.ui.RecordingsPanel.ui.recordingDetailsLabel_1.setText(languageTexts['Recordings.recordingDetailsLabel_1'])
    self.moduleWidget.ui.RecordingsPanel.ui.recordingDetailsLabel_2.setText(languageTexts['Recordings.recordingDetailsLabel_2'])
    self.moduleWidget.ui.RecordingsPanel.ui.recordingDetailsLabel_3.setText(languageTexts['Recordings.recordingDetailsLabel_3'])
    self.moduleWidget.ui.RecordingsPanel.ui.recordingDetailsLabel_4.setText(languageTexts['Recordings.recordingDetailsLabel_4'])
    self.moduleWidget.ui.RecordingsPanel.ui.recordingDetailsLabel_5.setText(languageTexts['Recordings.recordingDetailsLabel_5'])
    self.moduleWidget.ui.RecordingsPanel.ui.recordingDetailsLabel_6.setText(languageTexts['Recordings.recordingDetailsLabel_6'])
    self.recordings_deleteMessageBoxTitle = languageTexts['Recordings.deleteMessageBoxTitle']
    self.recordings_deleteMessageBoxLabel = languageTexts['Recordings.deleteMessageBoxText_1'] + '\n\n' + languageTexts['Recordings.deleteMessageBoxText_2'] 

    # Adjust width of table columns to new horizontal headers
    COLUMN_H_MARGIN = 50
    self.addMarginToColumnWidth(self.moduleWidget.ui.DashboardPanel.ui.participantsTable, COLUMN_H_MARGIN)
    self.addMarginToColumnWidth(self.moduleWidget.ui.ParticipantsPanel.ui.participantsTable, COLUMN_H_MARGIN)
    self.addMarginToColumnWidth(self.moduleWidget.ui.RecordingsPanel.ui.recordingsTable, COLUMN_H_MARGIN)

  #------------------------------------------------------------------------------
  def addMarginToColumnWidth(self, tableWidget, margin):
    tableWidget.horizontalHeader().stretchLastSection = False
    tableWidget.resizeColumnsToContents()
    numColumns = tableWidget.columnCount
    for col in range(numColumns):
      tableWidget.setColumnWidth(col, tableWidget.columnWidth(col) + margin)
    tableWidget.horizontalHeader().stretchLastSection = True

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

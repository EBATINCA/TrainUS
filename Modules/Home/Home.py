import vtk, qt, ctk, slicer
import os
import numpy as np
import json
import shutil

from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
# from Resources import HomeResourcesResources

import logging

# Custom widgets
import Widgets

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

    # Update UI tables
    self.updateParticipantsTable()
    self.updateRecordingsTable()

    # The parameter node had defaults at creation, propagate them to the GUI
    self.updateGUIFromMRML()

    # Update UI mode
    #TODO: Include the content of this function in updateGUIFromMRML, and use the parameter node
    # to identify the current mode instead of the argument. The mode is set to the logic already
    # (see the current switchAppMode function).
    self.updateUIforMode(modeID = 0)

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

    # Observe parameter node
    self.logic.observeParameterNode()

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
      if self.homeWidget.isMaximized():
        mainWindow.showMaximized()
      self.homeWidget.hide()

  #------------------------------------------------------------------------------
  def setupConnections(self):
    # Welcome page
    self.ui.fullScreenButton.clicked.connect(self.onFullScreenButtonClicked)
    self.ui.backToSlicerButton.clicked.connect(self.onBackToSlicerButtonClicked)
    self.ui.exitAppButton.clicked.connect(self.onExitAppButtonClicked)
    self.ui.languageComboBox.currentIndexChanged.connect(self.onLanguageComboBoxIndexChanged)
    self.ui.mainTrainingModeButton.clicked.connect(self.onMainTrainingModeButtonClicked)
    self.ui.mainEvaluationModeButton.clicked.connect(self.onMainEvaluationModeButtonClicked)
    self.ui.configurationButton.clicked.connect(self.onConfigurationButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    # Welcome page
    self.ui.fullScreenButton.clicked.disconnect()
    self.ui.backToSlicerButton.clicked.disconnect()
    self.ui.exitAppButton.clicked.disconnect()
    self.ui.languageComboBox.currentIndexChanged.disconnect()
    self.ui.mainTrainingModeButton.clicked.disconnect()
    self.ui.mainEvaluationModeButton.clicked.disconnect()
    self.ui.configurationButton.clicked.disconnect()

  #------------------------------------------------------------------------------
  def onFullScreenButtonClicked(self):
    mainWindow = slicer.util.mainWindow()
    if self.homeWidget.isFullScreen():
      mainWindow.showMaximized()
      self.homeWidget.showMaximized()
    else:
      mainWindow.showFullScreen()
      self.homeWidget.showFullScreen()

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
  def onLanguageComboBoxIndexChanged(self):
    # Update UI
    self.logic.updateLanguageUI(self.ui.languageComboBox.currentIndex)

  #------------------------------------------------------------------------------
  def onMainTrainingModeButtonClicked(self):
    # Update mode
    #TODO: Rename logic function to setMode
    self.logic.switchAppMode('TRAINING')

    # Update UI
    #TODO: No need to call this explicitly after having implemented the
    # updateGUIFromMRML function properly, because it will be called as
    # a callback to the parameter node Modified event
    self.updateUIforMode(modeID = 1) # switch to training mode

    # Update UI tables
    self.updateParticipantsTable()
    self.updateRecordingsTable()

  #------------------------------------------------------------------------------
  def onMainEvaluationModeButtonClicked(self):

    # Update mode
    self.logic.switchAppMode('EVALUATION')

    # Update UI
    self.updateUIforMode(modeID = 6) # switch to evaluation mode

    # Update UI tables
    self.updateParticipantsTable()
    self.updateRecordingsTable()

  #------------------------------------------------------------------------------
  def onConfigurationButtonClicked(self):
    # Update UI
    self.updateUIforMode(modeID = 7) # switch to configuration

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

    # Update review selection panel
    self.updateReviewSelectionPanel()

    # Update training session panel
    self.updateTrainingSessionPanel()

    # Update configuration panel
    self.updateConfigurationPanel()

  #------------------------------------------------------------------------------
  def setupUi(self):
    logging.debug('Home.setupUi')

    # Configuration page
    self.ui.ConfigurationPanel = Widgets.Configuration(self.ui.configurationWidget)
    self.ui.ConfigurationPanel.homeWidget = self
    self.ui.ConfigurationPanel.setupUi()
    self.ui.configurationWidget.layout().addWidget(self.ui.ConfigurationPanel)

    # Training page
    ## Step 1
    self.ui.ParticipantSelectionPanel = Widgets.ParticipantSelection(self.ui.step1Page)
    self.ui.ParticipantSelectionPanel.homeWidget = self
    self.ui.ParticipantSelectionPanel.setupUi()
    self.ui.step1Page.layout().addWidget(self.ui.ParticipantSelectionPanel)
    ## Step 2
    self.ui.HardwareSelectionPanel = Widgets.HardwareSelection(self.ui.step2Page)
    self.ui.HardwareSelectionPanel.homeWidget = self
    self.ui.HardwareSelectionPanel.setupUi()
    self.ui.step2Page.layout().addWidget(self.ui.HardwareSelectionPanel)
    ## Step 3
    self.ui.ReviewSelectionPanel = Widgets.ReviewSelection(self.ui.step3Page)
    self.ui.ReviewSelectionPanel.homeWidget = self
    self.ui.ReviewSelectionPanel.setupUi()
    self.ui.step3Page.layout().addWidget(self.ui.ReviewSelectionPanel)
    ## Step 4
    self.ui.PlugAndPlayPanel = Widgets.PlugAndPlay(self.ui.step4Page)
    self.ui.PlugAndPlayPanel.homeWidget = self
    self.ui.PlugAndPlayPanel.setupUi()
    self.ui.step4Page.layout().addWidget(self.ui.PlugAndPlayPanel)

    # Evaluation page
    self.ui.EvaluationPanel = Widgets.Evaluation(self.ui.evaluationWidget)
    self.ui.EvaluationPanel.homeWidget = self
    self.ui.EvaluationPanel.setupUi()
    self.ui.evaluationWidget.layout().addWidget(self.ui.EvaluationPanel)

    # Training session page
    self.ui.TrainingSessionPanel = Widgets.TrainingSession(self.ui.trainingSessionWidget)
    self.ui.TrainingSessionPanel.homeWidget = self
    self.ui.TrainingSessionPanel.setupUi()
    self.ui.trainingSessionWidget.layout().addWidget(self.ui.TrainingSessionPanel)

    # Update UI language
    self.logic.updateLanguageUI(selectedLanguageIndex = 0) # english by default

  #------------------------------------------------------------------------------
  def updateUIforMode(self, modeID):
    logging.debug('Home.updateUIforMode')

    # Reset navigation label style
    self.ui.step1NavigationLabel.setStyleSheet("QLabel { color : #969696 }")
    self.ui.step2NavigationLabel.setStyleSheet("QLabel { color : #969696 }")
    self.ui.step3NavigationLabel.setStyleSheet("QLabel { color : #969696 }")
    self.ui.step4NavigationLabel.setStyleSheet("QLabel { color : #969696 }")
    self.ui.step1NavigationFrame.lineWidth = 0
    self.ui.step2NavigationFrame.lineWidth = 0
    self.ui.step3NavigationFrame.lineWidth = 0
    self.ui.step4NavigationFrame.lineWidth = 0

    # Switch mode
    if modeID == 0: # home page
      self.ui.welcomePage.visible = True
      self.ui.configurationPage.visible = False
      self.ui.trainingPage.visible = False
      self.ui.trainingSessionPage.visible = False
      self.ui.evaluationPage.visible = False
    if modeID == 1: # start training - step 1
      self.ui.welcomePage.visible = False
      self.ui.configurationPage.visible = False
      self.ui.trainingPage.visible = True
      self.ui.stackedWidget.currentIndex = 0
      self.ui.step1NavigationLabel.setStyleSheet("QLabel { color : black }")
      self.ui.step1NavigationFrame.lineWidth = 2
      self.ui.trainingSessionPage.visible = False
      self.ui.evaluationPage.visible = False
    if modeID == 2: # start training - step 2
      self.ui.welcomePage.visible = False
      self.ui.configurationPage.visible = False
      self.ui.trainingPage.visible = True
      self.ui.stackedWidget.currentIndex = 1
      self.ui.step2NavigationLabel.setStyleSheet("QLabel { color : black }")
      self.ui.step2NavigationFrame.lineWidth = 2
      self.ui.trainingSessionPage.visible = False
      self.ui.evaluationPage.visible = False
    if modeID == 3: # start training - step 3
      self.ui.welcomePage.visible = False
      self.ui.configurationPage.visible = False
      self.ui.trainingPage.visible = True
      self.ui.stackedWidget.currentIndex = 2
      self.ui.step3NavigationLabel.setStyleSheet("QLabel { color : black }")
      self.ui.step3NavigationFrame.lineWidth = 2
      self.ui.trainingSessionPage.visible = False
      self.ui.evaluationPage.visible = False
    if modeID == 4: # start training - step 4
      self.ui.welcomePage.visible = False
      self.ui.configurationPage.visible = False
      self.ui.trainingPage.visible = True
      self.ui.stackedWidget.currentIndex = 3
      self.ui.step4NavigationLabel.setStyleSheet("QLabel { color : black }")
      self.ui.step4NavigationFrame.lineWidth = 2
      self.ui.trainingSessionPage.visible = False
      self.ui.evaluationPage.visible = False
    if modeID == 5: # Training session
      self.ui.welcomePage.visible = False
      self.ui.configurationPage.visible = False
      self.ui.trainingPage.visible = False
      self.ui.trainingSessionPage.visible = True
      self.ui.evaluationPage.visible = False
    if modeID == 6: # Recording management
      self.ui.welcomePage.visible = False
      self.ui.configurationPage.visible = False
      self.ui.trainingPage.visible = False
      self.ui.trainingSessionPage.visible = False
      self.ui.evaluationPage.visible = True
    if modeID == 7: # configuration
      self.ui.welcomePage.visible = False
      self.ui.configurationPage.visible = True
      self.ui.trainingPage.visible = False
      self.ui.trainingSessionPage.visible = False
      self.ui.evaluationPage.visible = False

  #------------------------------------------------------------------------------
  def updateParticipantsTable(self):
    """
    Updates content of participants table by reading the database in root directory.
    """
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get current app mode
    appMode = parameterNode.GetParameter(self.trainUsWidget.logic.selectedAppModeParameterName)

    # Select target table to update according to app mode
    if appMode == 'TRAINING':
      uiPanel = self.ui.ParticipantSelectionPanel
    elif appMode == 'EVALUATION':
      uiPanel = self.ui.EvaluationPanel
    else:
      logging.error('Home.updateParticipantsTable: Unknown app mode')
      return

    # Get data from directory
    participantInfo_list = self.trainUsWidget.logic.dataManager.readRootDirectory()

    # Filter participants according to search text
    searchText = uiPanel.ui.participantSearchText.text
    if searchText is not '':
      participantInfo_list = self.trainUsWidget.logic.dataManager.filterParticipantInfoListFromSearchText(participantInfo_list, searchText)

    ## Get table widget
    tableWidget = uiPanel.ui.participantsTable

    ## Reset table
    tableWidget.clearContents()

    ## Update table content
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

    # Get current app mode
    appMode = parameterNode.GetParameter(self.trainUsWidget.logic.selectedAppModeParameterName)

    # Select target table to update according to app mode
    if appMode == 'TRAINING':
      uiPanel = self.ui.ParticipantSelectionPanel
    elif appMode == 'EVALUATION':
      uiPanel = self.ui.EvaluationPanel
    else:
      logging.error('Home.updateParticipantsTableSelection: Unknown app mode')
      return

    # Get table widget
    tableWidget = uiPanel.ui.participantsTable

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
    selectedParticipantInfo = self.trainUsWidget.logic.dataManager.getParticipantInfoFromID(selectedParticipantID)

    # Create string to display in GUI
    if selectedParticipantInfo:
      participantID = selectedParticipantInfo['id']
      participantName= selectedParticipantInfo['name']
      participantSurname = selectedParticipantInfo['surname']
      selectedParticipantLabel = f'[{participantID}] {participantSurname}, {participantName}'
    else:
      selectedParticipantLabel = ''

    # Update GUI
    self.ui.EvaluationPanel.ui.participantSelectionText.text = selectedParticipantLabel

    #
    # Update table content
    #

    # Get table widget
    tableWidget = self.ui.EvaluationPanel.ui.recordingsTable

    # Reset table
    tableWidget.clearContents()
    tableWidget.sortingEnabled = False

    # Update table if participant is selected
    if selectedParticipantID is not '':
      # Get data from directory
      recordingInfo_list = self.trainUsWidget.logic.dataManager.readParticipantDirectory(selectedParticipantID)

      # Update table content
      if len(recordingInfo_list) >= 0:
        numRecordings = len(recordingInfo_list)
        tableWidget.setRowCount(numRecordings)
        for recordingPos in range(numRecordings):
          recordingIDTableItem = qt.QTableWidgetItem(recordingInfo_list[recordingPos]['id'])
          recordingDateTableItem = qt.QTableWidgetItem(recordingInfo_list[recordingPos]['date'])
          recordingTimeTableItem = qt.QTableWidgetItem(recordingInfo_list[recordingPos]['time'])
          recordingExerciseTableItem = qt.QTableWidgetItem(recordingInfo_list[recordingPos]['exercise'])
          recordingDurationTableItem = qt.QTableWidgetItem(recordingInfo_list[recordingPos]['duration'])
          tableWidget.setItem(recordingPos, 0, recordingIDTableItem)
          tableWidget.setItem(recordingPos, 1, recordingDateTableItem)
          tableWidget.setItem(recordingPos, 2, recordingTimeTableItem)
          tableWidget.setItem(recordingPos, 3, recordingExerciseTableItem)
          tableWidget.setItem(recordingPos, 4, recordingDurationTableItem)
      else:
        tableWidget.setRowCount(0)
        logging.debug('Home.updateRecordingsTable: No recordings found in database...')
    else:
      tableWidget.setRowCount(0)
      logging.debug('Home.updateRecordingsTable: No participant is selected')
    tableWidget.sortingEnabled = True

  #------------------------------------------------------------------------------
  def updateReviewSelectionPanel(self):
    """
    Update review selection panel indicating selected participant and configuration.
    """
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get information from selected participant
    participantSelected = self.trainUsWidget.logic.dataManager.isParticipantSelected()
    if participantSelected:
      selectedParticipantInfo = self.trainUsWidget.logic.dataManager.getParticipantInfoFromSelection()
      selectedParticipantID = selectedParticipantInfo['id']
      selectedParticipantName = selectedParticipantInfo['name']
      selectedParticipantSurname = selectedParticipantInfo['surname']
    else:
      selectedParticipantID = ''
      selectedParticipantName = ''
      selectedParticipantSurname = ''

    # Get selected hardware configuration
    selectedUltrasoundDevice = parameterNode.GetParameter(self.trainUsWidget.logic.selectedUltrasoundDeviceParameterName)
    selectedTrackingSystem = parameterNode.GetParameter(self.trainUsWidget.logic.selectedTrackingSystemParameterName)
    selectedSimulationPhantom = parameterNode.GetParameter(self.trainUsWidget.logic.selectedSimulationPhantomParameterName)

    # Update GUI in dashboard tab
    self.ui.ReviewSelectionPanel.ui.participantNameText.text = selectedParticipantName
    self.ui.ReviewSelectionPanel.ui.participantSurnameText.text = selectedParticipantSurname
    self.ui.ReviewSelectionPanel.ui.participantIDText.text = selectedParticipantID
    self.ui.ReviewSelectionPanel.ui.ultrasoundDeviceText.text = selectedUltrasoundDevice
    self.ui.ReviewSelectionPanel.ui.trackingSystemText.text = selectedTrackingSystem
    self.ui.ReviewSelectionPanel.ui.simulationPhantomText.text = selectedSimulationPhantom

  #------------------------------------------------------------------------------
  def updateTrainingSessionPanel(self):
    """
    Update training session panel indicating selected participant, configuration, and date.
    """
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get information from selected participant
    participantSelected = self.trainUsWidget.logic.dataManager.isParticipantSelected()
    if participantSelected:
      selectedParticipantInfo = self.trainUsWidget.logic.dataManager.getParticipantInfoFromSelection()
      selectedParticipantID = selectedParticipantInfo['id']
      selectedParticipantName = selectedParticipantInfo['name']
      selectedParticipantSurname = selectedParticipantInfo['surname']
    else:
      selectedParticipantID = ''
      selectedParticipantName = ''
      selectedParticipantSurname = ''

    # Get current date
    from datetime import datetime
    dateLabel = datetime.now().strftime('%Y-%m-%d')

    # Get selected hardware configuration
    selectedUltrasoundDevice = parameterNode.GetParameter(self.trainUsWidget.logic.selectedUltrasoundDeviceParameterName)
    selectedTrackingSystem = parameterNode.GetParameter(self.trainUsWidget.logic.selectedTrackingSystemParameterName)
    selectedSimulationPhantom = parameterNode.GetParameter(self.trainUsWidget.logic.selectedSimulationPhantomParameterName)

    # Update GUI in training session info box
    self.ui.TrainingSessionPanel.ui.participantLabel.text = f'[{selectedParticipantID}] {selectedParticipantSurname}, {selectedParticipantName}'
    self.ui.TrainingSessionPanel.ui.dateTimeLabel.text = dateLabel
    self.ui.TrainingSessionPanel.ui.hardwareSetUpLabel.text = f'{selectedUltrasoundDevice} / {selectedTrackingSystem} / {selectedSimulationPhantom}'

  #------------------------------------------------------------------------------
  def updateConfigurationPanel(self):
    """
    Update configuration panel to indicate connection status.
    """
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get PLUS connection status
    plusConnectionStatus = parameterNode.GetParameter(self.trainUsWidget.logic.plusConnectionStatusParameterName)
    plusServerRunning = parameterNode.GetParameter(self.trainUsWidget.logic.plusServerRunningParameterName)

    # Update GUI in training session info box
    self.ui.ConfigurationPanel.ui.connectionStatusText.text = plusConnectionStatus
    if plusServerRunning == 'True':
      self.ui.ConfigurationPanel.ui.ultrasoundDeviceComboBox.enabled = False
      self.ui.ConfigurationPanel.ui.trackingSystemComboBox.enabled = False
      self.ui.ConfigurationPanel.ui.simulationPhantomComboBox.enabled = False
    else:
      self.ui.ConfigurationPanel.ui.ultrasoundDeviceComboBox.enabled = True
      self.ui.ConfigurationPanel.ui.trackingSystemComboBox.enabled = True
      self.ui.ConfigurationPanel.ui.simulationPhantomComboBox.enabled = True

    # Update GUI config panel
    self.ui.ConfigurationPanel.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def exitApplicationMessageBox(self):
    """
    Display message box for the user to confirm if the participant data must be deleted.
    :return bool: True if delete action is confirmed, False otherwise
    """
    confirmExit = qt.QMessageBox()
    confirmExit.setIcon(qt.QMessageBox.Warning)
    confirmExit.setWindowTitle(self.logic.home_exitAppMessageBoxTitle) #TODO: Use class constants instead
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
    self.parameterNode = None #TODO: Remove parameter node handling from this class. Each class should use the main TrainUS parameter node. I see other classes do that, great, but they still have their set/getParameterNode functions. Please remove those to reduce confusion.

    # Store whether python console was floating so that it is restored when hidden
    self.pythonConsoleWasFloating = False

    # Constants
    #TODO:

    # UI variables
    self.home_exitAppMessageBoxTitle = '' #TODO: Define these not as member variables but class variables, outside the body of the constructor. Use capital letters like HOME_EXIT_APP...
    self.home_exitAppMessageBoxLabel = ''
    self.newParticipantWarningMessageText = ''
    self.editParticipantWarningMessageText = ''
    self.participants_deleteMessageBoxTitle = ''
    self.participants_deleteMessageBoxLabel = ''
    self.recordings_deleteMessageBoxTitle = ''
    self.recordings_deleteMessageBoxLabel = ''

    #TODO: Remove parameter node related things
    # Default parameters map
    self.defaultParameters = {}
    # self.defaultParameters["DecimationFactor"] = 0.85

    # Parameter node reference roles
    # self.modelReferenceRolePrefix = 'Model_'

    # Setup keyboard shortcuts
    self.setupKeyboardShortcuts()

  #------------------------------------------------------------------------------
  def observeParameterNode(self):
    """
    Add observe to TrainUS parameter node.
    """
    # Get parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('updateGUIFromMRML: Failed to get parameter node')
      return

    # Add observations on referenced nodes
    if not self.hasObserver(parameterNode, vtk.vtkCommand.ModifiedEvent, self.moduleWidget.updateGUIFromMRML):
      self.addObserver(parameterNode, vtk.vtkCommand.ModifiedEvent, self.moduleWidget.updateGUIFromMRML)

    # Update widgets
    self.moduleWidget.updateGUIFromMRML()

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
    self.moduleWidget.ui.fullScreenButton.setText(languageTexts['Home.fullScreenButton'])
    self.moduleWidget.ui.backToSlicerButton.setText(languageTexts['Home.backToSlicerButton'])
    self.moduleWidget.ui.exitAppButton.setText(languageTexts['Home.exitAppButton'])
    self.moduleWidget.ui.mainTrainingModeButton.setText(languageTexts['Home.mainTrainingModeButton'])
    self.moduleWidget.ui.mainEvaluationModeButton.setText(languageTexts['Home.mainEvaluationModeButton'])
    self.moduleWidget.ui.configurationButton.setText(languageTexts['Home.configurationButton'])
    self.moduleWidget.ui.step1NavigationLabel.setText(languageTexts['Home.step1NavigationLabel'])
    self.moduleWidget.ui.step2NavigationLabel.setText(languageTexts['Home.step2NavigationLabel'])
    self.moduleWidget.ui.step3NavigationLabel.setText(languageTexts['Home.step3NavigationLabel'])
    self.moduleWidget.ui.step4NavigationLabel.setText(languageTexts['Home.step4NavigationLabel'])
    self.home_exitAppMessageBoxTitle = languageTexts['Home.exitAppMessageBoxTitle']
    self.home_exitAppMessageBoxLabel = languageTexts['Home.exitAppMessageBoxText_1'] + '\n\n' + languageTexts['Home.exitAppMessageBoxText_2']
    ## Configuration
    self.moduleWidget.ui.ConfigurationPanel.ui.label_1.setText(languageTexts['Configuration.label_1'])
    self.moduleWidget.ui.ConfigurationPanel.ui.label_2.setText(languageTexts['Configuration.label_2'])
    self.moduleWidget.ui.ConfigurationPanel.ui.label_3.setText(languageTexts['Configuration.label_3'])
    self.moduleWidget.ui.ConfigurationPanel.ui.label_4.setText(languageTexts['Configuration.label_4'])
    self.moduleWidget.ui.ConfigurationPanel.ui.label_5.setText(languageTexts['Configuration.label_5'])
    self.moduleWidget.ui.ConfigurationPanel.ui.hardwareConnectionGroupBox.setTitle(languageTexts['Configuration.hardwareConnectionGroupBox'])
    self.moduleWidget.ui.ConfigurationPanel.ui.ultrasoundImagingGroupBox.setTitle(languageTexts['Configuration.ultrasoundImagingGroupBox'])
    self.moduleWidget.ui.ConfigurationPanel.ui.trackingSystemGrouBox.setTitle(languageTexts['Configuration.trackingSystemGrouBox'])
    self.moduleWidget.ui.ConfigurationPanel.ui.plusConnectionButton.setText(languageTexts['Configuration.plusConnectionButton'])
    self.moduleWidget.ui.ConfigurationPanel.ui.ultrasoundDisplaySettingsButton.setText(languageTexts['Configuration.ultrasoundDisplaySettingsButton'])
    self.moduleWidget.ui.ConfigurationPanel.ui.ultrasoundProbeCalibrationButton.setText(languageTexts['Configuration.ultrasoundProbeCalibrationButton'])
    self.moduleWidget.ui.ConfigurationPanel.ui.toolTrackingStatusButton.setText(languageTexts['Configuration.toolTrackingStatusButton'])
    self.moduleWidget.ui.ConfigurationPanel.ui.toolPivotCalibrationButton.setText(languageTexts['Configuration.toolPivotCalibrationButton'])
    self.moduleWidget.ui.ConfigurationPanel.ui.phantomRegistrationButton.setText(languageTexts['Configuration.phantomRegistrationButton'])
    self.moduleWidget.ui.ConfigurationPanel.ui.previousPageButton.setText(languageTexts['Configuration.previousPageButton'])
    ## Participant selection
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.label_1.setText(languageTexts['ParticipantSelection.label_1'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.label_2.setText(languageTexts['ParticipantSelection.label_2'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.participantsTable.setHorizontalHeaderItem(0, qt.QTableWidgetItem(languageTexts['ParticipantSelection.participantsTable_column1']))
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.participantsTable.setHorizontalHeaderItem(1, qt.QTableWidgetItem(languageTexts['ParticipantSelection.participantsTable_column2']))
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.participantsTable.setHorizontalHeaderItem(2, qt.QTableWidgetItem(languageTexts['ParticipantSelection.participantsTable_column3']))
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.participantsTable.setHorizontalHeaderItem(3, qt.QTableWidgetItem(languageTexts['ParticipantSelection.participantsTable_column4']))
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.participantsTable.setHorizontalHeaderItem(4, qt.QTableWidgetItem(languageTexts['ParticipantSelection.participantsTable_column5']))
    #self.moduleWidget.ui.ParticipantSelectionPanel.ui.participantOptionsGroupBox.setTitle(languageTexts['ParticipantSelection.participantOptionsGroupBox'])
    #self.moduleWidget.ui.ParticipantSelectionPanel.ui.checkRecordingsButton.setText(languageTexts['ParticipantSelection.checkRecordingsButton'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.newParticipantButton.setText(languageTexts['ParticipantSelection.newParticipantButton'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.editParticipantButton.setText(languageTexts['ParticipantSelection.editParticipantButton'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.deleteParticipantButton.setText(languageTexts['ParticipantSelection.deleteParticipantButton'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.newParticipantGroupBox.setTitle(languageTexts['ParticipantSelection.newParticipantGroupBox'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.newParticipantLabel_1.setText(languageTexts['ParticipantSelection.newParticipantLabel_1'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.newParticipantLabel_2.setText(languageTexts['ParticipantSelection.newParticipantLabel_2'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.newParticipantLabel_3.setText(languageTexts['ParticipantSelection.newParticipantLabel_3'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.newParticipantLabel_4.setText(languageTexts['ParticipantSelection.newParticipantLabel_4'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.newParticipantSaveButton.setText(languageTexts['ParticipantSelection.newParticipantSaveButton'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.newParticipantCancelButton.setText(languageTexts['ParticipantSelection.newParticipantCancelButton'])
    self.newParticipantWarningMessageText = languageTexts['ParticipantSelection.newParticipantWarningMessageText']
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.editParticipantGroupBox.setTitle(languageTexts['ParticipantSelection.editParticipantGroupBox'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.editParticipantLabel_1.setText(languageTexts['ParticipantSelection.editParticipantLabel_1'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.editParticipantLabel_2.setText(languageTexts['ParticipantSelection.editParticipantLabel_2'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.editParticipantLabel_3.setText(languageTexts['ParticipantSelection.editParticipantLabel_3'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.editParticipantLabel_4.setText(languageTexts['ParticipantSelection.editParticipantLabel_4'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.editParticipantSaveButton.setText(languageTexts['ParticipantSelection.editParticipantSaveButton'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.editParticipantCancelButton.setText(languageTexts['ParticipantSelection.editParticipantCancelButton'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.previousPageButton.setText(languageTexts['ParticipantSelection.previousPageButton'])
    self.moduleWidget.ui.ParticipantSelectionPanel.ui.nextPageButton.setText(languageTexts['ParticipantSelection.nextPageButton'])
    self.editParticipantWarningMessageText = languageTexts['ParticipantSelection.editParticipantWarningMessageText']
    self.participants_deleteMessageBoxTitle = languageTexts['ParticipantSelection.deleteMessageBoxTitle']
    self.participants_deleteMessageBoxLabel = languageTexts['ParticipantSelection.deleteMessageBoxText_1'] + '\n\n' + languageTexts['ParticipantSelection.deleteMessageBoxText_2']
    ## Hardware selection
    self.moduleWidget.ui.HardwareSelectionPanel.ui.label_1.setText(languageTexts['HardwareSelection.label_1'])
    self.moduleWidget.ui.HardwareSelectionPanel.ui.label_2.setText(languageTexts['HardwareSelection.label_2'])
    self.moduleWidget.ui.HardwareSelectionPanel.ui.label_3.setText(languageTexts['HardwareSelection.label_3'])
    self.moduleWidget.ui.HardwareSelectionPanel.ui.label_4.setText(languageTexts['HardwareSelection.label_4'])
    self.moduleWidget.ui.HardwareSelectionPanel.ui.label_5.setText(languageTexts['HardwareSelection.label_5'])
    self.moduleWidget.ui.HardwareSelectionPanel.ui.previousPageButton.setText(languageTexts['HardwareSelection.previousPageButton'])
    self.moduleWidget.ui.HardwareSelectionPanel.ui.nextPageButton.setText(languageTexts['HardwareSelection.nextPageButton'])
    ## Review selection
    self.moduleWidget.ui.ReviewSelectionPanel.ui.label_1.setText(languageTexts['ReviewSelection.label_1'])
    self.moduleWidget.ui.ReviewSelectionPanel.ui.participantGroupBox.setTitle(languageTexts['ReviewSelection.participantGroupBox'])
    self.moduleWidget.ui.ReviewSelectionPanel.ui.participantNameLabel.setText(languageTexts['ReviewSelection.participantNameLabel'])
    self.moduleWidget.ui.ReviewSelectionPanel.ui.participantSurnameLabel.setText(languageTexts['ReviewSelection.participantSurnameLabel'])
    self.moduleWidget.ui.ReviewSelectionPanel.ui.participantIDLabel.setText(languageTexts['ReviewSelection.participantIDLabel'])
    self.moduleWidget.ui.ReviewSelectionPanel.ui.editParticipantSelectionButton.setText(languageTexts['ReviewSelection.editParticipantSelectionButton'])
    self.moduleWidget.ui.ReviewSelectionPanel.ui.configurationGroupBox.setTitle(languageTexts['ReviewSelection.configurationGroupBox'])
    self.moduleWidget.ui.ReviewSelectionPanel.ui.ultrasoundDeviceLabel.setText(languageTexts['ReviewSelection.ultrasoundDeviceLabel'])
    self.moduleWidget.ui.ReviewSelectionPanel.ui.trackingSystemLabel.setText(languageTexts['ReviewSelection.trackingSystemLabel'])
    self.moduleWidget.ui.ReviewSelectionPanel.ui.simulationPhantomLabel.setText(languageTexts['ReviewSelection.simulationPhantomLabel'])
    self.moduleWidget.ui.ReviewSelectionPanel.ui.editHardwareSelectionButton.setText(languageTexts['ReviewSelection.editHardwareSelectionButton'])
    self.moduleWidget.ui.ReviewSelectionPanel.ui.previousPageButton.setText(languageTexts['ReviewSelection.previousPageButton'])
    self.moduleWidget.ui.ReviewSelectionPanel.ui.nextPageButton.setText(languageTexts['ReviewSelection.nextPageButton'])
    ## Plug and play
    self.moduleWidget.ui.PlugAndPlayPanel.ui.label_1.setText(languageTexts['PlugAndPlay.label_1'])
    self.moduleWidget.ui.PlugAndPlayPanel.ui.hardwareConnectionGroupBox.setTitle(languageTexts['PlugAndPlay.hardwareConnectionGroupBox'])
    self.moduleWidget.ui.PlugAndPlayPanel.ui.connectHardwareButton.setText(languageTexts['PlugAndPlay.connectHardwareButton'])
    self.moduleWidget.ui.PlugAndPlayPanel.ui.connectionStatusLabel.setText(languageTexts['PlugAndPlay.connectionStatusLabel'])
    self.moduleWidget.ui.PlugAndPlayPanel.ui.previousPageButton.setText(languageTexts['PlugAndPlay.previousPageButton'])
    self.moduleWidget.ui.PlugAndPlayPanel.ui.nextPageButton.setText(languageTexts['PlugAndPlay.nextPageButton'])
    ## Training session
    self.moduleWidget.ui.TrainingSessionPanel.ui.trainingInfoGroupBox.setTitle(languageTexts['TrainingSession.trainingInfoGroupBox'])
    self.moduleWidget.ui.TrainingSessionPanel.ui.participantInfoLabel_1.setText(languageTexts['TrainingSession.participantInfoLabel_1'])
    self.moduleWidget.ui.TrainingSessionPanel.ui.participantInfoLabel_2.setText(languageTexts['TrainingSession.participantInfoLabel_2'])
    self.moduleWidget.ui.TrainingSessionPanel.ui.participantInfoLabel_3.setText(languageTexts['TrainingSession.participantInfoLabel_3'])
    self.moduleWidget.ui.TrainingSessionPanel.ui.trainingTabWidget.setTabText(0, languageTexts['TrainingSession.basicTrainingTab'])
    self.moduleWidget.ui.TrainingSessionPanel.ui.trainingTabWidget.setTabText(1, languageTexts['TrainingSession.advancedTrainingTab'])
    self.moduleWidget.ui.TrainingSessionPanel.ui.finishTrainingButton.setText(languageTexts['TrainingSession.finishTrainingButton'])
    ## Evaluation
    self.moduleWidget.ui.EvaluationPanel.ui.tabWidget.setTabText(0, languageTexts['Evaluation.participantsTab'])
    self.moduleWidget.ui.EvaluationPanel.ui.tabWidget.setTabText(1, languageTexts['Evaluation.recordingsTab'])
    self.moduleWidget.ui.EvaluationPanel.ui.label_1.setText(languageTexts['ParticipantSelection.label_1'])
    self.moduleWidget.ui.EvaluationPanel.ui.label_2.setText(languageTexts['ParticipantSelection.label_2'])
    self.moduleWidget.ui.EvaluationPanel.ui.participantsTable.setHorizontalHeaderItem(0, qt.QTableWidgetItem(languageTexts['ParticipantSelection.participantsTable_column1']))
    self.moduleWidget.ui.EvaluationPanel.ui.participantsTable.setHorizontalHeaderItem(1, qt.QTableWidgetItem(languageTexts['ParticipantSelection.participantsTable_column2']))
    self.moduleWidget.ui.EvaluationPanel.ui.participantsTable.setHorizontalHeaderItem(2, qt.QTableWidgetItem(languageTexts['ParticipantSelection.participantsTable_column3']))
    self.moduleWidget.ui.EvaluationPanel.ui.participantsTable.setHorizontalHeaderItem(3, qt.QTableWidgetItem(languageTexts['ParticipantSelection.participantsTable_column4']))
    self.moduleWidget.ui.EvaluationPanel.ui.participantsTable.setHorizontalHeaderItem(4, qt.QTableWidgetItem(languageTexts['ParticipantSelection.participantsTable_column5']))
    self.moduleWidget.ui.EvaluationPanel.ui.participantOptionsGroupBox.setTitle(languageTexts['ParticipantSelection.participantOptionsGroupBox'])
    self.moduleWidget.ui.EvaluationPanel.ui.checkRecordingsButton.setText(languageTexts['ParticipantSelection.checkRecordingsButton'])
    self.moduleWidget.ui.EvaluationPanel.ui.newParticipantButton.setText(languageTexts['ParticipantSelection.newParticipantButton'])
    self.moduleWidget.ui.EvaluationPanel.ui.editParticipantButton.setText(languageTexts['ParticipantSelection.editParticipantButton'])
    self.moduleWidget.ui.EvaluationPanel.ui.deleteParticipantButton.setText(languageTexts['ParticipantSelection.deleteParticipantButton'])
    self.moduleWidget.ui.EvaluationPanel.ui.newParticipantGroupBox.setTitle(languageTexts['ParticipantSelection.newParticipantGroupBox'])
    self.moduleWidget.ui.EvaluationPanel.ui.newParticipantLabel_1.setText(languageTexts['ParticipantSelection.newParticipantLabel_1'])
    self.moduleWidget.ui.EvaluationPanel.ui.newParticipantLabel_2.setText(languageTexts['ParticipantSelection.newParticipantLabel_2'])
    self.moduleWidget.ui.EvaluationPanel.ui.newParticipantLabel_3.setText(languageTexts['ParticipantSelection.newParticipantLabel_3'])
    self.moduleWidget.ui.EvaluationPanel.ui.newParticipantLabel_4.setText(languageTexts['ParticipantSelection.newParticipantLabel_4'])
    self.moduleWidget.ui.EvaluationPanel.ui.newParticipantSaveButton.setText(languageTexts['ParticipantSelection.newParticipantSaveButton'])
    self.moduleWidget.ui.EvaluationPanel.ui.newParticipantCancelButton.setText(languageTexts['ParticipantSelection.newParticipantCancelButton'])
    self.newParticipantWarningMessageText = languageTexts['ParticipantSelection.newParticipantWarningMessageText']
    self.moduleWidget.ui.EvaluationPanel.ui.editParticipantGroupBox.setTitle(languageTexts['ParticipantSelection.editParticipantGroupBox'])
    self.moduleWidget.ui.EvaluationPanel.ui.editParticipantLabel_1.setText(languageTexts['ParticipantSelection.editParticipantLabel_1'])
    self.moduleWidget.ui.EvaluationPanel.ui.editParticipantLabel_2.setText(languageTexts['ParticipantSelection.editParticipantLabel_2'])
    self.moduleWidget.ui.EvaluationPanel.ui.editParticipantLabel_3.setText(languageTexts['ParticipantSelection.editParticipantLabel_3'])
    self.moduleWidget.ui.EvaluationPanel.ui.editParticipantLabel_4.setText(languageTexts['ParticipantSelection.editParticipantLabel_4'])
    self.moduleWidget.ui.EvaluationPanel.ui.editParticipantSaveButton.setText(languageTexts['ParticipantSelection.editParticipantSaveButton'])
    self.moduleWidget.ui.EvaluationPanel.ui.editParticipantCancelButton.setText(languageTexts['ParticipantSelection.editParticipantCancelButton'])
    self.editParticipantWarningMessageText = languageTexts['ParticipantSelection.editParticipantWarningMessageText']
    self.participants_deleteMessageBoxTitle = languageTexts['ParticipantSelection.deleteMessageBoxTitle']
    self.participants_deleteMessageBoxLabel = languageTexts['ParticipantSelection.deleteMessageBoxText_1'] + '\n\n' + languageTexts['ParticipantSelection.deleteMessageBoxText_2']
    self.moduleWidget.ui.EvaluationPanel.ui.label_3.setText(languageTexts['Recordings.label_3'])
    self.moduleWidget.ui.EvaluationPanel.ui.label_4.setText(languageTexts['Recordings.label_4'])
    self.moduleWidget.ui.EvaluationPanel.ui.recordingsTable.setHorizontalHeaderItem(0, qt.QTableWidgetItem(languageTexts['Recordings.recordingsTable_column1']))
    self.moduleWidget.ui.EvaluationPanel.ui.recordingsTable.setHorizontalHeaderItem(1, qt.QTableWidgetItem(languageTexts['Recordings.recordingsTable_column2']))
    self.moduleWidget.ui.EvaluationPanel.ui.recordingsTable.setHorizontalHeaderItem(2, qt.QTableWidgetItem(languageTexts['Recordings.recordingsTable_column3']))
    self.moduleWidget.ui.EvaluationPanel.ui.recordingsTable.setHorizontalHeaderItem(3, qt.QTableWidgetItem(languageTexts['Recordings.recordingsTable_column4']))
    self.moduleWidget.ui.EvaluationPanel.ui.recordingsTable.setHorizontalHeaderItem(4, qt.QTableWidgetItem(languageTexts['Recordings.recordingsTable_column5']))
    self.moduleWidget.ui.EvaluationPanel.ui.recordingOptionsGroupBox.setTitle(languageTexts['Recordings.recordingOptionsGroupBox'])
    self.moduleWidget.ui.EvaluationPanel.ui.recordingDetailsButton.setText(languageTexts['Recordings.recordingDetailsButton'])
    self.moduleWidget.ui.EvaluationPanel.ui.evaluateRecordingButton.setText(languageTexts['Recordings.evaluateRecordingButton'])
    self.moduleWidget.ui.EvaluationPanel.ui.deleteRecordingButton.setText(languageTexts['Recordings.deleteRecordingButton'])
    self.moduleWidget.ui.EvaluationPanel.ui.recordingDetailsGroupBox.setTitle(languageTexts['Recordings.recordingDetailsGroupBox'])
    self.moduleWidget.ui.EvaluationPanel.ui.recordingDetailsLabel_1.setText(languageTexts['Recordings.recordingDetailsLabel_1'])
    self.moduleWidget.ui.EvaluationPanel.ui.recordingDetailsLabel_2.setText(languageTexts['Recordings.recordingDetailsLabel_2'])
    self.moduleWidget.ui.EvaluationPanel.ui.recordingDetailsLabel_3.setText(languageTexts['Recordings.recordingDetailsLabel_3'])
    self.moduleWidget.ui.EvaluationPanel.ui.recordingDetailsLabel_4.setText(languageTexts['Recordings.recordingDetailsLabel_4'])
    self.moduleWidget.ui.EvaluationPanel.ui.recordingDetailsLabel_5.setText(languageTexts['Recordings.recordingDetailsLabel_5'])
    self.moduleWidget.ui.EvaluationPanel.ui.recordingDetailsLabel_6.setText(languageTexts['Recordings.recordingDetailsLabel_6'])
    self.recordings_deleteMessageBoxTitle = languageTexts['Recordings.deleteMessageBoxTitle']
    self.recordings_deleteMessageBoxLabel = languageTexts['Recordings.deleteMessageBoxText_1'] + '\n\n' + languageTexts['Recordings.deleteMessageBoxText_2']
    self.moduleWidget.ui.EvaluationPanel.ui.previousPageButton.setText(languageTexts['Evaluation.previousPageButton'])

    # Adjust width of table columns to new horizontal headers
    COLUMN_H_MARGIN = 100
    self.addMarginToColumnWidth(self.moduleWidget.ui.ParticipantSelectionPanel.ui.participantsTable, COLUMN_H_MARGIN)
    self.addMarginToColumnWidth(self.moduleWidget.ui.EvaluationPanel.ui.recordingsTable, COLUMN_H_MARGIN)

  #------------------------------------------------------------------------------
  def addMarginToColumnWidth(self, tableWidget, margin):
    tableWidget.horizontalHeader().stretchLastSection = False
    tableWidget.resizeColumnsToContents()
    numColumns = tableWidget.columnCount
    for col in range(numColumns):
      tableWidget.setColumnWidth(col, tableWidget.columnWidth(col) + margin)
    tableWidget.horizontalHeader().stretchLastSection = True

  #------------------------------------------------------------------------------
  def switchAppMode(self, mode):
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Store app mode in parameter node
    parameterNode.SetParameter(self.trainUsWidget.logic.selectedAppModeParameterName, mode)


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

from __main__ import vtk, qt, ctk, slicer
import logging
import os

# TrainUS parameters
import TrainUSLib.TrainUSParameters as Parameters

#------------------------------------------------------------------------------
#
# Evaluation
#
#------------------------------------------------------------------------------
class Evaluation(qt.QWidget):

  def __init__(self, parent=None):
    super(Evaluation, self).__init__(parent)

    # Define member variables
    self.homeWidget = None # Set externally after creation
    self.trainUsWidget = slicer.trainUsWidget

    # GUI flags    
    self.newParticipantVisible = False
    self.editParticipantVisible = False

  #------------------------------------------------------------------------------
  # Clean up when application is closed
  def cleanup(self):
    logging.debug('Evaluation.cleanup')

    self.disconnect()

  #------------------------------------------------------------------------------
  def setupUi(self):
    logging.debug('Evaluation.setupUi')

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiFilePath = os.path.join(self.homeWidget.logic.fileDir, 'Resources', 'UI', 'Evaluation.ui')
    uiWidget = slicer.util.loadUI(uiFilePath)
    self.sectionLayout = qt.QVBoxLayout(self)
    self.sectionLayout.setContentsMargins(0, 0, 0, 0)
    self.sectionLayout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Customize widgets - participants tab
    self.ui.newParticipantGroupBox.visible = False
    self.ui.editParticipantGroupBox.visible = False
    self.ui.checkRecordingsButton.enabled = False
    self.ui.newParticipantButton.enabled = True
    self.ui.editParticipantButton.enabled = False
    self.ui.deleteParticipantButton.enabled = False
    self.ui.newParticipantSaveButton.enabled = True 
    self.ui.newParticipantCancelButton.enabled = True
    self.ui.editParticipantSaveButton.enabled = True 
    self.ui.editParticipantCancelButton.enabled = True

    # New participant input
    self.ui.newParticipantNameText.setText('')
    self.ui.newParticipantSurnameText.setText('')
    self.ui.newParticipantEmailText.setText('')    
    self.ui.newParticipantBirthDateEdit.setDate(qt.QDate().currentDate())
    self.ui.newParticipantBirthDateEdit.setDisplayFormat('MM.dd.yyyy')

    # Edit participant input
    self.ui.editParticipantNameText.setText('')
    self.ui.editParticipantSurnameText.setText('')
    self.ui.editParticipantEmailText.setText('')    
    self.ui.editParticipantBirthDateEdit.setDate(qt.QDate().currentDate())
    self.ui.editParticipantBirthDateEdit.setDisplayFormat('MM.dd.yyyy')

    # Invalid input warnings
    self.ui.newParticipantNameWarning.setText('')
    self.ui.newParticipantNameWarning.setStyleSheet("QLabel { color : red }")
    self.ui.newParticipantSurnameWarning.setText('')
    self.ui.newParticipantSurnameWarning.setStyleSheet("QLabel { color : red }")
    self.ui.newParticipantEmailWarning.setText('')
    self.ui.newParticipantEmailWarning.setStyleSheet("QLabel { color : red }")
    self.ui.newParticipantWarningMessageText.setText('')
    self.ui.newParticipantWarningMessageText.setStyleSheet("QLabel { color : red }")
    self.ui.editParticipantNameWarning.setText('')
    self.ui.editParticipantNameWarning.setStyleSheet("QLabel { color : red }")
    self.ui.editParticipantSurnameWarning.setText('')
    self.ui.editParticipantSurnameWarning.setStyleSheet("QLabel { color : red }")
    self.ui.editParticipantEmailWarning.setText('')
    self.ui.editParticipantEmailWarning.setStyleSheet("QLabel { color : red }")
    self.ui.editParticipantWarningMessageText.setText('')
    self.ui.editParticipantWarningMessageText.setStyleSheet("QLabel { color : red }")

    # Customize widgets - recordings tab
    self.ui.recordingDetailsGroupBox.visible = self.ui.recordingDetailsButton.checked
    self.ui.recordingDetailsButton.enabled = self.trainUsWidget.logic.recordingManager.isRecordingSelected()
    
    # Setup GUI connections
    self.setupConnections()

  #------------------------------------------------------------------------------
  def setupConnections(self):
    logging.debug('Evaluation.setupConnections')

    # Participants tab
    self.ui.participantSearchText.textChanged.connect(self.onParticipantSearchTextChanged)
    self.ui.participantsTable.itemSelectionChanged.connect(self.onParticipantsTableItemSelected)
    self.ui.participantsTable.itemDoubleClicked.connect(self.onParticipantsTableItemDoubleClicked)
    self.ui.checkRecordingsButton.clicked.connect(self.onCheckRecordingsButtonClicked)
    self.ui.newParticipantButton.clicked.connect(self.onNewParticipantButtonClicked)
    self.ui.editParticipantButton.clicked.connect(self.onEditParticipantButtonClicked)
    self.ui.deleteParticipantButton.clicked.connect(self.onDeleteParticipantButtonClicked)
    self.ui.newParticipantSaveButton.clicked.connect(self.onNewParticipantSaveButtonClicked)
    self.ui.newParticipantCancelButton.clicked.connect(self.onNewParticipantCancelButtonClicked)
    self.ui.editParticipantSaveButton.clicked.connect(self.onEditParticipantSaveButtonClicked)
    self.ui.editParticipantCancelButton.clicked.connect(self.onEditParticipantCancelButtonClicked)
    # Recordings tab
    self.ui.recordingsTable.itemSelectionChanged.connect(self.onRecordingsTableItemSelected)
    self.ui.recordingsTable.itemDoubleClicked.connect(self.onRecordingsTableItemDoubleClicked)
    self.ui.recordingDetailsButton.clicked.connect(self.onRecordingDetailsButtonClicked)
    self.ui.evaluateRecordingButton.clicked.connect(self.onEvaluateRecordingButtonClicked)
    self.ui.deleteRecordingButton.clicked.connect(self.onDeleteRecordingButtonClicked)
    # Navigation bar    
    self.ui.previousPageButton.clicked.connect(self.onPreviousPageButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    logging.debug('Evaluation.disconnect')

    # Participants tab
    self.ui.participantSearchText.textChanged.disconnect()
    self.ui.participantsTable.itemSelectionChanged.disconnect()
    self.ui.participantsTable.itemDoubleClicked.disconnect()
    self.ui.checkRecordingsButton.clicked.disconnect()
    self.ui.newParticipantButton.clicked.disconnect()
    self.ui.editParticipantButton.clicked.disconnect()
    self.ui.deleteParticipantButton.clicked.disconnect()
    self.ui.newParticipantSaveButton.clicked.disconnect()
    self.ui.newParticipantCancelButton.clicked.disconnect()
    self.ui.editParticipantSaveButton.clicked.disconnect()
    self.ui.editParticipantCancelButton.clicked.disconnect()
    # Recordings tab
    self.ui.recordingsTable.itemSelectionChanged.disconnect()
    self.ui.recordingsTable.itemDoubleClicked.disconnect()
    self.ui.recordingDetailsButton.clicked.disconnect()
    self.ui.evaluateRecordingButton.clicked.disconnect()
    self.ui.deleteRecordingButton.clicked.disconnect()
    # Navigation bar    
    self.ui.previousPageButton.clicked.disconnect()

  #------------------------------------------------------------------------------
  def updateGUIFromMRML(self, caller=None, event=None):
    """
    Set selections and other settings on the GUI based on the parameter node
    """
    del caller
    del event
    
    # Participant selection
    participantSelected = self.trainUsWidget.logic.recordingManager.isParticipantSelected()
    self.ui.checkRecordingsButton.enabled = participantSelected
    self.ui.newParticipantButton.enabled = (not self.newParticipantVisible) and (not self.editParticipantVisible)
    self.ui.editParticipantButton.enabled = participantSelected and (not self.newParticipantVisible) and (not self.editParticipantVisible)
    self.ui.deleteParticipantButton.enabled = participantSelected and (not self.newParticipantVisible) and (not self.editParticipantVisible)
    
    # Edit participant group box
    self.ui.newParticipantGroupBox.visible = self.newParticipantVisible
    self.ui.editParticipantGroupBox.visible = self.editParticipantVisible

    # Edit participant text
    participantInfo = self.trainUsWidget.logic.recordingManager.getParticipantInfoFromSelection()
    if participantInfo:
      self.ui.editParticipantNameText.text = participantInfo['name']
      self.ui.editParticipantSurnameText.text = participantInfo['surname']
      self.ui.editParticipantBirthDateEdit.setDate(qt.QDate().fromString(participantInfo['birthdate'], 'yyyy-MM-dd'))
      self.ui.editParticipantEmailText.text = participantInfo['email']  
    else:
      self.ui.editParticipantNameText.text = ''
      self.ui.editParticipantSurnameText.text = ''
      self.ui.editParticipantBirthDateEdit.setDate(qt.QDate().currentDate())
      self.ui.editParticipantEmailText.text = ''  

    # Recording selection
    self.ui.recordingDetailsButton.enabled = self.trainUsWidget.logic.recordingManager.isRecordingSelected()

    # Recording details groupbox visibility
    self.ui.recordingDetailsGroupBox.visible = self.ui.recordingDetailsButton.checked

    # Recording details content
    participantInfo = self.trainUsWidget.logic.recordingManager.getParticipantInfoFromSelection()
    recordingInfo = self.trainUsWidget.logic.recordingManager.getRecordingInfoFromSelection()
    if recordingInfo:
      self.ui.recordingParticipantIDText.text = participantInfo['id']
      self.ui.recordingParticipantNameText.text = participantInfo['name']
      self.ui.recordingParticipantSurnameText.text = participantInfo['surname']
      self.ui.recordingDetailsExerciseText.text = recordingInfo['exercise']
      self.ui.recordingDetailsDateText.text = recordingInfo['date']
      self.ui.recordingDetailsDurationText.text = recordingInfo['duration']
    else:
      self.ui.recordingParticipantIDText.text = ''
      self.ui.recordingParticipantNameText.text = ''
      self.ui.recordingParticipantSurnameText.text = ''
      self.ui.recordingDetailsExerciseText.text = ''
      self.ui.recordingDetailsDateText.text = ''
      self.ui.recordingDetailsDurationText.text = '' 


  #------------------------------------------------------------------------------
  #
  # Event handler functions
  #
  #------------------------------------------------------------------------------
  
  #------------------------------------------------------------------------------
  def onParticipantSearchTextChanged(self, searchText):
    # Update table content
    self.homeWidget.updateParticipantsTable()
    self.homeWidget.updateRecordingsTable()

  #------------------------------------------------------------------------------
  def onParticipantsTableItemSelected(self):
    # Get selected cells
    participantID = ''
    selected = self.ui.participantsTable.selectedItems()
    if selected:
      for item in selected:
        # Get data
        if item.column() == 0: # participant ID is stored in column 0
          participantID = item.text()

    # Update selected participant
    self.trainUsWidget.logic.recordingManager.setSelectedParticipantID(participantID)

    # Update recordings table
    self.homeWidget.updateRecordingsTable()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onParticipantsTableItemDoubleClicked(self):
    self.onCheckRecordingsButtonClicked()

  #------------------------------------------------------------------------------
  def onCheckRecordingsButtonClicked(self):
    # Change current tab to "Recordings"
    self.ui.tabWidget.currentIndex = 1

  #------------------------------------------------------------------------------
  def onNewParticipantButtonClicked(self):
    # Update group box visibility
    self.newParticipantVisible = True
    self.updateGUIFromMRML() 

  #------------------------------------------------------------------------------
  def onEditParticipantButtonClicked(self):
    # Update group box visibility
    self.editParticipantVisible = True
    self.updateGUIFromMRML() 

  #------------------------------------------------------------------------------
  def onDeleteParticipantButtonClicked(self):    
    # Display message box to confirm delete action
    deleteFlag = self.deleteParticipantMessageBox()
    if deleteFlag:
      # Delete selected participant
      self.trainUsWidget.logic.recordingManager.deleteSelectedParticipant()

      # Update tables    
      self.homeWidget.updateParticipantsTable()
      self.homeWidget.updateRecordingsTable()

  #------------------------------------------------------------------------------
  def onNewParticipantSaveButtonClicked(self):
    # Check if user input is valid
    isInputValid = self.isNewParticipantInputValid()
    if not isInputValid:
      logging.error('Not all input data is valid. New participant cannot be created.')
      return

    # Get new participant input data
    newParticipantName = self.ui.newParticipantNameText.text
    newParticipantSurname = self.ui.newParticipantSurnameText.text
    newParticipantBirthDate = self.ui.newParticipantBirthDateEdit.date.toString('yyyy-MM-dd') 
    newParticipantEmail = self.ui.newParticipantEmailText.text

    # Create new participant
    self.trainUsWidget.logic.recordingManager.createNewParticipant(newParticipantName, newParticipantSurname, newParticipantBirthDate, newParticipantEmail)

    # Get selected participant ID
    selectedParticipantID = self.trainUsWidget.logic.recordingManager.getSelectedParticipantID()

    # Update table
    self.homeWidget.updateParticipantsTable()
    self.homeWidget.updateRecordingsTable()

    # Set selected participant ID
    self.trainUsWidget.logic.recordingManager.setSelectedParticipantID(selectedParticipantID)

    # Update table selection
    self.homeWidget.updateParticipantsTableSelection()

    # Reset input text fields
    self.ui.newParticipantNameText.text = ''
    self.ui.newParticipantSurnameText.text = ''
    self.ui.newParticipantEmailText.text = ''
    self.ui.newParticipantBirthDateEdit.setDate(qt.QDate().currentDate())

    # Update group box visibility
    self.newParticipantVisible = False

    # Update GUI
    self.updateGUIFromMRML() 

  #------------------------------------------------------------------------------
  def onNewParticipantCancelButtonClicked(self):
    # Update group box visibility
    self.newParticipantVisible = False

    # Reset input text fields
    self.ui.newParticipantNameText.text = ''
    self.ui.newParticipantSurnameText.text = ''
    self.ui.newParticipantEmailText.text = ''
    self.ui.newParticipantBirthDateEdit.setDate(qt.QDate().currentDate())

    # Update GUI
    self.updateGUIFromMRML() 

  #------------------------------------------------------------------------------
  def onEditParticipantSaveButtonClicked(self):
    # Check if user input is valid
    isInputValid = self.isEditParticipantInputValid()
    if not isInputValid:
      logging.error('Not all input data is valid. Participant data cannot be edited.')
      return

    # Get edit participant input data
    editParticipantName = self.ui.editParticipantNameText.text
    editParticipantSurname = self.ui.editParticipantSurnameText.text
    editParticipantBirthDate = self.ui.editParticipantBirthDateEdit.date.toString('yyyy-MM-dd') 
    editParticipantEmail = self.ui.editParticipantEmailText.text    

    # Modify participant's info  
    self.trainUsWidget.logic.recordingManager.editParticipantInfo(editParticipantName, editParticipantSurname, editParticipantBirthDate, editParticipantEmail) 

     # Get selected participant ID
    selectedParticipantID = self.trainUsWidget.logic.recordingManager.getSelectedParticipantID()

    # Update table
    self.homeWidget.updateParticipantsTable()

    # Set selected participant ID
    self.trainUsWidget.logic.recordingManager.setSelectedParticipantID(selectedParticipantID)

    # Update table selection
    self.homeWidget.updateParticipantsTableSelection()

    # Update group box visibility
    self.editParticipantVisible = False

    # Update GUI
    self.updateGUIFromMRML() 

  #------------------------------------------------------------------------------
  def onEditParticipantCancelButtonClicked(self):
    # Update group box visibility
    self.editParticipantVisible = False

    # Reset input info
    self.ui.editParticipantNameText.text = ''
    self.ui.editParticipantSurnameText.text = ''
    self.ui.editParticipantBirthDateEdit.setDate(qt.QDate().currentDate())
    self.ui.editParticipantEmailText.text = ''   
    
    # Update GUI
    self.updateGUIFromMRML() 

  #------------------------------------------------------------------------------
  def onRecordingsTableItemSelected(self):
    # Get selected cells
    recordingID = ''
    recordingDate = ''
    recordingExercise = ''
    recordingDuration = ''
    selected = self.ui.recordingsTable.selectedItems()
    if selected:
      for item in selected:
        # Get data
        if item.column() == 0:
          recordingID = item.text()
        if item.column() == 1:
          recordingDate = item.text()
        if item.column() == 2:
          recordingExercise = item.text()
        if item.column() == 3:
          recordingDuration = item.text()

    # Update selected recording
    self.trainUsWidget.logic.recordingManager.setSelectedRecordingID(recordingID)

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onRecordingsTableItemDoubleClicked(self):
    self.onEvaluateRecordingButtonClicked()

  #------------------------------------------------------------------------------
  def onRecordingDetailsButtonClicked(self):
    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onEvaluateRecordingButtonClicked(self):
    # Get selected participant info
    participantInfo = self.trainUsWidget.logic.recordingManager.getParticipantInfoFromSelection()

    # Get selected recording info
    recordingInfo = self.trainUsWidget.logic.recordingManager.getRecordingInfoFromSelection()

    # Get exercise name
    exerciseName = recordingInfo['exercise']

    # Open corresponding module for recording evaluation
    if exerciseName in Parameters.EXERCISE_TO_MODULENAME_DICTIONARY.keys():
      # Shows slicer interface
      self.homeWidget.hideHome()
      # Open corresponding module
      slicer.util.selectModule(Parameters.EXERCISE_TO_MODULENAME_DICTIONARY[exerciseName])

  #------------------------------------------------------------------------------
  def onDeleteRecordingButtonClicked(self):    
    # Display message box to confirm delete action
    deleteFlag = self.deleteRecordingMessageBox()
    if deleteFlag:
      # Delete selected recording
      self.trainUsWidget.logic.recordingManager.deleteSelectedRecording()

      # Update tables    
      self.homeWidget.updateRecordingsTable()

  #------------------------------------------------------------------------------
  def onPreviousPageButtonClicked(self):
    # Update UI page
    self.homeWidget.logic.setMode(modeID = 0) # switch to welcome page

  #------------------------------------------------------------------------------
  #
  # Logic functions
  #
  #------------------------------------------------------------------------------

  #------------------------------------------------------------------------------
  def deleteParticipantMessageBox(self):
    """
    Display message box for the user to confirm if the partipant data must be deleted.
    :return bool: True if delete action is confirmed, False otherwise
    """
    confirmDelete = qt.QMessageBox()
    confirmDelete.setIcon(qt.QMessageBox.Warning)
    confirmDelete.setWindowTitle(self.homeWidget.logic.participants_deleteMessageBoxTitle)
    confirmDelete.setText(self.homeWidget.logic.participants_deleteMessageBoxLabel)
    confirmDelete.setStandardButtons(qt.QMessageBox.Yes | qt.QMessageBox.No)
    confirmDelete.setDefaultButton(qt.QMessageBox.No)
    confirmDelete.setModal(True)
    retval = confirmDelete.exec_()
    if retval == qt.QMessageBox.Yes:
      return True
    else:
      return False
    
  #------------------------------------------------------------------------------
  def isNewParticipantInputValid(self):    
    # Get user input
    newParticipantName = self.ui.newParticipantNameText.text
    newParticipantSurname = self.ui.newParticipantSurnameText.text
    newParticipantEmail = self.ui.newParticipantEmailText.text

    # Check valid input
    validInput = (newParticipantName != '') and (newParticipantSurname != '') and (newParticipantEmail != '')

    # Display warnings to user
    if validInput:
      self.ui.newParticipantNameWarning.setText('')
      self.ui.newParticipantSurnameWarning.setText('')
      self.ui.newParticipantEmailWarning.setText('')
      self.ui.newParticipantWarningMessageText.setText('')
    else:
      self.ui.newParticipantWarningMessageText.setText('* ' + self.homeWidget.logic.newParticipantWarningMessageText)
      self.ui.newParticipantNameWarning.setText('')
      self.ui.newParticipantSurnameWarning.setText('')
      self.ui.newParticipantEmailWarning.setText('')
      if newParticipantName == '':
        self.ui.newParticipantNameWarning.setText('*')
      if newParticipantSurname == '':
        self.ui.newParticipantSurnameWarning.setText('*')
      if newParticipantEmail == '':
        self.ui.newParticipantEmailWarning.setText('*')
    return validInput

  #------------------------------------------------------------------------------
  def isEditParticipantInputValid(self):    
    
    # Get user input
    editParticipantName = self.ui.editParticipantNameText.text
    editParticipantSurname = self.ui.editParticipantSurnameText.text
    editParticipantEmail = self.ui.editParticipantEmailText.text

    # Check valid input
    validInput = (editParticipantName != '') and (editParticipantSurname != '') and (editParticipantEmail != '')

    # Display warnings to user
    if validInput:
      self.ui.editParticipantNameWarning.setText('')
      self.ui.editParticipantSurnameWarning.setText('')
      self.ui.editParticipantEmailWarning.setText('')
      self.ui.editParticipantWarningMessageText.setText('')
    else:
      self.ui.editParticipantWarningMessageText.setText('* ' + self.homeWidget.logic.editParticipantWarningMessageText)
      self.ui.editParticipantNameWarning.setText('')
      self.ui.editParticipantSurnameWarning.setText('')
      self.ui.editParticipantEmailWarning.setText('')
      if editParticipantName == '':
        self.ui.editParticipantNameWarning.setText('*')
      if editParticipantSurname == '':
        self.ui.editParticipantSurnameWarning.setText('*')
      if editParticipantEmail == '':
        self.ui.editParticipantEmailWarning.setText('*')
    return validInput

  #------------------------------------------------------------------------------
  def deleteRecordingMessageBox(self):
    """
    Display message box for the user to confirm if the recording data must be deleted.
    :return bool: True if delete action is confirmed, False otherwise
    """
    confirmDelete = qt.QMessageBox()
    confirmDelete.setIcon(qt.QMessageBox.Warning)
    confirmDelete.setWindowTitle(self.homeWidget.logic.recordings_deleteMessageBoxTitle)
    confirmDelete.setText(self.homeWidget.logic.recordings_deleteMessageBoxLabel)
    confirmDelete.setStandardButtons(qt.QMessageBox.Yes | qt.QMessageBox.No)
    confirmDelete.setDefaultButton(qt.QMessageBox.No)
    confirmDelete.setModal(True)
    retval = confirmDelete.exec_()
    if retval == qt.QMessageBox.Yes:
      return True
    else:
      return False
      
from __main__ import vtk, qt, ctk, slicer
import logging
import os

#------------------------------------------------------------------------------
#
# Dashboard
#
#------------------------------------------------------------------------------
class Dashboard(qt.QWidget):

  def __init__(self, parent=None):
    super(Dashboard, self).__init__(parent)

    # Define member variables
    self.homeWidget = None # Set externally after creation
    self.trainUsWidget = slicer.trainUsWidget

  #------------------------------------------------------------------------------
  # Clean up when application is closed
  def cleanup(self):
    logging.debug('Dashboard.cleanup')

    self.disconnect()

  #------------------------------------------------------------------------------
  def setupUi(self):
    logging.debug('Dashboard.setupUi')

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiFilePath = os.path.join(self.homeWidget.logic.fileDir, 'Resources', 'UI', 'Dashboard.ui')
    uiWidget = slicer.util.loadUI(uiFilePath)
    self.sectionLayout = qt.QVBoxLayout(self)
    self.sectionLayout.setContentsMargins(0, 0, 0, 0)
    self.sectionLayout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Customize widgets
    self.ui.newParticipantRadioButton.checked = True
    self.ui.existingParticipantRadioButton.checked = False
    self.ui.newParticipantGroupBox.visible = True
    self.ui.existingParticipantGroupBox.visible = False

    # New participant input
    self.ui.newParticipantNameText.setText('')
    self.ui.newParticipantSurnameText.setText('')
    self.ui.newParticipantEmailText.setText('')    
    self.ui.newParticipantBirthDateEdit.setDate(qt.QDate().currentDate())
    self.ui.newParticipantBirthDateEdit.setDisplayFormat('MM.dd.yyyy')

    # Invalid input warnings
    self.ui.newParticipantNameWarning.setText('')
    self.ui.newParticipantNameWarning.setStyleSheet("QLabel { color : red }")
    self.ui.newParticipantSurnameWarning.setText('')
    self.ui.newParticipantSurnameWarning.setStyleSheet("QLabel { color : red }")
    self.ui.newParticipantEmailWarning.setText('')
    self.ui.newParticipantEmailWarning.setStyleSheet("QLabel { color : red }")
    self.ui.warningMessageText.setText('')
    self.ui.warningMessageText.setStyleSheet("QLabel { color : red }")
    
    # Setup GUI connections
    self.setupConnections()

    # Update GUI from MRML
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def setupConnections(self):
    logging.debug('Dashboard.setupConnections')

    self.ui.newParticipantRadioButton.clicked.connect(self.onNewParticipantRadioButtonClicked)
    self.ui.existingParticipantRadioButton.clicked.connect(self.onExistingParticipantRadioButtonClicked)
    self.ui.participantSearchText.textChanged.connect(self.onParticipantSearchTextChanged)
    self.ui.participantsTable.itemSelectionChanged.connect(self.onParticipantsTableItemSelected)
    self.ui.participantsTable.itemDoubleClicked.connect(self.onParticipantsTableItemDoubleClicked)    
    self.ui.startButton.clicked.connect(self.onStartButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    logging.debug('Dashboard.disconnect')

    self.ui.newParticipantRadioButton.clicked.disconnect()
    self.ui.existingParticipantRadioButton.clicked.disconnect()
    self.ui.participantSearchText.textChanged.disconnect()
    self.ui.participantsTable.itemSelectionChanged.disconnect()
    self.ui.participantsTable.itemDoubleClicked.disconnect()
    self.ui.startButton.clicked.disconnect()

  #------------------------------------------------------------------------------
  def updateGUIFromMRML(self, caller=None, event=None):
    """
    Set selections and other settings on the GUI based on the parameter node
    """
    del caller
    del event
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Update state of radio buttons
    participantSelectionMode = parameterNode.GetParameter(self.trainUsWidget.logic.participantSelectionModeParameterName)
    if participantSelectionMode == 'New Participant':
      isRadioButtonChecked = self.ui.newParticipantRadioButton.checked
      if not isRadioButtonChecked:
        self.ui.newParticipantRadioButton.checked = True
        self.onNewParticipantRadioButtonClicked()
    if participantSelectionMode == 'Existing Participant':
      isRadioButtonChecked = self.ui.existingParticipantRadioButton.checked
      if not isRadioButtonChecked:
        self.ui.existingParticipantRadioButton.checked = True
        self.onExistingParticipantRadioButtonClicked()

    # Update state of start button
    if participantSelectionMode == 'New Participant':
      self.ui.startButton.enabled = True
    if participantSelectionMode == 'Existing Participant':
      participantSelected = self.homeWidget.logic.isParticipantSelected()
      self.ui.startButton.enabled = participantSelected


  #------------------------------------------------------------------------------
  #
  # Event handler functions
  #
  
  #------------------------------------------------------------------------------
  def onNewParticipantRadioButtonClicked(self):
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Update parameter node
    parameterNode.SetParameter(self.trainUsWidget.logic.participantSelectionModeParameterName, 'New Participant')

    # Update group box visibility
    self.ui.newParticipantGroupBox.visible = True
    self.ui.existingParticipantGroupBox.visible = False

    # Update GUI from MRML
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onExistingParticipantRadioButtonClicked(self):
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Update parameter node
    parameterNode.SetParameter(self.trainUsWidget.logic.participantSelectionModeParameterName, 'Existing Participant')
    
    # Update group box visibility
    self.ui.newParticipantGroupBox.visible = False
    self.ui.existingParticipantGroupBox.visible = True

    # Update GUI from MRML
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onParticipantSearchTextChanged(self, searchText):
    # Synchronize partipants table search
    self.homeWidget.ui.ParticipantsPanel.ui.participantSearchText.setText(searchText)

    # Update table content
    self.homeWidget.updateDashboardTable()
    self.homeWidget.updateRecordingsTable()

    # Update GUI from MRML
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onParticipantsTableItemSelected(self):
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get selected cells
    participantID = ''
    selected = self.ui.participantsTable.selectedItems()
    if selected:
      for item in selected:
        # Get data
        if item.column() == 0: # participant ID is stored in column 0
          participantID = item.text()

    # Update parameter node
    parameterNode.SetParameter(self.trainUsWidget.logic.selectedParticipantIDParameterName, participantID)

    # Update participants table
    self.homeWidget.updateParticipantsTableSelection()
    self.homeWidget.updateRecordingsTable()

    # Update GUI from MRML
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onParticipantsTableItemDoubleClicked(self):
    # Change current tab to "Participants"
    self.homeWidget.ui.dashboardTabWidget.currentIndex = 1

    # Update GUI from MRML
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onStartButtonClicked(self):
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get participant selection mode
    participantSelectionMode = parameterNode.GetParameter(self.trainUsWidget.logic.participantSelectionModeParameterName)

    # New participants
    if participantSelectionMode == 'New Participant':
      print('Starting training session - New Participant')

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
      newParticipantInfo = self.homeWidget.logic.createNewParticipant(newParticipantName, newParticipantSurname, newParticipantBirthDate, newParticipantEmail)

      # Reset input text fields
      self.ui.newParticipantNameText.text = ''
      self.ui.newParticipantSurnameText.text = ''
      self.ui.newParticipantEmailText.text = ''
      self.ui.newParticipantBirthDateEdit.setDate(qt.QDate().currentDate())

      # Update table
      self.homeWidget.updateDashboardTable()
      self.homeWidget.updateParticipantsTable()
      self.homeWidget.updateRecordingsTable()

      # Update parameter node
      parameterNode.SetParameter(self.trainUsWidget.logic.selectedParticipantIDParameterName, newParticipantInfo['id'])   
      parameterNode.SetParameter(self.trainUsWidget.logic.participantSelectionModeParameterName, 'Existing Participant') 

      # Update table selection
      self.homeWidget.updateDashboardTableSelection()
      self.homeWidget.updateParticipantsTableSelection()        

    # Existing participants
    if participantSelectionMode == 'Existing Participant':
      print('Starting training session - Existing Participant')

    # Get selected participant
    selectedParticipantID = parameterNode.GetParameter(self.trainUsWidget.logic.selectedParticipantIDParameterName)

    # Get participant info from ID
    selectedParticipantInfo = self.homeWidget.logic.getParticipantInfoFromID(selectedParticipantID)

    # Display
    if selectedParticipantInfo:
      print('Selected participant: ')
      print('   - Participant ID: ', selectedParticipantInfo['id'])
      print('   - Participant Name: ', selectedParticipantInfo['name'])
      print('   - Participant Surname: ', selectedParticipantInfo['surname'])
      print('   - Participant Birth Date: ', selectedParticipantInfo['birthdate'])
      print('   - Participant Email: ', selectedParticipantInfo['email'])
    else:
      print('Selected participant: NONE')

    # Get training session info
    participantID = selectedParticipantInfo['id']
    participantName= selectedParticipantInfo['name']
    participantSurname = selectedParticipantInfo['surname']
    from datetime import datetime
    dateLabel = datetime.now().strftime('%Y-%m-%d')
    
    # Update training session info in UI
    self.homeWidget.ui.participantLabel.text = f'[{participantID}] {participantSurname}, {participantName}'
    self.homeWidget.ui.dateTimeLabel.text = dateLabel
    self.homeWidget.ui.hardwareSetUpLabel.text = '-' # TODO

    # Shows training menu
    self.homeWidget.updateTrainingMenuVisibility(visible = True)    

    # Update GUI from MRML
    self.updateGUIFromMRML()


  #------------------------------------------------------------------------------
  #
  # Logic functions
  #
  #------------------------------------------------------------------------------
  
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
      self.ui.warningMessageText.setText('')
    else:
      self.ui.warningMessageText.setText('* ' + self.homeWidget.logic.dashboard_warningMessageTextLabel)
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
  
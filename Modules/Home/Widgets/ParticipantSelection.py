from __main__ import vtk, qt, ctk, slicer
import logging
import os

#------------------------------------------------------------------------------
#
# ParticipantSelection
#
#------------------------------------------------------------------------------
class ParticipantSelection(qt.QWidget):

  def __init__(self, parent=None):
    super(ParticipantSelection, self).__init__(parent)

    # Define member variables
    self.homeWidget = None # Set externally after creation
    self.trainUsWidget = slicer.trainUsWidget

    # GUI flags    
    self.newParticipantVisible = False
    self.editParticipantVisible = False

  #------------------------------------------------------------------------------
  # Clean up when application is closed
  def cleanup(self):
    logging.debug('ParticipantSelection.cleanup')

    self.disconnect()

  #------------------------------------------------------------------------------
  def setupUi(self):
    logging.debug('ParticipantSelection.setupUi')

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiFilePath = os.path.join(self.homeWidget.logic.fileDir, 'Resources', 'UI', 'ParticipantSelection.ui')
    uiWidget = slicer.util.loadUI(uiFilePath)
    self.sectionLayout = qt.QVBoxLayout(self)
    self.sectionLayout.setContentsMargins(0, 0, 0, 0)
    self.sectionLayout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Customize widgets    
    self.ui.newParticipantGroupBox.visible = False
    self.ui.editParticipantGroupBox.visible = False
    self.ui.newParticipantButton.enabled = True
    self.ui.editParticipantButton.enabled = False
    self.ui.deleteParticipantButton.enabled = False
    self.ui.newParticipantSaveButton.enabled = True 
    self.ui.newParticipantCancelButton.enabled = True
    self.ui.editParticipantSaveButton.enabled = True 
    self.ui.editParticipantCancelButton.enabled = True
    self.ui.previousPageButton.enabled = True
    self.ui.nextPageButton.enabled = False

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
    
    # Setup GUI connections
    self.setupConnections()

  #------------------------------------------------------------------------------
  def setupConnections(self):
    logging.debug('ParticipantSelection.setupConnections')

    self.ui.participantSearchText.textChanged.connect(self.onParticipantSearchTextChanged)
    self.ui.participantsTable.itemSelectionChanged.connect(self.onParticipantSelectionTableItemSelected)
    self.ui.newParticipantButton.clicked.connect(self.onNewParticipantButtonClicked)
    self.ui.editParticipantButton.clicked.connect(self.onEditParticipantButtonClicked)
    self.ui.deleteParticipantButton.clicked.connect(self.onDeleteParticipantButtonClicked)
    self.ui.newParticipantSaveButton.clicked.connect(self.onNewParticipantSaveButtonClicked)
    self.ui.newParticipantCancelButton.clicked.connect(self.onNewParticipantCancelButtonClicked)
    self.ui.editParticipantSaveButton.clicked.connect(self.onEditParticipantSaveButtonClicked)
    self.ui.editParticipantCancelButton.clicked.connect(self.onEditParticipantCancelButtonClicked)
    self.ui.previousPageButton.clicked.connect(self.onPreviousPageButtonClicked)
    self.ui.nextPageButton.clicked.connect(self.onNextPageButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    logging.debug('ParticipantSelection.disconnect')

    self.ui.participantSearchText.textChanged.disconnect()
    self.ui.participantsTable.itemSelectionChanged.disconnect()
    self.ui.newParticipantButton.clicked.disconnect()
    self.ui.editParticipantButton.clicked.disconnect()
    self.ui.deleteParticipantButton.clicked.disconnect()
    self.ui.newParticipantSaveButton.clicked.disconnect()
    self.ui.newParticipantCancelButton.clicked.disconnect()
    self.ui.editParticipantSaveButton.clicked.disconnect()
    self.ui.editParticipantCancelButton.clicked.disconnect()
    self.ui.previousPageButton.clicked.disconnect()
    self.ui.nextPageButton.clicked.disconnect()

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

    # Participant selection
    participantSelected = self.trainUsWidget.logic.dataManager.isParticipantSelected()
    self.ui.newParticipantButton.enabled = (not self.newParticipantVisible) and (not self.editParticipantVisible)
    self.ui.editParticipantButton.enabled = participantSelected and (not self.newParticipantVisible) and (not self.editParticipantVisible)
    self.ui.deleteParticipantButton.enabled = participantSelected and (not self.newParticipantVisible) and (not self.editParticipantVisible)
    self.ui.nextPageButton.enabled = participantSelected

    # Edit participant group box
    self.ui.newParticipantGroupBox.visible = self.newParticipantVisible
    self.ui.editParticipantGroupBox.visible = self.editParticipantVisible

    # Edit participant text
    participantInfo = self.trainUsWidget.logic.dataManager.getParticipantInfoFromSelection()
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


  #------------------------------------------------------------------------------
  #
  # Event handler functions
  #
  #------------------------------------------------------------------------------
  
  #------------------------------------------------------------------------------
  def onParticipantSearchTextChanged(self, searchText):
    
    # Update table content
    self.homeWidget.updateParticipantsTable()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onParticipantSelectionTableItemSelected(self):
    # Get selected cells
    participantID = ''
    selected = self.ui.participantsTable.selectedItems()
    if selected:
      for item in selected:
        # Get data
        if item.column() == 0: # participant ID is stored in column 0
          participantID = item.text()

    # Update selected participant
    self.trainUsWidget.logic.dataManager.setSelectedParticipantID(participantID)

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onNewParticipantButtonClicked(self):
    # Update table content to remove current selection
    self.homeWidget.updateParticipantsTable()

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
      self.trainUsWidget.logic.dataManager.deleteSelectedParticipant()
      # Update tables    
      self.homeWidget.updateParticipantsTable()

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
    self.trainUsWidget.logic.dataManager.createNewParticipant(newParticipantName, newParticipantSurname, newParticipantBirthDate, newParticipantEmail)

    # Get selected participant ID
    selectedParticipantID = self.trainUsWidget.logic.dataManager.getSelectedParticipantID()

    # Update table
    self.homeWidget.updateParticipantsTable()

    # Set selected participant ID
    self.trainUsWidget.logic.dataManager.setSelectedParticipantID(selectedParticipantID)

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

    # Modify selected participant's info  
    self.trainUsWidget.logic.dataManager.editParticipantInfo(editParticipantName, editParticipantSurname, editParticipantBirthDate, editParticipantEmail) 

    # Get selected participant ID
    selectedParticipantID = self.trainUsWidget.logic.dataManager.getSelectedParticipantID()

    # Update table
    self.homeWidget.updateParticipantsTable()

    # Set selected participant ID
    self.trainUsWidget.logic.dataManager.setSelectedParticipantID(selectedParticipantID)

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
  def onPreviousPageButtonClicked(self):
    # Update UI page
    self.homeWidget.logic.setMode(modeID = 0)

  #------------------------------------------------------------------------------
  def onNextPageButtonClicked(self):
    # Update UI page
    self.homeWidget.logic.setMode(modeID = 2)


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
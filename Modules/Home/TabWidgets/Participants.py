from __main__ import vtk, qt, ctk, slicer
import logging
import os

#------------------------------------------------------------------------------
#
# Participants
#
#------------------------------------------------------------------------------
class Participants(qt.QWidget):

  def __init__(self, parent=None):
    super(Participants, self).__init__(parent)

    # Define member variables
    self.homeWidget = None # Set externally after creation
    self.trainUsWidget = slicer.trainUsWidget

    # GUI flags
    self.editParticipantVisible = False

  #------------------------------------------------------------------------------
  # Clean up when application is closed
  def cleanup(self):
    logging.debug('Participants.cleanup')

    self.disconnect()

  #------------------------------------------------------------------------------
  def setupUi(self):
    logging.debug('Participants.setupUi')

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiFilePath = os.path.join(self.homeWidget.logic.fileDir, 'Resources', 'UI', 'Participants.ui')
    uiWidget = slicer.util.loadUI(uiFilePath)
    self.sectionLayout = qt.QVBoxLayout(self)
    self.sectionLayout.setContentsMargins(0, 0, 0, 0)
    self.sectionLayout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Customize widgets    
    self.ui.editParticipantGroupBox.visible = False
    self.ui.checkRecordingsButton.enabled = False
    self.ui.editParticipantButton.enabled = False
    self.ui.deleteParticipantButton.enabled = False
    self.ui.saveEditButton.enabled = True 
    self.ui.cancelEditButton.enabled = True
    
    # Setup GUI connections
    self.setupConnections()

  #------------------------------------------------------------------------------
  def setupConnections(self):
    logging.debug('Participants.setupConnections')

    self.ui.participantSearchText.textChanged.connect(self.onParticipantSearchTextChanged)
    self.ui.participantsTable.itemSelectionChanged.connect(self.onParticipantsTableItemSelected)
    self.ui.checkRecordingsButton.clicked.connect(self.onCheckRecordingsButtonClicked)
    self.ui.editParticipantButton.clicked.connect(self.onEditParticipantButtonClicked)
    self.ui.deleteParticipantButton.clicked.connect(self.onDeleteParticipantButtonClicked)
    self.ui.saveEditButton.clicked.connect(self.onSaveEditButtonClicked)
    self.ui.cancelEditButton.clicked.connect(self.onCancelEditButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    logging.debug('Participants.disconnect')

    self.ui.participantSearchText.textChanged.disconnect()
    self.ui.participantsTable.itemSelectionChanged.disconnect()
    self.ui.checkRecordingsButton.clicked.disconnect()
    self.ui.editParticipantButton.clicked.disconnect()
    self.ui.deleteParticipantButton.clicked.disconnect()
    self.ui.saveEditButton.clicked.disconnect()
    self.ui.cancelEditButton.clicked.disconnect()

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
    participantSelected = self.isParticipantSelected()
    self.ui.checkRecordingsButton.enabled = participantSelected
    self.ui.editParticipantButton.enabled = participantSelected and (not self.editParticipantVisible)
    self.ui.deleteParticipantButton.enabled = participantSelected

    # Edit participant group box
    self.ui.editParticipantGroupBox.visible = self.editParticipantVisible

    # Edit participant text
    participantInfo = self.homeWidget.logic.getParticipantInfoFromSelection()
    if participantInfo:
      self.ui.editParticipantNameText.text = participantInfo['name']
      self.ui.editParticipantSurnameText.text = participantInfo['surname']
    else:
      self.ui.editParticipantNameText.text = ''
      self.ui.editParticipantSurnameText.text = ''
    


  #------------------------------------------------------------------------------
  #
  # Event handler functions
  #
  #------------------------------------------------------------------------------
  
  #------------------------------------------------------------------------------
  def onParticipantSearchTextChanged(self, searchText):
    # Synchronize dasboard table search
    self.homeWidget.ui.DashboardPanel.ui.participantSearchText.setText(searchText)

    # Update table content
    self.homeWidget.updateParticipantsTable()
    self.homeWidget.updateRecordingsTable()

  #------------------------------------------------------------------------------
  def onParticipantsTableItemSelected(self):
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get selected cells
    participantID = ''
    participantName = ''
    participantSurname = ''
    participantNumRecordings = ''
    selected = self.ui.participantsTable.selectedItems()
    if selected:
      for item in selected:
        # Get data
        if item.column() == 0:
          participantID = item.text()
        if item.column() == 1:
          participantName = item.text()
        if item.column() == 2:
          participantSurname = item.text()
        if item.column() == 3:
          participantNumRecordings = item.text()

    # Update parameter node
    parameterNode.SetParameter(self.trainUsWidget.logic.selectedParticipantIDParameterName, participantID)

    # Update dashboard table
    self.homeWidget.updateDashboardTableSelection()
    self.homeWidget.updateRecordingsTable()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onCheckRecordingsButtonClicked(self):
    # Change current tab to "Recordings"
    self.homeWidget.ui.tabWidget.currentIndex = 2

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
      self.deleteSelectedParticipant()

      # Update tables    
      self.homeWidget.updateDashboardTable()
      self.homeWidget.updateParticipantsTable()
      self.homeWidget.updateRecordingsTable()

  #------------------------------------------------------------------------------
  def onSaveEditButtonClicked(self):
    # Update group box visibility
    self.editParticipantVisible = False

    # Get selected participant info
    selectedParticipantInfo = self.homeWidget.logic.getParticipantInfoFromSelection()
    selectedParticipantID = selectedParticipantInfo['id']
    
    # Get input info
    participantName = self.ui.editParticipantNameText.text
    participantSurname = self.ui.editParticipantSurnameText.text

    # Modify participant's info  
    self.editParticipantInfo(participantName, participantSurname) 

    # Update GUI
    self.updateGUIFromMRML() 

  #------------------------------------------------------------------------------
  def onCancelEditButtonClicked(self):
    # Update group box visibility
    self.editParticipantVisible = False

    # Reset input info
    self.ui.editParticipantNameText.text = ''
    self.ui.editParticipantSurnameText.text = ''
    
    # Update GUI
    self.updateGUIFromMRML() 

  #------------------------------------------------------------------------------
  #
  # Logic functions
  #
  #------------------------------------------------------------------------------
  
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
  def editParticipantInfo(self, participantName, participantSurname):
    """
    Edit name and surname of the selected participant in the JSON info file.
    :param participantName: new name for partipant (string)
    :param participantSurname: new surname for participant (string)
    """    
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get selected participant info
    selectedParticipantInfo = self.homeWidget.logic.getParticipantInfoFromSelection() 

    # Get JSON info file path
    selectedParticipantID = selectedParticipantInfo['id']
    participantInfoFilePath = self.homeWidget.logic.getParticipantInfoFilePath(selectedParticipantID)

    # Edit participant info
    selectedParticipantInfo['name'] = participantName
    selectedParticipantInfo['surname'] = participantSurname

    # Write new file
    self.homeWidget.logic.writeParticipantInfoFile(participantInfoFilePath, selectedParticipantInfo)

    # Update table content
    self.homeWidget.updateDashboardTable()
    self.homeWidget.updateParticipantsTable()

    # Update participant selection
    parameterNode.SetParameter(self.trainUsWidget.logic.selectedParticipantIDParameterName, selectedParticipantID)

    # Update table selection
    self.homeWidget.updateDashboardTableSelection()
    self.homeWidget.updateParticipantsTableSelection()

  #------------------------------------------------------------------------------
  def deleteParticipantMessageBox(self):
    """
    Display message box for the user to confirm if the partipant data must be deleted.
    :return bool: True if delete action is confirmed, False otherwise
    """
    confirmDelete = qt.QMessageBox()
    confirmDelete.setIcon(qt.QMessageBox.Warning)
    confirmDelete.setWindowTitle('Confirm')
    confirmDelete.setText(
      'Are you sure you want to delete the selected participant?\n\nOnce deleted, data associated with this participant will be lost.')
    confirmDelete.setStandardButtons(qt.QMessageBox.Yes | qt.QMessageBox.No)
    confirmDelete.setDefaultButton(qt.QMessageBox.No)
    confirmDelete.setModal(True)
    retval = confirmDelete.exec_()
    if retval == qt.QMessageBox.Yes:
      return True
    else:
      return False

  #------------------------------------------------------------------------------
  def deleteSelectedParticipant(self):
    """
    Delete selected participant from root directory.
    """
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get selected participant
    selectedParticipantID = parameterNode.GetParameter(self.trainUsWidget.logic.selectedParticipantIDParameterName)

    # Delete participant
    self.homeWidget.logic.deleteParticipant(selectedParticipantID)
    
    # Update parameter node
    parameterNode.SetParameter(self.trainUsWidget.logic.selectedParticipantIDParameterName, '')

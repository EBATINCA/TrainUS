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

    self.ui.participantsTable.itemSelectionChanged.connect(self.onParticipantsTableItemSelected)
    self.ui.checkRecordingsButton.clicked.connect(self.onCheckRecordingsButtonClicked)
    self.ui.editParticipantButton.clicked.connect(self.onEditParticipantButtonClicked)
    self.ui.deleteParticipantButton.clicked.connect(self.onDeleteParticipantButtonClicked)
    self.ui.saveEditButton.clicked.connect(self.onSaveEditButtonClicked)
    self.ui.cancelEditButton.clicked.connect(self.onCancelEditButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    logging.debug('Participants.disconnect')

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
    self.ui.editParticipantButton.enabled = participantSelected
    self.ui.deleteParticipantButton.enabled = participantSelected

    # Edit participant group box
    self.ui.editParticipantGroupBox.visible = self.editParticipantVisible
    self.ui.editParticipantButton.enabled = not self.editParticipantVisible

    # Edit participant text
    participantInfo = self.getInfoForSelectedParticipant()
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

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onCheckRecordingsButtonClicked(self):
    pass

  #------------------------------------------------------------------------------
  def onEditParticipantButtonClicked(self):
    
    # Update group box visibility
    self.editParticipantVisible = True
    self.updateGUIFromMRML() 

  #------------------------------------------------------------------------------
  def onDeleteParticipantButtonClicked(self):
    pass

  #------------------------------------------------------------------------------
  def onSaveEditButtonClicked(self):
    # Update group box visibility
    self.editParticipantVisible = False

    # Get input info
    participantName = self.ui.editParticipantNameText.text
    participantSurname = self.ui.editParticipantSurnameText.text

    # Modify participant's info  
    self.editParticipantInfo(participantName, participantSurname) 

    # Update GUI
    self.updateGUIFromMRML() 

    # Tables    
    self.homeWidget.updateDashboardTable()
    self.homeWidget.updateParticipantsTable()


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
  
  def isParticipantSelected(self):
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get selected participant
    selectedParticipantID = parameterNode.GetParameter(self.trainUsWidget.logic.selectedParticipantIDParameterName)

    # Check valid selection
    participantSelected = True
    if (selectedParticipantID == '') :
      participantSelected = False

    return participantSelected


  def getInfoForSelectedParticipant(self):
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get selected participant
    selectedParticipantID = parameterNode.GetParameter(self.trainUsWidget.logic.selectedParticipantIDParameterName)

    # Get participant info from ID
    selectedParticipantInfo = self.homeWidget.logic.getParticipantInfoFromID(selectedParticipantID)

    return selectedParticipantInfo

  def editParticipantInfo(self, participantName, participantSurname):

    # Get selected participant info
    selectedParticipantInfo = self.getInfoForSelectedParticipant()

    # Edit participant info
    selectedParticipantInfo['name'] = participantName
    selectedParticipantInfo['surname'] = participantSurname

    # Get JSON info file path
    selectedParticipantID = selectedParticipantInfo['id']
    participantInfoFilePath = self.homeWidget.logic.getParticipantInfoFilePath(selectedParticipantID)

    # Write new file
    self.homeWidget.logic.writeParticipantInfoFile(participantInfoFilePath, selectedParticipantInfo)

      
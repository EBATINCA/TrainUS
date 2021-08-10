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
    
    # Setup GUI connections
    self.setupConnections()

  #------------------------------------------------------------------------------
  def setupConnections(self):
    logging.debug('Dashboard.setupConnections')

    self.ui.newParticipantRadioButton.clicked.connect(self.onNewParticipantRadioButtonClicked)
    self.ui.existingParticipantRadioButton.clicked.connect(self.onExistingParticipantRadioButtonClicked)
    self.ui.participantsTable.itemSelectionChanged.connect(self.onParticipantsTableItemSelected)
    self.ui.startButton.clicked.connect(self.onStartButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    logging.debug('Dashboard.disconnect')

    self.ui.newParticipantRadioButton.clicked.disconnect()
    self.ui.existingParticipantRadioButton.clicked.disconnect()
    self.ui.participantsTable.itemSelectionChanged.disconnect()
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

    pass


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
    parameterNode.SetParameter(self.trainUsWidget.logic.selectedParticipantNameParameterName, participantName)
    parameterNode.SetParameter(self.trainUsWidget.logic.selectedParticipantSurnameParameterName, participantSurname)


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

      # Get new participant input data
      newParticipantName = self.ui.newParticipantNameText.text
      newParticipantSurname = self.ui.newParticipantSurnameText.text

      # Create new participant
      newParticipantID = self.homeWidget.logic.createNewParticipant(newParticipantName, newParticipantSurname)

      # Update table
      self.homeWidget.updateDashboardTable()
      self.homeWidget.updateParticipantsTable()

      # Update parameter node
      parameterNode.SetParameter(self.trainUsWidget.logic.selectedParticipantIDParameterName, newParticipantID)
      parameterNode.SetParameter(self.trainUsWidget.logic.selectedParticipantNameParameterName, newParticipantName)
      parameterNode.SetParameter(self.trainUsWidget.logic.selectedParticipantSurnameParameterName, newParticipantSurname)

    # Existing participants
    if participantSelectionMode == 'Existing Participant':
      print('Starting training session - Existing Participant')

      # Get selected participant
      selectedParticipantID = parameterNode.GetParameter(self.trainUsWidget.logic.selectedParticipantIDParameterName)
      selectedParticipantName = parameterNode.GetParameter(self.trainUsWidget.logic.selectedParticipantNameParameterName)
      selectedParticipantSurname = parameterNode.GetParameter(self.trainUsWidget.logic.selectedParticipantSurnameParameterName)

      # Get participant info
      [participantID, participantName, participantSurname, participantNumRecordings] = self.getParticipantInfoByID(selectedParticipantID)

      # Display
      print('Selected participant: ')
      print('   - Participant ID: ', participantID)
      print('   - Participant Name: ', participantName)
      print('   - Participant Surname: ', participantSurname)
      print('   - Participant Num Recordings: ', participantNumRecordings)


  #------------------------------------------------------------------------------
  #
  # Logic functions
  #
  #------------------------------------------------------------------------------
  
  #------------------------------------------------------------------------------
  def getParticipantInfoByID(self, inputParticipantID):
    # Get data from table
    [participantID_list, participantName_list, participantSurname_list, participantNumRecordings_list] = self.homeWidget.getDataFromDashboardTable()

    # Get participant data
    participantID = ''
    participantName = ''
    participantSurname = ''
    participantNumRecordings = ''
    numParticipants = len(participantID_list)
    for participantPos in range(numParticipants):
      if inputParticipantID == participantID_list[participantPos]:
        participantID = participantID_list[participantPos]
        participantName = participantName_list[participantPos]
        participantSurname = participantSurname_list[participantPos]
        participantNumRecordings = participantNumRecordings_list[participantPos]
    return participantID, participantName, participantSurname, participantNumRecordings


     
  
  
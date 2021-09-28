from __main__ import vtk, qt, ctk, slicer
import logging
import os

#------------------------------------------------------------------------------
#
# Recordings
#
#------------------------------------------------------------------------------
class Recordings(qt.QWidget):

  def __init__(self, parent=None):
    super(Recordings, self).__init__(parent)

    # Define member variables
    self.homeWidget = None # Set externally after creation
    self.trainUsWidget = slicer.trainUsWidget

    # GUI flags
    self.recordingDetailsVisible = False

  #------------------------------------------------------------------------------
  # Clean up when application is closed
  def cleanup(self):
    logging.debug('Recordings.cleanup')

    self.disconnect()

  #------------------------------------------------------------------------------
  def setupUi(self):
    logging.debug('Recordings.setupUi')

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiFilePath = os.path.join(self.homeWidget.logic.fileDir, 'Resources', 'UI', 'Recordings.ui')
    uiWidget = slicer.util.loadUI(uiFilePath)
    self.sectionLayout = qt.QVBoxLayout(self)
    self.sectionLayout.setContentsMargins(0, 0, 0, 0)
    self.sectionLayout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Customize widgets
    self.ui.recordingDetailsGroupBox.visible = self.ui.recordingDetailsButton.checked
    self.ui.recordingDetailsButton.enabled = self.isRecordingSelected()

    # Setup GUI connections
    self.setupConnections()

  #------------------------------------------------------------------------------
  def setupConnections(self):
    logging.debug('Recordings.setupConnections')

    self.ui.recordingsTable.itemSelectionChanged.connect(self.onRecordingsTableItemSelected)
    self.ui.recordingDetailsButton.clicked.connect(self.onRecordingDetailsButtonClicked)
    self.ui.deleteRecordingButton.clicked.connect(self.onDeleteRecordingButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    logging.debug('Recordings.disconnect')

    self.ui.recordingsTable.itemSelectionChanged.disconnect()
    self.ui.recordingDetailsButton.clicked.disconnect()
    self.ui.deleteRecordingButton.clicked.disconnect()

  #------------------------------------------------------------------------------
  def updateGUIFromMRML(self, caller=None, event=None):
    """
    Set selections and other settings on the GUI based on the parameter node
    """
    del caller
    del event

    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Recording selection
    self.ui.recordingDetailsButton.enabled = self.isRecordingSelected()

    # Recording details groupbox visibility
    self.ui.recordingDetailsGroupBox.visible = self.ui.recordingDetailsButton.checked

    # Recording details content
    participantInfo = self.homeWidget.logic.getParticipantInfoFromSelection()
    recordingInfo = self.homeWidget.logic.getRecordingInfoFromSelection()
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
  def onRecordingsTableItemSelected(self):
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

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

    # Update parameter node
    parameterNode.SetParameter(self.trainUsWidget.logic.selectedRecordingIDParameterName, recordingID)

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onRecordingDetailsButtonClicked(self):
    # Update GUI
    self.updateGUIFromMRML() 

  #------------------------------------------------------------------------------
  def onDeleteRecordingButtonClicked(self):    
    # Display message box to confirm delete action
    deleteFlag = self.deleteRecordingMessageBox()
    if deleteFlag:
      # Delete selected recording
      self.deleteSelectedRecording()

      # Update tables    
      self.homeWidget.updateRecordingsTable()

  #------------------------------------------------------------------------------
  #
  # Logic functions
  #
  #------------------------------------------------------------------------------

  #------------------------------------------------------------------------------
  def isRecordingSelected(self):
    """
    Check if a recording is selected.
    :return bool: True if valid recording is selected, False otherwise
    """    
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get selected recording
    selectedRecordingID = parameterNode.GetParameter(self.trainUsWidget.logic.selectedRecordingIDParameterName)

    # Check valid selection
    recordingSelected = True
    if (selectedRecordingID == '') :
      recordingSelected = False
    return recordingSelected

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

  #------------------------------------------------------------------------------
  def deleteSelectedRecording(self):
    """
    Delete selected recording from root directory.
    """
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get selected participant and recording
    selectedParticipantID = parameterNode.GetParameter(self.trainUsWidget.logic.selectedParticipantIDParameterName)
    selectedRecordingID = parameterNode.GetParameter(self.trainUsWidget.logic.selectedRecordingIDParameterName)

    # Delete recording
    self.homeWidget.logic.deleteRecording(selectedParticipantID, selectedRecordingID)
    
    # Update parameter node
    parameterNode.SetParameter(self.trainUsWidget.logic.selectedRecordingIDParameterName, '')

  
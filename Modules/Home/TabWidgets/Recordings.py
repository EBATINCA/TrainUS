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
    self.ui.recordingDetailsGroupBox.visible = self.recordingDetailsVisible
    self.ui.recordingDetailsButton.enabled = self.isRecordingSelected()
    self.ui.recordingDetailsButton.setText('See details')

    # Setup GUI connections
    self.setupConnections()

  #------------------------------------------------------------------------------
  def setupConnections(self):
    logging.debug('Recordings.setupConnections')

    self.ui.recordingsTable.itemSelectionChanged.connect(self.onRecordingsTableItemSelected)
    self.ui.recordingDetailsButton.clicked.connect(self.onRecordingDetailsButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    logging.debug('Recordings.disconnect')

    self.ui.recordingsTable.itemSelectionChanged.disconnect()
    self.ui.recordingDetailsButton.clicked.disconnect()

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
    self.ui.recordingDetailsGroupBox.visible = self.recordingDetailsVisible

    # Recording details button text
    if self.recordingDetailsVisible:
      self.ui.recordingDetailsButton.setText('Hide details')
    else:
      self.ui.recordingDetailsButton.setText('See details') 

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
    # Update group box visibility
    if self.recordingDetailsVisible:
      self.recordingDetailsVisible = False
    else:
      self.recordingDetailsVisible = True

    # Update GUI
    self.updateGUIFromMRML() 

  #------------------------------------------------------------------------------
  #
  # Logic functions
  #
  #------------------------------------------------------------------------------

  def isRecordingSelected(self):
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
  
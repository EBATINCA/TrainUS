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
    self.ui.participantNameText.text = '-'
    self.ui.participantSurnameText.text = '-'
    self.ui.ultrasoundDeviceText.text = '-'
    self.ui.trackingSystemText.text = '-'
    self.ui.simulationPhantomText.text = '-'
    
    # Setup GUI connections
    self.setupConnections()

    # Update GUI from MRML
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def setupConnections(self):
    logging.debug('Dashboard.setupConnections')

    self.ui.startButton.clicked.connect(self.onStartButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    logging.debug('Dashboard.disconnect')

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

    # Update state of start button
    participantSelected = self.homeWidget.logic.isParticipantSelected()
    self.ui.startButton.enabled = participantSelected


  #------------------------------------------------------------------------------
  #
  # Event handler functions
  #

  #------------------------------------------------------------------------------
  def onStartButtonClicked(self):
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

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

    # Shows training menu
    self.homeWidget.updateTrainingMenuVisibility(visible = True)    

    # Update GUI from MRML
    self.updateGUIFromMRML()


  #------------------------------------------------------------------------------
  #
  # Logic functions
  #
  #------------------------------------------------------------------------------
  
  
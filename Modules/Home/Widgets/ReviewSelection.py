from __main__ import vtk, qt, ctk, slicer
import logging
import os

#------------------------------------------------------------------------------
#
# ReviewSelection
#
#------------------------------------------------------------------------------
class ReviewSelection(qt.QWidget):

  def __init__(self, parent=None):
    super(ReviewSelection, self).__init__(parent)

    # Define member variables
    self.homeWidget = None # Set externally after creation
    self.trainUsWidget = slicer.trainUsWidget

  #------------------------------------------------------------------------------
  # Clean up when application is closed
  def cleanup(self):
    logging.debug('ReviewSelection.cleanup')

    self.disconnect()

  #------------------------------------------------------------------------------
  def setupUi(self):
    logging.debug('ReviewSelection.setupUi')

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiFilePath = os.path.join(self.homeWidget.logic.fileDir, 'Resources', 'UI', 'ReviewSelection.ui')
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
    logging.debug('ReviewSelection.setupConnections')

    self.ui.editParticipantSelectionButton.clicked.connect(self.onEditParticipantSelectionButtonClicked)
    self.ui.editHardwareSelectionButton.clicked.connect(self.onEditHardwareSelectionButtonClicked)
    self.ui.previousPageButton.clicked.connect(self.onPreviousPageButtonClicked)
    self.ui.nextPageButton.clicked.connect(self.onNextPageButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    logging.debug('ReviewSelection.disconnect')

    self.ui.editParticipantSelectionButton.clicked.disconnect()
    self.ui.editHardwareSelectionButton.clicked.disconnect()
    self.ui.previousPageButton.clicked.disconnect()
    self.ui.nextPageButton.clicked.disconnect()

  #------------------------------------------------------------------------------
  def updateGUIFromMRML(self, caller=None, event=None):
    """
    Set selections and other settings on the GUI based on the parameter node
    """
    del caller
    del event

    pass


  #------------------------------------------------------------------------------
  #
  # Event handler functions
  #

  #------------------------------------------------------------------------------
  def onEditParticipantSelectionButtonClicked(self):
    # Update UI page
    self.homeWidget.logic.setMode(modeID = 1)

  #------------------------------------------------------------------------------
  def onEditHardwareSelectionButtonClicked(self):
    # Update UI page
    self.homeWidget.logic.setMode(modeID = 2)

  #------------------------------------------------------------------------------
  def onPreviousPageButtonClicked(self):
    # Update UI page
    self.homeWidget.logic.setMode(modeID = 2)

  #------------------------------------------------------------------------------
  def onNextPageButtonClicked(self):
    # Update UI page
    self.homeWidget.logic.setMode(modeID = 4)

    # Select first tab in training session tab widget
    self.homeWidget.ui.TrainingSessionPanel.ui.trainingTabWidget.currentIndex = 0

  #------------------------------------------------------------------------------
  #
  # Logic functions
  #
  #------------------------------------------------------------------------------
  
  
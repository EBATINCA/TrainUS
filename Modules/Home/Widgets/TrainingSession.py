from __main__ import vtk, qt, ctk, slicer
import logging
import os

#------------------------------------------------------------------------------
#
# TrainingSession
#
#------------------------------------------------------------------------------
class TrainingSession(qt.QWidget):

  def __init__(self, parent=None):
    super(TrainingSession, self).__init__(parent)

    # Define member variables
    self.homeWidget = None # Set externally after creation

  #------------------------------------------------------------------------------
  # Clean up when application is closed
  def cleanup(self):
    logging.debug('TrainingSession.cleanup')

    self.disconnect()

  #------------------------------------------------------------------------------
  def setupUi(self):
    logging.debug('TrainingSession.setupUi')

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiFilePath = os.path.join(self.homeWidget.logic.fileDir, 'Resources', 'UI', 'TrainingSession.ui')
    uiWidget = slicer.util.loadUI(uiFilePath)
    self.sectionLayout = qt.QVBoxLayout(self)
    self.sectionLayout.setContentsMargins(0, 0, 0, 0)
    self.sectionLayout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Customize widgets
    
    # Setup GUI connections
    self.setupConnections()

  #------------------------------------------------------------------------------
  def setupConnections(self):
    logging.debug('TrainingSession.setupConnections')

    self.ui.finishTrainingButton.clicked.connect(self.onFinishTrainingButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    logging.debug('TrainingSession.disconnect')

    self.ui.finishTrainingButton.clicked.disconnect()

  #------------------------------------------------------------------------------
  def updateGUIFromMRML(self, caller=None, event=None):
    """
    Set selections and other settings on the GUI based on the parameter node
    """
    del caller
    del event
    parameterNode = self.homeWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    pass


  #------------------------------------------------------------------------------
  #
  # Event handler functions
  #
  #------------------------------------------------------------------------------
  
  #------------------------------------------------------------------------------
  def onFinishTrainingButtonClicked(self):
    # Update UI page
    self.homeWidget.updateUIforMode(modeID = 0) # switch back to welcome page

  
  #------------------------------------------------------------------------------
  #
  # Logic functions
  #
  #------------------------------------------------------------------------------

from __main__ import vtk, qt, ctk, slicer
import logging
import os

#------------------------------------------------------------------------------
#
# PlugAndPlay
#
#------------------------------------------------------------------------------
class PlugAndPlay(qt.QWidget):

  def __init__(self, parent=None):
    super(PlugAndPlay, self).__init__(parent)

    # Define member variables
    self.homeWidget = None # Set externally after creation
    self.trainUsWidget = slicer.trainUsWidget

    # GUI flags
    self.recordingDetailsVisible = False

  #------------------------------------------------------------------------------
  # Clean up when application is closed
  def cleanup(self):
    logging.debug('PlugAndPlay.cleanup')

    self.disconnect()

  #------------------------------------------------------------------------------
  def setupUi(self):
    logging.debug('PlugAndPlay.setupUi')

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiFilePath = os.path.join(self.homeWidget.logic.fileDir, 'Resources', 'UI', 'PlugAndPlay.ui')
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
    logging.debug('PlugAndPlay.setupConnections')

    self.ui.previousPageButton.clicked.connect(self.onPreviousPageButtonClicked)
    self.ui.nextPageButton.clicked.connect(self.onNextPageButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    logging.debug('PlugAndPlay.disconnect')

    self.ui.previousPageButton.clicked.disconnect()
    self.ui.nextPageButton.clicked.disconnect()

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

    

  #------------------------------------------------------------------------------
  #
  # Event handler functions
  #
  #------------------------------------------------------------------------------
  
  #------------------------------------------------------------------------------
  def onPreviousPageButtonClicked(self):
    # Update UI page
    self.homeWidget.updateUIforMode(modeID = 3)

  #------------------------------------------------------------------------------
  def onNextPageButtonClicked(self):
    # Update UI page
    self.homeWidget.updateUIforMode(modeID = 5)

  #------------------------------------------------------------------------------
  #
  # Logic functions
  #
  #------------------------------------------------------------------------------

  
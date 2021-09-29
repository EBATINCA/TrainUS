from __main__ import vtk, qt, ctk, slicer
import logging
import os

#------------------------------------------------------------------------------
#
# Configuration
#
#------------------------------------------------------------------------------
class Configuration(qt.QWidget):

  def __init__(self, parent=None):
    super(Configuration, self).__init__(parent)

    # Define member variables
    self.homeWidget = None # Set externally after creation

  #------------------------------------------------------------------------------
  # Clean up when application is closed
  def cleanup(self):
    logging.debug('Configuration.cleanup')

    self.disconnect()

  #------------------------------------------------------------------------------
  def setupUi(self):
    logging.debug('Configuration.setupUi')

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiFilePath = os.path.join(self.homeWidget.logic.fileDir, 'Resources', 'UI', 'Configuration.ui')
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
    logging.debug('Configuration.setupConnections')

    self.ui.ultrasoundDisplaySettingsButton.clicked.connect(self.onUltrasoundDisplaySettingsButton)

  #------------------------------------------------------------------------------
  def disconnect(self):
    logging.debug('Configuration.disconnect')

    self.ui.ultrasoundDisplaySettingsButton.clicked.disconnect()

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
  def onUltrasoundDisplaySettingsButton(self):
    
    # Shows slicer interface
    self.homeWidget.hideHome()

    # Change to UltrasoundDisplaySettings module
    slicer.util.selectModule('UltrasoundDisplaySettings')



  #------------------------------------------------------------------------------
  #
  # Logic functions
  #
  #------------------------------------------------------------------------------

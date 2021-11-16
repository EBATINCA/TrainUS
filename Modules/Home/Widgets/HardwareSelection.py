from __main__ import vtk, qt, ctk, slicer
import logging
import os

#------------------------------------------------------------------------------
#
# HardwareSelection
#
#------------------------------------------------------------------------------
class HardwareSelection(qt.QWidget):

  def __init__(self, parent=None):
    super(HardwareSelection, self).__init__(parent)

    # Define member variables
    self.homeWidget = None # Set externally after creation
    self.trainUsWidget = slicer.trainUsWidget

  #------------------------------------------------------------------------------
  # Clean up when application is closed
  def cleanup(self):
    logging.debug('HardwareSelection.cleanup')

    self.disconnect()

  #------------------------------------------------------------------------------
  def setupUi(self):
    logging.debug('HardwareSelection.setupUi')

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiFilePath = os.path.join(self.homeWidget.logic.fileDir, 'Resources', 'UI', 'HardwareSelection.ui')
    uiWidget = slicer.util.loadUI(uiFilePath)
    self.sectionLayout = qt.QVBoxLayout(self)
    self.sectionLayout.setContentsMargins(0, 0, 0, 0)
    self.sectionLayout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Customize widgets
    ## Ultrasound device selection combo box
    for option in self.trainUsWidget.logic.ultrasoundDeviceOptions:
      self.ui.ultrasoundDeviceComboBox.addItem(option)
    ## Tracking system selection combo box
    for option in self.trainUsWidget.logic.trackingSystemOptions:
      self.ui.trackingSystemComboBox.addItem(option)
    ## Simulation phantom selection combo box
    for option in self.trainUsWidget.logic.simulationPhantomOptions:
      self.ui.simulationPhantomComboBox.addItem(option)

    # Setup GUI connections
    self.setupConnections()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def setupConnections(self):
    logging.debug('HardwareSelection.setupConnections')
    
    self.ui.ultrasoundDeviceComboBox.currentTextChanged.connect(self.onUltrasoundDeviceComboBoxTextChanged)
    self.ui.trackingSystemComboBox.currentTextChanged.connect(self.onTrackingSystemComboBoxTextChanged)
    self.ui.simulationPhantomComboBox.currentTextChanged.connect(self.onSimulationPhantomComboBoxTextChanged)
    self.ui.previousPageButton.clicked.connect(self.onPreviousPageButtonClicked)
    self.ui.nextPageButton.clicked.connect(self.onNextPageButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    logging.debug('HardwareSelection.disconnect')

    self.ui.ultrasoundDeviceComboBox.currentTextChanged.disconnect()
    self.ui.trackingSystemComboBox.currentTextChanged.disconnect()
    self.ui.simulationPhantomComboBox.currentTextChanged.disconnect()
    self.ui.previousPageButton.clicked.disconnect()
    self.ui.nextPageButton.clicked.disconnect()

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

    # Update combo box selection from parameter node
    self.ui.ultrasoundDeviceComboBox.currentText = parameterNode.GetParameter(self.trainUsWidget.logic.selectedUltrasoundDeviceParameterName)
    self.ui.trackingSystemComboBox.currentText = parameterNode.GetParameter(self.trainUsWidget.logic.selectedTrackingSystemParameterName)
    self.ui.simulationPhantomComboBox.currentText = parameterNode.GetParameter(self.trainUsWidget.logic.selectedSimulationPhantomParameterName)

  #------------------------------------------------------------------------------
  #
  # Event handler functions
  #
  #------------------------------------------------------------------------------
  
  #------------------------------------------------------------------------------
  def onUltrasoundDeviceComboBoxTextChanged(self, text):
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Update parameter node
    parameterNode.SetParameter(self.trainUsWidget.logic.selectedUltrasoundDeviceParameterName, text)

  #------------------------------------------------------------------------------
  def onTrackingSystemComboBoxTextChanged(self, text):
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Update parameter node
    parameterNode.SetParameter(self.trainUsWidget.logic.selectedTrackingSystemParameterName, text)

  #------------------------------------------------------------------------------
  def onSimulationPhantomComboBoxTextChanged(self, text):
    # Parameter node
    parameterNode = self.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Update parameter node
    parameterNode.SetParameter(self.trainUsWidget.logic.selectedSimulationPhantomParameterName, text)

  #------------------------------------------------------------------------------
  def onPreviousPageButtonClicked(self):
    # Update UI page
    self.homeWidget.logic.setMode(modeID = 1)

  #------------------------------------------------------------------------------
  def onNextPageButtonClicked(self):
    # Update UI page
    self.homeWidget.logic.setMode(modeID = 3)

  #------------------------------------------------------------------------------
  #
  # Logic functions
  #
  #------------------------------------------------------------------------------

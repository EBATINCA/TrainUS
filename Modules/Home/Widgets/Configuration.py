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
    self.trainUsWidget = slicer.trainUsWidget

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
    logging.debug('Configuration.setupConnections')
    
    self.ui.ultrasoundDeviceComboBox.currentTextChanged.connect(self.onUltrasoundDeviceComboBoxTextChanged)
    self.ui.trackingSystemComboBox.currentTextChanged.connect(self.onTrackingSystemComboBoxTextChanged)
    self.ui.simulationPhantomComboBox.currentTextChanged.connect(self.onSimulationPhantomComboBoxTextChanged)
    self.ui.plusConnectionButton.clicked.connect(self.onPlusConnectionButton)
    self.ui.ultrasoundDisplaySettingsButton.clicked.connect(self.onUltrasoundDisplaySettingsButton)
    self.ui.previousPageButton.clicked.connect(self.onPreviousPageButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    logging.debug('Configuration.disconnect')

    self.ui.ultrasoundDeviceComboBox.currentTextChanged.disconnect()
    self.ui.trackingSystemComboBox.currentTextChanged.disconnect()
    self.ui.simulationPhantomComboBox.currentTextChanged.disconnect()
    self.ui.plusConnectionButton.clicked.disconnect()
    self.ui.ultrasoundDisplaySettingsButton.clicked.disconnect()
    self.ui.previousPageButton.clicked.disconnect()

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
  def onPlusConnectionButton(self):
    
    # Shows slicer interface
    self.homeWidget.hideHome()

    # Change to UltrasoundDisplaySettings module
    slicer.util.selectModule('PlusServerConnection')

  #------------------------------------------------------------------------------
  def onUltrasoundDisplaySettingsButton(self):
    
    # Shows slicer interface
    self.homeWidget.hideHome()

    # Change to UltrasoundDisplaySettings module
    slicer.util.selectModule('UltrasoundDisplaySettings')

  #------------------------------------------------------------------------------
  def onPreviousPageButtonClicked(self):
    
    # Update UI page
    self.homeWidget.updateUIforMode(modeID = 0)

  #------------------------------------------------------------------------------
  #
  # Logic functions
  #
  #------------------------------------------------------------------------------

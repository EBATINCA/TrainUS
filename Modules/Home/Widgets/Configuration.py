from __main__ import vtk, qt, ctk, slicer
import logging
import os

# TrainUS parameters
import TrainUSLib.TrainUSParameters as Parameters

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
    self.ui.toolTrackingStatusButton.clicked.connect(self.onToolTrackingStatusButton)
    self.ui.toolPivotCalibrationButton.clicked.connect(self.onToolPivotCalibrationButton)
    self.ui.previousPageButton.clicked.connect(self.onPreviousPageButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    logging.debug('Configuration.disconnect')

    self.ui.ultrasoundDeviceComboBox.currentTextChanged.disconnect()
    self.ui.trackingSystemComboBox.currentTextChanged.disconnect()
    self.ui.simulationPhantomComboBox.currentTextChanged.disconnect()
    self.ui.plusConnectionButton.clicked.disconnect()
    self.ui.ultrasoundDisplaySettingsButton.clicked.disconnect()
    self.ui.toolTrackingStatusButton.clicked.disconnect()
    self.ui.toolPivotCalibrationButton.clicked.disconnect()
    self.ui.previousPageButton.clicked.disconnect()

  #------------------------------------------------------------------------------
  def updateGUIFromMRML(self, caller=None, event=None):
    """
    Set selections and other settings on the GUI based on the parameter node
    """
    del caller
    del event
    parameterNode = Parameters.instance.getParameterNode()
    
    # Update combo box selection from parameter node    
    self.ui.ultrasoundDeviceComboBox.currentText = Parameters.instance.getParameterString(Parameters.SELECTED_ULTRASOUND)
    self.ui.trackingSystemComboBox.currentText = Parameters.instance.getParameterString(Parameters.SELECTED_TRACKER)
    self.ui.simulationPhantomComboBox.currentText = Parameters.instance.getParameterString(Parameters.SELECTED_PHANTOM)

    # Update Plus config file and server paths according to selected devices
    plusServerPath = self.trainUsWidget.logic.deviceManager.getUltrasoundDevicePlusServerPathFromSelection()
    Parameters.instance.setParameter(Parameters.PLUS_SERVER_PATH, plusServerPath)
    plusServerLauncherPath = self.trainUsWidget.logic.deviceManager.getUltrasoundDevicePlusServerLauncherPathFromSelection()
    Parameters.instance.setParameter(Parameters.PLUS_SERVER_LAUNCHER_PATH, plusServerLauncherPath)
    usPlusConfigFilePath = self.trainUsWidget.logic.deviceManager.getUltrasoundDeviceConfigFilePathFromSelection()
    Parameters.instance.setParameter(Parameters.ULTRASOUND_PLUS_CONFIG_PATH, usPlusConfigFilePath)
    trackerPlusConfigFilePath = self.trainUsWidget.logic.deviceManager.getTrackerDeviceConfigFilePathFromSelection()
    Parameters.instance.setParameter(Parameters.TRACKER_PLUS_CONFIG_PATH, trackerPlusConfigFilePath)

  #------------------------------------------------------------------------------
  #
  # Event handler functions
  #
  #------------------------------------------------------------------------------
  
  #------------------------------------------------------------------------------
  def onUltrasoundDeviceComboBoxTextChanged(self, text):
    # Update parameter node
    Parameters.instance.setParameter(Parameters.SELECTED_ULTRASOUND, text)

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onTrackingSystemComboBoxTextChanged(self, text):
    # Update parameter node
    Parameters.instance.setParameter(Parameters.SELECTED_TRACKER, text)

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onSimulationPhantomComboBoxTextChanged(self, text):
    # Update parameter node
    Parameters.instance.setParameter(Parameters.SELECTED_PHANTOM, text)

    # Update GUI
    self.updateGUIFromMRML()

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
  def onToolTrackingStatusButton(self):
    
    # Shows slicer interface
    self.homeWidget.hideHome()

    # Change to ToolTrackingStatus module
    slicer.util.selectModule('ToolTrackingStatus')

  #------------------------------------------------------------------------------
  def onToolPivotCalibrationButton(self):
    
    # Shows slicer interface
    self.homeWidget.hideHome()

    # Change to ToolTrackingStatus module
    slicer.util.selectModule('ToolPivotCalibration')

  #------------------------------------------------------------------------------
  def onPreviousPageButtonClicked(self):
    
    # Update UI page
    self.homeWidget.logic.setMode(modeID = 0)

  #------------------------------------------------------------------------------
  #
  # Logic functions
  #
  #------------------------------------------------------------------------------

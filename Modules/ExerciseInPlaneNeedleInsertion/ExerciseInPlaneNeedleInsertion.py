import vtk, qt, ctk, slicer
import os
import numpy as np
import time

from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

import logging

import json

#------------------------------------------------------------------------------
#
# ExerciseInPlaneNeedleInsertion
#
#------------------------------------------------------------------------------
class ExerciseInPlaneNeedleInsertion(ScriptedLoadableModule):
  
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Exercise In-Plane Needle Insertion"
    self.parent.categories = ["TrainUS"]
    self.parent.dependencies = []
    self.parent.contributors = ["David Garcia Mato (Ebatinca)"]
    self.parent.helpText = """ Module to train US-guided needle insertion. """
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """This project has been funded by NEOTEC grant from the Centre for the Development of Technology and Innovation (CDTI) of the Ministry for Science and Innovation of the Government of Spain."""

#------------------------------------------------------------------------------
#
# ExerciseInPlaneNeedleInsertionWidget
#
#------------------------------------------------------------------------------
class ExerciseInPlaneNeedleInsertionWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  
  def __init__(self, parent):
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)

    # Create logic class
    self.logic = ExerciseInPlaneNeedleInsertionLogic(self)

    slicer.ExerciseInPlaneNeedleInsertionWidget = self # ONLY FOR DEVELOPMENT

    # TrainUS widget
    #self.trainUsWidget = slicer.trainUsWidget

  #------------------------------------------------------------------------------
  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Set up UI
    self.setupUi()

    # Setup connections
    self.setupConnections()

    # The parameter node had defaults at creation, propagate them to the GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onClose(self, unusedOne, unusedTwo):
    pass

  #------------------------------------------------------------------------------
  def cleanup(self):
    self.disconnect()

  #------------------------------------------------------------------------------
  def enter(self):
    """
    Runs whenever the module is reopened
    """
    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def exit(self):
    """
    Runs when exiting the module.
    """
    pass

  #------------------------------------------------------------------------------
  def setupUi(self):    
    # Load widget from .ui file (created by Qt Designer).
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/ExerciseInPlaneNeedleInsertion.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Customize widgets
    self.ui.showInstructionsButton.setText('Show')
    self.ui.trimSequenceGroupBox.collapsed = True
    self.ui.recordingTimerWidget.slider().visible = False
    self.ui.metricSelectionFrame.visible = False
    self.ui.videoInstructionsButton.setIcon(qt.QIcon(self.resourcePath('Icons/videoIcon_small.png')))    
    self.ui.videoInstructionsButton.minimumWidth = self.ui.videoInstructionsButton.sizeHint.height()

    # Disable slice annotations immediately
    sliceAnnotations = slicer.modules.DataProbeInstance.infoWidget.sliceAnnotations
    sliceAnnotations.sliceViewAnnotationsEnabled = False
    sliceAnnotations.updateSliceViewFromGUI()

  #------------------------------------------------------------------------------
  def setupConnections(self):    
    # Load data
    self.ui.loadDataButton.clicked.connect(self.onLoadDataButtonClicked)
    # Mode
    self.ui.modeSelectionComboBox.currentTextChanged.connect(self.onModeSelectionComboBoxTextChanged)
    # Instructions
    self.ui.showInstructionsButton.clicked.connect(self.onShowInstructionsButtonClicked)
    self.ui.previousInstructionButton.clicked.connect(self.onPreviousInstructionButtonClicked)
    self.ui.nextInstructionButton.clicked.connect(self.onNextInstructionButtonClicked)
    self.ui.videoInstructionsButton.clicked.connect(self.onVideoInstructionsButtonClicked)
    # Difficulty
    self.ui.easyRadioButton.toggled.connect(self.onDifficultyRadioButtonToggled)
    self.ui.mediumRadioButton.toggled.connect(self.onDifficultyRadioButtonToggled)
    self.ui.hardRadioButton.toggled.connect(self.onDifficultyRadioButtonToggled)
    # Target generator
    self.ui.generateTargetButton.clicked.connect(self.onGenerateTargetButtonClicked)
    # Recording
    self.ui.startStopRecordingButton.clicked.connect(self.onStartStopRecordingButtonClicked)
    self.ui.clearRecordingButton.clicked.connect(self.onClearRecordingButtonClicked)
    self.ui.saveRecordingButton.clicked.connect(self.onSaveRecordingButtonClicked)
    # Load recording
    self.ui.loadRecordingFileButton.clicked.connect(self.onLoadRecordingFileButtonClicked)
    # Trim sequence
    self.ui.trimSequenceGroupBox.toggled.connect(self.onTrimSequenceGroupBoxCollapsed)
    self.ui.trimSequenceDoubleRangeSlider.valuesChanged.connect(self.onTrimSequenceDoubleRangeSliderModified)
    self.ui.trimSequenceDoubleRangeSlider.minimumPositionChanged.connect(self.onTrimSequenceMinPosDoubleRangeSliderModified)
    self.ui.trimSequenceDoubleRangeSlider.maximumPositionChanged.connect(self.onTrimSequenceMaxPosDoubleRangeSliderModified)
    self.ui.trimSequenceButton.clicked.connect(self.onTrimSequenceButtonClicked)
    # View control
    self.ui.leftViewButton.clicked.connect(self.onLeftViewButtonClicked)
    self.ui.frontViewButton.clicked.connect(self.onFrontViewButtonClicked)
    self.ui.rightViewButton.clicked.connect(self.onRightViewButtonClicked)
    self.ui.bottomViewButton.clicked.connect(self.onBottomViewButtonClicked)
    self.ui.freeViewButton.clicked.connect(self.onFreeViewButtonClicked)
    # Compute metrics
    self.ui.computeRealTimeMetricsButton.clicked.connect(self.onComputeRealTimeMetricsButtonClicked)
    self.ui.displayPlotButton.clicked.connect(self.onDisplayPlotButtonClicked)
    self.ui.metricSelectionComboBox.currentTextChanged.connect(self.onMetricSelectionComboBoxTextChanged)
    self.ui.computeOverallMetricsButton.clicked.connect(self.onComputeOverallMetricsButtonClicked)
    self.ui.displayTableButton.clicked.connect(self.onDisplayTableButtonClicked)
    # Back to menu
    self.ui.backToMenuButton.clicked.connect(self.onBackToMenuButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    # Load data
    self.ui.loadDataButton.clicked.disconnect()    
    # Mode
    self.ui.modeSelectionComboBox.currentTextChanged.disconnect()
    # Instructions
    self.ui.showInstructionsButton.clicked.disconnect()
    self.ui.previousInstructionButton.clicked.disconnect()
    self.ui.nextInstructionButton.clicked.disconnect()    
    self.ui.videoInstructionsButton.clicked.disconnect()    
    # Difficulty
    self.ui.easyRadioButton.clicked.disconnect()
    self.ui.mediumRadioButton.clicked.disconnect()
    self.ui.hardRadioButton.clicked.disconnect()
    # Target generator
    self.ui.generateTargetButton.clicked.disconnect()
    # Recording
    self.ui.startStopRecordingButton.clicked.disconnect()
    self.ui.clearRecordingButton.clicked.disconnect()
    self.ui.saveRecordingButton.clicked.disconnect()
    # Load recording
    self.ui.loadRecordingFileButton.clicked.disconnect()
    # Trim sequence
    self.ui.trimSequenceGroupBox.toggled.disconnect()
    self.ui.trimSequenceDoubleRangeSlider.valuesChanged.disconnect()
    self.ui.trimSequenceDoubleRangeSlider.minimumPositionChanged.disconnect()
    self.ui.trimSequenceDoubleRangeSlider.maximumPositionChanged.disconnect()
    self.ui.trimSequenceButton.clicked.disconnect()
    # View control
    self.ui.leftViewButton.clicked.disconnect()
    self.ui.frontViewButton.clicked.disconnect()
    self.ui.rightViewButton.clicked.disconnect()
    self.ui.bottomViewButton.clicked.disconnect()
    self.ui.freeViewButton.clicked.disconnect()
    # Compute metrics
    self.ui.computeRealTimeMetricsButton.clicked.disconnect()
    self.ui.displayPlotButton.clicked.disconnect()
    self.ui.metricSelectionComboBox.currentTextChanged.disconnect()
    self.ui.computeOverallMetricsButton.clicked.disconnect()
    self.ui.displayTableButton.clicked.disconnect()
    # Back to menu
    self.ui.backToMenuButton.clicked.disconnect()

  #------------------------------------------------------------------------------
  def updateGUIFromMRML(self, caller=None, event=None):
    """
    Set selections and other settings on the GUI based on the parameter node.

    Calls the updateGUIFromMRML function of all tabs so that they can take care of their own GUI.
    """    
    # Load data button
    self.ui.loadDataButton.enabled = self.ui.easyRadioButton.isChecked() or self.ui.mediumRadioButton.isChecked() or self.ui.hardRadioButton.isChecked()

    # Mode
    if self.logic.exerciseMode == 'Recording':
      self.ui.instructionsGroupBox.visible = True
      self.ui.difficultyGroupBox.visible = True
      self.ui.targetGeneratorGroupBox.visible = True
      self.ui.recordingGroupBox.visible = True
      self.ui.importRecordingGroupBox.visible = False
      self.ui.playbackGroupBox.visible = False
      self.ui.viewControllerGroupBox.visible = False
      self.ui.metricsGroupBox.visible = False
    elif self.logic.exerciseMode == 'Evaluation':
      self.ui.instructionsGroupBox.visible = True
      self.ui.difficultyGroupBox.visible = True
      self.ui.targetGeneratorGroupBox.visible = False
      self.ui.recordingGroupBox.visible = False
      self.ui.importRecordingGroupBox.visible = True
      self.ui.playbackGroupBox.visible = True
      self.ui.viewControllerGroupBox.visible = True
      self.ui.metricsGroupBox.visible = True
    else:
      logging.error('Invalid exercise mode...')

    # Show/Hide instruction images
    if self.logic.instructionsImagesVisible:
      self.ui.showInstructionsButton.setText('Hide')
      self.ui.previousInstructionButton.enabled = True
      self.ui.nextInstructionButton.enabled = True
      self.ui.videoInstructionsButton.enabled = False
    else:
      self.ui.showInstructionsButton.setText('Show')
      self.ui.previousInstructionButton.enabled = False
      self.ui.nextInstructionButton.enabled = False
      self.ui.videoInstructionsButton.enabled = True

    # Show/Hide instruction video
    if self.logic.instructionsVideoVisible:
      self.ui.videoInstructionsButton.checked = True
      self.ui.showInstructionsButton.enabled = False
    else:
      self.ui.videoInstructionsButton.checked = False
      self.ui.showInstructionsButton.enabled = True    

    # Difficulty
    if self.logic.exerciseDifficulty == 'Easy':
      self.ui.easyRadioButton.checked = True
    elif self.logic.exerciseDifficulty == 'Medium':
      self.ui.mediumRadioButton.checked = True
    elif self.logic.exerciseDifficulty == 'Hard':
      self.ui.hardRadioButton.checked = True

    # Start/Stop recording
    if self.logic.sequenceBrowserUtils.getRecordingInProgress():
      self.ui.startStopRecordingButton.setText('Stop')
      self.ui.clearRecordingButton.enabled = False
      self.ui.saveRecordingButton.enabled = False
    else:
      self.ui.startStopRecordingButton.setText('Start')
      self.ui.clearRecordingButton.enabled = bool(self.logic.sequenceBrowserUtils.getSequenceBrowser())
      self.ui.saveRecordingButton.enabled = bool(self.logic.sequenceBrowserUtils.getSequenceBrowser())

    # Recording info
    self.ui.recordingLengthLabel.setText('{0:.3g} s'.format(self.logic.sequenceBrowserUtils.getRecordingLength()))
    if bool(self.logic.sequenceBrowserUtils.getSequenceBrowser()):
      self.ui.recordingTimerWidget.setMRMLSequenceBrowserNode(self.logic.sequenceBrowserUtils.getSequenceBrowser())

    # Playback
    if bool(self.logic.sequenceBrowserUtils.getSequenceBrowser()):
      self.ui.SequenceBrowserPlayWidget.enabled = True
      self.ui.SequenceBrowserPlayWidget.setMRMLSequenceBrowserNode(self.logic.sequenceBrowserUtils.getSequenceBrowser())
      self.ui.SequenceBrowserSeekWidget.enabled = True
      self.ui.SequenceBrowserSeekWidget.setMRMLSequenceBrowserNode(self.logic.sequenceBrowserUtils.getSequenceBrowser())
    else:
      self.ui.SequenceBrowserPlayWidget.enabled = False
      self.ui.SequenceBrowserSeekWidget.enabled = False

    # Trim sequence
    rangeSequence = self.logic.sequenceBrowserUtils.getTimeRangeInSequenceBrowser()
    if rangeSequence:
      self.ui.trimSequenceDoubleRangeSlider.minimum = rangeSequence[0]
      self.ui.trimSequenceDoubleRangeSlider.maximum = rangeSequence[1]
      self.ui.trimSequenceDoubleRangeSlider.minimumValue = rangeSequence[0]
      self.ui.trimSequenceDoubleRangeSlider.maximumValue = rangeSequence[1]
    if self.logic.sequenceBrowserUtils.isSequenceBrowserEmpty():
      self.ui.maxValueTrimSequenceLabel.text = '-'
      self.ui.minValueTrimSequenceLabel.text = '-'

    # Metric computation
    self.ui.computeRealTimeMetricsButton.enabled = not self.logic.sequenceBrowserUtils.isSequenceBrowserEmpty()
    self.ui.computeOverallMetricsButton.enabled = not self.logic.sequenceBrowserUtils.isSequenceBrowserEmpty()
    
    # Display plot
    plotVisible = self.logic.layoutUtils.isPlotVisibleInCurrentLayout()
    if plotVisible:
      self.ui.displayPlotButton.setText('Hide results')
    else:
      self.ui.displayPlotButton.setText('Show results')
    self.ui.metricSelectionComboBox.enabled = (not self.logic.sequenceBrowserUtils.isSequenceBrowserEmpty()) and plotVisible

    # Display table    
    tableVisible = self.logic.layoutUtils.isTableVisibleInCurrentLayout()
    if tableVisible:
      self.ui.displayTableButton.setText('Hide results')
    else:
      self.ui.displayTableButton.setText('Show results')

    # Update viewpoint
    self.logic.updateViewpoint()
    self.ui.leftViewButton.checked = False
    self.ui.frontViewButton.checked = False
    self.ui.rightViewButton.checked = False
    self.ui.bottomViewButton.checked = False
    self.ui.freeViewButton.checked = False
    if self.logic.currentViewpointMode == 'Left': self.ui.leftViewButton.checked = True
    if self.logic.currentViewpointMode == 'Front': self.ui.frontViewButton.checked = True
    if self.logic.currentViewpointMode == 'Right': self.ui.rightViewButton.checked = True
    if self.logic.currentViewpointMode == 'Bottom': self.ui.bottomViewButton.checked = True
    if self.logic.currentViewpointMode == 'Free': self.ui.freeViewButton.checked = True

  #------------------------------------------------------------------------------
  def onLoadDataButtonClicked(self):
    # Start exercise
    self.logic.setupScene()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onModeSelectionComboBoxTextChanged(self, text):
    # Update mode
    self.logic.exerciseMode = text

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onDifficultyRadioButtonToggled(self):
    # Determine input difficulty
    if self.ui.easyRadioButton.isChecked():
      self.logic.exerciseDifficulty = 'Easy'
    elif self.ui.mediumRadioButton.isChecked():
      self.logic.exerciseDifficulty = 'Medium'
    elif self.ui.hardRadioButton.isChecked():
      self.logic.exerciseDifficulty = 'Hard'
    else:
      self.logic.exerciseDifficulty = None

    # Update exercise settings
    self.logic.updateDifficulty()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onShowInstructionsButtonClicked(self):
    # Update instructions visibility flag
    self.logic.instructionsImagesVisible = not self.logic.instructionsImagesVisible

    # Update instruction display
    self.logic.updateDisplayExerciseInstructionsImages()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onPreviousInstructionButtonClicked(self):
    self.logic.previousExerciseInstruction()

  #------------------------------------------------------------------------------
  def onNextInstructionButtonClicked(self):
    self.logic.nextExerciseInstruction()

  #------------------------------------------------------------------------------
  def onVideoInstructionsButtonClicked(self):
    # Update instructions visibility flag
    self.logic.instructionsVideoVisible = not self.logic.instructionsVideoVisible

    # Update instruction display
    self.logic.updateDisplayExerciseInstructionsVideo()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onGenerateTargetButtonClicked(self):    
    # Generate random target ID
    targetID = self.logic.getRandomTargetID()

    # Load selected target
    self.logic.loadTarget(targetID)

  #------------------------------------------------------------------------------
  def onStartStopRecordingButtonClicked(self):    
    # Check recording status
    recordingInProgress = self.logic.sequenceBrowserUtils.getRecordingInProgress()

    # Update sequence browser recording status
    if recordingInProgress:
      # Stop recording
      self.logic.sequenceBrowserUtils.stopSequenceBrowserRecording()
    else:
      # Start recording
      synchronizedNodes = [self.logic.NeedleToTracker, self.logic.ProbeToTracker, self.logic.usImageVolumeNode]
      self.logic.sequenceBrowserUtils.setSynchronizedNodes(synchronizedNodes)
      self.logic.sequenceBrowserUtils.startSequenceBrowserRecording()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onClearRecordingButtonClicked(self):
    # Remove observer
    self.logic.removeObserverToMasterSequenceNode()

    # Delete previous recording
    self.logic.sequenceBrowserUtils.clearSequenceBrowser()

    # Create new recording
    synchronizedNodes = [self.logic.NeedleToTracker, self.logic.ProbeToTracker, self.logic.usImageVolumeNode]
    self.logic.sequenceBrowserUtils.setSynchronizedNodes(synchronizedNodes)
    self.logic.sequenceBrowserUtils.createNewSequenceBrowser()

    # Add observer
    self.logic.addObserverToMasterSequenceNode()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onSaveRecordingButtonClicked(self):
    # Generate recording file path
    filename = 'Recording-' + time.strftime("%Y%m%d-%H%M%S") + os.extsep + "sqbr"
    directory = self.logic.dataFolderPath
    filePath = os.path.join(directory, filename)

    # Save sequence browser node
    self.logic.sequenceBrowserUtils.saveSequenceBrowser(filePath)

    # Recording info to save in JSON file
    print('>>>>>>>>>>>>>>>>RECORDING SAVED<<<<<<<<<<<<<<<<')
    print('Date:', time.strftime("%Y%m%d"))
    print('Time:', time.strftime("%H%M%S"))
    print('Recording length:', self.logic.sequenceBrowserUtils.getRecordingLength())
    print('Target:', self.logic.targetFileName)
    print('User:', 'XXXXXXXXXXX')
    print('Hardware setup:', 'XXXXXXXXXXX')

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onLoadRecordingFileButtonClicked(self):    
    # Show dialog to select file path
    defaultPath = self.logic.dataFolderPath
    fileDialog = ctk.ctkFileDialog()
    fileDialog.setDirectory(defaultPath)
    fileDialog.setFilter(qt.QDir.Files)
    filters = ['*.sqbr']
    fileDialog.setNameFilters(filters)
    fileDialog.setFileMode(qt.QFileDialog().ExistingFile) # just one file can be selected
    fileDialog.exec_()
    selectedFiles = fileDialog.selectedFiles()
    if not selectedFiles:
      return
    filePath = selectedFiles[0]
    if not filePath:
      return

    # Remove observer
    self.logic.removeObserverToMasterSequenceNode()

    # Delete previous recording
    self.logic.sequenceBrowserUtils.clearSequenceBrowser()

    # Load sequence browser node
    self.logic.sequenceBrowserUtils.loadSequenceBrowser(filePath)

    # Add observer
    self.logic.addObserverToMasterSequenceNode()

    # Reset focal point in 3D view
    self.logic.layoutUtils.resetFocalPointInThreeDView()

    # Load recording info file
    recordingInfoFilePath = os.path.join(os.path.dirname(filePath), 'Recording_Info.json')
    recordingInfo = self.logic.readRecordingInfoFile(recordingInfoFilePath)

    # Update target corresponding to recording
    targetID = recordingInfo['options']['target']
    self.logic.loadTarget(targetID)

    # Update difficulty corresponding to recording
    self.logic.exerciseDifficulty = recordingInfo['options']['difficulty']

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onTrimSequenceGroupBoxCollapsed(self, toggled):
    pass

  #------------------------------------------------------------------------------
  def onTrimSequenceDoubleRangeSliderModified(self, minValue, maxValue):
    # Update UI labels to indicate current min and max values in slider range
    self.ui.minValueTrimSequenceLabel.text = str("{0:05.2f}".format(minValue)) + ' s'
    self.ui.maxValueTrimSequenceLabel.text = str("{0:05.2f}".format(maxValue)) + ' s'

  #------------------------------------------------------------------------------
  def onTrimSequenceMinPosDoubleRangeSliderModified(self, minValue):
    # Update current sample in sequence browser by modifying seek widget slider
    self.ui.SequenceBrowserSeekWidget.slider().value = self.logic.sequenceBrowserUtils.getSequenceBrowserItemFromTimestamp(minValue)

  #------------------------------------------------------------------------------
  def onTrimSequenceMaxPosDoubleRangeSliderModified(self, maxValue):
    # Update current sample in sequence browser by modifying seek widget slider
    self.ui.SequenceBrowserSeekWidget.slider().value = self.logic.sequenceBrowserUtils.getSequenceBrowserItemFromTimestamp(maxValue)

  #------------------------------------------------------------------------------
  def onTrimSequenceButtonClicked(self):
    # Get slider values
    minValue = self.ui.trimSequenceDoubleRangeSlider.minimumValue
    maxValue = self.ui.trimSequenceDoubleRangeSlider.maximumValue

    # Collapse trim sequence group box
    self.ui.trimSequenceGroupBox.collapsed = True

    # Trim sequence
    self.logic.sequenceBrowserUtils.trimSequenceBrowserRecording(minValue, maxValue)

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onLeftViewButtonClicked(self):
    # Update viewpoint
    self.logic.currentViewpointMode = 'Left'

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onFrontViewButtonClicked(self):
    # Update viewpoint
    self.logic.currentViewpointMode = 'Front'

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onRightViewButtonClicked(self):
    # Update viewpoint
    self.logic.currentViewpointMode = 'Right'

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onBottomViewButtonClicked(self):
    # Update viewpoint
    self.logic.currentViewpointMode = 'Bottom'

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onFreeViewButtonClicked(self):
    # Update viewpoint
    self.logic.currentViewpointMode = 'Free'

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onComputeRealTimeMetricsButtonClicked(self):    
    
    # Set wait cursor
    qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)

    # Compute real-time metrics
    self.logic.computeRealTimeMetricsFromRecording()

    # Remove current items in combo box
    numItems = self.ui.metricSelectionComboBox.count
    for itemID in range(numItems):
      self.ui.metricSelectionComboBox.removeItem(0)

    # Add items to metric selection combo box
    listOfMetrics = self.logic.plotChartUtils.getListOfMetrics()
    for metricName in listOfMetrics:
      self.ui.metricSelectionComboBox.addItem(metricName)

    # Restore cursor
    qt.QApplication.restoreOverrideCursor()
    
    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onComputeOverallMetricsButtonClicked(self):    
    
    # Set wait cursor
    qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)

    # Compute overall metrics using PerkTutor
    self.logic.computeOverallMetricsFromRecording()

    # Restore cursor
    qt.QApplication.restoreOverrideCursor()
    
    # Update GUI
    self.updateGUIFromMRML()    

  #------------------------------------------------------------------------------
  def onDisplayPlotButtonClicked(self):    
    # Display metrics
    self.logic.displayMetricPlot()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onDisplayTableButtonClicked(self):    
    # Display metrics
    self.logic.displayMetricTable()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onMetricSelectionComboBoxTextChanged(self, text):
    # Selected metric
    self.logic.selectedMetric = text

    # Update plot chart
    self.logic.updatePlotChart()
    
    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onBackToMenuButtonClicked(self):    
    # Go back to Home module
    #slicer.util.selectModule('Home') 
    print('Back to home!')

#---------------------------------------------------------------------------------------------#
#                                                                                             #
#                                                                                             #
#                                                                                             #
#                        ExerciseInPlaneNeedleInsertionLogic                                  #
#                                                                                             #
#                                                                                             #
#                                                                                             #
#---------------------------------------------------------------------------------------------#
class ExerciseInPlaneNeedleInsertionLogic(ScriptedLoadableModuleLogic, VTKObservationMixin):
  
  def __init__(self, widgetInstance, parent=None):
    ScriptedLoadableModuleLogic.__init__(self, parent)
    VTKObservationMixin.__init__(self)

    # Define member variables
    self.fileDir = os.path.dirname(__file__)
    # Only defined in case there is no other way but having to use the widget from the logic
    self.moduleWidget = widgetInstance

    # Import utility classes
    import TrainUsUtilities
    self.sequenceBrowserUtils= TrainUsUtilities.SequenceBrowserUtils()
    self.layoutUtils= TrainUsUtilities.LayoutUtils()
    self.plotChartUtils= TrainUsUtilities.PlaybackPlotChartUtils()
    self.metricCalculationUtils= TrainUsUtilities.MetricCalculationUtils()

    # Data path
    self.dataFolderPath = self.moduleWidget.resourcePath('ExerciseInPlaneNeedleInsertionData/')
    self.metricsDirectory = self.moduleWidget.resourcePath('ExerciseInPlaneNeedleInsertionData/Metrics/')

    # Exercise default settings
    self.exerciseDifficulty = 'Medium'  
    self.exerciseLayout = '3D only'
    self.exerciseMode = 'Evaluation'

    # Instructions
    self.instructionsImagesVisible = False
    self.instructionsVideoVisible = False

    # Viewpoint
    self.currentViewpointMode = 'Front' # default is front view

    # Observer
    self.observerID = None

    # Target nodes
    self.targetFileName = ''
    self.targetLineNode = None
    self.targetPointNode = None

    # Metric data
    self.sampleID = []
    self.timestamp = []
    self.needleTipToUsPlaneDistanceMm = []
    self.needleTipToTargetDistanceMm = []
    self.needleToUsPlaneAngleDeg = []
    self.needleToTargetLineInPlaneAngleDeg = []

    # PerkTutor node
    self.perkEvaluatorNode = None
    self.perkTutorMetricTableNode = None

  #------------------------------------------------------------------------------
  def loadData(self):
    logging.debug('Loading data')

    # Load instructions images
    try:
        self.instructionsImageVolume = slicer.util.getNode('Slide1')
    except:
      try:
        self.instructionsImageVolume = slicer.util.loadVolume(self.dataFolderPath + '/Instructions/Slide1.PNG')
      except:
        logging.error('ERROR: Instructions files could not be loaded...')

    # Load instructions video
    try:
      self.instructionsSequenceBrowser = slicer.util.loadNodeFromFile(self.dataFolderPath + '/Instructions/video.sqbr', 'Tracked Sequence Browser')
      self.instructionsVideoVolume = slicer.util.getNode('video')
    except:
      logging.error('ERROR:  Video instructions could not be loaded...')     

    # Load models
    self.usProbe_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'UsProbe_Telemed_L12', [1.0,0.93,0.91], visibility_bool = True, opacityValue = 1.0)    
    self.needle_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'NeedleModel', [1.0,0.86,0.68], visibility_bool = True, opacityValue = 1.0)

    # Load transforms
    self.NeedleToTracker = self.getOrCreateTransform('NeedleToTracker')
    self.ProbeToTracker = self.getOrCreateTransform('ProbeToTracker')
    #self.NeedleToTracker = self.loadTransformFromFile(self.dataFolderPath, 'NeedleToTracker') # ONLY FOR DEVELOPMENT
    #self.ProbeToTracker = self.loadTransformFromFile(self.dataFolderPath, 'ProbeToTracker') # ONLY FOR DEVELOPMENT
    self.TrackerToPatient = self.getOrCreateTransform('TrackerToPatient')
    self.NeedleTipToNeedle = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'NeedleTipToNeedle')
    self.ProbeModelToProbe = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'ProbeModelToProbe')
    self.ImageToProbe = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'ImageToProbe')

    # Load camera transforms
    self.LeftCameraToProbeModel = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'LeftCameraToProbeModel')
    self.FrontCameraToProbeModel = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'FrontCameraToProbeModel')
    self.RightCameraToProbeModel = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'RightCameraToProbeModel')
    self.BottomCameraToProbeModel = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'BottomCameraToProbeModel')

    # Get ultrasound image
    try:
      self.usImageVolumeNode = slicer.util.getNode('Image_Reference')
    except:
      try:
        self.usImageVolumeNode = slicer.util.loadVolume(self.dataFolderPath + '/Image_Reference.nrrd') # ONLY FOR DEVELOPMENT
      except:
        self.usImageVolumeNode = slicer.vtkMRMLScalarVolumeNode()
        self.usImageVolumeNode.SetName('Image_Reference')
        slicer.mrmlScene.AddNode(self.usImageVolumeNode)
        logging.error('ERROR: ' + 'Image_Reference' + ' volume not found in scene. Creating empty volume...')

  #------------------------------------------------------------------------------
  def setupScene(self):

    # Load exercise data
    self.loadData()

    # Build transform tree
    self.needle_model.SetAndObserveTransformNodeID(self.NeedleTipToNeedle.GetID())
    self.NeedleTipToNeedle.SetAndObserveTransformNodeID(self.NeedleToTracker.GetID())
    self.usProbe_model.SetAndObserveTransformNodeID(self.ProbeModelToProbe.GetID())
    self.usImageVolumeNode.SetAndObserveTransformNodeID(self.ImageToProbe.GetID())
    self.ProbeModelToProbe.SetAndObserveTransformNodeID(self.ProbeToTracker.GetID())    
    self.ImageToProbe.SetAndObserveTransformNodeID(self.ProbeToTracker.GetID())    
    self.NeedleToTracker.SetAndObserveTransformNodeID(self.TrackerToPatient.GetID())
    self.ProbeToTracker.SetAndObserveTransformNodeID(self.TrackerToPatient.GetID())

    # US probe camera transforms
    self.LeftCameraToProbeModel.SetAndObserveTransformNodeID(self.ProbeModelToProbe.GetID())
    self.FrontCameraToProbeModel.SetAndObserveTransformNodeID(self.ProbeModelToProbe.GetID())
    self.RightCameraToProbeModel.SetAndObserveTransformNodeID(self.ProbeModelToProbe.GetID())
    self.BottomCameraToProbeModel.SetAndObserveTransformNodeID(self.ProbeModelToProbe.GetID())    

    # Display US image in red slice view
    self.layoutUtils.showUltrasoundInSliceView(self.usImageVolumeNode, 'Red')

    # Remove 3D cube and 3D axis label from 3D view
    self.layoutUtils.hideCubeAndLabelsInThreeDView()

    # Reset focal point in 3D view
    self.layoutUtils.resetFocalPointInThreeDView()

    # Avoid needle model to be seen in yellow slice view during instructions display
    self.needle_model.GetModelDisplayNode().SetViewNodeIDs(('vtkMRMLSliceNodeRed', 'vtkMRMLViewNode1'))

    # Set difficulty parameters
    self.updateDifficulty()

  #------------------------------------------------------------------------------
  def updateDifficulty(self):
    # Set parameters according to difficulty
    if self.exerciseDifficulty == 'Easy':
      self.exerciseLayout = '2D + 3D'
      self.highlightModelsInImage = True
    elif self.exerciseDifficulty == 'Medium':
      self.exerciseLayout = '2D + 3D'
      self.highlightModelsInImage = False
    elif self.exerciseDifficulty == 'Hard':
      self.exerciseLayout = '2D only red'
      self.highlightModelsInImage = False
    else:
      self.exerciseLayout = '3D only'
      self.highlightModelsInImage = False
      logging.warning('Invalid difficulty level was selected.')

    # Update layout
    self.layoutUtils.setCustomLayout(self.exerciseLayout)

    # Set exercise layout as default layout 
    self.layoutUtils.setDefaultLayout(self.layoutUtils.getCurrentLayout())

    # Update model slice visibility
    try:
      # Display needle model projected in US image
      self.needle_model.GetModelDisplayNode().SetSliceDisplayModeToDistanceEncodedProjection()
      self.needle_model.GetModelDisplayNode().SetVisibility2D(self.highlightModelsInImage)
    except:
      pass

  #------------------------------------------------------------------------------
  def updateDisplayExerciseInstructionsImages(self):
    if self.instructionsImagesVisible:
      # Hide slice controller visibility
      self.layoutUtils.updateSliceControllerVisibility(False)
      
      # Switch to 2D only layout
      self.layoutUtils.setCustomLayout('2D only yellow')

      # Display instructions in yellow view
      self.layoutUtils.showImageInstructionsInSliceView(self.instructionsImageVolume, 'Yellow')
    else:
      # Restore slice controller visibility
      self.layoutUtils.updateSliceControllerVisibility(True)

      # Restore last layout if any
      self.layoutUtils.restoreDefaultLayout()

      # Restore difficulty settings
      self.updateDifficulty()

  #------------------------------------------------------------------------------
  def updateDisplayExerciseInstructionsVideo(self):
    if self.instructionsVideoVisible:
      # Hide slice controller visibility
      self.layoutUtils.updateSliceControllerVisibility(False)
      
      # Switch to 2D only layout
      self.layoutUtils.setCustomLayout('2D only green')

      # Display instructions in yellow view
      self.layoutUtils.showVideoInstructionsInSliceView(self.instructionsVideoVolume, 'Green')

      # Play video
      self.instructionsSequenceBrowser.SetPlaybackRateFps(5.0)
      self.instructionsSequenceBrowser.SelectFirstItem() # reset
      self.instructionsSequenceBrowser.SetPlaybackLooped(True)
      self.instructionsSequenceBrowser.SetPlaybackActive(True)
    else:
      # Restore slice controller visibility
      self.layoutUtils.updateSliceControllerVisibility(True)

      # Restore last layout if any
      self.layoutUtils.restoreDefaultLayout()

      # Restore difficulty settings
      self.updateDifficulty()

      # Stop video
      self.instructionsSequenceBrowser.SelectFirstItem() # reset
      self.instructionsSequenceBrowser.SetPlaybackActive(False)

  #------------------------------------------------------------------------------
  def previousExerciseInstruction(self):
    # Modify slice offset
    if self.instructionsImagesVisible:
      self.layoutUtils.previousInstructionInSliceView('Yellow')

  #------------------------------------------------------------------------------
  def nextExerciseInstruction(self):
    # Modify slice offset
    if self.instructionsImagesVisible:
      self.layoutUtils.nextInstructionInSliceView('Yellow')

  #------------------------------------------------------------------------------
  def getRandomTargetID(self):
    # Get targets in folder
    targetDataFolder = self.dataFolderPath + '/Targets/'
    targetFileList = os.listdir(targetDataFolder)
    numTargets = len(targetFileList)

    # Generate random target ID
    targetID = np.random.randint(0, numTargets) + 1
    return targetID
    
  #------------------------------------------------------------------------------
  def loadTarget(self, targetID):

    # Get target file location
    targetFileName = 'Target_' + str(targetID) + '.mrk.json'
    targetDataFolder = self.dataFolderPath + '/Targets/'

    # Remove previous target from scene
    if self.targetLineNode:
      slicer.mrmlScene.RemoveNode(self.targetLineNode)
      self.targetLineNode = None
    if self.targetPointNode:
      slicer.mrmlScene.RemoveNode(self.targetPointNode)
      self.targetPointNode = None    

    # Load selected target    
    targetFilePath = targetDataFolder + targetFileName
    try:
      self.targetLineNode = slicer.util.loadMarkups(targetFilePath)
      self.targetLineNode.SetName('Target Line')
    except:
      logging.error('ERROR: Target markups file could not be loaded')

    # Store target file name
    self.targetFileName = targetFileName

    # Generate target point
    self.targetPointNode = slicer.vtkMRMLMarkupsFiducialNode()
    slicer.mrmlScene.AddNode(self.targetPointNode)
    self.targetPointNode.SetName('Target Point')

    # Position target in line end
    lineEndPosition = [0,0,0]
    self.targetLineNode.GetNthControlPointPositionWorld(0, lineEndPosition)
    self.targetPointNode.AddControlPoint(vtk.vtkVector3d(lineEndPosition))

    # Transform targets to US image coordinate space
    self.targetPointNode.SetAndObserveTransformNodeID(self.ImageToProbe.GetID())
    self.targetLineNode.SetAndObserveTransformNodeID(self.ImageToProbe.GetID())

    # Set point node parameters
    self.targetPointNode.SetLocked(True)
    self.targetPointNode.GetDisplayNode().SetPropertiesLabelVisibility(False)
    self.targetPointNode.GetDisplayNode().SetPointLabelsVisibility(False)
    self.targetPointNode.GetDisplayNode().SetUseGlyphScale(False) # Activates absolute size mode
    self.targetPointNode.GetDisplayNode().SetGlyphSize(5) # 5 mm
    self.targetPointNode.GetDisplayNode().SetSelectedColor(0,1,0) # Green point
    self.targetPointNode.GetDisplayNode().SetOpacity(0.2)

    # Set line node parameters
    self.targetLineNode.SetLocked(True)
    self.targetLineNode.GetDisplayNode().SetPropertiesLabelVisibility(False)
    self.targetLineNode.GetDisplayNode().SetUseGlyphScale(False) # Activates absolute size mode
    self.targetLineNode.GetDisplayNode().SetGlyphSize(0.5)
    self.targetLineNode.GetDisplayNode().SetCurveLineSizeMode(True)
    self.targetLineNode.GetDisplayNode().SetLineDiameter(0.5)
    self.targetLineNode.GetDisplayNode().SetSelectedColor(0,1,0) # Green line
    self.targetLineNode.GetDisplayNode().SetOpacity(0.2)    

  #------------------------------------------------------------------------------
  def getOrCreateTransform(self, transformName):
    try:
        node = slicer.util.getNode(transformName)
    except:
        node=slicer.vtkMRMLLinearTransformNode()
        node.SetName(transformName)
        slicer.mrmlScene.AddNode(node)
        logging.error('ERROR: ' + transformName + ' transform was not found. Creating node as identity...')
    return node

  #------------------------------------------------------------------------------
  def loadTransformFromFile(self, transformFilePath, transformFileName):
    try:
        node = slicer.util.getNode(transformName)
    except:
        try:
          node = slicer.util.loadTransform(transformFilePath +  '/' + transformFileName + '.h5')
          print(transformFileName + ' transform loaded')
        except:
          node=slicer.vtkMRMLLinearTransformNode()
          node.SetName(transformFileName)
          slicer.mrmlScene.AddNode(node)
          logging.error('ERROR: ' + transformFileName + ' transform not found in path. Creating node as identity...')
    return node

  #------------------------------------------------------------------------------
  def loadModelFromFile(self, modelFilePath, modelFileName, colorRGB_array, visibility_bool, opacityValue):
    try:
        node = slicer.util.getNode(modelFileName)
    except:
        try:
          node = slicer.util.loadModel(modelFilePath + '/' + modelFileName + '.stl')
          node.GetModelDisplayNode().SetColor(colorRGB_array)
          node.GetModelDisplayNode().SetVisibility(visibility_bool)
          node.GetModelDisplayNode().SetOpacity(opacityValue)
          print(modelFileName + ' model loaded')
        except:
          node = None
          logging.error('ERROR: ' + modelFileName + ' model not found in path')
    return node

  #------------------------------------------------------------------------------
  def addObserverToMasterSequenceNode(self):
    """
    Add observer to master sequence node.
    """
    try:
      self.observerID = self.NeedleToTracker.AddObserver(slicer.vtkMRMLTransformableNode.TransformModifiedEvent, self.callbackCursorPosition)
    except:
      logging.error('Error adding observer to master sequence node...')    

  #------------------------------------------------------------------------------
  def removeObserverToMasterSequenceNode(self):
    """
    Remove observer from master sequence node.
    """
    if self.observerID:
      try:
        self.NeedleToTracker.RemoveObserver(self.observerID)
      except:
        logging.error('Error removing observer from master sequence node...')   

  #------------------------------------------------------------------------------
  def callbackCursorPosition(self, unused1=None, unused2=None):
    """
    Update cursor position in plot chart.
    """
    self.plotChartUtils.updateCursorPosition(self.sequenceBrowserUtils.getSelectedTimestampInSequenceBrowser())    

  #------------------------------------------------------------------------------
  def readRecordingInfoFile(self, filePath):
    """
    Reads recording's information from .json file.

    :param filePath: path to JSON file (string)

    :return recording info (dict)
    """
    try:
      with open(filePath, 'r') as inputFile:
        recordingInfo =  json.loads(inputFile.read())
    except:
      logging.error('Cannot read recording information from JSON file at ' + filePath)
      recordingInfo = None
    return recordingInfo

  #------------------------------------------------------------------------------
  def updateViewpoint(self):
    """
    Update virtual camera mode for 3D view.
    """
    # Select camera transform
    try:
      if self.currentViewpointMode == 'Left': cameraTransform = self.LeftCameraToProbeModel
      elif self.currentViewpointMode == 'Front': cameraTransform = self.FrontCameraToProbeModel
      elif self.currentViewpointMode == 'Right': cameraTransform = self.RightCameraToProbeModel
      elif self.currentViewpointMode == 'Bottom': cameraTransform = self.BottomCameraToProbeModel
      else: cameraTransform = None
    except:
      return

    # Update viewpoint in 3D view
    self.layoutUtils.activateViewpoint(cameraTransform)

  #------------------------------------------------------------------------------
  def computeRealTimeMetricsFromRecording(self):

    # Create message window to indicate to user what is happening
    progressDialog = self.showProgressDialog('Computing performance metrics. Please, wait...') 

    # Get number of items
    numItems = self.sequenceBrowserUtils.getNumberOfItemsInSequenceBrowser()

    # Metrics
    self.sampleID = []
    self.timestamp = []
    self.needleTipToUsPlaneDistanceMm = []
    self.needleTipToTargetDistanceMm = []
    self.needleToUsPlaneAngleDeg = []
    self.needleToTargetLineInPlaneAngleDeg = []

    # Check if targets are defined in the scene
    try:
      self.targetPointNode.GetName()
    except:
      logging.error('No target point is defined...')
      return
    try:
      self.targetLineNode.GetName()
    except:
      logging.error('No target line is defined...')
      return

    # Iterate along items
    self.sequenceBrowserUtils.selectFirstItemInSequenceBrowser() # reset
    for currentItem in range(numItems):

      # Update progress dialog if any
      if progressDialog:
        progress = (currentItem / numItems) * (progressDialog.maximum - progressDialog.minimum)
        progressDialog.setValue(progress)

      # Get timestamp
      timestamp = self.sequenceBrowserUtils.getTimestampFromItemID(currentItem)

      # Get target point position
      targetPoint = [0,0,0]
      self.targetPointNode.GetNthControlPointPositionWorld(0, targetPoint)

      # Get target line position
      targetLineStart = [0,0,0]
      targetLineEnd = [0,0,0]
      self.targetLineNode.GetNthControlPointPositionWorld(0, targetLineEnd)
      self.targetLineNode.GetNthControlPointPositionWorld(1, targetLineStart)

      #
      # Real-time metrics
      #
      # Get current tool positions
      self.metricCalculationUtils.getCurrentToolPositions(self.NeedleTipToNeedle, self.ProbeModelToProbe, self.ImageToProbe)

      # Distance from needle tip to US plane
      distance_NeedleTipToUSPlane = self.metricCalculationUtils.computeNeedleTipToUsPlaneDistanceMm()

      # Distance from needle tip to target point
      distance_NeedleTipToTargetPoint = self.metricCalculationUtils.computeNeedleTipToTargetDistanceMm(targetPoint)

      # Angle between needle and US plane
      angle_NeedleToUsPlane = self.metricCalculationUtils.computeNeedleToUsPlaneAngleDeg()

      # Angle between needle and target trajectory
      angle_NeedleToTargetLineInPlane = self.metricCalculationUtils.computeNeedleToTargetLineInPlaneAngleDeg(targetLineStart, targetLineEnd)

      # Store metrics
      self.sampleID.append(currentItem)
      self.timestamp.append(timestamp)
      self.needleTipToUsPlaneDistanceMm.append(distance_NeedleTipToUSPlane)
      self.needleTipToTargetDistanceMm.append(distance_NeedleTipToTargetPoint)
      self.needleToUsPlaneAngleDeg.append(angle_NeedleToUsPlane)
      self.needleToTargetLineInPlaneAngleDeg.append(angle_NeedleToTargetLineInPlane)

      # Next sample
      self.sequenceBrowserUtils.selectNextItemInSequenceBrowser()

    # Store real-time metric values
    self.plotChartUtils.addNewMetric('needleTipToUsPlaneDistanceMm', self.needleTipToUsPlaneDistanceMm)
    self.plotChartUtils.addNewMetric('needleTipToTargetDistanceMm', self.needleTipToTargetDistanceMm)
    self.plotChartUtils.addNewMetric('needleToUsPlaneAngleDeg', self.needleToUsPlaneAngleDeg)
    self.plotChartUtils.addNewMetric('needleToTargetLineInPlaneAngleDeg', self.needleToTargetLineInPlaneAngleDeg)

    # Store real-time metric timestamps
    self.plotChartUtils.addMetricTimestamps(self.timestamp)

    # Create real-time plot chart
    self.plotChartUtils.createPlotChart(cursor = True)

    # Hide progress dialog
    progressDialog.hide()
    progressDialog.deleteLater()

    # Display metrics
    self.displayMetricPlot()
    plotVisible = self.layoutUtils.isPlotVisibleInCurrentLayout()
    if not plotVisible:
      self.displayMetricPlot()

  #------------------------------------------------------------------------------
  def computeOverallMetricsFromRecording(self):    
    # Get Perk Evaluator logic
    peLogic = slicer.modules.perkevaluator.logic()
    if (peLogic is None):
      logging.error( "Could not find Perk Evaluator logic." )
      return

    # Delete existing metric script nodes
    oldMetricScriptNodes = vtk.vtkCollection()
    for oldMetricScriptNode in oldMetricScriptNodes:
      slicer.mrmlScene.RemoveNode(oldMetricScriptNode)

    # Delete existing metric instance nodes
    oldMetricInstanceNodes = vtk.vtkCollection()
    for oldMetricInstanceNode in oldMetricInstanceNodes:
      slicer.mrmlScene.RemoveNode(oldMetricInstanceNode)

    # Delete existing perk evaluator node if any
    if self.perkEvaluatorNode:
      slicer.mrmlScene.RemoveNode(self.perkEvaluatorNode)
      self.perkEvaluatorNode = None 

    # Create Perk Evaluator node
    self.perkEvaluatorNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLPerkEvaluatorNode')

    # Delete existing table node if any
    if self.perkTutorMetricTableNode:
      slicer.mrmlScene.RemoveNode(self.perkTutorMetricTableNode)
      self.perkTutorMetricTableNode = None 
    
    # Create table node to store PerkTutor metrics
    self.perkTutorMetricTableNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTableNode')
    self.perkTutorMetricTableNode.SetName('MetricsTable')
    self.perkTutorMetricTableNode.SetLocked(True) # lock table to avoid modifications
    self.perkTutorMetricTableNode.RemoveAllColumns() # reset

    # Assign table to PerkTutor node
    self.perkEvaluatorNode.SetMetricsTableID(self.perkTutorMetricTableNode.GetID())

    # Assign sequence browser to PerkTutor node
    sequenceBrowserNode = self.sequenceBrowserUtils.getSequenceBrowser()
    self.perkEvaluatorNode.SetTrackedSequenceBrowserNodeID(sequenceBrowserNode.GetID())

    # Remove all pervasive metric instances and just recreate the ones for the relevant transforms
    metricInstanceNodes = slicer.mrmlScene.GetNodesByClass( "vtkMRMLMetricInstanceNode" )
    for i in range( metricInstanceNodes.GetNumberOfItems() ):
      node = metricInstanceNodes.GetItemAsObject( i )
      pervasive = peLogic.GetMetricPervasive( node.GetAssociatedMetricScriptID() )
      needleTipRole = node.GetRoleID( "Any", slicer.vtkMRMLMetricInstanceNode.TransformRole ) == self.NeedleTipToNeedle.GetID()
      ultrasoundRole = node.GetRoleID( "Any", slicer.vtkMRMLMetricInstanceNode.TransformRole ) == self.ImageToProbe.GetID()
      if ( pervasive and not needleTipRole and not ultrasoundRole ):
        self.perkEvaluatorNode.RemoveMetricInstanceID( node.GetID() )

    # Load Python metric scripts
    metricScriptNodes = []
    dirfiles = os.listdir(self.metricsDirectory)
    for fileName in dirfiles:
      scriptNode = slicer.util.loadNodeFromFile( os.path.join( self.metricsDirectory, fileName ), "Python Metric Script", {} )
      if scriptNode:
        metricScriptNodes.append(scriptNode)

    # Add metric instances from script nodes
    for scriptNode in metricScriptNodes:
      metricInstanceNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMetricInstanceNode')
      metricInstanceNode.SetAssociatedMetricScriptID(scriptNode.GetID())
      self.perkEvaluatorNode.AddMetricInstanceID(metricInstanceNode.GetID())      

    # Assign roles to PerkTutor node
    peLogic.SetMetricInstancesRolesToID(self.perkEvaluatorNode, self.NeedleTipToNeedle.GetID(), "Any", slicer.vtkMRMLMetricInstanceNode().TransformRole)
    peLogic.SetMetricInstancesRolesToID(self.perkEvaluatorNode, self.NeedleTipToNeedle.GetID(), "Needle", slicer.vtkMRMLMetricInstanceNode().TransformRole)
    # peLogic.SetMetricInstancesRolesToID(peNode, tissueNode.GetID(), "Tissue", slicer.vtkMRMLMetricInstanceNode().AnatomyRole)
    peLogic.SetMetricInstancesRolesToID( self.perkEvaluatorNode, self.ImageToProbe.GetID(), "Ultrasound", slicer.vtkMRMLMetricInstanceNode().TransformRole )
    peLogic.SetMetricInstancesRolesToID( self.perkEvaluatorNode, self.perkTutorMetricTableNode.GetID(), "Parameter", slicer.vtkMRMLMetricInstanceNode.AnatomyRole )
    peLogic.SetMetricInstancesRolesToID( self.perkEvaluatorNode, self.targetPointNode.GetID(), "Targets", slicer.vtkMRMLMetricInstanceNode.AnatomyRole )

    # Create progress dialog
    analysisDialogWidget = slicer.qSlicerPerkEvaluatorAnalysisDialogWidget()
    analysisDialogWidget.setPerkEvaluatorNode( self.perkEvaluatorNode )
    analysisDialogWidget.show()

    # Compute metrics
    peLogic.ComputeMetrics(self.perkEvaluatorNode)

    # Hide progress dialog
    analysisDialogWidget.hide()

    # Display metrics
    self.displayMetricTable()

  #------------------------------------------------------------------------------
  def updatePlotChart(self):

    # Get selected metric name
    metricName = self.selectedMetric

    # Update visible plot series in plot chart
    self.plotChartUtils.updatePlotChart(metricName)  

  #------------------------------------------------------------------------------
  def displayMetricPlot(self):
    plotVisible = self.layoutUtils.isPlotVisibleInCurrentLayout()
    if plotVisible:
      # Restore last layout if any
      self.layoutUtils.restoreDefaultLayout()
    else:
      # Switch to layout with plot
      self.layoutUtils.setCustomLayout('2D + 3D + Plot')

      # Show plot chart in plot view
      self.layoutUtils.setActivePlotChart(self.plotChartUtils.getPlotChart())

      # Add combo box to plot controller
      metricSelectionFrame = self.moduleWidget.ui.metricSelectionFrame
      metricSelectionFrame.visible = True
      slicer.app.layoutManager().plotWidget(0).plotController().barWidget().layout().insertWidget(4,metricSelectionFrame)
      slicer.app.layoutManager().plotWidget(0).plotController().barWidget().layout().setStretch(4,1)

  #------------------------------------------------------------------------------
  def displayMetricTable(self):
    tableVisible = self.layoutUtils.isTableVisibleInCurrentLayout()
    if tableVisible:
      # Restore last layout if any
      self.layoutUtils.restoreDefaultLayout()
    else:
      # Switch to table only layout
      self.layoutUtils.setCustomLayout('2D + 3D + Table')    

      # Show table in table view
      self.layoutUtils.setActiveTable(self.perkTutorMetricTableNode)

  #------------------------------------------------------------------------------
  def showProgressDialog(self, messageText):
    """
    Show progress dialog during metric computation.
    """
    progressDialog = qt.QProgressDialog(messageText, 'Cancel', 0, 100, slicer.util.mainWindow())
    progressDialog.setCancelButton(None) # hide cancel button in dialog
    progressDialog.setMinimumWidth(300) # dialog size
    font = qt.QFont()
    font.setPointSize(12)
    progressDialog.setFont(font) # font size
    progressDialog.show()
    slicer.app.processEvents()
    return progressDialog

#------------------------------------------------------------------------------
#
# ExerciseInPlaneNeedleInsertionTest
#
#------------------------------------------------------------------------------
class ExerciseInPlaneNeedleInsertionTest(ScriptedLoadableModuleTest):
  """This is the test case for your scripted module.
  """

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    ScriptedLoadableModuleTest.runTest(self)

#
# Class for avoiding python error that is caused by the method SegmentEditor::setup
# http://issues.slicer.org/view.php?id=3871
#
class ExerciseInPlaneNeedleInsertionFileWriter(object):
  def __init__(self, parent):
    pass

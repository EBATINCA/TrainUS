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
    self.parent.acknowledgementText = """EBATINCA, S.L."""

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
    self.ui.computeMetricsButton.clicked.connect(self.onComputeMetricsButtonClicked)
    self.ui.displayPlotButton.clicked.connect(self.onDisplayPlotButtonClicked)
    self.ui.metricSelectionComboBox.currentTextChanged.connect(self.onMetricSelectionComboBoxTextChanged)
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
    self.ui.computeMetricsButton.clicked.disconnect()
    self.ui.displayPlotButton.clicked.disconnect()
    self.ui.metricSelectionComboBox.currentTextChanged.disconnect()
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

    # Show/Hide instructions
    if self.logic.intructionsVisible:
      self.ui.showInstructionsButton.setText('Hide')
      self.ui.previousInstructionButton.enabled = True
      self.ui.nextInstructionButton.enabled = True
    else:
      self.ui.showInstructionsButton.setText('Show')
      self.ui.previousInstructionButton.enabled = False
      self.ui.nextInstructionButton.enabled = False

    # Difficulty
    if self.logic.exerciseDifficulty == 'Easy':
      self.ui.easyRadioButton.checked = True
    elif self.logic.exerciseDifficulty == 'Medium':
      self.ui.mediumRadioButton.checked = True
    elif self.logic.exerciseDifficulty == 'Hard':
      self.ui.hardRadioButton.checked = True

    # Start/Stop recording
    if self.logic.sequenceBrowserManager.getRecordingInProgress():
      self.ui.startStopRecordingButton.setText('Stop')
      self.ui.clearRecordingButton.enabled = False
      self.ui.saveRecordingButton.enabled = False
    else:
      self.ui.startStopRecordingButton.setText('Start')
      self.ui.clearRecordingButton.enabled = bool(self.logic.sequenceBrowserManager.getSequenceBrowser())
      self.ui.saveRecordingButton.enabled = bool(self.logic.sequenceBrowserManager.getSequenceBrowser())

    # Recording info
    self.ui.recordingLengthLabel.setText('{0:.3g} s'.format(self.logic.sequenceBrowserManager.getRecordingLength()))
    if bool(self.logic.sequenceBrowserManager.getSequenceBrowser()):
      self.ui.recordingTimerWidget.setMRMLSequenceBrowserNode(self.logic.sequenceBrowserManager.getSequenceBrowser())

    # Playback
    if bool(self.logic.sequenceBrowserManager.getSequenceBrowser()):
      self.ui.SequenceBrowserPlayWidget.enabled = True
      self.ui.SequenceBrowserPlayWidget.setMRMLSequenceBrowserNode(self.logic.sequenceBrowserManager.getSequenceBrowser())
      self.ui.SequenceBrowserSeekWidget.enabled = True
      self.ui.SequenceBrowserSeekWidget.setMRMLSequenceBrowserNode(self.logic.sequenceBrowserManager.getSequenceBrowser())
    else:
      self.ui.SequenceBrowserPlayWidget.enabled = False
      self.ui.SequenceBrowserSeekWidget.enabled = False

    # Trim sequence
    rangeSequence = self.logic.sequenceBrowserManager.getTimeRangeInSequenceBrowser()
    if rangeSequence:
      self.ui.trimSequenceDoubleRangeSlider.minimum = rangeSequence[0]
      self.ui.trimSequenceDoubleRangeSlider.maximum = rangeSequence[1]
      self.ui.trimSequenceDoubleRangeSlider.minimumValue = rangeSequence[0]
      self.ui.trimSequenceDoubleRangeSlider.maximumValue = rangeSequence[1]
    if self.logic.sequenceBrowserManager.isSequenceBrowserEmpty():
      self.ui.maxValueTrimSequenceLabel.text = '-'
      self.ui.minValueTrimSequenceLabel.text = '-'

    # Metric computation
    self.ui.computeMetricsButton.enabled = not self.logic.sequenceBrowserManager.isSequenceBrowserEmpty()
    self.ui.metricSelectionComboBox.enabled = (not self.logic.sequenceBrowserManager.isSequenceBrowserEmpty()) and self.logic.plotVisible

    # Display plot
    self.ui.displayPlotButton.enabled = not self.logic.sequenceBrowserManager.isSequenceBrowserEmpty()
    self.ui.displayPlotButton.checked = self.logic.plotVisible

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
    self.logic.intructionsVisible = not self.logic.intructionsVisible

    # Update instruction display
    self.logic.updateDisplayExerciseInstructions()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onPreviousInstructionButtonClicked(self):
    self.logic.previousExerciseInstruction()

  #------------------------------------------------------------------------------
  def onNextInstructionButtonClicked(self):
    self.logic.nextExerciseInstruction()

  #------------------------------------------------------------------------------
  def onGenerateTargetButtonClicked(self):    
    # Generate random target ID
    targetID = self.logic.getRandomTargetID()

    # Load selected target
    self.logic.loadTarget(targetID)

  #------------------------------------------------------------------------------
  def onStartStopRecordingButtonClicked(self):    
    # Check recording status
    recordingInProgress = self.logic.sequenceBrowserManager.getRecordingInProgress()

    # Update sequence browser recording status
    if recordingInProgress:
      # Stop recording
      self.logic.sequenceBrowserManager.stopSequenceBrowserRecording()
    else:
      # Start recording
      self.logic.sequenceBrowserManager.startSequenceBrowserRecording()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onClearRecordingButtonClicked(self):
    # Remove observer
    self.logic.removeObserverToMasterSequenceNode()

    # Delete previous recording
    self.logic.sequenceBrowserManager.clearSequenceBrowser()

    # Create new recording
    browserName = 'TrainUS_Recording'
    synchronizedNodes = [self.logic.NeedleToTracker, self.logic.ProbeToTracker, self.logic.usImageVolumeNode]
    self.logic.sequenceBrowserManager.createNewSequenceBrowser(browserName, synchronizedNodes)

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
    self.logic.sequenceBrowserManager.saveSequenceBrowser(filePath)

    # Recording info to save in JSON file
    print('>>>>>>>>>>>>>>>>RECORDING SAVED<<<<<<<<<<<<<<<<')
    print('Date:', time.strftime("%Y%m%d"))
    print('Time:', time.strftime("%H%M%S"))
    print('Recording length:', self.sequenceBrowserManager.getRecordingLength())
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
    self.logic.sequenceBrowserManager.clearSequenceBrowser()

    # Load sequence browser node
    self.logic.sequenceBrowserManager.loadSequenceBrowser(filePath)

    # Add observer
    self.logic.addObserverToMasterSequenceNode()

    # Reset focal point in 3D view
    self.logic.layoutManager.resetFocalPointInThreeDView()

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
    self.ui.SequenceBrowserSeekWidget.slider().value = self.logic.sequenceBrowserManager.getSequenceBrowserItemFromTimestamp(minValue)

  #------------------------------------------------------------------------------
  def onTrimSequenceMaxPosDoubleRangeSliderModified(self, maxValue):
    # Update current sample in sequence browser by modifying seek widget slider
    self.ui.SequenceBrowserSeekWidget.slider().value = self.logic.sequenceBrowserManager.getSequenceBrowserItemFromTimestamp(maxValue)

  #------------------------------------------------------------------------------
  def onTrimSequenceButtonClicked(self):
    # Get slider values
    minValue = self.ui.trimSequenceDoubleRangeSlider.minimumValue
    maxValue = self.ui.trimSequenceDoubleRangeSlider.maximumValue

    # Collapse trim sequence group box
    self.ui.trimSequenceGroupBox.collapsed = True

    # Trim sequence
    self.logic.sequenceBrowserManager.trimSequenceBrowserRecording(minValue, maxValue)

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
  def onComputeMetricsButtonClicked(self):    
    
    # Set wait cursor
    qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)

    # Create message window to indicate to user what is happening
    progressDialog = self.showProgressDialog()

    # Compute metrics
    self.logic.computeMetricsFromRecording(progressDialog)

    # Remove current items in combo box
    numItems = self.ui.metricSelectionComboBox.count
    for itemID in range(numItems):
      self.ui.metricSelectionComboBox.removeItem(0)

    # Add items to metric selection combo box
    listOfMetrics = self.logic.plotChartManager.getListOfMetrics()
    for metricName in listOfMetrics:
      if (metricName != 'Sample ID') and (metricName != 'Timestamp'):
        self.ui.metricSelectionComboBox.addItem(metricName)

    # Hide plot
    self.logic.plotVisible = False
    self.logic.displayMetricPlot()

    # Restore cursor and hide progress dialog
    qt.QApplication.restoreOverrideCursor()
    progressDialog.hide()
    progressDialog.deleteLater()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onDisplayPlotButtonClicked(self):    
    # Update plot visibility flag
    self.logic.plotVisible = not self.logic.plotVisible

    # Display metrics
    self.logic.displayMetricPlot()

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

  #------------------------------------------------------------------------------
  def showProgressDialog(self):
    """
    Show progress dialog during metric computation.
    """
    progressDialog = qt.QProgressDialog('Computing performance metrics. Please, wait...', 'Cancel', 0, 100, slicer.util.mainWindow())
    progressDialog.setCancelButton(None) # hide cancel button in dialog
    progressDialog.setMinimumWidth(300) # dialog size
    font = qt.QFont()
    font.setPointSize(12)
    progressDialog.setFont(font) # font size
    progressDialog.show()
    slicer.app.processEvents()
    return progressDialog


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

    # Setup keyboard shortcuts
    self.setupKeyboardShortcuts()

    # Exercise settings
    self.exerciseDifficulty = 'Medium'  
    self.exerciseLayout = '3D only'
    self.exerciseMode = 'Evaluation'

    # Instructions
    self.intructionsVisible = False

    # Viewpoint
    self.currentViewpointMode = 'Front' # default is front view

    # Sequence browser manager
    import TrainUsUtilities
    self.sequenceBrowserManager = TrainUsUtilities.SequenceBrowserManager()
    self.layoutManager = TrainUsUtilities.LayoutManager()    
    self.plotChartManager = TrainUsUtilities.PlaybackPlotChartManager()

    # Observer
    self.observerID = None

    # Data path
    self.dataFolderPath = self.moduleWidget.resourcePath('ExerciseInPlaneNeedleInsertionData/')

    # Target nodes
    self.targetFileName = ''
    self.targetLineNode = None
    self.targetPointNode = None

    # Tool reference points
    self.NEEDLE_TIP = [0.0, 0.0, 0.0]
    self.NEEDLE_HANDLE = [0.0, 0.0, -50.0]
    self.USPROBE_TIP = [0.0, 0.0, 0.0]
    self.USPROBE_HANDLE = [0.0, 50.0, 0.0]
    self.USPLANE_ORIGIN = [0.0, 0.0, 0.0]
    self.USPLANE_NORMAL = [0.0, 0.0, 1.0]

    # Plot
    self.plotVisible = False

    # Metric data
    self.sampleID = []
    self.timestamp = []
    self.needleTipToUsPlaneDistanceMm = []
    self.needleTipToTargetDistanceMm = []
    self.needleToUsPlaneAngleDeg = []
    self.needleToTargetLineInPlaneAngleDeg = []

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
    self.layoutManager.setCustomLayout(self.exerciseLayout)

    # Update model slice visibility
    try:
      self.needle_model.GetModelDisplayNode().SetSliceIntersectionVisibility(self.highlightModelsInImage)
    except:
      pass

  #------------------------------------------------------------------------------
  def updateDisplayExerciseInstructions(self):

    if self.intructionsVisible:
      # Hide slice controller visibility
      self.layoutManager.updateSliceControllerVisibility(False)

      # Switch to 2D only layout
      self.layoutManager.setCustomLayout('2D only yellow')

      # Display instructions in yellow view
      self.layoutManager.showImageInstructionsInSliceView(self.instructions, 'Yellow')

    else:
      # Restore slice controller visibility
      self.layoutManager.updateSliceControllerVisibility(True)

      # Restore last layout if any
      self.layoutManager.restoreLastLayout()
      #self.needle_model.GetModelDisplayNode().SetSliceIntersectionVisibility(self.lastLayout[1]) # set model intersection visibility in slice

  #------------------------------------------------------------------------------
  def previousExerciseInstruction(self):
    # Modify slice offset
    if self.intructionsVisible:
      self.layoutManager.previousInstructionInSliceView('Yellow')

  #------------------------------------------------------------------------------
  def nextExerciseInstruction(self):
    # Modify slice offset
    if self.intructionsVisible:
      self.layoutManager.nextInstructionInSliceView('Yellow')

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
    self.layoutManager.showUltrasoundInSliceView(self.usImageVolumeNode, 'Red')

    # Remove 3D cube and 3D axis label from 3D view
    self.layoutManager.hideCubeAndLabelsInThreeDView()

    # Reset focal point in 3D view
    self.layoutManager.resetFocalPointInThreeDView()

    # Display needle model projected in US image
    self.needle_model.GetDisplayNode().SetSliceDisplayModeToDistanceEncodedProjection()
    self.needle_model.GetDisplayNode().SetVisibility2D(True)

    # Set difficulty parameters
    self.updateDifficulty()

  #------------------------------------------------------------------------------
  def loadData(self):
    logging.debug('Loading data')

    # Load exercise instructions
    try:
        self.instructions = slicer.util.getNode('Instructions1')
    except:
      try:
        self.instructions = slicer.util.loadVolume(self.dataFolderPath + '/Instructions/Instructions1.PNG')
      except:
        logging.error('ERROR: Instructions files could not be loaded...')

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
    self.plotChartManager.updateCursorPosition(self.sequenceBrowserManager.getSelectedItemInSequenceBrowser())    

  #------------------------------------------------------------------------------
  def readRecordingInfoFile(self, filePath):
    """
    Reads recording's information from .json file.

    :param filePath: path to JSON file (string)

    :return recording info (dict)
    """
    logging.debug('RecordingManager.readRecordingInfoFile')
    
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
    self.layoutManager.activateViewpoint(cameraTransform)

  #------------------------------------------------------------------------------
  def computeMetricsFromRecording(self, progressDialog = None):
    # Get number of items
    numItems = self.sequenceBrowserManager.getNumberOfItemsInSequenceBrowser()

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
    self.sequenceBrowserManager.selectFirstItemInSequenceBrowser() # reset
    for currentItem in range(numItems):

      # Update progress dialog if any
      if progressDialog:
        progress = (currentItem / numItems) * (progressDialog.maximum - progressDialog.minimum)
        progressDialog.setValue(progress)

      # Get timestamp
      timestamp = self.sequenceBrowserManager.GetTimestampFromItemID(currentItem)

      # Get needle position
      needleTip = self.getTransformedPoint(self.NEEDLE_TIP, self.NeedleTipToNeedle)
      needleHandle = self.getTransformedPoint(self.NEEDLE_HANDLE, self.NeedleTipToNeedle)

      # Get US probe position
      usProbeTip = self.getTransformedPoint(self.USPROBE_TIP, self.ProbeModelToProbe)
      usProbeHandle = self.getTransformedPoint(self.USPROBE_HANDLE, self.ProbeModelToProbe)

      # Get US image plane orientation
      usPlanePointA = self.getTransformedPoint(self.USPLANE_ORIGIN, self.ImageToProbe)
      usPlanePointB = self.getTransformedPoint(self.USPLANE_NORMAL, self.ImageToProbe)
      usPlaneCentroid = usPlanePointA
      usPlaneNormal = (usPlanePointB - usPlanePointA) / np.linalg.norm(usPlanePointB - usPlanePointA)

      # Get target point position
      targetPoint = [0,0,0]
      self.targetPointNode.GetNthControlPointPositionWorld(0, targetPoint)
      targetPoint = self.getTransformedPoint(targetPoint, None)

      # Get target line position
      targetLineStart = [0,0,0]
      targetLineEnd = [0,0,0]
      self.targetLineNode.GetNthControlPointPositionWorld(0, targetLineEnd)
      self.targetLineNode.GetNthControlPointPositionWorld(1, targetLineStart)
      targetLineStart = self.getTransformedPoint(targetLineStart, None)
      targetLineEnd = self.getTransformedPoint(targetLineEnd, None)

      #
      # Metrics
      #

      # Distance from needle tip to US plane
      distance_NeedleTipToUSPlane = self.computeNeedleTipToUsPlaneDistanceMm(needleTip, usPlaneCentroid, usPlaneNormal)

      # Distance from needle tip to target point
      distance_NeedleTipToTargetPoint = self.computeNeedleTipToTargetDistanceMm(needleTip, targetPoint)

      # Angle between needle and US plane
      angle_NeedleToUsPlane = self.computeNeedleToUsPlaneAngleDeg(needleTip, needleHandle, usPlaneCentroid, usPlaneNormal)

      # Angle between needle and target trajectory
      angle_NeedleToTargetLineInPlane = self.computeNeedleToTargetLineInPlaneAngleDeg(needleTip, needleHandle, targetLineStart, targetLineEnd, usPlaneCentroid, usPlaneNormal)

      # Store metrics
      self.sampleID.append(currentItem)
      self.timestamp.append(timestamp)
      self.needleTipToUsPlaneDistanceMm.append(distance_NeedleTipToUSPlane)
      self.needleTipToTargetDistanceMm.append(distance_NeedleTipToTargetPoint)
      self.needleToUsPlaneAngleDeg.append(angle_NeedleToUsPlane)
      self.needleToTargetLineInPlaneAngleDeg.append(angle_NeedleToTargetLineInPlane)

      # Next sample
      self.sequenceBrowserManager.SelectNextItemInSequenceBrowser()

    # Store metrics
    self.plotChartManager.addNewMetric('Sample ID', self.sampleID)
    self.plotChartManager.addNewMetric('Timestamp', self.timestamp)
    self.plotChartManager.addNewMetric('needleTipToUsPlaneDistanceMm', self.needleTipToUsPlaneDistanceMm)
    self.plotChartManager.addNewMetric('needleTipToTargetDistanceMm', self.needleTipToTargetDistanceMm)
    self.plotChartManager.addNewMetric('needleToUsPlaneAngleDeg', self.needleToUsPlaneAngleDeg)
    self.plotChartManager.addNewMetric('needleToTargetLineInPlaneAngleDeg', self.needleToTargetLineInPlaneAngleDeg)

    # Create plot chart
    self.plotChartManager.createPlotChart()

  #------------------------------------------------------------------------------
  def computeNeedleTipToUsPlaneDistanceMm(self, needleTip, usPlaneCentroid, usPlaneNormal):
    """
    Compute the distance in mm from the needle tip to the ultrasound image plane.

    :param needleTip: needle tip position (numpy array)
    :param usPlaneCentroid: position of the US plane centroid (numpy array)
    :param usPlaneNormal: unitary vector defining US plane normal (numpy array)

    :return float: output distance value in mm
    """
    # Compute distance from point to plane
    distance = self.computeDistancePointToPlane(needleTip, usPlaneCentroid, usPlaneNormal)
    
    return distance

  #------------------------------------------------------------------------------
  def computeNeedleTipToTargetDistanceMm(self, needleTip, targetPoint):
    """
    Compute the distance in mm from the needle tip to a target 3D point.

    :param needleTip: needle tip position (numpy array)
    :param targetPoint: target point position (numpy array)

    :return float: output distance value in mm
    """
    # Compute distance from point to point
    distance = self.computeDistancePointToPoint(needleTip, targetPoint)
    
    return distance

  #------------------------------------------------------------------------------
  def computeNeedleToUsPlaneAngleDeg(self, needleTip, needleHandle, usPlaneCentroid, usPlaneNormal):
    """
    Compute the angle in degrees between the needle and the US plane.

    :param needleTip: needle tip position (numpy array)
    :param needleHandle: needle handle position (numpy array)
    :param usPlaneCentroid: position of the US plane centroid (numpy array)
    :param usPlaneNormal: unitary vector defining US plane normal (numpy array)

    :return float: output angle value in degrees
    """
    # Project needle points into US plane
    needleTip_proj = self.projectPointToPlane(needleTip, usPlaneCentroid, usPlaneNormal)
    needleHandle_proj = self.projectPointToPlane(needleHandle, usPlaneCentroid, usPlaneNormal)

    # Define needle vector
    needleVector = needleTip - needleHandle

    # Define needle projection vector
    needleProjectionVector = needleTip_proj - needleHandle_proj

    # Compute angular deviation
    angle = self.computeAngularDeviation(needleVector, needleProjectionVector)

    return angle

  #------------------------------------------------------------------------------
  def computeNeedleToTargetLineInPlaneAngleDeg(self, needleTip, needleHandle, targetLineStart, targetLineEnd, usPlaneCentroid, usPlaneNormal):
    """
    Compute the angle in degrees between the needle and the target line.

    :param needleTip: needle tip position (numpy array)
    :param needleHandle: needle handle position (numpy array)
    :param targetLineStart: target line start position (numpy array)
    :param targetLineEnd: target line end position (numpy array)
    :param usPlaneCentroid: position of the US plane centroid (numpy array)
    :param usPlaneNormal: unitary vector defining US plane normal (numpy array)

    :return float: output angle value in degrees
    """
    # Project needle points into US plane
    needleTip_proj = self.projectPointToPlane(needleTip, usPlaneCentroid, usPlaneNormal)
    needleHandle_proj = self.projectPointToPlane(needleHandle, usPlaneCentroid, usPlaneNormal)

    # Project target line points into US plane (NOT NEEDED, SINCE LINE IS SUPPOSED TO BE WITHIN PLANE)
    targetLineStart_proj = self.projectPointToPlane(targetLineStart, usPlaneCentroid, usPlaneNormal)
    targetLineEnd_proj = self.projectPointToPlane(targetLineEnd, usPlaneCentroid, usPlaneNormal)

    # Define needle projection vector
    needleProjectionVector = needleTip_proj - needleHandle_proj

    # Define target projection vector
    targetProjectionVector = targetLineEnd_proj - targetLineStart_proj    

    # Compute angular deviation
    angle = self.computeAngularDeviation(needleProjectionVector, targetProjectionVector)

    return angle

  #------------------------------------------------------------------------------
  def updatePlotChart(self):

    # Get selected metric name
    metricName = self.selectedMetric

    # Update visible plot series in plot chart
    self.plotChartManager.updatePlotChart(metricName)

  #------------------------------------------------------------------------------
  def computeDistancePointToPoint(self, fromPoint, toPoint):

    # Compute distance
    distance = np.linalg.norm(np.array(toPoint) - np.array(fromPoint))

    return distance

  #------------------------------------------------------------------------------
  def computeDistancePointToPlane(self, point, planeCentroid, planeNormal):

    # Project point to plane
    projectedPoint = self.projectPointToPlane(point, planeCentroid, planeNormal)
    
    # Compute distance
    distance = np.linalg.norm(np.array(projectedPoint) - np.array(point))

    return distance

  #------------------------------------------------------------------------------
  def projectPointToPlane(self, point, planeCentroid, planeNormal):

    # Project point to plane
    projectedPoint = np.subtract(np.array(point), np.dot(np.subtract(np.array(point), np.array(planeCentroid)), np.array(planeNormal)) * np.array(planeNormal))
    
    return projectedPoint

  # ------------------------------------------------------------------------------
  def computeAngularDeviation(self, vec1, vec2):
    """
    Compute angle between two vectors.

    :param vec1: Vector 1 numpy array
    :param vec2: Vector 2 numpy array

    :return float: Angle between vector 1 and vector 2 in degrees.
    """
    try:
      # Cosine value
      cos_value = np.dot(vec1,vec2)/(np.linalg.norm(vec1)*np.linalg.norm(vec2))
      # Cosine value can only be between [-1, 1].
      if cos_value > 1.0:
        cos_value = 1.0
      elif cos_value < -1.0:
        cos_value = -1.0
      # Compute angle in degrees
      angle = np.rad2deg (np.arccos(cos_value))
    except:
      angle = -1.0
    return angle

  #------------------------------------------------------------------------------
  def getTransformedPoint(self, point, transformNode):

    # Convert to homogenous coordinates
    point_hom = np.hstack((np.array(point), 1.0))

    # Get transform to world
    if transformNode:
      transformToWorld_array = self.getToolToWorldTransform(transformNode)
    else:
      transformToWorld_array = np.eye(4) # identity

    # Get world to ultrasound transform
    #worldToUltrasound_array = self.getWorldToUltrasoundTransform()
    
    # Get transformed point
    point_transformed_hom = np.dot(transformToWorld_array, point_hom)
    #point_transformed_hom = np.dot(worldToUltrasound_array, np.dot(transformToWorld_array, point_hom))

    # Output points
    point_transformed = np.array([point_transformed_hom[0], point_transformed_hom[1], point_transformed_hom[2]])

    return point_transformed

  #------------------------------------------------------------------------------
  def getWorldToUltrasoundTransform(self):

    if not self.ImageToProbe:
      logging.error('ImageToProbe transform does not exist. WorldToUltrasoundTransform cannot be computed.')

    # Get transform from image to world
    ultrasoundToWorldMatrix = vtk.vtkMatrix4x4()
    self.ImageToProbe.GetMatrixTransformToWorld(ultrasoundToWorldMatrix)

    # Get inverse transform
    worldToUltrasoundMatrix = vtk.vtkMatrix4x4()
    worldToUltrasoundMatrix.DeepCopy( ultrasoundToWorldMatrix )
    worldToUltrasoundMatrix.Invert()

    # Get numpy array
    worldToUltrasoundArray = self.convertVtkMatrixToNumpyArray(worldToUltrasoundMatrix)
    return worldToUltrasoundArray

  #------------------------------------------------------------------------------
  def getToolToParentTransform(self, node):
    # Get matrix
    transform_matrix = vtk.vtkMatrix4x4() # vtk matrix
    node.GetMatrixTransformToParent(transform_matrix) # get vtk matrix
    return self.convertVtkMatrixToNumpyArray(transform_matrix)

  #------------------------------------------------------------------------------
  def getToolToWorldTransform(self, node):
    # Get matrix
    transform_matrix = vtk.vtkMatrix4x4() # vtk matrix
    node.GetMatrixTransformToWorld(transform_matrix) # get vtk matrix
    return self.convertVtkMatrixToNumpyArray(transform_matrix)

  #------------------------------------------------------------------------------
  def convertVtkMatrixToNumpyArray(self, vtkMatrix):
    # Build array
    R00 = vtkMatrix.GetElement(0, 0) 
    R01 = vtkMatrix.GetElement(0, 1) 
    R02 = vtkMatrix.GetElement(0, 2)
    Tx = vtkMatrix.GetElement(0, 3)
    R10 = vtkMatrix.GetElement(1, 0)
    R11 = vtkMatrix.GetElement(1, 1)
    R12 = vtkMatrix.GetElement(1, 2)
    Ty = vtkMatrix.GetElement(1, 3)
    R20 = vtkMatrix.GetElement(2, 0)
    R21 = vtkMatrix.GetElement(2, 1)
    R22 = vtkMatrix.GetElement(2, 2)
    Tz = vtkMatrix.GetElement(2, 3)
    H0 = vtkMatrix.GetElement(3, 0)
    H1 = vtkMatrix.GetElement(3, 1)
    H2 = vtkMatrix.GetElement(3, 2)
    H3 = vtkMatrix.GetElement(3, 3)
    return np.array([[R00, R01, R02, Tx],[R10, R11, R12, Ty], [R20, R21, R22, Tz], [H0, H1, H2, H3]])

  #------------------------------------------------------------------------------
  def displayMetricPlot(self):
    if self.plotVisible:
      # TODO store model slice intersection
      #needleSliceIntersectionVisibility = self.needle_model.GetModelDisplayNode().GetSliceIntersectionVisibility()
    
      # Switch to plot only layout
      self.layoutManager.setCustomLayout('2D + 3D + Plot')

      # Show plot chart in plot view
      self.layoutManager.setActivePlotChart(self.plotChartManager.getPlotChart())   

    else:
      # Restore last layout if any
      self.layoutManager.restoreLastLayout()

  #------------------------------------------------------------------------------
  def exitApplication(self, status=slicer.util.EXIT_SUCCESS, message=None):
    """Exit application.
    If ``status`` is ``slicer.util.EXIT_SUCCESS``, ``message`` is logged using ``logging.info(message)``
    otherwise it is logged using ``logging.error(message)``.
    """
    def _exitApplication():
      if message:
        if status == slicer.util.EXIT_SUCCESS:
          logging.info(message)
        else:
          logging.error(message)
      slicer.util.mainWindow().hide()
      slicer.util.exit(slicer.util.EXIT_FAILURE)
    qt.QTimer.singleShot(0, _exitApplication)

  #------------------------------------------------------------------------------
  def setupKeyboardShortcuts(self):
    shortcuts = [
        ('Ctrl+3', lambda: slicer.util.mainWindow().pythonConsole().parent().setVisible(not slicer.util.mainWindow().pythonConsole().parent().visible))
        ]

    for (shortcutKey, callback) in shortcuts:
        shortcut = qt.QShortcut(slicer.util.mainWindow())
        shortcut.setKey(qt.QKeySequence(shortcutKey))
        shortcut.connect('activated()', callback)    

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

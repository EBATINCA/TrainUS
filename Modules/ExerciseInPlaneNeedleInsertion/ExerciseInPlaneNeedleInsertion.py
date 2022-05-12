import vtk, qt, ctk, slicer
import os
import numpy as np
import time

from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

import logging

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

    # Layout
    self.logic.updateSliceControllerVisibility(True)
    self.logic.setupLayouts()

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
    # Layout
    self.logic.updateSliceControllerVisibility(True)
    self.logic.setupLayouts()

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
      self.ui.metricsGroupBox.visible = False
    elif self.logic.exerciseMode == 'Evaluation':
      self.ui.instructionsGroupBox.visible = True
      self.ui.difficultyGroupBox.visible = True
      self.ui.targetGeneratorGroupBox.visible = False
      self.ui.recordingGroupBox.visible = False
      self.ui.importRecordingGroupBox.visible = True
      self.ui.playbackGroupBox.visible = True
      self.ui.metricsGroupBox.visible = True
    elif self.logic.exerciseMode == 'Developer':
      self.ui.instructionsGroupBox.visible = True
      self.ui.difficultyGroupBox.visible = True
      self.ui.targetGeneratorGroupBox.visible = True
      self.ui.recordingGroupBox.visible = True
      self.ui.importRecordingGroupBox.visible = True
      self.ui.playbackGroupBox.visible = True
      self.ui.metricsGroupBox.visible = True
    else:
      logging.error('Invalid selected mode...')

    # Show/Hide instructions
    if self.logic.intructionsVisible:
      self.ui.showInstructionsButton.setText('Hide')
      self.ui.previousInstructionButton.enabled = True
      self.ui.nextInstructionButton.enabled = True
    else:
      self.ui.showInstructionsButton.setText('Show')
      self.ui.previousInstructionButton.enabled = False
      self.ui.nextInstructionButton.enabled = False

    # Start/Stop recording
    if self.logic.recordingInProgress:
      self.ui.startStopRecordingButton.setText('Stop')
      self.ui.clearRecordingButton.enabled = False
      self.ui.saveRecordingButton.enabled = False
    else:
      self.ui.startStopRecordingButton.setText('Start')
      self.ui.clearRecordingButton.enabled = (self.logic.sequenceBrowserNode is not None)
      self.ui.saveRecordingButton.enabled = (self.logic.sequenceBrowserNode is not None)

    # Recording info
    self.ui.recordingLengthLabel.setText('{0:.3g} s'.format(self.logic.recordingLength))
    self.ui.recordingTimerWidget.slider().visible = False
    if (self.logic.sequenceBrowserNode is not None):
      self.ui.recordingTimerWidget.setMRMLSequenceBrowserNode(self.logic.sequenceBrowserNode)

    # Playback
    if (self.logic.sequenceBrowserNode is not None):
      self.ui.SequenceBrowserPlayWidget.enabled = True
      self.ui.SequenceBrowserPlayWidget.setMRMLSequenceBrowserNode(self.logic.sequenceBrowserNode)
      self.ui.SequenceBrowserSeekWidget.enabled = True
      self.ui.SequenceBrowserSeekWidget.setMRMLSequenceBrowserNode(self.logic.sequenceBrowserNode)
    else:
      self.ui.SequenceBrowserPlayWidget.enabled = False
      self.ui.SequenceBrowserSeekWidget.enabled = False

    # Metric computation
    self.ui.computeMetricsButton.enabled = not self.logic.isSequenceBrowserEmpty()
    self.ui.metricSelectionComboBox.enabled = (not self.logic.isSequenceBrowserEmpty()) and self.logic.plotVisible

    # Display plot
    self.ui.displayPlotButton.enabled = not self.logic.isSequenceBrowserEmpty()
    self.ui.displayPlotButton.checked = self.logic.plotVisible

  #------------------------------------------------------------------------------
  def onLoadDataButtonClicked(self):
    # Start exercise
    self.logic.setupScene()

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
    self.logic.intructionsVisible = not self.logic.intructionsVisible

    # Update GUI
    self.updateGUIFromMRML()

    # Update instruction display
    self.logic.updateDisplayExerciseInstructions()

  #------------------------------------------------------------------------------
  def onPreviousInstructionButtonClicked(self):
    self.logic.previousExerciseInstruction()

  #------------------------------------------------------------------------------
  def onNextInstructionButtonClicked(self):
    self.logic.nextExerciseInstruction()

  #------------------------------------------------------------------------------
  def onGenerateTargetButtonClicked(self):    
    # Get number of targets
    numTargets = self.logic.getNumberOfTargets()

    # Generate random target ID
    targetID = np.random.randint(0, numTargets) + 1

    # Get target file location
    targetFileName = 'Target_' + str(targetID) + '.mrk.json'
    targetDataFolder = self.logic.dataFolderPath + '/Targets/'

    # Load selected target
    self.logic.loadTarget(targetFileName, targetDataFolder)

  #------------------------------------------------------------------------------
  def onStartStopRecordingButtonClicked(self):    
    # Update recording status
    self.logic.updateSequenceBrowserRecording()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onClearRecordingButtonClicked(self):    
    # Delete previous recording
    self.logic.clearSequenceBrowserRecording()

    # Create new recording
    self.logic.createSequenceBrowserRecording()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onSaveRecordingButtonClicked(self):
    # Generate recording file path
    filename = 'Recording-' + time.strftime("%Y%m%d-%H%M%S") + os.extsep + "sqbr"
    directory = self.logic.dataFolderPath
    filePath = os.path.join(directory, filename)

    # Save sequence browser node
    self.logic.saveSequenceBrowserRecording(filePath)

    # Recording info to save in JSON file
    print('>>>>>>>>>>>>>>>>RECORDING SAVED<<<<<<<<<<<<<<<<')
    print('Date:', time.strftime("%Y%m%d"))
    print('Time:', time.strftime("%H%M%S"))
    print('Recording length:', self.logic.recordingLength)
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
    filePath = fileDialog.getOpenFileName()
    if not filePath:
      return

    # Delete previous recording
    self.logic.clearSequenceBrowserRecording()

    # Load sequence browser node
    self.logic.loadSequenceBrowserRecording(filePath)

    # Reset focal point in 3D view
    self.logic.resetFocalPointInThreeDView()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onLeftViewButtonClicked(self):
    # Update viewpoint
    self.logic.updateViewpoint(cameraID = 'Left')

  #------------------------------------------------------------------------------
  def onFrontViewButtonClicked(self):
    # Update viewpoint
    self.logic.updateViewpoint(cameraID = 'Front')

  #------------------------------------------------------------------------------
  def onRightViewButtonClicked(self):
    # Update viewpoint
    self.logic.updateViewpoint(cameraID = 'Right')

  #------------------------------------------------------------------------------
  def onBottomViewButtonClicked(self):
    # Update viewpoint
    self.logic.updateViewpoint(cameraID = 'Bottom')

  #------------------------------------------------------------------------------
  def onFreeViewButtonClicked(self):
    # Update viewpoint
    self.logic.updateViewpoint(cameraID = 'Free')

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
    numMetrics = len(self.logic.metric_names) - 2
    for metricID in range(numMetrics):
      self.ui.metricSelectionComboBox.addItem(self.logic.metric_names[metricID+2])

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

    # Register layouts
    self.customLayout_Dual2D3D_ID = 997
    self.customLayout_2Donly_ID = 998
    self.customLayout_Dual3D3D_ID = 999
    self.customLayout_FourUp3D_ID = 1000
    self.customLayout_Dual2D3D_withPlot_ID = 1001

    # Exercise settings
    self.exerciseDifficulty = 'Medium'  
    self.exerciseLayout = '3D only'
    self.exerciseMode = 'Evaluation'

    # Instructions
    self.intructionsVisible = False
    self.lastLayout = None 
    self.lastBackgroundVolumeID = None

    # Data path
    self.dataFolderPath = self.moduleWidget.resourcePath('ExerciseInPlaneNeedleInsertionData/')

    # Viewpoint module (SlicerIGT extension)
    try:
      import Viewpoint # Viewpoint Module must have been added to Slicer 
      self.viewpointLogic = Viewpoint.ViewpointLogic()
    except:
      logging.error('ERROR: "Viewpoint" module was not found.')

    # Volume reslice driver (SlicerIGT extension)
    try:
      self.volumeResliceDriverLogic = slicer.modules.volumereslicedriver.logic()
    except:
      logging.error('ERROR: "Volume Reslice Driver" module was not found.')

    # Red slice
    self.redSliceLogic = slicer.app.layoutManager().sliceWidget("Red").sliceLogic()

    # 3D view
    self.threeDViewNode = slicer.app.layoutManager().threeDWidget(0).mrmlViewNode()
    self.threeDView = slicer.app.layoutManager().threeDWidget(0).threeDView()

    # Target nodes
    self.targetFileName = ''
    self.targetLineNode = None
    self.targetPointNode = None

    # Sequences (Sequences extension)
    try:
      self.sequencesLogic = slicer.modules.sequences.logic()
    except:
      logging.error('ERROR: "Sequences" module was not found.')

    # Recording
    self.recordingInProgress = False
    self.sequenceBrowserNode = None
    self.recordingLength = 0.0
    self.observerID = None

    # Playback
    self.playbackInProgress = False

    # Tool reference points
    self.NEEDLE_TIP = [0.0, 0.0, 0.0]
    self.NEEDLE_HANDLE = [0.0, 0.0, -50.0]
    self.USPROBE_TIP = [0.0, 0.0, 0.0]
    self.USPROBE_HANDLE = [0.0, 50.0, 0.0]
    self.USPLANE_ORIGIN = [0.0, 0.0, 0.0]
    self.USPLANE_NORMAL = [0.0, 0.0, 1.0]

    # Metrics
    self.metricTableNode = None
    self.cursorTableNode = None
    self.metricValuesPlotSeriesNodes = []
    self.cursorValuesPlotSeriesNodes = []
    self.plotChartNode = None
    self.plotVisible = False

    # Metric data
    self.sampleID = []
    self.timestamp = []
    self.needleTipToUsPlaneDistanceMm = []
    self.needleTipToTargetDistanceMm = []
    self.needleToUsPlaneAngleDeg = []
    self.needleToTargetLineInPlaneAngleDeg = []
    self.metric_names = ['SampleID', 'TimeStamp', 'NeedleTipToUsPlaneDistanceMm', 'NeedleTipToTargetDistanceMm', 'NeedleToUsPlaneAngleDeg', 'NeedleToTargetLineInPlaneAngleDeg']
    self.metric_array = []

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
      self.exerciseLayout = '2D only'
      self.highlightModelsInImage = False
    else:
      self.exerciseLayout = '3D only'
      self.highlightModelsInImage = False
      logging.warning('Invalid difficulty level was selected.')

    # Update layout
    self.setCustomLayout(self.exerciseLayout)

    # Update model slice visibility
    try:
      self.needle_model.GetModelDisplayNode().SetSliceIntersectionVisibility(self.highlightModelsInImage)
    except:
      pass

  #------------------------------------------------------------------------------
  def updateDisplayExerciseInstructions(self):

    if self.intructionsVisible:
      # Store last layout
      layoutManager= slicer.app.layoutManager()
      self.lastLayout = layoutManager.layout

      # Store last background volume in red slice view
      self.lastBackgroundVolumeID = self.redSliceLogic.GetSliceCompositeNode().GetBackgroundVolumeID()

      # Deactivate volume reslice driver
      self.volumeResliceDriverLogic.SetModeForSlice(self.volumeResliceDriverLogic.MODE_NONE, self.redSliceLogic.GetSliceNode())

      # Avoid visibility of needle model in 2D view
      self.needle_model.GetModelDisplayNode().SetSliceIntersectionVisibility(False)

      # Switch to 2D only layout
      self.setCustomLayout('2D only')

      # Display instructions
      self.redSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(self.instructions.GetID())
      self.redSliceLogic.GetSliceNode().SetOrientationToAxial()
      self.redSliceLogic.FitSliceToAll()
      self.redSliceLogic.SetSliceOffset(0)

    else:
      # Restore last layout if any
      if self.lastLayout:
        layoutManager= slicer.app.layoutManager()
        layoutManager.setLayout(self.lastLayout)

      # Activate volume reslice driver
      self.volumeResliceDriverLogic.SetModeForSlice(self.volumeResliceDriverLogic.MODE_TRANSVERSE, self.redSliceLogic.GetSliceNode())

      # Restore visibility of needle model in 2D view
      self.updateDifficulty()

      # Restore last volume
      if self.lastBackgroundVolumeID:
        self.redSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(self.lastBackgroundVolumeID)
        self.redSliceLogic.FitSliceToAll()

  #------------------------------------------------------------------------------
  def previousExerciseInstruction(self):
    # Modify slice offset
    if self.intructionsVisible:
      sliceOffset = self.redSliceLogic.GetSliceOffset()
      sliceIndex = self.redSliceLogic.GetSliceIndexFromOffset(sliceOffset - 1)
      if sliceIndex > 0:
        self.redSliceLogic.SetSliceOffset(sliceOffset - 1)

  #------------------------------------------------------------------------------
  def nextExerciseInstruction(self):
    # Modify slice offset
    if self.intructionsVisible:
      sliceOffset = self.redSliceLogic.GetSliceOffset()
      sliceIndex = self.redSliceLogic.GetSliceIndexFromOffset(sliceOffset + 1)
      if sliceIndex > 0:
        self.redSliceLogic.SetSliceOffset(sliceOffset + 1)

  #------------------------------------------------------------------------------
  def getNumberOfTargets(self):
    # Get targets in folder
    targetDataFolder = self.dataFolderPath + '/Targets/'
    targetFileList = os.listdir(targetDataFolder)
    numTargets = len(targetFileList)
    return numTargets
    
  #------------------------------------------------------------------------------
  def loadTarget(self, targetFileName, targetDataFolder):

    # Remove previous target from scene
    if self.targetLineNode:
      slicer.mrmlScene.RemoveNode(self.targetLineNode)
      self.targetLineNode = None
    if self.targetPointNode:
      slicer.mrmlScene.RemoveNode(self.targetPointNode)
      self.targetPointNode = None    

    # Load selected target    
    targetFilePath = targetDataFolder + targetFileName
    logging.debug('Loading target from file: %s' % targetFilePath)
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

    # Display US image using volume reslice driver module
    self.redSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(self.usImageVolumeNode.GetID())
    self.volumeResliceDriverLogic.SetDriverForSlice(self.usImageVolumeNode.GetID(), self.redSliceLogic.GetSliceNode())
    self.volumeResliceDriverLogic.SetModeForSlice(self.volumeResliceDriverLogic.MODE_TRANSVERSE, self.redSliceLogic.GetSliceNode())

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

    # Fit US image to view and display in 3D view     
    self.redSliceLogic.FitSliceToAll()
    self.redSliceLogic.GetSliceNode().SetSliceVisible(1)

    # Remove 3D cube and 3D axis label from 3D view
    self.threeDViewNode.SetBoxVisible(False)
    self.threeDViewNode.SetAxisLabelsVisible(False)

    # Reset focal point in 3D view
    self.resetFocalPointInThreeDView()

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
  def updateSequenceBrowserRecording(self):

    if self.recordingInProgress:
      # Stop recording
      success = self.stopSequenceBrowserRecording()

      # Update recording flag
      if success:
        self.recordingInProgress = False 
      else:
        self.recordingInProgress = True

    else:
      # Start recording
      success = self.startSequenceBrowserRecording()

      # Update recording flag
      if success:
        self.recordingInProgress = True 
      else:
        self.recordingInProgress = False

  #------------------------------------------------------------------------------
  def startSequenceBrowserRecording(self):
    """
    Start recording data using sequence browser node.
    """
    # Create sequence browser if needed
    if self.sequenceBrowserNode == None:
      success = self.createSequenceBrowserRecording()
      if not success:
        return False

    # Start recording
    try:
      self.sequenceBrowserNode.SetRecordMasterOnly(False)
      self.sequenceBrowserNode.SetRecording(None, True)
      self.sequenceBrowserNode.SetRecordingActive(True)
      return True
    except:
      logging.error('Error starting sequence browser recording...')
      return False

  #------------------------------------------------------------------------------
  def stopSequenceBrowserRecording(self):
    """
    Stop recording data using sequence browser node.
    """
    # Stop recording
    try:
      self.sequenceBrowserNode.SetRecordingActive(False)
      self.sequenceBrowserNode.SetRecording(None, False)
      self.setPlaybackRealtime()
      return True
    except:
      logging.error('Error stopping sequence browser recording...')
      return False

  #------------------------------------------------------------------------------
  def createSequenceBrowserRecording(self):
    """
    Create new sequence browser node to manage data recording.
    """
    try:
      # Create a sequence browser node
      browserName = 'TrainUS_Recording'
      self.sequenceBrowserNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSequenceBrowserNode', slicer.mrmlScene.GenerateUniqueName(browserName))
  
      modifiedFlag = self.sequenceBrowserNode.StartModify()

      # Add synchronized nodes
      self.sequencesLogic.AddSynchronizedNode(None, self.NeedleToTracker, self.sequenceBrowserNode)
      self.sequencesLogic.AddSynchronizedNode(None, self.ProbeToTracker, self.sequenceBrowserNode)
      self.sequencesLogic.AddSynchronizedNode(None, self.usImageVolumeNode, self.sequenceBrowserNode)

      # Stop overwritting and saving changes to all nodes
      self.sequenceBrowserNode.SetRecording(None, True)
      self.sequenceBrowserNode.SetOverwriteProxyName(None, False)
      self.sequenceBrowserNode.SetSaveChanges(None, False)

      self.sequenceBrowserNode.EndModify(modifiedFlag)

      # Add observer
      try:
        self.observerID = self.NeedleToTracker.AddObserver(slicer.vtkMRMLTransformableNode.TransformModifiedEvent, self.callbackCursorPosition)
      except:
        logging.error('Error adding an observer to the NeedleToTracker transform...')

      return True

    except:
      logging.error('Error creating a new sequence browser node...')
      return False

  #------------------------------------------------------------------------------
  def callbackCursorPosition(self, unused1=None, unused2=None):
    """
    Update cursor position in plot chart.
    """
    self.updateCursorPosition(self.sequenceBrowserNode.GetSelectedItemNumber())    

  #------------------------------------------------------------------------------
  def clearSequenceBrowserRecording(self):
    """
    Clear recording data.
    """
    try:
      # Remove observer
      if self.observerID:
        self.sequenceBrowserNode.GetMasterSequenceNode().RemoveObserver(self.observerID)

      # Delete plot series nodes
      if self.metricValuesPlotSeriesNodes:
        for plotSeriesNode in self.metricValuesPlotSeriesNodes:
          slicer.mrmlScene.RemoveNode(plotSeriesNode)
        self.metricValuesPlotSeriesNodes = []
      if self.cursorValuesPlotSeriesNodes:
        for plotSeriesNode in self.cursorValuesPlotSeriesNodes:
          slicer.mrmlScene.RemoveNode(plotSeriesNode)
        self.cursorValuesPlotSeriesNodes = []

      # Delete plot chart node
      if self.plotChartNode:
        slicer.mrmlScene.RemoveNode(self.plotChartNode)
        self.plotChartNode = None

      # Remove sequence nodes from scene
      synchronizedSequenceNodes = vtk.vtkCollection()
      self.sequenceBrowserNode.GetSynchronizedSequenceNodes(synchronizedSequenceNodes)
      synchronizedSequenceNodes.AddItem(self.sequenceBrowserNode.GetMasterSequenceNode())
      for sequenceNode in synchronizedSequenceNodes:
        slicer.mrmlScene.RemoveNode(sequenceNode)

      # Remove sequence browser node from scene
      slicer.mrmlScene.RemoveNode(self.sequenceBrowserNode)
      self.sequenceBrowserNode = None 
      self.recordingLength = 0.0

      return True
    except:
      logging.error('Error deleting sequence browser node...')
      return False

  #------------------------------------------------------------------------------
  def saveSequenceBrowserRecording(self, filePath):
    """
    Save recording data to file.
    """
    # Save sequence browser node to file
    try:
      print('Saving sequence browser node at: ' + filePath)
      slicer.util.saveNode(self.sequenceBrowserNode, filePath)
    except:
      logging.error('Error saving sequence browser node to file...')

  #------------------------------------------------------------------------------
  def loadSequenceBrowserRecording(self, filePath):
    """
    Load recording data from file.
    """
    # Save sequence browser node to file
    try:
      print('Loading sequence browser node from file: ' + filePath)
      self.sequenceBrowserNode = slicer.util.loadNodeFromFile(filePath, 'Tracked Sequence Browser')

      # Add observer
      try:
          self.observerID = self.NeedleToTracker.AddObserver(slicer.vtkMRMLTransformableNode.TransformModifiedEvent, self.callbackCursorPosition)
      except:
        logging.error('Error adding an observer to the NeedleToTracker transform...')
    except:
      logging.error('Error loading sequence browser node from file...')

  #------------------------------------------------------------------------------
  def isSequenceBrowserEmpty(self):
    """
    Check if recording is empty or not.
    """
    # Get number of items
    try:
      numItems = self.sequenceBrowserNode.GetNumberOfItems()
    except:
      return True

    # Define sequence browser state
    if numItems == 0:
      isEmpty = True
    else:
      isEmpty = False
    return isEmpty

  #------------------------------------------------------------------------------
  def setPlaybackRealtime(self):
    try: #- update the playback fps rate
      sequenceNode = self.sequenceBrowserNode.GetMasterSequenceNode()
      numDataNodes = sequenceNode.GetNumberOfDataNodes()
      startTime = float(sequenceNode.GetNthIndexValue(0))
      stopTime = float(sequenceNode.GetNthIndexValue(numDataNodes-1))
      self.recordingLength = stopTime - startTime
      frameRate = numDataNodes / self.recordingLength
      self.sequenceBrowserNode.SetPlaybackRateFps(frameRate)
    except:
      logging.error('Could not set playback realtime fps rate')

  #------------------------------------------------------------------------------
  def updateViewpoint(self, cameraID):
    """
    Update virtual camera mode for 3D view.
    """
    # Select camera transform
    if cameraID == 'Left':
        cameraTransform = self.LeftCameraToProbeModel
    elif cameraID == 'Front':
        cameraTransform = self.FrontCameraToProbeModel
    elif cameraID == 'Right':
        cameraTransform = self.RightCameraToProbeModel
    elif cameraID == 'Bottom':
        cameraTransform = self.BottomCameraToProbeModel
    else:
        cameraTransform = None

    # Disable bulleye mode if active
    bullseyeMode = self.viewpointLogic.getViewpointForViewNode(self.threeDViewNode).getCurrentMode()
    if bullseyeMode:
      self.viewpointLogic.getViewpointForViewNode(self.threeDViewNode).bullseyeStop()
    
    # Update viewpoint
    if cameraTransform:
      self.viewpointLogic.getViewpointForViewNode(self.threeDViewNode).setViewNode(self.threeDViewNode)
      self.viewpointLogic.getViewpointForViewNode(self.threeDViewNode).bullseyeSetTransformNode(cameraTransform)
      self.viewpointLogic.getViewpointForViewNode(self.threeDViewNode).bullseyeStart()

  #------------------------------------------------------------------------------
  def resetFocalPointInThreeDView(self):
    self.threeDView.resetFocalPoint()

  #------------------------------------------------------------------------------
  def computeMetricsFromRecording(self, progressDialog = None):

    # Get number of items
    numItems = self.sequenceBrowserNode.GetNumberOfItems()

    # Metrics
    self.sampleID = []
    self.timestamp = []
    self.needleTipToUsPlaneDistanceMm = []
    self.needleTipToTargetDistanceMm = []
    self.needleToUsPlaneAngleDeg = []
    self.needleToTargetLineInPlaneAngleDeg = []

    # Get target point position
    targetPoint = [0,0,0]
    try:
      self.targetPointNode.GetNthControlPointPositionWorld(0, targetPoint)
      targetPoint = self.getTransformedPoint(targetPoint, None)
    except:
      logging.warning('No target point is defined...')

    # Get target line position
    targetLineStart = [0,0,0]
    targetLineEnd = [0,0,0]
    try:
      self.targetLineNode.GetNthControlPointPositionWorld(0, targetLineEnd)
      self.targetLineNode.GetNthControlPointPositionWorld(1, targetLineStart)
      targetLineStart = self.getTransformedPoint(targetLineStart, None)
      targetLineEnd = self.getTransformedPoint(targetLineEnd, None)
    except:
      logging.warning('No target line is defined...')

    # Iterate along items
    self.sequenceBrowserNode.SelectFirstItem() # reset
    for currentItem in range(numItems):

      # Update progress dialog if any
      if progressDialog:
        progress = (currentItem / numItems) * (progressDialog.maximum - progressDialog.minimum)
        progressDialog.setValue(progress)

      # Get timestamp
      timestamp = self.sequenceBrowserNode.GetMasterSequenceNode().GetNthIndexValue(currentItem)

      # Get needle position
      needleTip = self.getTransformedPoint(self.NEEDLE_TIP, self.NeedleTipToNeedle)
      needleHandle = self.getTransformedPoint(self.NEEDLE_HANDLE, self.NeedleTipToNeedle)

      # Get US probe position
      usProbeTip = self.getTransformedPoint(self.USPROBE_TIP, self.ProbeModelToProbe)
      usProbeHandle = self.getTransformedPoint(self.USPROBE_HANDLE, self.ProbeModelToProbe)

      # Get US image plane orientation
      usPlanePointA = np.array(self.USPLANE_ORIGIN)
      usPlanePointB = np.array(self.USPLANE_NORMAL)
      usPlaneCentroid = usPlanePointA
      usPlaneNormal = (usPlanePointB - usPlanePointA) / np.linalg.norm(usPlanePointB - usPlanePointA)

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
      self.sequenceBrowserNode.SelectNextItem()

    # Fill metric array
    self.metric_array = [self.sampleID, self.timestamp, self.needleTipToUsPlaneDistanceMm, self.needleTipToTargetDistanceMm, self.needleToUsPlaneAngleDeg, self.needleToTargetLineInPlaneAngleDeg]   

    # Create table
    self.createMetricTable()

    # Create table
    self.createCursorTable()

    # Create plot chart
    self.createPlotChart()

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
  def createMetricTable(self):

    # Get number of metrics
    numMetrics = len(self.metric_names)

    # Get number of items in recording
    numItems = self.sequenceBrowserNode.GetNumberOfItems()

    # Delete existing table node if any
    if self.metricTableNode:
      slicer.mrmlScene.RemoveNode(self.metricTableNode)
      self.metricTableNode = None      

    # Create table node
    self.metricTableNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTableNode')
    self.metricTableNode.SetName('Metrics')

    # Add one column for each metric
    self.metricTableNode.SetLocked(True) # lock table to avoid modifications
    self.metricTableNode.RemoveAllColumns() # reset
    table = self.metricTableNode.GetTable()
    for metricID in range(numMetrics):
      array = vtk.vtkFloatArray()
      array.SetName(self.metric_names[metricID])
      table.AddColumn(array)

    # Fill table
    table.SetNumberOfRows(numItems)
    for itemID in range(numItems):
      for metricID in range(numMetrics):
        table.SetValue(itemID, metricID, self.metric_array[metricID][itemID])
    table.Modified()

  #------------------------------------------------------------------------------
  def createCursorTable(self):

    # Get number of metrics
    numMetrics = len(self.metric_names)

    # Get number of items in recording
    numItems = self.sequenceBrowserNode.GetNumberOfItems()

    # Delete existing table node if any
    if self.cursorTableNode:
      slicer.mrmlScene.RemoveNode(self.cursorTableNode)
      self.cursorTableNode = None      

    # Create table node
    self.cursorTableNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTableNode')
    self.cursorTableNode.SetName('Cursor')

    # Add one column for each metric
    self.cursorTableNode.SetLocked(True) # lock table to avoid modifications
    self.cursorTableNode.RemoveAllColumns() # reset
    table = self.cursorTableNode.GetTable()
    for metricID in range(numMetrics):
      array = vtk.vtkFloatArray()
      array.SetName(self.metric_names[metricID])
      table.AddColumn(array)

    # Fill table
    table.SetNumberOfRows(1)
    for metricID in range(numMetrics):
      table.SetValue(0, metricID, max(self.metric_array[metricID][:]))
    table.Modified()

    # Set cursor to initial position
    self.updateCursorPosition(0)

  #------------------------------------------------------------------------------
  def updateCursorPosition(self, itemID):
    if self.cursorTableNode:
      # Modify cursor table to force plot chart update
      table = self.cursorTableNode.GetTable()
      table.SetValue(0, 0, float(itemID))
      table.Modified()

  #------------------------------------------------------------------------------
  def createPlotChart(self):

    # Get number of metrics
    numMetrics = len(self.metric_names)

    # Delete previous plot series
    if self.metricValuesPlotSeriesNodes:
      for plotSeriesNode in self.metricValuesPlotSeriesNodes:
        slicer.mrmlScene.RemoveNode(plotSeriesNode)
      self.metricValuesPlotSeriesNodes = []

    # Create plot series
    self.metricValuesPlotSeriesNodes = []
    for metricID in range(numMetrics-2):
      plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLPlotSeriesNode')
      plotSeriesNode.SetName(self.metric_names[metricID+2])
      plotSeriesNode.SetAndObserveTableNodeID(self.metricTableNode.GetID())
      plotSeriesNode.SetXColumnName(self.metric_names[0])
      plotSeriesNode.SetYColumnName(self.metric_names[metricID+2])
      plotSeriesNode.SetPlotType(slicer.vtkMRMLPlotSeriesNode.PlotTypeScatter)
      plotSeriesNode.SetMarkerStyle(slicer.vtkMRMLPlotSeriesNode.MarkerStyleNone)
      plotSeriesNode.SetMarkerSize(15)
      plotSeriesNode.SetLineWidth(4)
      plotSeriesNode.SetColor([1,0,0]) # Red
      self.metricValuesPlotSeriesNodes.append(plotSeriesNode)

    # Delete previous cursor plot series
    if self.cursorValuesPlotSeriesNodes:
      for plotSeriesNode in self.cursorValuesPlotSeriesNodes:
        slicer.mrmlScene.RemoveNode(plotSeriesNode)
      self.cursorValuesPlotSeriesNodes = []

    # Create cursor plot series
    self.cursorValuesPlotSeriesNodes = []
    for metricID in range(numMetrics-2):
      plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLPlotSeriesNode')
      plotSeriesNode.SetName(self.metric_names[metricID+2] + '_Cursor')
      plotSeriesNode.SetAndObserveTableNodeID(self.cursorTableNode.GetID())
      plotSeriesNode.SetXColumnName(self.metric_names[0])
      plotSeriesNode.SetYColumnName(self.metric_names[metricID+2])
      plotSeriesNode.SetPlotType(slicer.vtkMRMLPlotSeriesNode.PlotTypeScatterBar)
      plotSeriesNode.SetMarkerStyle(slicer.vtkMRMLPlotSeriesNode.MarkerStyleCircle)
      plotSeriesNode.SetMarkerSize(15)
      plotSeriesNode.SetLineWidth(4)
      plotSeriesNode.SetColor([0,0,0]) # Black
      self.cursorValuesPlotSeriesNodes.append(plotSeriesNode)

    # Delete previous plot chart
    if self.plotChartNode:
      slicer.mrmlScene.RemoveNode(self.plotChartNode)
      self.plotChartNode = None

    # Create plot chart
    self.plotChartNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLPlotChartNode')
    self.plotChartNode.SetName('Chart')
    self.plotChartNode.RemoveAllPlotSeriesNodeIDs() # reset
    self.plotChartNode.AddAndObservePlotSeriesNodeID(self.metricValuesPlotSeriesNodes[0].GetID())
    self.plotChartNode.AddAndObservePlotSeriesNodeID(self.cursorValuesPlotSeriesNodes[0].GetID())
    self.plotChartNode.SetTitle('Metric Plot')
    self.plotChartNode.SetXAxisTitle('Sample ID')
    #self.plotChartNode.SetYAxisTitle('ANGLE (\xB0)')
    self.plotChartNode.SetAxisLabelFontSize(20)
    self.plotChartNode.LegendVisibilityOff() # hide legend
    self.plotChartNode.GridVisibilityOff()

    print('Plot chart has been created!')


  #------------------------------------------------------------------------------
  def updatePlotChart(self):

    # Get selected metric name
    metricName = self.selectedMetric

    # Get metric ID from name
    selectedMetricID = -1
    numMetrics = len(self.metric_names)
    for metricID in range(numMetrics-2):
      if metricName == self.metric_names[metricID+2]:
        selectedMetricID = metricID

    # Update visible plot series in plot chart
    if self.plotChartNode:
      self.plotChartNode.RemoveAllPlotSeriesNodeIDs() # reset
      self.plotChartNode.AddAndObservePlotSeriesNodeID(self.metricValuesPlotSeriesNodes[selectedMetricID].GetID())
      self.plotChartNode.AddAndObservePlotSeriesNodeID(self.cursorValuesPlotSeriesNodes[selectedMetricID].GetID())
      self.plotChartNode.SetTitle(metricName)

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
    worldToUltrasound_array = self.getWorldToUltrasoundTransform()
    
    # Get transformed point
    point_transformed = np.dot(worldToUltrasound_array, np.dot(transformToWorld_array, point_hom))

    # Output points
    point = np.array([point_transformed[0], point_transformed[1], point_transformed[2]])

    return point

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
      # Store last layout
      layoutManager= slicer.app.layoutManager()
      self.lastLayout = layoutManager.layout

      # Switch to plot only layout
      self.setCustomLayout('2D + 3D + Plot')

      # Show plot chart in plot view
      slicer.app.applicationLogic().GetSelectionNode().SetReferenceActivePlotChartID(self.plotChartNode.GetID())
      slicer.app.applicationLogic().PropagatePlotChartSelection()    

    else:
      # Restore last layout if any
      if self.lastLayout:
        layoutManager= slicer.app.layoutManager()
        layoutManager.setLayout(self.lastLayout)

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
  def setupLayouts(self):
    self.registerCustomLayouts()
    #self.setCustomLayout('3D only') # default

  #------------------------------------------------------------------------------
  def showViewerPinButton(self, sliceWidget, show):
    try:
      sliceControlWidget = sliceWidget.children()[1]
      pinButton = sliceControlWidget.children()[1].children()[1]
      if show:
        pinButton.show()
      else:
        pinButton.hide()
    except: # pylint: disable=w0702
      pass

  #------------------------------------------------------------------------------
  def updateSliceControllerVisibility(self, visible):
    # Update visibility of slice controllers
    for name in slicer.app.layoutManager().sliceViewNames():
      sliceWidget = slicer.app.layoutManager().sliceWidget(name)
      sliceWidget.sliceController().setVisible(visible)

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
  def registerCustomLayouts(self):
      layoutManager= slicer.app.layoutManager()
      layoutLogic = layoutManager.layoutLogic()
      customLayout_Dual2D3D = ("<layout type=\"horizontal\" split=\"true\">"
      " <item splitSize=\"400\" >\n"
      "  <view class=\"vtkMRMLSliceNode\" singletontag=\"Red\">"
      "     <property name=\"orientation\" action=\"default\">Axial</property>"
      "     <property name=\"viewlabel\" action=\"default\">R</property>"
      "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
      "  </view>"
      " </item>"
      " <item splitSize=\"600\" >\n"
      "  <view class=\"vtkMRMLViewNode\" singletontag=\"1\">"
      "  <property name=\"viewlabel\" action=\"default\">T</property>"
      "  </view>"
      " </item>"
      "</layout>")
      customLayout_2Donly = ("<layout type=\"horizontal\">"
      " <item>"
      "  <view class=\"vtkMRMLSliceNode\" singletontag=\"Red\">"
      "   <property name=\"orientation\" action=\"default\">Axial</property>"
      "     <property name=\"viewlabel\" action=\"default\">R</property>"
      "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
      "  </view>"
      " </item>"
      "</layout>")
      customLayout_Dual3D3D = ("<layout type=\"horizontal\" split=\"false\">"
      " <item>"
      "  <view class=\"vtkMRMLViewNode\" singletontag=\"1\">"
      "  <property name=\"viewlabel\" action=\"default\">1</property>"
      "  </view>"
      " </item>"
      " <item>"
      "  <view class=\"vtkMRMLViewNode\" singletontag=\"2\">"
      "  <property name=\"viewlabel\" action=\"default\">2</property>"
      "  </view>"
      " </item>"
      "</layout>")
      customLayout_FourUp3D = ("<layout type=\"vertical\">"
      " <item>"
      "  <layout type=\"horizontal\">"
      "   <item>"
      "    <view class=\"vtkMRMLViewNode\" singletontag=\"1\">"
      "     <property name=\"viewlabel\" action=\"default\">1</property>"
      "    </view>"
      "   </item>"
      "   <item>"
      "    <view class=\"vtkMRMLViewNode\" singletontag=\"2\">"
      "     <property name=\"viewlabel\" action=\"default\">2</property>"
      "    </view>"
      "   </item>"
      "  </layout>"
      " </item>"
      " <item>"
      "  <layout type=\"horizontal\">"
      "   <item>"
      "    <view class=\"vtkMRMLViewNode\" singletontag=\"3\">"
      "     <property name=\"viewlabel\" action=\"default\">3</property>"
      "    </view>"
      "   </item>"
      "   <item>"
      "    <view class=\"vtkMRMLViewNode\" singletontag=\"4\">"
      "     <property name=\"viewlabel\" action=\"default\">4</property>"
      "    </view>"
      "   </item>"
      "  </layout>"
      " </item>"
      "</layout>")
      customLayout_Dual2D3DwithPlot = ("<layout type=\"vertical\" split=\"true\" >\n"
      " <item splitSize=\"700\" >\n"
      "  <layout type=\"horizontal\" split=\"true\">"
      "   <item>"
      "    <view class=\"vtkMRMLSliceNode\" singletontag=\"Red\">"
      "       <property name=\"orientation\" action=\"default\">Axial</property>"
      "       <property name=\"viewlabel\" action=\"default\">R</property>"
      "       <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
      "    </view>"
      "   </item>"
      "   <item>"
      "    <view class=\"vtkMRMLViewNode\" singletontag=\"1\">"
      "    <property name=\"viewlabel\" action=\"default\">T</property>"
      "    </view>"
      "   </item>"
      "  </layout>"
      " </item>"
      " <item splitSize=\"300\" >\n"
      "  <view class=\"vtkMRMLPlotViewNode\" singletontag=\"PlotView1\">"
      "  <property name=\"viewlabel\" action=\"default\">1</property>"
      "  </view>"
      " </item>"
      "</layout>")
      
      layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_Dual2D3D_ID, customLayout_Dual2D3D)
      layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_2Donly_ID, customLayout_2Donly)
      layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_Dual3D3D_ID, customLayout_Dual3D3D)
      layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_FourUp3D_ID, customLayout_FourUp3D)
      layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_Dual2D3D_withPlot_ID, customLayout_Dual2D3DwithPlot)

  #------------------------------------------------------------------------------
  def setCustomLayout(self, layoutName):

    # Determine layout id from name
    if layoutName == '3D only':
      layoutID = slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView
    elif layoutName == '2D only':
      layoutID = self.customLayout_2Donly_ID
    elif layoutName == '2D + 3D':
      layoutID = self.customLayout_Dual2D3D_ID
    elif layoutName == 'Dual 3D':
      layoutID = self.customLayout_Dual3D3D_ID
    elif layoutName == '2D + 3D + Plot':
      layoutID = self.customLayout_Dual2D3D_withPlot_ID
    elif layoutName == 'Four Up 3D':
      layoutID = self.customLayout_FourUp3D_ID
    elif layoutName == 'Plot only':
      layoutID = slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpPlotView
    else:
      layoutID = 1

    # Set layout
    layoutManager= slicer.app.layoutManager()
    layoutManager.setLayout(layoutID)
    

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

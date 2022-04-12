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
#                                       ExerciseInPlaneNeedleInsertionLogic                                          #
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

    # CreateModels module (SlicerIGT extension)
    try:
      self.createModelsLogic = slicer.modules.createmodels.logic()
    except:
      logging.error('ERROR: "CreateModels" module is not available...')

    # Setup keyboard shortcuts
    self.setupKeyboardShortcuts()

    # Register layouts
    self.customLayout_Dual2D3D_ID = 997
    self.customLayout_2Donly_ID = 998
    self.customLayout_Dual3D3D_ID = 999
    self.customLayout_FourUp3D_ID = 1000

    # Tool transform names
    self.toolNames = ['Probe', 'Stylus', 'Patient']    
    self.toolTransformNames = ['ProbeToTracker', 'StylusToTracker', 'ReferenceToTracker']

    # Exercise settings
    self.exerciseDifficulty = 'Medium'  
    self.exerciseLayout = '3D only'
    self.exerciseMode = 'Developer'

    # Instructions
    self.intructionsVisible = False
    self.lastLayout = None 
    self.lastBackgroundVolumeID = None

    # Data path
    self.dataFolderPath = self.moduleWidget.resourcePath('ExerciseInPlaneNeedleInsertionData/')

    # Volume reslice driver (SlicerIGT extension)
    try:
      self.volumeResliceDriverLogic = slicer.modules.volumereslicedriver.logic()
    except:
      logging.error('ERROR: "Volume Reslice Driver" module was not found.')

    # CreateModels module (SlicerIGT extension)
    try:
      self.createModelsLogic = slicer.modules.createmodels.logic()
    except:
      logging.error('ERROR: "Create Models" module was not found.')

    # Red slice
    self.redSliceLogic = slicer.app.layoutManager().sliceWidget("Red").sliceLogic()

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

    # Playback
    self.playbackInProgress = False

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
      self.stylus_model.GetModelDisplayNode().SetSliceIntersectionVisibility(self.highlightModelsInImage)
      self.vessel_1_model.GetModelDisplayNode().SetSliceIntersectionVisibility(self.highlightModelsInImage)
      self.vessel_2_model.GetModelDisplayNode().SetSliceIntersectionVisibility(self.highlightModelsInImage)
      self.vessel_3_model.GetModelDisplayNode().SetSliceIntersectionVisibility(self.highlightModelsInImage)
      self.vessel_4_model.GetModelDisplayNode().SetSliceIntersectionVisibility(self.highlightModelsInImage)
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
    self.stylus_model.SetAndObserveTransformNodeID(self.StylusTipToStylus.GetID())
    self.StylusTipToStylus.SetAndObserveTransformNodeID(self.StylusToTracker.GetID())
    self.needle_model.SetAndObserveTransformNodeID(self.NeedleTipToNeedle.GetID())
    self.NeedleTipToNeedle.SetAndObserveTransformNodeID(self.NeedleToTracker.GetID())
    self.usProbe_model.SetAndObserveTransformNodeID(self.ProbeModelToProbe.GetID())
    self.usImageVolumeNode.SetAndObserveTransformNodeID(self.ImageToProbe.GetID())
    self.ProbeModelToProbe.SetAndObserveTransformNodeID(self.ProbeToTracker.GetID())    
    self.ImageToProbe.SetAndObserveTransformNodeID(self.ProbeToTracker.GetID())    
    self.StylusToTracker.SetAndObserveTransformNodeID(self.TrackerToPatient.GetID())
    self.NeedleToTracker.SetAndObserveTransformNodeID(self.TrackerToPatient.GetID())
    self.ProbeToTracker.SetAndObserveTransformNodeID(self.TrackerToPatient.GetID())

    # Fit US image to view and display in 3D view     
    self.redSliceLogic.FitSliceToAll()
    self.redSliceLogic.GetSliceNode().SetSliceVisible(1)

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
    self.stylus_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'StylusModel', [0.21,0.90,0.10], visibility_bool = True, opacityValue = 1.0)
    self.needle_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'NeedleModel', [1.0,0.86,0.68], visibility_bool = True, opacityValue = 1.0)

    # Load transforms
    self.StylusToTracker = self.getOrCreateTransform('StylusToTracker')
    self.NeedleToTracker = self.getOrCreateTransform('NeedleToTracker')
    self.ProbeToTracker = self.getOrCreateTransform('ProbeToTracker')
    #self.StylusToTracker = self.loadTransformFromFile(self.dataFolderPath, 'StylusToTracker') # ONLY FOR DEVELOPMENT
    #self.NeedleToTracker = self.loadTransformFromFile(self.dataFolderPath, 'NeedleToTracker') # ONLY FOR DEVELOPMENT
    #self.ProbeToTracker = self.loadTransformFromFile(self.dataFolderPath, 'ProbeToTracker') # ONLY FOR DEVELOPMENT
    self.TrackerToPatient = self.getOrCreateTransform('TrackerToPatient')
    self.StylusTipToStylus = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'StylusTipToStylus')
    self.NeedleTipToNeedle = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'NeedleTipToNeedle')
    self.ProbeModelToProbe = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'ProbeModelToProbe')
    self.ImageToProbe = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'ImageToProbe')

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
        print('ERROR: ' + transformName + ' transform was not found. Creating node as identity...')
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
          print('ERROR: ' + transformFileName + ' transform not found in path. Creating node as identity...')
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
          print('ERROR: ' + modelFileName + ' model not found in path')
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
      self.sequencesLogic.AddSynchronizedNode(None, self.StylusToTracker, self.sequenceBrowserNode)
      self.sequencesLogic.AddSynchronizedNode(None, self.usImageVolumeNode, self.sequenceBrowserNode)

      # Stop overwritting and saving changes to all nodes
      self.sequenceBrowserNode.SetRecording(None, True)
      self.sequenceBrowserNode.SetOverwriteProxyName(None, False)
      self.sequenceBrowserNode.SetSaveChanges(None, False)

      self.sequenceBrowserNode.EndModify(modifiedFlag)

      return True

    except:
      logging.error('Error creating a new sequence browser node...')
      return False

  #------------------------------------------------------------------------------
  def clearSequenceBrowserRecording(self):
    """
    Clear recording data.
    """
    try:
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
    except:
      logging.error('Error loading sequence browser node from file...')

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
    self.setCustomLayout('3D only') # default

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
      " <item>"
      "  <view class=\"vtkMRMLSliceNode\" singletontag=\"Red\">"
      "     <property name=\"orientation\" action=\"default\">Axial</property>"
      "     <property name=\"viewlabel\" action=\"default\">R</property>"
      "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
      "  </view>"
      " </item>"
      " <item>"
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
      layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_Dual2D3D_ID, customLayout_Dual2D3D)
      layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_2Donly_ID, customLayout_2Donly)
      layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_Dual3D3D_ID, customLayout_Dual3D3D)
      layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_FourUp3D_ID, customLayout_FourUp3D)

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
    elif layoutName == 'Four Up 3D':
      layoutID = self.customLayout_FourUp3D_ID

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

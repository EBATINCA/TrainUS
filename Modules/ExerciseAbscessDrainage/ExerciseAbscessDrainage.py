import vtk, qt, ctk, slicer
import os
import numpy as np
import time

from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

import logging

import json

# TrainUS parameters
import TrainUSLib.TrainUSParameters as Parameters

#------------------------------------------------------------------------------
#
# ExerciseAbscessDrainage
#
#------------------------------------------------------------------------------
class ExerciseAbscessDrainage(ScriptedLoadableModule):
  
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Exercise Abscess Drainage"
    self.parent.categories = ["TrainUS"]
    self.parent.dependencies = []
    self.parent.contributors = ["David Garcia Mato (Ebatinca)"]
    self.parent.helpText = """ Module to train US-guided abscess drainage. """
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """This project has been funded by NEOTEC grant from the Centre for the Development of Technology and Innovation (CDTI) of the Ministry for Science and Innovation of the Government of Spain."""


#------------------------------------------------------------------------------
#
# ExerciseAbscessDrainageWidget
#
#------------------------------------------------------------------------------
class ExerciseAbscessDrainageWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  
  def __init__(self, parent):
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)

    # Create logic class
    self.logic = ExerciseAbscessDrainageLogic(self)

    slicer.ExerciseAbscessDrainageWidget = self # ONLY FOR DEVELOPMENT

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
    # Get app use case
    appUseCase = Parameters.instance.getParameterString(Parameters.APP_USE_CASE)

    # Set use case: recording or evaluation
    self.logic.exerciseMode = appUseCase
    
    # Load exercise data
    self.logic.loadExerciseData()

    # Evaluation use case
    if appUseCase == Parameters.APP_USE_CASE_EVALUATION:
      # Get selected participant and recording
      selectedParticipantID = slicer.trainUsWidget.logic.recordingManager.getSelectedParticipantID()
      selectedRecordingID = slicer.trainUsWidget.logic.recordingManager.getSelectedRecordingID()
      # Get recording folder
      recordingInfoFilePath = slicer.trainUsWidget.logic.recordingManager.getRecordingInfoFilePath(selectedParticipantID, selectedRecordingID)
      recordingFolderPath = os.path.dirname(recordingInfoFilePath)
      # Search for SQBR file in folder
      recordingFile = None
      for fileName in os.listdir(recordingFolderPath):
        if fileName.endswith(".sqbr"):
          recordingFile = fileName        
      # Load recording file
      if recordingFile:
        self.logic.loadRecordingFile(os.path.join(recordingFolderPath, recordingFile))
      else:
        logging.error('Recording file was not found in database. Skipping...')

    # Default viewpoint
    self.logic.currentViewpointMode = 'Front'

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
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/ExerciseAbscessDrainage.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Customize widgets
    self.ui.modeSelectionGroupBox.visible = False
    self.ui.showInstructionsButton.setText('Show')
    self.ui.videoInstructionsButton.setIcon(qt.QIcon(self.resourcePath('Icons/videoIcon_small.png')))    
    self.ui.videoInstructionsButton.minimumWidth = self.ui.videoInstructionsButton.sizeHint.height()
    self.ui.recordingTimerWidget.slider().visible = False    
    self.ui.trimSequenceGroupBox.collapsed = True

    # Disable slice annotations immediately
    #sliceAnnotations = slicer.modules.DataProbeInstance.infoWidget.sliceAnnotations
    #sliceAnnotations.sliceViewAnnotationsEnabled = False
    #sliceAnnotations.updateSliceViewFromGUI()

  #------------------------------------------------------------------------------
  def setupConnections(self):    
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
    # View control
    self.ui.leftViewButton.clicked.connect(self.onLeftViewButtonClicked)
    self.ui.frontViewButton.clicked.connect(self.onFrontViewButtonClicked)
    self.ui.rightViewButton.clicked.connect(self.onRightViewButtonClicked)
    self.ui.bottomViewButton.clicked.connect(self.onBottomViewButtonClicked)
    self.ui.freeViewButton.clicked.connect(self.onFreeViewButtonClicked)
    # Recording
    self.ui.startStopRecordingButton.clicked.connect(self.onStartStopRecordingButtonClicked)
    self.ui.clearRecordingButton.clicked.connect(self.onClearRecordingButtonClicked)
    self.ui.saveRecordingButton.clicked.connect(self.onSaveRecordingButtonClicked)
    # Trim sequence
    self.ui.trimSequenceGroupBox.toggled.connect(self.onTrimSequenceGroupBoxCollapsed)
    self.ui.trimSequenceDoubleRangeSlider.valuesChanged.connect(self.onTrimSequenceDoubleRangeSliderModified)
    self.ui.trimSequenceDoubleRangeSlider.minimumPositionChanged.connect(self.onTrimSequenceMinPosDoubleRangeSliderModified)
    self.ui.trimSequenceDoubleRangeSlider.maximumPositionChanged.connect(self.onTrimSequenceMaxPosDoubleRangeSliderModified)
    self.ui.trimSequenceButton.clicked.connect(self.onTrimSequenceButtonClicked)
    # Back to menu
    self.ui.backToMenuButton.clicked.connect(self.onBackToMenuButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
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
    # View control
    self.ui.leftViewButton.clicked.disconnect()
    self.ui.frontViewButton.clicked.disconnect()
    self.ui.rightViewButton.clicked.disconnect()
    self.ui.bottomViewButton.clicked.disconnect()
    self.ui.freeViewButton.clicked.disconnect()
    # Recording
    self.ui.startStopRecordingButton.clicked.disconnect()
    self.ui.clearRecordingButton.clicked.disconnect()
    self.ui.saveRecordingButton.clicked.disconnect()
    # Trim sequence
    self.ui.trimSequenceGroupBox.toggled.disconnect()
    self.ui.trimSequenceDoubleRangeSlider.valuesChanged.disconnect()
    self.ui.trimSequenceDoubleRangeSlider.minimumPositionChanged.disconnect()
    self.ui.trimSequenceDoubleRangeSlider.maximumPositionChanged.disconnect()
    self.ui.trimSequenceButton.clicked.disconnect()
    # Back to menu
    self.ui.backToMenuButton.clicked.disconnect()

  #------------------------------------------------------------------------------
  def updateGUIFromMRML(self, caller=None, event=None):
    """
    Set selections and other settings on the GUI based on the parameter node.

    Calls the updateGUIFromMRML function of all tabs so that they can take care of their own GUI.
    """    
    # Mode
    if self.logic.exerciseMode == Parameters.APP_USE_CASE_RECORDING:
      self.ui.instructionsGroupBox.visible = True
      self.ui.recordingGroupBox.visible = True
      self.ui.playbackGroupBox.visible = False
    elif self.logic.exerciseMode == Parameters.APP_USE_CASE_EVALUATION:
      self.ui.instructionsGroupBox.visible = True
      self.ui.recordingGroupBox.visible = False
      self.ui.playbackGroupBox.visible = True
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
  def onStartStopRecordingButtonClicked(self):    
    # Check recording status
    recordingInProgress = self.logic.sequenceBrowserUtils.getRecordingInProgress()

    # Update sequence browser recording status
    if recordingInProgress:
      # Stop recording
      self.logic.sequenceBrowserUtils.stopSequenceBrowserRecording()
    else:
      # Start recording
      synchronizedNodes = [self.logic.NeedleToTracker, self.logic.ProbeToTracker, self.logic.TrackerToPatient, self.logic.usImageVolumeNode]
      self.logic.sequenceBrowserUtils.setSynchronizedNodes(synchronizedNodes)
      self.logic.sequenceBrowserUtils.startSequenceBrowserRecording()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onClearRecordingButtonClicked(self):
    # Delete previous recording
    self.logic.sequenceBrowserUtils.clearSequenceBrowser()

    # Create new recording
    synchronizedNodes = [self.logic.NeedleToTracker, self.logic.ProbeToTracker, self.logic.TrackerToPatient, self.logic.usImageVolumeNode]
    self.logic.sequenceBrowserUtils.setSynchronizedNodes(synchronizedNodes)
    self.logic.sequenceBrowserUtils.createNewSequenceBrowser()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onSaveRecordingButtonClicked(self):

    # Get recording duration
    recordingDuration = self.logic.sequenceBrowserUtils.getRecordingLength()
    
    # Create new recording
    slicer.trainUsWidget.logic.recordingManager.createNewRecording(Parameters.EXERCISE_ADVANCED_DRAINAGE, recordingDuration)

    # Get recording folder path
    selectedParticipantID = slicer.trainUsWidget.logic.recordingManager.getSelectedParticipantID()
    selectedRecordingID = slicer.trainUsWidget.logic.recordingManager.getSelectedRecordingID()
    recordingInfoFilePath = slicer.trainUsWidget.logic.recordingManager.getRecordingInfoFilePath(selectedParticipantID, selectedRecordingID)
    recordingFolderPath = os.path.dirname(recordingInfoFilePath)

    # Generate recording file path
    filename = 'Recording-' + time.strftime("%Y%m%d-%H%M%S") + os.extsep + "sqbr"
    filePath = os.path.join(recordingFolderPath, filename)

    # Save sequence browser node
    self.logic.sequenceBrowserUtils.saveSequenceBrowser(filePath)

    # Save exercise options to JSON file
    recordingInfo = slicer.trainUsWidget.logic.recordingManager.readRecordingInfoFile(recordingInfoFilePath)
    recordingInfo['options'] = {}
    recordingInfo['options']['difficulty'] = self.logic.exerciseDifficulty

    # Rewrite info JSON file
    slicer.trainUsWidget.logic.recordingManager.writeRecordingInfoFile(recordingInfoFilePath, recordingInfo)

    # Recording info to save in JSON file
    print('>>>>>>>>>>>>>>>>RECORDING SAVED<<<<<<<<<<<<<<<<')
    print('Date:', time.strftime("%Y%m%d"))
    print('Time:', time.strftime("%H%M%S"))
    print('Recording length:', recordingDuration)
    print('User:', 'XXXXXXXXXXX')
    print('Hardware setup:', 'XXXXXXXXXXX')

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
  def onBackToMenuButtonClicked(self):
    # Free viewpoint
    self.logic.currentViewpointMode = 'Free'
    self.logic.updateViewpoint()
    
    # Delete exercise data
    self.logic.deleteExerciseData()
    
    # Go back to Home module
    slicer.util.selectModule('Home')

#---------------------------------------------------------------------------------------------#
#                                                                                             #
#                                                                                             #
#                                                                                             #
#                            ExerciseAbscessDrainageLogic                                     #
#                                                                                             #
#                                                                                             #
#                                                                                             #
#---------------------------------------------------------------------------------------------#
class ExerciseAbscessDrainageLogic(ScriptedLoadableModuleLogic, VTKObservationMixin):
  
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

    # Data path
    self.dataFolderPath = self.moduleWidget.resourcePath('ExerciseAbscessDrainageData/')

    # Exercise default settings
    self.exerciseDifficulty = 'Medium'  
    self.exerciseLayout = '3D only'
    self.exerciseMode = 'Recording'

    # Instructions
    self.instructionsImagesVisible = False
    self.instructionsVideoVisible = False

    # Viewpoint
    self.currentViewpointMode = 'Front' # default is front view

    # Observer
    self.observerID = None

  #------------------------------------------------------------------------------
  def loadExerciseData(self):
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
    self.usProbe_plane_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'UsProbe_Telemed_L12_US_Plane_width40mm_depth50mm', [0.0,0.0,0.0], visibility_bool = True, opacityValue = 0.5)    
    self.needle_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'StylusModel', [0.0,1.0,0.0], visibility_bool = True, opacityValue = 1.0)
    self.needle_trajectory_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'StylusTrajectoryModel', [1.0,0.0,0.0], visibility_bool = True, opacityValue = 1.0)
    self.softTissue_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'DrainagePhantom_SoftTissue', [0.87,0.67,0.45], visibility_bool = True, opacityValue = 0.5)
    self.boneTissue_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'DrainagePhantom_Ribs', [1.0,0.98,0.86], visibility_bool = True, opacityValue = 0.8)
    self.phantomFilling_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'DrainagePhantom_Filling', [1.0,0.0,0.0], visibility_bool = True, opacityValue = 0.5)
    
    # Load tracker transforms (ONLY FOR DEVELOPMENT)
    _ = self.loadTransformFromFile(self.dataFolderPath, 'NeedleToTracker') # ONLY FOR DEVELOPMENT
    _ = self.loadTransformFromFile(self.dataFolderPath, 'ProbeToTracker') # ONLY FOR DEVELOPMENT
    _ = self.loadTransformFromFile(self.dataFolderPath, 'TrackerToPatient') # ONLY FOR DEVELOPMENT
    
    # Load transforms
    self.NeedleToTracker = self.getOrCreateTransform('NeedleToTracker')
    self.ProbeToTracker = self.getOrCreateTransform('ProbeToTracker')
    self.TrackerToPatient = self.getOrCreateTransform('TrackerToPatient')
    self.NeedleTipToNeedle = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'NeedleTipToNeedle')
    self.ProbeModelToProbe = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'ProbeModelToProbe')
    self.ImageToProbe = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'ImageToProbe')
    self.PatientToRas = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'PatientToRas')

    # Load camera transforms
    self.LeftCameraToRas = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'LeftCameraToRas')
    self.FrontCameraToRas = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'FrontCameraToRas')
    self.RightCameraToRas = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'RightCameraToRas')
    self.BottomCameraToRas = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'BottomCameraToRas')

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

    # Build transform tree
    self.needle_model.SetAndObserveTransformNodeID(self.NeedleTipToNeedle.GetID())
    self.needle_trajectory_model.SetAndObserveTransformNodeID(self.NeedleTipToNeedle.GetID())
    self.needleTrajectory_fiducials.SetAndObserveTransformNodeID(self.NeedleTipToNeedle.GetID())
    self.NeedleTipToNeedle.SetAndObserveTransformNodeID(self.NeedleToTracker.GetID())
    self.usProbe_model.SetAndObserveTransformNodeID(self.ProbeModelToProbe.GetID())
    self.usProbe_plane_model.SetAndObserveTransformNodeID(self.ProbeModelToProbe.GetID())
    self.usProbe_plane.SetAndObserveTransformNodeID(self.ProbeModelToProbe.GetID())
    self.usImageVolumeNode.SetAndObserveTransformNodeID(self.ImageToProbe.GetID())
    self.ProbeModelToProbe.SetAndObserveTransformNodeID(self.ProbeToTracker.GetID())    
    self.ImageToProbe.SetAndObserveTransformNodeID(self.ProbeToTracker.GetID())    
    self.NeedleToTracker.SetAndObserveTransformNodeID(self.TrackerToPatient.GetID())
    self.ProbeToTracker.SetAndObserveTransformNodeID(self.TrackerToPatient.GetID())
    self.TrackerToPatient.SetAndObserveTransformNodeID(self.PatientToRas.GetID())

    # Volume reslice driver (SlicerIGT extension)
    try:
      volumeResliceDriverLogic = slicer.modules.volumereslicedriver.logic()
    except:
      logging.error('ERROR: "Volume Reslice Driver" module was not found.')

    # Display US image in red slice view
    sliceLogic = slicer.app.layoutManager().sliceWidget('Red').sliceLogic()
    sliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(self.usImageVolumeNode.GetID())
    volumeResliceDriverLogic.SetDriverForSlice(self.usImageVolumeNode.GetID(), sliceLogic.GetSliceNode())
    volumeResliceDriverLogic.SetModeForSlice(volumeResliceDriverLogic.MODE_TRANSVERSE, sliceLogic.GetSliceNode())
    sliceLogic.FitSliceToAll()
    sliceLogic.GetSliceNode().SetSliceVisible(False)

    # Remove 3D cube and 3D axis label from 3D view
    self.layoutUtils.hideCubeAndLabelsInThreeDView()

    # Reset focal point in 3D view
    self.layoutUtils.resetFocalPointInThreeDView()

    # Avoid needle model to be seen in yellow slice view during instructions display
    self.needle_model.GetModelDisplayNode().SetViewNodeIDs(('vtkMRMLSliceNodeRed', 'vtkMRMLViewNode1'))

    # Set difficulty parameters
    self.updateDifficulty()

  #------------------------------------------------------------------------------
  def deleteExerciseData(self):
    # Delete instructions    
    slicer.mrmlScene.RemoveNode(self.instructionsImageVolume)
    try:
      slicer.mrmlScene.RemoveNode(self.instructionsSequenceBrowser)
      slicer.mrmlScene.RemoveNode(self.instructionsVideoVolume)
    except:
      pass

    # Delete models
    slicer.mrmlScene.RemoveNode(self.usProbe_model)
    slicer.mrmlScene.RemoveNode(self.usProbe_plane_model)
    slicer.mrmlScene.RemoveNode(self.needle_model)
    slicer.mrmlScene.RemoveNode(self.needle_trajectory_model)
    slicer.mrmlScene.RemoveNode(self.softTissue_model)
    slicer.mrmlScene.RemoveNode(self.boneTissue_model)
    slicer.mrmlScene.RemoveNode(self.phantomFilling_model)

    # Delete transforms
    slicer.mrmlScene.RemoveNode(self.NeedleTipToNeedle)
    slicer.mrmlScene.RemoveNode(self.ProbeModelToProbe)
    slicer.mrmlScene.RemoveNode(self.ImageToProbe)
    slicer.mrmlScene.RemoveNode(self.PatientToRas)
    slicer.mrmlScene.RemoveNode(self.LeftCameraToRas)
    slicer.mrmlScene.RemoveNode(self.FrontCameraToRas)
    slicer.mrmlScene.RemoveNode(self.RightCameraToRas)
    slicer.mrmlScene.RemoveNode(self.BottomCameraToRas)
  
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
      self.needle_model.GetModelDisplayNode().SetVisibility2D(self.highlightModelsInImage)
      # Display spine model projected in US image
      self.spine_model.GetModelDisplayNode().SetVisibility2D(self.highlightModelsInImage)
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
        node = slicer.util.getNode(transformFileName)
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
  def loadMarkupsFiducialListFromFile(self, markupsFiducialListFilePath, markupsFiducialListFileName, colorRGB_array, visibility_bool, opacityValue):
    try:
        node = slicer.util.getNode(markupsFiducialListFileName)
    except:
        try:
          node = slicer.util.loadMarkups(markupsFiducialListFilePath + '/' + markupsFiducialListFileName + '.mrk.json')
          node.SetLocked(True)
          node.GetDisplayNode().SetSelectedColor(colorRGB_array)
          node.GetDisplayNode().SetPropertiesLabelVisibility(False) # hide text
          node.GetDisplayNode().SetVisibility(visibility_bool)
          print(markupsFiducialListFileName + ' markups fiducial list loaded')
        except:
          node = None
          logging.error('ERROR: ' + markupsFiducialListFileName + ' markups fiducial list not found in path')
    return node
    
  #------------------------------------------------------------------------------
  def loadMarkupsPlaneFromFile(self, markupsPlaneFilePath, markupsPlaneFileName, colorRGB_array, visibility_bool, opacityValue):
    try:
        node = slicer.util.getNode(markupsPlaneFileName)
    except:
        try:
          node = slicer.util.loadMarkups(markupsPlaneFilePath + '/' + markupsPlaneFileName + '.mrk.json')
          node.SetLocked(True)
          node.GetDisplayNode().SetGlyphScale(0.0)
          node.GetDisplayNode().SetOpacity(opacityValue)
          node.GetDisplayNode().SetSelectedColor(colorRGB_array)
          node.GetDisplayNode().SetPropertiesLabelVisibility(False) # hide text
          node.GetDisplayNode().SetHandlesInteractive(False)
          node.GetDisplayNode().SetVisibility2D(False)
          node.GetDisplayNode().SetVisibility(visibility_bool)
          print(markupsPlaneFileName + ' markups plane loaded')
        except:
          node = None
          logging.error('ERROR: ' + markupsPlaneFileName + ' markups plane not found in path')
    return node
  
  #------------------------------------------------------------------------------
  def updateViewpoint(self):
    """
    Update virtual camera mode for 3D view.
    """
    # Select camera transform
    try:
      if self.currentViewpointMode == 'Left': cameraTransform = self.LeftCameraToRas
      elif self.currentViewpointMode == 'Front': cameraTransform = self.FrontCameraToRas
      elif self.currentViewpointMode == 'Right': cameraTransform = self.RightCameraToRas
      elif self.currentViewpointMode == 'Bottom': cameraTransform = self.BottomCameraToRas
      else: cameraTransform = None
    except:
      return

    # Update viewpoint in 3D view
    self.layoutUtils.activateViewpoint(cameraTransform)

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
  def loadRecordingFile(self, filePath):
    """
    Load recording from .sqbr file.
    """
    # Delete previous recording
    self.sequenceBrowserUtils.clearSequenceBrowser()

    # Load sequence browser node
    self.sequenceBrowserUtils.loadSequenceBrowser(filePath)

    # Reset focal point in 3D view
    self.layoutUtils.resetFocalPointInThreeDView()

    # Load recording info file
    recordingInfoFilePath = os.path.join(os.path.dirname(filePath), 'Recording_Info.json')
    if os.path.isfile(recordingInfoFilePath):
      recordingInfo = slicer.trainUsWidget.logic.recordingManager.readRecordingInfoFile(recordingInfoFilePath)
    else:
      logging.error('Recording info file was not found in folder.')
      return 

    # Apply saved exercise options
    if 'options' in recordingInfo.keys():
      # Update difficulty corresponding to recording
      self.exerciseDifficulty = recordingInfo['options']['difficulty']
      self.updateDifficulty()


#------------------------------------------------------------------------------
#
# ExerciseAbscessDrainageTest
#
#------------------------------------------------------------------------------
class ExerciseAbscessDrainageTest(ScriptedLoadableModuleTest):
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
class ExerciseAbscessDrainageFileWriter(object):
  def __init__(self, parent):
    pass

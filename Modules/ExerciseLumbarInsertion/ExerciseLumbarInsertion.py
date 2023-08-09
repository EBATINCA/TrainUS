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
# ExerciseLumbarInsertion
#
#------------------------------------------------------------------------------
class ExerciseLumbarInsertion(ScriptedLoadableModule):
  
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Exercise Lumbar Insertion"
    self.parent.categories = ["TrainUS"]
    self.parent.dependencies = []
    self.parent.contributors = ["David Garcia Mato (Ebatinca)"]
    self.parent.helpText = """ Module to train US-guided lumbar needle insertion. """
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """This project has been funded by NEOTEC grant from the Centre for the Development of Technology and Innovation (CDTI) of the Ministry for Science and Innovation of the Government of Spain."""


#------------------------------------------------------------------------------
#
# ExerciseLumbarInsertionWidget
#
#------------------------------------------------------------------------------
class ExerciseLumbarInsertionWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  
  def __init__(self, parent):
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)

    # Create logic class
    self.logic = ExerciseLumbarInsertionLogic(self)

    slicer.ExerciseLumbarInsertionWidget = self # ONLY FOR DEVELOPMENT

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
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/ExerciseLumbarInsertion.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Customize widgets
    self.ui.showInstructionsButton.setText('Show')
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
    # Workflow
    self.ui.checkStep1Button.clicked.connect(self.onCheckStep1ButtonClicked)
    self.ui.checkStep2Button.clicked.connect(self.onCheckStep2ButtonClicked)
    self.ui.checkStep3Button.clicked.connect(self.onCheckStep3ButtonClicked)
    self.ui.checkStep4Button.clicked.connect(self.onCheckStep4ButtonClicked)
    self.ui.checkStep5Button.clicked.connect(self.onCheckStep5ButtonClicked)
    # Back to menu
    self.ui.backToMenuButton.clicked.connect(self.onBackToMenuButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    # Load data
    self.ui.loadDataButton.clicked.disconnect()    
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
    # Workflow
    self.ui.checkStep1Button.clicked.disconnect()
    self.ui.checkStep2Button.clicked.disconnect()
    self.ui.checkStep3Button.clicked.disconnect()
    self.ui.checkStep4Button.clicked.disconnect()
    self.ui.checkStep5Button.clicked.disconnect()
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
  def onCheckStep1ButtonClicked(self):
    # Check workflow step
    success = self.logic.checkWorkflowStep(stepId = 1)

    # Show result
    if success:
      self.ui.checkStep1OutputLabel.setText('CORRECT')
      self.ui.checkStep1OutputLabel.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; color : green; }")
    else:
      self.ui.checkStep1OutputLabel.setText('INCORRECT')
      self.ui.checkStep1OutputLabel.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; color : red; }")

  #------------------------------------------------------------------------------
  def onCheckStep2ButtonClicked(self):
    # Check workflow step
    success = self.logic.checkWorkflowStep(stepId = 2)

    # Show result
    if success:
      self.ui.checkStep1OutputLabel.setText('CORRECT')
    else:
      self.ui.checkStep1OutputLabel.setText('INCORRECT')

  #------------------------------------------------------------------------------
  def onCheckStep3ButtonClicked(self):
    # Check workflow step
    success = self.logic.checkWorkflowStep(stepId = 3)

    # Show result
    if success:
      self.ui.checkStep1OutputLabel.setText('CORRECT')
    else:
      self.ui.checkStep1OutputLabel.setText('INCORRECT')

  #------------------------------------------------------------------------------
  def onCheckStep4ButtonClicked(self):
    # Check workflow step
    success = self.logic.checkWorkflowStep(stepId = 4)

    # Show result
    if success:
      self.ui.checkStep1OutputLabel.setText('CORRECT')
    else:
      self.ui.checkStep1OutputLabel.setText('INCORRECT')

  #------------------------------------------------------------------------------
  def onCheckStep5ButtonClicked(self):
    # Check workflow step
    success = self.logic.checkWorkflowStep(stepId = 5)

    # Show result
    if success:
      self.ui.checkStep1OutputLabel.setText('CORRECT')
    else:
      self.ui.checkStep1OutputLabel.setText('INCORRECT')

  #------------------------------------------------------------------------------
  def onBackToMenuButtonClicked(self):    
    # Go back to Home module
    #slicer.util.selectModule('Home') 
    print('Back to home!')

#---------------------------------------------------------------------------------------------#
#                                                                                             #
#                                                                                             #
#                                                                                             #
#                            ExerciseLumbarInsertionLogic                                     #
#                                                                                             #
#                                                                                             #
#                                                                                             #
#---------------------------------------------------------------------------------------------#
class ExerciseLumbarInsertionLogic(ScriptedLoadableModuleLogic, VTKObservationMixin):
  
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
    self.dataFolderPath = self.moduleWidget.resourcePath('ExerciseLumbarInsertionData/')

    # Exercise default settings
    self.exerciseDifficulty = 'Medium'  
    self.exerciseLayout = '3D only'
    self.exerciseMode = 'Evaluation'

    # Instructions
    self.instructionsImagesVisible = False
    self.instructionsVideoVisible = False

    # Viewpoint
    self.currentViewpointMode = 'Free' # default is front view

    # Observer
    self.observerID = None

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
    self.usProbe_plane_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'UsProbe_Telemed_L12_US_Plane_width40mm_depth50mm', [0.0,0.0,0.0], visibility_bool = True, opacityValue = 0.5)    
    self.needle_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'StylusModel', [0.0,1.0,0.0], visibility_bool = True, opacityValue = 1.0)
    self.needle_trajectory_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'StylusTrajectoryModel', [1.0,0.0,0.0], visibility_bool = True, opacityValue = 1.0)
    self.softTissue_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'LumbarPhantom_SoftTissueModel', [0.87,0.67,0.45], visibility_bool = True, opacityValue = 0.5)
    self.spine_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'LumbarPhantom_SpineModel', [1.0,0.98,0.86], visibility_bool = True, opacityValue = 1.0)
    self.l1_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'LumbarPhantom_SpinousProcess_L1', [1.0,0.98,0.86], visibility_bool = False, opacityValue = 1.0)
    self.l2_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'LumbarPhantom_SpinousProcess_L2', [1.0,0.98,0.86], visibility_bool = False, opacityValue = 1.0)
    self.l3_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'LumbarPhantom_SpinousProcess_L3', [1.0,0.98,0.86], visibility_bool = False, opacityValue = 1.0)
    self.l4_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'LumbarPhantom_SpinousProcess_L4', [1.0,0.98,0.86], visibility_bool = False, opacityValue = 1.0)
    self.l5_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'LumbarPhantom_SpinousProcess_L5', [1.0,0.98,0.86], visibility_bool = False, opacityValue = 1.0)
    
    # Load transforms
    self.NeedleToTracker = self.getOrCreateTransform('StylusToTracker')
    self.ProbeToTracker = self.getOrCreateTransform('ProbeToTracker')
    #self.NeedleToTracker = self.loadTransformFromFile(self.dataFolderPath, 'NeedleToTracker') # ONLY FOR DEVELOPMENT
    #self.ProbeToTracker = self.loadTransformFromFile(self.dataFolderPath, 'ProbeToTracker') # ONLY FOR DEVELOPMENT
    self.TrackerToPatient = self.getOrCreateTransform('TrackerToPatient')
    self.NeedleTipToNeedle = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'StylusTipToStylus')
    self.ProbeModelToProbe = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'ProbeModelToProbe')
    self.ImageToProbe = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'ImageToProbe')
    self.PatientToRas = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'PatientToRas')

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
    self.needle_trajectory_model.SetAndObserveTransformNodeID(self.NeedleTipToNeedle.GetID())
    self.NeedleTipToNeedle.SetAndObserveTransformNodeID(self.NeedleToTracker.GetID())
    self.usProbe_model.SetAndObserveTransformNodeID(self.ProbeModelToProbe.GetID())
    self.usProbe_plane_model.SetAndObserveTransformNodeID(self.ProbeModelToProbe.GetID())
    self.usImageVolumeNode.SetAndObserveTransformNodeID(self.ImageToProbe.GetID())
    self.ProbeModelToProbe.SetAndObserveTransformNodeID(self.ProbeToTracker.GetID())    
    self.ImageToProbe.SetAndObserveTransformNodeID(self.ProbeToTracker.GetID())    
    self.NeedleToTracker.SetAndObserveTransformNodeID(self.TrackerToPatient.GetID())
    self.ProbeToTracker.SetAndObserveTransformNodeID(self.TrackerToPatient.GetID())
    self.TrackerToPatient.SetAndObserveTransformNodeID(self.PatientToRas.GetID())

    # US probe camera transforms
    self.LeftCameraToProbeModel.SetAndObserveTransformNodeID(self.ProbeModelToProbe.GetID())
    self.FrontCameraToProbeModel.SetAndObserveTransformNodeID(self.ProbeModelToProbe.GetID())
    self.RightCameraToProbeModel.SetAndObserveTransformNodeID(self.ProbeModelToProbe.GetID())
    self.BottomCameraToProbeModel.SetAndObserveTransformNodeID(self.ProbeModelToProbe.GetID())    

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
  def checkWorkflowStep(self, stepId):
    """
    Check performance on each workflow step.
    """
    if stepId == 1: # Check if L1 spinous process if intersected by ultrasound plane
      success = self.getCollisionWithUltrasoundPlane(self.l1_model)
      print('checkWorkflowStep --- Step 1 = ', success)
    if stepId == 2: # Check if L2 spinous process if intersected by ultrasound plane
      success = self.getCollisionWithUltrasoundPlane(self.l2_model)
      print('checkWorkflowStep --- Step 2 = ', success)
    if stepId == 3: # Check if L3 spinous process if intersected by ultrasound plane
      success = self.getCollisionWithUltrasoundPlane(self.l3_model)
      print('checkWorkflowStep --- Step 3 = ', success)
    if stepId == 4: # Check if L4 spinous process if intersected by ultrasound plane
      success = self.getCollisionWithUltrasoundPlane(self.l4_model)
      print('checkWorkflowStep --- Step 4 = ', success)
    if stepId == 5: # Check if L5 spinous process if intersected by ultrasound plane
      success = self.getCollisionWithUltrasoundPlane(self.l5_model)
      print('checkWorkflowStep --- Step 5 = ', success)

    return success

  #------------------------------------------------------------------------------
  def getCollisionWithUltrasoundPlane(self, inputModelNode):
    """
    Check collision between ultrasound plane model and input model.
    """
    # Get models
    modelA = self.usProbe_plane_model
    modelB = inputModelNode

    # Model world transforms
    modelAToWorldMatrix = vtk.vtkMatrix4x4()
    modelA.GetParentTransformNode().GetMatrixTransformToWorld(modelAToWorldMatrix)
    modelBToWorldMatrix = vtk.vtkMatrix4x4()
    if modelB.GetParentTransformNode():
      modelB.GetParentTransformNode().GetMatrixTransformToWorld(modelBToWorldMatrix)

    # Model collision
    collide = vtk.vtkCollisionDetectionFilter()
    collide.SetInputData(0, modelA.GetPolyData())
    collide.SetInputData(1, modelB.GetPolyData())
    collide.SetCollisionModeToFirstContact()
    collide.SetMatrix(0, modelAToWorldMatrix)
    collide.SetMatrix(1, modelBToWorldMatrix)
    collide.Update()
    numContacts = collide.GetNumberOfContacts()
    print('getCollisionWithUltrasoundPlane ---> # contacts = ', numContacts)

    # Output
    if numContacts > 0:
      collision = True
    else:
      collision = False
    
    return collision

#------------------------------------------------------------------------------
#
# ExerciseLumbarInsertionTest
#
#------------------------------------------------------------------------------
class ExerciseLumbarInsertionTest(ScriptedLoadableModuleTest):
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
class ExerciseLumbarInsertionFileWriter(object):
  def __init__(self, parent):
    pass

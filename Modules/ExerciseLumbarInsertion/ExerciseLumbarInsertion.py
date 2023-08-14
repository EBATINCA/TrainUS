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

    # Define steps group boxes
    self.currentWorkflowStep = 0
    self.workflowStepGroupBoxesDict = {'Step 1': self.ui.step1GroupBox,
                                      'Step 2': self.ui.step2GroupBox,
                                      'Step 3': self.ui.step3GroupBox,
                                      'Step 4': self.ui.step4GroupBox,
                                      'Step 5': self.ui.step5GroupBox,
                                      'Step 6': self.ui.step6GroupBox,
                                      'Step 7': self.ui.step7GroupBox}
    
    # Set up default visibility for workflow step group boxes
    self.ui.step1GroupBox.visible = True
    self.ui.step2GroupBox.visible = False
    self.ui.step3GroupBox.visible = False
    self.ui.step4GroupBox.visible = False
    self.ui.step5GroupBox.visible = False
    self.ui.step6GroupBox.visible = False
    self.ui.step7GroupBox.visible = False

    # Uncollapse all workflow step group boxes
    self.ui.step1GroupBox.collapsed = False
    self.ui.step2GroupBox.collapsed = False
    self.ui.step3GroupBox.collapsed = False
    self.ui.step4GroupBox.collapsed = False
    self.ui.step5GroupBox.collapsed = False
    self.ui.step6GroupBox.collapsed = False
    self.ui.step7GroupBox.collapsed = False

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
    self.ui.checkStep6Button.clicked.connect(self.onCheckStep6ButtonClicked)
    self.ui.checkStep7Button.clicked.connect(self.onCheckStep7ButtonClicked)
    self.ui.previousStepButton.clicked.connect(self.onPreviousStepButtonClicked)
    self.ui.nextStepButton.clicked.connect(self.onNextStepButtonClicked)
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
    self.ui.checkStep6Button.clicked.disconnect()
    self.ui.checkStep7Button.clicked.disconnect()
    self.ui.previousStepButton.clicked.disconnect()
    self.ui.nextStepButton.clicked.disconnect()
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
      self.ui.checkStep2OutputLabel.setText('CORRECT')
      self.ui.checkStep2OutputLabel.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; color : green; }")
    else:
      self.ui.checkStep2OutputLabel.setText('INCORRECT')
      self.ui.checkStep2OutputLabel.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; color : red; }")

  #------------------------------------------------------------------------------
  def onCheckStep3ButtonClicked(self):
    # Check workflow step
    success = self.logic.checkWorkflowStep(stepId = 3)

    # Show result
    if success:
      self.ui.checkStep3OutputLabel.setText('CORRECT')
      self.ui.checkStep3OutputLabel.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; color : green; }")
    else:
      self.ui.checkStep3OutputLabel.setText('INCORRECT')
      self.ui.checkStep3OutputLabel.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; color : red; }")

  #------------------------------------------------------------------------------
  def onCheckStep4ButtonClicked(self):
    # Check workflow step
    success = self.logic.checkWorkflowStep(stepId = 4)

    # Show result
    if success:
      self.ui.checkStep4OutputLabel.setText('CORRECT')
      self.ui.checkStep4OutputLabel.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; color : green; }")
    else:
      self.ui.checkStep4OutputLabel.setText('INCORRECT')
      self.ui.checkStep4OutputLabel.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; color : red; }")

  #------------------------------------------------------------------------------
  def onCheckStep5ButtonClicked(self):
    # Check workflow step
    success = self.logic.checkWorkflowStep(stepId = 5)

    # Show result
    if success:
      self.ui.checkStep5OutputLabel.setText('CORRECT')
      self.ui.checkStep5OutputLabel.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; color : green; }")
    else:
      self.ui.checkStep5OutputLabel.setText('INCORRECT')
      self.ui.checkStep5OutputLabel.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; color : red; }")

  #------------------------------------------------------------------------------
  def onCheckStep6ButtonClicked(self):
    # Check workflow step
    success = self.logic.checkWorkflowStep(stepId = 6)

    # Show result
    if success:
      self.ui.checkStep6OutputLabel.setText('CORRECT')
      self.ui.checkStep6OutputLabel.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; color : green; }")
    else:
      self.ui.checkStep6OutputLabel.setText('INCORRECT')
      self.ui.checkStep6OutputLabel.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; color : red; }")

  #------------------------------------------------------------------------------
  def onCheckStep7ButtonClicked(self):
    # Check workflow step
    success = self.logic.checkWorkflowStep(stepId = 7)

    # Show result
    if success:
      self.ui.checkStep7OutputLabel.setText('CORRECT')
      self.ui.checkStep7OutputLabel.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; color : green; }")
    else:
      self.ui.checkStep7OutputLabel.setText('INCORRECT')
      self.ui.checkStep7OutputLabel.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; color : red; }")

  #------------------------------------------------------------------------------
  def onPreviousStepButtonClicked(self):
    # Update current workflow step
    if self.currentWorkflowStep == 0:
      pass
    else:      
      self.currentWorkflowStep = self.currentWorkflowStep - 1

    # Get new workflow step ID
    stepIdList = list(self.workflowStepGroupBoxesDict.keys())
    currentStepId = stepIdList[self.currentWorkflowStep]

    # Update group box visibility
    for stepId in stepIdList:
      if stepId == currentStepId:
        self.workflowStepGroupBoxesDict[stepId].visible = True
      else:
        self.workflowStepGroupBoxesDict[stepId].visible = False

  #------------------------------------------------------------------------------
  def onNextStepButtonClicked(self):
    # Update current workflow step
    if self.currentWorkflowStep == (len(list(self.workflowStepGroupBoxesDict.keys()))-1):
      pass
    else:      
      self.currentWorkflowStep = self.currentWorkflowStep + 1

    # Get new workflow step ID
    stepIdList = list(self.workflowStepGroupBoxesDict.keys())
    currentStepId = stepIdList[self.currentWorkflowStep]

    # Update group box visibility
    for stepId in stepIdList:
      if stepId == currentStepId:
        self.workflowStepGroupBoxesDict[stepId].visible = True
      else:
        self.workflowStepGroupBoxesDict[stepId].visible = False

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
    self.currentViewpointMode = 'Front' # default is front view

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

    # Load additional models
    self.targetL3L4_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'LumbarPhantom_SpinousSpace_L3-L4_Target1', [1.0,0.0,0.0], visibility_bool = False, opacityValue = 1.0)

    # Load reference planes
    self.usProbe_plane = self.loadMarkupsPlaneFromFile(self.dataFolderPath + '/Planes/', 'Plane_US_Image', [0.0,0.0,0.0], visibility_bool = False, opacityValue = 0.7)
    self.sagittal_plane = self.loadMarkupsPlaneFromFile(self.dataFolderPath + '/Planes/', 'Plane_Sagittal', [1.0,0.0,0.0], visibility_bool = False, opacityValue = 0.7)
    self.axial_l1_plane = self.loadMarkupsPlaneFromFile(self.dataFolderPath + '/Planes/', 'Plane_Axial_L1', [1.0,0.0,0.0], visibility_bool = False, opacityValue = 0.7)
    self.axial_l2_plane = self.loadMarkupsPlaneFromFile(self.dataFolderPath + '/Planes/', 'Plane_Axial_L2', [1.0,0.0,0.0], visibility_bool = False, opacityValue = 0.7)
    self.axial_l3_plane = self.loadMarkupsPlaneFromFile(self.dataFolderPath + '/Planes/', 'Plane_Axial_L3', [1.0,0.0,0.0], visibility_bool = False, opacityValue = 0.7)
    self.axial_l4_plane = self.loadMarkupsPlaneFromFile(self.dataFolderPath + '/Planes/', 'Plane_Axial_L4', [1.0,0.0,0.0], visibility_bool = False, opacityValue = 0.7)
    self.axial_l5_plane = self.loadMarkupsPlaneFromFile(self.dataFolderPath + '/Planes/', 'Plane_Axial_L5', [1.0,0.0,0.0], visibility_bool = False, opacityValue = 0.7)

    # Load reference landmarks
    self.needleTrajectory_fiducials = self.loadMarkupsFiducialListFromFile(self.dataFolderPath + '/Landmarks/', 'NeedleTrajectory_TipHandle', [1.0,0.0,0.0], visibility_bool = False, opacityValue = 1.0)    
    self.optimalTrajectoryL3L4_fiducials = self.loadMarkupsFiducialListFromFile(self.dataFolderPath + '/Landmarks/', 'OptimalTrajectory_L3-L4', [1.0,0.0,0.0], visibility_bool = False, opacityValue = 1.0)
    
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

  #------------------------------------------------------------------------------
  def setupScene(self):

    # Load exercise data
    self.loadData()

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
  def checkWorkflowStep(self, stepId):
    """
    Check performance on each workflow step.
    """
    # Define thresholds for angle deviation
    angle_RL_threshold = 15.0 # degrees
    angle_AP_threshold = 15.0 # degrees
    angle_SI_threshold = 15.0 # degrees
    needle_linear_deviation_threshold = 10.0 # mm
    needle_angle_deviation_threshold = 15.0 # degrees

    # Evaluate US probe position
    #
    # Step 1: Check if L5 spinous process is aligned with ultrasound beam
    #
    if stepId == 1:
      spinousProcessIntersected = self.getCollisionWithUltrasoundPlane(self.l5_model)
      angle_AP = self.computeTransversePlaneAngleDeviationAP(self.axial_l5_plane)
      angle_RL = self.computeTransversePlaneAngleDeviationRL(self.axial_l5_plane)
      success = spinousProcessIntersected and (angle_AP < angle_AP_threshold) and (angle_RL < angle_RL_threshold)
      print('\nStep 1:')
      print('  - spinousProcessIntersected = ', spinousProcessIntersected)
      print('  - Angle AP = ', angle_AP)
      print('  - Angle RL = ', angle_RL)
      print('  - success = ', success)
    #
    # Step 2: Check if L4 spinous process is aligned with ultrasound beam
    #
    if stepId == 2:
      spinousProcessIntersected = self.getCollisionWithUltrasoundPlane(self.l4_model)
      angle_AP = self.computeTransversePlaneAngleDeviationAP(self.axial_l4_plane)
      angle_RL = self.computeTransversePlaneAngleDeviationRL(self.axial_l4_plane)
      success = spinousProcessIntersected and (angle_AP < angle_AP_threshold) and (angle_RL < angle_RL_threshold)
      print('\nStep 2:')
      print('  - spinousProcessIntersected = ', spinousProcessIntersected)
      print('  - Angle AP = ', angle_AP)
      print('  - Angle RL = ', angle_RL)
      print('  - success = ', success)
    #
    # Step 3: Check if L3 spinous process is aligned with ultrasound beam
    #
    if stepId == 3:
      spinousProcessIntersected = self.getCollisionWithUltrasoundPlane(self.l3_model)
      angle_AP = self.computeTransversePlaneAngleDeviationAP(self.axial_l3_plane)
      angle_RL = self.computeTransversePlaneAngleDeviationRL(self.axial_l3_plane)
      success = spinousProcessIntersected and (angle_AP < angle_AP_threshold) and (angle_RL < angle_RL_threshold)
      print('\nStep 3:')
      print('  - spinousProcessIntersected = ', spinousProcessIntersected)
      print('  - Angle AP = ', angle_AP)
      print('  - Angle RL = ', angle_RL)
      print('  - success = ', success)
    #
    # Step 4: Check if L2 spinous process is aligned with ultrasound beam
    #
    if stepId == 4:
      spinousProcessIntersected = self.getCollisionWithUltrasoundPlane(self.l2_model)
      angle_AP = self.computeTransversePlaneAngleDeviationAP(self.axial_l2_plane)
      angle_RL = self.computeTransversePlaneAngleDeviationRL(self.axial_l2_plane)
      success = spinousProcessIntersected and (angle_AP < angle_AP_threshold) and (angle_RL < angle_RL_threshold)
      print('\nStep 4:')
      print('  - spinousProcessIntersected = ', spinousProcessIntersected)
      print('  - Angle AP = ', angle_AP)
      print('  - Angle RL = ', angle_RL)
      print('  - success = ', success)
    #
    # Step 5: Check if L1 spinous process is aligned with ultrasound beam
    #
    if stepId == 5:
      spinousProcessIntersected = self.getCollisionWithUltrasoundPlane(self.l1_model)
      angle_AP = self.computeTransversePlaneAngleDeviationAP(self.axial_l1_plane)
      angle_RL = self.computeTransversePlaneAngleDeviationRL(self.axial_l1_plane)
      success = spinousProcessIntersected and (angle_AP < angle_AP_threshold) and (angle_RL < angle_RL_threshold)
      print('\nStep 5:')
      print('  - spinousProcessIntersected = ', spinousProcessIntersected)
      print('  - Angle AP = ', angle_AP)
      print('  - Angle RL = ', angle_RL)
      print('  - success = ', success)
    #
    # Step 6: Check if L3-L4 interspinous space is aligned with ultrasound beam
    #
    if stepId == 6: 
      l3SpinousProcessIntersected = self.getCollisionWithUltrasoundPlane(self.l3_model)
      l4SpinousProcessIntersected = self.getCollisionWithUltrasoundPlane(self.l4_model)
      angle_AP = self.computeLongitudinalPlaneAngleDeviationAP(self.axial_l4_plane) # using L4 axial plane for angle computation
      angle_SI = self.computeLongitudinalPlaneAngleDeviationSI(self.axial_l4_plane) # using L4 axial plane for angle computation
      success = l3SpinousProcessIntersected and l4SpinousProcessIntersected and (angle_AP < angle_AP_threshold) and (angle_SI < angle_SI_threshold)
      print('\nStep 6:')
      print('  - spinousProcessIntersected (L3) = ', l3SpinousProcessIntersected)
      print('  - spinousProcessIntersected (L4) = ', l4SpinousProcessIntersected)
      print('  - Angle AP = ', angle_AP)
      print('  - Angle SI = ', angle_SI)
      print('  - success = ', success)

    #
    # Step 7: Check needle trajectory before insertion in L3-L$ interspinous process
    #
    if stepId == 7:
      targetIntersected = self.getCollisionWithNeedleTrajectory(self.targetL3L4_model)
      spineIntersected = self.getCollisionWithNeedleTrajectory(self.spine_model)
      needle_linear_deviation, needle_angle_deviation = self.computeNeedleDeviationFromOptimalTrajectory(self.optimalTrajectoryL3L4_fiducials)
      print('\nStep 7:')
      print('  - Target intersected = ', targetIntersected)
      print('  - Spine intersected = ', spineIntersected)
      print('  - Needle tip linear deviation = ', needle_linear_deviation)
      print('  - Needle angle deviation = ', needle_angle_deviation)
      success = targetIntersected and (not spineIntersected) and (needle_linear_deviation < needle_linear_deviation_threshold) and (needle_angle_deviation < needle_angle_deviation_threshold)
      print('  - success = ', success)

    return success

  #------------------------------------------------------------------------------
  def computeNeedleDeviationFromOptimalTrajectory(self, optimalTrajectoryFiducials):
    # Get optimal trajectory vector
    optimalTrajectory_pointA = np.array(optimalTrajectoryFiducials.GetNthControlPointPositionWorld(1))
    optimalTrajectory_pointB = np.array(optimalTrajectoryFiducials.GetNthControlPointPositionWorld(0))
    optimalTrajectory_vector = optimalTrajectory_pointB - optimalTrajectory_pointA

    # Get needle trajectory vector
    needleTrajectory_pointA = np.array(self.needleTrajectory_fiducials.GetNthControlPointPositionWorld(1))
    needleTrajectory_pointB = np.array(self.needleTrajectory_fiducials.GetNthControlPointPositionWorld(0))
    needleTrajectory_vector = needleTrajectory_pointB - needleTrajectory_pointA

    # Compute needle tip deviation
    needle_linear_deviation = self.computeDistanceFromPointToLine(needleTrajectory_pointB, optimalTrajectory_pointA, optimalTrajectory_pointB)

    # Compute angle between needle trajectory and optimal trajectory
    needle_angle_deviation = self.computeAngularDeviation(needleTrajectory_vector, optimalTrajectory_vector)

    return needle_linear_deviation, needle_angle_deviation

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

    # Output
    if numContacts > 0:
      collision = True
    else:
      collision = False
    
    return collision

  #------------------------------------------------------------------------------
  def getCollisionWithNeedleTrajectory(self, inputModelNode):
    """
    Check collision between needle trajectory model and input model.
    """
    # Get models
    modelA = self.needle_trajectory_model
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

    # Output
    if numContacts > 0:
      collision = True
    else:
      collision = False
    
    return collision
  
  #------------------------------------------------------------------------------
  def computeTransversePlaneAngleDeviationRL(self, vertebraAxialPlane):
    # Get US image plane
    usImage_plane_centroid = np.array(self.usProbe_plane.GetCenterWorld())
    usImage_plane_normal = np.array(self.usProbe_plane.GetNormalWorld())

    # Get vertebra axial plane
    vertebraAxial_plane_centroid = np.array(vertebraAxialPlane.GetCenterWorld())
    vertebraAxial_plane_normal = np.array(vertebraAxialPlane.GetNormalWorld())

    # Get sagittal plane
    sagittal_plane_centroid = np.array(self.sagittal_plane.GetCenterWorld())
    sagittal_plane_normal = np.array(self.sagittal_plane.GetNormalWorld())

    # Project US plane normal to coronal plane
    usPlane_pointA = usImage_plane_centroid
    usPlane_pointB = usImage_plane_centroid + 10.0*usImage_plane_normal
    usPlane_pointA_proj = self.projectPointToPlane(usPlane_pointA, sagittal_plane_centroid, sagittal_plane_normal)
    usPlane_pointB_proj = self.projectPointToPlane(usPlane_pointB, sagittal_plane_centroid, sagittal_plane_normal)

    # Project vertebra axial plane to coronal plane
    vertebraAxialPlane_pointA = vertebraAxial_plane_centroid
    vertebraAxialPlane_pointB = vertebraAxial_plane_centroid + 10.0*vertebraAxial_plane_normal
    vertebraAxialPlane_pointA_proj = self.projectPointToPlane(vertebraAxialPlane_pointA, sagittal_plane_centroid, sagittal_plane_normal)
    vertebraAxialPlane_pointB_proj = self.projectPointToPlane(vertebraAxialPlane_pointB, sagittal_plane_centroid, sagittal_plane_normal)

    # Compute angular deviation within coronal plane
    usPlane_orientation_vector = usPlane_pointB_proj - usPlane_pointA_proj
    vertebraAxialPlane_orientation_vector = vertebraAxialPlane_pointB_proj - vertebraAxialPlane_pointA_proj
    angle = self.computeAngularDeviation(usPlane_orientation_vector, vertebraAxialPlane_orientation_vector)
    
    # Reformat angle
    if angle > 90.0:
      angle = 180.0 - angle

    return angle
  
  #------------------------------------------------------------------------------
  def computeTransversePlaneAngleDeviationAP(self, vertebraAxialPlane):
    # Get US image plane
    usImage_plane_centroid = np.array(self.usProbe_plane.GetCenterWorld())
    usImage_plane_normal = np.array(self.usProbe_plane.GetNormalWorld())

    # Get vertebra axial plane
    vertebraAxial_plane_centroid = np.array(vertebraAxialPlane.GetCenterWorld())
    vertebraAxial_plane_normal = np.array(vertebraAxialPlane.GetNormalWorld())

    # Get sagittal plane
    sagittal_plane_centroid = np.array(self.sagittal_plane.GetCenterWorld())
    sagittal_plane_normal = np.array(self.sagittal_plane.GetNormalWorld())

    # Get coronal plane
    IS_axis = vertebraAxial_plane_normal
    LR_axis = sagittal_plane_normal
    PA_axis = np.cross(IS_axis, LR_axis)/np.linalg.norm(np.cross(IS_axis, LR_axis))
    coronal_plane_centroid = vertebraAxial_plane_centroid
    coronal_plane_normal = np.array(PA_axis)    

    # Project US plane normal to coronal plane
    usPlane_pointA = usImage_plane_centroid
    usPlane_pointB = usImage_plane_centroid + 10*usImage_plane_normal
    usPlane_pointA_proj = self.projectPointToPlane(usPlane_pointA, coronal_plane_centroid, coronal_plane_normal)
    usPlane_pointB_proj = self.projectPointToPlane(usPlane_pointB, coronal_plane_centroid, coronal_plane_normal)

    # Project vertebra axial plane to coronal plane
    vertebraAxialPlane_pointA = vertebraAxial_plane_centroid
    vertebraAxialPlane_pointB = vertebraAxial_plane_centroid + 10*vertebraAxial_plane_normal
    vertebraAxialPlane_pointA_proj = self.projectPointToPlane(vertebraAxialPlane_pointA, coronal_plane_centroid, coronal_plane_normal)
    vertebraAxialPlane_pointB_proj = self.projectPointToPlane(vertebraAxialPlane_pointB, coronal_plane_centroid, coronal_plane_normal)

    # Compute angular deviation within coronal plane
    usPlane_orientation_vector = usPlane_pointB_proj - usPlane_pointA_proj
    vertebraAxialPlane_orientation_vector = vertebraAxialPlane_pointB_proj - vertebraAxialPlane_pointA_proj
    angle = self.computeAngularDeviation(usPlane_orientation_vector, vertebraAxialPlane_orientation_vector)
    
    # Reformat angle
    if angle > 90.0:
      angle = 180.0 - angle

    return angle
  
  #------------------------------------------------------------------------------
  def computeLongitudinalPlaneAngleDeviationAP(self, vertebraAxialPlane):
    # Get US image plane
    usImage_plane_centroid = np.array(self.usProbe_plane.GetCenterWorld())
    usImage_plane_normal = np.array(self.usProbe_plane.GetNormalWorld())

    # Get vertebra axial plane
    vertebraAxial_plane_centroid = np.array(vertebraAxialPlane.GetCenterWorld())
    vertebraAxial_plane_normal = np.array(vertebraAxialPlane.GetNormalWorld())

    # Get sagittal plane
    sagittal_plane_centroid = np.array(self.sagittal_plane.GetCenterWorld())
    sagittal_plane_normal = np.array(self.sagittal_plane.GetNormalWorld())

    # Get coronal plane
    IS_axis = vertebraAxial_plane_normal
    LR_axis = sagittal_plane_normal
    PA_axis = np.cross(IS_axis, LR_axis)/np.linalg.norm(np.cross(IS_axis, LR_axis))
    coronal_plane_centroid = vertebraAxial_plane_centroid
    coronal_plane_normal = np.array(PA_axis)    

    # Project US plane normal to reference axial plane
    usPlane_pointA = usImage_plane_centroid
    usPlane_pointB = usImage_plane_centroid + 10*usImage_plane_normal
    usPlane_pointA_proj = self.projectPointToPlane(usPlane_pointA, coronal_plane_centroid, coronal_plane_normal)
    usPlane_pointB_proj = self.projectPointToPlane(usPlane_pointB, coronal_plane_centroid, coronal_plane_normal)

    # Project sagittal plane to reference axial plane
    sagittalPlane_pointA = sagittal_plane_centroid
    sagittalPlane_pointB = sagittal_plane_centroid + 10*sagittal_plane_normal
    sagittalPlane_pointA_proj = self.projectPointToPlane(sagittalPlane_pointA, coronal_plane_centroid, coronal_plane_normal)
    sagittalPlane_pointB_proj = self.projectPointToPlane(sagittalPlane_pointB, coronal_plane_centroid, coronal_plane_normal)

    # Compute angular deviation within coronal plane
    usPlane_orientation_vector = usPlane_pointB_proj - usPlane_pointA_proj
    sagittalPlane_orientation_vector = sagittalPlane_pointB_proj - sagittalPlane_pointA_proj
    angle = self.computeAngularDeviation(usPlane_orientation_vector, sagittalPlane_orientation_vector)
    
    # Reformat angle
    if angle > 90.0:
      angle = 180.0 - angle

    return angle
  
  #------------------------------------------------------------------------------
  def computeLongitudinalPlaneAngleDeviationSI(self, vertebraAxialPlane):
    # Get US image plane
    usImage_plane_centroid = np.array(self.usProbe_plane.GetCenterWorld())
    usImage_plane_normal = np.array(self.usProbe_plane.GetNormalWorld())

    # Get vertebra axial plane
    vertebraAxial_plane_centroid = np.array(vertebraAxialPlane.GetCenterWorld())
    vertebraAxial_plane_normal = np.array(vertebraAxialPlane.GetNormalWorld())

    # Get sagittal plane
    sagittal_plane_centroid = np.array(self.sagittal_plane.GetCenterWorld())
    sagittal_plane_normal = np.array(self.sagittal_plane.GetNormalWorld())

    # Project US plane normal to reference axial plane
    usPlane_pointA = usImage_plane_centroid
    usPlane_pointB = usImage_plane_centroid + 10*usImage_plane_normal
    usPlane_pointA_proj = self.projectPointToPlane(usPlane_pointA, vertebraAxial_plane_centroid, vertebraAxial_plane_normal)
    usPlane_pointB_proj = self.projectPointToPlane(usPlane_pointB, vertebraAxial_plane_centroid, vertebraAxial_plane_normal)

    # Project sagittal plane to reference axial plane
    sagittalPlane_pointA = sagittal_plane_centroid
    sagittalPlane_pointB = sagittal_plane_centroid + 10*sagittal_plane_normal
    sagittalPlane_pointA_proj = self.projectPointToPlane(sagittalPlane_pointA, vertebraAxial_plane_centroid, vertebraAxial_plane_normal)
    sagittalPlane_pointB_proj = self.projectPointToPlane(sagittalPlane_pointB, vertebraAxial_plane_centroid, vertebraAxial_plane_normal)

    # Compute angular deviation within coronal plane
    usPlane_orientation_vector = usPlane_pointB_proj - usPlane_pointA_proj
    sagittalPlane_orientation_vector = sagittalPlane_pointB_proj - sagittalPlane_pointA_proj
    angle = self.computeAngularDeviation(usPlane_orientation_vector, sagittalPlane_orientation_vector)
    
    # Reformat angle
    if angle > 90.0:
      angle = 180.0 - angle

    return angle
  
  #------------------------------------------------------------------------------
  def projectPointToPlane(self, point, planeCentroid, planeNormal):

    # Project point to plane
    projectedPoint = np.subtract(np.array(point), np.dot(np.subtract(np.array(point), np.array(planeCentroid)), np.array(planeNormal)) * np.array(planeNormal))
    
    return projectedPoint

  #------------------------------------------------------------------------------
  def computeDistanceFromPointToLine(self, point, linePointA, linePointB):
    return np.linalg.norm(np.cross(linePointB-linePointA, point-linePointA) / np.linalg.norm(linePointB-linePointA))

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

import vtk, qt, ctk, slicer
import os
import numpy as np

from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

import logging

# TrainUS parameters
import TrainUSLib.TrainUSParameters as Parameters

#------------------------------------------------------------------------------
#
# ExerciseVascular
#
#------------------------------------------------------------------------------
class ExerciseVascular(ScriptedLoadableModule):
  
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "ExerciseVascular"
    self.parent.categories = ["TrainUS"]
    self.parent.dependencies = []
    self.parent.contributors = ["David Garcia Mato (Ebatinca)"]
    self.parent.helpText = """ Module to train US-guided needle insertion. """
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """This project has been funded by NEOTEC grant from the Centre for the Development of Technology and Innovation (CDTI) of the Ministry for Science and Innovation of the Government of Spain."""

#------------------------------------------------------------------------------
#
# ExerciseVascularWidget
#
#------------------------------------------------------------------------------
class ExerciseVascularWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  
  def __init__(self, parent):
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)

    # Create logic class
    self.logic = ExerciseVascularLogic(self)

    # TrainUS widget
    self.trainUsWidget = slicer.trainUsWidget

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

    # Load exercise data
    self.logic.loadExerciseData()

    # Update GUI
    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def exit(self):
    """
    Runs when exiting the module.
    """
    # Delete exercise data
    self.logic.deleteExerciseData()

  #------------------------------------------------------------------------------
  def setupUi(self):
    
    # Load widget from .ui file (created by Qt Designer).
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/ExerciseVascular.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Customize widgets
    self.ui.showInstructionsButton.setText('Show')

  #------------------------------------------------------------------------------
  def setupConnections(self):
    self.ui.easyRadioButton.toggled.connect(self.onDifficultyRadioButtonToggled)
    self.ui.mediumRadioButton.toggled.connect(self.onDifficultyRadioButtonToggled)
    self.ui.hardRadioButton.toggled.connect(self.onDifficultyRadioButtonToggled)
    self.ui.showInstructionsButton.clicked.connect(self.onShowInstructionsButtonClicked)
    self.ui.previousInstructionButton.clicked.connect(self.onPreviousInstructionButtonClicked)
    self.ui.nextInstructionButton.clicked.connect(self.onNextInstructionButtonClicked)
    self.ui.backToMenuButton.clicked.connect(self.onBackToMenuButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    self.ui.easyRadioButton.clicked.disconnect()
    self.ui.mediumRadioButton.clicked.disconnect()
    self.ui.hardRadioButton.clicked.disconnect()
    self.ui.showInstructionsButton.clicked.disconnect()
    self.ui.previousInstructionButton.clicked.disconnect()
    self.ui.nextInstructionButton.clicked.disconnect()
    self.ui.backToMenuButton.clicked.disconnect()

  #------------------------------------------------------------------------------
  def updateGUIFromMRML(self, caller=None, event=None):
    """
    Set selections and other settings on the GUI based on the parameter node.

    Calls the updateGUIFromMRML function of all tabs so that they can take care of their own GUI.
    """
    pass

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

    self.updateGUIFromMRML()

  #------------------------------------------------------------------------------
  def onShowInstructionsButtonClicked(self):
    self.logic.intructionsVisible = not self.logic.intructionsVisible

    # Update GUI
    if self.logic.intructionsVisible:
      self.ui.showInstructionsButton.setText('Hide')
    else:
      self.ui.showInstructionsButton.setText('Show')

    # Update instruction display
    self.logic.updateDisplayExerciseInstructions()

  #------------------------------------------------------------------------------
  def onPreviousInstructionButtonClicked(self):
    self.logic.previousExerciseInstruction()

  #------------------------------------------------------------------------------
  def onNextInstructionButtonClicked(self):
    self.logic.nextExerciseInstruction()

  #------------------------------------------------------------------------------
  def onBackToMenuButtonClicked(self):
    # Go back to Home module
    slicer.util.selectModule('Home')


#---------------------------------------------------------------------------------------------#
#                                                                                             #
#                                                                                             #
#                                                                                             #
#                                       ExerciseVascularLogic                                          #
#                                                                                             #
#                                                                                             #
#                                                                                             #
#---------------------------------------------------------------------------------------------#
class ExerciseVascularLogic(ScriptedLoadableModuleLogic, VTKObservationMixin):
  
  def __init__(self, widgetInstance, parent=None):
    ScriptedLoadableModuleLogic.__init__(self, parent)
    VTKObservationMixin.__init__(self)

    # Define member variables
    self.fileDir = os.path.dirname(__file__)
    # Only defined in case there is no other way but having to use the widget from the logic
    self.moduleWidget = widgetInstance
    self.trainUsWidget = slicer.trainUsWidget

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

    # Exercise settings
    self.exerciseDifficulty = 'Medium'  
    self.exerciseLayout = '3D only'

    # Instructions
    self.instructions = None
    self.intructionsVisible = False
    self.lastLayout = None 
    self.lastBackgroundVolumeID = None

    # Data path
    self.dataFolderPath = self.moduleWidget.resourcePath('ExerciseVascularData/')

    # Volume reslice driver
    try:
      self.volumeResliceDriverLogic = slicer.modules.volumereslicedriver.logic()
    except:
      logging.error('Volume Reslice Driver module was not found.')

    # Red slice
    self.redSliceLogic = slicer.app.layoutManager().sliceWidget("Red").sliceLogic()

  #------------------------------------------------------------------------------
  def loadExerciseData(self):
    # Load instructions
    try:
        self.instructions = slicer.util.getNode('Instructions1')
    except:
      try:
        self.instructions = slicer.util.loadVolume(self.dataFolderPath + '/Instructions/Instructions1.PNG')
      except:
        print('ERROR: Instructions files could not be loaded...')

    # Load models
    self.usProbe_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'UsProbe_Telemed_L12', [1.0,0.93,0.91], visibility_bool = True, opacityValue = 1.0)    
    self.stylus_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'StylusModel', [0.21,0.90,0.10], visibility_bool = True, opacityValue = 1.0)
    self.needle_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'NeedleModel', [0.21,0.90,0.10], visibility_bool = True, opacityValue = 1.0)
    self.phantom_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'PhantomVascularTissue', [1.0,0.86,0.68], visibility_bool = True, opacityValue = 0.3)
    self.vessels_model = self.loadModelFromFile(self.dataFolderPath + '/Models/', 'VesselsModel', [0.76,0.18,0.18], visibility_bool = True, opacityValue = 0.5)

    # Load transforms
    self.StylusToTracker = self.getOrCreateTransform('StylusToTracker')
    self.NeedleToTracker = self.getOrCreateTransform('NeedleToTracker')
    self.ProbeToTracker = self.getOrCreateTransform('ProbeToTracker')
    self.TrackerToPatient = self.getOrCreateTransform('TrackerToPatient')
    self.StylusTipToStylus = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'StylusTipToStylus')
    self.NeedleTipToNeedle = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'NeedleTipToNeedle')
    self.ProbeModelToProbe = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'ProbeModelToProbe')
    self.ImageToProbe = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'ImageToProbe')
    self.PatientToRAS = self.loadTransformFromFile(self.dataFolderPath + '/Transforms/', 'PatientToRAS')

    # Get ultrasound image
    try:
      self.usImageVolumeNode = slicer.util.getNode('Image_Reference')
    except:
      logging.error('ERROR: Image_Reference volume node was not found...')
      return

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
    self.TrackerToPatient.SetAndObserveTransformNodeID(self.PatientToRAS.GetID())  

    # Fit US image to view and display in 3D view     
    self.redSliceLogic.FitSliceToAll()
    self.redSliceLogic.GetSliceNode().SetSliceVisible(1)

    # Set difficulty parameters
    self.updateDifficulty()

    # Improve visibility removing: 3D cube and 3D axis label.
    view1 = slicer.util.getNode('View1')
    view1.SetBoxVisible(False)
    view1.SetAxisLabelsVisible(False)

  #------------------------------------------------------------------------------
  def deleteExerciseData(self):
    # Delete instructions    
    slicer.mrmlScene.RemoveNode(self.instructions)

    # Delete models
    slicer.mrmlScene.RemoveNode(self.usProbe_model)
    slicer.mrmlScene.RemoveNode(self.stylus_model)
    slicer.mrmlScene.RemoveNode(self.needle_model)
    slicer.mrmlScene.RemoveNode(self.phantom_model)
    slicer.mrmlScene.RemoveNode(self.vessels_model)

    # Delete transforms
    slicer.mrmlScene.RemoveNode(self.StylusTipToStylus)
    slicer.mrmlScene.RemoveNode(self.NeedleTipToNeedle)
    slicer.mrmlScene.RemoveNode(self.ProbeModelToProbe)
    slicer.mrmlScene.RemoveNode(self.ImageToProbe)
    slicer.mrmlScene.RemoveNode(self.PatientToRAS)
    
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
      self.stylus_model.GetModelDisplayNode().SetVisibility2D(self.highlightModelsInImage)
      self.needle_model.GetModelDisplayNode().SetVisibility2D(self.highlightModelsInImage)
      self.vessels_model.GetModelDisplayNode().SetVisibility2D(self.highlightModelsInImage)
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
      if self.instructions:
        self.redSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(self.instructions.GetID())
        self.redSliceLogic.GetSliceNode().SetOrientationToAxial()
        self.redSliceLogic.SetSliceOffset(0)
        self.redSliceLogic.GetSliceNode().SetSliceVisible(False)
        self.redSliceLogic.FitSliceToAll()        

      # Deactivate model slice visibility
      try:
        self.stylus_model.GetModelDisplayNode().SetVisibility2D(False)
        self.needle_model.GetModelDisplayNode().SetVisibility2D(False)
        self.vessels_model.GetModelDisplayNode().SetVisibility2D(False)
      except:
        pass

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
        self.redSliceLogic.GetSliceNode().SetSliceVisible(True)
        self.redSliceLogic.FitSliceToAll()

      # Restore model slice visibility
      try:
        self.stylus_model.GetModelDisplayNode().SetVisibility2D(self.highlightModelsInImage)
        self.needle_model.GetModelDisplayNode().SetVisibility2D(self.highlightModelsInImage)
        self.vessels_model.GetModelDisplayNode().SetVisibility2D(self.highlightModelsInImage)
      except:
        pass

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

    # Modify slice viewers
    for name in layoutManager.sliceViewNames():
      sliceWidget = layoutManager.sliceWidget(name)
      self.showViewerPinButton(sliceWidget, show = True)
    

#------------------------------------------------------------------------------
#
# ExerciseVascularTest
#
#------------------------------------------------------------------------------
class ExerciseVascularTest(ScriptedLoadableModuleTest):
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
class ExerciseVascularFileWriter(object):
  def __init__(self, parent):
    pass

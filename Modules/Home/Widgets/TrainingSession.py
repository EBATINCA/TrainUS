from __main__ import vtk, qt, ctk, slicer
import logging
import os

#------------------------------------------------------------------------------
#
# TrainingSession
#
#------------------------------------------------------------------------------
class TrainingSession(qt.QWidget):

  def __init__(self, parent=None):
    super(TrainingSession, self).__init__(parent)

    # Define member variables
    self.homeWidget = None # Set externally after creation
    self.trainUsWidget = slicer.trainUsWidget

  #------------------------------------------------------------------------------
  # Clean up when application is closed
  def cleanup(self):
    logging.debug('TrainingSession.cleanup')

    self.disconnect()

  #------------------------------------------------------------------------------
  def setupUi(self):
    logging.debug('TrainingSession.setupUi')

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiFilePath = os.path.join(self.homeWidget.logic.fileDir, 'Resources', 'UI', 'TrainingSession.ui')
    uiWidget = slicer.util.loadUI(uiFilePath)
    self.sectionLayout = qt.QVBoxLayout(self)
    self.sectionLayout.setContentsMargins(0, 0, 0, 0)
    self.sectionLayout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Customize widgets
    self.ui.advancedExercise1Button.setText('Lumbar Insertion')
    self.ui.advancedExercise2Button.setText('Vascular Cannulation')
    
    # Display TrainUS logo in UI
    logoFilePath = os.path.join(self.homeWidget.logic.fileDir, 'Resources', 'Logo', 'TrainUS_Logo.png')
    self.ui.trainUSLogo.pixmap = qt.QPixmap(logoFilePath)
    
    # Setup GUI connections
    self.setupConnections()

  #------------------------------------------------------------------------------
  def setupConnections(self):
    logging.debug('TrainingSession.setupConnections')

    self.ui.basicExercise1Button.clicked.connect(self.onBasicExercise1ButtonClicked)
    self.ui.basicExercise2Button.clicked.connect(self.onBasicExercise2ButtonClicked)
    self.ui.basicExercise3Button.clicked.connect(self.onBasicExercise3ButtonClicked)
    self.ui.basicExercise4Button.clicked.connect(self.onBasicExercise4ButtonClicked)
    self.ui.advancedExercise1Button.clicked.connect(self.onAdvancedExercise1ButtonClicked)
    self.ui.advancedExercise2Button.clicked.connect(self.onAdvancedExercise2ButtonClicked)
    self.ui.advancedExercise3Button.clicked.connect(self.onAdvancedExercise3ButtonClicked)
    self.ui.finishTrainingButton.clicked.connect(self.onFinishTrainingButtonClicked)

  #------------------------------------------------------------------------------
  def disconnect(self):
    logging.debug('TrainingSession.disconnect')

    self.ui.basicExercise1Button.clicked.disconnect()
    self.ui.basicExercise2Button.clicked.disconnect()
    self.ui.basicExercise3Button.clicked.disconnect()
    self.ui.basicExercise4Button.clicked.disconnect()
    self.ui.advancedExercise1Button.clicked.disconnect()
    self.ui.advancedExercise2Button.clicked.disconnect()
    self.ui.advancedExercise3Button.clicked.disconnect()
    self.ui.finishTrainingButton.clicked.disconnect()

  #------------------------------------------------------------------------------
  def updateGUIFromMRML(self, caller=None, event=None):
    """
    Set selections and other settings on the GUI based on the parameter node
    """
    del caller
    del event
    parameterNode = self.homeWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    pass


  #------------------------------------------------------------------------------
  #
  # Event handler functions
  #
  #------------------------------------------------------------------------------
  
  #------------------------------------------------------------------------------
  def onBasicExercise1ButtonClicked(self):
    print('Basic training - Exercise 1')

    # Create new recording
    self.trainUsWidget.logic.recordingManager.createNewRecording('Basic Exercise 1')
  
  #------------------------------------------------------------------------------
  def onBasicExercise2ButtonClicked(self):
    print('Basic training - Exercise 2')    

    # Create new recording
    self.trainUsWidget.logic.recordingManager.createNewRecording('Basic Exercise 2')
  
  #------------------------------------------------------------------------------
  def onBasicExercise3ButtonClicked(self):
    print('Basic training - Exercise 3')    

    # Create new recording
    self.trainUsWidget.logic.recordingManager.createNewRecording('Basic Exercise 3')
  
  #------------------------------------------------------------------------------
  def onBasicExercise4ButtonClicked(self):
    print('Basic training - Exercise 4')    

    # Create new recording
    self.trainUsWidget.logic.recordingManager.createNewRecording('Basic Exercise 4')
  
  #------------------------------------------------------------------------------
  def onAdvancedExercise1ButtonClicked(self):
    print('Advanced training - Exercise 1')

    # Create new recording
    self.trainUsWidget.logic.recordingManager.createNewRecording('Advanced Exercise 1')    

    # Shows slicer interface
    self.homeWidget.hideHome()

    # Change to ExerciseVascular module
    slicer.util.selectModule('ExerciseLumbarInsertion')
  
  #------------------------------------------------------------------------------
  def onAdvancedExercise2ButtonClicked(self):
    print('Advanced training - Exercise 2')    

    # Create new recording
    self.trainUsWidget.logic.recordingManager.createNewRecording('Advanced Exercise 2')

    # Shows slicer interface
    self.homeWidget.hideHome()

    # Change to ExerciseVascular module
    slicer.util.selectModule('ExerciseVascular')
  
  #------------------------------------------------------------------------------
  def onAdvancedExercise3ButtonClicked(self):
    print('Advanced training - Exercise 3')    

    # Create new recording
    self.trainUsWidget.logic.recordingManager.createNewRecording('Advanced Exercise 3')
  
  #------------------------------------------------------------------------------
  def onFinishTrainingButtonClicked(self):
    # Update UI page
    self.homeWidget.logic.setMode(modeID = 0) # switch back to welcome page

  
  #------------------------------------------------------------------------------
  #
  # Logic functions
  #
  #------------------------------------------------------------------------------

import vtk, qt, ctk, slicer
import os

from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
# from Resources import HomeResourcesResources

import logging

#------------------------------------------------------------------------------
#
# Home
#
#------------------------------------------------------------------------------
class Home(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Home"
    self.parent.categories = ["TrainUS"]
    self.parent.dependencies = []
    self.parent.contributors = ["Csaba Pinter (Ebatinca), David Garcia Mato (Ebatinca)"]
    self.parent.helpText = """The Home screen of the custom application"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """EBATINCA, S.L.""" # replace with organization, grant and thanks.


#------------------------------------------------------------------------------
#
# Home dialog class
#
#------------------------------------------------------------------------------
class QHomeWidget(qt.QDialog):
  """
  QHomeWidget extends QDialog class to have a modified close event for required home screen functionality
  """
  def __init__(self):
    """
    Initializes required window options for the widget

    :return void:
    """
    qt.QDialog.__init__(self)
    self.setWindowFlags(qt.Qt.Window)
    self.setWindowTitle('TrainUS')

  def closeEvent(self, event):
    """
    Handle closing

    :param QCloseEvent event: The parameters that describe the close event

    :return void:
    """
    confirmCloseBox = qt.QMessageBox()
    confirmCloseBox.setIcon(qt.QMessageBox.Warning)
    confirmCloseBox.setWindowTitle('Confirm Close')
    confirmCloseBox.setText(
      'Are you sure you want to close TrainUS?\n\nAny unsaved changes will be lost.')
    confirmCloseBox.setStandardButtons(qt.QMessageBox.Ok | qt.QMessageBox.Cancel)
    confirmCloseBox.setDefaultButton(qt.QMessageBox.Cancel)
    confirmCloseBox.setModal(True)
    retval = confirmCloseBox.exec_()
    if retval == qt.QMessageBox.Ok:
      self.hide()
      slicer.mrmlScene.Clear(0)
      qt.QTimer.singleShot(0, slicer.app, slicer.app.closeAllWindows())
      #TODO: Use slicer.trainUsWidget.exitApplication()
    else:
      event.ignore()


#------------------------------------------------------------------------------
#
# HomeWidget
#
#------------------------------------------------------------------------------
class HomeWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    """
    Initialize the window and main GUI for the TrainUS home screen

    :param QWidget parent: The parent widget for the QHomeWidget class

    :return void:
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)

    self.homeWidget = QHomeWidget()
    # self.homeWidget.setStyleSheet(self.loadStyleSheet())

  #------------------------------------------------------------------------------
  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer)
    self.uiWidget = slicer.util.loadUI(self.resourcePath('UI/Home.ui'))
    self.layout.addWidget(self.uiWidget)
    self.ui = slicer.util.childWidgetVariables(self.uiWidget)

    # Create logic class
    self.logic = HomeLogic(self)

    # Setup connections
    self.setupConnections()

    # Dark palette does not propagate on its own?
    # self.uiWidget.setPalette(slicer.util.mainWindow().style().standardPalette())

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
    self.showHome()

  #------------------------------------------------------------------------------
  def showHome(self):
    """
    Open the home screen by setting positioning and raising to modal widget

    :return void:
    """
    mainWindow = slicer.util.mainWindow()
    if mainWindow:
      self.popupGeometry = mainWindow.geometry
      self.homeWidget.setGeometry(self.popupGeometry)
      self.homeWidget.show()
      if mainWindow.isFullScreen():
        self.homeWidget.showFullScreen()
      if mainWindow.isMaximized():
        self.homeWidget.showMaximized()
      mainWindow.hide()
    self.creatingNewStudy = False

  #------------------------------------------------------------------------------
  def hideHome(self):
    """
    Hide the home screen and reveals the main interface after loading a scene

    :return void:
    """
    mainWindow = slicer.util.mainWindow()
    if mainWindow:
      self.popupGeometry = self.homeWidget.geometry
      mainWindow.show()
      mainWindow.setGeometry(self.popupGeometry)
      if self.homeWidget.isFullScreen():
        mainWindow.showFullScreen()
      #if self.homeWidget.isMaximized():
      #  mainWindow.showMaximized()
      self.homeWidget.hide()

  #------------------------------------------------------------------------------
  def setupConnections(self):
    pass

  #------------------------------------------------------------------------------
  def disconnect(self):
    pass

  #------------------------------------------------------------------------------
  def loadStyleSheet(self):
    """
    Loading style sheet for the home screen

    :return string: Returns stylesheet as a string to be applied to the home screen
    """
    moduleDir = os.path.dirname(__file__)
    styleFile = os.path.join(moduleDir, 'Resources', 'StyleSheets', 'HomeStyle.qss')
    f = qt.QFile(styleFile)

    # Adding logging statement for when a particular file does not exist
    if not f.exists():
      logging.debug("Unable to load stylesheet, file not found")
      return ""
    else:
      f.open(qt.QFile.ReadOnly | qt.QFile.Text)
      ts = qt.QTextStream(f)
      stylesheet = ts.readAll()
      return stylesheet

  #------------------------------------------------------------------------------
  def updateGUIFromMRML(self, caller=None, event=None):
    """
    Set selections and other settings on the GUI based on the parameter node.

    Calls the updateGUIFromMRML function of all tabs so that they can take care of their own GUI.
    """
    # Get parameter node
    parameterNode = slicer.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('updateGUIFromMRML: Failed to get parameter node')
      return


#---------------------------------------------------------------------------------------------#
#                                                                                             #
#                                                                                             #
#                                                                                             #
#                                       HomeLogic                                             #
#                                                                                             #
#                                                                                             #
#                                                                                             #
#---------------------------------------------------------------------------------------------#
class HomeLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual computation done by your module.  The interface
  should be such that other python code can import this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, widgetInstance, parent=None):
    ScriptedLoadableModuleLogic.__init__(self, parent)
    VTKObservationMixin.__init__(self)

    # Define member variables
    self.fileDir = os.path.dirname(__file__)
    # Only defined in case there is no other way but having to use the widget from the logic
    self.moduleWidget = widgetInstance
    # Pointer to the parameter node so that we have access to the old one before setting the new one
    self.parameterNode = None

    # Constants
    #TODO:

    # Default parameters map
    self.defaultParameters = {}
    # self.defaultParameters["DecimationFactor"] = 0.85

    # Parameter node reference roles
    # self.modelReferenceRolePrefix = 'Model_'

    # Parameter node parameter names
    # self.datasetNameParameterName = 'DatasetName'

    # Setup scene
    self.setupScene()

    # Setup keyboard shortcuts
    self.setupKeyboardShortcuts()

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
# HomeTest
#
#------------------------------------------------------------------------------
class HomeTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_Home1()

  def test_Home1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #

    logic = HomeLogic()
    self.delayDisplay('Test passed!')


#
# Class for avoiding python error that is caused by the method SegmentEditor::setup
# http://issues.slicer.org/view.php?id=3871
#
class HomeFileWriter(object):
  def __init__(self, parent):
    pass

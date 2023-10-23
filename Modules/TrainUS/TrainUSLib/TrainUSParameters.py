import logging
import os

from __main__ import vtk, qt, slicer  # pylint: disable=no-name-in-module
from slicer.util import VTKObservationMixin

# Make this instance easy to access:
#
#  import TrainUSLib.TrainUSParameters as Parameters
#  ...
#  Parameters.instance.getParameterString(Parameters.PARAM_NAME)
#  Parameters.instance.getNodeReference(Parameters.NODE_REF)
#

class TrainUSParameters(VTKObservationMixin):
  """
  Encapsulation of all core features and convenience functions related to
  application-wide parameter node handling.

  The TrainUSLogic class still owns the parameter node (being subclass of
  GuideletLogic), but this class encapsulates the related functionality for
  easier usage and better code readability and maintainability.
  """

  instance = None

  #
  # Reference roles
  # (reference names are same as the node names)
  #

  # Transforms
  REF_IMAGE_TO_TRANSD_TRANSFORM = 'ImageToTransd'
  REF_REFERENCE_TO_RAS_TRANSFORM = 'ReferenceToRas'

  # Models
  REF_REFERENCEHOLDER_MODEL_REFERENCE = 'ReferenceHolder'
  REF_REFERENCEMARKER_MODEL_REFERENCE = 'ReferenceMarker'
  REF_USPROBEMODEL_TRANSDUCER = 'UsProbe_Transd'

  #
  # Parameters
  #
  APP_MODE = 'AppMode'
  APP_USE_CASE = 'AppUseCase'
  SELECTED_PARTICIPANT_ID = 'SelectedParticipantID'
  SELECTED_RECORDING_ID = 'SelectedRecordingID'
  SELECTED_ULTRASOUND = 'SelectedUltrasoundDevice'
  SELECTED_TRACKER = 'SelectedTrackingSystem'
  SELECTED_PHANTOM = 'SelectedSimulationPhantom'
  ULTRASOUND_IMAGE_NAME = 'UltrasoundImageName'
  ULTRASOUND_PLUS_SERVER_PORT = 'UltrasoundPlusServerPort'
  ULTRASOUND_PLUS_CONFIG_PATH = 'UltrasoundPlusConfigPath'
  ULTRASOUND_PLUS_CONFIG_TEXTNODEID = 'UltrasoundPlusConfigTextNodeID'
  ULTRASOUND_IGTL_CONNECTOR_NODE_ID = 'UltrasoundIGTLConnectorNodeID'
  TRACKER_PLUS_SERVER_PORT = 'TrackerPlusServerPort'
  TRACKER_PLUS_CONFIG_PATH = 'TrackerPlusConfigPath'
  TRACKER_PLUS_CONFIG_TEXTNODEID = 'TrackerPlusConfigTextNodeID'
  TRACKER_IGTL_CONNECTOR_NODE_ID = 'TrackerIGTLConnectorNodeID'
  PLUS_SERVER_RUNNING = 'PlusServerRunning'
  PLUS_SERVER_PATH = 'PlusServerPath'
  PLUS_SERVER_LAUNCHER_PATH = 'PlusServerLauncherPath'
  PLUS_CONNECTION_STATUS = 'PlusConnectionStatus'
  IGTL_CONNECTION_STATUS = 'IGTLConnectionStatus'

  #
  # Constants
  #
  APP_USE_CASE_RECORDING = 'Recording'
  APP_USE_CASE_EVALUATION = 'Evaluation'
  EXERCISE_BASIC_INPLANE_INSERTION = 'In-plane needle insertion'
  EXERCISE_BASIC_OUTPLANE_INSERTION = 'Out-of-plane needle insertion'
  EXERCISE_ADVANCED_LUMBAR = 'Lumbar insertion'
  EXERCISE_ADVANCED_VASCULAR = 'Vascular cannulation'
  EXERCISE_ADVANCED_DRAINAGE = 'Abscess drainage'
  EXERCISE_TO_MODULENAME_DICTIONARY = {
    EXERCISE_BASIC_INPLANE_INSERTION: 'ExerciseInPlaneNeedleInsertion',
    EXERCISE_BASIC_OUTPLANE_INSERTION: 'ExerciseOutPlaneNeedleInsertion',
    EXERCISE_ADVANCED_LUMBAR: 'ExerciseLumbarInsertion',
    EXERCISE_ADVANCED_VASCULAR: 'ExerciseVascular',
    EXERCISE_ADVANCED_DRAINAGE: 'ExerciseAbscessDrainage'
  }

  def __init__(self, trainUsWidgetInstance):
    """
    Constructor of class. Intializes variables with default values.
    """
    VTKObservationMixin.__init__(self)

    self.trainUsWidgetInstance = trainUsWidgetInstance

    # Pointer to the parameter node so that we have access to the old one before setting the new one
    self.parameterNode = None

    # Default parameters map
    self.defaultParameters = {}
    self.defaultParameters[self.APP_MODE] = '0'
    self.defaultParameters[self.APP_USE_CASE] = self.APP_USE_CASE_RECORDING
    self.defaultParameters[self.SELECTED_PARTICIPANT_ID] = ''
    self.defaultParameters[self.SELECTED_RECORDING_ID] = ''
    self.defaultParameters[self.SELECTED_ULTRASOUND] = 'Simulated US - Linear Probe'
    self.defaultParameters[self.SELECTED_TRACKER] = 'None'
    self.defaultParameters[self.SELECTED_PHANTOM] = 'None'
    self.defaultParameters[self.ULTRASOUND_IMAGE_NAME] = 'Image_Reference'
    self.defaultParameters[self.ULTRASOUND_PLUS_SERVER_PORT] = '18944'
    self.defaultParameters[self.ULTRASOUND_PLUS_CONFIG_PATH] = ''
    self.defaultParameters[self.ULTRASOUND_PLUS_CONFIG_TEXTNODEID] = ''
    self.defaultParameters[self.ULTRASOUND_IGTL_CONNECTOR_NODE_ID] = ''
    self.defaultParameters[self.TRACKER_PLUS_SERVER_PORT] = '18945'
    self.defaultParameters[self.TRACKER_PLUS_CONFIG_PATH] = ''
    self.defaultParameters[self.TRACKER_PLUS_CONFIG_TEXTNODEID] = ''
    self.defaultParameters[self.TRACKER_IGTL_CONNECTOR_NODE_ID] = ''
    self.defaultParameters[self.PLUS_SERVER_RUNNING] = 'False'
    self.defaultParameters[self.PLUS_SERVER_PATH] = ''
    self.defaultParameters[self.PLUS_SERVER_LAUNCHER_PATH] = ''
    self.defaultParameters[self.PLUS_CONNECTION_STATUS] = 'OFF'
    self.defaultParameters[self.IGTL_CONNECTION_STATUS] = 'OFF'

  def getParameterNode(self):
    """
    Get parameter node.
    """
    return self.trainUsWidgetInstance.logic.getParameterNode()

  def setParameterNode(self, inputParameterNode):
    """
    Set parameter node as main parameter node in the TrainUS application.
    - When importing a scene the parameter node from the scene is set
    - When closing the scene, the parameter node is reset
    - Handle observations of managed nodes (remove from old ones, add to new ones)
    - Set default parameters if not specified in the given node
    """
    logging.debug('TrainUSParameters.setParameterNode')
    if inputParameterNode == self.parameterNode:
      return

    # Remove observations from nodes referenced in the old parameter node
    if self.parameterNode:
      self.removeObserver(self.parameterNode, vtk.vtkCommand.ModifiedEvent, self.trainUsWidgetInstance.updateGUIFromMRML)

    # Reset member variables
    #TODO: If any

    #
    # Set parameter node member variable (so that we have access to the old one before setting the new one)
    #
    self.parameterNode = inputParameterNode

    # Add observations on referenced nodes
    if self.parameterNode:
      self.addObserver(self.parameterNode, vtk.vtkCommand.ModifiedEvent, self.trainUsWidgetInstance.updateGUIFromMRML)

    # Make sure parameter node is associated to this module
    if self.parameterNode:
      self.parameterNode.SetModuleName(self.trainUsWidgetInstance.moduleName)

    #
    # Set default parameters if missing
    #
    self.setDefaultParameters()

    # Create nodes that are persistent in the scene and missing
    #TODO: If any, like the basic transformation nodes or an SH folder

  def setDefaultParameters(self, force=False):
    """
    Set default parameters to the parameter node. The default parameters are stored in the map TrainUSLogic.defaultParameters

    :param bool force: Set default parameter even if the parameter is already set. False by default
    """
    parameterNode = self.getParameterNode()
    if not parameterNode:
      logging.error('Failed to set default parameters due to missing parameter node')
      return

    existingParameterNames = parameterNode.GetParameterNames()

    wasModified = parameterNode.StartModify()  # Modify all properties in a single batch

    for name, value in self.defaultParameters.items():
      if not force and name in existingParameterNames:
        continue
      parameterNode.SetParameter(name, str(value))

    parameterNode.EndModify(wasModified)

  def getNodeReference(self, referenceRole):
    """
    Get a given referenced node. Do not create it if does not exist but return None.

    :param string referenceRole: The reference role for the referenced node
    :return: Referenced node or None if does not exist
    """
    parameterNode = self.getParameterNode()
    if not parameterNode:
      raise Exception('Failed to get parameter node')

    nodeID = parameterNode.GetNodeReferenceID(referenceRole)
    if nodeID in [None, '']:
      return None

    # Node is found, return it
    node = slicer.mrmlScene.GetNodeByID(nodeID)
    return node

  def setNodeReference(self, referenceRole, node):
    """
    Set a node reference.

    :param string referenceRole: The reference role for the referenced node
    :param vtkMRMLNode node: The node to reference
    """
    if not node:
      raise ValueError('Invalid node given to set reference "%s"' % referenceRole)

    parameterNode = self.getParameterNode()
    if not parameterNode:
      raise Exception('Failed to get parameter node')

    parameterNode.SetNodeReferenceID(referenceRole, node.GetID())

  def setParameter(self, parameterName, parameterValue):
    """
    Convenience function to set a parameter in the parameter node
    :param string parameterName: Name of the parameter. Should be coming from a constant stored as member variable
    :param string parameterValue: Value of the parameter. Any value is accepted and converted to string
    """
    parameterNode = self.getParameterNode()
    if not parameterNode:
      raise Exception('Failed to set value %s to parameter named %s due to missing parameter node' % (str(parameterValue), parameterName))

    parameterNode.SetParameter(parameterName, str(parameterValue))

  def getParameterBool(self, parameterName):
    """
    Convenience function to get a boolean parameter from the parameter node
    :param string parameterName: Name of the parameter. Should be coming from a constant stored as member variable
    :return bool: The parameter value if found, False otherwise
    """
    parameterNode = self.getParameterNode()
    if not parameterNode:
      raise Exception('Failed to get value of parameter named %s due to missing parameter node' % (parameterName))

    value = parameterNode.GetParameter(parameterName)
    return (value == 'True')

  def getParameterInt(self, parameterName):
    """
    Convenience function to get an integer parameter from the parameter node
    :param string parameterName: Name of the parameter. Should be coming from a constant stored as member variable
    :return int: The parameter value if found, 0 otherwise
    """
    parameterNode = self.getParameterNode()
    if not parameterNode:
      raise Exception('Failed to get value of parameter named %s due to missing parameter node' % (parameterName))

    value = parameterNode.GetParameter(parameterName)
    try:
      return int(value)
    except ValueError:
      logging.error('Failed to convert value %s of parameter %s to integer. Returning zero' % (str(value), parameterName))
      raise

  def getParameterFloat(self, parameterName):
    """
    Convenience function to get a floating point parameter from the parameter node
    :param string parameterName: Name of the parameter. Should be coming from a constant stored as member variable
    :return float: The parameter value if found, 0 otherwise
    """
    parameterNode = self.getParameterNode()
    if not parameterNode:
      raise Exception('Failed to get value of parameter named %s due to missing parameter node' % (parameterName))

    value = parameterNode.GetParameter(parameterName)
    try:
      return float(value)
    except ValueError:
      logging.error('Failed to convert value %s of parameter %s to floating point number. Returning zero' % (str(value), parameterName))
      raise

  def getParameterString(self, parameterName):
    """
    Convenience function to get a string parameter from the parameter node
    :param string parameterName: Name of the parameter. Should be coming from a constant stored as member variable
    :return string: The parameter value if found, empty string otherwise
    """
    parameterNode = self.getParameterNode()
    if not parameterNode:
      raise Exception('Failed to get value of parameter named %s due to missing parameter node' % (parameterName))

    return parameterNode.GetParameter(parameterName)

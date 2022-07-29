import math
import vtk

class PerkEvaluatorMetric:

  @staticmethod
  def GetMetricName():
    return "Maximal rotational error while moving the needle"

  @staticmethod
  def GetMetricUnit():
    return "deg"

  @staticmethod
  def GetAcceptedTransformRoles():
    return [ "Needle", "Ultrasound" ]

  @staticmethod
  def GetRequiredAnatomyRoles():
    # Although not really anatomy, we will need the image node
    return { "Parameter": "vtkMRMLNode" }

    
  def __init__( self ):
    self.inputParameterNode = None
  
    self.maximumAngleDeg = 0
    

  def AddAnatomyRole( self, role, node ):
    if ( node == None or not node.IsA( self.GetRequiredAnatomyRoles()[ role ] ) ):
      return False
      
    if ( role == "Parameter" ):
      self.inputParameterNode = node
      return True

    return False

  def AddTimestamp( self, time, matrix, point, role ):  
    if ( self.inputParameterNode == None ):
      return

    currAngleDeg = self.inputParameterNode.GetAttribute( "PerkTutor_NeedlePlaneAngleDeg" )
    try:
      currAngleDeg = float( currAngleDeg )
    except:
      return
      
    inAction = self.inputParameterNode.GetAttribute( "PerkTutor_InAction" )
    inAction = ( inAction == "True" )
    if ( not inAction ):
      return
  
    if ( currAngleDeg > self.maximumAngleDeg ):
      self.maximumAngleDeg = currAngleDeg


  def GetMetric( self ):
    return round( self.maximumAngleDeg, 1 )

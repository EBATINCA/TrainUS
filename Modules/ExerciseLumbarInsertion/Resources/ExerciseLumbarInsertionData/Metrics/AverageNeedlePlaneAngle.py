import math
import vtk

class PerkEvaluatorMetric:

  @staticmethod
  def GetMetricName():
    return "Average rotational error while moving the needle"

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
  
    self.angleSumDeg = 0
    self.timestampCount = 0
    

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
  
    self.angleSumDeg = self.angleSumDeg + currAngleDeg
    self.timestampCount = self.timestampCount + 1


  def GetMetric( self ):
    if ( self.timestampCount == 0 ):
      return 0
    else:
      return round( self.angleSumDeg / self.timestampCount, 1 )

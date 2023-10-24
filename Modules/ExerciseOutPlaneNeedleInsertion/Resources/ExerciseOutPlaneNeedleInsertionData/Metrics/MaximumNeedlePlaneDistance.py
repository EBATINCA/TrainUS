import math
import vtk

class PerkEvaluatorMetric:

  @staticmethod
  def GetMetricName():
    return "Maximal distance from plane while moving the needle"

  @staticmethod
  def GetMetricUnit():
    return "mm"

  @staticmethod
  def GetAcceptedTransformRoles():
    return [ "Needle", "Ultrasound" ]

  @staticmethod
  def GetRequiredAnatomyRoles():
    # Although not really anatomy, we will need the image node
    return { "Parameter": "vtkMRMLNode" }

    
  def __init__( self ):
    self.inputParameterNode = None
  
    self.maximumDistanceMm = 0
    

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

    currDistanceMm = self.inputParameterNode.GetAttribute( "PerkTutor_NeedlePlaneDistanceMm" )
    try:
      currDistanceMm = float( currDistanceMm )
    except:
      return
      
    inAction = self.inputParameterNode.GetAttribute( "PerkTutor_InAction" )
    inAction = ( inAction == "True" )
    if ( not inAction ):
      return
  
    if ( currDistanceMm > self.maximumDistanceMm and inAction ):
      self.maximumDistanceMm = currDistanceMm


  def GetMetric( self ):
    return round( self.maximumDistanceMm, 1 )
